"""Bounded administrative publication closure; never rewrites scientific payloads."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[6]
QA = Path(__file__).resolve().parent.parent / "qa"
PLAN = "explainers/plans/project_reorganization_plan.md"
LEDGER = "common_reference_data/provenance/source_paths.csv"
GRAPH = "tools/knowledge_graph/"
TARGETS = {PLAN, *(GRAPH + name for name in (
    "graph.json", "graph.html", "GRAPH_REPORT.md", "REFRESH_SCOPE.md"
))}
WORK = "regions/LME/LME_028/work/2026-10-04_000002_reorganization/"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_report(name: str, result: dict) -> None:
    (QA / name).write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print(json.dumps(result, ensure_ascii=False))


def ledger() -> None:
    baseline = list(csv.DictReader(io.StringIO(git("show", "HEAD:" + LEDGER).decode("utf8"))))
    current = list(csv.DictReader(io.StringIO((ROOT / LEDGER).read_text(encoding="utf8"))))
    assert current == baseline, "Unexpected ledger changes before bounded closure"
    changes = []
    for row in current:
        path = row["retained_path"]
        if path in TARGETS and row["action"] != "removed":
            actual = sha((ROOT / path).read_bytes())
            if actual != row["retained_sha256"]:
                changes.append({"retained_path": path, "previous_current_sha256": row["retained_sha256"], "current_sha256": actual})
                row["retained_sha256"] = actual
    for old, new in zip(baseline, current):
        assert all(old[key] == new[key] for key in old if key != "retained_sha256")
        assert old["retained_sha256"] == new["retained_sha256"] or old["retained_path"] in TARGETS
    assert len(current) == len(baseline)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(current[0]), lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(current)
    (ROOT / LEDGER).write_bytes(buffer.getvalue().encode("utf8"))
    write_report("ledger_publication_closure.json", {"rows": len(current), "original_sha_and_other_fields_unchanged": True, "bounded_hash_updates": changes})


def inventory() -> None:
    entries = git("status", "--porcelain=v1", "-z", "--untracked-files=all").split(b"\0")
    paths = []
    for entry in entries:
        if not entry:
            continue
        text = entry.decode("utf8")
        assert text[:2] in {" M", "??"}, text
        path = text[3:]
        assert path in {PLAN, LEDGER} or path.startswith(GRAPH) or path in {
            WORK + "qa/publication_record.json",
            WORK + "qa/ledger_publication_closure.json",
            WORK + "code/publication_closure.py",
        }, "Unexpected change: " + path
        assert (ROOT / path).is_file(), path
        paths.append(path)
    (QA / "publication_stage_paths.nul").write_bytes(b"\0".join(path.encode("utf8") for path in paths) + b"\0")
    print(json.dumps({"authorized_metadata_paths": paths, "count": len(paths)}, ensure_ascii=False))


def staged() -> None:
    paths = [p.decode("utf8") for p in git("diff", "--cached", "--name-only", "-z").split(b"\0") if p]
    assert paths
    for path in paths:
        assert git("show", ":" + path) == (ROOT / path).read_bytes(), path
    completion = json.loads((ROOT / GRAPH / "provenance/completion_verification.json").read_text(encoding="utf8"))
    assert completion["pass"] and completion["integrity_pass"]
    assert completion["latest_plan_sha256"] == sha((ROOT / PLAN).read_bytes())
    assert completion["graph_sha256"] == sha((ROOT / GRAPH / "graph.json").read_bytes())
    assert completion["html_sha256"] == sha((ROOT / GRAPH / "graph.html").read_bytes())
    assert completion["report_sha256"] == sha((ROOT / GRAPH / "GRAPH_REPORT.md").read_bytes())
    graph = json.loads((ROOT / GRAPH / "graph.json").read_text(encoding="utf8"))
    node_ids = {node["id"] for node in graph["nodes"]}
    assert len(node_ids) == len(graph["nodes"]) == completion["nodes"]
    assert len(graph["links"]) == completion["topology_pairs"]
    assert all(edge["source"] in node_ids and edge["target"] in node_ids for edge in graph["links"])
    assert not git("diff", "--name-only"), "Unstaged changes remain"
    write_report("publication_staged_verification.json", {"pass": True, "exact_staged_files": len(paths), "plan_actual_sha256": completion["latest_plan_sha256"], "graph_actual_sha256": completion["graph_sha256"], "html_actual_sha256": completion["html_sha256"], "source_and_endpoint_checks": "PASS in graph completion record", "scientific_changes": 0})


if __name__ == "__main__":
    {"ledger": ledger, "inventory": inventory, "staged": staged}[sys.argv[1]]()
