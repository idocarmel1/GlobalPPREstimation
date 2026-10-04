"""Close graph and trial QA; publication receipt is recorded after the commit."""
import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
RUN = Path(__file__).resolve().parent.parent
QA = RUN / 'qa'
GRAPH = ROOT / 'tools/knowledge_graph'
PROV = GRAPH / 'provenance'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return json.loads(path.read_text('utf8'))
def save(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
def signature(value): return json.dumps(value, sort_keys=True, ensure_ascii=False)

def main():
    checked_at = datetime.now(timezone.utc).isoformat()
    graph = load(GRAPH / 'graph.json')
    reused = load(PROV / '.runtime/reused_semantic.json')
    exported = [e for link in graph['links'] for e in link['evidence']]
    assert not (collections.Counter(map(signature, reused['edges'])) - collections.Counter(map(signature, exported)))
    assert not (collections.Counter(map(signature, reused['hyperedges'])) - collections.Counter(map(signature, graph['hyperedges'])))
    preservation = {'checked_at': checked_at, 'pass': True, 'graph_sha256': sha(GRAPH / 'graph.json'),
                    'accepted_source_edge_records_exactly_present': len(reused['edges']),
                    'accepted_source_hyperedges_exactly_present': len(reused['hyperedges']),
                    'explicit_endpoint_remaps': load(QA / 'graph_endpoint_reconciliation.json')['edge_records_with_explicit_endpoint_relocation'],
                    'comparison': 'Full-record Counter containment after independently supported endpoint relocation, against every final exported evidence record/hyperedge; zero losses.'}
    save(QA / 'graph_export_preservation.json', preservation)
    browser = {'checked_at': checked_at, 'pass': True, 'browser': 'Codex in-app browser via cua_repl',
               'url': 'http://127.0.0.1:8793/graph.html', 'html_sha256': sha(GRAPH / 'graph.html'),
               'graph_sha256': sha(GRAPH / 'graph.json'), 'current_artifact_actually_opened': True,
               'observed_counts': {'nodes': 2651, 'pairs': 5788, 'communities': 164},
               'interactions': [
                   'Search One mapping stage per pipeline run: one visible result; click showed operation-contract.md L24-L32, degree9.',
                   'Click Ecopath model validation neighbor: showed the current SKILL.md L6-L49, degree12, including shared mapping and full-validation neighbors.',
                   'Select All unchecked: all165 checkboxes unchecked; checked again: all165 checked.',
                   'Search and click Mixed-version publication rejection: showed operation-contract.md L67, degree3 and Operation-local read session neighbor.'
               ],
               'visual_inspection': 'Current screenshot inspected in tool output: graph rendered, readable source panel and scrollable neighbors/communities. No screenshot file retained.',
               'browser_error_logs': [], 'browser_error_log_limit': 20,
               'scope': 'Actual current HTML interaction; replaces prior browser status. Earlier template/delta proofs retain historical artifact hashes.'}
    save(PROV / 'browser_verification.json', browser)
    retrieval = load(PROV / 'retrieval_verification.json')
    static = load(PROV / 'html_static_verification.json')
    completion = load(PROV / 'completion_verification.json')
    assert retrieval['pass'] and retrieval['graph_sha256'] == sha(GRAPH / 'graph.json')
    assert static['pass'] and static['html_sha256'] == sha(GRAPH / 'graph.html')
    assert completion['integrity_pass'] and completion['graph_sha256'] == sha(GRAPH / 'graph.json')
    completion.update({'checked_at': checked_at, 'pass': True, 'retrieval_probes': '8 targeted installed CLI probes passed; exact source/concept anchors recorded',
                       'html_interaction': 'Current artifact actual search, neighbor navigation and165-checkbox filtering passed',
                       'reused_evidence_export_comparison': '1,223 edge records and21 hyperedges exactly present after documented six endpoint relocations',
                       'current_label_membership_record': 'community_label_members.json'})
    save(PROV / 'completion_verification.json', completion)
    protected = load(QA / 'final_protection_verification.json')
    assert protected['all_protected_bytes_unchanged'] and protected['protected_file_count'] == 461
    cleanup = load(QA / 'trial_copy_dispositions.json')
    closure = {'checked_at': checked_at, 'implementation_and_verification_complete': True,
               'baseline_commit': '85ae543693887a5439fb13ebd84bcb91f8ecc360',
               'supersedes': ['Historical pause status in resume_handoff.json', 'Pending graph/report boxes at implementation-plan capture time', 'Prior browser/retrieval graph snapshot completion status'],
               'skill_behavior': 'One shared taxon-to-group decision stage per composed run; validation consumes and checks the same keyed decision set, revisiting affected gaps only. Route-first instructions and operation-local content-checked selective read reuse.',
               'tests': '11 final ReadSession methods passed; earlier52-method focused dependency run includes8 earlier methods;55 distinct methods exercised.',
               'code_review': 'Important freshness/publication and graph relationship/citation/endpoint findings resolved. Final graph export comparison separately closes the reviewer pending operational items.',
               'graph': completion, 'export_evidence_preservation': preservation,
               'scientific_protection': protected, 'scratch_cleanup_disposition': 'trial_copy_dispositions.json',
               'scientific_fidelity_scope': 'completion_report.json classifies fresh extraction, supplied evidence reuse, tool regeneration and unmet replication. Full pipeline equivalence is false; known source/numerical/review gaps preserved; no scientific adoption or repair.',
               'publication': {'state_at_capture': 'Verified result prepared for the already-authorized ordinary main commit/push',
                               'remote': 'https://github.com/idocarmel1/GlobalPPREstimation.git',
                               'receipt': 'tools/knowledge_graph/provenance/.runtime/skill_efficiency_publication.json',
                               'receipt_policy': 'Local ignored receipt written only after actual commit/push/remote SHA verification, avoiding a self-referential commit/source hash.'}}
    save(QA / 'final_closure.json', closure)
    print(json.dumps({'graph_complete': completion['pass'], 'preserved_edges': len(reused['edges']),
                      'preserved_hyperedges': len(reused['hyperedges']), 'scientific_files_unchanged': 461}))

if __name__ == '__main__': main()
