"""Bounded diet fidelity audit. Only new evidence folder writes are allowed."""
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timezone
import csv, json, hashlib, zipfile, xml.etree.ElementTree as ET, shutil
import openpyxl

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
REG = ROOT / 'regions/LME_050'
MID = '50_502013_Coastal_Kyoto_Inoue_(2013)'
MODEL = REG / 'models' / MID
ETABLE = MODEL / 'extracted_tables'
OUT = Path(__file__).parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(name, obj): (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

protected = [p for p in MODEL.rglob('*') if p.is_file()]
protected += [REG/'LME_050.xlsx', REG/('Model_validation_' + MID + '.docx')]
protected += [p for p in (REG/'validation_reports'/MID).rglob('*') if p.is_file()]
before = {rel(p): sha(p) for p in protected}
dump('protected_before.json', before)
for p in [MODEL/'model.json', ETABLE/'model.json', ETABLE/'Diet_composition.csv', next(ETABLE.glob('*_reconstructed.xlsx'))]:
    target = OUT/'input_archive'/sha(p)/p.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists(): shutil.copyfile(p, target)
    assert sha(target) == sha(p)

canonical = read(MODEL/'model.json')
extraction = read(ETABLE/'model.json')
source = read(ETABLE/'diet_source_cells.json')
source_file = REG/'papers/SOJ-2023/Inoue_et_al_2023_Sea_of_Japan-eaca3b45.pdf'
source_index = {(str(c['predator_seq']), str(c['prey_seq']).lower()): c for c in source if c['prey_seq'] != 'Sum'}
source_sums = {str(c['predator_seq']): c for c in source if c['prey_seq'] == 'Sum'}
groups = {g['group_seq']: g for g in canonical['group']}
with (ETABLE/'Diet_composition.csv').open(encoding='utf-8-sig', newline='') as f: rows = list(csv.reader(f))
csv_index = {(c, (row[0] or row[1]).lower()): row[ci] for ci,c in enumerate(rows[0]) if ci >= 2 for row in rows[1:] if row and len(row)>ci}
cells=[]
for gi,g in enumerate(canonical['group']):
    c = g['group_seq']
    for di, d in enumerate(g['diet_descr']['diet']):
        prey = d['prey_seq']; sc = source_index.get((c,prey)); literal = sc['source_text'] if sc else None
        extracted = extraction['diet'].get(c,{}).get(prey)
        imported = csv_index.get((c,prey))
        matches = d['proportion'] == literal if literal is not None else d['proportion']=='-9999'
        cells.append(dict(consumer_id=c,consumer_name=g['group_name'],prey_id=prey,
            canonical_pointer=f'/group/{gi}/diet_descr/diet/{di}/proportion',canonical_literal=d['proportion'],
            source_literal=literal,extracted_literal=extracted,import_csv_literal=imported,
            exact_literal_match=matches,source_status='printed_value' if sc else 'blank_or_not_tabulated',
            source_path=rel(source_file),source_sha256=sha(source_file),source_location=sc,
            accepted_corrected_literal=None,accepted_correction_evidence=None,review_state='not_established'))
    sc=source_index.get((c,'import')); literal=sc['source_text'] if sc else None
    cells.append(dict(consumer_id=c,consumer_name=g['group_name'],prey_id='import',canonical_pointer=f'/group/{gi}/diet_imp',
        canonical_literal=g['diet_imp'],source_literal=literal,extracted_literal=extraction['diet'].get(c,{}).get('import'),
        import_csv_literal=csv_index.get((c,'import')),exact_literal_match=g['diet_imp']==literal if sc else g['diet_imp']=='-9999',
        source_status='printed_value' if sc else 'blank_or_not_tabulated',source_path=rel(source_file),source_sha256=sha(source_file),
        source_location=sc,accepted_corrected_literal=None,accepted_correction_evidence=None,review_state='not_established'))
for cell in cells:
    if cell['source_literal'] is not None:
        assert cell['exact_literal_match'], cell
        assert cell['source_literal']==cell['extracted_literal']==cell['import_csv_literal'],cell
assert all(c['exact_literal_match'] for c in cells)
dump('cell_ledger.json',cells)

# The reconstructed workbook is retained converter history, distinct from selected JSON.
export = next(ETABLE.glob('*_reconstructed.xlsx'))
w=openpyxl.load_workbook(export,read_only=True,data_only=True)
export_rows=list(w['Diet composition'].values); w.close()
export_index={(str(c),str(row[0]).lower()):(row[ci],ri+1,ci+1) for ci,c in enumerate(export_rows[0]) if ci>=2 for ri,row in enumerate(export_rows[1:],1)}
export_changes=[]
for cell in cells:
    if cell['source_literal'] is None: continue
    value,row,col=export_index[(cell['consumer_id'],cell['prey_id'])]
    if abs(float(value)-float(cell['source_literal']))>1e-12:
        export_changes.append(dict(consumer_id=cell['consumer_id'],prey_id=cell['prey_id'],sheet='Diet composition',row=row,column=col,
            export_value=value,source_literal=cell['source_literal'],canonical_literal=cell['canonical_literal']))
dump('historical_export_differences.json',dict(path=rel(export),sha256=sha(export),classification='normalized_historical_converter_export',
    changed_cells=export_changes,restoration_applied=False,reason='Selected canonical/extraction/import already source faithful; no re-extraction authorized by normalization-first steering. Historical artifact not used by selected runtime.'))

def compare(a,b,path=''):
    diffs=[]
    if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool):
        if abs(a-b)>1e-12: diffs.append(dict(path=path,old=a,new=b,abs_diff=abs(a-b)))
    elif type(a)!=type(b): diffs.append(dict(path=path,old=a,new=b,kind='type_difference'))
    elif isinstance(a,dict):
        for k in sorted(set(a)|set(b)):
            if k not in a or k not in b: diffs.append(dict(path=path+'/'+k,kind='presence_difference'))
            else: diffs += compare(a[k],b[k],path+'/'+k)
    elif isinstance(a,list):
        if len(a)!=len(b): diffs.append(dict(path=path,old_length=len(a),new_length=len(b)))
        for i,(x,y) in enumerate(zip(a,b)): diffs+=compare(x,y,path+'/'+str(i))
    elif a!=b: diffs.append(dict(path=path,old=a,new=b))
    return diffs

