"""Bounded 437-source refresh after the 2026-11-14 publication transactions.

The current coordinator explicitly authorized the eight additions below within
the existing source roles. No work copies, binary science or model results are
added. This script never calculates scientific results or changes review status.
"""
import argparse
import collections
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pipeline

ROOT, GRAPH, PROV = pipeline.ROOT, pipeline.GRAPH, pipeline.PROV
RUN = PROV / '.runtime' / 'current_refresh_20261114'
pipeline.RUN = RUN
os.environ['GRAPHIFY_OUT'] = str(RUN)
load, save, sha, now = pipeline.load, pipeline.save, pipeline.sha, pipeline.now

ADDED_DOCUMENTS = [
    'regions/LME/LME_002/papers/GOA-2007/models/Aydin2007_Gulf_of_Alaska_1990-1994/model_notes.md',
    'regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49/model_notes.md',
    'regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance/model_notes.md',
    'regions/LME/LME_026/papers/MED-2022/models/Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114/model_notes.md',
]
ADDED_CODE = [
    'tools/project_core/registry/review_candidates.py',
    'tools/scientific_code/PPREstimation/tests/test_final_accounting.py',
    'tools/scientific_code/PPREstimation/tests/test_loader_source_fidelity.py',
    'tools/scientific_code/PPREstimation/tests/test_source_accounting.py',
]


def bounded_detection(scope):
    """Run installed detection on a proven exhaustive deny-by-default tree.

    The allowlist consists solely of root/child exclusion, required ancestor
    directory reinclusion, and the exact file paths. Excluded siblings cannot
    become sources. Supplying that explicit tree removes expensive enumeration
    and repeated ignore matching for unrelated work/raw/dependency entries.
    The installed noise, ancestor-ignore, sensitivity, file type and word-count
    logic still runs unchanged for every permitted source.
    """
    dirs = {parent.as_posix() for source in scope for parent in Path(source).parents if parent != Path('.')}
    expected = ['# Canonical curated graph corpus; see tools/knowledge_graph/provenance/corpus.json', '/*']
    for directory in sorted(dirs, key=lambda value: (value.count('/'), value)):
        expected += ['!/' + directory + '/', '/' + directory + '/*']
    expected += ['!/' + source for source in sorted(scope)]
    assert (ROOT / '.graphifyignore').read_text('utf8').splitlines() == expected
    assert not (ROOT / 'graphify-out').exists(), 'Unexpected second/default graph directory'
    tree = collections.defaultdict(lambda: {'dirs': set(), 'files': set()})
    for source in sorted(scope):
        path = ROOT / source
        assert path.is_file() and not path.is_symlink()
        tree[path.parent]['files'].add(path.name)
        current = path.parent
        while current != ROOT:
            assert current.is_dir() and not current.is_symlink()
            tree[current.parent]['dirs'].add(current.name)
            current = current.parent
    def descend(directory):
        names = sorted(tree[directory]['dirs'])
        yield str(directory), names, sorted(tree[directory]['files'])
        # Honor the installed detector's in-place directory pruning.
        for name in names:
            yield from descend(directory / name)
    def explicit_walk(directory, **kwargs):
        assert Path(directory).resolve() == ROOT and kwargs.get('followlinks') is False
        yield from descend(ROOT)
    from graphify.detect import detect
    with patch('graphify.detect.os.walk', explicit_walk):
        result = detect(ROOT, follow_symlinks=False, google_workspace=False)
    actual = {Path(path).relative_to(ROOT).as_posix() for values in result['files'].values() for path in values}
    assert actual == scope, {'missing': sorted(scope - actual), 'unexpected': sorted(actual - scope)}
    result['traversal'] = 'Exact allowlisted source/ancestor tree; installed ignore, noise, sensitive, classification and word-count gates unchanged.'
    result['exhaustiveness_proof'] = 'Allowlist bytes exactly equal generated root/child deny rules, necessary directory inclusions and437 exact file inclusions; no general source inclusion exists.'
    return result


