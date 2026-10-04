"""Check retained source coordinates and canonical values; never mutate inputs."""
import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import fitz
import openpyxl

ROOT = Path(__file__).resolve().parents[4]
REGION = ROOT / 'regions/LME_052'
MODEL_ID = '52_1_Sea_of_Okhotsk_NE_(1980)'
EVIDENCE = REGION / 'validation_reports' / MODEL_ID / 'diet_reextraction_20261002'
OUTPUT = Path(__file__).resolve().parent
MODEL = REGION / 'models' / MODEL_ID / 'model.json'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def diets(group):
    d = (group.get('diet_descr') or {}).get('diet', [])
    return [d] if isinstance(d, dict) else d

protected_before = {str(p.relative_to(ROOT)): sha(p) for p in REGION.rglob('*')
                    if p.is_file() and 'diet_audit_master_20261002' not in p.parts}
canonical_hash = sha(MODEL)
baseline_path = EVIDENCE / 'baseline_normalized_model.json'
baseline_hash = sha(baseline_path)
assert canonical_hash == 'f85c62fa8e4c57dcca72130aa649482d5716a87ac1ef3184324c2ca378ac2268'
assert baseline_hash == '61b6176affe6051948b3ec972fe87d95dabd8d98b66744b4c7350fcf303b9099'
canonical, baseline, ledger = read(MODEL), read(baseline_path), read(EVIDENCE / 'printed_diet_cells.json')
groups = {int(g['group_seq']): g for g in canonical['group']}
oldgroups = {int(g['group_seq']): g for g in baseline['group']}
source = ROOT / ledger['source_path']
assert sha(source) == ledger['source_sha256']
assert len(groups) == 29
assert len(ledger['cells']) == 754
assert len({(c['consumer_id'], c['prey_id']) for c in ledger['cells']}) == 754

# Verify the already-recorded bounding boxes against native PDF text. No fresh
# table discovery, model extraction, normalization or scientific run is invoked.
coordinate_text = {}
with fitz.open(source) as pdf:
    for page_id, grid in ledger['grids'].items():
        page = pdf[int(page_id) - 1]
        words = page.get_text('words')
        prey_right = grid['cell_bboxes'][0][2]
        row_boxes = grid['cell_bboxes'][1:30]
        candidate_boxes = [b for b in grid['cell_bboxes'] if b[0] >= prey_right - 0.001
                           and b[1] >= row_boxes[0][1] - 0.001]
        xstarts = sorted({b[0] for b in candidate_boxes})
        assert len(xstarts) == 13 and len(candidate_boxes) == 377
        offset = 0 if int(page_id) == 29 else 13
        for box in candidate_boxes:
            row = next(i for i, r in enumerate(row_boxes)
                       if abs(r[1] - box[1]) < 0.001 and abs(r[3] - box[3]) < 0.001)
            col = xstarts.index(box[0])
            text = ' '.join(w[4] for w in words
                            if box[0] <= (w[0] + w[2]) / 2 < box[2]
                            and box[1] <= (w[1] + w[3]) / 2 < box[3])
            coordinate_text[(offset + col + 1, row + 1)] = {'text': text, 'bbox': box}

cell_results, positive_count, blank_count = [], 0, 0
numeric_changes, precision_changes = [], []
sums, imports = [], []
for c in ledger['cells']:
    key = (c['consumer_id'], c['prey_id'])
    source_literal = coordinate_text[key]['text']
    assert source_literal == c['printed_cell'], (key, source_literal, c['printed_cell'])
    entries = {int(d['prey_seq']): d for d in diets(groups[key[0]])}
    actual = entries.get(key[1], {}).get('proportion', '0')
    assert Decimal(actual) == Decimal(source_literal or '0'), (key, actual, source_literal)
    if source_literal:
        positive_count += 1
        assert Decimal(source_literal) > 0 and actual == source_literal
    else:
        blank_count += 1
    cell_results.append({**c, 'verified_bbox': coordinate_text[key]['bbox'],
                         'native_pdf_text': source_literal, 'canonical_literal': actual,
                         'canonical_entry_present': key[1] in entries, 'match': True})
assert (positive_count, blank_count) == (174, 580)

