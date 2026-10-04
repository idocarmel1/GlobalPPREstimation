"""Record the completed manual inspection; no document or scientific mutations."""
from pathlib import Path
import hashlib
import json
import os
from datetime import datetime, timezone
import pypdfium2 as pdfium

E = Path(__file__).resolve().parent
R = E.parents[3]
C = E.parents[1] / "models/52_GM2019_Fig9_Pelagic_(2000-2014)"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

spec = read(E / "report_inputs.json")
content = read(E / "report_content_verification.json")
reports = []
for name, filename_key, expected_pages in (("validation", "validation_filename", 10), ("departures", "departures_filename", 19)):
    docx = E.parents[1] / spec[filename_key]
    pdf = E / "qa" / name / "report.pdf"
    document = pdfium.PdfDocument(str(pdf))
    assert len(document) == expected_pages
    document.close()
    assert sha(docx) == content["report_hashes"][docx.name]
    pages = []
    for number in range(1, expected_pages + 1):
        path = E / "qa" / name / f"page-{number}.png"
        assert path.is_file()
        finding = "PASS: legible text and numeric columns; no clipping, overlaps, blank pages or stranded headers; coherent page continuation."
        if name == "validation" and number in (9, 10):
            finding = "PASS: geographic figure, title and caption stay together; source pixels and explanatory text are readable."
        if name == "validation" and number in (5, 6, 7, 8):
            finding = "PASS: all grouped Very low labels and explanations are readable; headers repeat; rows remain intact."
        if name == "departures" and number == 7:
            finding = "PASS: final widened EE column keeps the previously wrapped 0.0797462 value on one line; all solved budget values and case header are legible."
        if name == "departures" and number >= 10 and number <= 18:
            finding = "PASS: exhaustive changed-cell rows remain intact, repeat column headers and display complete before/after values; page number is correct."
        pages.append({"page":number,"image_path":path.relative_to(E).as_posix(),"sha256":sha(path),"reviewed":True,"finding":finding})
    reports.append({"short_name":name,"docx_path":docx.relative_to(R).as_posix(),"docx_sha256":sha(docx),"pdf_path":pdf.relative_to(E).as_posix(),"pdf_sha256":sha(pdf),"page_count":expected_pages,"pages":pages})

qa = {
    "schema_version":1,"recorded_utc":datetime.now(timezone.utc).isoformat(),
    "all_pages_inspected":True,"total_final_pages":29,
    "review_method":"Direct visual inspection of every final page PNG through view_image after the final DOCX rebuild and read-only export.",
    "renderer":"Independent hidden Word COM instance, macros disabled, DOCX opened read-only, PDF export, close without saving; PDFium rasterization at 1.7 scale. Packaged LibreOffice renderer unavailable on this host.",
    "checks":{"all_final_pages_viewed":True,"no_clipping_or_overlapping_text":True,"numeric_values_legible":True,"repeated_table_headers":True,"figures_and_captions_together":True,"no_blank_pages":True,"researcher_review_fields_undecided":True,"departures_dynamic_page_numbers_correct":True},
    "repairs":"Earlier table/header and page-number issues corrected. Final repair widened the solved-budget EE column; the exact final page 7 was then re-inspected.",
    "reports":reports,
    "human_validated":False,
}
(E/"visual_inspection.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf-8")

gate = read(E / "map_alignment_confirmed.json")
gate["authority"] = "Root independently verified the adopted frozen model, regional workbook, exact annual/map payload and live browser values, and authorized removal of pending alignment wording."
gate["recorded_utc"] = datetime.now(timezone.utc).isoformat()
gate["proofs"] = []
for name in ("map_build_execution.json", "map_verification_execution.json", "browser_verification.json", "final_layout_refresh.json"):
    path = C / "research_20261003/completion_integration" / name
    gate["proofs"].append({"path":Path(os.path.relpath(path,E)).as_posix(),"sha256":sha(path),"result":read(path)})
(E/"map_alignment_confirmed.json").write_text(json.dumps(gate,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"all_pages_inspected":True,"page_counts":{r["short_name"]:r["page_count"] for r in reports},"visual_inspection_sha256":sha(E/"visual_inspection.json"),"docx_hashes":content["report_hashes"]}))
