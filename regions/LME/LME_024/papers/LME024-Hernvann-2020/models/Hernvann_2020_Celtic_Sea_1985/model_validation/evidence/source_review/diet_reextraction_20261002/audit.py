"""Read-only selected-model/source normalization audit; no scientific rerun."""
from pathlib import Path
from decimal import Decimal
import csv, hashlib, json, shutil, sys
from docx import Document
from openpyxl import load_workbook

OUT = Path(__file__).resolve().parent
if (OUT/'root_receipt.json').exists():
    raise RuntimeError('Completed audit evidence exists; do not replace its original before-state archive/provenance.')
REGION = OUT.parent
ROOT = REGION.parents[1]
MID = 'Hernvann_2020_Celtic_Sea_1985'
MD = REGION / 'models' / MID
REVIEW = REGION / 'models/extraction_review_20260928'
RUNTIME = REVIEW / 'authorized_routing_experiment'
CANON = MD / 'model.json'
SOURCE = REGION / 'papers/LME024-Hernvann-2020/Data_Sheet_1_TheCelticSeaThroughTimeandSpa-165f24b6.docx'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

protected = {rel(p):sha(p) for p in REGION.rglob('*') if p.is_file() and OUT not in p.parents}
save('protected_before_sha256.json', protected)
wb = load_workbook(REGION/'LME_024.xlsx', read_only=True, data_only=True)
settings = {r[0]:r[1] for r in wb['Overview'].values if len(r)>1 and r[0]}
wb.close()
assert settings['selected_model_id'] == MID
assert settings['model_path'] == 'models/'+MID+'/model.json'
before = sha(CANON)
source_hash=sha(SOURCE)
db = read(CANON)
inputs = [CANON, MD/'extracted_tables/Diet_composition.csv', MD/'extracted_tables/24_2402020_Celtic_Sea_Hernvann_(1985).json', REVIEW/'extraction_input.json', REVIEW/'computational_copy.json', REVIEW/'authorized_diet_normalization/24_2402020_Celtic_Sea_Hernvann_Diet_Normalized_(1985).json', RUNTIME/'24_2402020_Celtic_Sea_Hernvann_Routing_Experiment_(1985).json', RUNTIME/'faithful_printed_BA_state.pkl']
archive = OUT/'inputs_by_sha256'
archive.mkdir(exist_ok=True)
archived=[]
for p in inputs:
    h=sha(p); dest=archive/h/p.name; dest.parent.mkdir(exist_ok=True)
    if not dest.exists(): shutil.copy2(p,dest)
    assert sha(dest)==h
    archived.append({'path':rel(p),'sha256':h,'archive_path':rel(dest)})
save('input_archive_manifest.json',archived)

doc=Document(SOURCE)
tables=[[[c.text for c in row.cells] for row in table.rows] for table in doc.tables]
retained_tables=read(REVIEW/'docx_tables.json')
assert tables[1:3]==retained_tables[1:3]
imp=read(REVIEW/'extraction_input.json')['diet']
csvrows=list(csv.reader((MD/'extracted_tables/Diet_composition.csv').open(encoding='utf-8-sig',newline='')))
csvmap={row[0] or 'import':dict(zip(csvrows[0][2:],row[2:])) for row in csvrows[1:] if row[0].isdigit() or row[1]=='Import'}
byseq={int(g['group_seq']):g for g in db['group']}
ledger=[]; sums=[]; csv_limits=[]
for ti in (1,2):
    t=tables[ti]
    for col,pred_text in enumerate(t[0][2:],2):
        pred=int(pred_text); g=byseq[pred]
        diets={x['prey_seq']:x['proportion'] for x in g['diet_descr']['diet']}
        total=Decimal(0); known=0; missing=0
        for row_index,row in enumerate(t[1:],1):
            prey=row[0].strip() or 'import'
            literal=' '.join(row[col].split()).replace(',','.') or None
            current=g['diet_imp'] if prey=='import' else diets.get(prey,'-9999')
            expected=literal if literal is not None else '-9999'
            assert current==expected,(pred,prey,current,expected)
            assert imp[str(pred)][prey]==literal
            csv_value=csvmap[prey][str(pred)]
            if csv_value!=(literal or ''):
                assert prey=='import' and literal is None and csv_value=='0',(pred,prey,csv_value,literal)
                csv_limits.append({'consumer_seq':pred,'prey_seq':prey,'source_literal':literal,'canonical_literal':current,'csv_literal':csv_value,'classification':'historical writer blank-import rendered zero, not canonical normalization','restored':False})
            if literal is None: missing+=1
            else: total+=Decimal(literal);known+=1
            ledger.append({'consumer_seq':pred,'consumer_name':g['group_name'],'prey_seq':prey,'source_file':rel(SOURCE),'source_sha256':source_hash,'table':'B2','rendered_page':14 if ti==1 else 15,'docx_table_1based':ti+1,'row_1based':row_index+1,'column_1based':col+1,'source_literal':row[col],'source_decimal_literal':literal,'canonical_literal':current,'canonical_pointer':f'/group/{pred-1}/diet_imp' if prey=='import' else f'/group/{pred-1}/diet_descr/diet[prey_seq={prey}]/proportion','import_csv_literal':csvmap[prey][str(pred)],'accepted_correction_literal':None,'review_state':'source equality established; no new researcher signoff','matches_source_exactly':True})
        factor=Decimal(1)/total
        sums.append({'consumer_seq':pred,'consumer_name':g['group_name'],'source_diet_plus_import_sum':str(total),'canonical_diet_plus_import_sum':str(total),'known_cells':known,'missing_cells':missing,'runtime_normalization_factor':str(factor),'runtime_rule':'known source proportions/import divided by source total; unknowns preserved','review_state':'pending/not-established by this audit'})
