"""Independent seven-cohort arithmetic, regression and lineage verification.

Reconstructs allocations from the published payload and solves design matrices.
Never imports analyze.py or cohort_guard.py, and never invokes a model solver.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import sys
import zipfile
import numpy as np

METHOD = "GE"
METHOD_KEY = "new_GE"
STUDY = Path(__file__).resolve().parents[1]
ROOT = next(p for p in STUDY.parents if (p / "Project.xlsx").is_file())
EXPERIMENT = ROOT / "research/human/sppr_trophic_level_20261018_validated7"
OUTPUT = STUDY / "evidence/independent_verification.json"
consumed, checks = {}, []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    consumed[path] = digest(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def check(label, actual, expected):
    assert math.isclose(actual, expected, rel_tol=2e-10, abs_tol=1e-8), (label, actual, expected)
    checks.append({"check": label, "actual": actual, "expected": expected,
                   "relative_error": abs(actual - expected) / max(abs(expected), 1e-30)})


ledger = read(STUDY / "inputs/source_hashes.json")
for relative, item in ledger.items():
    assert digest(ROOT / relative) == item["sha256"], relative
cohort = read(STUDY / "inputs/cohort.json")
assert (STUDY / "inputs/cohort.json").read_bytes() == (EXPERIMENT / "inputs/cohort.json").read_bytes()
pairs = {(r["unit_id"], r["model_id"]) for r in cohort["pairs"]}
assert len(pairs) == len(cohort["pairs"])
assert ("LME_028", "28_646_Guinea_(1998)") not in pairs
assert digest(ROOT / "Project.xlsx") == cohort["project_sha256"]
sys.path.insert(0, str(ROOT))
from tools.project_core.validation.researcher_review import table_rows
with zipfile.ZipFile(ROOT / "Project.xlsx") as archive:
    central = [r for _, r in table_rows(archive, "Models & coverage", "Models")[3]]
assert pairs == {(r["unit_id"], r["model_id"]) for r in central
                 if r.get("researcher_review_status") == "Validated by researcher"}
units = sorted(p[0] for p in pairs)
ids = dict(pairs)
html = ROOT / "interactive_map/trends.html"
consumed[html] = digest(html)
text = html.read_text(encoding="utf-8")
assert f'ppr-project-sha256" content="{cohort["project_sha256"]}"' in text
start = text.index("const SERIES_DB=") + len("const SERIES_DB=")
db, _ = json.JSONDecoder().raw_decode(text, start)
allocations, groups, included = [], {}, {}
taxon_records = 0
for uid in units:
    unit = db["units"][uid]
    assert unit["default_model"] == ids[uid]
    model = next(m for m in unit["models"] if m["id"] == ids[uid])
    assert model["researcher_review"]["status"] == "Validated by researcher"
    data, inputs = model["group_data"], unit["group_inputs"]
    excluded = set(model["display_ppr_excluded_group_ids"])
    included[uid] = {g["id"] for g in data["groups"]} - excluded
    year = inputs["years"].index(2019)
    mi, ci = data["methods"].index(METHOD_KEY), data["methods"].index("SPPR_1995_TE0.1")
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
            key = (uid, data["groups"][gi]["id"])
            new, classic = data["scopes"]["all"][gi][mi], data["scopes"]["all"][gi][ci]
            assert new is not None and new > 0 and classic > 0
            row = (key, catch * share, tl, new, classic, 1 + math.log10(classic), simple)
            allocations.append(row)
            groups.setdefault(key, []).append(row)

summary = read(STUDY / "results/summary.json")
assert summary["cohort"] == cohort, "Summary cohort differs from exact input manifest"
expect = read(STUDY / "inputs/sample_manifest.json")
counts = {"models": len(pairs), "catch_groups": len(groups),
          "region_taxon_records": taxon_records, "taxon_group_allocations": len(allocations)}
assert all(counts[k] == expect[k] for k in counts), (counts, expect)
assert summary["sample"]["positive_catch_groups"] == len(groups)
assert summary["sample"]["region_taxon_records"] == taxon_records
assert summary["sample"]["taxon_group_allocations"] == len(allocations)
baseline = math.fsum(c * s / 9 for _, c, _, s, _, _, _ in allocations)
check("baseline", baseline, summary["baseline"]["new_" + METHOD + "_tC"])
check("classic", math.fsum(c * cl / 9 for _, c, _, _, cl, _, _ in allocations), summary["baseline"]["classic_model_tC"])
check("simple", math.fsum(c * sp / 9 for _, c, _, _, _, _, sp in allocations), summary["baseline"]["simple_taxon_tC"])
check("catch", math.fsum(r[1] for r in allocations), summary["sample"]["covered_catch_tonnes"])
group_catch = {key: math.fsum(r[1] for r in rows) for key, rows in groups.items()}
group_mean = {key: math.fsum(r[1] * r[2] for r in rows) / group_catch[key] for key, rows in groups.items()}
joined = {(r["unit"], r["group"]): r for r in read(STUDY / "results/joined_groups.json")}
assert set(joined) == set(groups)
for key, rows in groups.items():
    assert joined[key]["model_id"] == ids[key[0]]
    for label, value in (("C", group_catch[key]), ("mu", group_mean[key]), ("T", rows[0][5]), ("S", rows[0][3])):
        check("joined " + str(key) + " " + label, value, joined[key][label])


def total(b, selected=allocations):
    return math.fsum(c * s * 10 ** (b * (tl - tg)) / 9 for _, c, tl, s, _, tg, _ in selected)


scenarios = read(STUDY / "results/scenarios.json")
transport = read(STUDY / "results/group_transport.json")
for scenario in scenarios:
    b = scenario["b"]
    values = {"full_tC": total(b),
              "shift_only_tC": math.fsum(c * s * 10 ** (b * (group_mean[key] - tg)) / 9 for key, c, _, s, _, tg, _ in allocations),
              "centered_jensen_only_tC": math.fsum(c * s * 10 ** (b * (tl - group_mean[key])) / 9 for key, c, tl, s, _, _, _ in allocations)}
    for label, value in values.items():
        check(scenario["id"] + " " + label, value, scenario[label])
    check(scenario["id"] + " ratio", values["full_tC"] / baseline, scenario["full_over_base"])
    for g in transport[scenario["id"]]:
        key = (g["unit"], g["group"])
        check(scenario["id"] + " group " + str(key), total(b, groups[key]), g["full_tC"])
        assert g["within_group_J"] >= 1 - 1e-12
    for regional in scenario["regional"]:
        selection = [r for r in allocations if r[0][0] == regional["unit"]]
        check(scenario["id"] + " region " + regional["unit"], total(b, selection), regional["full_tC"])

source_records = read(EXPERIMENT / "results/group_records.json")
method_records = [r for r in source_records if r["method"] == METHOD]
assert len(method_records) == expect["consumer_groups"]
assert {(r["unit"], r["model_id"]) for r in method_records} == pairs
records = [r for r in method_records if r["s"] is not None and math.isfinite(r["s"]) and r["s"] > 0]


def design_fit(cohort_name, mode, omitted=None, only=None, explicit_weight=None):
    rows = [r for r in records if r["unit"] != omitted and (only is None or r["unit"] == only)]
    if cohort_name == "review_included_uniform" or only is not None:
        rows = [r for r in rows if r["group"] in included[r["unit"]]]
    weight = explicit_weight or {"fished_catch": "C", "fished_ppr": "PPR"}.get(cohort_name, "uniform")
    if cohort_name.startswith("fished") or weight != "uniform":
        rows = [r for r in rows if (r["unit"], r["group"]) in groups]
    x = np.array([r["TL"] for r in rows]); y = np.log10([r["s"] for r in rows])
    w = np.ones(len(rows)); names = np.array([r["unit"] for r in rows]); model_names = sorted(set(names))
    if weight != "uniform":
        w = np.array([group_catch[(r["unit"], r["group"])] for r in rows])
        if weight == "PPR": w *= np.array([r["s"] / 9 for r in rows])
    n_source = len(rows)
    if mode == "between":
        centers = [(np.average(x[names == u], weights=w[names == u]), np.average(y[names == u], weights=w[names == u])) for u in model_names]
        x, y = np.array(centers).T; w = np.ones(len(centers)); names = np.array(model_names)
    if mode == "within":
        indicators = np.array([[float(u == m) for m in model_names] for u in names])
        design = np.column_stack([indicators, x])
        center = np.array([np.average(y[names == u], weights=w[names == u]) for u in names])
    else:
        design = np.column_stack([np.ones(len(x)), x]); center = np.full(len(y), np.average(y, weights=w))
    rootw = np.sqrt(w / w.mean())
    parameters = np.linalg.lstsq(design * rootw[:, None], y * rootw, rcond=None)[0]
    prediction = design @ parameters
    r2 = 1 - np.dot(w * (y - prediction), y - prediction) / np.dot(w * (y - center), y - center)
    return {"slope": float(parameters[-1]), "r2": float(r2), "n_observations": len(x), "n_source_groups": n_source, "n_models": len(model_names)}


regression = read(STUDY / "results/regressions.json")
for name, saved in regression["fits"].items():
    cohort_name, mode = name.split("__")
    actual = design_fit(cohort_name, mode)
    for field in ("slope", "r2"):
        check("design matrix " + name + " " + field, actual[field], saved[field])
    for field in ("n_observations", "n_source_groups", "n_models"):
        assert actual[field] == saved[field], (name, field)
for saved in regression["per_model"]:
    actual = design_fit("review_included_uniform", "pooled", only=saved["unit"], explicit_weight=saved["weight"])
    for field in ("slope", "r2"):
        check("per model " + saved["unit"] + " " + saved["weight"] + " " + field, actual[field], saved[field])
for saved in regression["leave_one_model_out"]:
    cohort_name, mode = saved["fit"].split("__"); omitted = saved["omitted_model"]
    actual = design_fit(cohort_name, mode, omitted=omitted)
    check("LOMO " + saved["fit"] + " " + omitted, actual["slope"], saved["training_slope"])
    check("LOMO r2 " + saved["fit"] + " " + omitted, actual["r2"], saved["training_r2"])
    full = total(actual["slope"])
    check("LOMO total " + saved["fit"] + " " + omitted, full, saved["full_cohort_total_tC"])
    check("LOMO factor " + saved["fit"] + " " + omitted, full / baseline, saved["full_cohort_factor"])
    held = [r for r in allocations if r[0][0] == omitted]
    held_base = math.fsum(c * s / 9 for _, c, _, s, _, _, _ in held)
    check("LOMO held out " + saved["fit"] + " " + omitted, total(actual["slope"], held) / held_base, saved["held_out_model_factor"])
assert len(regression["leave_one_model_out"]) == len(pairs) * sum(not key.endswith("__between") for key in regression["fits"])

if METHOD == "GE":
    te = ROOT / "research/human/ppr_taxonomic_resolution_20261018_validated7"
    assert (te / "inputs/cohort.json").read_bytes() == (STUDY / "inputs/cohort.json").read_bytes()
    te_groups = {(r["unit"], r["group"]): r for r in read(te / "results/joined_groups.json")}
    assert set(te_groups) == set(groups)
    for key, rows in groups.items():
        for field, value in (("C", group_catch[key]), ("mu", group_mean[key]), ("T", rows[0][5])):
            check("GE TE common support " + str(key) + " " + field, value, te_groups[key][field])
    te_transport = read(te / "results/group_transport.json")
    for sid in ("identity_b0", "unit_slope_b1"):
        reference = {(r["unit"], r["group"]): r for r in te_transport[sid]}
        for row in transport[sid]:
            for field in ("shift_factor", "within_group_J", "full_factor"):
                check("GE TE fixed slope " + sid + str((row["unit"], row["group"])) + field, row[field], reference[(row["unit"], row["group"])][field])
    te_scenarios = {r["id"]: r for r in read(te / "results/scenarios.json")}
    ge_scenarios = {r["id"]: r for r in scenarios}
    comparison = read(STUDY / "results/ge_te_comparison.json")
    assert set(te_scenarios) == set(ge_scenarios) == {r["id"] for r in comparison["scenarios"]}
    for row in comparison["scenarios"]:
        sid = row["id"]
        for key, expected_scenario in (("GE", ge_scenarios[sid]), ("TE", te_scenarios[sid])):
            for field, value in row[key].items():
                check("GE TE comparison " + sid + key + field, expected_scenario[field], value)
        check("GE TE total ratio " + sid, ge_scenarios[sid]["full_tC"] / te_scenarios[sid]["full_tC"], row["GE_over_TE_total"])
        check("GE TE total difference " + sid, ge_scenarios[sid]["full_tC"] - te_scenarios[sid]["full_tC"], row["GE_minus_TE_total_tC"])
        check("GE TE slope difference " + sid, ge_scenarios[sid]["b"] - te_scenarios[sid]["b"], row["GE_minus_TE_slope"])
    for relative, item in read(te / "inputs/source_hashes.json").items():
        assert digest(ROOT / relative) == item["sha256"], ("TE transitive source", relative)

figure_review = read(STUDY / "evidence/figure_review.json")
for reviewed in figure_review["figures"]:
    assert reviewed["result"] == "pass" and reviewed["rendered_pixels_inspected"]
    assert digest(STUDY / reviewed["path"]) == reviewed["sha256"], "Reviewed figure changed"

links = []
for relative in ("README.md", "report.md", "evidence/process.md"):
    document = STUDY / relative
    for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "#")): continue
        target = target.split("#")[0].strip("<>")
        resolved = (document.parent / target).resolve()
        assert resolved == OUTPUT or resolved.exists(), (relative, target)
        links.append({"document": relative, "target": target})
for relative, item in ledger.items():
    assert digest(ROOT / relative) == item["sha256"], relative
for path, expected in consumed.items():
    assert digest(path) == expected, ("Verifier input changed", path)
result = {"verified_utc": datetime.now(timezone.utc).isoformat(), "runtime": sys.executable,
          "implementation": "Independent direct allocation sums and weighted least-squares design matrices for pooled, within, between, per-model and leave-one-model-out fits; analysis implementation not imported.",
          "verifier_sha256": digest(Path(__file__)), "checks": checks, "all_numeric_checks_passed": True,
          "source_hash_checks": len(ledger), "all_source_hashes_match": True, "local_links_checked": links,
          "counts": counts, "regression_fits_checked": len(regression["fits"]),
          "per_model_fits_checked": len(regression["per_model"]), "lomo_fits_checked": len(regression["leave_one_model_out"]),
          "source_writes": 0, "engine_invocations": 0,
          "scope": "Reproducibility and arithmetic only; not biological validation or annual-result permission."}
OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
print(json.dumps({"passed": True, "method": METHOD, "counts": counts, "numeric_checks": len(checks),
                  "source_hashes": len(ledger), "baseline_tC": baseline,
                  "max_relative_error": max(c["relative_error"] for c in checks)}))
