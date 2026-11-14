"""Register two unselected GOA extraction candidates; never run calculations.

Prepared for the root coordinator. No workbook writes occur without --apply. At application
time, the live workbook is reread inside central_lock. update_book operates on a
copy, which must pass preservation checks before guarded atomic replacement.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import posixpath
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "README.md").is_file() and (p / "Project.xlsx").is_file())
sys.path.insert(0, str(ROOT))
from tools.project_core.registry.writes import central_lock
from tools.project_core.workbooks.workbooks import read_book, update_book

RUN = Path(__file__).resolve().parent.parent
UNIT = "LME_002"
PAPER_ROOT = "regions/LME/LME_002/papers"
FULL_ID = "Aydin2007_Gulf_of_Alaska_1990-1994"
AGG_ID = "Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49"
PDF_SHA = "9dadd884031657e9a51741ef32a824083acf93a78c217a3a5b271fe83f3161d3"
SOURCE_COMMIT = "fe63f6d370d942ff1786f4d649e432fbfb85f81b"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REVIEW_FIELDS = ("researcher_review_status", "researcher_name", "researcher_review_date", "validation_report_path", "validation_report_sha256", "reviewed_model_sha256", "reviewed_calculation_input_sha256", "researcher_review_summary")
TABLES = (("Papers", "Papers", ("article_id",)), ("Models & coverage", "Models", ("unit_id", "model_id")))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def append_evidence(previous, addition):
    if not previous:
        return addition
    return previous if addition in str(previous) else str(previous) + "\n" + addition


def ensure_packages():
    """Authenticate the retained identities without loading a calculator."""
    evidence = {}
    for paper, model in (("GOA-2007", FULL_ID), ("GOA-2020", AGG_ID)):
        paper_dir = ROOT / PAPER_ROOT / paper
        model_path = paper_dir / "models" / model / "model.json"
        notes_path = model_path.with_name("model_notes.md")
        manifest_path = paper_dir / "source_manifest.json"
        for path in (model_path, notes_path, manifest_path):
            if not path.is_file():
                raise ValueError(f"Candidate package is not ready: {path.relative_to(ROOT)}")
        load_json(model_path)
        manifest = load_json(manifest_path)
        if model not in manifest.get("models", []):
            raise ValueError(f"{paper} source_manifest does not yet register {model}")
        for item in manifest.get("files", []):
            source_path = (paper_dir / item["path"]).resolve()
            if not source_path.is_relative_to(paper_dir.resolve()):
                raise ValueError("Source manifest path escapes paper directory")
            if not source_path.is_file() or digest(source_path) != item["sha256"]:
                raise ValueError(f"Source bytes do not match manifest: {source_path}")
        evidence[model] = {"model_path": model_path.relative_to(ROOT).as_posix(), "model_sha256": digest(model_path), "source_manifest": manifest_path.relative_to(ROOT).as_posix(), "source_manifest_sha256": digest(manifest_path), "model_notes_sha256": digest(notes_path)}
    source = ROOT / PAPER_ROOT / "GOA-2007/sources/noaa_22894_DS1-9dadd884.pdf"
    if digest(source) != PDF_SHA:
        raise ValueError("Original 2007 PDF differs from reviewed source")
    native = load_json(ROOT / PAPER_ROOT / "GOA-2020/source_manifest.json")
    if not any(f.get("commit") == SOURCE_COMMIT for f in native["files"]):
        raise ValueError("Unexpected official Rpath source revision")
    return evidence


def keyed(header, rows, keys):
    result = {}
    for row in rows:
        record = dict(zip(header, row))
        key = tuple(record.get(k) for k in keys)
        if key in result:
            raise ValueError(f"Duplicate registry key: {key}")
        result[key] = record
    return result


def build_patch(original, evidence):
    patch = deepcopy(original)
    changes = []
    paper_header, paper_rows = patch["Papers"]["Papers"]
    papers = keyed(paper_header, paper_rows, ("article_id",))
    old_key = ("GOA-2007__LME_002",)
    if old_key not in papers or papers[old_key]["unit_id"] != UNIT:
        raise ValueError("Expected GOA-2007 article row missing or mismatched")
    old_paper = papers[old_key]
    coverage = ("2026-11-14 source review: Aydin et al. (2007), printed pp.5-6 / PDF pp.15-16, gives a 291,840 km2 shelf/slope domain (50-1,000 m); nearshore waters shallower than 50 m are excluded. Target-LME overlap was not measured. The previous ratio 1 is unsupported and is cleared. Retained coverage_class, geometry descriptors and map payload are historical envelope metadata, not a verified model boundary.")
    full_dir = f"{PAPER_ROOT}/GOA-2007/models/{FULL_ID}"
    aggregate_dir = f"{PAPER_ROOT}/GOA-2020/models/{AGG_ID}"
    paper_updates = {
        "model_years": "1990-1994",
        "functional_groups": 133,
        "target_coverage_ratio": None,
        "coverage_note": append_evidence(old_paper.get("coverage_note"), coverage),
        "loadability_class": "Partial source parameter extraction retained; numerical execution NOT_RUN",
        "full_model_loadable": "Not numerically load-tested; unresolved diet allocations and source omissions retained",
        "extraction_readiness": "extracted_partial",
        "model_file_status": "extracted_parameter_package; original native model not recovered",
        "loadability_evidence": append_evidence(old_paper.get("loadability_evidence"), f"{full_dir}/model_notes.md; {full_dir}/extracted_tables/evidence/REPORT.md. Published 133-compartment extraction; unresolved preference diets and other omissions remain unknown. No SPPR/PPR execution or researcher approval."),
        "documentation_evidence": append_evidence(old_paper.get("documentation_evidence"), f"{PAPER_ROOT}/GOA-2007/source_manifest.json; original PDF SHA256 {PDF_SHA}; Appendix C GOA columns and Appendix B prose evidence retained in model-local extraction package."),
    }
    new_paper = {
        "article_id": "GOA-2020__LME_002", "unit_id": UNIT, "region_name": "Gulf of Alaska",
        "region_rank": old_paper.get("region_rank"), "atlas_region_rank": old_paper.get("atlas_region_rank"),
        "authors": "Whitehouse, G.A. and Aydin, K.Y.", "publication_year": 2020,
        "title": "Assessing the sensitivity of three Alaska marine food webs to perturbations: an example of Ecosim simulations using Rpath",
        "doi": "10.1016/j.ecolmodel.2020.109074", "landing_page": "https://repository.library.noaa.gov/view/noaa/30747",
        "model_years": "1990-1994", "functional_groups": 49, "coverage_class": "unknown", "target_coverage_ratio": None,
        "geometry_method": None, "geometry_confidence": None,
        "loadability_class": "Official native Rpath parameter extraction; numerical execution NOT_RUN",
        "full_model_loadable": "Schema-admitted sparse source parameters; no balance or calculator execution",
        "extraction_readiness": "extracted_native_parameters", "download_status": "native_inputs_verified; article_pdf_not_retained",
        "main_file_status": "local_pdf_unavailable; indexed_fulltext_read", "model_file_status": "official_native_CSVs_and_RDA_retained",
        "language": "English", "region_dir": "regions/LME/LME_002", "article_dir": f"{PAPER_ROOT}/GOA-2020",
        "source_article_id": "GOA-2020", "selected": False,
        "provenance": f"Official NOAA-EDAB/Rpath Ecosense.GOA, source commit {SOURCE_COMMIT}; {PAPER_ROOT}/GOA-2020/source_manifest.json",
        "source_urls": "https://repository.library.noaa.gov/view/noaa/30747; https://github.com/NOAA-EDAB/Rpath",
        "loadability_evidence": f"{aggregate_dir}/model_notes.md; {aggregate_dir}/extracted_tables/evidence/loader_schema_check.json; {aggregate_dir}/extracted_tables/evidence/source_to_loader_ledger.json",
        "documentation_evidence": f"{PAPER_ROOT}/GOA-2020/source_manifest.json; 49 biological groups plus one fleet; CSV extraction follows official RDA builder. RDA bytes archived, not independently decoded.",
        "coverage_note": "Article section 2.2.3 p.4 reports 291,840 km2 shelf domain, 140 W-170 W. Model period 1990-1994 is inherited from Aydin et al. (2007). Target-LME coverage fraction and precise boundary were not derived.",
        "notes": "Distinct aggregate candidate, not an exact recovery of the published 133-compartment model. Native NA cells, unknown EE/detritus biomass and zero detritus-fate rows are preserved. No scientific solve, selection, researcher review or production eligibility. Article PDF retrieval returned 403; source membership pending visual verification; numeric inputs are authenticated local native files.",
    }

    def apply_row(sheet, table, keys, desired, only_if_new=False):
        header, rows = patch[sheet][table]
        if set(desired) - set(header):
            raise ValueError(f"Unrecognized registry fields: {set(desired) - set(header)}")
        record_key = tuple(desired[k] for k in keys)
        matches = [i for i, row in enumerate(rows) if tuple(row[header.index(k)] for k in keys) == record_key]
        if len(matches) > 1:
            raise ValueError(f"Duplicate candidate key: {record_key}")
        if matches:
            i = matches[0]
            current = dict(zip(header, rows[i]))
            if only_if_new:
                # An existing target might have received curation after staging.
                # Exact replay is allowed; do not overwrite a changed target.
                conflicts = {k: (current.get(k), v) for k, v in desired.items() if current.get(k) != v}
                if conflicts:
                    raise ValueError(f"Candidate already exists with differing metadata; reconcile manually: {record_key}: {conflicts}")
                return
        else:
            i = len(rows)
            rows.append([None] * len(header))
        for field, value in desired.items():
            col = header.index(field)
            previous = rows[i][col]
            if previous != value:
                changes.append({"sheet": sheet, "table": table, "key": list(record_key), "field": field, "before": previous, "after": value, "row_index": i, "column_index": col})
                rows[i][col] = value

    apply_row("Papers", "Papers", ("article_id",), {"article_id": old_key[0], **paper_updates})
    apply_row("Papers", "Papers", ("article_id",), new_paper, only_if_new=True)
    for paper, model, year, variant in (("GOA-2007", FULL_ID, 2007, "published_Appendix_C_133_compartments_partial"), ("GOA-2020", AGG_ID, 2020, "official_Rpath_49_biological_groups_plus_1_fleet")):
        desired = {
            "unit_id": UNIT, "model_id": model, "model_path": evidence[model]["model_path"],
            "source_filename": "noaa_22894_DS1-9dadd884.pdf" if year == 2007 else "Ecosense_GOA_base.csv; Ecosense_GOA_diet.csv; Ecosense_GOA_pedigree.csv; Ecosense.GOA.rda",
            "selected": False, "selection_rationale": None, "paper_ids": f"{paper}__{UNIT}",
            "model_year": "1990-1994", "variant": variant, "model_area_km2": 291840,
            "availability": "extracted_partial_NOT_RUN" if year == 2007 else "native_parameters_extracted_NOT_RUN",
            "publication_year": year, "model_years": "1990-1994", "target_coverage_ratio": None,
            "coverage_class": "unknown", "doi": None if year == 2007 else "10.1016/j.ecolmodel.2020.109074",
            "coverage_note": coverage if year == 2007 else new_paper["coverage_note"],
            "atlas_region_rank": old_paper.get("atlas_region_rank"), "production_eligible": False,
            "canonical_source_path": evidence[model]["model_path"],
            "canonical_source_sha256": evidence[model]["model_sha256"],
            "diagnostic_grades": json.dumps({method: {"status": "NOT_RUN", "reason": "Extraction-only candidate; no numerical diagnostics executed"} for method in ("GE", "TE", "With Egestion")}, separators=(",", ":")),
            **{field: None for field in REVIEW_FIELDS},
        }
        apply_row("Models & coverage", "Models", ("unit_id", "model_id"), desired, only_if_new=True)
    # This asserts every old row by stable key, including unchanged target fields.
    allowed = {(c["sheet"], tuple(c["key"]), c["field"]) for c in changes}
    for sheet, table, keys in TABLES:
        old_header, old_rows = original[sheet][table]
        header, rows = patch[sheet][table]
        if header != old_header:
            raise AssertionError("Registry header change is not authorized")
        updated = keyed(header, rows, keys)
        for key, before in keyed(old_header, old_rows, keys).items():
            for field, value in before.items():
                if (sheet, key, field) not in allowed and updated[key][field] != value:
                    raise AssertionError(f"Unrelated field changed: {sheet}/{key}/{field}")
    return patch, changes


def workbook_snapshot(path):
    """Cell-level semantic snapshot across all worksheets, including manual cells."""
    with zipfile.ZipFile(path) as z:
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            strings = ["".join(n.itertext()) for n in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        book = ET.fromstring(z.read("xl/workbook.xml"))
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        result = {}
        for sheet in book.find("m:sheets", NS):
            target = rels[sheet.attrib[f"{{{NS['r']}}}id"]]
            member = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            tree = ET.fromstring(z.read(member))
            rel_member = posixpath.dirname(member) + "/_rels/" + posixpath.basename(member) + ".rels"
            sheet_rels = {}
            if rel_member in z.namelist():
                sheet_rels = {r.attrib["Id"]: r.attrib for r in ET.fromstring(z.read(rel_member))}
            links = {}
            for link in tree.findall("m:hyperlinks/m:hyperlink", NS):
                attrs = dict(link.attrib)
                rel_id = attrs.pop(f"{{{NS['r']}}}id", None)
                relation = sheet_rels.get(rel_id, {})
                links[attrs["ref"]] = (tuple(sorted(attrs.items())), relation.get("Target"), relation.get("TargetMode"))
            comments = {}
            for relation in sheet_rels.values():
                if relation.get("Type", "").endswith("/comments"):
                    comment_target = relation["Target"]
                    comment_member = comment_target.lstrip("/") if comment_target.startswith("/") else posixpath.normpath(posixpath.dirname(member) + "/" + comment_target)
                    comment_tree = ET.fromstring(z.read(comment_member))
                    authors = [a.text for a in comment_tree.findall("m:authors/m:author", NS)]
                    for comment in comment_tree.findall("m:commentList/m:comment", NS):
                        comments[comment.attrib["ref"]] = (authors[int(comment.attrib["authorId"])], "".join(comment.find("m:text", NS).itertext()))
            cells = {}
            for cell in tree.findall("m:sheetData/m:row/m:c", NS):
                value_node = cell.find("m:v", NS)
                value = value_node.text if value_node is not None else None
                kind = cell.get("t", "n")
                if kind == "s":
                    kind, value = "str", strings[int(value)]
                elif kind in ("inlineStr", "str"):
                    kind = "str"
                    inline = cell.find("m:is", NS)
                    if inline is not None:
                        value = "".join(inline.itertext())
                elif kind == "n" and value is not None:
                    value = str(Decimal(value).normalize())
                formula = cell.find("m:f", NS)
                coord = cell.attrib["r"]
                if formula is None and value in (None, ""):
                    kind, value = "blank", None
                    if cell.get("s", "0") == "0" and coord not in links and coord not in comments:
                        continue
                cells[coord] = (kind, value, cell.get("s", "0"), None if formula is None else (formula.text, tuple(sorted(formula.attrib.items()))), links.get(coord), comments.get(coord))
            result[sheet.attrib["name"]] = cells
        return result


def permitted_coordinates(path, changes):
    import openpyxl
    from openpyxl.utils import get_column_letter
    wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
    try:
        starts = {}
        for sheet, table, _ in TABLES:
            for row in wb[sheet].iter_rows():
                if row[0].value == "@table" and row[1].value == table:
                    starts[(sheet, table)] = row[0].row
                    break
        return {(c["sheet"], f"{get_column_letter(c['column_index'] + 1)}{starts[c['sheet'], c['table']] + 2 + c['row_index']}") for c in changes}
    finally:
        wb.close()


def verify_preservation(before, after, allowed):
    if list(before) != list(after):
        raise AssertionError("Worksheet names/order changed")
    for sheet, cells in before.items():
        for coord, state in cells.items():
            if (sheet, coord) not in allowed and state != after[sheet].get(coord):
                raise AssertionError(f"Unrelated cell changed: {sheet}!{coord}")
        for coord, state in after[sheet].items():
            if coord not in cells and (sheet, coord) not in allowed and state[1] is not None:
                raise AssertionError(f"Unexpected new cell: {sheet}!{coord}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply the guarded metadata-only patch; default prints the proposed edits")
    args = parser.parse_args()
    target = ROOT / "Project.xlsx"
    with central_lock(ROOT):
        before_sha = digest(target)
        original = read_book(target, sheets=["Papers", "Models & coverage"])
        evidence = ensure_packages()
        patch, changes = build_patch(original, evidence)
        report = {"scope": "metadata_only_two_unselected_candidates", "before_sha256": before_sha, "source_evidence": evidence, "changes": changes, "unrelated_values_preserved": True, "regional_workbook_map_selection_PPR_writes": False}
        if not args.apply:
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return
        if not changes:
            print("No changes: both candidates are already registered with identical metadata.")
            return
        before_cells = workbook_snapshot(target)
        allowed = permitted_coordinates(target, changes)
        qa = RUN / "qa"
        qa.mkdir(exist_ok=True)
        backup = qa / f"Project.before_candidate_registration.{before_sha}.xlsx"
        if backup.exists() and digest(backup) != before_sha:
            raise ValueError("Existing backup does not match its content-addressed name")
        fd, name = tempfile.mkstemp(prefix=".candidate-registry-", suffix=".xlsx", dir=target.parent)
        os.close(fd)
        staged = Path(name)
        try:
            shutil.copy2(target, staged)
            if digest(staged) != before_sha or digest(target) != before_sha:
                raise ValueError("Live workbook changed before staging; reread and reconcile")
            if not backup.exists():
                shutil.copy2(staged, backup)
            if digest(backup) != before_sha:
                raise ValueError("Backup does not match the verified baseline")
            update_book(staged, patch)
            if read_book(staged, sheets=list(patch)) != patch:
                raise AssertionError("Staged registry differs from the proposed keyed patch")
            verify_preservation(before_cells, workbook_snapshot(staged), allowed)
            # A package changed while registration was staged: re-review, don't relabel.
            if ensure_packages() != evidence:
                raise ValueError("Candidate package changed during staging")
            if digest(target) != before_sha:
                raise ValueError("Live Project.xlsx changed; staged update not applied")
            after_sha = digest(staged)
            os.replace(staged, target)
            if digest(target) != after_sha:
                raise AssertionError("Applied workbook hash mismatch")
            report.update({"status": "applied", "after_sha256": after_sha, "backup": backup.relative_to(ROOT).as_posix(), "applied_utc": datetime.now(timezone.utc).isoformat(), "cell_preservation_verified": True})
            (qa / "candidate_registration_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"status": "applied", "changed_cells": len(changes), "before_sha256": before_sha, "after_sha256": after_sha, "report": (qa / "candidate_registration_report.json").relative_to(ROOT).as_posix()}, indent=2))
        finally:
            staged.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
