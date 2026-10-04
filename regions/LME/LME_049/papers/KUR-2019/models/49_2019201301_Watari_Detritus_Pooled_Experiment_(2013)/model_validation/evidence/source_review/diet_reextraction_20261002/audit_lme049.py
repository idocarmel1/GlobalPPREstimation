"""Read-only selected pooled-model diet audit. Writes only this evidence folder."""
from pathlib import Path
from decimal import Decimal
import csv, hashlib, json, sys, zipfile
from xml.etree import ElementTree as ET
import openpyxl

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
REG = ROOT / 'regions/LME_049'
OUT = Path(__file__).resolve().parent
MID = '49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'
MODEL = REG / 'models' / MID
PARENT = REG / 'models/49_20192013_Western_North_Pacific_Watari_(2013)'
EV = MODEL / 'evidence'
RUNTIME = REG / 'models/regional_ge_integration_20260928'
CANON = MODEL / 'model.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

def rel(path):
    return path.relative_to(ROOT).as_posix()

protected = {rel(p): sha(p) for p in REG.rglob('*') if p.is_file() and OUT not in p.parents}
dump('protected_before_sha256.json', protected)
before = sha(CANON)
model = read(CANON)
frozen = read(EV / 'source_model_frozen.json')
manifest = read(EV / 'derivation_manifest.json')
assert before == manifest['derived_model_sha256']
assert sha(EV / 'source_model_frozen.json') == manifest['source_model_sha256']
assert sha(PARENT / 'model.json') == manifest['source_model_sha256']
pdf = REG / 'papers/KUR-2019/Watari-Ecosystemmodelingwestern-2019.pdf'
assert sha(pdf) == manifest['publication_sources'][0]['sha256']
source_cells = read(PARENT / 'extracted_tables/diet_source_cells.json')
assert len(source_cells) == 1435
source = {(int(x['predator_seq']), int(x['prey_seq'])): x for x in source_cells}
rows = list(csv.reader((PARENT / 'extracted_tables/Diet_composition.csv').open(encoding='utf-8-sig', newline='')))
import_rows = {int(row[0]): row for row in rows[1:] if row[0].isdigit()}
assert len(import_rows) == 41
ledger = []
sums = []
for index, consumer in enumerate(model['group'][:35]):
    seq = int(consumer['group_seq'])
    original = frozen['group'][index]
    # Preserve every unrelated field, including diet_import sentinel and fates.
    assert {k:v for k,v in consumer.items() if k != 'diet_descr'} == {k:v for k,v in original.items() if k != 'diet_descr'}
    assert len(consumer['diet_descr']['diet']) == 39
    for prey in original['diet_descr']['diet']:
        p = int(prey['prey_seq'])
        literal = source[(seq,p)]['source_text']
        assert Decimal(literal) == Decimal(prey['proportion']) == Decimal(import_rows[p][seq+1])
    for prey_index, prey in enumerate(consumer['diet_descr']['diet']):
        p = int(prey['prey_seq'])
        components = [source[(seq,k)] for k in ([p] if p < 39 else [39,40,41])]
        adopted = original['diet_descr']['diet'][prey_index]['proportion'] if p < 39 else str(sum(Decimal(source[(seq,k)]['source_text']) for k in [39,40,41]))
        assert prey['proportion'] == adopted
        assert prey['detritus_fate'] == '-9999'
        ledger.append({'consumer_seq':seq,'consumer_name':consumer['group_name'],'prey_seq':p,
            'canonical_pointer':f'/group/{index}/diet_descr/diet/{prey_index}/proportion',
            'canonical_literal':prey['proportion'],'adopted_literal':adopted,
            'source_components':components,'source_pdf':rel(pdf),'source_pdf_sha256':sha(pdf),
            'retained_source_cell_ledger':rel(PARENT/'extracted_tables/diet_source_cells.json'),
            'accepted_correction': '2026-09-28 detritus-only pooling: exact decimal sum of source prey 39/40/41' if p == 39 else None,
            'accepted_decision_evidence':[rel(EV/'DECISIONS_AND_LIMITATIONS.md'),rel(REG/f'Model_validation_{MID}.docx')],
            'review_state':'pooling explicitly accepted; source rounding/import completeness not independently researcher verified'})
    raw = sum(Decimal(x['proportion']) for x in consumer['diet_descr']['diet'])
    old = sum(Decimal(x['proportion']) for x in original['diet_descr']['diet'])
    assert raw == old
    assert consumer['diet_imp'] == '-9999'
    sums.append({'consumer_seq':seq,'consumer_name':consumer['group_name'],
        'source_known_prey_sum':str(old),'canonical_known_prey_sum':str(raw),
        'source_import':'not supplied','canonical_import_literal':'-9999',
        'diet_plus_import_sum':'not established: source import missing',
        'runtime_import_default':0,'runtime_sum_expected':1,
        'runtime_normalization_factor_known_prey':str(Decimal(1)/raw) if abs(float(raw)-1)>0.001 else '1',
        'researcher_verification':'not established for rounding/import completeness; pooling accepted'})
