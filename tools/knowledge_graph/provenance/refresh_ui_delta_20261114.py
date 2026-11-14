"""Code-only graph delta for the frozen November14 model preference fixes.

No directory traversal, semantic extraction, scientific execution or map writes.
The five additions preserve the graph's existing implementation/check roles.
"""
import argparse
import collections
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline
import refresh_20261114 as prior

ROOT, GRAPH, PROV = pipeline.ROOT, pipeline.GRAPH, pipeline.PROV
RUN = PROV / '.runtime' / 'ui_preferences_delta_20261114'
CACHE = PROV / '.runtime' / 'current_refresh_20261114'
pipeline.RUN = prior.RUN = RUN
os.environ['GRAPHIFY_OUT'] = str(CACHE)
load, save, sha, now = pipeline.load, pipeline.save, pipeline.sha, pipeline.now

ADDED = [
    'tools/project_core/maps/model_preferences.js',
    'tools/project_core/maps/model_preferences_layout.py',
    'tools/workflow_checks/maps/check_model_preferences.js',
    'tools/workflow_checks/maps/test_model_preferences.py',
    'tools/workflow_checks/maps/check_trend_validated_set.js',
]
CHANGED = [
    'tools/project_core/maps/build_html.py',
    'tools/project_core/maps/trend_extras.js',
    'tools/project_core/maps/trend_extras_layout.py',
    'tools/workflow_checks/maps/test_trend_extras.py',
]


def allowlist_lines(scope):
    dirs = {parent.as_posix() for source in scope for parent in Path(source).parents if parent != Path('.')}
    lines = ['# Canonical curated graph corpus; see tools/knowledge_graph/provenance/corpus.json', '/*']
    for directory in sorted(dirs, key=lambda name: (name.count('/'), name)):
        lines += ['!/' + directory + '/', '/' + directory + '/*']
    return lines + ['!/' + source for source in sorted(scope)]


def reconcile_unchanged_ast():
    """Retain prior independently attributed evidence for unchanged code."""
    corpus = pipeline.assert_sources()
    before = load(RUN / 'before/graph.json')
    current = load(RUN / 'extraction.json')
    old_nodes = {node['id']: node for node in before['nodes']}
    current_ids = {node['id'] for node in current['nodes']}
    signature = lambda edge: json.dumps(edge, sort_keys=True, ensure_ascii=False)
    current_records = {signature(edge) for edge in current['edges']}
    restore = []
    for link in before['links']:
        for edge in link['evidence']:
            if edge.get('_origin') != 'ast' or signature(edge) in current_records:
                continue
            if edge.get('source_sha256') != corpus['sha256'][edge['source_file']]:
                continue  # The four expressly changed sources were re-extracted.
            for endpoint in [edge['source'], edge['target']]:
                assert endpoint in current_ids, 'Unchanged structural evidence needs explicit endpoint reconciliation'
                for citation in [old_nodes[endpoint]] + old_nodes[endpoint].get('source_evidence', []):
                    assert citation['source_sha256'] == corpus['sha256'][citation['source_file']], 'Changed endpoint needs explicit structural evidence reconciliation'
            restore.append(edge)
    if restore:
        ast = load(RUN / 'ast.json')
        ast['edges'].extend(restore)
        save(RUN / 'ast.json', ast)
        pipeline.merge()
        current_records = {signature(edge) for edge in load(RUN / 'extraction.json')['edges']}
        assert all(signature(edge) in current_records for edge in restore), 'Authenticated structural evidence was not preserved'
    save(PROV / 'ast_cache_preservation.json', {
        'checked_at': now(), 'pass': True, 'retained_records': len(restore), 'records': restore,
        'method': 'The installed cache-backed cross-file pass did not re-emit these prior records. Each cited source and every endpoint source remains full-byte identical, all endpoint IDs still exist, and exact original evidence is retained beside newly extracted code evidence.',
        'scientific_execution': False})
    proof = load(PROV / 'ast_validation.json')
    proof['unchanged_structural_evidence_restored_exact'] = len(restore)
    proof['preservation_evidence'] = 'ast_cache_preservation.json'
    save(PROV / 'ast_validation.json', proof)
    print('Preserved unchanged AST evidence records:', len(restore), flush=True)


