"""Prepare reviewed East China Sea metadata against the latest central state."""
from pathlib import Path
import json
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from workbooks import read_book, unchunks, sha
from apply_reviewed_metadata import geometry_digest

REGION = ROOT / "regions/LME_047"
EVIDENCE = REGION / "validation_reports/47_2_East_China_Sea_(2018)"
proposal_path = EVIDENCE / "shared_metadata_proposals.json"
proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
project = ROOT / "Project.xlsx"
digest = sha(project)
snapshot = json.loads((BASE / "central_source_metadata_current.json").read_text(encoding="utf-8"))
assert snapshot["project_sha256"] == digest
book = read_book(project)
geometries = unchunks(book["Map geography"]["Geometry"][1])
proof = BASE / "verification/LME_047_geography_coordinator_review.json"
geography_note = (
    "Figure 1 study/survey footprint reconstructed from its native graticule: "
    "A approximately 13.60932015% of the target and B 100% of the study "
    "(descriptive ranges 10–15% and 90–100%). The selected model uses the joint "
    "autumn 2018/spring 2019 survey; an exact native model boundary and area are "
    "not supplied. Whole-LME transfer remains unverified. "
    "See regions/LME_047/validation_reports/47_2_East_China_Sea_(2018)/geography/geographic_assessment.json."
)
wording = {
    ("Models & coverage", "availability"): (
        "Selected accepted M2018 reconstruction; all 276 catch labels reviewed, "
        "none unresolved. Twelve splits use complete positive 2018 S4 catch proxies "
        "and 15 use complete source biomass; allocation confidence is Medium. "
        "GE, TE and With Egestion remain WARN, with strict input and budget balance "
        "passing. EE 0 for Sharks 22 and Marine mammals 23, and unverified canonical "
        "export-0 catch placeholders, remain accepted. Production eligibility is "
        "preserved; review completion is not scientific approval. Evidence: "
        "regions/LME_047/validation_reports/47_2_East_China_Sea_(2018)/coordination_handoff.json"
    ),
    ("Models & coverage", "coverage_note"): geography_note,
    ("Papers", "geometry_note"): geography_note,
    ("Papers", "model_years"): "Static M1997 (1997–2000 survey), M2018 (2018–2019 survey); M1997 Ecosim 2000–2018",
    ("Papers", "geometry_method"): (
        "Approximate native Figure 1 study hatch traced against the original graticule, "
        "preserving the offshore coastal gap and ordered bends; consistent Natural Earth "
        "1:50 million land mask, WGS84 areas and eight water controls. Exact native "
        "model boundary remains unstated."
    ),
    ("Papers", "full_model_loadable"): (
        "Accepted reconstructed M2018 JSON load-tested at exact settings; no native "
        "EwE export. Source catch placeholders, defaults and accounting assumptions remain."
    ),
    ("Papers", "extraction_readiness"): (
        "Core B/PB/QB/EE and accepted normalization of the S3 diet verified. Native "
        "catch, GS, migration, accumulation and routing export remains incomplete. "
        "Source reconstruction and qualified catch/biomass allocation proxies are documented."
    ),
}
patches = []
for patch in proposal["source_proposals"]:
    sheet = patch["sheet"]
    table = "Models" if sheet == "Models & coverage" else "Papers"
    header, rows = book[sheet][table]
    matched = [dict(zip(header, r)) for r in rows
               if all(dict(zip(header, r)).get(k) == v for k, v in patch["key"].items())]
    assert len(matched) == 1
    assert matched[0][patch["field"]] == patch["expected_old"], (sheet, patch["field"])
    patches.append({"sheet": sheet, "table": table, "key": patch["key"],
                    "field": patch["field"], "expected_old": patch["expected_old"],
                    "proposed": wording.get((sheet, patch["field"]), patch["proposed"]),
                    "evidence": [proposal_path.relative_to(ROOT).as_posix(),
                                 (EVIDENCE / "source_review.md").relative_to(ROOT).as_posix(),
                                 proof.relative_to(ROOT).as_posix()]})
gp = proposal["geometry_proposals"][0]
key = "article:" + gp["article_id"]
assert key in geometries
assert geometry_digest(geometries[key]) == geometry_digest(gp["expected_old_geometry"]), "Current central geometry differs from the reviewed inherited envelope"
replacement = ROOT / gp["proposed_file"]
g = json.loads(replacement.read_text(encoding="utf-8"))
if g["type"] == "FeatureCollection":
    assert len(g["features"]) == 1
    g = g["features"][0]
if g["type"] == "Feature":
    g = g["geometry"]
assert geometry_digest(g) == geometry_digest(gp["proposed_feature"]["geometry"])
inputs = [proposal_path, EVIDENCE / "coordination_handoff.json", EVIDENCE / "source_review.md",
          EVIDENCE / "geography/geographic_assessment.json", REGION / "LME_047.xlsx", proof,
          EVIDENCE / "source_2018_catch_proxy.json", EVIDENCE / "taxon_audit.json"]
plan = {"project_sha256_at_review": digest,
        "regional_proposal_original_snapshot": proposal["authenticated_project_sha256"],
        "scope": "Twenty keyed source fields and approximate Figure 1 study footprint. Root rechecked every expected-old field against latest shared state; readable spacing changes preserve reviewed scientific meaning. Preserve eligibility, historical scores, selection and accepted scientific inputs.",
        "regional_inputs": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in inputs],
        "patches": patches,
        "geometry_patches": [{"unit_id": "LME_047", "key": key, "action": "replace",
            "expected_old_geometry_sha256": geometry_digest(geometries[key]),
            "replacement_geojson": replacement.relative_to(ROOT).as_posix(),
            "replacement_file_sha256": sha(replacement), "replacement_geometry_sha256": geometry_digest(g),
            "geometry_role": "Approximate displayed study/survey footprint, not an exact native model domain. No target-region or PPR multiplier change.",
            "evidence": proof.relative_to(ROOT).as_posix()}]}
assert sha(project) == digest
out = BASE / "verification/metadata_batch_15_plan.json"
out.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"path": out.relative_to(ROOT).as_posix(), "patches": len(patches),
                  "geometry": "replace", "current_project": digest}), flush=True)
