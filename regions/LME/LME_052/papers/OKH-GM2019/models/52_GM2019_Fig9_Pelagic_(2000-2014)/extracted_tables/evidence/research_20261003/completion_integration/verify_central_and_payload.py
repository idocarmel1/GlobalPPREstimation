"""Independently verify the targeted central adoption and generated map payload."""
import hashlib
import json
import sys
import zipfile
import copy
from collections import defaultdict
from decimal import Decimal
from itertools import product
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / "tools"))
from researcher_review import S, R, column_index, table_rows
from original_atlas_data import embedded

MODEL_ID = "52_GM2019_Fig9_Pelagic_balanced_(2000-2014)"
MODEL_SHA = "9beff5a4e525dcf4253bf83472253c7a4a9f7e7db10379ecef64eb33cd32a656"
PAPER_ID = "OKH-GM2019__LME_052"
CLASSIC_FIELDS = ["unit_id", "model_id", "scope", "method", "catch_basis", "unidentified", "metric", "status"]
YEAR_FIELDS = [str(y) for y in range(1950, 2020)]
BOUND_STATUS = "External fixed taxon-TL benchmark; discard-routing ecological uncertainty is not assessed."


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalized_cell(cell, shared):
    formula = cell.find(f"{{{S}}}f")
    if formula is not None:
        return {"formula": formula.text, "attributes": formula.attrib}
    kind = cell.get("t")
    if kind == "inlineStr":
        return "".join(t.text or "" for t in cell.findall(f".//{{{S}}}t"))
    value = cell.find(f"{{{S}}}v")
    if value is None or value.text is None:
        return None
    value = value.text
    if kind == "s":
        return shared[int(value)]
    if kind == "b":
        return {"boolean": value == "1"}
    if kind not in {"str", "e"}:
        return {"number": str(Decimal(value).normalize())}
    return value