def apply():
    assert not RUN.exists(), 'Single-use delta preparation; inspect existing run before resuming'
    corpus = load(PROV / 'corpus.json')
    old_hashes = load(PROV / 'source_hashes.json')
    old = load(GRAPH / 'graph.json')
    assert corpus['total_files'] == len(old_hashes) == 437
    assert corpus['sha256'] == old_hashes
    assert old['freshness']['source_manifest_sha256'] == sha(PROV / 'source_hashes.json')
    assert (ROOT / '.graphifyignore').read_text('utf8').splitlines() == allowlist_lines(old_hashes)
    assert set(ADDED).isdisjoint(old_hashes) and set(CHANGED) <= set(old_hashes)
    scope = set(old_hashes) | set(ADDED)
    assert len(scope) == 442
    hashes = {source: sha(ROOT / source) for source in sorted(scope)}
    changed = {source for source in old_hashes if hashes[source] != old_hashes[source]}
    assert changed == set(CHANGED), {'unexpected_changes': sorted(changed - set(CHANGED)), 'unchanged_expected': sorted(set(CHANGED) - changed)}
    docs = set(corpus['files']['document'])
    assert len(docs) == 194 and all(hashes[source] == old_hashes[source] for source in docs)
    code = sorted(set(corpus['files']['code']) | set(ADDED))
    assert len(code) == 248
    nodes = [copy.deepcopy(node) for node in old['nodes'] if node.get('source_file') in docs and node.get('_origin') == 'semantic']
    for node in nodes:
        node.pop('community', None)
        node.pop('norm_label', None)
    edges = [copy.deepcopy(edge) for link in old['links'] for edge in link['evidence'] if edge.get('source_file') in docs]
    hypers = [copy.deepcopy(hyper) for hyper in old['hyperedges'] if hyper.get('source_file') in docs]
    assert (len(nodes), len(edges), len(hypers)) == (1167, 1717, 25)
    ids = {node['id'] for node in nodes}
    assert all(edge['source'] in ids and edge['target'] in ids for edge in edges)
    assert all(set(hyper['nodes']) <= ids for hyper in hypers)
    for item in nodes + edges + hypers:
        for citation in [item] + item.get('source_evidence', []):
            assert citation['source_sha256'] == hashes[citation['source_file']]
    RUN.mkdir(parents=True)
    for name in ['graph.json', 'graph.html', 'provenance/corpus.json', 'provenance/source_hashes.json',
                 'provenance/refresh_dispositions.json', 'provenance/retrieval_verification.json']:
        target = RUN / 'before' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(GRAPH / name, target)
    shutil.copyfile(ROOT / '.graphifyignore', RUN / 'before' / 'graphifyignore')
    semantic = {'nodes': nodes, 'edges': edges, 'hyperedges': hypers, 'input_tokens': None, 'output_tokens': None}
    save(RUN / 'reused_semantic.json', semantic)
    save(RUN / 'semantic.json', semantic)
    corpus.update(files={'code': code, 'document': sorted(docs)}, sha256=hashes,
                  total_files=442, total_words=sum(len((ROOT / source).read_text('utf8', errors='replace').split()) for source in scope),
                  status='final_sources_confirmed',
                  semantic_refresh_state='All194 documents reused by exact full-byte hash; code-only delta pending deterministic extraction.',
                  policy='Prior437-file curated corpus plus exactly five frozen map-preference helpers/regression checks. No work/raw/binary or generated-map expansion.')
    save(PROV / 'corpus.json', corpus)
    (ROOT / '.graphifyignore').write_text('\n'.join(allowlist_lines(scope)) + '\n', encoding='utf8')
    assert (ROOT / '.graphifyignore').read_text('utf8').splitlines() == allowlist_lines(scope)
    from graphify.detect import classify_file, _is_sensitive, _is_noise_dir
    classified = collections.defaultdict(list)
    for source in sorted(scope):
        path = ROOT / source
        assert path.is_file() and path.resolve().is_relative_to(ROOT) and not path.is_symlink()
        assert not _is_sensitive(path)
        assert all(not _is_noise_dir(parent.name, parent.parent) for parent in path.parents if parent.is_relative_to(ROOT) and parent != ROOT)
        classified[classify_file(path).value].append(str(path))
    assert set(classified) == {'code', 'document'}
    assert {Path(path).relative_to(ROOT).as_posix() for path in classified['code']} == set(code)
    assert {Path(path).relative_to(ROOT).as_posix() for path in classified['document']} == docs
    save(RUN / 'detect.json', {'files': dict(classified), 'total_files': 442,
         'total_words': corpus['total_words'], 'scan_root': str(ROOT), 'skipped_sensitive': [],
         'needs_graph': True, 'warning': None,
         'method': 'Installed classifier/sensitive/noise checks on explicit442 full-hashed paths; exact deny-by-default allowlist structure proves exhaustive membership. No filesystem traversal or repeated ordered-pattern scan.'})
    save(PROV / 'refresh_dispositions.json', {'checked_at': now(), 'prior_files': 437, 'current_files': 442,
         'added_source_paths': ADDED, 'changed_source_paths': CHANGED, 'removed_source_paths': [],
         'semantic_reuse_count': 194, 'semantic_changed_or_new': 0, 'semantic_chunks': [],
         'unchanged_source_edge_records': 1717, 'unchanged_source_hyperedges': 25,
         'pending_endpoint_references': [], 'endpoint_reconciliation_status': 'No semantic endpoints depend on changed code; all retained semantic endpoints already present.',
         'policy': 'Exactly the frozen five-new/four-changed code delta. No semantic extraction or scientific work.'})
    save(PROV / 'semantic_validation.json', {'checked_at': now(), 'pass': True, 'chunks': [],
         'reuse': {'full_hash_checked': True, 'sources': 194, 'nodes': 1167,
                   'independent_edge_records': 1717, 'hyperedges': 25}, 'semantic_agents_run': 0})
    # Keep the immediately previous cache; a new runtime output directory must
    # not accidentally turn an affected-code update into a cold AST extraction.
    from graphify import cache
    from graphify.extract import extract, _JS_CACHE_BYPASS_SUFFIXES
    cache._GRAPHIFY_OUT = str(CACHE)
    cache._ensure_stat_index(ROOT)
    cache._stat_index.clear()  # Full content hashing rather than stat-only reuse.
    reusable = [source for source in code if Path(source).suffix not in _JS_CACHE_BYPASS_SUFFIXES
                and cache.load_cached(Path(source), ROOT) is not None]
    result = extract([Path(source) for source in code], cache_root=ROOT, parallel=True, max_workers=2)
    result['extraction_method'] = 'installed_graphify_ast_with_previous_cache_and_current_global_symbol_resolution'
    save(RUN / 'ast.json', result)
    covered = {pipeline.relative(node.get('source_file')) for node in result['nodes'] if node.get('source_file')}
    assert set(code) <= covered
    save(PROV / 'ast_validation.json', {'checked_at': now(), 'code_files': 248,
         'code_sha256': {source: hashes[source] for source in code}, 'cached_sources': len(reusable),
         'parsed_sources': 248 - len(reusable), 'js_cache_bypass_sources': sum(Path(source).suffix in _JS_CACHE_BYPASS_SUFFIXES for source in code),
         'all_code_sources_have_nodes': True, 'raw_nodes': len(result['nodes']), 'raw_edges': len(result['edges']),
         'method': 'Installed per-file AST cache plus current corpus symbol resolution. JS always reparsed by installed extractor; unchanged Python reused only after full content/path hashing.',
         'input_tokens': 0, 'output_tokens': 0, 'scientific_execution': False})
    save(PROV / 'extraction_method.json', {'started_at': now(), 'method': 'installed_ast_cache_and_exact_semantic_reuse',
         'code_sources': 248, 'semantic_sources': 194, 'reused_semantic_sources': 194,
         'freshly_extracted_semantic_sources': 0, 'semantic_agents_run': 0,
         'input_tokens': None, 'output_tokens': None, 'usage_status': 'No new semantic extraction. Overall host-agent token/cost telemetry unavailable.'})
    save(PROV / 'detector_scope_verification.json', {'checked_at': now(), 'pass': True,
         'source_files': 442, 'code_files': 248, 'document_files': 194,
         'no_directory_traversal': True, 'installed_classification_sensitive_noise_checks': True,
         'exact_allowlist_structure': True, 'current_full_source_hashes': True,
         'policy': 'Exact prior437 paths plus the five authorized code paths; only four existing source hashes changed. Root/child deny rules and exact filename inclusions mathematically exclude all other files.'})
    pipeline.merge()
    reconcile_unchanged_ast()
    prior.label()
    print(json.dumps({'prepared': True, 'cached_code_sources': len(reusable), 'parsed_code_sources': 248 - len(reusable),
                      'semantic_sources_reused': 194, 'next': 'Review changed community names, then finish'}, indent=2))


