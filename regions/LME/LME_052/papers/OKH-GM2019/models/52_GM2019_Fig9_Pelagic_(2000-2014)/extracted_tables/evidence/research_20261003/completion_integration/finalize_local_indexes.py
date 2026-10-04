"""Preserve prior navigation files and identify the adopted provisional model."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
REGION = BASE.parents[1]
MID = "52_GM2019_Fig9_Pelagic_balanced_(2000-2014)"
VARIANT = BASE / "assumption_variants/adopted_balanced_20261003"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    paths = [BASE / "CURRENT_VARIANT.json", REGION / "models/MASTER_INDEX.md", REGION / "reports_index.md"]
    proof = {"model_id": MID, "files": []}
    for path in paths:
        old = sha(path)
        backup = HERE / (path.name + ".before_" + old[:12])
        if not backup.exists():
            backup.write_bytes(path.read_bytes())
        proof["files"].append({"path": str(path), "before_sha256": old, "backup": backup.name})
    pointer = json.loads(paths[0].read_text(encoding="utf-8"))
    pointer.update({
        "current_figure_variant": "assumption_variants/adopted_balanced_20261003",
        "model_id": MID,
        "model_sha256": sha(VARIANT / "model.json"),
        "selected": True, "balanced": True,
        "status": "ADOPTED_PROVISIONAL_WARN",
        "ready_for_researcher_validation": True,
        "production_eligible": False,
        "scientific_validation": "pending researcher review",
        "latest_authorized_assumptions": "assumption_variants/adopted_balanced_20261003/source_to_final_ledger.json",
        "latest_runtime_experiment": "assumption_variants/adopted_balanced_20261003/reload_consistency.json",
        "current_evidence_index": "assumption_variants/adopted_balanced_20261003/evidence_index.json",
        "completed_mandatory_cases_file": "assumption_variants/adopted_balanced_20261003/case_coverage.json",
        "completed_roundtrip_verification": "assumption_variants/adopted_balanced_20261003/ewe_roundtrip_verification.json",
        "current_direct_diagnostics": "assumption_variants/adopted_balanced_20261003/diagnostics",
        "latest_GS_policy": "Free GS under actual standard LIM bounds 0.10–0.35; default_gs false",
        "latest_catch_migration_policy": "Catch, immigration and emigration zero",
        "balance_limitation": "All living BA zero; detritus BA 242.50886238380988 tC/km2/yr is a positive closure residual, not observed burial or steady-state validation",
        "direct_diagnostic_status": {"GE": "WARN", "TE": "WARN", "WithEgestion": "WARN"},
        "pending_remedy_choice": None,
        "authorized_next_stage": "Researcher scientific review of adopted assumptions and WARN diagnostics",
        "completion_evidence_directory": "research_20261003/completion_integration"
    })
    paths[0].write_text(json.dumps(pointer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    master = paths[1].read_text(encoding="utf-8")
    master = master.replace("This index covers the new extraction attempt. Existing NE and SD models remain unchanged; it does not alter selection or map status.",
        "The 2000–2014 assumption reconstruction is now selected in the regional workbook, Project and map. Native balance is verified; all three direct methods remain WARN and scientific review is pending. The earlier extraction and legacy models are retained as historical evidence.")
    if MID not in master:
        master += "\n| " + MID + " | [Adopted native-balanced reconstruction](52_GM2019_Fig9_Pelagic_(2000-2014)/assumption_variants/adopted_balanced_20261003/REPORT.md) |2000–2014|52|22 biological + native Import23|0 catch|selected, provisional WARN|Living BA0; positive detritus closure residual. All three direct diagnostics, source departures, unit bridge and regional integration retained. Researcher review pending.|\n"
    paths[1].write_text(master, encoding="utf-8")
    reports = paths[2].read_text(encoding="utf-8")
    reports = reports.replace("Current selected model: `52_1_Sea_of_Okhotsk_NE_(1980)`.", "Historical selected model before 3 October 2026: `52_1_Sea_of_Okhotsk_NE_(1980)`.")
    if "Current selected model: `" + MID + "`." not in reports:
        block = f"""# Sea of Okhotsk validation reports

Current selected model: `{MID}`.

- [Model validation report](Model_validation_{MID}.docx)
- [Article departures and assumptions report](Article_departures_{MID}.docx)
- [Regional workbook](LME_052.xlsx)
- [Adopted native reconstruction and evidence](models/52_GM2019_Fig9_Pelagic_(2000-2014)/assumption_variants/adopted_balanced_20261003/REPORT.md)
- [Completion evidence inventory](models/52_GM2019_Fig9_Pelagic_(2000-2014)/research_20261003/completion_integration/overall_evidence_index.json)

The adopted assumption reconstruction loads and physically balances in the native engine. GE, TE and With Egestion remain WARN; living BA is zero, but the positive detritus closure residual is not an observed steady-state sink. Source departures, inferred prey imports, carbon conversions and catch mapping remain explicit scientific assumptions. Production eligibility is false and researcher review is pending. The two new reports retain the inherited manual review content without assigning it to the new model or adding a signoff.

## Historical reports and validation stages

"""
        reports = block + reports.split("\n", 1)[1].lstrip()
    paths[2].write_text(reports, encoding="utf-8")
    for record, path in zip(proof["files"], paths):
        record["after_sha256"] = sha(path)
    proof["checks"] = {"exact_model_hash": pointer["model_sha256"] == "9beff5a4e525dcf4253bf83472253c7a4a9f7e7db10379ecef64eb33cd32a656", "all_previous_navigation_bytes_preserved": all(sha(HERE / r["backup"]) == r["before_sha256"] for r in proof["files"])}
    proof["passed"] = all(proof["checks"].values())
    (HERE / "navigation_updates.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")
    assert proof["passed"]
    print(json.dumps(proof["checks"]))


if __name__ == "__main__":
    main()
