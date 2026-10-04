"""Reconcile freshly verified moved concepts without dropping source evidence."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
RUN = Path(__file__).resolve().parent.parent
PROV = ROOT / 'tools/knowledge_graph/provenance'
RUNTIME = PROV / '.runtime'
def load(path): return json.loads(path.read_text(encoding='utf8'))
def save(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
reused = load(RUNTIME / 'reused_semantic.json')
fragment = load(RUNTIME / 'chunk_01.json')
nodes = {n['id']: n for n in fragment['nodes']}
resolutions = load(RUNTIME / 'endpoint_resolution.json')['resolutions']
dispositions = load(PROV / 'refresh_dispositions.json')
required = {n['id'] for n in dispositions['pending_endpoint_references'] if n['requires_fresh_semantic_source']}
assert {r['old_id'] for r in resolutions} == required
for r in resolutions:
    n = nodes[r['new_id']]
    assert n['source_file'] == r['source_file'] and n['source_location'] == r['source_location']
    assert sha(ROOT / r['source_file']) == load(PROV / 'corpus.json')['sha256'][r['source_file']]
    assert r['disposition'] in ['supported_current_identity', 'moved_supported_concept']
mapping = {r['old_id']: r['new_id'] for r in resolutions}
original = copy.deepcopy(reused)
changed_edges = changed_hypers = 0
for e in reused['edges']:
    replacements = {k: mapping.get(e[k], e[k]) for k in ['source', 'target']}
    if any(replacements[k] != e[k] for k in replacements):
        e['original_source'] = e['source']; e['original_target'] = e['target']
        e.update(replacements); e['endpoint_reconciliation'] = 'provenance/endpoint_reconciliation.json'
        changed_edges += 1
for h in reused.get('hyperedges', []):
    replacements = [mapping.get(n, n) for n in h['nodes']]
    if replacements != h['nodes']:
        h['original_nodes'] = h['nodes']; h['nodes'] = replacements
        h['endpoint_reconciliation'] = 'provenance/endpoint_reconciliation.json'
        changed_hypers += 1
assert len(original['edges']) == len(reused['edges']) == dispositions['unchanged_source_edge_records']
assert len(original['hyperedges']) == len(reused['hyperedges']) == dispositions['unchanged_source_hyperedges']
for before, after in zip(original['edges'], reused['edges']):
    recovered = copy.deepcopy(after)
    if 'endpoint_reconciliation' in recovered:
        recovered['source'] = recovered.pop('original_source'); recovered['target'] = recovered.pop('original_target')
        recovered.pop('endpoint_reconciliation')
    assert before == recovered, 'Changed original evidence beyond explicit endpoint relocation'
for before, after in zip(original['hyperedges'], reused['hyperedges']):
    recovered = copy.deepcopy(after)
    if 'endpoint_reconciliation' in recovered:
        recovered['nodes'] = recovered.pop('original_nodes'); recovered.pop('endpoint_reconciliation')
    assert before == recovered
save(RUNTIME / 'reused_semantic.json', reused)
result = {'policy': 'Original unchanged-source evidence preserved, with independently extracted endpoint locations for moved concepts',
          'required_concepts': len(required), 'resolutions': resolutions,
          'unchanged_source_edge_records': len(reused['edges']), 'unchanged_source_hyperedges': len(reused['hyperedges']),
          'edge_records_with_explicit_endpoint_relocation': changed_edges, 'hyperedges_with_explicit_endpoint_relocation': changed_hypers,
          'original_evidence_recoverable_exactly': True, 'edge_records_dropped': 0, 'hyperedges_dropped': 0,
          'semantic_fragment_sha256': sha(RUNTIME / 'chunk_01.json'), 'source_identity_checked': True}
save(PROV / 'endpoint_reconciliation.json', result)
save(RUN / 'qa/graph_endpoint_reconciliation.json', result)
print(json.dumps({k: result[k] for k in ['required_concepts', 'unchanged_source_edge_records', 'unchanged_source_hyperedges', 'edge_records_with_explicit_endpoint_relocation', 'hyperedges_with_explicit_endpoint_relocation', 'edge_records_dropped']}))