def finish():
    corpus = pipeline.assert_sources()
    review = load(RUN / 'community_label_review.json')
    assert all(not row['needs_manual_review'] or row.get('reviewed') for row in review)
    # Windows rejected the library's direct truncating open once while the
    # original graph bytes remained exact. Export through same-directory owned
    # temporary files, checking the original fingerprint before each replace.
    import graphify.export as exporter
    original_json, original_html, original_save = exporter.to_json, exporter.to_html, pipeline.save
    writes = []
    def atomic_target(target, producer):
        target = Path(target).resolve()
        assert target.parent == GRAPH and target.name in {'graph.json', 'graph.html'}
        previous = sha(target) if target.is_file() else None
        temporary = target.with_name('.' + target.name + '.ui_delta_' + uuid.uuid4().hex + '.tmp')
        try:
            value = producer(temporary)
            assert temporary.is_file() and temporary.stat().st_size > 0
            wanted = sha(temporary)
            assert (sha(target) if target.is_file() else None) == previous, 'Graph target changed during export'
            os.replace(temporary, target)
            assert sha(target) == wanted, 'Graph replacement bytes differ'
            writes.append({'path': target.name, 'before_sha256': previous, 'after_sha256': wanted,
                           'same_directory_atomic_replace': True, 'verified': True})
            return value
        finally:
            if temporary.exists():
                temporary.unlink()  # Only this exact task-created temporary file.
    def json_export(graph, communities, output, **kwargs):
        return atomic_target(output, lambda path: original_json(graph, communities, str(path), **kwargs))
    def html_export(graph, communities, output, **kwargs):
        def produce(path):
            result = original_html(graph, communities, str(path), **kwargs)
            html = path.read_text('utf8')
            title = re.search(r'<title>.*?</title>', (RUN / 'before/graph.html').read_text('utf8')).group(0)
            html, count = re.subn(r'<title>.*?</title>', lambda _: title, html, count=1)
            assert count == 1
            path.write_text(html, encoding='utf8')
            return result
        return atomic_target(output, produce)
    def guarded_save(path, data):
        if Path(path).resolve() == GRAPH / 'graph.json':
            return atomic_target(path, lambda temporary: original_save(temporary, data))
        return original_save(path, data)
    with patch('graphify.export.to_json', json_export), patch('graphify.export.to_html', html_export), patch.object(pipeline, 'save', guarded_save):
        pipeline.export()
    save(PROV / 'atomic_export_verification.json', {'checked_at': now(), 'pass': True,
         'initial_direct_export': {'status': 'failed_before_target_mutation', 'error': 'OSError Errno22 Invalid argument opening graph.json for truncating write',
                                  'target_bytes_verified_equal_to_baseline': True, 'nontruncating_write_handle_probe': 'passed'},
         'writes': writes})
    verify_exports()


