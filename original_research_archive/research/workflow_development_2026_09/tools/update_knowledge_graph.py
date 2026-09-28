"""Finish a scoped graphify refresh after host-agent semantic extraction.

Use the interpreter saved in graphify-out/.graphify_python. The .graphifyignore
defines the source/review corpus. This helper never executes project model code.
Semantic chunks must be produced by host agents using graphify's extraction spec.
Run the ast phase, then merge, review/write .graphify_labels.json, then render.
"""
from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'graphify-out'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def relative(value):
    if not value:
        return value
    value = str(value).replace('\\', '/')
    prefix = ROOT.as_posix() + '/'
    if value.lower().startswith(prefix.lower()):
        value = value[len(prefix):]
    return value.removeprefix('./')


def normalize(extraction):
    d = copy.deepcopy(extraction)
    for kind in ('nodes', 'edges', 'links', 'hyperedges'):
        for item in d.get(kind, []):
            if 'source_file' in item:
                item['source_file'] = relative(item['source_file'])
    return d


def detect_current():
    from graphify.detect import detect_incremental
    d = detect_incremental(ROOT)
    if d['total_files'] > 500 or d['total_words'] > 2_000_000:
        raise RuntimeError('Scope exceeded the approved corpus ceiling; review .graphifyignore.')
    write(OUT / '.graphify_incremental.json', d)
    write(OUT / '.graphify_detect.json', {
        **d, 'all_files': d['files'], 'files': d['new_files'],
        'total_files': d['total_files'], 'changed_files': d['new_total'],
    })
    return d


def ast():
    from graphify.extract import extract
    d = detect_current()
    files = [Path(f) for f in d['new_files']['code']]
    result = extract(files, cache_root=ROOT)
    write(OUT / '.graphify_ast.json', normalize(result))
    write(OUT / '.refresh_source_hashes.json', {
        relative(f): hashlib.sha256(Path(f).read_bytes()).hexdigest()
        for fs in d['files'].values() for f in fs
    })
    print(f'AST: {len(files)} changed files, {len(result["nodes"])} nodes, {len(result["edges"])} edges')