def finish_preparation():
    corpus = pipeline.assert_sources()
    assert (corpus['total_files'], len(corpus['files']['code']), len(corpus['files']['document'])) == (437, 243, 194)
    scope = set(corpus['sha256'])
    dispositions = load(PROV / 'refresh_dispositions.json')
    chunks = dispositions['semantic_chunks']
    reused = load(RUN / 'reused_semantic.json')
    detected = bounded_detection(scope)
    save(RUN / 'detect.json', detected)
    save(RUN / 'preparation.json', {
        'checked_at': now(), 'sources': len(scope), 'code': len(corpus['files']['code']),
        'documents': len(corpus['files']['document']), 'total_words': corpus['total_words'],
        'semantic_fresh_words': sum(len((ROOT / p).read_text('utf8').split()) for p in sum(chunks, [])),
        'chunk_sizes': list(map(len, chunks)),
        'chunk_words': [sum(len((ROOT / p).read_text('utf8').split()) for p in chunk) for chunk in chunks],
        'reused_documents': dispositions['semantic_reuse_count'], 'reused_nodes': len(reused['nodes']),
        'reused_edge_records': len(reused['edges']), 'reused_hyperedges': len(reused['hyperedges']),
        'endpoint_ids_to_reverify': len(dispositions['pending_endpoint_references']),
        'installed_detector_exact_scope': True, 'bounded_traversal_exhaustiveness_proven': True,
        'source_mutations': False, 'before_graph_sha256': sha(RUN / 'before' / 'graph.json'),
        'source_manifest_sha256': sha(PROV / 'corpus.json'),
    })
    pipeline.prompts()
    print(json.dumps(load(RUN / 'preparation.json'), indent=2))


