"""Read-only source comparison. Every output stays in this new evidence directory."""
from pathlib import Path
from decimal import Decimal, localcontext
import hashlib, json, zipfile, xml.etree.ElementTree as ET, datetime, shutil
import openpyxl

OUT = Path(__file__).resolve().parent
R = OUT.parent
ROOT = R.parent.parent
MID = '47_2_East_China_Sea_(2018)'
V = R / 'validation_reports' / MID
M = R / 'models' / MID / 'model.json'
S = R / 'papers/ECS-2022/DataSheet_1_EstimatingtheImpactofaSeasonal-7491f315.docx'
REPORT = R / f'Model_validation_{MID}.docx'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
D = Decimal

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def snapshot():
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(R.rglob('*'))
            if p.is_file() and not p.is_relative_to(OUT)}

before = snapshot()
model_hash = sha(M)
model_bytes = M.read_bytes()
model = json.loads(model_bytes)
wb = openpyxl.load_workbook(R / 'LME_047.xlsx', read_only=True, data_only=False)
overview = {row[0]: row[1] for row in wb['Overview'].values if len(row) >= 2 and row[0]}
wb.close()
assert overview['selected_model_id'] == MID
assert (R / overview['model_path']).resolve() == M.resolve()
assert hashlib.sha256(model_bytes).hexdigest() == model_hash
with zipfile.ZipFile(S) as z:
    doc = ET.fromstring(z.read('word/document.xml'))
tables = doc.findall('.//w:tbl', NS)
rows = [[''.join(x.text or '' for x in c.findall('.//w:t', NS)).strip()
         for c in row.findall('w:tc', NS)] for row in tables[5].findall('w:tr', NS)]
body = list(doc.find('w:body', NS))
table_position = body.index(tables[5])
caption = ''.join(x.text or '' for x in body[table_position-1].findall('.//w:t', NS))
assert 'M2018' in caption and 'Table 3' in caption
assert len(rows) == 25 and all(len(row) == 24 for row in rows)
canonical = {int(g['group_seq']): (i, g) for i, g in enumerate(model['group'])}
ledger, sums = [], []
retained = json.loads((V / 'source_diet_cell_review.json').read_text(encoding='utf-8'))
retained_cells = {(c['prey'], c['predator']): c for c in retained['cells']}
retained_disagreements = []
with localcontext() as ctx:
    ctx.prec = 60
    for pred in range(2, 24):
        gi, g = canonical[pred]
        diet = g['diet_descr']['diet']
        singleton = isinstance(diet, dict)
        diet = [diet] if singleton else diet
        native = {int(c['prey_seq']): (i, c) for i, c in enumerate(diet)}
        source_sum = sum(D(row[pred]) for row in rows[1:])
        canonical_sum = sum(D(c['proportion']) for c in diet)
        imp = D(g['diet_imp'])
        mismatch_count = 0
        norm_gap = D(0)
        for row_idx, row in enumerate(rows[1:], 2):
            prey = int(row[0]); literal = row[pred]
            entry = native.get(prey)
            can_literal = entry[1]['proportion'] if entry else '0'
            can = D(can_literal); source = D(literal)
            exact_match = source == can
            mismatch_count += not exact_match
            normalized = source / source_sum
            gap = abs(normalized-can); norm_gap = max(norm_gap, gap)
            pointer = (f'/group/{gi}/diet_descr/diet' + ('' if singleton else f'/{entry[0]}') + '/proportion') if entry else None
            previous = retained_cells[(prey, pred)]
            if D(str(previous['published'])) != source or D(str(previous['canonical'])) != can:
                retained_disagreements.append({'prey': prey, 'consumer': pred})
            ledger.append({'consumer_id': pred, 'consumer_name': g['group_name'],
                           'prey_id': prey, 'source_prey_name': row[1],
                           'source_file': S.relative_to(ROOT).as_posix(), 'source_sha256': sha(S),
                           'source_xml_coordinate': f'word/document.xml table[6] row[{row_idx}] cell[{pred+1}] (one-based)',
                           'table': 'Supplementary Table 3 M2018', 'source_literal': literal,
                           'canonical_literal': can_literal, 'canonical_json_pointer': pointer,
                           'missing_canonical_cell': entry is None,
                           'missing_cell_treatment': 'implicit structural zero for comparison' if entry is None else None,
                           'exact_decimal_equal': exact_match,
                           'source_column_normalized_comparison_literal': str(normalized),
                           'normalization_residual': str(gap),
                           'accepted_cell_correction': 'No separate cell-specific researcher override found; signed review accepts diet deviations as rounding errors.'})
        sums.append({'consumer_id': pred, 'consumer_name': g['group_name'],
                     'source_prey_sum': str(source_sum), 'canonical_prey_sum': str(canonical_sum),
                     'canonical_import_literal': str(imp), 'canonical_diet_plus_import_sum': str(canonical_sum+imp),
                     'primary_import_status': 'S3 has no import row; canonical native diet_imp is zero; no separate primary import vector established.',
                     'source_to_canonical_normalization_factor': str(D(1)/source_sum),
                     'changed_source_cells': mismatch_count,
                     'maximum_residual_from_source_column_normalization': str(norm_gap),
                     'source_normalization_matches_within_1e-12': norm_gap < D('1e-12')})
    for pred in [1, 24]:
        gi, g = canonical[pred]; diet=(g.get('diet_descr') or {}).get('diet') or []; diet=[diet] if isinstance(diet,dict) else diet
        s=sum(D(c['proportion']) for c in diet); imp=D(g['diet_imp'])
        sums.append({'consumer_id':pred, 'consumer_name':g['group_name'],
                     'source_prey_sum':None, 'canonical_prey_sum':str(s),
                     'canonical_import_literal':str(imp), 'canonical_diet_plus_import_sum':str(s+imp),
                     'status':'Nonfeeding phytoplankton/detritus; S3 has no consumer column; unchanged.'})