for group_id, group in groups.items():
    old = oldgroups[group_id]
    imports.append({'consumer_id': group_id, 'canonical_import': group['diet_imp'],
                    'baseline_import': old['diet_imp'], 'source_table_has_import_row': False,
                    'exactly_preserved': group['diet_imp'] == old['diet_imp']})
    assert group['diet_imp'] == old['diet_imp'] == '0'
    total = sum((Decimal(d['proportion']) for d in diets(group)), Decimal(group['diet_imp']))
    sums.append({'consumer_id': group_id, 'consumer': group['group_name'],
                 'diet_plus_import_sum': str(total),
                 'table_consumer': group_id <= 26,
                 'review': 'pending cause/researcher trust review' if group_id <= 26 and total != 1
                 else 'no sum residual' if group_id <= 26 else 'nonfeeding group'})
    for d, od in zip(diets(group), diets(old)):
        assert d['prey_seq'] == od['prey_seq'] and d['detritus_fate'] == od['detritus_fate']
        if Decimal(d['proportion']) != Decimal(od['proportion']):
            numeric_changes.append({'consumer_id': group_id, 'prey_id': int(d['prey_seq']),
                                    'before': od['proportion'], 'after': d['proportion']})
        elif d['proportion'] != od['proportion']:
            precision_changes.append({'consumer_id': group_id, 'prey_id': int(d['prey_seq']),
                                      'before': od['proportion'], 'after': d['proportion']})
    # Replacing only diet proportion strings must reproduce the full baseline.
    test = copy.deepcopy(group)
    assert len(diets(test)) == len(diets(old))
    for d, od in zip(diets(test), diets(old)):
        d['proportion'] = od['proportion']
    assert test == old
assert canonical.keys() == baseline.keys() and len(numeric_changes) == 74 and len(precision_changes) == 30
assert {(c['consumer_id'],c['prey_id']) for c in numeric_changes} == {
    (c['consumer_id'],c['prey_id']) for c in read(EVIDENCE / 'changes.json')}
for c in read(EVIDENCE / 'changes.json'):
    match = next(x for x in numeric_changes if (x['consumer_id'],x['prey_id']) == (c['consumer_id'],c['prey_id']))
    assert match['before'] == c['old_proportion'] and match['after'] == c['new_printed_proportion']

workbook = openpyxl.load_workbook(REGION / 'LME_052.xlsx', read_only=True, data_only=False)
overview = {r[0]: r[1] for r in workbook['Overview'].values if len(r) >= 2 and r[0]}
workbook.close()
assert overview['selected_model_id'] == MODEL_ID
assert (REGION / overview['model_path']).resolve() == MODEL.resolve()
protected_after = {name: sha(ROOT / name) if (ROOT / name).exists() else None
                   for name in protected_before}
concurrent_changes = [name for name in protected_before if protected_before[name] != protected_after[name]]
assert sha(MODEL) == canonical_hash

result = {
    'timestamp_utc': datetime.now(timezone.utc).isoformat(),
    'outcome': 'verified unnormalized unchanged by independent auditor',
    'model_id': MODEL_ID, 'canonical_path': str(MODEL.relative_to(ROOT)),
    'audit_before_sha256': canonical_hash, 'audit_after_sha256': sha(MODEL),
    'owner_restoration_before_sha256': baseline_hash,
    'owner_restoration_after_sha256': canonical_hash,
    'source_path': ledger['source_path'], 'source_sha256': sha(source),
    'source_role': ledger['source_role'],
    'method': 'Native words checked against existing Table4a/b bounding boxes; exact Decimal cell comparison; structural baseline comparison; protected-file hashes',
    'verified_source_cells': len(cell_results), 'verified_positive_printed_cells': positive_count,
    'verified_blank_cells': blank_count, 'numeric_restorations_verified': len(numeric_changes),
    'printed_precision_only_changes_verified': len(precision_changes),
    'restored_consumers': sorted({c['consumer_id'] for c in numeric_changes}),
    'all_imports': imports, 'consumer_sums': sums,
    'non_diet_fields_and_detritus_fate_preserved_exactly': True,
    'protected_file_count': len(protected_before), 'concurrent_protected_file_changes': concurrent_changes,
    'runtime_normalization_always_allowed': True, 'runtime_normalization_or_fresh_scientific_runs_performed': False,
    'researcher_review': 'Non-unit sum causes and trust remain pending; small residuals alone do not establish rounding or approval',
    'accepted_overrides': 'All preexisting non-proportion fields preserved exactly; no source-disagreeing diet cell remains among 754 retained coordinates',
    'historical_results_model_sha256': overview['results_model_sha256'],
    'historical_results_match_new_canonical_bytes': overview['results_model_sha256'] == canonical_hash,
    'source_concerns': ['Related 2020 chapter based on unrecovered 2004 thesis; original thesis fidelity not established',
                        'Table4a/b has no import row; 29 existing diet_imp zero fields verified unchanged, not claimed printed-source values',
                        'Computational import group30 belongs to retained runtime evidence, not 29-group canonical source model',
                        'Historical diagnostics and saved workbook calculations retain prior normalized input identity'],
}
for name, value in [('verification.json',result), ('verified_cells.json',cell_results),
                    ('verified_baseline_changes.json',{'numeric':numeric_changes,'precision_only':precision_changes}),
                    ('protected_files.json',{'before':protected_before,'after':protected_after})]:
    (OUTPUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