historical=read(OUT/'loaded_state_historical.json');current=read(OUT/'loaded_state_current.json')
retained_comparisons={}
for opt in ['GE','TE','With_Egestion']:
    p=MODEL/'evidence'/('exact_loaded_state_'+opt+'.json')
    differences=compare(read(p),historical['loaded_state'])
    retained_comparisons[opt]=dict(path=rel(p),sha256=sha(p),differences=differences,equivalent=not differences)
active_diffs=compare(historical['loaded_state'],current['loaded_state'])
named=[];ignored=[]
for d in active_diffs:
    parts=d['path'].strip('/').split('/')
    if parts[:2]==['_groups_df','data'] and len(parts)==4:
        ri,ci=int(parts[2]),int(parts[3]); d=dict(d,group_id=historical['loaded_state']['_groups_df']['index'][ri],
            group_name=historical['loaded_state']['_groups_df']['data'][ri][0],field=historical['loaded_state']['_groups_df']['columns'][ci])
    ignore = parts[0] in ['growth','predation'] or d.get('field') in ['biomass_accum','predation']
    if ignore: ignored.append(dict(d,ignore_reason='Latest direct human steering excludes biomass accumulation and predation from refresh trigger. growth is the calculator biomass accumulation Series.'))
    else: named.append(d)
code_hashes={variant:{n:sha((MODEL/'diagnostic_code' if variant=='historical' else ROOT/'tools/scientific_code/PPREstimation')/n)
    for n in ['ModelData.py','PPRCalculator.py','utils.py']} for variant in ['historical','current']}
decisive=[d for d in named if d.get('kind')!='presence_difference']
runtime=dict(tolerance=dict(atol=1e-12,rtol=0,excluded_values=['biomass_accum','predation','growth (= biomass accumulation)']),settings=historical['settings'],settings_equal=historical['settings']==current['settings'],
    canonical_input_sha256=sha(MODEL/'model.json'),retained_input_sha256=sha(MODEL/'evidence'/(MID+'.json')),
    code_sha256=code_hashes,loaded_state_sha256={v:sha(OUT/('loaded_state_'+v+'.json')) for v in ['historical','current']},
    retained_state_reproduction=retained_comparisons,current_vs_historical=dict(equivalent=not decisive,differences=named,ignored_differences=ignored,
    diet_equivalent=not compare(historical['loaded_state']['_DC'],current['loaded_state']['_DC']),
    detritus_fate_equivalent=not compare(historical['loaded_state']['_det_fate'],current['loaded_state']['_det_fate'])),
    scientific_diagnostics_called=False,canonical_restoration_runtime_change=False,
    refresh_needed='Synthetic diet_import pb/qb differs beyond tolerance. Root-coordinated affected diagnostics/coefficient/calculation/report/display refresh or an evidence-backed equivalence assessment is required. Canonical audit itself made no input change.',
    stale_hashes_rewritten=False)
dump('runtime_comparison.json',runtime)

sums=[];state=current['loaded_state']['_DC']
for c,g in groups.items():
    raw=sum((Decimal(v) for v in extraction['diet'].get(c,{}).values()),Decimal(0))
    runtime_total=sum(state['data'][state['index'].index(int(c))])
    sums.append(dict(consumer_id=c,name=g['group_name'],raw_prey_plus_import=str(raw),
        source_reported_sum=source_sums.get(c,{}).get('source_text'),raw_nonunit=raw not in [Decimal(0),Decimal(1)],
        runtime_total=runtime_total,normalization_factor=str(Decimal(1)/raw) if raw else None,
        missing_prey_cells=sum(x['proportion']=='-9999' for x in g['diet_descr']['diet']),
        import_source_status='printed_value' if (c,'import') in source_index else 'blank_or_not_tabulated',
        researcher_review_state='not_established',sum_is_not_normalization_evidence=True))
