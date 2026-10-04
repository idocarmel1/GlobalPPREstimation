"""Read-only diet identity audit; writes evidence only in this directory."""
from pathlib import Path
from decimal import Decimal
import csv
import hashlib
import json
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
import pymupdf

OUT = Path(__file__).resolve().parent
REGION = OUT.parents[2]
ROOT = REGION.parents[1]
MODEL = OUT.parent / 'model.json'
MODEL_ID = OUT.parent.name
SOURCE = REGION / 'papers/HUM-2026'
TABLES = SOURCE / 'extracted/13_1_Chilean_Patagonia_1980'
COPIES = REGION / 'models/13_Humboldt_Current_13_1_Chilean_Patagonia_(1980)'
RUNTIME = REGION / 'models/regional_ge_integration_20260928'
PDF = next(SOURCE.glob('*.pdf'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rel(p):
    return p.relative_to(ROOT).as_posix()

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

before = {rel(p): sha(p) for p in REGION.rglob('*') if p.is_file() and OUT not in p.parents}
model_before = sha(MODEL)
shutil.copyfile(MODEL, OUT / 'selected_model_original.json')
assert sha(OUT / 'selected_model_original.json') == model_before
model = read(MODEL)
groups = {str(g['group_seq']): g for g in model['group']}
rows = list(csv.reader((TABLES / 'Diet_composition.csv').open(encoding='utf-8-sig', newline='')))
table = {r[0] if r[0] else r[1]: r for r in rows[1:]}

# Character positions resolve PDF words spanning invisible blank columns.
# Coordinates are PDF points on page 7, checked against retained page image.
xs = [134.871,168.26285,201.65472,235.04659,268.43845,301.82968,
      335.22156,368.61340,401.94852,435.34036,468.73221,502.12411,535.51532]
ys = [98.90059,107.51762,116.07854,124.63882,133.19974,141.76003,
      150.32031,158.88123,167.44151,176.05917,184.61946,193.17975,
      201.74066,210.30095,218.86186,227.42215,236.03917]
paper_cells = {}
with pymupdf.open(PDF) as doc:
    page = doc[6]
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                chars = span['chars']
                text = ''.join(c['c'] for c in chars)
                for match in re.finditer(r'\d\.\d{3}', text):
                    cs = chars[match.start():match.end()]
                    x, y = cs[0]['bbox'][:2]
                    if not 90 < y < 247:
                        continue
                    ci = min(range(13), key=lambda i: abs(xs[i] - x))
                    ri = min(range(17), key=lambda i: abs(ys[i] - y))
                    assert abs(xs[ci] - x) < .01 and abs(ys[ri] - y) < .01
                    prey = str(ri + 1) if ri < 15 else ['Import', 'Sum'][ri - 15]
                    key = (str(ci + 2), prey)
                    assert key not in paper_cells
                    paper_cells[key] = {'literal': match.group(), 'bbox': [cs[0]['bbox'][0], cs[0]['bbox'][1], cs[-1]['bbox'][2], cs[-1]['bbox'][3]]}
assert len(paper_cells) == 63  # 46 prey cells + 4 imports + 13 printed totals

ledger = []
source_sums = []
precision = []
for consumer in map(str, range(2, 15)):
    gi = int(consumer) - 1
    g = groups[consumer]
    entries = {str(e['prey_seq']): (ei, e['proportion']) for ei, e in enumerate(g['diet_descr']['diet'])}
    ci = rows[0].index(consumer)
    subtotal = Decimal(0)
    for prey in [*map(str, range(1, 16)), 'Import']:
        printed = paper_cells.get((consumer, prey), {})
        source_literal = printed.get('literal', '')
        csv_literal = table[prey][ci]
        if prey == 'Import':
            canonical_literal = g['diet_imp']
            pointer = f'/group/{gi}/diet_imp'
        else:
            item = entries.get(prey)
            canonical_literal = item[1] if item else None
            pointer = f'/group/{gi}/diet_descr/diet/{item[0]}/proportion' if item else None
        if source_literal:
            assert Decimal(source_literal) == Decimal(csv_literal) == Decimal(canonical_literal), (consumer, prey)
            subtotal += Decimal(source_literal)
            if prey != 'Import':
                assert source_literal == csv_literal == canonical_literal
            elif source_literal != canonical_literal:
                precision.append({'consumer': consumer, 'source': source_literal, 'canonical': canonical_literal, 'reason': 'Trailing zero omitted by retained import writer; numerically exact, not normalization.'})
        else:
            assert csv_literal == ''
            if prey == 'Import':
                assert canonical_literal == '-9999'
            else:
                assert canonical_literal in [None, '0']
        ledger.append({'consumer_seq': consumer, 'consumer_name': g['group_name'], 'prey_seq': prey,
                       'source_file': rel(PDF), 'pdf_page': 7, 'printed_page': 7, 'table': 4,
                       'source_row': prey, 'source_column': consumer, 'source_bbox_points': printed.get('bbox'),
                       'source_literal': source_literal, 'import_file': rel(TABLES / 'Diet_composition.csv'),
                       'csv_row': next(i+1 for i,r in enumerate(rows) if r is table[prey]), 'csv_column': ci+1,
                       'retained_import_literal': csv_literal, 'canonical_pointer': pointer,
                       'canonical_literal': canonical_literal, 'accepted_corrected_literal': None,
                       'interpretation': 'source-stated exact numeric match' if source_literal else
                       ('unknown import retained as -9999' if prey == 'Import' else 'source blank; sparse absent or retained detritus structural zero')})
    canonical_sum = sum(Decimal(v) for _,v in entries.values()) + (Decimal(g['diet_imp']) if g['diet_imp'] != '-9999' else 0)
    assert canonical_sum == subtotal
    source_sums.append({'consumer_seq': consumer, 'consumer_name': g['group_name'], 'diet_plus_stated_import_sum': str(subtotal),
                        'canonical_sum': str(canonical_sum), 'printed_sum_literal': paper_cells[(consumer,'Sum')]['literal'],
                        'import_unknown': g['diet_imp'] == '-9999', 'review_state': 'not-established',
                        'runtime_normalization_allowed': True})

copy_checks = []
for p in [MODEL, COPIES/'model.json', next((COPIES/'extracted_tables').glob('13_Humboldt*.json')), next(TABLES.glob('13_Humboldt*.json'))]:
    d = read(p)
    for a,b in zip(model['group'],d['group']):
        assert a['group_seq'] == b['group_seq'] and a['diet_imp'] == b['diet_imp'] and a['diet_descr'] == b['diet_descr']
    if 'source_tables' in d:
        assert d['source_tables']['Diet_composition.csv'] == rows
    copy_checks.append({'path': rel(p), 'sha256': sha(p), 'diet_and_import_exactly_equal_selected': True})
for p in [TABLES/'Diet_composition.csv', COPIES/'extracted_tables/Diet_composition.csv']:
    assert list(csv.reader(p.open(encoding='utf-8-sig',newline=''))) == rows
    copy_checks.append({'path': rel(p), 'sha256': sha(p), 'diet_import_table_exactly_equal_retained': True})

raw = next((SOURCE/'extracted/work/raw-converter-13_1').glob('*.json'))
raw_sea = next(g for g in read(raw)['group'] if g['group_seq']=='14')
runtime_rows = list(csv.reader((RUNTIME/'runtime_diet.csv').open(encoding='utf-8-sig')))
runtime_map = {r[0]:dict(zip(runtime_rows[0][1:],r[1:])) for r in runtime_rows[1:]}
runtime_ledger = []
for c in map(str,range(2,15)):
    source_total = Decimal(next(s['canonical_sum'] for s in source_sums if s['consumer_seq']==c))
    for prey in [*map(str,range(1,16)), 'Import']:
        source_value = Decimal(paper_cells.get((c,prey),{}).get('literal','0'))
        runtime_value = runtime_map[c]['16' if prey=='Import' else prey]
        expected = source_value/source_total if c=='14' else source_value
        assert abs(Decimal(runtime_value)-expected) < Decimal('1e-15')
        runtime_ledger.append({'consumer_seq': c,'prey_seq': prey,'source_value':str(source_value),'historical_runtime_value':runtime_value,
                               'runtime_factor': '1/1.002' if c=='14' else '1', 'changed_from_source': abs(Decimal(runtime_value)-source_value)>Decimal('1e-15')})

docx = REGION / f'Model_validation_{MODEL_ID}.docx'
with zipfile.ZipFile(docx) as z:
    xml = ET.fromstring(z.read('word/document.xml'))
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
docx_findings = [' '.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in xml.findall('.//w:p',ns)]
docx_findings = [s for s in docx_findings if 'normaliz' in s.lower() or 'diet sum' in s.lower()]
assert any('1.002 is preserved' in s for s in docx_findings)
after = {p:sha(ROOT/p) for p in before}
changes = [p for p in before if before[p] != after[p]]
assert not changes, changes
assert sha(MODEL) == model_before
save('protected_files_verification.json', {'before':before,'after':after,'changed_files':changes,'all_original_regional_files_unchanged':True})
save('cell_ledger.json',ledger)
save('consumer_sums.json',source_sums)
save('source_runtime_ledger.json', {'orientation':'consumer rows, prey columns; synthetic seq16 represents import', 'runtime_evidence':rel(RUNTIME/'runtime_diet.csv'), 'cells':runtime_ledger})
save('audit.json',{'schema_version':1,'run_id':'diet_reextraction_20261002_LME_013','unit_id':'LME_013','selected_model_id':MODEL_ID,
                   'status':'verified unnormalized unchanged','model_path':rel(MODEL),'before_model_sha256':model_before,'after_model_sha256':sha(MODEL),
                   'canonical_changed_cells':[],'source_canonical_copies':copy_checks,'source_pdf_sha256':sha(PDF),
                   'source_locators':'Neira et al., Progress in Oceanography 241 (2026) 103631, Table 4, PDF/printed page7; every nonblank cell independently compared using character coordinates and retained image.',
                   'cell_ledger_count':len(ledger),'stated_prey_cell_count':46,'stated_import_cell_count':4,
                   'review_state':'not-established; evidence of normalization status only, no scientific approval',
                   'source_precision_caveats':precision,'source_sum_discrepancy':'Sea lions printed Sum 1.000, sum of exact stated entries 1.002; canonical retains the entries, not printed total.',
                   'normalization_evidence':{'canonical_normalized':False,'historical_raw_converter_normalized':True,'raw_converter_path':rel(raw),'raw_converter_sha256':sha(raw),'raw_converter_sea_lion_import':raw_sea['diet_imp'],'source_preserving_adapter':rel(SOURCE/'extracted/work/preserve_database.py'),'adapter_run_in_this_audit':False,'historical_runtime_normalized':True,'runtime_factor_sea_lions':'1/1.002','runtime_options':read(RUNTIME/'runtime_verification.json')['constructor'],'runtime_normalization_allowed':True},
                   'accepted_researcher_evidence':{'docx_path':rel(docx),'docx_sha256':sha(docx),'read_only_excerpt':docx_findings,'accepted_input_verification':rel(REGION/f'validation_reports/{MODEL_ID}/accepted_input_verification.json'),'accepted_overrides_preserved':True},
                   'historical_runtime_inputs_sha256':read(RUNTIME/'runtime_verification.json')['canonical_sha256'],'historical_state_sha256_actual':sha(RUNTIME/'computational_state.json'),
                   'staleness':'No canonical identity change. Historical runtime/diagnostics retained with actual hashes; no freshness rewrite or calculation.',
                   'limitations':['Four printed import trailing zeros omitted in retained CSV/canonical strings; exact numeric values unchanged.','Source blanks and unknown import -9999 are distinguished from source-stated zero.','Referenced S1-S7 supplements remain absent; no new scientific validity claim.'],
                   'blockers':[],'protected_original_file_count':len(before),'protected_files_unchanged':True,'scientific_run_performed':False})

roles = {'audit':'audit.json','cell_ledger':'cell_ledger.json','consumer_sums':'consumer_sums.json','runtime_difference':'source_runtime_ledger.json','protection':'protected_files_verification.json','original_input':'selected_model_original.json','source_pdf':PDF,'source_import':TABLES/'Diet_composition.csv','historical_runtime':RUNTIME/'runtime_verification.json','source_adapter':SOURCE/'extracted/work/preserve_database.py','accepted_report':docx}
artifacts = []
import os
for role,p in roles.items():
    p = OUT/p if isinstance(p,str) else p
    artifacts.append({'role':role,'path':os.path.relpath(p,OUT).replace('\\','/'),'sha256':sha(p),'availability':'present'})
save('evidence-index.json',{'schema_version':1,'run_id':'diet_reextraction_20261002_LME_013','unit_id':'LME_013','region_id':'LME_013','methods':[],'model_id':MODEL_ID,'variant_id':'selected-source-canonical-unchanged','source_identity':{'doi':'10.1016/j.pocean.2025.103631','sha256':sha(PDF)},'computational_input_identity':{'sha256':model_before},'methods_options':{'audit_only':True,'calculator_run':False},'required_roles':list(roles),'artifacts':artifacts,'reconciliation':{'every_printed_diet_import_value_matches_canonical_numerically':True,'all_stated_prey_literals_match_exactly':True,'all_protected_regional_files_unchanged':True,'historical_runtime_factor_verified':True}})
print(json.dumps({'status':'verified unnormalized unchanged','sha256':model_before,'source_cells':50,'ledger_cells':len(ledger),'protected_files':len(before),'evidence':rel(OUT)},ensure_ascii=False))
