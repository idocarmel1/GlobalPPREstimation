"""Authenticate the completed administrative selection/publication evidence."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

ROOT = Path(__file__).resolve().parents[4]
STUDY = ROOT / 'research/agents/ewe_key_run_inventory_20261014'
EVIDENCE = STUDY / 'evidence'
verification = json.loads((EVIDENCE / 'balanced_selection_verification.json').read_text(encoding='utf-8'))
before = json.loads((EVIDENCE / 'balanced_selection_before.json').read_text(encoding='utf-8'))
paths = [
    ('before_selection', EVIDENCE / 'balanced_selection_before.json'),
    ('selection_verification', EVIDENCE / 'balanced_selection_verification.json'),
    ('browser_checks', EVIDENCE / 'balanced_selection_browser_checks.json'),
    ('html_verification', EVIDENCE / 'balanced_selection_html_verification.log'),
    ('north_refresh', EVIDENCE / 'north_sea_selection_refresh.log'),
    ('baltic_refresh', EVIDENCE / 'baltic_selection_refresh.log'),
    ('selection_report', STUDY / 'SELECTION_PUBLICATION_REPORT.md'),
    ('central_workbook', ROOT / 'Project.xlsx'),
    ('map_page', ROOT / 'interactive_map/index.html'),
    ('trend_page', ROOT / 'interactive_map/trends.html'),
    ('source_page', ROOT / 'interactive_map/sources.html'),
]
for record in verification['checks']:
    unit = record['unit_id']
    model = ROOT / record['model_path']
    assert hashlib.sha256(model.read_bytes()).hexdigest() == before['targets'][unit]['model_sha256']
    paths.extend([(unit + '_source_snapshot', model), (unit + '_regional_workbook', ROOT / 'regions/LME' / unit / (unit + '.xlsx'))])
old = ROOT / 'regions/LME/LME_022/papers/NS-2025/models/22_20251990_East_Coast_of_Scotland_(1991-1995)/results'
manifest = json.loads((old / 'result_manifest.json').read_text(encoding='utf-8'))
assert manifest['model_id'] == before['targets']['LME_022']['overview_before']['results_model_id']
assert manifest['snapshot_sha256'] == hashlib.sha256((old / 'regional_snapshot.xlsx').read_bytes()).hexdigest()
paths.extend([('outgoing_north_snapshot', old / 'regional_snapshot.xlsx'), ('outgoing_north_manifest', old / 'result_manifest.json')])
index = {
    'schema_version': 1, 'run_id': '2026-10-14_balanced_port_selection_publication',
    'region_id': 'LME_022_and_LME_023', 'model_id': 'North_Sea_and_Baltic_Proper_Rpath_snapshots',
    'variant_id': 'published_static_source_snapshots',
    'source_identity': 'Deposited Rpath ports; canonical hashes preserved; accepted native EwE equivalence unestablished',
    'computational_input_identity': 'Administrative selection only; independent saved arithmetic preserved; no new SPPR/Ecosim execution',
    'methods': [], 'required_roles': [role for role, _ in paths],
    'artifacts': [{'role': role, 'path': Path(os.path.relpath(path, EVIDENCE)).as_posix(),
                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'availability': 'present'} for role, path in paths],
    'reconciliation': {'saved_choices_match_pages': True, 'scientific_jsons_preserved': True,
                       'independent_numerical_values_preserved': True, 'other_region_workbooks_preserved': True,
                       'existing_source_metadata_and_review_records_preserved': True, 'unavailable_ecopath_results_remain_unavailable': True},
}
ip = EVIDENCE / 'balanced_selection_evidence_index.json'
ip.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
spec = importlib.util.spec_from_file_location('check_evidence', ROOT / 'tools/skills/paper-to-ppr/scripts/check_evidence.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
result = checker.check(ip)
(EVIDENCE / 'balanced_selection_evidence_completeness.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert result['complete'], result
print(json.dumps({'complete': result['complete'], 'verified_artifacts': len(result['verified_artifacts']), 'errors': result['errors']}))
