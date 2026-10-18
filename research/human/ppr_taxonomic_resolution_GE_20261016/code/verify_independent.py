"""Independent GE arithmetic check from published coefficients and catch allocations.

Adapted from the TE study verifier; the original study is not modified.

Uses only Python and numpy. Does not import the analysis implementation or solve
models. Writes one verification record within this research package.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import sys

import numpy as np

STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[2]
OUTPUT = STUDY / "evidence/independent_verification.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks = []


def check(label, actual, expected):
    assert math.isclose(actual, expected, rel_tol=2e-10, abs_tol=1e-9), (label, actual, expected)
    checks.append({"check": label, "actual": actual, "expected": expected,
                   "relative_error": abs(actual - expected) / max(abs(expected), 1e-30)})


html = ROOT / "interactive_map/trends.html"
db = json.loads(re.search(r"const SERIES_DB=(.*?);</script>", html.read_text(encoding="utf-8"), re.S).group(1))
units = ["HS_077", "LME_013", "LME_028", "LME_032", "LME_034", "LME_035", "LME_036", "LME_047"]
allocations, groups, included = [], {}, {}
taxon_records = 0
for uid in units:
    unit = db["units"][uid]
    model = next(m for m in unit["models"] if m["id"] == unit["default_model"])
    assert model["researcher_review"]["status"] == "Validated by researcher"
    data = model["group_data"]
    excluded = set(model["display_ppr_excluded_group_ids"])
    included[uid] = {g["id"] for g in data["groups"]} - excluded
    inputs = unit["group_inputs"]
    year = inputs["years"].index(2019)
    method_new = data["methods"].index("new_GE")
    method_classic = data["methods"].index("SPPR_1995_TE0.1")
    for ti, name in enumerate(inputs["taxa"]):
        catch = inputs["full_precision_catch"][ti][year]
        if catch is None or catch <= 0:
            continue
        eligible = [(gi, share) for gi, share in data["mappings"][ti]
                    if data["groups"][gi]["id"] not in excluded and share > 0]
        if not eligible:
            continue
        simple = inputs["simple_sppr"][ti]
        assert simple is not None and simple > 0
        tl = 1 + math.log10(simple)
        taxon_records += 1
        for gi, share in eligible:
            group_id = data["groups"][gi]["id"]
            key = (uid, group_id)
            coefficients = data["scopes"]["all"][gi]
            new, classic = coefficients[method_new], coefficients[method_classic]
            assert new is not None and new > 0 and classic > 0
            group_tl = 1 + math.log10(classic)
            allocated = catch * share
            row = (key, allocated, tl, new, classic, group_tl, simple)
            allocations.append(row)
            groups.setdefault(key, []).append(row)

summary = read(STUDY / "results/summary.json")
baseline = math.fsum(c * s / 9 for _, c, _, s, _, _, _ in allocations)
classic_total = math.fsum(c * cl / 9 for _, c, _, _, cl, _, _ in allocations)
simple_total = math.fsum(c * sp / 9 for _, c, _, _, _, _, sp in allocations)
check("new baseline from current HTML", baseline, summary["baseline"]["new_GE_tC"])
check("classic from current HTML", classic_total, summary["baseline"]["classic_model_tC"])
check("simple from current HTML", simple_total, summary["baseline"]["simple_taxon_tC"])
check("catch", math.fsum(r[1] for r in allocations), summary["sample"]["covered_catch_tonnes"])
assert len(groups) == 200 and taxon_records == 2018 and len(allocations) == 3089

group_catch = {key: math.fsum(r[1] for r in rows) for key, rows in groups.items()}
group_mean = {key: math.fsum(r[1] * r[2] for r in rows) / group_catch[key]
              for key, rows in groups.items()}
scenarios = read(STUDY / "results/scenarios.json")
for scenario in scenarios:
    b = scenario["b"]
    full = math.fsum(c * s * 10 ** (b * (tl - tg)) / 9
                     for _, c, tl, s, _, tg, _ in allocations)
    shifted = math.fsum(c * s * 10 ** (b * (group_mean[key] - tg)) / 9
                        for key, c, _, s, _, tg, _ in allocations)
    centered = math.fsum(c * s * 10 ** (b * (tl - group_mean[key])) / 9
                         for key, c, tl, s, _, _, _ in allocations)
    for label, actual in [("full_tC", full), ("shift_only_tC", shifted),
                          ("centered_jensen_only_tC", centered),
                          ("full_over_base", full / baseline)]:
        check(scenario["id"] + ":" + label, actual, scenario[label])

# Independent regression implementation: solve a weighted design matrix with
# ecosystem indicator columns, rather than the analysis's demeaning formula.
records = read(ROOT / "research/human/sppr_trophic_level_20261016/results/group_records.json")
records = [r for r in records if r["method"] == "GE" and r["s"] > 0]
fits = read(STUDY / "results/regressions.json")["fits"]
for name, fit in fits.items():
    cohort, mode = name.split("__")
    if mode == "between":
        continue
    rows = records
    if cohort == "review_included_uniform":
        rows = [r for r in rows if r["group"] in included[r["unit"]]]
    if cohort.startswith("fished"):
        rows = [r for r in rows if (r["unit"], r["group"]) in groups]
    x = np.array([r["TL"] for r in rows])
    y = np.log10([r["s"] for r in rows])
    w = np.ones(len(rows))
    if cohort in ("fished_catch", "fished_ppr"):
        w = np.array([group_catch[(r["unit"], r["group"])] for r in rows])
        if cohort == "fished_ppr":
            w *= np.array([r["s"] / 9 for r in rows])
    if mode == "pooled":
        design = np.column_stack([np.ones(len(rows)), x])
    else:
        indicators = np.array([[float(r["unit"] == uid) for uid in units] for r in rows])
        design = np.column_stack([indicators, x])
    rootw = np.sqrt(w / w.mean())
    parameters = np.linalg.lstsq(design * rootw[:, None], y * rootw, rcond=None)[0]
    check("independent design-matrix slope:" + name, float(parameters[-1]), fit["slope"])
    assert len(rows) == fit["n_observations"]

# Compare inputs, not GE results, to the previous TE study: identical catch,
# mapping weights, taxon TL and operative model-group TL must be retained.
te_study = ROOT / "research/human/ppr_taxonomic_resolution_20261016"
te_groups = {(g["unit"], g["group"]): g for g in read(te_study / "results/joined_groups.json")}
assert set(groups) == set(te_groups)
for key, rows in groups.items():
    old = te_groups[key]
    check("same catch:" + str(key), group_catch[key], old["C"])
    check("same mean taxon TL:" + str(key), group_mean[key], old["mu"])
    check("same group TL:" + str(key), rows[0][5], old["T"])

ledger = read(STUDY / "inputs/source_hashes.json")
for relative, entry in ledger.items():
    assert digest(ROOT / relative) == entry["sha256"], relative

links = []
for relative in ("README.md", "report.md", "evidence/process.md"):
    document = STUDY / relative
    for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "#")):
            continue
        target = target.split("#")[0].strip("<>")
        resolved = (document.parent / target).resolve()
        # This record is written only after verification succeeds, so its own
        # README link legitimately has no target on the first successful run.
        assert resolved == OUTPUT or resolved.exists(), (relative, target)
        links.append({"document": relative, "target": target})

result = {
    "verified_utc": datetime.now(timezone.utc).isoformat(),
    "runtime": sys.executable,
    "implementation": "Independent direct allocation sums from current HTML and numpy least-squares design matrices; analysis module never imported.",
    "verifier_sha256": digest(Path(__file__)),
    "checks": checks,
    "all_numeric_checks_passed": True,
    "source_hash_checks": len(ledger),
    "all_source_hashes_match": True,
    "local_links_checked": links,
    "counts": {"groups": len(groups), "region_taxon_records": taxon_records, "allocations": len(allocations)},
    "scope": "Checks reproducibility and arithmetic only; does not validate biological assumptions or annual-result availability."
}
OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
print(json.dumps({"passed": True, "numeric_checks": len(checks), "source_hashes": len(ledger),
                  "local_links": len(links), "baseline_tC": baseline,
                  "max_relative_error": max(c["relative_error"] for c in checks)}))
