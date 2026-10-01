"""Prepare reviewed Kuroshio/Kyoto metadata against the latest shared state."""
from pathlib import Path
import json
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from workbooks import read_book, unchunks, sha
from apply_reviewed_metadata import geometry_digest

project = ROOT / "Project.xlsx"
digest = sha(project)
snapshot = json.loads((BASE / "central_source_metadata_current.json").read_text(encoding="utf-8"))
assert snapshot["project_sha256"] == digest
book = read_book(project)
geometries = unchunks(book["Map geography"]["Geometry"][1])
patches, geometry_patches, inputs, original_snapshots = [], [], [], {}

kyoto_evidence = "regions/LME_050/validation_reports/50_502013_Coastal_Kyoto_Inoue_(2013)"
kyoto_geo = (
    "Approximate native Figure 1 coast-to-240 m study footprint: central A "
    "(target covered by study) 0.167347%, B (study covered by target) 98.388862%. "
    "Low-confidence indicative ranges A 0.15–0.23% and B 95–100% describe graphical "
    "and published-area scale uncertainty, not statistical bounds. The traced "
    "1,680.96 km² is 24.62% smaller than the main text's 2,230 km²; supplementary "
    "depth-bin areas sum to 1,223 km², an unresolved source discrepancy relevant "
    "to the benthic biomass denominator. These quantities remain distinct; no "
    "parameter rescaling or PPR multiplier is applied. Evidence: "
    + kyoto_evidence + "/geography/geographic_assessment.json"
)
kyoto_availability = (
    "Accepted 2013 reconstruction; source Table 1 quantities verified and exact "
    "historical GE, TE and With Egestion matrices reused with old/current loader "
    "parity. All three remain WARN. All 253 labels reviewed, 404 mapping rows, "
    "none unresolved: 20 High, 89 Medium, 1 Low and 143 Very low. Complete source "
    "2013 catch and final biomass splits are Medium-confidence proxies for unknown "
    "regional composition. Year-specific diet ambiguity, accepted defaults, "
    "spatial transfer and the 1,223/2,230 km² area discrepancy remain. Production "
    "eligibility remains false; review completion is not model approval."
)
kyoto_wording = {
    ("Models & coverage", "availability"): kyoto_availability,
    ("Models & coverage", "coverage_note"): kyoto_geo,
    ("Papers", "geometry_note"): kyoto_geo,
    ("Papers", "geometry_method"): (
        "Approximate native Figure 1 dashed 240 m boundary and source coastline "
        "with islands; calibrated against two visible grid ticks per axis. WGS84 "
        "areas, 12 water/land controls and ±0.005° graphical sensitivity retained. "
        "No author GIS or independently verified bathymetric boundary."
    ),
    ("Papers", "full_model_loadable"): (
        "Accepted 1985/2013 tabulated reconstructions load with documented "
        "transformations. Original year-specific diets and complete native EwE "
        "inputs remain unavailable or ambiguous."
    ),
    ("Papers", "extraction_readiness"): (
        "Final 2013 Table 1 core quantities match the accepted reconstruction. "
        "Shared Table 2 diet/year ambiguity, missing catch/default inputs and the "
        "supplementary area discrepancy remain. All 253 source-specific mappings "
        "were reviewed with conditional proxies explicitly identified."
    ),
    ("Papers", "recommendation"): (
        "User selected 2013 because it is newer; 1985 remains a comparison model. "
        "Local Kyoto applicability, diet/default uncertainty, conflicting source "
        "areas and large Very low mapping exposure remain explicit. Selection and "
        "review completion do not establish scientific approval."
    ),
    ("Papers", "notes"): (
        "User preferred this source as the available paper and selected 2013 "
        "for recency, not numerical superiority. " + kyoto_availability + " " + kyoto_geo
    ),
}

for unit in ("LME_049", "LME_050"):
    proposal_path, = (ROOT / "regions" / unit / "validation_reports").glob("*/shared_metadata_proposals.json")
    evidence = proposal_path.parent
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    original_snapshots[unit] = proposal["authenticated_project_sha256"]
    proof = BASE / "verification" / (unit + "_geography_coordinator_review.json")
    assert proof.exists(), "Coordinator geography review is required"
    for patch in proposal["source_proposals"]:
        sheet = patch["sheet"]
        table = "Models" if sheet == "Models & coverage" else "Papers"
        header, rows = book[sheet][table]
        matching = [dict(zip(header, row)) for row in rows
                    if all(dict(zip(header, row)).get(k) == v for k, v in patch["key"].items())]
        assert len(matching) == 1
        assert matching[0][patch["field"]] == patch["expected_old"], (unit, patch["field"])
        proposed = patch["proposed"]
        if unit == "LME_050":
            proposed = kyoto_wording.get((sheet, patch["field"]), proposed)
        patches.append({"sheet": sheet, "table": table, "key": patch["key"],
                        "field": patch["field"], "expected_old": patch["expected_old"],
                        "proposed": proposed,
                        "evidence": [proposal_path.relative_to(ROOT).as_posix(),
                                     (evidence / "source_review.md").relative_to(ROOT).as_posix(),
                                     proof.relative_to(ROOT).as_posix()]})
    gp, = proposal["geometry_proposals"]
    key = "article:" + gp["article_id"]
    assert geometry_digest(geometries[key]) == geometry_digest(gp["expected_old_geometry"])
    replacement = ROOT / gp["proposed_file"]
    value = json.loads(replacement.read_text(encoding="utf-8"))
    if value["type"] == "FeatureCollection":
        assert len(value["features"]) == 1
        value = value["features"][0]
    if value["type"] == "Feature":
        value = value["geometry"]
    assert geometry_digest(value) == geometry_digest(gp["proposed_feature"]["geometry"])
    geometry_patches.append({
        "unit_id": unit, "key": key, "action": "replace",
        "expected_old_geometry_sha256": geometry_digest(geometries[key]),
        "replacement_geojson": replacement.relative_to(ROOT).as_posix(),
        "replacement_file_sha256": sha(replacement),
        "replacement_geometry_sha256": geometry_digest(value),
        "geometry_role": "Approximate displayed source study footprint; Low confidence. No target boundary, scientific parameter or PPR multiplier change.",
        "evidence": proof.relative_to(ROOT).as_posix(),
    })
    inputs.extend([proposal_path, evidence / "coordination_handoff.json",
                   evidence / "source_review.md", evidence / "taxon_audit.json",
                   ROOT / "regions" / unit / (unit + ".xlsx"), proof])
    if unit == "LME_049":
        inputs.extend([evidence / "geography/geography_trace_assessment.json",
                       evidence / "independent_source_review/findings.json"])
    else:
        inputs.extend([evidence / "geography/geographic_assessment.json",
                       evidence / "geography/native_area_source_check.json"])

assert sha(project) == digest
plan = {
    "project_sha256_at_review": digest,
    "regional_proposal_original_snapshots": original_snapshots,
    "scope": "34 keyed source metadata fields and two reviewed article footprints. Preserve accepted parameters, selections, eligibility, reported model areas, quality scores and historical retrieval counts. Readable wording retains the regional scientific conclusions.",
    "regional_inputs": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in inputs],
    "patches": patches, "geometry_patches": geometry_patches,
}
out = BASE / "verification/metadata_batch_16_plan.json"
out.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"path": out.relative_to(ROOT).as_posix(), "patches": len(patches),
                  "geometries": len(geometry_patches), "project_sha256": digest}), flush=True)