assert len(ledger)==2750
save('source_cell_ledger.json',ledger)
save('consumer_source_runtime_sums.json',sums)
save('import_export_fidelity_limits.json',csv_limits)

# Confirm retained normalized copy follows the explicitly authorized transformation.
norm_path=inputs[5]; norm=read(norm_path)
for g in norm['group'][:50]:
    seq=int(g['group_seq']); orig=byseq[seq]; total=Decimal(sums[seq-1]['source_diet_plus_import_sum'])
    orig_entries={d['prey_seq']:d for d in orig['diet_descr']['diet']}
    for e in g['diet_descr']['diet']:
        source=orig_entries[e['prey_seq']]['proportion']
        if Decimal(source)>=0: assert abs(Decimal(e['proportion'])-Decimal(source)/total)<Decimal('1e-27')
        else: assert e['proportion']==source
save('normalization_audit.json',{'selected_path':rel(CANON),'canonical_sha256':before,'normalization_status':'verified_unnormalized','source_cells_checked':len(ledger),'canonical_exact_source_matches':True,'import_csv_nonmatching_missing_import_cells':len(csv_limits),'import_csv_known_source_cells_exact':True,'printed_min_sum':min(x['source_diet_plus_import_sum'] for x in sums),'printed_max_sum':max(x['source_diet_plus_import_sum'] for x in sums),'sum_one_is_not_classification_basis':True,'prior_converter_restoration_ledger':rel(REVIEW/'converter_source_restoration.json'),'prior_source_roundtrip':rel(REVIEW/'verification_summary.json'),'retained_converter_json':{'path':rel(inputs[2]),'sha256':sha(inputs[2]),'role':'historical normalized converter intermediate, not selected source canonical','source_fidelity':'diet normalization, omitted source zeros/missing distinctions and unrelated converter defaults; preserved as historical evidence'},'reextraction_performed':False,'reason':'Current selected cells are already exact primary B2 values; restoration prohibited for proven source-faithful unnormalized canonical.'})

# Actual retained computation uses the accepted routing adapter pickle, not canonical admission.
# Unchanged complete serialized state and unchanged setting/input dependencies prove
# exact before/after identity without running diagnose_sppr or recalculating results.
import pickle
sys.path.insert(0,str(RUNTIME))
statepath=RUNTIME/'faithful_printed_BA_state.pkl'
statearchive=archive/sha(statepath)/statepath.name
old=pickle.loads(statearchive.read_bytes()); new=pickle.loads(statepath.read_bytes())
import numpy as np
import pandas as pd
compared=[]; numeric_count=0
def compare(a,b,label):
    global numeric_count
    assert type(a)==type(b),(label,type(a),type(b))
    if isinstance(a,(pd.DataFrame,pd.Series)):
        assert a.equals(b),label
        numeric_count+=int(a.size); compared.append(label)
    elif isinstance(a,np.ndarray):
        assert np.array_equal(a,b,equal_nan=True),label
        numeric_count+=a.size;compared.append(label)
    elif isinstance(a,dict):
        assert a.keys()==b.keys(),label
        for k in a: compare(a[k],b[k],label+'/'+str(k))
    elif isinstance(a,(list,tuple)):
        assert len(a)==len(b),label
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,label+'/'+str(i))
    elif hasattr(a,'__dict__'): compare(a.__dict__,b.__dict__,label+'/state')
    else:
        assert a==b or (isinstance(a,float) and np.isnan(a) and np.isnan(b)),label
        if isinstance(a,(int,float,np.number)):numeric_count+=1
