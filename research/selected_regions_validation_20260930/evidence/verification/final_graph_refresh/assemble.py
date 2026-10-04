"""Root-only, bounded final graph assembly; outputs remain in staging."""
from pathlib import Path
import collections
import copy
import hashlib
import json
import math
import os
import re
import sys

S = Path(__file__).resolve().parent
B = S.parents[2]
R = B.parents[2]
sys.path.insert(0, str(B))
os.environ['GRAPHIFY_OUT'] = str(S)
from graph_evidence_merge import read, canonical, edge_records, normalize_fresh, merge_records
import networkx as nx
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections


def save(name, data):
    (S / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main():
    frozen = read(S / 'frozen.source_hashes.json')
    baseline = read(S / 'baseline.source_hashes.json')
    for f, h in frozen.items():
        assert hashlib.sha256((R / f).read_bytes()).hexdigest() == h, f
    old = read(S / 'baseline.graph.json')
    fragments = []
    semantic_checks = []
    assigned_seen = set()
    detection = read(S/'detection.json')
    expected_semantic = {Path(f).resolve().relative_to(R).as_posix() for kind, paths in detection['new_files'].items() if kind != 'code' for f in paths}
    file_types = {'code', 'document', 'paper', 'image', 'rationale', 'concept'}
    for k in range(1, 4):
        filename = f'chunk_{k:02d}.json'
        d = normalize_fresh(read(S / filename), R)
        assigned = {a['path']: a['sha256'] for a in read(S / f'chunk_{k:02d}_sources.json')}
        assert not assigned_seen.intersection(assigned), filename
        assigned_seen.update(assigned)
        assert all(f in frozen and h == frozen[f] for f,h in assigned.items()), filename
        ids = {n['id'] for n in d['nodes']}
        assert len(ids) == len(d['nodes']), filename
        covered = {n.get('source_file') for n in d['nodes']}
        assert covered == set(assigned), (filename, covered ^ set(assigned))
        assert len(d.get('hyperedges', [])) <= 3
        for n in d['nodes']:
            assert re.fullmatch(r'[a-z0-9_]+', n['id']), n
            assert n['file_type'] in file_types, n
            assert n['source_sha256'] == assigned[n['source_file']], n
        for e in d['edges']:
            assert e['source'] in ids and e['target'] in ids, e
        for e in d['edges'] + d.get('hyperedges', []):
            assert e['source_file'] in assigned, e
            assert e['confidence'] in {'EXTRACTED', 'INFERRED', 'AMBIGUOUS'}, e
            score = e['confidence_score']
            assert math.isfinite(score) and math.isfinite(e.get('weight',1)), e
            assert (e['confidence'] == 'EXTRACTED' and score == 1) or (e['confidence'] == 'INFERRED' and score in {.95, .85, .75, .65, .55}) or (e['confidence'] == 'AMBIGUOUS' and .1 <= score <= .3), e
        for h in d.get('hyperedges', []):
            assert re.fullmatch(r'[a-z0-9_]+', h['id']), h
            assert h['confidence'] in {'EXTRACTED','INFERRED'}, h
            assert set(h['nodes']) <= ids and len(h['nodes']) >= 3, h
        for row in d['nodes'] + d['edges'] + d.get('hyperedges', []):
            sf = row['source_file']
            assert row.get('source_location'), row
            loc = row['source_location']
            assert not isinstance(loc, bool), row
            line = re.fullmatch(r'(?:L(?:ine)?\s*)?(\d+)(?:\s*[-–:]\s*(?:L)?(\d+))?', str(loc), re.I)
            assert line, row
            first = int(line.group(1)); last = int(line.group(2) or first)
            assert 1 <= first <= last <= len((R/sf).read_text(encoding='utf-8-sig').splitlines()), row
            if row.get('source_sha256'):
                assert row['source_sha256'] == assigned[sf], row
            row['source_sha256'] = assigned[sf]
        semantic_checks.append({'fragment': filename, 'files': len(assigned), 'nodes': len(d['nodes']), 'edges': len(d['edges']), 'hyperedges': len(d.get('hyperedges', [])), 'sha256': hashlib.sha256((S/filename).read_bytes()).hexdigest(), 'source_hashes_and_line_ranges': 'PASS'})
        fragments.append(d)
    assert assigned_seen == expected_semantic, assigned_seen ^ expected_semantic

    ast_snapshot = read(S/'ast_snapshot_verification.json')
    assert ast_snapshot['status'] == 'PASS'
    assert ast_snapshot['ast_sha256'] == hashlib.sha256((S/'ast.json').read_bytes()).hexdigest()
    assert all(f in frozen and h == frozen[f] for f,h in ast_snapshot['source_sha256'].items())
    assert set(ast_snapshot['source_sha256']) == {Path(f).resolve().relative_to(R).as_posix() for f in detection['new_files']['code']}
    ast = normalize_fresh(read(S/'ast.json'), R)
    # Reviewed AST generic-reference collisions: Graphify emits unqualified
    # Any/Path IDs at ModelData annotations, while the baseline attributes the
    # same short IDs to unchanged files. Keep both provenance records intact.
    remaps = {'any': 'pprestimation_modeldata_any_reference',
              'path': 'pprestimation_modeldata_path_reference'}
    for n in ast['nodes']:
        if n['id'] in remaps:
            assert n['source_file'] == 'tools/scientific_code/PPREstimation/ModelData.py'
            n['id'] = remaps[n['id']]
            n['reference_scope'] = 'AST annotation reference; namespaced to preserve unchanged source provenance'
    for e in ast['edges']:
        for endpoint in ['source','target']:
            e[endpoint] = remaps.get(e[endpoint], e[endpoint])
    unchanged_files = {f for f,h in frozen.items() if baseline.get(f) == h}
    available = {n['id'] for n in old['nodes'] if not n.get('source_file') or n['source_file'] in unchanged_files} | {n['id'] for n in ast['nodes']}
    retained = [e for e in edge_records(old) if not e.get('source_file') or e['source_file'] in unchanged_files]
    available |= {e[k] for e in retained for k in ['source','target']}
    available |= {nid for h in old['hyperedges'] if not h.get('source_file') or h['source_file'] in unchanged_files for nid in h['nodes']}
    missing = {e[k] for e in ast['edges'] for k in ('source', 'target')} - available
    # AST import edges identify symbols but do not claim the external module
    # implementation was read. Explicit stubs prevent implicit NX endpoints.
    for nid in sorted(missing):
        ast['nodes'].append({'id': nid, 'label': nid.replace('_', '.'), 'file_type': 'code', 'source_file': None, 'source_location': None, 'external_reference': True, 'authority': 'AST symbol reference only; implementation not inspected', '_origin': 'ast'})
    for n in ast['nodes']:
        if not n.get('source_file'):
            n['external_reference'] = True
        else:
            n['source_sha256'] = frozen[n['source_file']]
    for e in ast['edges']:
        e['source_sha256'] = frozen[e['source_file']]
    save('ast.resolved.json', ast)
    fragments.insert(0, ast)
    fresh = {'nodes': [], 'edges': [], 'hyperedges': []}
    for d in fragments:
        for key in fresh:
            fresh[key].extend(d.get(key, []))
    merged, audit = merge_records(old, fresh, baseline, frozen)
    assert len({h['id'] for h in merged['hyperedges']}) == len(merged['hyperedges'])
    merged.pop('built_at_commit', None)
    merged['freshness'] = {'base_commit': 'd14c71a9d2e9f168af8c12e2ccd04c2d861df1cc', 'working_tree_snapshot': True, 'source_hashes_file': 'source_hashes.json', 'source_manifest_sha256': hashlib.sha256((S/'frozen.source_hashes.json').read_bytes()).hexdigest(), 'note': 'Exact source bytes, including frontmatter, determine freshness. Base commit is not a claim that this graph was built from an unchanged checkout.'}
    G = nx.DiGraph() if merged.get('directed') else nx.Graph()
    for n in merged['nodes']:
        G.add_node(n['id'], **{k: copy.deepcopy(v) for k,v in n.items() if k != 'id'})
    for e in merged['links']:
        attrs = {k: copy.deepcopy(v) for k,v in e.items() if k not in {'source','target'}}
        attrs.update(_src=e['source'], _tgt=e['target'])
        G.add_edge(e['source'], e['target'], **attrs)
    G.graph['hyperedges'] = copy.deepcopy(merged['hyperedges'])
    communities = cluster(G)
    membership = {n: c for c, members in communities.items() for n in members}
    assert set(membership) == set(G)
    # Evidence attributes remain unchanged; community is derived topology and
    # is recomputed consistently for JSON queries, HTML and the report.
    for n in merged['nodes']:
        n['community'] = membership[n['id']]
        G.nodes[n['id']]['community'] = membership[n['id']]
    merged['communities'] = {str(c): members for c,members in communities.items()}
    cohesion = score_all(G, communities)
    labels_old = read(R/'tools/knowledge_graph/.graphify_labels.json')
    old_members = collections.defaultdict(set)
    for n in old['nodes']:
        old_members[str(n.get('community'))].add(n['id'])
    label_candidates = []
    for c, members in communities.items():
        members_set = set(members)
        best_old = max(old_members, key=lambda k: len(members_set & old_members[k])/len(members_set | old_members[k]))
        overlap = len(members_set & old_members[best_old])/len(members_set | old_members[best_old])
        top = sorted(members, key=lambda n: G.degree(n), reverse=True)[:12]
        label_candidates.append({'community': c, 'count':len(members), 'best_old_label': labels_old.get(best_old), 'jaccard': overlap, 'top_nodes': [{'id':n,'label':G.nodes[n].get('label'), 'source_file':G.nodes[n].get('source_file')} for n in top]})
    analysis = {'communities': merged['communities'], 'cohesion': cohesion, 'gods': god_nodes(G), 'surprises': surprising_connections(G, communities)}
    save('merged.graph.json', merged)
    save('analysis.json', analysis)
    save('community_label_candidates.json', label_candidates)
    save('merge_audit.json', {**audit, 'semantic_checks': semantic_checks, 'ast_reviewed_reference_remaps': remaps, 'ast_input_sha256': hashlib.sha256((S/'ast.json').read_bytes()).hexdigest(), 'ast_external_stubs': sorted(missing), 'communities': len(communities), 'freshness_checks': len(frozen), 'derived_node_attribute_recomputed': 'community; all other protected node attributes preserved exactly'})
    print(json.dumps({'nodes':len(merged['nodes']),'pairs':len(merged['links']),'communities':len(communities),'hyperedges':len(merged['hyperedges']), 'semantic_checks':semantic_checks}))


if __name__ == '__main__':
    main()