def prepare():
    assert not RUN.exists(), 'This preparation is single-use; inspect existing evidence before resuming'
    corpus = load(PROV / 'corpus.json')
    old_hashes = load(PROV / 'source_hashes.json')
    old = load(GRAPH / 'graph.json')
    assert len(old_hashes) == corpus['total_files'] == 429
    assert set(old_hashes) == {p for values in corpus['files'].values() for p in values}
    assert set(ADDED_DOCUMENTS + ADDED_CODE).isdisjoint(old_hashes)
    assert len(ADDED_DOCUMENTS + ADDED_CODE) == 8
    allowlist = {line[2:] for line in (ROOT / '.graphifyignore').read_text('utf8').splitlines()
                 if line.startswith('!/') and not line.endswith('/')}
    assert allowlist == set(old_hashes), 'Prior allowlist differs from its recorded corpus'
    files = {'code': sorted(corpus['files']['code'] + ADDED_CODE),
             'document': sorted(corpus['files']['document'] + ADDED_DOCUMENTS)}
    scope = set(files['code'] + files['document'])
    assert (len(scope), len(files['code']), len(files['document'])) == (437, 243, 194)
    assert all((ROOT / p).is_file() and not (ROOT / p).is_symlink() for p in scope)
    hashes = {p: sha(ROOT / p) for p in sorted(scope)}
    changed = sorted(p for p in old_hashes if old_hashes[p] != hashes[p])
    same_docs = {p for p in files['document'] if old_hashes.get(p) == hashes[p]}
    nodes_by = collections.defaultdict(list)
    for node in old['nodes']:
        if node.get('_origin') != 'ast':
            nodes_by[node.get('source_file')].append(node)
    accepted = set()
    rejected = {}
    for source in same_docs:
        expected = pipeline.stem(source)
        nodes = nodes_by[source]
        valid = nodes and all(
            (n['id'] == expected or n['id'].startswith(expected + '_'))
            and not re.search(r'_rationale_\d+$', n['id'])
            and n.get('source_sha256') == hashes[source]
            and all(e.get('source_file') in hashes
                    and e.get('source_sha256') == hashes[e['source_file']]
                    for e in n.get('source_evidence', [])) for n in nodes)
        if valid:
            accepted.add(source)
        else:
            rejected[source] = 'No complete source-current deterministic semantic fragment'
    assert len(accepted) == 168 and not rejected, (len(accepted), rejected)
    reused_nodes = []
    for source in sorted(accepted):
        for original in nodes_by[source]:
            node = copy.deepcopy(original)
            node.pop('community', None)
            node.pop('norm_label', None)
            reused_nodes.append(node)
    reused_edges = [copy.deepcopy(e) for link in old['links']
                    for e in link.get('evidence', [link]) if e.get('source_file') in accepted]
    reused_hypers = [copy.deepcopy(h) for h in old.get('hyperedges', [])
                     if h.get('source_file') in accepted]
    reused_ids = {n['id'] for n in reused_nodes}
    pending = ({end for edge in reused_edges for end in [edge['source'], edge['target']]}
               | {end for hyper in reused_hypers for end in hyper['nodes']}) - reused_ids
    endpoints = [copy.deepcopy(n) for n in old['nodes'] if n['id'] in pending]
    assert {n['id'] for n in endpoints} == pending
    fresh = set(files['document']) - accepted
    assert len(fresh) == 26
    first = sorted(p for p in fresh if p in ADDED_DOCUMENTS or
                   (p.startswith('explainers/') and p not in
                    {'explainers/agents/project_contract.md', 'explainers/workflow.md'}))
    chunks = [first, sorted(fresh - set(first))]
    assert set(chunks[0]).isdisjoint(chunks[1]) and set(sum(chunks, [])) == fresh
    RUN.mkdir(parents=True)
    for relative in ['graph.json', 'graph.html', 'provenance/corpus.json',
                     'provenance/source_hashes.json', 'provenance/community_labels.json']:
        source = GRAPH / relative
        target = RUN / 'before' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    shutil.copyfile(ROOT / '.graphifyignore', RUN / 'before' / 'graphifyignore')
    save(RUN / 'reused_semantic.json', {'nodes': reused_nodes, 'edges': reused_edges,
         'hyperedges': reused_hypers, 'input_tokens': None, 'output_tokens': None})
    for i, chunk in enumerate(chunks, 1):
        required = [n for n in endpoints if n['source_file'] in chunk]
        save(RUN / f'endpoint_requirements_{i:02d}.json', {
            'instruction': 'These existing concept IDs are referenced by independently attributed unchanged-source relationships. Re-read the current source and retain the same ID and concept identity when supported; update source locations and attributes. If the concept is genuinely removed or changed, return an explicit per-ID disposition; do not invent support or silently discard the referencing evidence.',
            'nodes_to_reverify': required})
    assert all(n['source_file'] in fresh for n in endpoints)
    words = sum(len((ROOT / p).read_text('utf8', errors='replace').split()) for p in scope)
    corpus.update(status='final_sources_confirmed', files=files, sha256=hashes,
                  total_files=437, total_words=words,
                  semantic_refresh_state='26 changed/new documents pending fresh extraction; 168 unchanged documents eligible for full-byte verified reuse.',
                  policy='Exactly the prior 429-file curated corpus plus four current canonical model notes and four current shared implementation/test sources authorized by the coordinator. Work/QA copies, binaries, graph self-content and raw inputs remain excluded.')
    save(PROV / 'corpus.json', corpus)
    dispositions = {
        'checked_at': now(), 'prior_files': 429, 'current_files': 437,
        'added_source_paths': ADDED_DOCUMENTS + ADDED_CODE,
        'changed_source_paths': changed, 'removed_source_paths': [],
        'decisions': [{'original_path': p, 'retained_path': p,
                       'old_sha256': old_hashes.get(p), 'actual_sha256': hashes[p],
                       'disposition': 'new_current_source' if p not in old_hashes else
                                      'eligible_exact_reuse' if old_hashes[p] == hashes[p] else
                                      'changed_requires_reextraction'} for p in sorted(scope)],
        'reuse_accepted': sorted(accepted), 'reuse_rejected': rejected,
        'semantic_reuse_count': len(accepted), 'semantic_changed_or_new': len(fresh),
        'semantic_chunks': chunks, 'unchanged_source_edge_records': len(reused_edges),
        'unchanged_source_hyperedges': len(reused_hypers),
        'pending_endpoint_references': endpoints,
        'pending_endpoint_policy': 'Every eligible unchanged-source relationship is retained; changed-source referenced concepts receive explicit fresh verification before merging.',
        'no_scientific_calculations': True,
    }
    save(PROV / 'refresh_dispositions.json', dispositions)
    dirs = {parent.as_posix() for path in scope for parent in Path(path).parents if parent != Path('.')}
    lines = ['# Canonical curated graph corpus; see tools/knowledge_graph/provenance/corpus.json', '/*']
    for directory in sorted(dirs, key=lambda value: (value.count('/'), value)):
        lines += ['!/' + directory + '/', '/' + directory + '/*']
    lines += ['!/' + p for p in sorted(scope)]
    (ROOT / '.graphifyignore').write_text('\n'.join(lines) + '\n', encoding='utf8')
    finish_preparation()


