"""Explicitly retire references to the three user-removed planning concepts."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
QA = Path(__file__).resolve().parent.parent / 'qa'
PROV = ROOT / 'tools/knowledge_graph/provenance'
retired_ids = {
    'plans_skill_efficiency_ideas_reuse',
    'plans_skill_efficiency_ideas_proposed_reusable_mechanical_checks',
    'plans_skill_efficiency_implementation_plan_blind_source_extraction',
}
path = PROV / '.runtime/reused_semantic.json'
data = json.loads(path.read_text('utf8'))
retired = [e for e in data['edges'] if e['source'] in retired_ids or e['target'] in retired_ids]
assert len(retired) == 3
assert not any(retired_ids.intersection(h['nodes']) for h in data['hyperedges'])
assert not any(n['id'] in retired_ids for n in data['nodes'])
for e in retired:
    assert hashlib.sha256((ROOT / e['source_file']).read_bytes()).hexdigest() == e['source_sha256']
data['edges'] = [e for e in data['edges'] if e not in retired]
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
proof = {'explicit_user_scope': 'Replace legacy plans with current human guides and agent instructions; no current plan authority retained.',
         'retired_concept_ids': sorted(retired_ids), 'retired_relationship_count': len(retired),
         'exact_original_relationship_records': retired,
         'reason': 'These relationships refer to removed proposal/implementation-plan concepts, not a supported current source. Deliberate current-scope retirement is separately recorded rather than silently dropping a changed endpoint.',
         'retained_unchanged_source_edge_records': len(data['edges']),
         'retained_unchanged_source_hyperedges': len(data['hyperedges']),
         'scientific_source_bytes_changed': False}
(QA / 'retired_graph_relationships.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
path = PROV / 'refresh_dispositions.json'
dispositions = json.loads(path.read_text('utf8'))
dispositions['unchanged_source_edge_records_before_explicit_plan_retirements'] = dispositions['unchanged_source_edge_records']
dispositions['unchanged_source_edge_records'] = len(data['edges'])
dispositions['explicitly_retired_plan_relationships'] = len(retired)
dispositions['plan_retirement_evidence'] = 'regions/LME/LME_028/work/2026-10-04_000010_human_explainers/qa/retired_graph_relationships.json'
dispositions['retired_endpoint_references'] = [n for n in dispositions['pending_endpoint_references'] if n['id'] in retired_ids]
dispositions['pending_endpoint_references'] = [n for n in dispositions['pending_endpoint_references'] if n['id'] not in retired_ids]
path.write_text(json.dumps(dispositions, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'explicit_retirements': len(retired), 'retained_edges': len(data['edges']), 'retained_hyperedges': len(data['hyperedges'])}))