dump('consumer_sums.json',sums)
runtime_cells=[]
for cell in cells:
    ci=state['index'].index(int(cell['consumer_id']))
    prey=41 if cell['prey_id']=='import' else int(cell['prey_id'])
    pi=state['columns'].index(prey)
    value=state['data'][ci][pi]
    raw=0.0 if cell['canonical_literal']=='-9999' else float(cell['canonical_literal'])
    if abs(value-raw)>1e-12:
        runtime_cells.append(dict(consumer_id=cell['consumer_id'],prey_id=cell['prey_id'],source_literal=cell['source_literal'],canonical_literal=cell['canonical_literal'],raw_runtime_input=raw,runtime_value=value,abs_difference=abs(value-raw),source_pointer=cell['canonical_pointer']))
dump('runtime_diet_transformation_ledger.json',dict(canonical_input_sha256=sha(MODEL/'model.json'),runtime_state_sha256=sha(OUT/'loaded_state_current.json'),orientation='Consumer rows, prey columns, synthetic diet_import prey ID 41',changed_cells=runtime_cells,trust_status='Historical report accepts runtime normalization; year-specific source fidelity unresolved; no new approval inferred.'))
doc=REG/('Model_validation_'+MID+'.docx')
with zipfile.ZipFile(doc) as z:
    tree=ET.fromstring(z.read('word/document.xml'))
    paragraphs=[''.join(t.text or '' for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')) for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')]
accepted=dict(path=rel(doc),sha256=sha(doc),read_only=True,
    diet_relevant_paragraphs=[p for p in paragraphs if any(t in p.lower() for t in ['normaliz','diet','manual','researcher'])],
    accepted_canonical_cell_overrides_found=[],runtime_acceptance='Report explicitly documents accepted runtime normalization, GS 0.2, solved accumulation, default catch/migration and routing. Preserved.',
    caveat='No explicit before/after diet/import cell correction or researcher name/date signoff in inspected report; matching source values do not establish source-model year fidelity.')
dump('accepted_corrections_review.json',accepted)
after={rel(p):sha(p) for p in protected}
changed=[p for p in before if before[p]!=after[p]]
dump('protected_verification.json',dict(files_checked=len(before),changed_files=changed,unchanged=not changed,before_sha256=before,after_sha256=after))
assert not changed
blockers=['Published shared Table 2 year-specific identity remains unresolved; do not claim faithful original 2013 native model.',
          'Two consumers have printed prey-plus-import totals 1.01; source correction/rounding acceptance is not established.',
          f'Historical reconstructed converter export retains {len(export_changes)} normalized diet/import cells; selected canonical/extraction/import are unchanged and source faithful.',
          'Current shared runtime loader differs beyond 1e-12 in synthetic import pb/qb. Octopus/Tongue sole BA/growth changes are recorded but explicitly ignored under latest human steering. Root coordinates consequential refresh; audit did not alter runtime input.']
summary=dict(region='LME_050',selected_model_id=MID,selected_path=rel(MODEL/'model.json'),
    outcome='verified_unnormalized_unchanged_with_historical_export_and_current_loader_limits',
    normalization_status='Selected canonical/extraction JSON/import CSV not normalized; exact 206 printed prey/import literals preserved. Historical converter JSON/export normalized.',
    reextraction_performed=False,canonical_before_sha256=before[rel(MODEL/'model.json')],canonical_after_sha256=sha(MODEL/'model.json'),
    changed_diet_cells=[],source_printed_cells_checked=len(source_index),canonical_cells_checked=len(cells),
    historical_export_normalized_cells=len(export_changes),evidence_paths=[rel(OUT/n) for n in ['cell_ledger.json','consumer_sums.json','runtime_comparison.json','runtime_diet_transformation_ledger.json','accepted_corrections_review.json','historical_export_differences.json','protected_verification.json','loaded_state_historical.json','loaded_state_current.json','audit.py','runtime_probe.py']],
    precise_blockers=blockers,protected_files_unchanged=True,protected_files_checked=len(before),
    runtime_comparison_tolerance=dict(atol=1e-12,rtol=0),canonical_change_requires_refresh=False,current_shared_loader_requires_root_refresh_assessment=True,
    review_approval=False,timestamp_utc=datetime.now(timezone.utc).isoformat())
dump('root_receipt.json',summary)
print(json.dumps({k:summary[k] for k in ['outcome','source_printed_cells_checked','canonical_cells_checked','historical_export_normalized_cells','protected_files_checked','canonical_after_sha256']},ensure_ascii=False))