def label():
    """Reuse stable community names and expose every changed grouping for review."""
    old = load(RUN / 'before' / 'graph.json')['communities']
    analysis = load(RUN / 'analysis.json')
    labels, records = {}, []
    for cid, members in analysis['communities'].items():
        current = set(members)
        candidates = []
        for old_id, community in old.items():
            before = set(community['members'])
            overlap = len(current & before)
            if overlap:
                candidates.append((overlap / len(current), overlap / len(current | before), old_id, community))
        if candidates:
            share, jaccard, old_id, best = max(candidates, key=lambda item: (item[0], item[1]))
            proposed = best['label']
        else:
            share, jaccard, old_id, proposed = 0, 0, None, None
        needs_review = share < .7 or jaccard < .25
        labels[cid] = proposed
        records.append({'community': cid, 'label': proposed, 'prior_community': old_id,
                        'member_overlap_share': share, 'jaccard': jaccard,
                        'needs_manual_review': needs_review,
                        'top_labels': analysis['top_labels'][cid], 'members': members})
    save(PROV / 'community_labels.json', labels)
    save(RUN / 'community_label_review.json', records)
    print(json.dumps([dict(community=item['community'], label=item['label'],
                           share=round(item['member_overlap_share'], 3),
                           jaccard=round(item['jaccard'], 3),
                           top_labels=item['top_labels'][:8])
                      for item in records if item['needs_manual_review']], indent=2))


def current_probes():
    """Current exact-concept CLI traversals, including newly indexed sources."""
    pipeline.assert_sources()
    graph = load(GRAPH / 'graph.json')
    nodes = {node['id']: node for node in graph['nodes']}
    degrees = collections.Counter(endpoint for edge in graph['links']
                                  for endpoint in [edge['source'], edge['target']])
    queries = [
        ('structure', 'explainers_structure_regional_paper_and_candidate_layout'),
        ('shared_mapping', 'agents_project_contract_one_shared_mapping_decision_stage'),
        ('signed_review', 'references_researcher_signoff_and_map_researcher_signed_review_registration_and_bounded_map_refresh'),
        ('review_candidate', 'registry_review_candidates_add_review_candidate'),
    ]
    for name, source in [('pooled_mediterranean', ADDED_DOCUMENTS[-1]),
                         ('alaska_native_balance', ADDED_DOCUMENTS[2])]:
        candidates = [node for node in graph['nodes'] if node['source_file'] == source]
        assert candidates, source
        chosen = max(candidates, key=lambda node: degrees[node['id']])
        queries.append((name, chosen['id']))
    cli = Path.home() / 'miniconda3/Scripts/graphify.exe'
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    def probe(item):
        name, identity = item
        assert identity in nodes, identity
        # Current two-hop integration neighborhoods contain up to80 nodes;
        # reserve space for both their cited nodes and their relationships.
        budget = '6000'
        args = [str(cli), 'query', identity, '--graph', 'tools/knowledge_graph/graph.json', '--budget', budget]
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf8', env=env, timeout=90)
        node = nodes[identity]
        target = PROV / f'probe_20261114_{name}.txt'
        target.write_text(result.stdout, encoding='utf8')
        return {'name': name, 'question': identity, 'command': ['graphify'] + args[1:],
                'exit_code': result.returncode, 'output_file': target.name,
                'output_sha256': sha(target), 'expected_label': node['label'],
                'expected_source': node['source_file'],
                'exact_current_source_node_observed': ('NODE ' + node['label'] + ' [src=' + node['source_file']) in result.stdout,
                'related_edges_observed': 'EDGE ' in result.stdout,
                'stderr': result.stderr}
    with ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(probe, queries))
    passed = all(row['exit_code'] == 0 and row['exact_current_source_node_observed']
                 and row['related_edges_observed'] for row in records)
    save(PROV / 'retrieval_verification.json', {
        'checked_at': now(), 'pass': passed, 'graph_sha256': sha(GRAPH / 'graph.json'),
        'probes': records, 'status': 'Six actual exact-concept CLI traversals returned the current cited node and related edges; current source/endpoint integrity is verified separately.',
        'initial_limitations': [{'probes': ['signed_review', 'review_candidate'], 'budget': 1800,
                                'observation': 'Current source node was present but high-connectivity traversals returned no edges within this budget. The first suite stopped at the signed-review check; the second exposed the analogous candidate-check limit.',
                                'resolution': 'Measured traversals contain71 and80 nodes. All probes now reserve6000 tokens for nodes plus edges and collect every result before assessing the suite. No graph evidence or retrieval gate was changed.'}],
        'limitation': 'Exact concept retrieval is checked; broad natural-language ranking quality is not certified. The graph does not establish scientific readiness or researcher approval.'})
    print(json.dumps(records, indent=2))
    assert passed, 'Inspect every saved current probe result; at least one source/relationship check failed'


