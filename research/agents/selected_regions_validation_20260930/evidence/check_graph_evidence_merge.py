"""Verify graph preservation against the real baseline and focused edge cases."""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path

from graph_evidence_merge import canonical, edge_records, merge_records, write_scratch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def expect_rejection(call, text):
    try:
        call()
    except ValueError as exc:
        assert text in str(exc), str(exc)
    else:
        raise AssertionError(f"Expected rejection containing {text}")


def run():
    graph_path = ROOT / "tools/knowledge_graph/graph.json"
    hashes_path = ROOT / "tools/knowledge_graph/source_hashes.json"
    graph_bytes = graph_path.read_bytes()
    hashes_bytes = hashes_path.read_bytes()
    graph = json.loads(graph_bytes)
    hashes = json.loads(hashes_bytes)
    candidate, baseline_audit = merge_records(graph, {}, hashes, hashes)
    assert {n["id"]: n for n in candidate["nodes"]} == {n["id"]: n for n in graph["nodes"]}
    assert Counter(map(canonical, edge_records(candidate))) == Counter(map(canonical, edge_records(graph)))
    assert Counter(map(canonical, candidate["hyperedges"])) == Counter(map(canonical, graph["hyperedges"]))
    checks = {"real_baseline_nodes_evidence_hyperedges_exact": True}

    sample = {"directed": False, "nodes": [
        {"id": "stable", "label": "Stable", "source_file": "stable.md", "custom": [1, 2]},
        {"id": "changed", "label": "Changed", "source_file": "changed.md", "source_location": "L4"},
        {"id": "prior", "label": "Former reference: prior", "source_file": None, "retained_for_unchanged_source_evidence": True}],
        "links": [{"source": "changed", "target": "stable", "source_file": "changed.md", "relation": "outdated",
                   "additional_evidence": [{"_src": "stable", "_tgt": "changed", "source_file": "stable.md", "relation": "retained",
                                             "additional_evidence": [{"source": "prior", "target": "stable", "source_file": None, "relation": "historical"}]}]}],
        "hyperedges": [{"id": "stable_h", "nodes": ["stable", "changed"], "source_file": "stable.md"}]}
    before = {"stable.md": "s", "changed.md": "c"}
    after = {"stable.md": "s", "changed.md": "new"}
    fresh = {"nodes": [{"id": "new", "source_file": "changed.md", "label": "New current entity"}],
             "edges": [{"source": "new", "target": "stable", "source_file": "changed.md", "relation": "current"}]}
    merged, audit = merge_records(sample, fresh, before, after)
    nodes = {n["id"]: n for n in merged["nodes"]}
    assert nodes["stable"] == sample["nodes"][0]
    assert nodes["prior"] == sample["nodes"][2]
    assert nodes["changed"]["source_file"] is None
    assert nodes["changed"]["historical_source_sha256"] == "c"
    assert nodes["changed"]["historical_source_location"] == "L4"
    assert nodes["changed"]["authority"].startswith("former")
    assert merged["hyperedges"] == sample["hyperedges"]
    evidence = edge_records(merged)
    assert {e["relation"] for e in evidence} == {"retained", "historical", "current"}
    assert next(e for e in evidence if e["relation"] == "retained")["source"] == "stable"
    checks["nested_evidence_direction_and_former_anchors_preserved"] = True

    collision = copy.deepcopy(fresh)
    collision["nodes"].append({"id": "stable", "source_file": "changed.md", "label": "Wrong replacement"})
    expect_rejection(lambda: merge_records(sample, collision, before, after), "collision")
    dangling = copy.deepcopy(fresh)
    dangling["edges"][0]["target"] = "nonexistent"
    expect_rejection(lambda: merge_records(sample, dangling, before, after), "Dangling evidence")
    extra = copy.deepcopy(fresh)
    extra["edges"][0]["source_file"] = "outside.md"
    expect_rejection(lambda: merge_records(sample, extra, before, after), "outside frozen corpus")
    expect_rejection(lambda: write_scratch(graph_path, {}), "Output must stay")
    checks["collisions_dangling_out_of_scope_and_live_writes_rejected"] = True
    assert graph_path.read_bytes() == graph_bytes and hashes_path.read_bytes() == hashes_bytes
    output = {"checks": checks, "baseline": baseline_audit,
              "graph_sha256": hashlib.sha256(graph_bytes).hexdigest(),
              "source_hashes_sha256": hashlib.sha256(hashes_bytes).hexdigest(),
              "helper_sha256": hashlib.sha256((HERE / "graph_evidence_merge.py").read_bytes()).hexdigest(),
              "passed": True, "live_graph_unchanged": True}
    (HERE / "verification/graph_evidence_merge_coordinator_checks.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output), flush=True)


if __name__ == "__main__":
    run()
