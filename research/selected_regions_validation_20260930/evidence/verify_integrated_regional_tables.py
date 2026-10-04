"""Read-only regional-to-central annual/NPP/selection reconciliation.

Regional scientific arithmetic is verified separately. This check detects lost,
duplicated, stale, or mixed-region records during central consolidation.
Only the installed XLSX writer's exact numeric serialization is permitted when
the source workbook retained more precision; this is not a numeric tolerance.
"""
from collections import Counter
import argparse
import json
import math
from pathlib import Path
import sys
from openpyxl.compat.strings import safe_string

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from workbooks import ANNUAL_HEADER, YEARS, read_book, records, sha


def compare_rows(expected, actual, label):
    wanted, observed = Counter(map(tuple, expected)), Counter(map(tuple, actual))
    exact = wanted == observed
    adjusted_cells = 0
    if wanted != observed:
        serialized = []
        for row in expected:
            converted = []
            for value in row:
                # Do not normalize actual values, identifiers, statuses, missing
                # values or booleans. Permit exactly what write_book emits.
                stored = float(safe_string(value)) if isinstance(value, float) and math.isfinite(value) else value
                adjusted_cells += stored != value
                converted.append(stored)
            serialized.append(converted)
        wanted = Counter(map(tuple, serialized))
        if wanted != observed:
            missing, extra = wanted - observed, observed - wanted
            raise AssertionError(f"{label}: {sum(missing.values())} missing and {sum(extra.values())} extra rows after exact XLSX serialization")
    return {"rows": len(expected), "exact_multiset_match": exact,
            "xlsx_serialization_multiset_match": True,
            "serialization_adjusted_cells": adjusted_cells}


def verify(units, output_path=None):
    project = ROOT / "Project.xlsx"
    project_hash = sha(project)
    central = read_book(project)
    annual = records(central, "Regional PPR", "Annual")
    npp = records(central, "Regional NPP", "NPP")
    statuses = records(central, "Regions & status", "Regions")
    models = records(central, "Models & coverage", "Models")
    papers = records(central, "Papers", "Papers")
    output, sources = [], {}
    for unit in units:
        path = ROOT / "regions" / unit / f"{unit}.xlsx"
        sources[path] = sha(path)
        book = read_book(path)
        overview = {r["field"]: r["value"] for r in records(book, "Overview", "Settings")}
        expected = records(book, "Classic PPR", "Annual") + records(book, "PPR", "Annual")
        observed = [r for r in annual if r["unit_id"] == unit]
        result = {"unit_id": unit, "regional_sha256": sources[path],
                  "annual": compare_rows([[r.get(k) for k in ANNUAL_HEADER] for r in expected],
                                         [[r.get(k) for k in ANNUAL_HEADER] for r in observed], unit + " annual")}
        result["annual"]["year_cells"] = len(expected) * len(YEARS)
        fields = ["method", "units", *YEARS]
        result["npp"] = compare_rows([[r.get(k) for k in fields] for r in records(book, "NPP", "NPP")],
                                     [[r.get(k) for k in fields] for r in npp if r["unit_id"] == unit], unit + " NPP")
        status = [r for r in statuses if r["unit_id"] == unit]
        assert len(status) == 1 and status[0]["sha256"] == sources[path], f"{unit}: central workbook hash"
        selected = overview.get("selected_model_id")
        assert status[0]["selected_model_id"] == selected, f"{unit}: central regional selection"
        chosen = [r for r in models if r["unit_id"] == unit and r.get("selected")]
        assert len(chosen) == 1 and chosen[0]["model_id"] == selected, f"{unit}: selected model metadata"
        expected_papers = {x for x in str(chosen[0].get("paper_ids") or "").split(";") if x}
        actual_papers = {r["article_id"] for r in papers if r["unit_id"] == unit and r.get("selected")}
        assert expected_papers == actual_papers, f"{unit}: selected paper flags"
        result.update(selected_model_id=selected, selected_papers=sorted(actual_papers),
                      selection_and_source_flags_match=True)
        output.append(result)
    assert sha(project) == project_hash, "Project changed during verification"
    assert all(sha(path) == value for path, value in sources.items()), "Regional input changed during verification"
    receipt = {"project_sha256": project_hash, "checks": output,
               "scope": "Annual/NPP multiset reconciliation allowing only the XLSX writer's exact numeric serialization; selection and selected-paper flags match exactly. Independent arithmetic and browser checks remain separate."}
    destination = output_path or HERE / "verification" / ("integrated_tables_" + "_".join(units) + ".json")
    destination.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"units": units, "annual_cells": sum(r["annual"]["year_cells"] for r in output),
                      "passed": True, "project_sha256": project_hash}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("units", nargs="+")
    parser.add_argument("--output", type=Path, help="Explicit receipt path for long multi-region batches")
    args = parser.parse_args()
    verify(args.units, args.output)
