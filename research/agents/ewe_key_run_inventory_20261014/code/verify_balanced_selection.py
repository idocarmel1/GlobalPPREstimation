"""Verify the authorized selections, generated payloads and preservation."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import hashlib
import subprocess
import json
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from select_balanced_models import table_identity, TARGETS, STUDY, INDEPENDENT
from tools.project_core.validation.researcher_review import table_rows
from tools.project_core.workbooks.workbooks import sha
from tools.project_core.maps.original_atlas_data import embedded

def saved_rows(path, sheet, table):
    with ZipFile(path) as z:
        return [r for _, r in table_rows(z, sheet, table)[3]]

before = json.loads((STUDY / 'evidence/balanced_selection_before.json').read_text(encoding='utf-8'))
models = saved_rows(ROOT / 'Project.xlsx', 'Models & coverage', 'Models')
regions = {r['unit_id']: r for r in saved_rows(ROOT / 'Project.xlsx', 'Regions & status', 'Regions')}
catalog, _ = embedded(ROOT / 'interactive_map/index.html', 'DB')
series, _ = embedded(ROOT / 'interactive_map/trends.html', 'SERIES_DB')
checks = []
def independent_preservation(path, unit):
    current = table_identity(path)
    old = before['targets'][unit]['independent_tables_before']
    changes = []
    if current == old: return changes
    relative = path.relative_to(ROOT).as_posix()
    original_bytes = subprocess.run(['git', 'show', 'HEAD:' + relative], cwd=ROOT, capture_output=True, check=True).stdout
    assert hashlib.sha256(original_bytes).hexdigest() == before['region_hashes_before'][unit], 'Recovery bytes differ from assessed starting workbook'
    with ZipFile(BytesIO(original_bytes)) as previous, ZipFile(path) as present:
        for sheet, table in INDEPENDENT:
            key = sheet + '/' + table
            if old[key] == current[key]: continue
            old_table = table_rows(previous, sheet, table)
            new_table = table_rows(present, sheet, table)
            assert old_table[1] == new_table[1] and len(old_table[3]) == len(new_table[3]), 'Independent table structure changed: ' + key
            altered = []
            for i, ((_, a), (_, b)) in enumerate(zip(old_table[3], new_table[3])):
                for field in set(a) | set(b):
                    if a.get(field) == b.get(field): continue
                    assert field == 'model_id' and a.get(field) == '' and b.get(field) is None, 'Independent value changed: ' + key + '/' + str(field)
                    altered.append(i)
            changes.append({'table': key, 'change': 'Empty-string model_id cells serialized as absent cells; both mean independent Classic PPR with no Ecopath model identity', 'affected_rows': altered, 'numerical_cells_unchanged': True})
    return changes
for unit, _, mid, _, _, _ in TARGETS:
    path = ROOT / 'regions/LME' / unit / (unit + '.xlsx')
    settings = {r['field']: r.get('value') for r in saved_rows(path, 'Overview', 'Settings')}
    assert settings['selected_model_id'] == mid
    assert settings['results_model_id'] is None, 'Unexpected result adoption'
    assert settings['production_eligible'] in ['0', 'False'], settings['production_eligible']
    assert str(settings['calculation_status']).startswith('pending:')
    structural_changes = independent_preservation(path, unit)
    registered = [r for r in models if r['unit_id'] == unit and r.get('selected') == '1']
    assert len(registered) == 1 and registered[0]['model_id'] == mid
    assert not registered[0].get('researcher_review_status')
    assert regions[unit]['selected_model_id'] == mid and regions[unit]['sha256'] == sha(path)
    n = catalog['network']['units'][unit]
    chosen = n['models'][n['default_model']]
    s = series['units'][unit]
    assert chosen['id'] == mid and s['default_model'] == mid
    assert all(set(scope.get('methods', [])) <= {'simple trophic chain'} for scope in chosen['scopes'].values()), 'Unexpected Ecopath coefficient adoption'
    assert not chosen['group_data']['methods'], 'Unexpected group coefficients'
    assert not next(m for m in s['models'] if m['id'] == mid)['scopes']
    assert any(p['unit_id'] == unit and p.get('selected') for p in catalog['articles'])
    checks.append({'unit_id': unit, 'selected_model_id': mid, 'calculation_status': settings['calculation_status'],
                   'independent_values_unchanged': True, 'independent_serialization_changes': structural_changes, 'map_and_trend_default_match': True,
                   'ecopath_ppr_unavailable': True, 'researcher_approval_not_conferred': True,
                   'model_path': registered[0]['model_path'], 'overview_source_note': settings.get('source_note')})
target_units = {t[0] for t in TARGETS}
for unit, fingerprint in before['region_hashes_before'].items():
    if unit not in target_units:
        assert sha(ROOT / 'regions' / unit.split('_')[0] / unit / (unit + '.xlsx')) == fingerprint, unit
for path, fingerprint in before['canonical_hashes_before'].items():
    assert sha(ROOT / path) == fingerprint, path
current_models = {(r['unit_id'], r['model_id']): r for r in models}
current_papers = {r['article_id']: r for r in saved_rows(ROOT / 'Project.xlsx', 'Papers', 'Papers')}
def comparable(v):
    if v is None: return None
    if isinstance(v, bool): return '1' if v else '0'
    if isinstance(v, (int, float)):
        return format(float(v), '.16g')
    return str(v)
for old in before['registered_models_before']:
    new = current_models[(old['unit_id'], old['model_id'])]
    for key, value in old.items():
        if key in ['selected', 'selection_rationale', 'atlas_region_rank']: continue
        assert comparable(value) == comparable(new.get(key)), (old['model_id'], key)
for old in before['registered_papers_before']:
    new = current_papers[old['article_id']]
    for key, value in old.items():
        if key in ['selected', 'atlas_region_rank']: continue
        assert comparable(value) == comparable(new.get(key)), (old['article_id'], key)
result = {'date': '2026-10-14', 'checks': checks, 'all_canonical_jsons_unchanged': True,
          'unrelated_regional_workbooks_unchanged': True,
          'preexisting_source_metadata_and_review_records_preserved': True,
          'published_hashes': {p: sha(ROOT / p) for p in ['Project.xlsx', 'interactive_map/index.html', 'interactive_map/trends.html', 'interactive_map/sources.html']}}
(STUDY / 'evidence/balanced_selection_verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