def merge():
    from graphify.build import build_merge
    from graphify.cluster import cluster, score_all
    from graphify.analyze import god_nodes, surprising_connections, suggest_questions
    from graphify.cache import save_semantic_cache
    from graphify.export import to_json

    d = read(OUT / '.graphify_incremental.json')
    expected_hashes = read(OUT / '.refresh_source_hashes.json')
    changed_during_run = [f for f, h in expected_hashes.items()
                          if hashlib.sha256((ROOT / f).read_bytes()).hexdigest() != h]
    if changed_during_run:
        raise RuntimeError(f'Source files changed during extraction: {changed_during_run}')
    corpus = {relative(f) for fs in d['files'].values() for f in fs}
    changed = {relative(f) for fs in d['new_files'].values() for f in fs}
    old_path = OUT / '.graphify_old.json'
    if not old_path.exists():
        old_path.write_bytes((OUT / 'graph.json').read_bytes())
    old = normalize(read(old_path))
    previous_ids = {n['id'] for n in old['nodes']}
    prune = {relative(f) for f in d.get('deleted_files', [])} | changed
    prune |= {n.get('source_file') for n in old['nodes'] if n.get('source_file') not in corpus}
    retained_nodes = [n for n in old['nodes'] if n.get('source_file') not in prune]
    retained_ids = {n['id'] for n in retained_nodes}
    # Defer endpoint filtering until fresh IDs are known: an unchanged caller can
    # still refer to a changed function that the AST recreates with the same ID.
    candidate_edges = [e for e in old.get('links', old.get('edges', []))
                       if e.get('source_file') not in prune]
    candidate_hyper = [h for h in old.get('hyperedges', [])
                       if h.get('source_file') not in prune]

    chunks = []
    chunk_audits = []
    expected_chunks = read(OUT / '.semantic_chunks.json')['chunks']
    for number, files in enumerate(expected_chunks, 1):
        p = OUT / f'.graphify_chunk_{number:02d}.json'
        chunk = normalize(read(p))
        ids = {n['id'] for n in chunk['nodes']}
        assert len(ids) == len(chunk['nodes']), f'duplicate node IDs in chunk {number}'
        assert all(re.fullmatch('[a-z0-9_]+', n['id']) for n in chunk['nodes'])
        assert all(n['file_type'] in {'code', 'document', 'paper', 'image', 'rationale', 'concept'} for n in chunk['nodes'])
        assert all(n.get('source_file') in corpus for n in chunk['nodes']), number
        for e in chunk['edges']:
            assert e['source'] in ids and e['target'] in ids, (number, 'dangling semantic edge', e)
            expected = {'EXTRACTED': {1.0}, 'INFERRED': {.95, .85, .75, .65, .55}}
            if e['confidence'] == 'AMBIGUOUS':
                assert .1 <= e['confidence_score'] <= .3
            else:
                assert e['confidence_score'] in expected[e['confidence']], (number, e)
        # Agent tool does not expose actual usage. Schema zeros are placeholders.
        chunk['input_tokens'] = 0
        chunk['output_tokens'] = 0
        chunk_audits.append({'chunk': number, 'files': len(files), 'nodes': len(chunk['nodes']),
                             'edges': len(chunk['edges']), 'token_usage': None,
                             'usage_status': 'unavailable from host subagent tool'})
        chunks.append(chunk)
    semantic = {'nodes': [], 'edges': [], 'hyperedges': []}
    for c in chunks:
        for k in semantic:
            semantic[k].extend(c.get(k, []))
    # Same identifiers across different source documents would erase provenance.
    by_id = collections.defaultdict(set)
    for n in semantic['nodes']:
        by_id[n['id']].add(n['source_file'])
    assert not {k: v for k, v in by_id.items() if len(v) > 1}, 'semantic ID collisions across files'
    save_semantic_cache(semantic['nodes'], semantic['edges'], semantic['hyperedges'], root=ROOT)
    fresh = normalize(read(OUT / '.graphify_ast.json'))
    fresh['nodes'] += semantic['nodes']
    fresh['edges'] += semantic['edges']
    fresh['hyperedges'] = semantic['hyperedges']
    fresh['input_tokens'] = fresh['output_tokens'] = 0
    valid_ids = retained_ids | {n['id'] for n in fresh['nodes']}
    retained_edges = [e for e in candidate_edges
                      if e['source'] in valid_ids and e['target'] in valid_ids]
    retained_hyper = [h for h in candidate_hyper if set(h.get('nodes', [])) <= valid_ids]
    boundary_edges = [e for e in retained_edges
                      if e['source'] not in retained_ids or e['target'] not in retained_ids]
    boundary_hyper = [h for h in retained_hyper if not set(h.get('nodes', [])) <= retained_ids]
    filtered = {'nodes': retained_nodes, 'links': retained_edges, 'hyperedges': retained_hyper}
    write(OUT / '.graphify_retained.json', filtered)

    # Installed build_merge prunes after insertion, which would also remove fresh
    # nodes from changed files. Prune only the old JSON first, then merge safely.
    # Fuzzy dedup is disabled so similarly named functions in different files survive.
    G = build_merge([fresh], graph_path=OUT / '.graphify_retained.json', dedup=False,
                    directed=bool(old.get('directed', False)), root=ROOT)
    # A simple graph permits only one edge per pair. Keep unchanged-source
    # evidence and its original direction; retain any distinct fresh evidence
    # as an additional record rather than silently replacing either provenance.
    preservation_conflicts = 0
    for e in retained_edges:
        source, target = e['source'], e['target']
        attrs = {k: v for k, v in e.items() if k not in {'source', 'target'}}
        attrs.update(_src=source, _tgt=target)
        current = dict(G.get_edge_data(source, target) or {})
        if current and any(current.get(k) != v for k, v in attrs.items()):
            preservation_conflicts += 1
            attrs['additional_evidence'] = [current]
        G.add_edge(source, target, **attrs)
    G.graph['hyperedges'] = retained_hyper + semantic['hyperedges']
    lost_retained = retained_ids - set(G.nodes)
    assert not lost_retained, f'unaffected nodes lost: {sorted(lost_retained)[:10]}'
    assert all(G.has_edge(e['source'], e['target']) for e in retained_edges), 'unaffected edge lost'
    assert all(G.edges[e['source'], e['target']]['_src'] == e['source']
               and G.edges[e['source'], e['target']]['_tgt'] == e['target']
               for e in retained_edges), 'unchanged-source edge direction lost'
    communities = cluster(G)
    cohesion = score_all(G, communities)
    assert to_json(G, communities, str(OUT / 'graph.json'), force=True)
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    labels = {i: f'Community {i}' for i in communities}
    analysis = {'communities': communities, 'cohesion': cohesion, 'gods': gods,
                'surprises': surprises, 'questions': suggest_questions(G, communities, labels)}
    write(OUT / '.graphify_analysis.json', analysis)
    write(OUT / '.graphify_labels.json', labels)
    graph_sources = {n.get('source_file') for _, n in G.nodes(data=True)}
    audit = {'corpus_files': d['total_files'], 'corpus_words': d['total_words'],
             'changed_files': len(changed), 'pruned_sources': sorted(x for x in prune if x),
             'old_nodes': len(old['nodes']), 'old_edges': len(old.get('links', [])),
             'retained_nodes': len(retained_nodes), 'retained_edges': len(retained_edges),
             'boundary_edges_preserved': len(boundary_edges),
             'boundary_hyperedges_preserved': len(boundary_hyper),
             'unchanged_source_edges_removed_for_missing_endpoints': len(candidate_edges) - len(retained_edges),
             'edge_pairs_with_additional_evidence': preservation_conflicts,
             'new_nodes': G.number_of_nodes(), 'new_edges': G.number_of_edges(),
             'added_node_ids': sorted(set(G.nodes) - previous_ids),
             'removed_node_ids': sorted(previous_ids - set(G.nodes)),
             'communities': len(communities), 'semantic_chunks': chunk_audits,
             'unrepresented_source_files': sorted(corpus - graph_sources),
             'outside_scope_source_files': sorted(x for x in graph_sources - corpus if x),
             'token_usage': None, 'monetary_cost': None,
             'cost_note': 'Host agent tools expose no actual usage; no zero-cost claim.',
             'built_from_working_tree': True, 'algorithm_execution': False}
    audit['retained_legacy_inferred_scores_outside_current_rubric'] = sum(
        e.get('confidence') == 'INFERRED' and e.get('confidence_score') not in {.95, .85, .75, .65, .55}
        for e in retained_edges)
    write(OUT / 'refresh_audit.json', audit)
    # Human inspection drives community names, using these concise member samples.
    write(OUT / '.community_samples.json', {
        str(k): {'count': len(ns), 'labels': [G.nodes[n].get('label', n) for n in ns[:12]],
                 'sources': collections.Counter(G.nodes[n].get('source_file', '') for n in ns).most_common(5)}
        for k, ns in communities.items()
    })
    print(f'Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities')
    print(f'Preserved {len(retained_nodes)} unaffected nodes and {len(retained_edges)} unaffected edges')