def normalized_records(path, sheet_name, table_name, classic_central=False):
    """Read exact XML values; skip other units before normalizing annual cells."""
    result = []
    with zipfile.ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = ["".join(x.itertext()) for x in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        targets = {x.get("Id"): x.get("Target") for x in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        sheet = next(x for x in workbook.findall(f"{{{S}}}sheets/{{{S}}}sheet") if x.get("name") == sheet_name)
        target = targets[sheet.get(f"{{{R}}}id")]
        target = target.lstrip("/") if target.startswith("/") else "xl/" + target
        current, header = None, None
        with archive.open(target) as stream:
            for _, row in ET.iterparse(stream, events=("end",)):
                if row.tag != f"{{{S}}}row":
                    continue
                nodes = {column_index(c.get("r")) - 1: c for c in row}
                first = normalized_cell(nodes[0], shared) if 0 in nodes else None
                if first == "@table":
                    current, header = normalized_cell(nodes[1], shared), None
                elif current == table_name and nodes:
                    if header is None:
                        header = [normalized_cell(nodes[i], shared) if i in nodes else None for i in range(max(nodes) + 1)]
                        # Regional workbooks store calendar headers as numbers;
                        # the central registry stores the same years as text.
                        header = [str(int(Decimal(k["number"])))
                                  if isinstance(k, dict) and set(k) == {"number"}
                                  and Decimal(k["number"]) in range(1950, 2020)
                                  else k for k in header]
                    elif not classic_central or (first == "LME_052" and (1 not in nodes or not normalized_cell(nodes[1], shared))):
                        result.append({str(k): normalized_cell(nodes[i], shared) if i in nodes else None for i, k in enumerate(header)})
                row.clear()
    return result


def compare_classic_records(before, after):
    """Only 27 exact classic identities and six unavailable bounds are admissible."""
    def key(record):
        return tuple(record.get(k) for k in CLASSIC_FIELDS)
    numeric_keys = {("LME_052", None, "all", "simple trophic chain", basis, treatment, metric, "ok")
                    for basis, treatment, metric in product(["landings", "catch", "discards"], ["method", "zero", "simple"], ["ppr", "catch", "covered_catch"])}
    bound_keys = {("LME_052", None, "all", "simple trophic chain", "landings", treatment, metric, BOUND_STATUS)
                  for treatment, metric in product(["method", "zero", "simple"], ["min_tC", "max_tC"])}
    old = {key(r): r for r in before}
    new = {key(r): r for r in after}
    checks = {
        "before_exact33_unique_identities": len(before) == len(old) == 33 and set(old) == numeric_keys | bound_keys,
        "after_exact27_unique_identities": len(after) == len(new) == 27 and set(new) == numeric_keys,
        "all_fields_and_70_years_exact_schema": all(set(r) == set(CLASSIC_FIELDS + YEAR_FIELDS) for r in before + after),
        "six_missing_bounds_all70_years_blank": all(k in old and all(old[k].get(y) is None for y in YEAR_FIELDS) for k in bound_keys),
    }
    absolute_caps = {"ppr": Decimal("0.0000011"), "catch": Decimal("0.0000000011"), "covered_catch": Decimal("0.0000000011")}
    relative_cap = Decimal("1e-15")
    deltas = []
    numbers_ok = True
    for k in sorted(numeric_keys):
        if k not in old or k not in new:
            numbers_ok = False
            continue
        for year in YEAR_FIELDS:
            a, b = old[k].get(year), new[k].get(year)
            if a is None or b is None:
                numbers_ok = numbers_ok and a is None and b is None
                continue
            if not (isinstance(a, dict) and isinstance(b, dict) and set(a) == set(b) == {"number"}):
                numbers_ok = False
                continue
            av, bv = Decimal(a["number"]), Decimal(b["number"])
            difference = abs(bv - av)
            relative = difference / max(abs(av), abs(bv), Decimal(1))
            numbers_ok = numbers_ok and difference <= absolute_caps[k[6]] and relative <= relative_cap
            if difference:
                deltas.append({"identity": dict(zip(CLASSIC_FIELDS, k)), "year": int(year), "before": str(av), "after": str(bv),
                               "absolute_difference": str(difference), "relative_difference": str(relative)})
    checks["all1890_year_values_and_missing_masks_within_explicit_caps"] = numbers_ok
    maxima = {metric: max((Decimal(d["absolute_difference"]) for d in deltas
                           if d["identity"]["metric"] == metric), default=Decimal(0))
              for metric in absolute_caps}
    return {"checks": checks, "before_rows": len(before), "after_rows": len(after),
            "absolute_caps_wet_tonnes": {k: str(v) for k, v in absolute_caps.items()}, "relative_cap": str(relative_cap),
            "changed_numeric_cell_count": len(deltas),
            "observed_max_absolute_difference_wet_tonnes": {k: str(v) for k, v in maxima.items()},
            "observed_max_relative_difference": str(max((Decimal(d["relative_difference"]) for d in deltas), default=Decimal(0))),
            "changed_numeric_cells": deltas, "missing_blank_bounds": [old[k] for k in sorted(bound_keys) if k in old],
            "passed": all(checks.values())}


def verify_independent_classic(before_project, after_project):
    before = normalized_records(before_project, "Regional PPR", "Annual", True)
    after = normalized_records(after_project, "Regional PPR", "Annual", True)
    result = compare_classic_records(before, after)
    before_region = HERE.parent / "integration/LME_052_before_GM2019_adoption.xlsx"
    after_region = ROOT / "regions/LME_052/LME_052.xlsx"
    def regional(path):
        rows = [dict(r, unit_id="LME_052") for r in normalized_records(path, "Classic PPR", "Annual")]
        for row in rows:
            # An empty inline-string model ID serializes as a blank central cell.
            if row.get("model_id") == "":
                row["model_id"] = None
        return rows
    def canonical(records):
        return sorted(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in records)
    result["checks"]["before_central_matches_archived_region_exactly"] = canonical(before) == canonical(regional(before_region))
    result["checks"]["after_central_matches_current_region_exactly"] = canonical(after) == canonical(regional(after_region))
    for sheet, table in [("Catch", "Catch"), ("Classic PPR", "Taxa"), ("NPP", "NPP"), ("NPP", "Provenance")]:
        result["checks"]["unchanged_input_" + sheet + "/" + table] = normalized_records(before_region, sheet, table) == normalized_records(after_region, sheet, table)
    guards = {}
    for name in ["changed_numeric_value", "missing_numeric_row", "changed_status", "lost_year_missingness", "numeric_legacy_bound", "other_unit"]:
        mutated_before, mutated_after = copy.deepcopy(before), copy.deepcopy(after)
        if name == "changed_numeric_value": mutated_after[0]["2019"] = {"number": "1"}
        elif name == "missing_numeric_row": mutated_after.pop()
        elif name == "changed_status": mutated_after[0]["status"] = "unavailable"
        elif name == "lost_year_missingness": mutated_after[0]["2019"] = None
        elif name == "numeric_legacy_bound": next(r for r in mutated_before if r["metric"] == "min_tC")["2019"] = {"number": "1"}
        elif name == "other_unit": mutated_after[0]["unit_id"] = "LME_013"
        guards[name] = not compare_classic_records(mutated_before, mutated_after)["passed"]
    result["adversarial_guard_checks"] = guards
    result["checks"]["all_adversarial_changes_rejected"] = all(guards.values())
    result["scientific_basis"] = "Unchanged catch, TL/SPPR and NPP inputs; standard fsum recalculation differs only below 1e-15 relative. Migration flatten_method emits six all-blank classic min/max placeholders; regional.recalculate emits only ppr/catch/covered_catch. Blank unavailable uncertainty is not a numeric bound."
    result["generator_trace"] = ["tools/migrate.py:118", "tools/workbooks.py:159-173", "tools/regional.py:73-98", "tools/update_project.py:32-41"]
    result["passed"] = all(result["checks"].values())
    return result


def unaffected_record_fingerprints(path, classic_verified=False):
    """Read XML rows once; avoid materializing the central annual archive."""
    hashes = defaultdict(list)
    counts = defaultdict(int)
    with zipfile.ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = ["".join(x.itertext()) for x in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        wb = ET.fromstring(archive.read("xl/workbook.xml"))
        rel = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {x.get("Id"): x.get("Target") for x in rel}
        for sheet in wb.findall(f"{{{S}}}sheets/{{{S}}}sheet"):
            name = sheet.get("name")
            target = targets[sheet.get(f"{{{R}}}id")]
            target = target.lstrip("/") if target.startswith("/") else "xl/" + target
            current = None
            header = None
            with archive.open(target) as stream:
                for _, row in ET.iterparse(stream, events=("end",)):
                    if row.tag != f"{{{S}}}row":
                        continue
                    cells = {column_index(c.get("r")) - 1: normalized_cell(c, shared) for c in row}
                    if cells.get(0) == "@table":
                        current, header = cells.get(1), None
                    elif current and cells:
                        if header is None:
                            header = [cells.get(i) for i in range(max(cells) + 1)]
                        else:
                            record = dict(zip(map(str, header), (cells.get(i) for i in range(len(header)))))
                            unit = record.get("unit_id")
                            affected = False
                            if name == "Models & coverage" and current == "Models":
                                affected = record.get("model_id") == MODEL_ID and unit == "LME_052"
                                if unit == "LME_052" and not affected:
                                    # Superseded candidate metadata stays protected;
                                    # only its derived selection flag may change.
                                    record.pop("selected", None)
                            elif name == "Papers" and current == "Papers":
                                affected = record.get("article_id") == PAPER_ID
                                if unit == "LME_052" and not affected:
                                    record.pop("selected", None)
                            elif name == "Map geography" and current == "Geometry":
                                affected = "article:" + PAPER_ID in record.values()
                            elif name == "Definitions & build":
                                affected = current == "Last build"
                            elif unit == "LME_052":
                                affected = name in {"Regions & status", "Method comparisons", "Diagnostics & sensitivity"}
                                if name == "Regional PPR" and current == "Annual":
                                    # Classic records leave this strict fingerprint only
                                    # after the separate exact-key/value/mask gate passes.
                                    affected = bool(record.get("model_id")) or classic_verified
                            if not affected:
                                key = name + "/" + current
                                encoded = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                                hashes[key].append(hashlib.sha256(encoded.encode("utf-8")).hexdigest())
                                counts[key] += 1
                    row.clear()
    return {key: {"rows": counts[key], "sha256": hashlib.sha256("".join(sorted(vals)).encode("ascii")).hexdigest()}
            for key, vals in hashes.items()}


def bounded(archive, sheet, table):
    return [r for _, r in table_rows(archive, sheet, table)[3]]


def main():
    backups = list(HERE.glob("Project.before_registration_*.xlsx"))
    assert len(backups) == 1
    classic = verify_independent_classic(backups[0], ROOT / "Project.xlsx")
    before = unaffected_record_fingerprints(backups[0], classic["passed"])
    current = unaffected_record_fingerprints(ROOT / "Project.xlsx", classic["passed"])
    unaffected_checks = {key: current.get(key) == value for key, value in before.items()}
    unaffected_checks["no_unrelated_tables_added"] = set(before) == set(current)

    with zipfile.ZipFile(ROOT / "Project.xlsx") as archive:
        models = [r for r in bounded(archive, "Models & coverage", "Models") if r.get("unit_id") == "LME_052"]
        papers = [r for r in bounded(archive, "Papers", "Papers") if r.get("unit_id") == "LME_052"]
        regions = bounded(archive, "Regions & status", "Regions")
        region = next(r for r in regions if r.get("unit_id") == "LME_052")
    selected = [r for r in models if r.get("selected") == "1"]
    chosen = next(r for r in models if r.get("model_id") == MODEL_ID)
    regional_path = ROOT / region["workbook"]
    model_path = ROOT / chosen["model_path"]
    mapdata, maptext = embedded(ROOT / "interactive_map/index.html", "DB")
    trends, trendtext = embedded(ROOT / "interactive_map/trends.html", "SERIES_DB")
    unit = mapdata["network"]["units"]["LME_052"]
    model = next(m for m in unit["models"] if m["id"] == MODEL_ID)
    trend_unit = trends["units"]["LME_052"]
    expected = json.loads((HERE.parent / "integration/regional_adoption_verification.json").read_text(encoding="utf-8"))
    all_fresh = all(sha(ROOT / r["workbook"]) == r["sha256"] for r in regions)
    checks = {
        "independent_classic_keys_status_inputs_year_values_preserved": classic["passed"],
        "unrelated_central_records_preserved": all(unaffected_checks.values()),
        "one_selected_LME052_model": len(selected) == 1 and selected[0]["model_id"] == MODEL_ID,
        "unique_central_model_identity": sum(r.get("model_id") == MODEL_ID for r in models) == 1,
        "unique_map_model_identity": sum(m["id"] == MODEL_ID for m in unit["models"]) == 1,
        "unique_trends_model_identity": sum(m["id"] == MODEL_ID for m in trend_unit["models"]) == 1,
        "central_regional_model_identity": region["selected_model_id"] == MODEL_ID,
        "central_regional_workbook_hash": region["sha256"] == sha(regional_path),
        "regional_hash_matches_adoption": sha(regional_path) == expected["after_workbook_sha256"],
        "exact_frozen_model_hash": sha(model_path) == MODEL_SHA,
        "all_central_regional_hashes_fresh": all_fresh,
        "selected_paper_correct": [r.get("article_id") for r in papers if r.get("selected") == "1"] == [PAPER_ID],
        "production_eligibility_false": region.get("production_eligible") == "0",
        "no_fabricated_researcher_signoff": not chosen.get("researcher_review_status"),
        "map_payload_contains_model": model["id"] == MODEL_ID,
        "map_model_current_regional_hash": model.get("workbook_sha256") == sha(regional_path),
        "trends_model_current_regional_hash": next(m for m in trend_unit["models"] if m["id"] == MODEL_ID).get("workbook_sha256") == sha(regional_path),
        "map_selected_article_exact": unit.get("selected_articles") == [PAPER_ID],
        "native_source_link_exists": (ROOT / str(model.get("source", "")).removeprefix("../")).is_file(),
        "native_source_link_exact_adopted_sppr": str(model.get("source", "")).removeprefix("../") == model_path.with_name("sppr_source.xlsx").relative_to(ROOT).as_posix(),
        "map_default_selected_index": type(unit["default_model"]) is int and 0 <= unit["default_model"] < len(unit["models"]) and unit["models"][unit["default_model"]]["id"] == MODEL_ID,
        "trends_default_selected_id": trend_unit["default_model"] == MODEL_ID,
        "map_current_project_hash": f'content="{sha(ROOT / "Project.xlsx")}"' in maptext,
        "trends_current_project_hash": f'content="{sha(ROOT / "Project.xlsx")}"' in trendtext,
    }
    result = {
        "schema_version": 1,
        "model_id": MODEL_ID,
        "model_sha256": MODEL_SHA,
        "project_sha256": sha(ROOT / "Project.xlsx"),
        "regional_workbook_sha256": sha(regional_path),
        "checks": checks,
        "unaffected_table_checks": unaffected_checks,
        "unaffected_record_fingerprints_before": before,
        "unaffected_record_fingerprints_after": current,
        "independent_classic_comparison": classic,
        "map_model": model,
        "map_selected_articles": unit.get("selected_articles"),
        "trends_model": next(m for m in trend_unit["models"] if m["id"] == MODEL_ID),
        "passed": all(checks.values()),
    }
    (HERE / "central_payload_verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"checks": checks, "unaffected_tables": len(unaffected_checks), "passed": result["passed"]}, ensure_ascii=False, indent=2))
    assert result["passed"]


if __name__ == "__main__":
    main()