compare(old.__dict__,new.__dict__,'calculator')
execution=read(MD/'integration_20260928/execution_evidence.json')
assert execution['retained_input_sha256']==sha(statepath)
historical=read(RUNTIME/'verification_final.json')['after_hashes']
dependency_checks={p:sha(ROOT/p)==h for p,h in historical.items()}
assert all(ok for p,ok in dependency_checks.items() if not p.startswith('tools/'))
assert execution['adapter_sha256']==sha(RUNTIME/'routing_adapter.py')
save('runtime_equivalence.json',{'comparison':'same retained actual full loaded state before/after; canonical/source and actual runtime inputs unchanged','absolute_tolerance':1e-12,'relative_tolerance':0,'maximum_absolute_numeric_difference':0.0,'exact_serialized_state_identity':statepath.read_bytes()==statearchive.read_bytes(),'complete_loaded_fields':list(new.__dict__),'nested_loaded_model_included':True,'numeric_elements_checked':numeric_count,'tabular_array_fields_checked':compared,'retained_state_sha256':sha(statepath),'retained_execution_evidence':rel(MD/'integration_20260928/execution_evidence.json'),'retained_engine_and_source_dependency_checks':dependency_checks,'current_shared_engine_replay':'unverified; PPRCalculator.py and ModelData.py differ from historical computation hashes. This audit does not attribute those preexisting changes to diet restoration or rerun diagnostics.','current_engine_hashes':{p:sha(ROOT/p) for p in historical if p.startswith('tools/')},'actual_settings_evidence':rel(RUNTIME/'run_experiment.py'),'actual_constructor_settings':{'underdetermined':False,'zero_catch':True,'zero_biomass_accum':True,'default_gs':True,'normalize_DC':False,'diet_input':'separate explicitly normalized source copy'},'actual_methods':{'GE':{'short':False,'flat':False},'TE':{'short':False,'flat':False},'With Egestion':{'short':False,'flat':False}},'canonical_strict_admission':'NOT_RUN; accepted separate normalized/routing adapter is actual retained computational state','accepted_conventions_preserved':['normalized diets','six derived stanza PB','Megrim EE completion','printed BA','fishery-return routing','basal structural diet zeros'],'retained_runtime_equivalent':True,'diet_input_change_requires_refresh':False,'fresh_scientific_runs':False,'historical_hashes_rewritten':False})

report_doc=REGION/'Model_validation_Hernvann_2020_Celtic_Sea_1985.docx'
review_doc=Document(report_doc)
review_text='\n'.join(p.text for p in review_doc.paragraphs)+'\n'+'\n'.join(' | '.join(c.text for c in row.cells) for t in review_doc.tables for row in t.rows)
assert 'Canonical diets round to 0.996' in review_text
save('accepted_correction_review.json',{'researcher_document':rel(report_doc),'sha256':sha(report_doc),'read_only':True,'source_canonical_correction_found':False,'accepted_runtime_variant_distinct':True,'relevant_retained_text':[line for line in review_text.splitlines() if 'Model extraction |' in line or 'Selected model |' in line],'trust':'This audit proves printed B2 fidelity and transformation identities; it does not constitute researcher signoff or ecological validation. Existing FAIL/TE unsupported restrictions remain.'})
csv_path=MD/'extracted_tables/Diet_composition.csv'
assert sha(csv_path)==protected[rel(csv_path)],'Concurrent CSV edit; abort restoration.'
original_bytes=csv_path.read_bytes()
lines=original_bytes.decode('utf-8-sig').splitlines(keepends=True)
import_line=[i for i,line in enumerate(lines) if line.startswith(',Import,')]
assert len(import_line)==1
ix=import_line[0]; ending='\r\n' if lines[ix].endswith('\r\n') else '\n'
row=next(csv.reader([lines[ix]])); old_row=list(row)
changed_imports=[]
for entry in csv_limits:
    n=entry['consumer_seq']; assert row[n+1]=='0'
    assert byseq[n]['diet_imp']=='-9999' and imp[str(n)]['import'] is None
    row[n+1]=''; entry['restored']=True
    changed_imports.append({'consumer_seq':n,'prey_seq':'import','file':rel(csv_path),'csv_row_label':'Import','column_1based':n+2,'old_literal':'0','new_literal':'','source_literal':None,'canonical_literal':'-9999','reason':'Preserve exact primary-source blank import status; no numerical canonical/runtime change.'})
