"""Read-only coordinator comparison against the frozen accepted-input baseline.

This checks preservation, not scientific validity. A restored empty Groups table
is checked field by field against the accepted selected JSON, without defaults.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import openpyxl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from workbooks import YEARS, clean, digest_tables, overview, records, sha


def read_protected(path):
    """Read only relevant sheets, using the authoritative @table convention."""
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=False)
    result = {}
    try:
        for title in ("Overview", "Catch", "Classic PPR", "Selected model groups", "NPP"):
            if title not in workbook.sheetnames:
                continue
            blocks, name, header, data = {}, None, None, []
            for row in workbook[title].values:
                vals = list(row)
                while vals and vals[-1] is None:
                    vals.pop()
                if not vals:
                    continue
                if vals[0] == "@table":
                    if name is not None:
                        blocks[name] = (header or [], data)
                    name, header, data = vals[1], None, []
                elif name is not None:
                    if header is None:
                        header = [int(v) if isinstance(v, str) and v.isdigit() and int(v) in YEARS else v for v in vals]
                    else:
                        if any(isinstance(v, str) and v.startswith("=") for v in vals):
                            raise ValueError(f"Unexpected formula in protected table: {path}/{title}/{name}")
                        data.append((vals + [None] * len(header))[:len(header)])
            if name is not None:
                blocks[name] = (header or [], data)
            result[title] = blocks
    finally:
        workbook.close()
    return result


def compare(unit):
    inventory = json.loads((HERE / "preflight.json").read_text(encoding="utf-8"))["regions"]
    item = next(x for x in inventory if x["unit_id"] == unit)
    baseline = ROOT / item["baseline_directory"]
    current_path = ROOT / item["workbook"]
    old = read_protected(baseline / current_path.name)
    new = read_protected(current_path)
    before, after = overview(old), overview(new)
    checks = {
        "selected_model_id": after.get("selected_model_id") == item["model_id"],
        "accepted_model_bytes": sha(ROOT / item["model_path"]) == sha(baseline / "accepted_model.json"),
    }
    protected = [("Catch", "Catch"), ("Classic PPR", "Taxa"),
                 ("NPP", "NPP"), ("NPP", "Provenance")]
    for sheet, table in protected:
        a = old.get(sheet, {}).get(table, ([], []))
        b = new.get(sheet, {}).get(table, ([], []))
        checks[f"{sheet}/{table}"] = digest_tables(a) == digest_tables(b)
    old_groups = records(old, "Selected model groups", "Groups")
    new_groups = records(new, "Selected model groups", "Groups")
    inventory_restoration = not old_groups and bool(new_groups)
    if inventory_restoration:
        accepted = json.loads((baseline / "accepted_model.json").read_text(encoding="utf-8"))["group"]
        source_by_id = {int(g["group_seq"]): g for g in accepted}
        current_by_id = {int(g["seq"]): g for g in new_groups}
        exact = len(current_by_id) == len(new_groups) and set(current_by_id) == set(source_by_id)
        for group_id, current in current_by_id.items():
            source = source_by_id.get(group_id, {})
            keys = sorted((set(source) | set(current)) - {"inventory_provenance"})
            expected = [[key, group_id if key == "seq" else clean(source.get(key))] for key in keys]
            observed = [[key, current.get(key)] for key in keys]
            exact = exact and digest_tables(expected) == digest_tables(observed)
        checks["restored_group_inventory_exact_accepted_JSON"] = exact
    else:
        checks["accepted_group_parameters"] = digest_tables([
            old.get("Selected model groups", {}).get("Groups", ([], []))
        ]) == digest_tables([new.get("Selected model groups", {}).get("Groups", ([], []))])
    # Selection, catch basis/year and parameter/runtime configuration are protected;
    # ordinary calculation freshness/status fields are deliberately not compared.
    keys = sorted(k for k in before if any(token in k.lower() for token in
                  ("carbon", "conversion", "efficiency", "transfer", "balance", "detrit", "egestion")))
    for key in ["selected_model_id", "model_path", "taxon_detail_year", "catch_basis", "npp_policy", *keys]:
        if key in before:
            checks[f"Overview/{key}"] = before[key] == after.get(key)
    changed_derived = []
    for sheet, table in [("Selected model groups", "Group SPPR"), ("Classic PPR", "Annual")]:
        if digest_tables(old.get(sheet, {}).get(table, ([], []))) != digest_tables(new.get(sheet, {}).get(table, ([], []))):
            changed_derived.append(f"{sheet}/{table}")
    return {
        "unit_id": unit, "selected_model_id": item["model_id"],
        "baseline_workbook_sha256": sha(baseline / current_path.name),
        "current_workbook_sha256": sha(current_path), "checks": checks,
        "all_checked_protected_inputs_preserved": all(checks.values()),
        "empty_group_inventory_restored": inventory_restoration,
        "changed_derived_tables_requiring_review": changed_derived,
        "scope": "Input preservation only; no approval of model validity or completed regional review.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("units", nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = [compare(unit) for unit in args.units]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps([{k: r[k] for k in ("unit_id", "all_checked_protected_inputs_preserved", "empty_group_inventory_restored", "changed_derived_tables_requiring_review")} for r in result]))
    if not all(r["all_checked_protected_inputs_preserved"] for r in result):
        raise SystemExit(1)