raw = json.loads((V / 'raw_diet_review.json').read_text(encoding='utf-8'))
raw_comparison = []
for row in raw['canonical_rows']:
    seq = row['seq']; g = canonical[seq][1]; diet=(g.get('diet_descr') or {}).get('diet') or []; diet=[diet] if isinstance(diet,dict) else diet
    raw_comparison.append({'consumer_id':seq, 'retained_items_equal_current_canonical': row['items'] == diet,
                           'note':'Despite raw_diet filename, canonical_rows reproduces normalized accepted JSON, not printed S3 literals.'})
with zipfile.ZipFile(REPORT) as z:
    reportdoc = ET.fromstring(z.read('word/document.xml'))
report_diet = [''.join(x.text or '' for x in p.findall('.//w:t',NS)) for p in reportdoc.findall('.//w:p',NS)]
report_diet = [t for t in report_diet if 'diet' in t.lower() or 'rounding' in t.lower() or 'normaliz' in t.lower()]
signed = json.loads((V/'researcher_review_20261002/signed_source_summary.json').read_text(encoding='utf-8'))
review = json.loads((V/'researcher_review_20261002/verification.json').read_text(encoding='utf-8'))
execution = json.loads((V/'direct_diagnostics/execution_evidence.json').read_text(encoding='utf-8'))
runtime_state = json.loads((V/'direct_diagnostics/loaded_state.json').read_text(encoding='utf-8'))
runtime_diet_keys = [k for k in runtime_state if any(x in k.lower() for x in ['dc','diet'])]
dc=runtime_state['_DC']
runtime_rows=[]
runtime_cells=[]
with localcontext() as ctx:
    ctx.prec=60
    for seq, values in zip(dc['index'],dc['data']):
        if seq not in canonical:
            continue
        gi,g=canonical[seq]; diet=(g.get('diet_descr') or {}).get('diet') or []; diet=[diet] if isinstance(diet,dict) else diet
        can={int(c['prey_seq']):D(c['proportion']) for c in diet}; can[25]=D(g['diet_imp'])
        native_sum=sum(can.values()); loaded_sum=sum(D(str(x)) for x in values)
        changed=0
        for col_idx,(prey,value) in enumerate(zip(dc['columns'],values)):
            prior=can.get(prey,D(0));loaded=D(str(value));different=prior!=loaded;changed+=different
            if different:
                runtime_cells.append({'consumer_id':seq,'prey_id':prey,'canonical_literal':str(prior),
                                      'retained_runtime_literal':str(value),'runtime_json_pointer':f'/_DC/data/{dc["index"].index(seq)}/{col_idx}',
                                      'note':'Historical loaded state difference; not a mutation performed by this audit.'})
        runtime_rows.append({'consumer_id':seq,'canonical_diet_plus_import_sum':str(native_sum),
                             'retained_runtime_sum':str(loaded_sum),
                             'theoretical_runtime_factor_from_exact_canonical_literals':str(D(1)/native_sum) if native_sum else None,
                             'changed_decimal_cells':changed,
                             'factor_limitation':'Loaded float implementation uses binary row sums; factor above is exact-decimal comparison, not an executed transform.'})
