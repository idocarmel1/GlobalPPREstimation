"""Rescan actual regional selections and gather normalization audit receipts."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'tools'))
from researcher_review import table_rows
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return json.loads(path.read_text(encoding='utf-8-sig'))
initial = load(OUT / 'selected_inventory.json')
selected = []
for path in sorted((ROOT / 'regions').glob('*/*.xlsx')):
    if path.stem != path.parent.name:
        continue
    with zipfile.ZipFile(path) as archive:
        _, _, _, rows = table_rows(archive, 'Overview', 'Settings')
        settings = {data['field']: data['value'] for _, data in rows}
    if settings.get('selected_model_id'):
        model = path.parent / settings['model_path']
        selected.append({'region': path.stem, 'model': settings['selected_model_id'],
                         'path': settings['model_path'], 'current_model_sha256': sha(model)})
assert {(d['region'], d['model'], d['path']) for d in selected} == {(d['region'], d['model'], d['path']) for d in initial}, 'Selections changed during audit: investigate before completion'
fallback = {
    'LME_003': ('author_source_unnormalized_unchanged', 'regions/LME_003/diet_reextraction_20261002/audit_result.json'),
    'LME_027': ('native_preserved_unchanged_printed_fidelity_unresolved', 'regions/LME_027/validation_reports/diet_reextraction_20261002/provenance.json'),
    'LME_035': ('native_preserved_unchanged_printed_fidelity_unresolved', 'regions/LME_035/diet_reextraction_20261002/audit_result.json'),
    'LME_028': ('blocked_normalization_attribution_unchanged', 'regions/LME_028/validation_reports/28_646_Guinea_(1998)/diet_reextraction_20261002/result.json'),
    'LME_013': ('printed_unnormalized_unchanged', 'regions/LME_013/models/13_1_Chilean_Patagonia_(1980)/diet_reextraction_20261002/audit.json'),
    'HS_077': ('printed_unnormalized_unchanged_source_deficits_unresolved', 'regions/HS_077/evidence/diet_reextraction_20261002/audit.json'),
    'LME_052': ('owner_restored_source_verified_read_only', 'regions/LME_052/diet_audit_master_20261002/independent_verification/verification.json'),
    'LME_047': ('excluded_read_only_confirmed_normalized_91_cells', 'regions/LME_047/diet_audit_master_20261002/audit_result.json')}
outcomes = []
for current in selected:
    unit = current['region']
    old = next(d for d in initial if d['region'] == unit)
    item = {**current, 'audit_initial_model_sha256': old['audit_initial_model_sha256'],
            'scope': old['scope'], 'receipt_paths': []}
    paths = [p for p in (ROOT / 'regions' / unit).rglob('root_receipt.json') if '20261002' in p.as_posix()]
    if paths:
        path = max(paths, key=lambda p: p.stat().st_mtime)
        data = load(path)
        assert data.get('region') == unit, (unit, 'receipt region differs')
        assert data.get('selected_after_sha256', data['canonical_after_sha256']) == current['current_model_sha256'], (unit, 'selected receipt no longer current')
        item.update(outcome=data['outcome'], canonical_before_sha256=data['canonical_before_sha256'],
                    canonical_after_sha256=data['canonical_after_sha256'],
                    changed_diet_cells=data.get('changed_diet_cells', []),
                    precise_blockers=data.get('precise_blockers', []),
                    protected_files_unchanged=data.get('protected_files_unchanged'),
                    receipt_paths=[path.relative_to(ROOT).as_posix()])
    elif unit in fallback:
        outcome, path = fallback[unit]
        assert (ROOT / path).exists(), path
        item.update(outcome=outcome, receipt_paths=[path])
    else:
        assert unit in ('LME_032', 'LME_034', 'LME_036'), (unit, 'Missing regional audit')
        item['outcome'] = 'excluded_not_audited_or_modified'
    if unit not in ('LME_038', 'LME_052'):
        assert old['audit_initial_model_sha256'] == current['current_model_sha256'], (unit, 'Selected input unexpectedly changed')
    outcomes.append(item)
result = {'selected_count': len(selected), 'selections_unchanged': True,
          'runtime_comparison': {'atol': 1e-12, 'rtol': 0,
             'ignored_fields': ['biomass_accum', 'biomass_accum_rate', 'growth', 'predation'],
             'ignored_changes_recorded_separately': True},
          'outcomes': outcomes}
(OUT / 'outcomes.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({'selected_count': len(selected), 'selections_unchanged': True,
                  'regions': {item['region']: item['outcome'] for item in outcomes}}, indent=2))