def verify_exports():
    corpus = pipeline.assert_sources()
    review = load(RUN / 'community_label_review.json')
    pipeline.verify()
    import checks
    checks.RUN = RUN
    checks.syntax()
    checks.browser_delta()
    graph = load(GRAPH / 'graph.json')
    final_edges = [edge for link in graph['links'] for edge in link['evidence']]
    reused = load(RUN / 'reused_semantic.json')
    signature = lambda value: json.dumps(value, sort_keys=True, ensure_ascii=False)
    assert not (collections.Counter(map(signature, reused['edges'])) - collections.Counter(map(signature, final_edges)))
    assert not (collections.Counter(map(signature, reused['hyperedges'])) - collections.Counter(map(signature, graph['hyperedges'])))
    structural = load(PROV / 'ast_cache_preservation.json')
    assert not (collections.Counter(map(signature, structural['records'])) - collections.Counter(map(signature, final_edges)))
    structural['published_graph_sha256'] = sha(GRAPH / 'graph.json')
    structural['interpretation'] = 'Prior structural inferences remain recorded inferences, not newly verified runtime calls.'
    save(PROV / 'ast_cache_preservation.json', structural)
    nodes = {node['id']: node for node in graph['nodes']}
    identities = ['maps_model_preferences', 'maps_model_preferences_layout', 'maps_check_trend_validated_set',
                  'agents_project_contract_one_shared_mapping_decision_stage']
    cli = Path.home() / 'miniconda3/Scripts/graphify.exe'
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    def probe(identity):
        node = nodes[identity]
        args = [str(cli), 'query', identity, '--graph', 'tools/knowledge_graph/graph.json', '--budget', '6000']
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf8', env=env, timeout=90)
        target = PROV / ('probe_ui_delta_' + identity + '.txt')
        target.write_text(result.stdout, encoding='utf8')
        passed = result.returncode == 0 and ('NODE ' + node['label'] + ' [src=' + node['source_file']) in result.stdout and 'EDGE ' in result.stdout
        return {'query': identity, 'source_file': node['source_file'], 'pass': passed,
                'exit_code': result.returncode, 'output_file': target.name, 'output_sha256': sha(target)}
    with ThreadPoolExecutor(max_workers=2) as executor:
        probes = list(executor.map(probe, identities))
    save(PROV / 'retrieval_verification.json', {'checked_at': now(), 'pass': all(row['pass'] for row in probes),
         'graph_sha256': sha(GRAPH / 'graph.json'), 'probes': probes,
         'scope': 'Three newly indexed UI/check source anchors and one retained contract concept; actual CLI source/relationship retrieval, not broad ranking or scientific validation.'})
    assert all(row['pass'] for row in probes), probes
    labels = load(PROV / 'community_labels.json')
    save(PROV / 'community_label_delta.json', {'checked_at': now(), 'all_required_reviews_complete': True,
         'records': [{key: value for key, value in row.items() if key != 'members'} for row in review],
         'mapping': 'Existing names by actual member overlap; low-overlap/new groups reviewed for this code-only UI delta.'})
    save(PROV / 'community_label_members.json', {'checked_at': now(), 'communities': {
         cid: {'label': labels[cid], 'members': community['members']} for cid, community in graph['communities'].items()}})
    corpus['semantic_refresh_state'] = 'All194 semantic sources and their1717 edge records/25 hyperedges reused exactly after full SHA256 checks. Five new/four changed code files integrated through installed cache-backed AST and current symbol resolution.'
    save(PROV / 'corpus.json', corpus)
    method = load(PROV / 'extraction_method.json'); method['completed_at'] = now(); save(PROV / 'extraction_method.json', method)
    save(PROV / 'extraction_attestations.json', {'checked_at': now(), 'semantic_agents': [],
         'all194_document_sources_full_byte_reused': True, 'semantic_nodes': 1167,
         'unchanged_semantic_edges_exact': 1717, 'unchanged_semantic_hyperedges_exact': 25,
         'scientific_executions': 0, 'source_mutations': 0, 'input_tokens': None, 'output_tokens': None})
    from graphify.benchmark import run_benchmark
    benchmark = run_benchmark(str(GRAPH / 'graph.json'), corpus_words=corpus['total_words'],
                              questions=['One-command regional refresh', 'EE floor', 'Researcher disqualification'])
    benchmark.update(checked_at=now(), graph_sha256=sha(GRAPH / 'graph.json'),
                     measurement_status='Installed context-size heuristic, not measured host tokens or monetary cost.')
    save(PROV / 'benchmark.json', benchmark)
    checks.usage()
    proof = load(PROV / 'completion_verification.json')
    proof.update({'pass': True, 'completed_at': now(), 'communities': len(graph['communities']),
                  'retained_semantic_edge_records_exact': 1717, 'retained_semantic_hyperedges_exact': 25,
                  'retrieval_probes': 'PASS: four actual current CLI traversals including three added UI/check sources.',
                  'html_interaction': 'Current syntax/full payload and exact prior-tested template passed; no fresh visible browser interaction claimed.',
                  'current_refresh_controller': 'refresh_ui_delta_20261114.py'})
    save(PROV / 'completion_verification.json', proof)
    pipeline.assert_sources()
    receipt = {'completed_at': now(), 'pass': True, 'files': 442, 'code': 248, 'documents': 194,
               'nodes': len(graph['nodes']), 'topology_pairs': len(graph['links']), 'independent_edge_records': len(final_edges),
               'hyperedges': len(graph['hyperedges']), 'communities': len(graph['communities']),
               'new_code_paths': ADDED, 'changed_code_paths': CHANGED, 'semantic_sources_reused': 194,
               'cached_code_sources': load(PROV / 'ast_validation.json')['cached_sources'],
               'parsed_code_sources': load(PROV / 'ast_validation.json')['parsed_sources'],
               'retained_unchanged_ast_evidence_records': structural['retained_records'],
               'semantic_evidence_exact': True, 'full_current_source_hashes': True, 'scientific_execution': False,
               'current_visible_browser_check': False, 'no_directory_traversal': True,
               'files_sha256': {name: sha(GRAPH / name) for name in ['graph.json', 'graph.html', 'GRAPH_REPORT.md', 'REFRESH_SCOPE.md', 'provenance/source_hashes.json', 'provenance/corpus.json', 'provenance/completion_verification.json']},
               'runtime_location': 'provenance/.runtime/ui_preferences_delta_20261114 (ignored local cache)'}
    save(PROV / 'ui_graph_delta_verification.json', receipt)
    save(PROV / 'current_refresh_verification.json', receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['apply', 'reconcile', 'finish', 'verify_exports'])
    action = parser.parse_args().action
    if action == 'reconcile':
        reconcile_unchanged_ast()
        prior.label()
    else:
        globals()[action]()
