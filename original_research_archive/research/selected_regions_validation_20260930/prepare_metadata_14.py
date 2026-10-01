"""Prepare the root-reviewed Java Sea keyed metadata and geometry transaction."""
from pathlib import Path
import json
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from workbooks import read_book, unchunks, sha
from apply_reviewed_metadata import geometry_digest

REGION = ROOT / "regions/LME_038"
EVIDENCE = REGION / "validation_reports/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)"
proposal_path = EVIDENCE / "shared_metadata_proposals.json"
proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
handoff = json.loads((EVIDENCE / "coordination_handoff.json").read_text(encoding="utf-8"))
project = ROOT / "Project.xlsx"
digest = sha(project)
assert digest == proposal["project_snapshot_sha256"]
book = read_book(project)
geometry = unchunks(book["Map geography"]["Geometry"][1])
patches = []
proof = BASE / "verification/LME_038_geography_coordinator_review.json"
for patch in proposal["changes"]:
    sheet = patch["table"]
    patches.append({"sheet": sheet, "table": "Models" if sheet == "Models & coverage" else "Papers",
                    "key": patch["key"], "field": patch["field"], "expected_old": patch["expected_old"],
                    "proposed": patch["proposed_new"],
                    "evidence": [proposal_path.relative_to(ROOT).as_posix(), patch["evidence"],
                                 proof.relative_to(ROOT).as_posix()]})
gproposal = proposal["source_footprint_proposals"][0]
key = gproposal["geometry_key"]
replacement = ROOT / gproposal["proposed_geometry_path"]
assert sha(replacement) == gproposal["proposed_geometry_sha256"]
g = json.loads(replacement.read_text(encoding="utf-8"))
if g["type"] == "FeatureCollection":
    assert len(g["features"]) == 1
    g = g["features"][0]
if g["type"] == "Feature":
    g = g["geometry"]
inputs = [proposal_path, EVIDENCE / "coordination_handoff.json", EVIDENCE / "source_review.md",
          EVIDENCE / "geography/geographic_assessment.json", REGION / "LME_038.xlsx", proof]
assert sha(REGION / "LME_038.xlsx") == handoff["final"]["workbook_sha256"]
plan = {"project_sha256_at_review": digest,
        "scope": "Java Sea accepted-derived model source review and approximate larger east117.5 prose-bounds scenario; preserve source/model parameters, selected identity and all unrelated metadata. Range and geographic limitations retained.",
        "regional_inputs": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in inputs],
        "patches": patches,
        "geometry_patches": [{"unit_id": "LME_038", "key": key,
            "action": "replace" if key in geometry else "insert",
            "expected_old_geometry_sha256": geometry_digest(geometry[key]) if key in geometry else None,
            "replacement_geojson": replacement.relative_to(ROOT).as_posix(),
            "replacement_file_sha256": sha(replacement), "replacement_geometry_sha256": geometry_digest(g),
            "geometry_role": gproposal["method"] + " " + gproposal["limitations"],
            "evidence": proof.relative_to(ROOT).as_posix()}]}
assert sha(project) == digest
out = BASE / "verification/metadata_batch_14_plan.json"
out.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"path": out.relative_to(ROOT).as_posix(), "patches": len(patches),
                  "geometry_action": plan["geometry_patches"][0]["action"]}), flush=True)
