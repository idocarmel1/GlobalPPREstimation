"""Build the two adopted-model reports from an explicit, reviewed input record.

The input record is report provenance, never selection/configuration authority.
Uses current template and preserves the old researcher's SPPR cell as OOXML.
"""
from pathlib import Path
from copy import deepcopy
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import Inches, Pt, RGBColor

EVIDENCE = Path(__file__).resolve().parent
REPO = EVIDENCE.parents[3]
REGION = EVIDENCE.parents[1]
sys.path.insert(0, str(REPO / "tools"))
from validation_percentage_format import format_percent, verify_report


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fmt(value):
    if value is None:
        return "?"
    if isinstance(value, float):
        return f"{value:,.7g}"
    return str(value)


def set_link(paragraph, label, target):
    node = OxmlElement("w:hyperlink")
    if target.startswith("#"):
        node.set(qn("w:anchor"), target[1:])
    else:
        node.set(qn("r:id"), paragraph.part.relate_to(target, RT.HYPERLINK, is_external=True))
    run = OxmlElement("w:r")
    properties = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    properties.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    properties.append(underline)
    run.append(properties)
    text = OxmlElement("w:t")
    text.text = label
    run.append(text)
    node.append(run)
    paragraph._p.append(node)


def paragraph_content(paragraph, content):
    paragraph.clear()
    if isinstance(content, str):
        paragraph.add_run(content)
    else:
        for chunk in content:
            if isinstance(chunk, str):
                paragraph.add_run(chunk)
            elif "target" in chunk:
                set_link(paragraph, chunk["text"], chunk["target"])
            else:
                run = paragraph.add_run(chunk["text"])
                run.bold = chunk.get("bold", False)


def fill_cell(cell, lines):
    if isinstance(lines, str):
        lines = lines.split("\n")
    cell.text = ""
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        paragraph_content(p, line)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP


def repeat_header(row):
    pr = row._tr.get_or_add_trPr()
    item = OxmlElement("w:tblHeader")
    pr.append(item)
    for cell in row.cells:
        for paragraph in cell.paragraphs:
            paragraph.paragraph_format.keep_with_next = True


def no_row_split(row):
    pr = row._tr.get_or_add_trPr()
    item = OxmlElement("w:cantSplit")
    pr.append(item)


def rows(table, records, prevent_split=True):
    for row in list(table.rows)[1:]:
        table._tbl.remove(row._tr)
    repeat_header(table.rows[0])
    for record in records:
        row = table.add_row()
        for cell, value in zip(row.cells, record):
            fill_cell(cell, [fmt(value)])
        if prevent_split:
            no_row_split(row)


def add_table(doc, headers, records, widths=None, size=9):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for i, title in enumerate(headers):
        table.rows[0].cells[i].text = title
        table.rows[0].cells[i].paragraphs[0].runs[0].bold = True
    rows(table, records)
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            if widths:
                cell.width = Inches(widths[i])
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.space_before = Pt(0)
                for r in p.runs:
                    r.font.size = Pt(size)
    if widths:
        for col, width in zip(table.columns, widths):
            col.width = Inches(width)
    return table


def append_block(doc, block):
    if block.get("page_break"):
        doc.add_page_break()
    if "heading" in block:
        doc.add_heading(block["heading"], level=block.get("level", 1))
    for text in block.get("paragraphs", []):
        paragraph_content(doc.add_paragraph(), text)
    if "headers" in block:
        add_table(doc, block["headers"], block["rows"], block.get("widths"), block.get("font_size", 9))