def render():
    from graphify.build import build_from_json
    from graphify.analyze import suggest_questions
    from graphify.export import to_html
    from graphify.report import generate
    from graphify.detect import save_manifest

    d = read(OUT / '.graphify_incremental.json')
    hashes = read(OUT / '.refresh_source_hashes.json')
    assert all(hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h for f, h in hashes.items()), 'source changed before render'
    raw = read(OUT / 'graph.json')
    G = build_from_json(raw, directed=raw.get('directed', False), root=ROOT)
    a = read(OUT / '.graphify_analysis.json')
    communities = {int(k): v for k, v in a['communities'].items()}
    cohesion = {int(k): v for k, v in a['cohesion'].items()}
    labels = {int(k): v for k, v in read(OUT / '.graphify_labels.json').items()}
    assert set(labels) == set(communities)
    assert all(not x.startswith('Community ') for x in labels.values())
    if G.number_of_nodes() > 5000:
        raise RuntimeError('Warn the user and select aggregate HTML before rendering >5000 nodes.')
    questions = suggest_questions(G, communities, labels)
    report = generate(G, communities, cohesion, labels, a['gods'], a['surprises'], d,
                      {'input': 0, 'output': 0}, '.', suggested_questions=questions)
    report = report.replace('- Token cost: 0 input · 0 output',
        '- Token usage and monetary cost: unavailable from the host subagent tool; no zero-cost claim.')
    report += '\n\n## Refresh scope and provenance\n\n' + (OUT / 'REFRESH_SCOPE.md').read_text(encoding='utf-8')
    report += '\n\nThe graph reflects the current working tree before the integration commit. The stored commit identifies its base; the portable manifest records actual source hashes. Legacy confidence scores are retained on unchanged edges and must not be mistaken for newly calibrated estimates.\n'
    (OUT / 'GRAPH_REPORT.md').write_text(report, encoding='utf-8')
    to_html(G, communities, str(OUT / 'graph.html'), community_labels=labels)
    # save_manifest preserves old existing-file entries; prune excluded entries explicitly.
    save_manifest(d['files'], root=ROOT)
    p = OUT / 'manifest.json'
    corpus = {relative(f) for fs in d['files'].values() for f in fs}
    manifest = {relative(k): v for k, v in read(p).items() if relative(k) in corpus}
    write(p, manifest)
    cost_path = OUT / 'cost.json'
    cost = read(cost_path) if cost_path.exists() else {'runs': []}
    cost.setdefault('runs', []).append({'date': datetime.now(timezone.utc).isoformat(),
        'input_tokens': None, 'output_tokens': None, 'monetary_cost': None,
        'files': d['total_files'], 'status': 'actual usage unavailable from host subagent tools'})
    cost.setdefault('historical_totals_as_previously_recorded', {
        'input': cost.get('total_input_tokens'), 'output': cost.get('total_output_tokens')})
    cost['total_input_tokens'] = cost['total_output_tokens'] = None
    cost['total_status'] = 'Incomplete: current usage unavailable; historical usage not independently verified.'
    write(cost_path, cost)
    validate()


