"""Read-only HS_077 source/canonical/runtime diet audit; writes only this folder."""
from pathlib import Path
from decimal import Decimal
import csv, hashlib, json, shutil, zipfile, xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
REGION = OUT.parents[1]
ROOT = REGION.parents[1]
MODEL_ID = '077HS_1_Eastern_tropical_Pacific_(1993-1997)'
SELECTED = REGION / 'models' / MODEL_ID / 'model.json'
SOURCE_DIR = REGION / 'papers/ETP-2003/extracted'
WORK = SOURCE_DIR / 'work'
EXTRACT = SOURCE_DIR / 'HS_077_1_Eastern_tropical_Pacific_1993-1997'
COPY_DIR = REGION / 'models' / (MODEL_ID + '_c4937140')
HIST = REGION / 'evidence/2026-09-28_integration_audit'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def entries(g):
    v = (g.get('diet_descr') or {}).get('diet', [])
    if isinstance(v, dict): return [v]
    return v if isinstance(v, list) else []
def val(g, prey):
    if prey == 40: return g.get('diet_imp')
    return next((e.get('proportion') for e in entries(g) if int(e['prey_seq']) == prey), None)
def known(v): return v is not None and str(v) != '-9999'
def matrix(d):
    return {(int(i), int(c)):d['data'][ri][ci] for ri,i in enumerate(d['index']) for ci,c in enumerate(d['columns'])}

protected = {rel(p):sha(p) for p in REGION.rglob('*') if p.is_file() and OUT not in p.parents and 'raw' not in p.relative_to(REGION).parts}
prov = read(WORK/'provenance.json')
source = {(d['consumer'],d['prey']):d for d in prov['diet']}
assert len(source) == 315
pdf = REGION/'papers/ETP-2003/Olson_Watters_2003_ETP-c037fcbc.pdf'
assert sha(pdf) == prov['source_sha256']
models = [SELECTED, COPY_DIR/'model.json', COPY_DIR/'extracted_tables'/f'{MODEL_ID}.json', EXTRACT/f'{MODEL_ID}.json', HIST/'computational_input'/f'{MODEL_ID}.json']
comparisons = []
for i,p in enumerate(models):
    j=read(p); by={int(g['group_seq']):g for g in j['group']}
    mismatches = [{**d,'canonical_literal':val(by[c],q)} for (c,q),d in source.items() if val(by[c],q) != d['value']]
    comparisons.append({'path':rel(p),'sha256_before':sha(p),'populated_source_cells_checked':315,'exact_literal_mismatches':mismatches,'group_count':len(by)})
    assert not mismatches, (p,mismatches)
    if i==0: selected=j; groups=by
    snapshot=OUT/'input_snapshots'/str(i)
    snapshot.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(p,snapshot/p.name)

rawpath=WORK/'raw_converter'/('HS_077_Pacific_Eastern_Central_high_seas_HS_077_1_Eastern_tropical_Pacific_(1993-1997).json')
rawgroups={int(g['group_seq']):g for g in read(rawpath)['group']}
rawchanges=[]
for (c,q),d in source.items():
    v=val(rawgroups[c],q)
    if known(v) and Decimal(str(v)) != Decimal(d['value']):
        rawchanges.append({'consumer':c,'prey':q,'source_literal':d['value'],'raw_converter_literal':v})

csv_paths = [EXTRACT/'Diet_composition.csv',COPY_DIR/'extracted_tables/Diet_composition.csv']
csv_info=[]
csvcells={}
for p in csv_paths:
    rows=list(csv.reader(p.open(encoding='utf-8-sig',newline='')))
    lookup={}
    for rn,row in enumerate(rows[1:],2):
        q=int(row[0]) if row[0].isdigit() else 40 if row[1]=='Import' else None
        if q is not None:
            for col,c in enumerate(rows[0][2:],2):lookup[(int(c),q)]=(row[col],rn,col+1)
    mismatches=[{'consumer':c,'prey':q,'source':d['value'],'csv':lookup[(c,q)][0]} for (c,q),d in source.items() if lookup[(c,q)][0]!=d['value']]
    assert not mismatches
    csv_info.append({'path':rel(p),'sha256':sha(p),'populated_source_cells_checked':315,'exact_literal_mismatches':mismatches})
    if not csvcells:csvcells=lookup