assert len(ledger) == 1365
assert model['group'][35:38] == frozen['group'][35:38]
assert model['group'][38]['diet_descr'] is None
assert model['group'][38]['biomass'] == '44.12'
assert model['group'][38]['ee'] == '-9999'
assert model['group'][38]['habitat_area'] == '1.00'

# Historical canonical reconstruction is a source-faithful review view, not runtime output.
wb = openpyxl.load_workbook(EV/'canonical_reconstructed.xlsx', read_only=True, data_only=True)
table = list(wb['Diet composition'].values)
assert len(table) == 42
for item in ledger:
    assert Decimal(str(table[item['prey_seq']][item['consumer_seq']+1])) == Decimal(item['canonical_literal'])
assert all(v is None for v in table[-2][2:])
wb.close()

# Read researcher-edited DOCX without Office automation or modification.
report = REG / f'Model_validation_{MID}.docx'
with zipfile.ZipFile(report) as z:
    xml = ET.fromstring(z.read('word/document.xml'))
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
paragraphs = [''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in xml.findall('.//w:p',ns)]
relevant = [p for p in paragraphs if any(s in p.lower() for s in ['accepted pooling','retained loader','model — user selected','source and runtime'])]
assert any('Accepted pooling sums' in p for p in relevant)
dump('accepted_decisions.json', {'report':rel(report),'report_sha256':sha(report),'read_method':'OOXML read only',
    'verbatim_relevant_paragraphs':relevant,'decisions_file':rel(EV/'DECISIONS_AND_LIMITATIONS.md'),
    'decision_date':'2026-09-28','accepted_diet_change':'only detritus fractions 39/40/41 exact sum into pooled 39',
    'further_source_diet_overrides_found':False,'review_status':'pooling accepted; normalization review trust not established; runtime always allowed'})
dump('source_cell_ledger.json', ledger)
dump('consumer_source_sums.json', sums)

# Reconstruct with actual retained constructor and frozen executed engine; no SPPR rerun.
verification = read(RUNTIME/'runtime_verification.json')
assert verification['canonical_sha256'] == before
actual_input = RUNTIME/'input'/f'{MID}.json'
assert sha(actual_input) == before == verification['computational_input_sha256']
assert sha(RUNTIME/'computational_state.json') == verification['computational_state_sha256']
snapshot = RUNTIME/'executed_code'
assert sha(snapshot/'ModelData.py') == verification['engine_sha256']['ModelData.py']
assert sha(snapshot/'PPRCalculator.py') == verification['engine_sha256']['PPRCalculator.py']
sys.dont_write_bytecode = True
retained_utils = MODEL/'diagnostic_code/PPREstimation/utils.py'
assert sha(retained_utils) == sha(ROOT/'tools/scientific_code/PPREstimation/utils.py')
sys.path.insert(0,str(retained_utils.parent))
sys.path.insert(0,str(snapshot))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
from runtime_codec import encode
calculator = PPRCalculator.from_modeldata(ModelData(str(actual_input)), **verification['constructor'])
old_state = read(RUNTIME/'computational_state.json')
new_state = encode(vars(calculator))
differences = []
numeric_count = 0
max_abs = 0.0
def compare(a,b,path=''):
    global numeric_count,max_abs
    if isinstance(a,(float,int)) and not isinstance(a,bool) and isinstance(b,(float,int)) and not isinstance(b,bool):
        numeric_count += 1
        delta = abs(a-b)
        max_abs = max(max_abs,delta)
        if delta > 1e-12: differences.append({'path':path,'old':a,'new':b,'abs_difference':delta})
    elif isinstance(a,dict) and isinstance(b,dict):
        if a.keys()!=b.keys(): differences.append({'path':path,'reason':'dict keys differ'})
        for k in a.keys() & b.keys(): compare(a[k],b[k],path+'/'+str(k))
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b): differences.append({'path':path,'reason':'list lengths differ'})
        for k,(x,y) in enumerate(zip(a,b)): compare(x,y,path+'/'+str(k))
    elif a != b: differences.append({'path':path,'old':a,'new':b,'reason':'metadata or nonnumeric value differs'})
compare(old_state,new_state)
dump('reloaded_runtime_state.json',new_state)
runtime_record = {'canonical_before_sha256':before,'canonical_after_sha256':sha(CANON),
    'actual_retained_computational_input':rel(actual_input),'actual_retained_input_sha256':sha(actual_input),
    'historical_computational_state':rel(RUNTIME/'computational_state.json'),
    'historical_computational_state_sha256':sha(RUNTIME/'computational_state.json'),
    'fresh_reloaded_state_sha256':sha(OUT/'reloaded_runtime_state.json'),
    'actual_constructor':verification['constructor'],'engine_source':'retained executed_code exact hashes checked',
    'utility_dependency':{'path':rel(retained_utils),'sha256':sha(retained_utils),'note':'Integration snapshot omitted utils.py; retained original diagnostic copy and current utility exact hashes agree.'},
    'complete_calculator_state_compared':True,'numeric_values_compared':numeric_count,
    'tolerance':{'atol':1e-12,'rtol':0},'max_absolute_numeric_difference':max_abs,
    'different_values_beyond_tolerance':differences,'exact_encoded_state_equal':old_state==new_state,
    'runtime_equivalent':not differences,'scientific_refresh_required':bool(differences),
    'latest_human_refresh_exclusions':['biomass accumulation','predation'],
    'excluded_field_differences':[],
    'exclusion_application_note':'Complete state is exactly equal, so applying the later BA/predation exclusions gives the same no-refresh conclusion. Any later BA/predation differences must be recorded separately and must not trigger refresh.',
    'diagnostics_or_coefficients_rerun':False,'source_byte_change_triggers_refresh':False}
