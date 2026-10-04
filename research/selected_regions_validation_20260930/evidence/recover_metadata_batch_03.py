"""Verify the already-saved batch without rewriting Project.xlsx."""
from itertools import zip_longest
from pathlib import Path
import hashlib
import json
import posixpath
import zipfile

from lxml import etree
from integrate_ready_batch import metadata_and_regions

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def sheet_paths(z):
    rels = etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    paths = {r.get("Id"): posixpath.normpath("xl/" + r.get("Target"))
             if not r.get("Target").startswith("/") else r.get("Target")[1:] for r in rels}
    return {s.get("name"): paths[s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")]
            for s in etree.fromstring(z.read("xl/workbook.xml")).find(NS + "sheets")}


def rows(z, path):
    assert "xl/sharedStrings.xml" not in z.namelist(), "This recovery expects the audited inline-string writer"
    with z.open(path) as stream:
        for _, row in etree.iterparse(stream, events=("end",), tag=NS + "row"):
            values = {}
            for c in row:
                assert c.find(NS + "f") is None, "Unexpected authoritative formula"
                kind = c.get("t", "n")
                if kind == "inlineStr":
                    value = "".join(c.itertext())
                else:
                    v = c.find(NS + "v")
                    value = None if v is None or v.text is None else v.text
                    if value is not None and kind == "n":
                        value = float(value) if any(x in value for x in ".eE") else int(value)
                    elif value is not None and kind == "b":
                        value = bool(int(value))
                if value is not None:
                    values[c.get("r")] = value
            yield int(row.get("r")), values
            row.clear()
            while row.getprevious() is not None:
                del row.getparent()[0]


def main():
    plan_path = HERE / "verification/metadata_batch_03_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    before = HERE / "work/Project_before_metadata_f828d73f28db.xlsx"
    after = ROOT / "Project.xlsx"
    before_hash, after_hash = sha(before), sha(after)
    assert before_hash == plan["project_sha256_at_review"]
    assert after_hash == "1a549f3faa33efc0864a7117d58b665e06523f93b941b97128147a73ba137963"
    for item in plan["regional_inputs"]:
        assert sha(ROOT / item["path"]) == item["sha256"]
    changes, cell_count = [], 0
    with zipfile.ZipFile(before) as old, zipfile.ZipFile(after) as new:
        old_sheets, new_sheets = sheet_paths(old), sheet_paths(new)
        assert old_sheets == new_sheets
        structural = [n for n in old.namelist() if n.startswith("xl/tables/")
                      or n in {"xl/styles.xml", "xl/workbook.xml", "xl/_rels/workbook.xml.rels"}]
        assert all(old.read(n) == new.read(n) for n in structural)
        for title, path in old_sheets.items():
            for previous, current in zip_longest(rows(old, path), rows(new, path)):
                assert previous is not None and current is not None and previous[0] == current[0]
                p, c = previous[1], current[1]
                cell_count += len(set(p) | set(c))
                for address in set(p) | set(c):
                    if p.get(address) != c.get(address):
                        changes.append({"sheet": title, "cell": address, "old": p.get(address), "new": c.get(address)})
            print(title, "verified", flush=True)
    # Keyed source checks establish the affected record identities; the all-cell
    # scan proves that no additional workbook cell changed outside this multiset.
    tables = metadata_and_regions(after)
    patches = []
    for patch in plan["patches"]:
        value = patch["proposed"]
        stored = float(format(value, ".16g")) if isinstance(value, float) else value
        matches = [r for r in tables[patch["sheet"]] if all(r.get(k) == v for k, v in patch["key"].items())]
        assert len(matches) == 1 and matches[0].get(patch["field"]) == stored
        patches.append({**patch, "stored_value": stored})
    expected = sorted((p["sheet"], repr(p["expected_old"]), repr(p["stored_value"]))
                      for p in patches if p["expected_old"] != p["stored_value"])
    observed = sorted((p["sheet"], repr(p["old"]), repr(p["new"])) for p in changes)
    assert observed == expected, (observed, expected)
    assert sha(before) == before_hash and sha(after) == after_hash
    receipt = {"plan": plan_path.relative_to(ROOT).as_posix(), "plan_sha256": sha(plan_path),
               "project_before_sha256": before_hash, "project_after_sha256": after_hash,
               "patches": patches, "applied": True, "preserved_unrelated_content": True,
               "recovery": "No workbook rewrite. Full independent XML cell comparison plus keyed source checks; only intended 16-significant-digit numeric storage differs from proposed binary floats.",
               "cells_compared": cell_count, "changed_cells": changes,
               "native_tables_styles_and_workbook_structure_preserved": True}
    destination = plan_path.with_name(plan_path.stem + "_applied.json")
    destination.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cache_path = HERE / "central_source_metadata_current.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    cache.update({"project_sha256": after_hash, "transaction_evidence": destination.relative_to(HERE).as_posix(),
                  "provenance": receipt["recovery"],
                  "tables": {key: tables[key] for key in ("Models & coverage", "Papers")}})
    cache.setdefault("metadata_integration_evidence", []).append(destination.relative_to(HERE).as_posix())
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "cells_compared": cell_count, "intended_changes": len(changes),
                      "project_sha256": after_hash}), flush=True)


if __name__ == "__main__":
    main()
