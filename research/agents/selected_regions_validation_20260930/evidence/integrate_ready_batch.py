"""Coordinator-only consolidation of explicitly released regional handoffs."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

import openpyxl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def metadata_and_regions(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
    output = {}
    try:
        for title, wanted in (("Models & coverage", "Models"), ("Papers", "Papers"),
                              ("Regions & status", "Regions")):
            active, header, result = False, None, []
            for cells in wb[title].values:
                values = list(cells)
                while values and values[-1] is None:
                    values.pop()
                if not values:
                    continue
                if values[0] == "@table":
                    active = len(values) > 1 and values[1] == wanted
                    header = None
                elif active and header is None:
                    header = values
                elif active:
                    result.append(dict(zip(header, (values + [None] * len(header))[:len(header)])))
            output[title] = result
    finally:
        wb.close()
    return output


def run(batch_name, units):
    project = ROOT / "Project.xlsx"
    snapshot_path = HERE / "central_source_metadata_current.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    before = sha(project)
    assert before == snapshot["project_sha256"], "Refresh authenticated source metadata snapshot first"
    inventory = json.loads((HERE / "preflight.json").read_text(encoding="utf-8"))["regions"]
    inputs = []
    for unit in units:
        item = next(x for x in inventory if x["unit_id"] == unit)
        handoff = ROOT / "regions" / unit / "validation_reports" / item["model_id"] / "coordination_handoff.json"
        assert handoff.is_file(), handoff
        data = json.loads(handoff.read_text(encoding="utf-8"))
        path = ROOT / item["workbook"]
        inputs.append({"unit_id": unit, "path": item["workbook"], "sha256": sha(path),
                       "handoff": handoff.relative_to(ROOT).as_posix(), "handoff_sha256": sha(handoff)})
        # Regional completion and exact final hash are reviewed by the coordinator
        # before choosing this explicit batch; handoff schemas differ by region.
        assert inputs[-1]["sha256"] in json.dumps(data), f"Current regional hash absent from handoff: {unit}"
    work = HERE / "work"
    work.mkdir(exist_ok=True)
    backup = work / f"Project_before_{batch_name}_{before[:12]}.xlsx"
    shutil.copy2(project, backup)
    assert sha(project) == before == sha(backup)
    receipt = {"batch": batch_name, "project_before_sha256": before, "regional_inputs": inputs,
               "scope": "Generated central regional tables only; shared HTML/browser reconciliation remains pending."}
    destination = HERE / "verification" / f"{batch_name}_integration.json"
    destination.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    command = [sys.executable, "-X", "utf8", str(ROOT / "tools/update_project.py"), "--root", str(ROOT),
               "--region", *[str(ROOT / item["path"]) for item in inputs]]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    receipt["command_exit_code"] = result.returncode
    receipt["command_stdout"] = result.stdout
    receipt["command_stderr"] = result.stderr
    destination.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    tables = metadata_and_regions(project)
    receipt["central_source_tables_unchanged"] = all(tables[k] == snapshot["tables"][k]
                                                    for k in ("Models & coverage", "Papers"))
    receipt["integrated_regions"] = []
    for item in inputs:
        assert sha(ROOT / item["path"]) == item["sha256"], f"Region changed during batch: {item['unit_id']}"
        matches = [r for r in tables["Regions & status"] if r["unit_id"] == item["unit_id"]]
        assert len(matches) == 1 and matches[0]["sha256"] == item["sha256"]
        receipt["integrated_regions"].append(matches[0])
    receipt["project_after_sha256"] = sha(project)
    destination.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    assert receipt["central_source_tables_unchanged"], "Inspect central metadata changes before refreshing cache"
    snapshot["project_sha256"] = receipt["project_after_sha256"]
    snapshot["provenance"] += f"; {batch_name} numerical consolidation with exact source-table comparison"
    snapshot.setdefault("numerical_integration_evidence", []).append(destination.relative_to(HERE).as_posix())
    snapshot_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"batch": batch_name, "units": units, "source_metadata_preserved": True,
                      "project_sha256": receipt["project_after_sha256"]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_name")
    parser.add_argument("units", nargs="+")
    args = parser.parse_args()
    run(args.batch_name, args.units)