runtime=read(HIST/'loaded_state.json'); pre=read(HIST/'pre_constructor_state.json')
rt=matrix(runtime['DC']); precells=matrix(pre['DC'])
ledger=[]
for c in range(1,37):
    for q in range(1,41):
        d=source.get((c,q)); v=val(groups[c],q)
        idx=next((i for i,e in enumerate(entries(groups[c])) if int(e['prey_seq'])==q),None)
        pointer=f'/group/{c-1}/diet_imp' if q==40 else f'/group/{c-1}/diet_descr/diet/{idx}/proportion' if idx is not None else None
        cv,rn,cn=csvcells[(c,q)]
        ledger.append({'consumer':c,'consumer_name':groups[c]['group_name'],'prey':q,'source_pdf':rel(pdf),'table':'3a','pdf_page':28 if c<=18 else 29,'printed_page':158 if c<=18 else 159,'source_coordinate':f'prey row {q}; predator column {c}', 'source_bbox':d['bbox'] if d else None,'printed_literal':d['value'] if d else None,'printed_status':'printed number' if d else 'blank','canonical_pointer':pointer,'canonical_literal':v,'retained_import_csv':rel(csv_paths[0]),'csv_row':rn,'csv_column':cn,'csv_literal':cv,'accepted_corrected_literal':None,'review_state':'normalization audit only; no fresh correction adopted','runtime_retained_value':rt.get((c,q)), 'source_blank_import_encoding':q==40 and d is None and v=='0'})
write('cell_ledger.json',ledger)

sums=[]
for c,g in groups.items():
    if c>36:continue
    printed_sum=sum((Decimal(d['value']) for (cc,q),d in source.items() if cc==c),Decimal(0))
    canonical_diet=sum((Decimal(str(e['proportion'])) for e in entries(g) if known(e.get('proportion'))),Decimal(0))
    imported=Decimal(g['diet_imp']) if known(g.get('diet_imp')) else None
    total=canonical_diet+(imported or Decimal(0))
    assert total==printed_sum
    rtvalues=[rt.get((c,q)) for q in runtime['DC']['columns']]
    rt_sum=sum(x for x in rtvalues if x is not None)
    changed=[q for q in range(1,41) if precells.get((c,q)) != rt.get((c,q))]
    sums.append({'consumer':c,'name':g['group_name'],'source_populated_cells_sum':str(printed_sum),'canonical_known_diet_sum':str(canonical_diet),'canonical_import_literal':g['diet_imp'],'canonical_known_diet_plus_import_sum':str(total),'source_blank_import':(c,40) not in source,'source_blank_diet_cells':40-sum(1 for cc,q in source if cc==c),'canonical_unknown_diet_prey':[e['prey_seq'] for e in entries(g) if not known(e.get('proportion'))],'retained_runtime_sum_float':rt_sum,'retained_runtime_changed_prey_ids':changed,'runtime_normalization_factor_exact_if_changed':str(Decimal(1)/total) if changed else None,'factor_basis':'analytic reciprocal of exact source known-cell sum; explanatory only, not used to restore any value','review_status':'not established as scientifically complete; unchanged source retained','runtime_permission':'always allowed per current human steering'})
write('consumer_sums.json',sums)

docx=REGION/f'Model_validation_{MODEL_ID}.docx'
with zipfile.ZipFile(docx) as z:
    e=ET.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in e.findall('.//w:p',ns)]
docx_evidence=[p for p in paragraphs if any(k in p.lower() for k in ['diet','accepted loaded','source values','researcher: calculation'])]
write('accepted_report_readonly.json',{'path':rel(docx),'sha256':sha(docx),'read_method':'ZIP XML only; no Word automation or save','relevant_paragraphs':docx_evidence,'accepted_diet_correction_found':False,'runtime_acceptance_found':any('accepted historical runtime normalizes' in p.lower() for p in paragraphs)})

after={p:sha(ROOT/p) for p in protected}
changes=[{'path':p,'before':h,'after':after[p]} for p,h in protected.items() if after[p]!=h]
for x in comparisons:x['sha256_after']=sha(ROOT/x['path']); assert x['sha256_before']==x['sha256_after']
write('protected_files_verification.json',{'scope':'all pre-existing regional files excluding raw catch files; audit folder excluded','before':protected,'after':after,'changed_during_audit':changes,'audit_script_mutations':'only files beneath this evidence folder','concurrent_external_changes_possible':True})
audit={'schema_version':1,'run_id':'diet_reextraction_20261002_HS_077','region':'HS_077','selected_model_id':MODEL_ID,'selected_model_path':rel(SELECTED),'status':'verified unnormalized unchanged','source_sha256':sha(pdf),'canonical_comparisons':comparisons,'extracted_csv_comparisons':csv_info,'printed_populated_cells_exact':315,'all_source_matrix_cells_ledgered':1440,'raw_converter':{'path':rel(rawpath),'sha256':sha(rawpath),'numeric_differences':rawchanges,'role':'archived normalized intermediate, not selected canonical'},'runtime':{'manifest':rel(HIST/'manifest.json'),'manifest_sha256':sha(HIST/'manifest.json'),'loaded_state_sha256':sha(HIST/'loaded_state.json'),'transformation_ledger_sha256':sha(HIST/'transformation_ledger.json'),'settings':read(HIST/'manifest.json')['constructor'],'authority':'accepted historical runtime; always allowed by latest human steering','fresh_run_performed':False},'changed_canonical_cells':[],'staleness':'No canonical identity changed; no freshness hash updated; historical results preserved.','review_state':'normalization provenance verified; source/ecological trust remains not established','unresolved_evidence':['Nine material printed diet sum discrepancies remain; this audit establishes preservation, not ecological correctness.','35 blank source external-prey cells are encoded as 0 in retained import files and canonical diet_imp. No normalization causes this. Historical writer default is retained; exact scientific approval of each source-blank zero is not independently established by this audit.','Source blank detritus diet fractions remain unknown placeholders; no numerical fate or missing diet residual was supplied.'],'protected_files_changed_during_audit':changes,'actions':['Compared exact retained source bbox ledger and both import CSVs with selected and source canonical copies.','Read researcher DOCX as ZIP XML without changes.','Inspected upright primary Table 3a images PDF28-29.','Archived exact current model input bytes in this folder.','No re-extraction/restoration because canonical normalization was disproved.']}
write('audit.json',audit)

