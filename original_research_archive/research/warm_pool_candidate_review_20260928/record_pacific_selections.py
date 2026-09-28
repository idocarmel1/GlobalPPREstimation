"""Record the user's three-region selection, preserving exact experimental inputs."""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from workbooks import read_book, write_book, overview, sha
from regional import set_setting
from run_region import prepare_selection

REGIONS = ["HS_071", "EEZ_941", "EEZ_598"]
ORIGIN = ROOT / "regions/EEZ_941"
SOURCE_ID = "941_200701_WCPO_Warm_Pool_Final_(mixed_periods)"
SELECTED_ID = "941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)"
GRIFFITHS_IDS = ["941_201901_Warm_Pool_(2005)",
                 "941_20190101_Warm_Pool_Detritus_Pooled_Experiment_(2005)"]
EXPERIMENTS = ORIGIN / "models" / SOURCE_ID / "balance_investigation/correction_scenarios"
BENCHMARK = EXPERIMENTS / "D_fixed_M0"
INPUT = BENCHMARK / (SOURCE_ID + ".json")
INPUT_SHA = sha(INPUT)
SPATIAL = json.loads((OUT / "SPATIAL_OVERLAP.json").read_text(encoding="utf-8"))
RATIONALE = (
    "USER SELECTED 2026-09-28: WCP-2007 option 1 (D_fixed_M0) for HS_071, EEZ_941 "
    "and EEZ_598. Explicit experimental variant preserves juvenile other-mortality flows "
    "and changes Small BET P/B to 1.4129713563375232, EE to 0.7898725981469387; "
    "Small YFT P/B to 2.5304972811160384, EE to 0.8816702937266387. "
    "GE, TE and With Egestion all WARN; PP-budget checks OK, but strict mass balance "
    "remains false (adult BET residual 0.727940%). This is an adopted surrogate, not "
    "an author-confirmed correction or a region-specific native EwE model. "
    "Original source remains preserved. Griffiths 2019 source and pooled variant "
    "are retained for later investigation of failures, not selected."
)
INVESTIGATION = (
    "USER REQUEST 2026-09-28: retain Griffiths et al. (2019) for later investigation "
    "across HS_071, EEZ_941 and EEZ_598. Understand why it fails before considering "
    "adoption. Original 46-group extraction is blocked by unknown two-pool routing. "
    "The authorized 45-group pooled experiment loads but GE, TE and With Egestion "
    "all FAIL. Investigate the Pomfret production/predation inconsistency, 22 printed "
    "catch-total versus fleet-sum conflicts, and routing/fishery-return and loader "
    "effects separately. No further parameter repair is authorized by this note."
)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def copy_exact_tree(source, target, skip=()):
    if source.resolve() == target.resolve():
        return []
    checked = []
    for src in sorted(source.rglob("*")):
        if not src.is_file() or src.name in skip:
            continue
        rel = src.relative_to(source)
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            assert sha(dst) == sha(src), f"Conflicting existing file: {dst}"
        else:
            shutil.copy2(src, dst)
        assert sha(dst) == sha(src)
        checked.append({"path": dst.relative_to(ROOT).as_posix(), "sha256": sha(dst)})
    return checked