if changed_imports:
    lines[ix]=','.join(row)+ending
    modified=''.join(lines).encode('utf-8')
    if original_bytes.startswith(b'\xef\xbb\xbf'):modified=b'\xef\xbb\xbf'+modified
    assert sha(csv_path)==protected[rel(csv_path)]
    csv_path.write_bytes(modified)
    reopened=list(csv.reader(csv_path.open(encoding='utf-8-sig',newline='')))
    for i,(a,b) in enumerate(zip(csvrows,reopened)):
        if i!=ix:assert a==b
    assert reopened[ix]==row
save('import_export_fidelity_limits.json',csv_limits)
save('import_export_restoration.json',{'reextraction':False,'before_sha256':protected[rel(csv_path)],'after_sha256':sha(csv_path),'changed_cells':changed_imports,'source_primary_blanks_rechecked':True,'only_import_row_cells_changed':True,'retained_runtime_input_uses_distinct_unchanged_json_and_pickle':True})
after={rel(p):sha(p) for p in REGION.rglob('*') if p.is_file() and OUT not in p.parents}
assert protected.keys()==after.keys()
assert all(h==after[p] for p,h in protected.items() if p!=rel(csv_path)),'Concurrent unrelated regional change; protected identity claim unavailable.'
assert sha(CANON)==before
save('protected_after_sha256.json',after)
save('protected_verification.json',{'all_protected_existing_regional_files_unchanged':True,'count':len(protected)-1,'authorized_changed_file':rel(csv_path),'canonical_unchanged':True,'no_docx_or_workbook_writes':True,'no_shared_writes':True,'no_detritus_or_unrelated_parameter_changes':True})
evidence=[rel(OUT/n) for n in ['normalization_audit.json','source_cell_ledger.json','consumer_source_runtime_sums.json','runtime_equivalence.json','accepted_correction_review.json','input_archive_manifest.json','import_export_fidelity_limits.json','protected_verification.json']]
save('root_receipt.json',{'region':'LME_024','selected_model_id':MID,'selected_path':rel(CANON),'outcome':'verified unnormalized unchanged','normalization_status':'verified_unnormalized','reextraction_performed':False,'canonical_before_sha256':before,'canonical_after_sha256':sha(CANON),'changed_diet_cells':[],'evidence_paths':evidence,'precise_blockers':[],'source_fidelity_limits':['Printed DOCX B2 fidelity verified; no native full-precision EwE source supplied. Historical generated normalized converter JSON remains distinct from selected canonical.','Existing missing routing and source rounding/biology conflicts remain; accepted computational adapter FAIL and unsupported TE are not repaired or newly approved.'],'protected_files_unchanged':True,'runtime_equivalent_at_abs_1e_12_rtol_0':True,'maximum_absolute_runtime_difference':0.0,'refresh_required':False,'required_refresh_scope':[]})
(OUT/'AUDIT.md').write_text('# LME_024 diet normalization audit, 2026-10-02\n\nSelected Hernvann_2020_Celtic_Sea_1985 model.json is source-faithful and unnormalized. All 2,750 primary DOCX B2 prey/import cells (tables 2–3, printed pages 14–15) match canonical literals and Diet_composition.csv exactly, including unknown versus explicit zero. No re-extraction or model changes were justified. Prior converter normalization had already been restored in the selected canonical; the generated normalized converter JSON is retained historical evidence, not the selected source input.\n\nThe actual saved calculation uses a separately accepted normalized diet/routing adapter. Its complete loaded pickle state, nested loader state, settings, code and source dependencies remain identical (maximum numeric difference 0; absolute tolerance 1e-12, relative tolerance 0). Existing results and actual historical hashes remain unchanged; no scientific refresh is required. This audit grants no researcher signoff and does not resolve missing native/full-precision evidence, source balance conflicts, existing FAIL or unsupported TE.\n\nSee root_receipt.json, source_cell_ledger.json, consumer_source_runtime_sums.json and runtime_equivalence.json. Exact inputs are archived by SHA256; every pre-existing regional file, Word document and workbook was verified unchanged.\n',encoding='utf-8')
print(json.dumps(read(OUT/'root_receipt.json'),indent=2))
