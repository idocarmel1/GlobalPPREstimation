"""Read-only LME_035 diet preservation audit; writes only its own evidence folder."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
REGION = ROOT / "regions/LME_035"
MODEL = REGION / "models/35_412_Gulf_of_Thailande_(1963)/model.json"
LIB = ROOT / "common_reference_data/ecobase_library"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def diet(g):
    value = (g.get("diet_descr") or {}).get("diet", [])
    return [value] if isinstance(value, dict) else value


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    import openpyxl
    protected = [MODEL, REGION / "LME_035.xlsx", REGION / "Model_validation_35_412_Gulf_of_Thailande_(1963).docx"]
    before = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected}
    wb = openpyxl.load_workbook(REGION / "LME_035.xlsx", read_only=True, data_only=False)
    settings = {r[0]: r[1] for r in wb["Overview"].values if len(r) > 1 and r[0]}
    wb.close()
    assert settings["selected_model_id"] == "35_412_Gulf_of_Thailande_(1963)"
    assert (REGION / settings["model_path"]).resolve() == MODEL.resolve()
    current = json.loads(MODEL.read_text(encoding="utf-8"))
    raw_file = LIB / "model_diet_datas.json"
    native = json.loads(raw_file.read_text(encoding="utf-8"))["412"]
    native_groups = {g["group_seq"]: g for g in native["group"]}
    assert {g["group_seq"] for g in current["group"]} == set(native_groups)
    cells, sums = [], []
    for index, group in enumerate(current["group"]):
        seq = group["group_seq"]
        source = native_groups[seq]
        assert group["group_name"] == source["group_name"]
        assert group.get("diet_descr") == source.get("diet_descr")
        assert group.get("diet_imp") == source.get("diet_imp")
        for cell_index, (cell, original) in enumerate(zip(diet(group), diet(source))):
            canonical_suffix = "" if isinstance(group["diet_descr"]["diet"], dict) else f"/{cell_index}"
            native_suffix = "" if isinstance(source["diet_descr"]["diet"], dict) else f"/{cell_index}"
            cells.append({"consumer_seq": seq, "consumer_name": group["group_name"], "prey_seq": cell["prey_seq"],
                          "canonical_value": cell["proportion"], "native_value": original["proportion"],
                          "printed_value": None, "accepted_corrected_value": None,
                          "canonical_pointer": f"/group/{index}/diet_descr/diet{canonical_suffix}/proportion",
                          "native_pointer": f"/412/group/{native['group'].index(source)}/diet_descr/diet{native_suffix}/proportion",
                          "status": "exact_native_match; printed_source_unavailable", "transformation": "none"})
        cells.append({"consumer_seq": seq, "consumer_name": group["group_name"], "field": "diet_imp",
                      "canonical_value": group.get("diet_imp"), "native_value": source.get("diet_imp"),
                      "printed_value": None, "accepted_corrected_value": None,
                      "canonical_pointer": f"/group/{index}/diet_imp",
                      "native_pointer": f"/412/group/{native['group'].index(source)}/diet_imp",
                      "status": "exact_native_match; printed_source_unavailable", "transformation": "none"})
        internal = sum((Decimal(c["proportion"]) for c in diet(group)), Decimal(0))
        imported = Decimal(group.get("diet_imp", "0"))
        sums.append({"consumer_seq": seq, "consumer_name": group["group_name"], "native_internal_sum": str(internal),
                     "native_import": str(imported), "native_total": str(internal + imported),
                     "canonical_total": str(internal + imported), "printed_total": None,
                     "review_status": "native_preservation_verified; scientific_diet_review_unresolved",
                     "normalization_is_not_inferred_from_sum": True})
    snapshots = OUT / "original_inputs"
    snapshots.mkdir(exist_ok=True)
    snapshot = snapshots / (before[MODEL.relative_to(ROOT).as_posix()] + "_model.json")
    if not snapshot.exists():
        snapshot.write_bytes(MODEL.read_bytes())
    assert sha(snapshot) == before[MODEL.relative_to(ROOT).as_posix()]
    write("native_412_source_snapshot.json", native)
    write("diet_cell_ledger.json", cells)
    write("consumer_sums.json", sums)
    source_paths = [raw_file, LIB / "fetch_models_data.ipynb", LIB / "global_cover_jsons/35_412_Gulf_of_Thailande_(1963).json.pre-taxonomy",
                    LIB / "EwE_jsons/412_412_Gulf_of_Thailande_(1963).json", REGION / "papers/1998/35_412_Gulf_of_Thailande_(1963).json",
                    REGION / "papers/Christensen-1998/source-facts.json"]
    comparisons = []
    for p in source_paths[2:5]:
        other = {g["group_seq"]: g for g in json.loads(p.read_text(encoding="utf-8"))["group"]}
        comparisons.append({"path": p.relative_to(ROOT).as_posix(), "diet_and_import_exact_match": all(
            (g.get("diet_descr"), g.get("diet_imp")) == (other[g["group_seq"]].get("diet_descr"), other[g["group_seq"]].get("diet_imp")) for g in current["group"])})
    document = ET.fromstring(ZipFile(protected[2]).read("word/document.xml"))
    texts = [t.text or "" for t in document.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")]
    snippets = [t for t in texts if "diet" in t.lower() or "normaliz" in t.lower()]
    diagnosis = REGION / "validation_reports/35_412_Gulf_of_Thailande_(1963)/direct_diagnostics/execution_evidence.json"
    historical = json.loads(diagnosis.read_text(encoding="utf-8"))
    after = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected}
    assert before == after, "Concurrent protected-file change: re-audit required"
    write("audit_result.json", {
        "date": "2026-10-02", "unit_id": "LME_035", "selected_model_id": settings["selected_model_id"],
        "outcome": "verified_unchanged_relative_to_raw_native_source", "canonical_normalization_confirmed": False,
        "canonical_extra_normalization": "none: all diet/import strings and structures exactly match raw EcoBase accession412",
        "printed_source_faithful_claim": False, "reextraction_performed": False, "canonical_modified": False,
        "basis": "Exact native cell comparison and retained downloader code; unit sums are not the evidence for this conclusion.",
        "native_source": {"repository": "EcoBase", "accession": "412", "source_file": raw_file.relative_to(ROOT).as_posix(),
                          "download_code": "fetch_models_data.ipynb:get_model_diet_data_inner directly parses soap-client XML with xmltodict; no normalization step",
                          "endpoint": "http://sirs.agrocampus-ouest.fr/EcoBase/php/webser/soap-client.php?no_model=412"},
        "source_hashes": {p.relative_to(ROOT).as_posix(): sha(p) for p in source_paths},
        "native_snapshot_sha256": sha(OUT / "native_412_source_snapshot.json"),
        "protected_before": before, "protected_after": after, "comparison_archives": comparisons,
        "ledger_cells_including_import": len(cells), "group_count": len(sums),
        "accepted_corrections": {"diet_cell_corrections_located": [], "current_docx_diet_statements": snippets,
                                 "status": "No documented cell correction identified; all accepted current values retained."},
        "extracted_import_tables": "None for selected native accession. 1973 model imports are a different model and untouched.",
        "scientific_period": "1980 payload under inherited1963 join identity per existing eleven biomass comparisons; selection unchanged",
        "review_status": "Native preservation verified; exact printed cells and scientific diet validation unresolved; no approval inferred.",
        "runtime_policy": "Latest explicit user steering permits runtime normalization; no runtime run performed in this audit.",
        "historical_diagnostics": {"path": diagnosis.relative_to(ROOT).as_posix(), "canonical_input_sha256": historical["canonical_sha256"],
                                   "current_input_sha256": sha(MODEL), "canonical_identity_matches": historical["canonical_sha256"] == sha(MODEL),
                                   "stale_due_to_this_audit": False, "runtime_constructor_settings": historical["constructor_settings"],
                                   "note": "Historical diagnostics retained under actual saved input hash; matching hash does not establish scientific approval."},
        "source_recovery": [{"url": "https://ecobase.ecopath.org/php/protect/base_model.php?action=base&ident=&lang=&model=412&pass=&provenance=web",
                             "result": "Public card read:29groups,2fleets; conflicting1963–1964 metadata retained."},
                            {"url": "https://ecobase.ecopath.org/php/webser/soap-client.php?no_model=412", "result": "Web reader internal error; raw retained native source available."},
                            {"url": "https://sirs.agrocampus-ouest.fr/EcoBase/php/webser/soap-client.php?no_model=412", "result": "Web reader internal error; no new source bytes claimed."},
                            {"url": "https://onlinelibrary.wiley.com/doi/10.1111/j.1095-8649.1998.tb01023.x", "result": "Publisher access unavailable in web reader; existing source review reports no complete published diet table."}],
        "unresolved": "Complete printed diet/import matrix for focal1980model is not available. Native source is verified preserved, but no claim is made that EcoBase reproduces unavailable printed cells or that native values were never normalized upstream."})
    print(json.dumps({"outcome": "verified_unchanged_native", "canonical_sha256": sha(MODEL), "ledger_cells": len(cells), "protected_files_unchanged": before == after}))


if __name__ == "__main__":
    main()