dump('runtime_comparison.json',runtime_record)

# Quantify the authorized separate runtime normalization, not canonical normalization.
changes = []
for item in ledger:
    seq,prey = item['consumer_seq'],item['prey_seq']
    runtime = float(calculator._DC.loc[seq,prey])
    raw = float(item['canonical_literal'])
    if runtime != raw:
        changes.append({'consumer_seq':seq,'prey_seq':prey,'canonical_literal':item['canonical_literal'],'runtime':runtime,'difference':runtime-raw})
dump('canonical_to_runtime_diet_changes.json',changes)
material_changes = [c for c in changes if abs(c['difference']) > 1e-12]
assert len(material_changes) == 83
assert {c['consumer_seq'] for c in material_changes} == {2,3,5,6,8}
for item in sums:
    seq = item['consumer_seq']
    item['actual_runtime_prey_plus_import_sum'] = float(calculator._DC.loc[seq].sum())
    item['actual_runtime_import_proportion'] = float(calculator._DC.loc[seq,40])
dump('consumer_source_sums.json',sums)
dump('normalization_proof.json',{'normalization_status':'verified unnormalized canonical; runtime-only normalization',
    'selected_path':rel(CANON),'all_1365_canonical_diet_literals_equal_exact_parent_or_accepted_decimal_pool':True,
    'all_1435_original_cells_match_retained_printed_source_and_import_rows':True,
    'all_1365_historical_canonical_reconstruction_cells_match':True,
    'selected_model_original_derivation_hash_unchanged':True,'source_import_missingness_preserved':True,
    'all_unrelated_consumer_fields_unchanged_from_frozen_source':True,'all_three_producer_records_unchanged':True,
    'diet_normalized_only_in_runtime_cells_beyond_abs_1e_12':len(material_changes),'runtime_normalized_consumer_ids':[2,3,5,6,8],
    'additional_float_roundoff_runtime_cells_within_abs_1e_12':len(changes)-len(material_changes),
    'retained_converter_history':rel(PARENT/'extracted_tables/converter_transformations_reversed.json'),
    'converter_intermediate_is_historical_normalized_evidence_not_selected_canonical':True,
    'raw_nonunit_prey_sums':{str(x['consumer_seq']):x['canonical_known_prey_sum'] for x in sums if Decimal(x['canonical_known_prey_sum'])!=1},
    'no_new_extraction_permitted_or_required':'Canonical is proven unnormalized; retained source cell evidence audited without new extraction.',
    'source_fidelity_limit':'Source import not supplied; no claim that known prey sum is complete diet-plus-import. Researcher accepted pooling and conditional runtime defaults, not author-confirmed missing inputs.'})

after_protected = {p:sha(ROOT/p) for p in protected}
protected_changed = {p:{'before':protected[p],'after':after_protected[p]} for p in protected if protected[p]!=after_protected[p]}
dump('protected_after_sha256.json',after_protected)
dump('protected_verification.json',{'files_checked':len(protected),'all_unchanged':not protected_changed,'changed':protected_changed,'region_originals_written':False})
assert sha(CANON) == before
assert not protected_changed
blockers = ['Source import proportions are missing; complete source diet-plus-import totals and researcher review of source rounding are not established. This does not block permitted runtime normalization.']
dump('root_receipt.json',{'region':'LME_049','selected_model_id':MID,'selected_path':rel(CANON),
    'outcome':'verified unnormalized unchanged','normalization_status':'verified canonical unnormalized by exact source/frozen parent and approved pooling comparisons',
    'reextraction_performed':False,'canonical_before_sha256':before,'canonical_after_sha256':sha(CANON),
    'changed_diet_cells':[],'evidence_paths':[rel(OUT/n) for n in ['normalization_proof.json','source_cell_ledger.json','consumer_source_sums.json','accepted_decisions.json','runtime_comparison.json','canonical_to_runtime_diet_changes.json','protected_verification.json']],
    'precise_blockers':blockers,'protected_files_unchanged':True,'scientific_refresh_required':runtime_record['scientific_refresh_required'],
    'runtime_comparison_tolerance':{'atol':1e-12,'rtol':0},'historical_result_hashes_preserved':True,
    'review_approval':False})
print(json.dumps({'outcome':'verified unnormalized unchanged','canonical_sha256':before,'diet_cells_checked':len(ledger),'runtime_only_changed_cells':len(changes),'runtime_comparison':runtime_record,'protected_file_count':len(protected)},ensure_ascii=False))