archive = ROOT/'original_research_archive/research/discard_sensitivity_expanded_2026_09_10/inputs/corpus/global_cover_jsons'/f'{MID}.json'
baseline = ROOT/'original_research_archive/research/selected_regions_validation_20260930/baseline/LME_047/accepted_model.json'
history = {'migration_original_path':'PPREstimation/real_models/global_cover_jsons/47_2_East_China_Sea_(2018).json',
           'migration_sha256': '31b1f6c360ce1d454db528e050100e5521cbf663cdb9d3001f0f39724a14ed16',
           'retained_original_converter_receipt':None,
           'retained_native_EwE_export':None,
           'historical_copies':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p), 'bytes_equal_selected':p.read_bytes()==model_bytes} for p in [archive,baseline]],
           'later_source_review_script':'regions/LME_047/validation_reports/47_2_East_China_Sea_(2018)/reproduction/source_package.py lines 13-21 compare original S3 against canonical and document normalization; script was read, not run.'}
assert len(ledger)==528
assert sum(not c['exact_decimal_equal'] for c in ledger)==91
assert all(s['source_normalization_matches_within_1e-12'] for s in sums if 'source_normalization_matches_within_1e-12' in s)
assert not retained_disagreements
assert all(x['retained_items_equal_current_canonical'] for x in raw_comparison)
assert sha(M) == model_hash
write('cell_ledger.json',ledger)
write('consumer_sums.json',sums)
write('retained_runtime_comparison.json',{'source_input_sha256':execution['canonical_sha256'],
      'state_path':(V/'direct_diagnostics/loaded_state.json').relative_to(ROOT).as_posix(),
      'state_sha256':sha(V/'direct_diagnostics/loaded_state.json'),
      'settings':execution['constructor_settings'],'rows':runtime_rows,'changed_cells':runtime_cells,
      'note':'Historical runtime normalization is separate from canonical normalization; no fresh science or loader execution.'})
write('source_and_review_context.json',{'caption':caption,'overview':overview,'history':history,
      'retained_source_review_agrees_all_528_cells':not retained_disagreements,
      'retained_raw_diet_comparison':raw_comparison,
      'researcher':signed['researcher_name'],'review_date':signed['review_date'],
      'signed_report_sha256':signed['report_sha256'],'current_report_sha256':sha(REPORT),
      'current_report_matches_signed_identity':sha(REPORT)==signed['report_sha256'],
      'researcher_review_status':review['status'],'report_diet_text':report_diet,
      'review_status_limitation':'Existing signed overall researcher review retained. No new approval or correction is registered; exact cell-specific accepted replacement literals not independently present.',
      'runtime_execution':execution,'runtime_state_diet_keys':runtime_diet_keys,
      'runtime_scope':'Only retained loaded state inspected; no new model loading, normalization, calculation or diagnostic run.'})
(OUT / f'input_{model_hash}.json').write_bytes(model_bytes)
after=snapshot()
changes=[{'path':p,'before':before.get(p),'after':after.get(p)} for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)]
write('protected_files_verification.json',{'before':before,'after':after,'changed':changes,
      'all_existing_regional_files_unchanged':not changes,'write_scope':str(OUT),
      'note':'Concurrent owner edits, if any, are reported as observed differences, not attributed to this agent.'})
result={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'region':'LME_047',
        'selected_model_id':MID,'selected_path':M.relative_to(ROOT).as_posix(),
        'status':'normalized-needs-owner-action','canonical_mutation_permitted':False,
        'model_before_sha256':model_hash,'model_after_sha256':sha(M),
        'source_supplement_sha256':sha(S),'source_cell_comparisons':528,
        'exact_decimal_differences':91,'affected_consumers':[s['consumer_id'] for s in sums if s.get('changed_source_cells',0)],
        'normalization_confirmed_by':'All 528 original S3 XML numeric cells; 91 differing cells match normalized original columns within 1e-12; retained exact comparison and migration/history corroborate.',
        'accepted_context':'Researcher Ido Carmel, review 2026-10-01, signed DOCX says Diet Sums – only rounding errors. Preserve accepted context and owner control; no source restoration attempted.',
        'changed_cells':[],'fresh_science':False,'reextraction_or_restoration':False,
        'owner_action':'LME047 is excluded from canonical/diet/report mutation. Root may notify existing validation owner with this evidence; any owner reconciliation must preserve signed decisions and historical input identities.',
        'unresolved':['Original converter receipt and native EwE export not retained; causal stage of historical normalization not established.','S3 does not provide a separate import row/vector; native canonical diet_imp=0 retained.','No independently documented cell-specific replacement correction beyond signed diet-sum rounding assessment.'] + (['Current DOCX hash differs from historical signed report identity; current DOCX still retains diet rounding statement. Existing review record is historical, not a fresh verification of current DOCX.'] if sha(REPORT)!=signed['report_sha256'] else []),
        'protected_files_unchanged':not changes,'observed_concurrent_changes':changes}
write('audit_result.json',result)
write('evidence_manifest.json',{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='evidence_manifest.json'})
print(json.dumps(result,ensure_ascii=False,indent=2))