def validate():
    raw = read(OUT / 'graph.json')
    ids = {n['id'] for n in raw['nodes']}
    assert len(ids) == len(raw['nodes'])
    assert all(e['source'] in ids and e['target'] in ids for e in raw['links'])
    assert all(set(h['nodes']) <= ids for h in raw.get('hyperedges', []))
    manifest = read(OUT / 'manifest.json')
    assert all(not Path(k).is_absolute() and '\\' not in k and (ROOT / k).exists() for k in manifest)
    sf = {n.get('source_file') for n in raw['nodes'] if n.get('source_file')}
    assert sf <= set(manifest), sorted(sf - set(manifest))
    assert not any('settings.local' in json.dumps(n) for n in raw['nodes'])
    assert not any('settings.local' in json.dumps(e) for e in raw['links'])
    all_text = json.dumps(raw, ensure_ascii=False).lower()
    required = {
        'sppr_inner': 'sppr_inner' in all_text,
        'sppr_PP': 'sppr_pp' in all_text,
        'pilot_only': 'pilot' in all_text,
        'method_ratios': 'ratio' in all_text,
        'b_and_rho': 'rho' in all_text and ('recycling' in all_text or 'detritus' in all_text),
        'Thailand_1980': 'thailand' in all_text and '1980' in all_text,
        'Guinea_geographic_transfer': 'guinea' in all_text and ('geographic' in all_text or 'extrapolat' in all_text),
        'new_paper_validation': 'docs/NEW_PAPER_VALIDATION.md' in sf,
        'Jensen_preserved': 'jensen' in all_text,
        'Claude_entrypoints': all(f'skills/claude/{s}/SKILL.md' in sf for s in ('ecopath-extraction', 'ecopath-paper-to-ppr', 'ewe-species-to-group-mapper')),
        'Codex_entrypoints': all(f'skills/codex/{s}/SKILL.md' in sf for s in ('ecopath-extraction', 'ecopath-paper-to-ppr', 'ewe-species-to-group-mapper')),
        'integration_completion': 'docs/INTEGRATION_COMPLETION.md' in sf,
        'independent_Guinea_arm': 'data/LME_028/validation/combined-skill-comparison/README.md' in sf,
    }
    audit = read(OUT / 'refresh_audit.json')
    audit.update(required_content_checks=required, dangling_edges=0, portable_manifest=True,
                 personal_settings_present=False, source_files_represented=len(sf),
                 missing_source_files=sorted(set(manifest)-sf))
    write(OUT / 'refresh_audit.json', audit)
    assert all(required.values()), required
    print('Validated graph, source paths, all required integration topics and both skill sets.')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('phase', choices=('ast', 'merge', 'render', 'validate'))
    phase = ap.parse_args().phase
    {'ast': ast, 'merge': merge, 'render': render, 'validate': validate}[phase]()
