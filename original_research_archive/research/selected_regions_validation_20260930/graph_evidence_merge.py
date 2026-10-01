"""Reviewed graph-evidence merge safeguard; never writes the live graph.

Keep Graphify for extraction, clustering, analysis, and rendering. This helper
only merges its JSON records without the lossy build_from_json deduplication.
All CLI outputs must remain under this study's ignored work/graph_prepare directory.
"""
from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent / "work/graph_prepare"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_scratch(path, value):
    path = Path(path).resolve()
    if not path.is_relative_to(SCRATCH):
        raise ValueError(f"Output must stay in {SCRATCH}: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def evidence(edge, inherited=None):
    """Flatten separately attributed evidence, preserving each record's direction."""
    parent = inherited or {}
    row = copy.deepcopy(edge)
    children = row.pop("additional_evidence", [])
    row["source"] = row.pop("_src", row.get("source", parent.get("source")))
    row["target"] = row.pop("_tgt", row.get("target", parent.get("target")))
    if not row["source"] or not row["target"]:
        raise ValueError("Evidence record has no resolvable direction")
    yield row
    for child in children:
        yield from evidence(child, row)


def edge_records(graph):
    return [r for e in graph.get("links", graph.get("edges", [])) for r in evidence(e)]


def normalize_fresh(graph, root):
    graph = copy.deepcopy(graph)
    def visit(value):
        if isinstance(value, dict):
            if value.get("source_file"):
                p = Path(str(value["source_file"]).replace("\\", "/"))
                if p.is_absolute():
                    value["source_file"] = p.resolve().relative_to(root).as_posix()
                else:
                    value["source_file"] = p.as_posix().removeprefix("./")
            for v in value.values():
                visit(v)
        elif isinstance(value, list):
            for v in value:
                visit(v)
    visit(graph)
    return graph


def merge_records(old, fresh, baseline_hashes, frozen_hashes):
    unchanged = {f for f, h in frozen_hashes.items() if baseline_hashes.get(f) == h}
    affected = set(baseline_hashes) - unchanged
    old_nodes = {n["id"]: n for n in old["nodes"]}
    if len(old_nodes) != len(old["nodes"]):
        raise ValueError("Baseline has duplicate node IDs")
    protected = {k: copy.deepcopy(n) for k, n in old_nodes.items()
                 if not n.get("source_file") or n["source_file"] in unchanged}
    nodes = copy.deepcopy(protected)
    for n in fresh.get("nodes", []):
        sf = n.get("source_file")
        if sf and sf not in frozen_hashes:
            raise ValueError(f"Fresh node outside frozen corpus: {sf}")
        if n["id"] in nodes:
            prior = nodes[n["id"]]
            # An AST reference stub never supersedes a known/protected entity.
            if not sf and n.get("external_reference"):
                continue
            comparable = lambda x: {k: v for k, v in x.items()
                                    if k not in {"community", "norm_label"}}
            if comparable(n) != comparable(prior):
                raise ValueError(f"Node ID collision requires reviewed remap: {n['id']} "
                                 f"({prior.get('source_file')} vs {sf})")
            continue
        nodes[n["id"]] = copy.deepcopy(n)

    retained_edges = [e for e in edge_records(old)
                      if not e.get("source_file") or e["source_file"] in unchanged]
    retained_hyper = [copy.deepcopy(h) for h in old.get("hyperedges", [])
                      if not h.get("source_file") or h["source_file"] in unchanged]
    new_edges = edge_records(fresh)
    new_hyper = copy.deepcopy(fresh.get("hyperedges", []))
    for item in new_edges + new_hyper:
        if item.get("source_file") not in frozen_hashes:
            raise ValueError(f"Fresh evidence outside frozen corpus: {item.get('source_file')}")
    required = {e[k] for e in retained_edges for k in ("source", "target")}
    required |= {n for h in retained_hyper for n in h["nodes"]}
    created_anchors = []
    for nid in sorted(required - set(nodes)):
        if nid not in old_nodes:
            raise ValueError(f"Unchanged evidence references unknown ID: {nid}")
        anchor = copy.deepcopy(old_nodes[nid])
        sf = anchor.get("source_file")
        if sf not in affected or sf not in baseline_hashes:
            raise ValueError(f"Missing endpoint cannot be attributed to affected source: {nid}")
        anchor.update(source_file=None, source_location=None,
                      historical_source_file=sf,
                      historical_source_sha256=baseline_hashes[sf],
                      historical_source_location=old_nodes[nid].get("source_location"),
                      authority="former; retained only for unchanged historical evidence",
                      retained_for_unchanged_source_evidence=True)
        if not anchor.get("label", "").startswith("Former reference:"):
            anchor["label"] = "Former reference: " + anchor.get("label", nid)
        nodes[nid] = anchor
        created_anchors.append(nid)

    rows = retained_edges + new_edges
    hyperedges = retained_hyper + new_hyper
    for e in rows:
        if e["source"] not in nodes or e["target"] not in nodes:
            raise ValueError(f"Dangling evidence; resolve from actual source before merge: {e}")
    for h in hyperedges:
        if not set(h["nodes"]) <= set(nodes):
            raise ValueError(f"Dangling hyperedge: {h['id']}")
    seen_hyper = {}
    for h in hyperedges:
        if h["id"] in seen_hyper and canonical(seen_hyper[h["id"]]) != canonical(h):
            raise ValueError(f"Hyperedge ID collision requires reviewed remap: {h['id']}")
        seen_hyper[h["id"]] = h

    groups = collections.OrderedDict()
    directed = bool(old.get("directed", False))
    for e in rows:
        pair = (e["source"], e["target"])
        key = pair if directed else tuple(sorted(pair))
        groups.setdefault(key, []).append(copy.deepcopy(e))
    links = []
    for records in groups.values():
        row = records[0]
        if len(records) > 1:
            row["additional_evidence"] = records[1:]
        links.append(row)
    merged = copy.deepcopy(old)
    merged.pop("edges", None)
    merged.update(nodes=list(nodes.values()), links=links, hyperedges=hyperedges)
    # Do not let inherited graph.hyperedges retain a stale duplicated payload.
    if "hyperedges" in merged.get("graph", {}):
        merged["graph"]["hyperedges"] = copy.deepcopy(hyperedges)
    for nid, n in protected.items():
        assert nodes[nid] == n, f"Protected node attributes changed: {nid}"
    old_e = collections.Counter(map(canonical, retained_edges))
    new_e = collections.Counter(map(canonical, edge_records(merged)))
    assert not old_e - new_e, "Unchanged separately attributed evidence lost"
    old_h = collections.Counter(map(canonical, retained_hyper))
    new_h = collections.Counter(map(canonical, hyperedges))
    assert not old_h - new_h, "Unchanged hyperedge lost"
    audit = dict(unchanged_sources=len(unchanged), affected_sources=sorted(affected),
                 unchanged_node_attributes_preserved=len(protected),
                 unchanged_evidence_records_preserved=len(retained_edges),
                 unchanged_hyperedges_preserved=len(retained_hyper),
                 former_anchors_preserved=sum(bool(n.get("retained_for_unchanged_source_evidence"))
                                              for n in protected.values()),
                 created_historical_anchor_ids=created_anchors,
                 nodes=len(nodes), edge_pairs=len(links), evidence_records=len(rows),
                 hyperedges=len(hyperedges), token_usage=None, monetary_cost=None)
    return merged, audit


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "old-graph", "baseline-hashes", "frozen-hashes", "output", "audit"):
        ap.add_argument("--" + name, required=True)
    ap.add_argument("--fresh", nargs="+", required=True)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    frozen = read(args.frozen_hashes)
    for f, h in frozen.items():
        p = (root / f).resolve()
        if not p.is_relative_to(root) or hashlib.sha256(p.read_bytes()).hexdigest() != h:
            raise ValueError(f"Frozen source changed or escapes project: {f}")
    fresh = {"nodes": [], "edges": [], "hyperedges": []}
    for path in args.fresh:
        fragment = normalize_fresh(read(path), root)
        fresh["nodes"].extend(fragment.get("nodes", []))
        fresh["edges"].extend(fragment.get("edges", fragment.get("links", [])))
        fresh["hyperedges"].extend(fragment.get("hyperedges", []))
    merged, audit = merge_records(read(args.old_graph), fresh,
                                  read(args.baseline_hashes), frozen)
    write_scratch(args.output, merged)
    write_scratch(args.audit, audit)
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