def link_checks(path):
    ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships",
          "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    found = []
    with ZipFile(path) as archive:
        for name in archive.namelist():
            if name.endswith(".rels"):
                xml = ET.fromstring(archive.read(name))
                for rel in xml:
                    if not rel.attrib.get("Type", "").endswith("/hyperlink"):
                        continue
                    target = rel.attrib["Target"]
                    if urlsplit(target).scheme in ("https", "http", "mailto") or target.startswith("#"):
                        found.append({"target": target, "kind": "public or internal"})
                        continue
                    assert not target.startswith(("file:", "//", "\\")), target
                    assert not (len(target)>1 and target[1] == ":"), target
                    file_part = unquote(target.split("#", 1)[0]).replace("\\", "/")
                    resolved = (path.parent / file_part).resolve()
                    assert resolved.exists(), f"Missing local report link {target}"
                    relative = resolved.relative_to(REPO)
                    # Relocate the relevant complete relative directory hierarchy.
                    task_relocated_root = EVIDENCE / "qa" / "relocated_repository"
                    relocated_report_dir = task_relocated_root / path.parent.relative_to(REPO)
                    relocated_target = (relocated_report_dir / file_part).resolve()
                    assert relocated_target == (task_relocated_root / relative).resolve()
                    if resolved.is_file():
                        relocated_target.parent.mkdir(parents=True, exist_ok=True)
                        if not relocated_target.exists() or sha(relocated_target) != sha(resolved):
                            relocated_target.write_bytes(resolved.read_bytes())
                        assert sha(relocated_target) == sha(resolved)
                    else:
                        relocated_target.mkdir(parents=True, exist_ok=True)
                    found.append({"target": target, "kind": "local relative", "repo_path": relative.as_posix(), "exists_after_relocation": relocated_target.exists()})
        for n in archive.namelist():
            if n == "docProps/app.xml":
                properties = ET.fromstring(archive.read(n))
                assert not any((item.text or "").strip() for item in properties.iter() if item.tag.endswith("}HyperlinkBase")), "Machine-specific hyperlink base"
        docxml = ET.fromstring(archive.read("word/document.xml"))
        appearance = []
        for h in docxml.findall(".//w:hyperlink", ns):
            for run in h.findall("w:r", ns):
                pr = run.find("w:rPr", ns)
                assert pr is not None
                color = pr.find("w:color", ns)
                underline = pr.find("w:u", ns)
                assert color is not None and color.attrib.get(qn("w:val")) in ("0563C1", "0000FF"), "Link is not blue"
                assert underline is not None and underline.attrib.get(qn("w:val")) != "none", "Link not underlined"
                appearance.append("".join(run.itertext()))
    return {"links": found, "blue_underlined_runs": len(appearance)}


def build_validation(spec, old):
    doc = Document(REPO / "tools/templates/Model_validation_template.docx")
    template_tables = list(doc.tables)
    initial_paragraphs = list(doc.paragraphs)
    paragraph_content(initial_paragraphs[0], "Sea of Okhotsk pelagic model validation")
    initial_paragraphs[0].style = doc.styles["Title"]
    for run in initial_paragraphs[0].runs:
        run.font.color.rgb = RGBColor(0, 0, 0)
        run.font.underline = False
    paragraph_content(initial_paragraphs[1], spec["opening"])
    main = template_tables[0]
    main._tbl.addprevious(initial_paragraphs[1]._p)
    for row in list(main.rows)[1:]:
        field = row.cells[0].text.strip()
        if field != "SPPR calculation":
            fill_cell(row.cells[1], spec["validation_fields"][field])
    repeat_header(main.rows[0])
    # Preserve the entire manually maintained SPPR entry, properties and links.
    old_cell = next(r.cells[1] for r in old.tables[0].rows if r.cells[0].text.strip() == "SPPR calculation")
    new_cell = next(r.cells[1] for r in main.rows if r.cells[0].text.strip() == "SPPR calculation")
    copied = deepcopy(old_cell._tc)
    for h in copied.iter(qn("w:hyperlink")):
        rid = h.get(qn("r:id"))
        if rid:
            rel = old.part.rels[rid]
            h.set(qn("r:id"), doc.part.relate_to(rel.target_ref, RT.HYPERLINK, is_external=True))
    new_cell._tc.getparent().replace(new_cell._tc, copied)
    coverage = spec["coverage"]
    replacements = {
        3: coverage["reference"], 4: coverage["inventory"], 5: coverage["total"],
        6: coverage.get("missing", ""), 7: coverage["method"], 8: coverage["appendix_link"],
        9: "Overall confidence uses the weaker required membership or allocation component.",
        11: coverage["membership_evidence"], 13: coverage["weight_evidence"],
        14: "Each percentage is the independent simple-chain PPR associated with taxa using that rule.",
        15: coverage["uncertainty"], 19: spec["geography"]["introduction"],
        21: spec["geography"]["target_caption"], 23: spec["geography"]["study_caption"], 24: ""
    }
    for index, text in replacements.items():
        paragraph_content(initial_paragraphs[index], text)
    rows(template_tables[1], coverage["confidence_rows"])
    rows(template_tables[2], coverage["membership_rows"])
    rows(template_tables[3], coverage["allocation_rows"])
    if coverage["very_low_rows"]:
        rows(template_tables[4], coverage["very_low_rows"])
    else:
        template_tables[4]._tbl.getparent().remove(template_tables[4]._tbl)
        paragraph_content(initial_paragraphs[16], "Very low decisions none")
    initial_paragraphs[18].paragraph_format.page_break_before = True
    for table, image_spec in zip(template_tables[5:7], spec["geography"]["images"]):
        table.rows[0].cells[0].text = image_spec["title"]
        cell = table.rows[1].cells[0]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(REPO / image_spec["path"]), width=Inches(image_spec["width"]))
        no_row_split(table.rows[1])
    initial_paragraphs[22].paragraph_format.page_break_before = True
    path = REGION / spec["validation_filename"]
    doc.save(path)
    verify_report(path)
    return path, deepcopy(copied)


