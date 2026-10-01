"""Apply coordinator-reviewed, keyed central metadata with live freshness checks.

This helper never chooses which scientific proposal to adopt. An explicit plan
contains the reviewed fields, expected old values, and supporting evidence.
Generated regional tables remain the responsibility of tools/update_project.py.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from workbooks import chunks, read_book, records, sha, unchunks, write_book


def geometry_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def apply_geometry_patches(book, patches, checks):
    """Apply only reviewed article keys; retain every other chunk verbatim."""
    if not patches:
        return []
    header, old_rows = book["Map geography"]["Geometry"]
    current = unchunks(old_rows)
    replacements, reviewed = {}, []
    for patch in patches:
        key = patch["key"]
        if not key.startswith("article:") or key in replacements:
            raise ValueError(f"Expected a unique article geometry key: {key}")
        action = patch["action"]
        if action == "insert":
            if ("expected_old_geometry_sha256" not in patch
                    or patch["expected_old_geometry_sha256"] is not None or key in current):
                raise ValueError(f"Expected absent article geometry: {key}")
        elif key not in current or geometry_digest(current[key]) != patch["expected_old_geometry_sha256"]:
            raise ValueError(f"Geometry changed: {key}")
        if action in ("replace", "insert"):
            path = ROOT / patch["replacement_geojson"]
            if sha(path) != patch["replacement_file_sha256"]:
                raise ValueError(f"Replacement file changed: {path}")
            value = json.loads(path.read_text(encoding="utf-8"))
            if value.get("type") == "FeatureCollection":
                if len(value["features"]) != 1:
                    raise ValueError("Reviewed replacement must contain exactly one feature")
                value = value["features"][0]
            if value.get("type") == "Feature":
                value = value["geometry"]
            if geometry_digest(value) != patch["replacement_geometry_sha256"]:
                raise ValueError(f"Replacement geometry changed: {path}")
            from shapely.geometry import shape
            geometry = shape(value)
            if geometry.geom_type not in ("Polygon", "MultiPolygon") or geometry.is_empty or not geometry.is_valid:
                raise ValueError(f"Invalid reviewed polygon: {path}")
            checks[path] = patch["replacement_file_sha256"]
            replacements[key] = chunks(key, value)
        elif action == "remove":
            replacements[key] = []
        else:
            raise ValueError(f"Unreviewed geometry action: {action}")
        reviewed.append(dict(patch))
    new_rows, emitted = [], set()
    for row in old_rows:
        key = row[0]
        if key not in replacements:
            new_rows.append(row)
        elif key not in emitted:
            new_rows.extend(replacements[key])
            emitted.add(key)
    for key in replacements:
        if key not in emitted:
            new_rows.extend(replacements[key])
    if [r for r in old_rows if r[0] not in replacements] != [r for r in new_rows if r[0] not in replacements]:
        raise ValueError("Unrelated geometry chunks changed")
    book["Map geography"]["Geometry"] = (header, new_rows)
    return reviewed


def apply(plan_path: Path, execute: bool):
    plan_hash = sha(plan_path)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    project_path = ROOT / "Project.xlsx"
    before_hash = sha(project_path)
    checks = {project_path: before_hash, plan_path: plan_hash}
    for item in plan["regional_inputs"]:
        path = ROOT / item["path"]
        if sha(path) != item["sha256"]:
            raise ValueError(f"Regional handoff is stale: {item['path']}")
        checks[path] = item["sha256"]
    before = read_book(project_path)
    after = copy.deepcopy(before)
    changed = []
    allowed = {("Papers", "Papers"), ("Models & coverage", "Models")}
    for patch in plan["patches"]:
        table_key = (patch["sheet"], patch["table"])
        if table_key not in allowed:
            raise ValueError(f"Not central source metadata: {table_key}")
        header, rows = after[patch["sheet"]][patch["table"]]
        matches = [r for r in rows if all(dict(zip(header, r)).get(k) == v for k, v in patch["key"].items())]
        if len(matches) != 1:
            raise ValueError(f"Expected unique key: {patch['key']}")
        if patch["field"] not in header:
            raise ValueError(f"Unknown metadata field: {patch['field']}")
        idx = header.index(patch["field"])
        row = matches[0]
        if row[idx] != patch["expected_old"]:
            raise ValueError(f"Metadata changed: {patch['key']} / {patch['field']}")
        # The XLSX writer serializes numeric cells with 16 significant digits.
        # Normalize only the proposed metadata cell, retaining its full reviewed
        # value in the receipt; unrelated workbook content still compares exactly.
        value = patch["proposed"]
        stored = float(format(value, ".16g")) if isinstance(value, float) else value
        row[idx] = stored
        changed.append({**patch, "stored_value": stored})
    inserted = []
    for patch in plan.get("record_inserts", []):
        if (patch["sheet"], patch["table"]) != ("Papers", "Papers"):
            raise ValueError("Only reviewed missing paper records may be inserted")
        if patch.get("expected_old") != "record_absent":
            raise ValueError("Paper insertion requires an explicit absence precondition")
        header, rows = after["Papers"]["Papers"]
        key, proposed = patch["key"], patch["proposed"]
        if set(key) != {"article_id", "unit_id"} or not all(key.values()):
            raise ValueError("Paper insertion requires article_id and unit_id")
        if set(proposed) - set(header) or any(proposed.get(k) != value for k, value in key.items()):
            raise ValueError("Unknown paper field or inconsistent record identity")
        if any(dict(zip(header, row)).get("article_id") == key["article_id"] for row in rows):
            raise ValueError(f"Paper already exists: {key['article_id']}")
        stored = [float(format(proposed.get(name), ".16g")) if isinstance(proposed.get(name), float)
                  else proposed.get(name) for name in header]
        rows.append(stored)
        inserted.append({**patch, "stored_row": dict(zip(header, stored))})
    geometry_changes = apply_geometry_patches(after, plan.get("geometry_patches", []), checks)
    for path, expected in checks.items():
        if sha(path) != expected:
            raise ValueError(f"Input changed during metadata preparation: {path}")
    receipt = {"plan": plan_path.relative_to(ROOT).as_posix(), "plan_sha256": plan_hash,
               "project_before_sha256": before_hash, "patches": changed,
               "record_inserts": inserted,
               "geometry_patches": geometry_changes,
               "applied": execute, "preserved_unrelated_content": False}
    if execute:
        backup = HERE / "work" / ("Project_before_metadata_" + before_hash[:12] + ".xlsx")
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(project_path, backup)
        for path, expected in checks.items():
            if sha(path) != expected:
                raise ValueError(f"Input changed while retaining backup: {path}")
        write_book(project_path, after)
        reopened = read_book(project_path)
        if reopened != after:
            raise ValueError("Saved central metadata differs from reviewed in-memory table content")
        # Reverse exactly the approved values and require full-table equality.
        restored = copy.deepcopy(reopened)
        for patch in reversed(changed):
            header, rows = restored[patch["sheet"]][patch["table"]]
            row = next(r for r in rows if all(dict(zip(header, r)).get(k) == v for k, v in patch["key"].items()))
            row[header.index(patch["field"])] = patch["expected_old"]
        for patch in reversed(inserted):
            header, rows = restored["Papers"]["Papers"]
            matches = [i for i, row in enumerate(rows)
                       if all(dict(zip(header, row)).get(k) == v for k, v in patch["key"].items())]
            if len(matches) != 1 or dict(zip(header, rows[matches[0]])) != patch["stored_row"]:
                raise ValueError("Inserted paper differs from the exact reviewed record")
            del rows[matches[0]]
        if geometry_changes:
            # The geometry helper already requires untouched keys/chunks to be
            # identical; the reopened workbook must equal that reviewed result.
            restored["Map geography"]["Geometry"] = copy.deepcopy(before["Map geography"]["Geometry"])
        if restored != before:
            raise ValueError("Unrelated central content changed")
        receipt["preserved_unrelated_content"] = True
        receipt["project_after_sha256"] = sha(project_path)
    else:
        receipt["preserved_unrelated_content"] = True
    destination = plan_path.with_name(plan_path.stem + ("_applied" if execute else "_dry_run") + ".json")
    destination.write_text(json.dumps(receipt, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    if execute:
        # Publish the efficient read-only source view only after the full saved
        # workbook has passed the exact approved-change reversal comparison.
        snapshot_path = HERE / "central_source_metadata_current.json"
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8")) if snapshot_path.exists() else {}
        snapshot.update({
            "purpose": "Read-only central source metadata snapshot; Project.xlsx remains authority. Use only while its exact SHA256 matches.",
            "project_sha256": receipt["project_after_sha256"],
            "provenance": "Source tables read from the reopened Project.xlsx after exact approved-change and unrelated-content preservation checks.",
            "transaction_evidence": destination.relative_to(HERE).as_posix(),
            "tables": {"Models & coverage": records(reopened, "Models & coverage", "Models"),
                       "Papers": records(reopened, "Papers", "Papers")},
        })
        snapshot.setdefault("metadata_integration_evidence", []).append(destination.relative_to(HERE).as_posix())
        snapshot_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"patches": len(changed), "applied": execute, "receipt": destination.relative_to(ROOT).as_posix()}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    apply(args.plan.resolve(), args.apply)
