"""Narrow, lossless Office-package hyperlink styling for retained review files.

Only hyperlink text color and underline change. Values, formulas, destinations,
manual wording, views, filters, figures and scientific inputs remain untouched.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
BLUE = "0563C1"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_package(path):
    with ZipFile(path) as archive:
        return archive.infolist(), {item.filename: archive.read(item) for item in archive.infolist()}


def save_package(path, members, contents):
    temporary = path.with_name(path.name + ".link-style-tmp")
    with ZipFile(temporary, "w") as archive:
        for item in members:
            archive.writestr(item, contents[item.filename])
    temporary.replace(path)


def xml_bytes(root):
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True, standalone=True)


def word_links(path):
    members, old = load_package(path)
    new = dict(old)
    changed_runs = 0
    for name, data in old.items():
        if not re.fullmatch(r"word/(document|header\d+|footer\d+|footnotes|endnotes)\.xml", name):
            continue
        root = ET.fromstring(data)
        modified = False
        for hyperlink in root.iter(W + "hyperlink"):
            for run in hyperlink.iter(W + "r"):
                if not list(run.iter(W + "t")):
                    continue
                props = run.find(W + "rPr")
                if props is None:
                    props = ET.Element(W + "rPr")
                    run.insert(0, props)
                color = props.find(W + "color")
                underline = props.find(W + "u")
                already = color is not None and color.get(W + "val") == BLUE and underline is not None and underline.get(W + "val") == "single"
                if already:
                    continue
                if color is None:
                    color = ET.SubElement(props, W + "color")
                color.attrib.clear()
                color.set(W + "val", BLUE)
                if underline is None:
                    underline = ET.SubElement(props, W + "u")
                underline.attrib.clear()
                underline.set(W + "val", "single")
                changed_runs += 1
                modified = True
        if modified:
            before_text = list(ET.fromstring(data).itertext())
            assert before_text == list(root.itertext()), "Text changed during styling"
            new[name] = xml_bytes(root)
    return finalize(path, members, old, new, changed_runs)


def excel_links(path):
    members, old = load_package(path)
    new = dict(old)
    styles = ET.fromstring(old["xl/styles.xml"])
    fonts = styles.find(S + "fonts")
    formats = styles.find(S + "cellXfs")
    new_styles = {}
    changed_cells = 0
    for name, data in old.items():
        if not re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name):
            continue
        root = ET.fromstring(data)
        cells = {cell.get("r"): cell for cell in root.findall(".//" + S + "sheetData/" + S + "row/" + S + "c")}
        references = {link.get("ref") for link in root.findall(S + "hyperlinks/" + S + "hyperlink")}
        for reference, cell in cells.items():
            formula = cell.find(S + "f")
            if formula is not None and re.search(r"\bHYPERLINK\s*\(", formula.text or "", re.I):
                references.add(reference)
        modified = False
        for reference in sorted(references):
            if reference not in cells:
                raise ValueError(f"Unsupported absent/range hyperlink cell: {path}/{name}/{reference}")
            cell = cells[reference]
            style_id = int(cell.get("s", "0"))
            source_style = formats[style_id]
            font = fonts[int(source_style.get("fontId", "0"))]
            color = font.find(S + "color")
            underline = font.find(S + "u")
            if color is not None and color.get("rgb", "")[-6:] == BLUE and underline is not None and underline.get("val", "single") == "single":
                continue
            if style_id not in new_styles:
                styled_font = copy.deepcopy(font)
                color = styled_font.find(S + "color")
                underline = styled_font.find(S + "u")
                if color is None:
                    color = ET.SubElement(styled_font, S + "color")
                color.attrib.clear()
                color.set("rgb", "FF" + BLUE)
                if underline is None:
                    underline = ET.SubElement(styled_font, S + "u")
                underline.attrib.clear()
                underline.set("val", "single")
                font_id = len(fonts)
                fonts.append(styled_font)
                styled_format = copy.deepcopy(source_style)
                styled_format.set("fontId", str(font_id))
                styled_format.set("applyFont", "1")
                new_styles[style_id] = len(formats)
                formats.append(styled_format)
            cell.set("s", str(new_styles[style_id]))
            changed_cells += 1
            modified = True
        if modified:
            original = ET.fromstring(data)
            for c in original.iter(S + "c"):
                c.attrib.pop("s", None)
            structural_check = copy.deepcopy(root)
            for c in structural_check.iter(S + "c"):
                c.attrib.pop("s", None)
            assert ET.tostring(original) == ET.tostring(structural_check), "Non-style worksheet content changed"
            new[name] = xml_bytes(root)
    if changed_cells:
        fonts.set("count", str(len(fonts)))
        formats.set("count", str(len(formats)))
        new["xl/styles.xml"] = xml_bytes(styles)
    return finalize(path, members, old, new, changed_cells)


def finalize(path, members, old, new, changes):
    changed_parts = [name for name in old if old[name] != new[name]]
    relationships = [name for name in old if name.endswith(".rels")]
    assert all(old[name] == new[name] for name in relationships)
    before_hash = digest(path.read_bytes())
    if changes:
        save_package(path, members, new)
    _, reopened = load_package(path)
    assert reopened == new
    return {"path": path.relative_to(ROOT).as_posix(), "before_sha256": before_hash,
            "after_sha256": digest(path.read_bytes()), "changed_hyperlink_text_items": changes,
            "changed_package_parts": changed_parts, "all_relationships_preserved": True,
            "package_reopened_exactly": True, "scientific_rerun": False}


if __name__ == "__main__":
    findings = []
    for unit in ("LME_032", "LME_034", "LME_036"):
        directory = ROOT / "regions" / unit
        for report in directory.glob("Model_validation_*.docx"):
            findings.append(word_links(report))
        for appendix in directory.glob("*taxon_mapping_appendix.xlsx"):
            findings.append(excel_links(appendix))
    (HERE / "existing_package_link_style_changes.json").write_text(json.dumps(findings, indent=2), encoding="utf-8")
    print(json.dumps(findings))