def build_departures(spec):
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.left_margin = section.right_margin = Inches(0.65)
    section.top_margin = section.bottom_margin = Inches(0.62)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    run = OxmlElement("w:r")
    properties = OxmlElement("w:rPr")
    size = OxmlElement("w:sz")
    size.set(qn("w:val"), "18")
    properties.append(size)
    run.append(properties)
    value = OxmlElement("w:t")
    value.text = "1"
    run.append(value)
    field.append(run)
    footer._p.append(field)
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10)
    normal.paragraph_format.space_after = Pt(6)
    for name in ("Title", "Heading 1", "Heading 2"):
        doc.styles[name].font.color.rgb = RGBColor(0, 0, 0)
        doc.styles[name].font.name = "Calibri"
        for border in list(doc.styles[name].element.iter(qn("w:pBdr"))):
            border.getparent().remove(border)
    title = doc.add_paragraph("Sea of Okhotsk pelagic reconstruction departures", style="Title")
    title.paragraph_format.space_after = Pt(12)
    for line in spec["departures_opening"]:
        paragraph_content(doc.add_paragraph(), line)
    for block in spec["departures_blocks"]:
        append_block(doc, block)
    path = REGION / spec["departures_filename"]
    doc.save(path)
    verify_report(path)
    return path


def main():
    spec = json.loads((EVIDENCE / "report_inputs.json").read_text(encoding="utf-8"))
    old_path = REGION / "Model_validation_52_1_Sea_of_Okhotsk_NE_(1980).docx"
    old_before = sha(old_path)
    template_before = sha(REPO / "tools/templates/Model_validation_template.docx")
    old = Document(old_path)
    manual = {}
    for row in old.tables[0].rows:
        if row.cells[0].text in ("SPPR calculation", "Open issues and next action", "Review and reproducibility"):
            manual[row.cells[0].text] = {"text": row.cells[1].text, "xml": row.cells[1]._tc.xml}
    (EVIDENCE / "inherited_manual_fields.json").write_text(json.dumps({"source_model_id": "52_1_Sea_of_Okhotsk_NE_(1980)", "source_sha256":old_before,"fields":manual,"new_record_treatment":"Exact SPPR cell preserved. Old-model SD-sensitivity action and old review identity retained here only; new model action and signoff remain researcher fields."}, ensure_ascii=False, indent=2), encoding="utf-8")
    validation, copied_sppr = build_validation(spec, old)
    departures = build_departures(spec)
    assert sha(old_path) == old_before, "Researcher original changed"
    assert sha(REPO / "tools/templates/Model_validation_template.docx") == template_before, "Template changed"
    loaded = Document(validation)
    final_sppr = next(r.cells[1] for r in loaded.tables[0].rows if r.cells[0].text.strip() == "SPPR calculation")
    assert ET.tostring(ET.fromstring(final_sppr._tc.xml)) == ET.tostring(ET.fromstring(copied_sppr.xml)), "SPPR cell not preserved"
    checks = {"source_researcher_report_unchanged": True, "template_unchanged": True, "exact_sppr_cell_preserved": True,
              "adopted_model_id": spec["model_id"], "reports":[]}
    for path in (validation, departures):
        checks["reports"].append({"path":path.relative_to(REPO).as_posix(),"sha256":sha(path),"links":link_checks(path)})
    (EVIDENCE / "document_structural_verification.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"reports":[x["path"] for x in checks["reports"]],"checks_pass":True}))


if __name__ == "__main__":
    main()
