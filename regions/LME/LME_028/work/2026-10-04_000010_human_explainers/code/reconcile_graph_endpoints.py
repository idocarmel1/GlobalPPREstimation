"""Resolve current moved concepts while preserving prior graph evidence exactly."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
RUN = Path(__file__).resolve().parent.parent
PROV = ROOT / 'tools/knowledge_graph/provenance'
RUNTIME = PROV / '.runtime'

def load(path): return json.loads(path.read_text('utf8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

def main():
    reused = load(RUNTIME / 'reused_semantic.json')
    fragment = load(RUNTIME / 'chunk_01.json')
    nodes = {n['id']: n for n in fragment['nodes']}
    dispositions = load(PROV / 'refresh_dispositions.json')
    required = {n['id'] for n in dispositions['pending_endpoint_references'] if n['requires_fresh_semantic_source']}
    resolutions = load(RUNTIME / 'endpoint_resolution.json')['resolutions']
    assert {r['old_id'] for r in resolutions} == required
    hashes = load(PROV / 'corpus.json')['sha256']
    for r in resolutions:
        n = nodes[r['new_id']]
        assert n['source_file'] == r['source_file'] and n['source_location'] == r['source_location']
        assert sha(ROOT / r['source_file']) == hashes[r['source_file']]
        assert r['disposition'] in ['supported_current_identity', 'moved_supported_concept']
    mapping = {r['old_id']: r['new_id'] for r in resolutions}
    original = copy.deepcopy(reused)
    changes = {'edges': 0, 'hyperedges': 0}
    proof_path = RUN.relative_to(ROOT).as_posix() + '/qa/graph_endpoint_reconciliation.json'
    for kind in ['edges', 'hyperedges']:
        for record in reused[kind]:
            before = record['nodes'][:] if kind == 'hyperedges' else [record['source'], record['target']]
            after = [mapping.get(n, n) for n in before]
            if before == after: continue
            history = record.get('endpoint_relocation_history', [])
            record['endpoint_relocation_history'] = history + [{'before': before, 'after': after, 'proof': proof_path}]
            if kind == 'hyperedges': record['nodes'] = after
            else: record['source'], record['target'] = after
            changes[kind] += 1
    assert len(reused['edges']) == len(original['edges']) == dispositions['unchanged_source_edge_records']
    assert len(reused['hyperedges']) == len(original['hyperedges']) == dispositions['unchanged_source_hyperedges']
    for kind in ['edges', 'hyperedges']:
        for before, after in zip(original[kind], reused[kind]):
            recovered = copy.deepcopy(after)
            if len(after.get('endpoint_relocation_history', [])) > len(before.get('endpoint_relocation_history', [])):
                event = recovered['endpoint_relocation_history'].pop()
                if not recovered['endpoint_relocation_history'] and 'endpoint_relocation_history' not in before:
                    recovered.pop('endpoint_relocation_history')
                if kind == 'hyperedges': recovered['nodes'] = event['before']
                else: recovered['source'], recovered['target'] = event['before']
            assert before == recovered, 'Original evidence beyond the declared current endpoint layer changed'
    save(RUNTIME / 'reused_semantic.json', reused)
    result = {'policy': 'Retain every current-scope unchanged-source record and prior relocation metadata; add only independently supported current endpoint history.',
              'required_concepts': len(required), 'resolutions': resolutions,
              'unchanged_source_edge_records': len(reused['edges']), 'unchanged_source_hyperedges': len(reused['hyperedges']),
              'edge_records_with_explicit_endpoint_relocation': changes['edges'], 'hyperedges_with_explicit_endpoint_relocation': changes['hyperedges'],
              'original_evidence_recoverable_exactly': True, 'unexplained_edge_records_dropped': 0, 'hyperedges_dropped': 0,
              'separate_user_authorized_retirements': 'retired_graph_relationships.json',
              'prior_endpoint_reconciliation_evidence': 'regions/LME/LME_028/work/2026-10-04_000009_skill_efficiency/qa/graph_endpoint_reconciliation.json',
              'semantic_fragment_sha256': sha(RUNTIME / 'chunk_01.json'), 'source_identity_checked': True}
    save(PROV / 'endpoint_reconciliation.json', result)
    save(RUN / 'qa/graph_endpoint_reconciliation.json', result)
    print(json.dumps({'resolved_concepts': len(required), 'retained_edges': len(reused['edges']), 'retained_hyperedges': len(reused['hyperedges']), 'relocations': changes}))

if __name__ == '__main__': main()
