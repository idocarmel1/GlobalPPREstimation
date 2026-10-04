import datetime as dt
import json
from pathlib import Path
from collections import Counter

RUN = Path(__file__).resolve().parents[1]
meta = RUN / "qa/old_word_trial.json"
data = json.loads(meta.read_text(encoding="utf-8"))
rows = [json.loads(line) for line in (RUN / "qa/old_word_trace.jsonl").read_text(encoding="utf-8").splitlines()]
def stats(items):
    return {
        "content_read_operations": len(items),
        "content_bytes_read": sum(x.get("bytes", 0) for x in items),
        "workbook_parses": sum(x.get("workbook_parses", 0) for x in items),
        "reader_seconds": sum(x.get("elapsed_seconds", 0) for x in items),
        "unique_paths": len(set(x["path"] for x in items)),
        "operations_by_type": dict(Counter(x["operation"] for x in items)),
    }
excluded = [x for x in rows if x["path"].replace("\\", "/").endswith("tools/skills/paper-to-ppr/SKILL.md")]
included = [x for x in rows if x not in excluded]
assert len(excluded) == 1
data["measurement"] = {
    "raw_trace_totals": stats(rows),
    "matched_reference_totals_excluding_version_crossing": stats(included),
    "excluded_version_crossing_rows": excluded,
    "path_read_multiplicity": dict(Counter(x["path"] for x in rows)),
    "note": "Raw observed totals include transport-truncation rereads and the repeated Overview full-reader parse. No efficiency comparison is asserted by this trial.",
}
data["render"]["all_pages_visually_inspected"] = True
data["render"]["visual_inspection"] = {
    "pages": [1,2,3,4,5,6], "image_open_count":6, "detail":"original",
    "result":"All six final pages readable; no clipped text, overlaps, broken tables, missing figures, blank pages or page-flow change.",
    "unchanged_pixels_outside_heading":True,
    "before_after_page_count_equal":True,
}
for operation in data["operations"]:
    if operation["kind"] == "packaged_render_attempt":
        end = dt.datetime.fromisoformat(operation.pop("timestamp_start"))
        operation["timestamp_end"] = end.isoformat()
        operation["timestamp_start_reconstructed"] = (end - dt.timedelta(seconds=operation["seconds"])).isoformat()
data["operations"] += [
    {"timestamp":dt.datetime.now(dt.timezone.utc).isoformat(),"kind":"visual_inspection","image_open_count":6,"pages":6,"result":"pass"},
    {"timestamp":dt.datetime.now(dt.timezone.utc).isoformat(),"kind":"binary_metadata_and_capability_probes",
     "filesystem_inventory_commands":3,"runtime_import_probes":2,"process_inventory_commands":1,
     "trace_cli_help_commands":1,"source_content_not_inspected_by_probes":True}
]
data["applicability"] = {
    "heading_edit":"performed",
    "full_report_render_and_all_page_review":"performed",
    "package_manual_cells_links_styles_text_preservation":"performed",
    "linked_appendix_and_regional_central_workbook_bytes":"verified exact unchanged",
    "fresh_appendix_scientific_reassessment":"inapplicable to expressly bounded wording edit",
    "whole_source_scientific_review":"inapplicable and not performed",
    "extraction_solver_mapping_selection_adoption_project_map_writes":"not authorized and not performed",
}
data["end_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
data["wall_clock_seconds"] = (dt.datetime.fromisoformat(data["end_utc"]) - dt.datetime.fromisoformat(data["start_utc"])).total_seconds()
data["completed"] = True
data["limitations"] = [
    "Packaged LibreOffice rendering unavailable; independent hidden Word export plus bundled Poppler supplied full rendering.",
    "Bundled PyMuPDF unavailable; bundled Poppler supplied rasterization.",
    "One current revised pipeline entry was read before its OLD checkpoint was supplied; recorded separately and excluded from matched reference totals, while retained in raw totals.",
    "Early output truncation and one lost asynchronous read result caused repeated measured reads; raw totals retain them.",
    "A failed PowerShell 7 COM attempt had no usable Hwnd before any document open; existing processes were left untouched. Successful Windows PowerShell instance ownership was proved by a single new PID and it was quit."
]
meta.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps({"completed":data["completed"],"start_utc":data["start_utc"],"end_utc":data["end_utc"],
                  "wall_clock_seconds":data["wall_clock_seconds"],"measurement":data["measurement"]["raw_trace_totals"],
                  "matched":data["measurement"]["matched_reference_totals_excluding_version_crossing"],
                  "qa":str(meta)},ensure_ascii=False))
