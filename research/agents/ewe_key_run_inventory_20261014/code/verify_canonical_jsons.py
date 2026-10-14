"""Verify the three source snapshots without calculation or publication."""
from pathlib import Path
import csv
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.project_core.registry.discovery import discover_models
STUDY = ROOT / "research/agents/ewe_key_run_inventory_20261014"
MODELS = [
    ("LME_022", "ICES-WGSAM-2015", "ICES_WGSAM2015_North_Sea_1991", 69),
    ("LME_023", "ICES-WGSAM-2016", "ICES_WGSAM2016_Baltic_Proper_2004", 22),
    ("LME_024", "ICES-WGSAM-2019-Irish-Sea", "ICES_WGSAM2019_Irish_Sea_1973", 41),
]
IMPORTS = ["Basic_input.csv", "Diet_composition.csv", "Landings.csv", "Discards.csv",
           "Detritus_fate.csv", "Biomass_accumulation.csv", "TL.xlsx", "Metadata.xlsx"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject_nonfinite(value):
    if isinstance(value, float):
        assert math.isfinite(value), "Nonfinite JSON number"
    elif isinstance(value, dict):
        for item in value.values():
            reject_nonfinite(item)
    elif isinstance(value, list):
        for item in value:
            reject_nonfinite(item)


def main():
    before = json.loads((STUDY / "evidence/region_preparation_before.json").read_text(encoding="utf-8"))
    protected = {path: sha(ROOT / path) == expected for path, expected in before["protected_files"].items()}
    assert all(protected.values()), "A protected workbook, map or pre-existing model changed"
    results = []
    for unit, paper, model_id, count in MODELS:
        region = ROOT / "regions/LME" / unit
        directory = region / "papers" / paper / "models" / model_id
        path = directory / "model.json"
        assert discover_models(region)[model_id] == path.resolve()
        model = json.loads(path.read_text(encoding="utf-8"))
        reject_nonfinite(model)
        groups = model["group"]
        assert isinstance(groups, list) and len(groups) == count
        ids = [int(group["group_seq"]) for group in groups]
        assert ids == list(range(1, count + 1)), ids
        names = [group["group_name"] for group in groups]
        assert all(isinstance(name, str) and name for name in names) and len(set(names)) == count
        diet_cells = 0
        missing = {}
        for group in groups:
            for field in ["biomass", "pb", "qb", "ee", "gs", "biomass_accum", "export"]:
                value = group.get(field)
                if value is None or value == "-9999" or value == -9999:
                    missing.setdefault(field, []).append(group["group_name"])
                else:
                    assert math.isfinite(float(value)), (group["group_name"], field)
            prey_ids = []
            for item in (group.get("diet_descr") or {}).get("diet", []) or []:
                prey = int(item["prey_seq"])
                assert prey in ids
                prey_ids.append(prey)
                for field in ["proportion", "detritus_fate"]:
                    value = item.get(field)
                    if value is not None and value not in ("-9999", -9999):
                        assert math.isfinite(float(value)), (group["group_name"], prey, field)
                diet_cells += 1
            assert len(set(prey_ids)) == len(prey_ids)
        for name in IMPORTS:
            assert (directory / "extracted_tables" / name).is_file(), name
        for name in ["Basic_input.csv", "Biomass_accumulation.csv", "Detritus_fate.csv"]:
            with (directory / "extracted_tables" / name).open(encoding="utf-8", newline="") as stream:
                rows = list(csv.reader(stream))
            assert len(rows) == count + 1, (name, len(rows), count)
            assert [int(row[0]) for row in rows[1:]] == ids
        assert (directory / "model_notes.md").is_file()
        results.append(dict(unit_id=unit, model_id=model_id, path=path.relative_to(ROOT).as_posix(),
                            sha256=sha(path), groups=count, diet_entries=diet_cells,
                            missing_parameters=missing, canonical_discovery=True, imports_present=IMPORTS))
    result = dict(date="2026-10-14", verification_scope="JSON syntax, identity, finite values, table cardinality, discovery and preservation",
                  scientific_validity="not established by these structural checks", models=results,
                  protected_files_unchanged=protected, map_updated=False, selections_changed=False,
                  project_workbook_modified=False)
    output = STUDY / "evidence/canonical_json_verification.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"models": [{"region": x["unit_id"], "groups": x["groups"], "diet_entries": x["diet_entries"]} for x in results],
                      "protected_files_unchanged": len(protected), "scope": result["verification_scope"]}, indent=2))


if __name__ == "__main__":
    main()
