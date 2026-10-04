"""Record current CLI retrieval and protected bytes after bounded trials."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
RUN = Path(__file__).resolve().parent.parent
QA = RUN / 'qa'
GRAPH = ROOT / 'tools/knowledge_graph'
PROV = GRAPH / 'provenance'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

def main():
    assert (ROOT / 'README.md').is_file(), ROOT
    graph = json.loads((GRAPH / 'graph.json').read_text('utf8'))
    probes = [
        ('mapping', 'One mapping stage per pipeline run', ['operation-contract.md', 'Ecopath model validation', 'Ecopath paper to regional PPR']),
        ('freshness', 'Mixed-version publication rejection', ['operation-contract.md', 'Operation-local read session']),
        ('read_session', 'ReadSession content hashes publication guard', ['workbooks/read_session.py', 'assert_unchanged']),
        ('validation', 'Full model validation workflow', ['references/full-validation.md', 'Ecopath model validation']),
        ('paper', 'Ecopath paper to regional PPR', ['paper-to-ppr/SKILL.md', 'Selection loadability readiness and researcher approval separation']),
        ('structure', 'Grouped region paper model layout', ['explainers/structure.md']),
        ('refresh', 'One-command regional refresh', ['explainers/structure.md']),
        ('restore', 'Selective compatible restoration', ['explainers/structure.md']),
    ]
    records = []
    for name, question, required in probes:
        args = ['graphify', 'query', question, '--graph', 'tools/knowledge_graph/graph.json', '--budget', '8000']
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf8')
        assert result.returncode == 0, (args, result.stderr)
        target = PROV / ('probe_efficiency_' + name + '.txt')
        target.write_text(result.stdout, encoding='utf8')
        missing = [anchor for anchor in required if anchor not in result.stdout]
        assert not missing, (name, missing)
        records.append({'name': name, 'question': question, 'command': args,
                        'exit_code': result.returncode, 'output_file': target.name,
                        'output_sha256': sha(target), 'required_visible_anchors': required,
                        'all_required_anchors_present': True,
                        'budget_notice_present': 'truncat' in result.stdout.lower(),
                        'scope': 'Targeted relevance and current source navigation; no complete-traversal claim.'})
    save(PROV / 'retrieval_verification.json', {
        'checked_at': datetime.now(timezone.utc).isoformat(), 'pass': True,
        'graph_sha256': sha(GRAPH / 'graph.json'), 'probes': records,
        'review': 'Root checked exact concept/source anchors in actual installed CLI output against the current graph. Earlier baseline probe files are historical; these eight probes supersede their completion status.',
        'limits': 'The initial informal budget1800 probes had truncated output. A first final-script attempt incorrectly expected the code class within the freshness concept neighborhood; its actual neighbor is Operation-local read session. A separate direct code query now checks ReadSession. Final budget8000 probes verify required visible anchors only; neither whole-graph traversal nor scientific validity is inferred.'})
    protected = json.loads((QA / 'live_protected_hashes.json').read_text('utf8'))
    differences = []
    for name, expected in protected.items():
        path = ROOT / name
        actual = sha(path) if path.is_file() else None
        if actual != expected:
            differences.append({'path': name, 'expected': expected, 'actual': actual})
    proof = {'checked_at': datetime.now(timezone.utc).isoformat(),
             'protected_file_count': len(protected), 'all_protected_bytes_unchanged': not differences,
             'differences': differences, 'input_manifest_sha256': sha(QA / 'live_protected_hashes.json'),
             'scope': 'Regional workbooks, canonical model JSONs, current validation Word reports, Project.xlsx and current atlas pages; full-byte comparison after graph export and scratch cleanup.'}
    save(QA / 'final_protection_verification.json', proof)
    assert not differences, differences
    save(PROV / 'community_label_members.json', {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'graph_sha256': sha(GRAPH / 'graph.json'), 'communities': graph['communities'],
        'label_review_evidence': 'community_label_delta.json',
        'scope': 'Actual exported membership with labels assessed by the fresh semantic agent; replaces the prior snapshot membership basis.'})
    print(json.dumps({'retrieval_probes_passed': len(records), 'protected_bytes_unchanged': len(protected),
                      'community_membership_records': len(graph['communities'])}))

if __name__ == '__main__':
    main()
