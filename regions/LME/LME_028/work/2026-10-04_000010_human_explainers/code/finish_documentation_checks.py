"""Bounded current documentation graph checks; never executes science."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[6]
WORK = Path(__file__).resolve().parent.parent
QA = WORK / 'qa'
GRAPH = ROOT / 'tools/knowledge_graph'
PROV = GRAPH / 'provenance'
RUNTIME = PROV / '.runtime'

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text('utf8'))
def save(p, data): p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
def canonical(record): return json.dumps(record, ensure_ascii=False, sort_keys=True)

def probes():
    graph_sha = sha(GRAPH / 'graph.json')
    cli = Path.home() / 'miniconda3/Scripts/graphify.exe'
    questions = [
        ('human_index', 'Guides to the project', 'explainers/README.md'),
        ('human_layout', 'Where to find things', 'explainers/structure.md'),
        ('human_workflow', 'Working with a region', 'explainers/workflow.md'),
        ('human_validation', 'Validation reports and researcher decisions', 'explainers/validation.md'),
        ('agent_contract', 'Project operating contract for agents', 'explainers/agents/project_contract.md'),
        ('current_limitations', 'Current limitations and what they mean', 'explainers/limitations.md'),
        ('shared_mapping', 'One mapping stage per pipeline run', 'tools/skills/paper-to-ppr/references/operation-contract.md'),
        ('current_restoration', 'Selective compatible restoration', 'explainers/agents/project_contract.md'),
        ('current_snapshot', 'Full regional workbook snapshot', 'explainers/agents/project_contract.md'),
    ]
    records = []
    for key, question, expected_source in questions:
        command = [str(cli), 'query', question, '--graph', 'tools/knowledge_graph/graph.json', '--budget', '8000']
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf8')
        assert result.returncode == 0, (key, result.stderr)
        target = PROV / ('probe_human_' + key + '.txt')
        target.write_text(result.stdout, encoding='utf8')
        assert f'NODE {question} [src={expected_source} ' in result.stdout.replace('\\', '/'), (key, expected_source)
        records.append({'name': key, 'question': question, 'command': ['graphify'] + command[1:],
                        'exit_code': result.returncode, 'expected_current_source': expected_source,
                        'concept_and_source_present': True, 'output_file': target.name,
                        'output_sha256': sha(target), 'characters': len(result.stdout)})
        print(key + ': current concept and source retrieved')
    assert graph_sha == sha(GRAPH / 'graph.json')
    prior_path = PROV / 'retrieval_verification.json'
    prior = load(prior_path)
    save(prior_path, {'checked_at': now(), 'pass': True, 'graph_sha256': graph_sha,
                     'probes': records, 'prior_verified_suite': prior,
                     'scope': 'Nine actual installed CLI queries retrieve named current concepts and their correct human or agent source. This is bounded source navigation, not a full traversal or scientific verification.'})

def preservation():
    graph = load(GRAPH / 'graph.json')
    reused = load(RUNTIME / 'reused_semantic.json')
    retired = load(QA / 'retired_graph_relationships.json')
    edges = [e for link in graph['links'] for e in link['evidence']]
    exported = Counter(map(canonical, edges))
    expected = Counter(map(canonical, reused['edges']))
    hypers = Counter(map(canonical, graph.get('hyperedges', [])))
    expected_hypers = Counter(map(canonical, reused.get('hyperedges', [])))
    assert not (expected - exported), 'Missing or changed retained edge record'
    assert not (expected_hypers - hypers), 'Missing or changed retained hyperedge'
    dispositions = load(PROV / 'refresh_dispositions.json')
    assert dispositions['explicitly_retired_plan_relationships'] == 3
    assert len(reused['edges']) == dispositions['unchanged_source_edge_records'] == 1204
    assert len(reused.get('hyperedges', [])) == 23
    save(QA / 'graph_export_preservation.json', {
        'checked_at': now(), 'pass': True, 'graph_sha256': sha(GRAPH / 'graph.json'),
        'retained_edges_checked_as_full_record_multiset_subset': len(reused['edges']),
        'retained_hyperedges_checked_as_full_record_multiset_subset': len(reused.get('hyperedges', [])),
        'independent_exported_edge_records': len(edges), 'exported_hyperedges': len(graph.get('hyperedges', [])),
        'unexplained_record_losses': 0, 'explicit_plan_retirements': 3,
        'exact_retirement_evidence': 'retired_graph_relationships.json',
        'retirement_evidence_sha256': sha(QA / 'retired_graph_relationships.json'),
        'scope': 'All eligible retained current-source relationship records, including endpoint history, must survive export exactly. Three separately documented superseded plan relationships are the explicit scope exception.'})
    save(PROV / 'community_label_members.json', {
        'checked_at': now(), 'graph_sha256': sha(GRAPH / 'graph.json'),
        'communities': {cid: {'label': value['label'], 'members': value['members']} for cid, value in graph['communities'].items()},
        'assessment': 'All current communities were semantically assessed against actual current members, with prior actual membership overlap recorded in community_label_delta.json.'})
    print('Exact export preservation: 1204 retained edge records,23 hyperedges;3 explicit plan retirements')

def close():
    verification = load(PROV / 'completion_verification.json')
    assert verification['integrity_pass'] and verification['graph_sha256'] == sha(GRAPH / 'graph.json')
    retrieval = load(PROV / 'retrieval_verification.json')
    html = load(PROV / 'html_delta_verification.json')
    docs = load(QA / 'documentation_verification.json')
    preservation_proof = load(QA / 'graph_export_preservation.json')
    audit = load(QA / 'explainer_audit.json')
    review = load(QA / 'documentation_graph_review.json')
    html_review = load(QA / 'html_delta_review.json')
    assert all(d['pass'] for d in [retrieval, html, docs, preservation_proof])
    assert retrieval['graph_sha256'] == html['current_graph_sha256'] == preservation_proof['graph_sha256'] == sha(GRAPH / 'graph.json')
    assert html['current_html_sha256'] == verification['html_sha256'] == sha(GRAPH / 'graph.html')
    assert len(retrieval['probes']) == 9
    for record in retrieval['probes']:
        output=PROV / record['output_file']
        assert record['exit_code'] == 0 and sha(output) == record['output_sha256']
        assert f"NODE {record['question']} [src={record['expected_current_source']} " in output.read_text('utf8').replace('\\', '/')
    assert not review['findings']
    assert not html_review['findings']
    for name, expected in html_review['reviewed_sha256'].items():
        assert sha(ROOT / name) == expected, name
    assert audit['assessment']['ready_for_documentation_source_freeze']
    assert all(audit['assessment'][key] == 0 for key in ['open_critical', 'open_important', 'open_minor'])
    for record in audit['verification']['document_current_hashes']:
        assert sha(ROOT / record['path']) == record['sha256'], record['path']
    for name, expected in review['reviewed_sha256'].items():
        assert sha(ROOT / name) == expected, name
    assert len(load(PROV / 'community_labels.json')) == len(load(GRAPH / 'graph.json')['communities'])
    verification.update({'pass': True, 'retrieval_probes': 'Nine actual current-source CLI probes passed; bounded concept/source assertions.',
                         'html_interaction': 'Reuse of prior actual browser-tested identical script/template; current payload Node syntax, IDs and endpoints pass. No new interaction or screenshot claimed.',
                         'html_delta_verification': 'html_delta_verification.json',
                         'record_preservation': str((QA / 'graph_export_preservation.json').relative_to(ROOT)).replace('\\', '/'),
                         'explicit_plan_relationship_retirements': 3, 'completed_at': now()})
    save(PROV / 'completion_verification.json', verification)
    report = {'checked_at': now(), 'pass': True, 'baseline_commit': '768dffbee84c014e07850f88f042983caa186a41',
              'outcome': 'Current human guides are under explainers; operational agent rules are in explainers/agents/project_contract.md; three superseded plans are removed and durable rulings migrated.',
              'human_guides_kept_exactly': docs['preserved_human_guides'],
              'human_guides_exact_except_declared_replacements': docs['human_scientific_guides_exact_bytes_except_documented_replacements'],
              'local_link_destinations_checked': docs['local_link_destinations_checked'],
              'protected_scientific_files_full_byte_checked': docs['scientific_artifact_files_checked'],
              'scientific_bytes_unchanged': docs['scientific_bytes_unchanged'], 'scientific_executions': 0,
              'independent_review_findings_remaining': 0, 'independent_graph_review': 'documentation_graph_review.json',
              'independent_html_delta_review': 'html_delta_review.json',
              'independent_documentation_audit': 'explainer_audit.json',
              'graph': {'sources': verification['scope_files'], 'nodes': verification['nodes'],
                        'pairs': verification['topology_pairs'], 'edge_records': verification['independent_edge_evidence'],
                        'hyperedges': verification['hyperedges'], 'communities': len(load(GRAPH / 'graph.json')['communities']),
                        'sha256': verification['graph_sha256'], 'current_source_cli_probes': len(retrieval['probes']),
                        'retained_edge_records': 1204, 'retained_hyperedges': 23, 'explicit_plan_relationship_retirements': 3,
                        'html_verification': 'Prior actual interaction reused for byte-identical script/template; current payload checks pass.'},
              'scientific_readiness_or_full_pipeline_equivalence_established': False,
              'publication': 'Verified before commit; actual push and remote HEAD confirmation are recorded separately in ignored local receipt tools/knowledge_graph/provenance/.runtime/human_explainers_publication.json.'}
    save(QA / 'completion_report.json', report)
    evidence = [QA / name for name in ['documentation_verification.json', 'documentation_dispositions.json',
                'engine_guide_example_changes.json', 'explainer_audit.json', 'documentation_graph_review.json', 'html_delta_review.json',
                'retired_graph_relationships.json', 'graph_endpoint_reconciliation.json',
                'graph_export_preservation.json', 'completion_report.json']]
    evidence += [PROV / name for name in ['completion_verification.json', 'retrieval_verification.json',
                 'html_delta_verification.json', 'semantic_validation.json', 'community_label_delta.json']]
    save(QA / 'final_closure.json', {'checked_at': now(), 'pass': True,
         'state': 'All documentation, scientific-byte preservation, independent review and current graph checks complete before publication.',
         'evidence_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in evidence},
         'post_publication_receipt': 'tools/knowledge_graph/provenance/.runtime/human_explainers_publication.json',
         'self_reference_policy': 'No future commit hash or push result is invented in committed evidence.'})
    print('Documentation closure verified: scientific files unchanged; current graph and source navigation pass')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['probes', 'preservation', 'close'])
    globals()[parser.parse_args().action]()
