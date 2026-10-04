"""Run the standard updater and retain its output if Windows denies replacement.

Only the file-install boundary is instrumented. Calculations, guards, metadata
and serialization are the unmodified tools/update_project.py implementation.
"""
import gc
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / "tools"))
import update_project


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class DeferredInstall(Exception):
    pass


project = ROOT / "Project.xlsx"
region = ROOT / "regions/LME_052/LME_052.xlsx"
before_project, before_region = sha(project), sha(region)
prepared = HERE / "Project.standard_update_prepared.xlsx"
native_replace = os.replace
evidence = {"standard_updater": "tools/update_project.py", "updater_sha256": sha(ROOT / "tools/update_project.py"),
            "writer_sha256": sha(ROOT / "tools/workbooks.py"), "project_before_sha256": before_project,
            "regional_workbook_sha256": before_region, "scientific_transform_modified": False}


def instrumented_replace(source, destination):
    if Path(destination).resolve() != project:
        return native_replace(source, destination)
    assert sha(project) == before_project and sha(region) == before_region
    try:
        result = native_replace(source, destination)
        evidence.update(installed=True, deferred=False, project_after_sha256=sha(project))
        return result
    except PermissionError as error:
        evidence["first_replace_error"] = str(error)
        evidence["garbage_collection_objects"] = gc.collect()
        try:
            result = native_replace(source, destination)
            evidence.update(installed=True, deferred=False, project_after_sha256=sha(project),
                            replacement_after_gc=True)
            return result
        except PermissionError as retry:
            evidence["second_replace_error"] = str(retry)
            prepared.write_bytes(Path(source).read_bytes())
            evidence.update(installed=False, deferred=True, prepared_path=prepared.name,
                            prepared_sha256=sha(prepared), original_project_unchanged=sha(project) == before_project)
            raise DeferredInstall("Standard output prepared; install from a fresh process after readers close.")


os.replace = instrumented_replace
try:
    update_project.update(ROOT, [region], False)
except DeferredInstall as error:
    print(str(error), flush=True)
finally:
    os.replace = native_replace
    (HERE / "project_update_execution.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(evidence, ensure_ascii=False, indent=2), flush=True)