items=[('source',pdf),('source_cell_provenance',WORK/'provenance.json'),('source_extraction',WORK/'model_source.json'),('converter_adapter',WORK/'adapt_database.py'),('bilingual_comparison',WORK/'bilingual_diet_comparison.txt'),('extraction_report',EXTRACT/'REPORT.md'),('raw_converter',rawpath),('runtime_manifest',HIST/'manifest.json'),('runtime_state',HIST/'loaded_state.json'),('runtime_transformations',HIST/'transformation_ledger.json'),('accepted_report',docx),('audit',OUT/'audit.json'),('cell_ledger',OUT/'cell_ledger.json'),('consumer_sums',OUT/'consumer_sums.json'),('protected_verification',OUT/'protected_files_verification.json')]
items += [('canonical_input',p) for p in models]
items += [('diet_import_table',p) for p in csv_paths]
items += [('exact_input_snapshot',p) for p in (OUT/'input_snapshots').rglob('*.json')]
import os
inventory=[{'role':role,'path':Path(os.path.relpath(p,OUT)).as_posix(),'sha256':sha(p),'availability':'present'} for role,p in items]
write('evidence_index.json',{'schema_version':1,'run_id':audit['run_id'],'region_id':'HS_077','model_id':MODEL_ID,'variant_id':'unchanged-source','source_identity':{'sha256':sha(pdf)},'computational_input_identity':{'path':rel(SELECTED),'sha256':sha(SELECTED)},'methods':[],'methods_options':{'fresh_scientific_run':False,'scope':'diet normalization source comparison only'},'required_roles':sorted(set(role for role,p in items)),'artifacts':inventory,'reconciliation':{'all_315_exact':True,'canonical_before_after_identical':True,'source_csv_literals_exact':True,'known_diet_plus_import_sums_exact':True}})
write('completeness.json',{'files_checked':len(inventory),'all_present_hashes_match':all(sha(OUT/x['path'])==x['sha256'] for x in inventory),'missing_roles':[],'reconciliation_failures':[],'status':'complete normalization audit; not a full scientific model validation'})
(OUT/'AUDIT.md').write_text('HS_077 selected canonical diet is verified unnormalized and unchanged.\n\nAll 315 printed Table 3a diet/import literals match exactly across selected input, retained source copies, explicit historical computational input, and both retained Diet_composition.csv files. Primary PDF SHA-256 matches the bbox provenance ledger; upright PDF28-29 table images were inspected. A complete 1,440-cell ledger includes blanks, native JSON pointers, source rows/columns and import coordinates.\n\nThe historical converter produced normalized values and the local adapter restored exact source literals before selection. Accepted historical runtime normalizes ten consumer diets; its own manifest/state/transformation hashes are retained separately. The latest human instruction allows runtime normalization. No calculator was run and no canonical cell or freshness identity changed.\n\nNine material source sum discrepancies remain, plus Albacore 1.001. Review of ecological completeness remains not established. Thirty-five blank source external-prey cells became zero in the retained writer/import/canonical representation; this distinct default encoding is recorded without claiming printed zeros or fresh researcher approval. It is unrelated to normalization and was preserved within the authorized audit scope. Unknown detritus proportions remain unknown.\n\nSee audit.json, cell_ledger.json, consumer_sums.json, accepted_report_readonly.json, protected_files_verification.json, evidence_index.json and completeness.json for exact identities and limitations. Canonical copies and historical computations were preserved; no workbook, DOCX, report index, scientific run, selection or map update was performed.\n',encoding='utf-8')
print(json.dumps({'status':audit['status'],'model_sha256_before':comparisons[0]['sha256_before'],'model_sha256_after':comparisons[0]['sha256_after'],'printed_cells':315,'ledger_cells':1440,'raw_converter_numeric_differences':len(rawchanges),'protected_changes':changes,'audit_path':rel(OUT/'audit.json')},indent=2))