def main():
    original_hashes = {mid: sha(ORIGIN / "models" / mid / "model.json") for mid in GRIFFITHS_IDS}
    original_hashes[SOURCE_ID] = sha(ORIGIN / "models" / SOURCE_ID / "model.json")
    paper_metadata = json.loads((ORIGIN / "papers/Griffiths-2019/metadata.json").read_text(encoding="utf-8"))
    scenario = json.loads((BENCHMARK / "SCENARIO_SUMMARY.json").read_text())
    assert scenario["input_sha256"] == INPUT_SHA
    assert all(v["status"] == "WARN" for v in scenario["methods"].values())
    result = {"selected_model_id": SELECTED_ID, "source_scenario": "D_fixed_M0",
              "selected_input_sha256": INPUT_SHA, "regions": [], "central_status": "pending registration"}
    for uid in REGIONS:
        region = ROOT / "regions" / uid
        model_dir = region / "models" / SELECTED_ID
        model_dir.mkdir(parents=True, exist_ok=True)
        for name in ["model.json", SELECTED_ID + ".json"]:
            dest = model_dir / name
            if dest.exists():
                assert sha(dest) == INPUT_SHA
            else:
                shutil.copy2(INPUT, dest)
            assert sha(dest) == INPUT_SHA
        files = copy_exact_tree(BENCHMARK, model_dir / "diagnostic_evidence")
        for name in ["PROVENANCE.json", "VERIFICATION.json", "CORRECTION_SCENARIOS.md"]:
            dest = model_dir / "diagnostic_evidence" / ("experiment_" + name)
            shutil.copy2(EXPERIMENTS / name, dest)
        write_json(model_dir / "SELECTION_AND_PROVENANCE.json", {
            "unit_id": uid, "selected_model_id": SELECTED_ID, "selected": True,
            "rationale": RATIONALE, "experimental_source": INPUT.relative_to(ROOT).as_posix(),
            "input_sha256": INPUT_SHA, "parameter_changes": scenario["changes"],
            "diagnostic_summary": scenario["methods"], "strict_balance": False,
            "region_coverage": SPATIAL["domains"]["WCP2007"]["overlap"][uid],
            "regional_results_status": "pending; selection does not imply full catch coverage"})
        (model_dir / "SELECTION_REPORT.md").write_text(
            f"# {uid}: selected WCP-2007 option 1\n\n{RATIONALE}\n\n"
            f"Exact selected model: `{SELECTED_ID}`. Its JSON bytes match the tested "
            f"D_fixed_M0 experiment (SHA-256 `{INPUT_SHA}`).\n\n"
            "Existing diagnostic returns are retained in diagnostic_evidence/. "
            "No diagnostic rerun or additional biological correction was performed "
            "to record this selection. Previous regional results are archived and "
            "model-dependent tables are cleared pending calculations for this selection.\n\n"
            f"{INVESTIGATION}\n", encoding="utf-8")

        paper_dir = region / "papers/Griffiths-2019"
        files += copy_exact_tree(ORIGIN / "papers/Griffiths-2019", paper_dir,
                                 skip=("metadata.json", "LATER_INVESTIGATION.md"))
        local_meta = copy.deepcopy(paper_metadata)
        local_meta.update(unit_id=uid, article_id=f"Griffiths-2019__{uid}", selected=False,
                          review_status="deferred investigation requested by user",
                          investigation_note=INVESTIGATION,
                          target_coverage_ratio=SPATIAL["domains"]["Griffiths2019"]["overlap"][uid]["percent_target_region_covered"] / 100)
        local_meta["later_selection_context"] = "WCP-2007 option 1 selected for all three regions; Griffiths retained for later investigation."
        for material in local_meta.get("material_files", []):
            material["relative_path"] = material["relative_path"].replace("regions/EEZ_941/", f"regions/{uid}/")
        local_meta["canonical_model_path"] = f"regions/{uid}/models/{GRIFFITHS_IDS[0]}/model.json"
        local_meta["review_path"] = f"regions/{uid}/models/{GRIFFITHS_IDS[0]}/source_review"
        write_json(paper_dir / "metadata.json", local_meta)
        (paper_dir / "LATER_INVESTIGATION.md").write_text("# Deferred model investigation\n\n" + INVESTIGATION + "\n", encoding="utf-8")
        for mid in GRIFFITHS_IDS:
            target = region / "models" / mid
            files += copy_exact_tree(ORIGIN / "models" / mid, target, skip=("REGIONAL_REVIEW_STATUS.json",))
            assert sha(target / "model.json") == original_hashes[mid]
            write_json(target / "REGIONAL_REVIEW_STATUS.json", {
                "unit_id": uid, "model_id": mid, "selected": False,
                "status": "deferred investigation", "user_note": INVESTIGATION,
                "source_model_sha256": original_hashes[mid],
                "diagnostics": "NOT_RUN: routing blocked" if mid == GRIFFITHS_IDS[0] else "GE FAIL; TE FAIL; With Egestion FAIL"})

        workbook = region / (uid + ".xlsx")
        book = read_book(workbook)
        before = copy.deepcopy(book)
        backup = model_dir / "selection_evidence" / (uid + "_before_" + sha(workbook)[:12] + ".xlsx")
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copy2(workbook, backup)
        set_setting(book, "selected_model_id", SELECTED_ID)
        set_setting(book, "model_path", f"models/{SELECTED_ID}/{SELECTED_ID}.json")
        set_setting(book, "selection_rationale", RATIONALE)
        set_setting(book, "production_eligible", False)
        set_setting(book, "griffiths_later_investigation", INVESTIGATION)
        prepare_selection(book, workbook)
        write_book(workbook, book)
        after = read_book(workbook)
        assert overview(after)["selected_model_id"] == SELECTED_ID
        assert sha(region / overview(after)["model_path"]) == INPUT_SHA
        for sheet in ["Catch", "Classic PPR", "NPP"]:
            assert json.dumps(before[sheet], sort_keys=True) == json.dumps(after[sheet], sort_keys=True), sheet
        result["regions"].append({"unit_id": uid, "workbook_sha256": sha(workbook),
            "backup": backup.relative_to(ROOT).as_posix(), "copied_files_verified": len(files),
            "griffiths_model_hashes": {mid: sha(region / "models" / mid / "model.json") for mid in GRIFFITHS_IDS},
            "selected": True, "regional_calculation_status": overview(after)["calculation_status"]})
        write_json(model_dir / "selection_evidence/COPIED_FILE_MANIFEST.json", files)
    for mid, expected in original_hashes.items():
        assert sha(ORIGIN / "models" / mid / "model.json") == expected
    result["original_model_jsons_unchanged"] = True
    result["status"] = "PASS"
    write_json(OUT / "PACIFIC_SELECTION_VERIFICATION.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