def finish():
    corpus = pipeline.assert_sources()
    graph = load(GRAPH / 'graph.json')
    proof = load(PROV / 'completion_verification.json')
    static = load(PROV / 'html_static_verification.json')
    delta = load(PROV / 'html_delta_verification.json')
    retrieval = load(PROV / 'retrieval_verification.json')
    assert proof['integrity_pass'] and static['pass'] and delta['pass'] and retrieval['pass']
    assert sha(GRAPH / 'graph.json') == proof['graph_sha256'] == delta['current_graph_sha256'] == retrieval['graph_sha256']
    assert sha(GRAPH / 'graph.html') == proof['html_sha256'] == delta['current_html_sha256'] == static['html_sha256']
    reused = load(RUN / 'reused_semantic.json')
    final_edges = [edge for link in graph['links'] for edge in link['evidence']]
    def signature(item):
        return json.dumps(item, sort_keys=True, ensure_ascii=False)
    edge_counts = collections.Counter(map(signature, final_edges))
    hyper_counts = collections.Counter(map(signature, graph.get('hyperedges', [])))
    assert not (collections.Counter(map(signature, reused['edges'])) - edge_counts), 'Unchanged-source edge evidence lost or altered'
    assert not (collections.Counter(map(signature, reused['hyperedges'])) - hyper_counts), 'Unchanged-source hyperedge evidence lost or altered'
    assert len({h['id'] for h in graph.get('hyperedges', [])}) == len(graph.get('hyperedges', [])), 'Duplicate hyperedge identity'
    ids = {node['id'] for node in graph['nodes']}
    pending = load(PROV / 'refresh_dispositions.json')['pending_endpoint_references']
    assert {node['id'] for node in pending} <= ids
    labels = load(PROV / 'community_labels.json')
    label_records = load(RUN / 'community_label_review.json')
    assert all(not row['needs_manual_review'] or row.get('reviewed') for row in label_records), 'Community labels still await topical review'
    save(PROV / 'community_label_delta.json', {
        'checked_at': now(), 'mapping': 'Prior names reused by measured member overlap; all low-overlap/new communities manually reviewed against their actual members and source labels.',
        'records': [{k: value for k, value in row.items() if k != 'members'} for row in label_records],
        'all_required_reviews_complete': True})
    save(PROV / 'community_label_members.json', {
        'checked_at': now(), 'communities': {cid: {'label': labels[cid], 'members': value['members']}
                                              for cid, value in graph['communities'].items()}})
    validation = load(PROV / 'semantic_validation.json')
    save(PROV / 'extraction_attestations.json', {
        'checked_at': now(), 'prompt_source': '~/.agents/skills/graphify/references/extraction-spec.md',
        'prompt_sha256': sha(Path.home() / '.agents/skills/graphify/references/extraction-spec.md'),
        'semantic_agents': ['semantic_guides', 'semantic_workflows'],
        'chunks': validation['chunks'], 'fresh_documents_fully_read': 26,
        'unchanged_document_full_byte_reuse': 168, 'retained_endpoint_ids_reverified': 60,
        'source_mutations_by_graph_agents': 0, 'scientific_engine_executions': 0,
        'input_tokens': None, 'output_tokens': None,
        'usage_status': 'Host collaboration tools do not expose actual token usage.'})
    corpus['semantic_refresh_state'] = '26 changed/new documents fully re-read and extracted;168 unchanged documents reused after full SHA256/identity checks;243 current code sources parsed deterministically; all60 retained cross-source concept endpoints reverified.'
    save(PROV / 'corpus.json', corpus)
    method = load(PROV / 'extraction_method.json')
    method.update(completed_at=now(), semantic_sources=194, code_sources=243,
                  reused_semantic_sources=168, freshly_extracted_semantic_sources=26,
                  preserved_unchanged_edge_records=len(reused['edges']),
                  preserved_unchanged_hyperedges=len(reused['hyperedges']))
    save(PROV / 'extraction_method.json', method)
    from graphify.benchmark import run_benchmark, print_benchmark
    benchmark = run_benchmark(str(GRAPH / 'graph.json'), corpus_words=corpus['total_words'],
                              questions=['One-command regional refresh', 'EE floor', 'Researcher disqualification'])
    assert 'error' not in benchmark, benchmark
    benchmark.update(measurement_status='Installed heuristic for corpus/query context size; not measured extraction tokens, elapsed runtime or monetary cost.',
                     checked_at=now(), graph_sha256=sha(GRAPH / 'graph.json'))
    save(PROV / 'benchmark.json', benchmark)
    print_benchmark(benchmark)
    import checks
    checks.RUN = RUN
    checks.usage()
    proof.update(pass_=True, completed_at=now(), communities=len(graph['communities']),
                 retained_semantic_edge_records_exact=len(reused['edges']),
                 retained_semantic_hyperedges_exact=len(reused['hyperedges']),
                 retained_endpoint_ids_reverified=60,
                 retrieval_probes='PASS: six current exact-concept CLI traversals with source citations and related edges.',
                 html_interaction='Current JavaScript syntax and full payload checked; exact prior-tested template preserved. No fresh visible browser interaction was performed or claimed.',
                 html_delta_verification_file='html_delta_verification.json',
                 retrieval_verification_file='retrieval_verification.json',
                 detector_scope_verification_file='detector_scope_verification.json',
                 current_refresh_controller='refresh_20261114.py')
    proof['pass'] = proof.pop('pass_')
    save(PROV / 'completion_verification.json', proof)
    receipt = {'completed_at': now(), 'pass': True, 'files': 437, 'code': 243, 'documents': 194,
               'nodes': len(graph['nodes']), 'topology_pairs': len(graph['links']),
               'independent_edge_records': len(final_edges), 'hyperedges': len(graph.get('hyperedges', [])),
               'communities': len(graph['communities']), 'reused_documents': 168, 'fresh_documents': 26,
               'all_sources_current_sha256': True, 'unchanged_semantic_evidence_exact': True,
               'retained_endpoints_reverified': 60, 'scientific_execution': False,
               'current_visible_browser_check': False,
               'files_sha256': {name: sha(GRAPH / name) for name in ['graph.json', 'graph.html', 'GRAPH_REPORT.md', 'REFRESH_SCOPE.md', 'provenance/source_hashes.json', 'provenance/corpus.json', 'provenance/completion_verification.json']},
               'runtime_location': 'provenance/.runtime/current_refresh_20261114 (ignored local cache)',
               'scope_limit': 'Architecture/evidence index of the explicit curated sources. Binary published reviews and workbook/results are not freshly extracted and this graph grants no scientific or researcher approval.'}
    save(PROV / 'current_refresh_verification.json', receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'finish_preparation', 'ast', 'collect', 'merge', 'label', 'export', 'verify', 'syntax', 'browser_delta', 'current_probes', 'finish', 'usage'])
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare()
    elif args.action == 'finish_preparation':
        finish_preparation()
    elif args.action == 'label':
        label()
    elif args.action == 'current_probes':
        current_probes()
    elif args.action == 'finish':
        finish()
    elif hasattr(pipeline, args.action):
        getattr(pipeline, args.action)()
    else:
        import checks
        checks.RUN = RUN
        getattr(checks, args.action)()
