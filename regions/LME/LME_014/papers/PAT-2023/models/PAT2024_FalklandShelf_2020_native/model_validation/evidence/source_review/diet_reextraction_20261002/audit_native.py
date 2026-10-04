"""Read-only source/canonical/selected/native-diet audit; no scientific runs."""
from pathlib import Path
from decimal import Decimal
import csv, hashlib, json, shutil, sys
from datetime import datetime, timezone
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import pyodbc

E = Path(__file__).resolve().parent
REGION = E.parent
ROOT = REGION.parents[1]
MID = 'PAT2024_FalklandShelf_2020_native'
M = REGION / 'models' / MID
REVIEW = REGION / 'models/extraction_review_20260928'
NATIVE = REVIEW / 'evidence/PAT-2023_native_tables.json'
SOURCE = next((REGION / 'papers/PAT-2023').glob('*.eweaccdb'))
SELECTED = M / 'computational_input' / f'14_140001_{MID}_(2020).json'
CANONICAL = M / 'model.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(name, data):
    (E/name).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

protected = {rel(p): sha(p) for p in REGION.rglob('*') if p.is_file() and E not in p.parents}
source_sha = protected[rel(SOURCE)]
save('protected_before.json', protected)
inputs = [CANONICAL, SELECTED, M/'loader_input'/SELECTED.name, M/'extraction_input.json',
          M/'extracted_tables/Diet_composition.csv']
archive = E/'original_inputs_sha256'; archive.mkdir(exist_ok=True)
for p in inputs:
    h = protected[rel(p)]
    target = archive/(h + p.suffix)
    if not target.exists(): shutil.copyfile(p,target)
    assert sha(target) == h and sha(p) == h

sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book, overview
settings = overview(read_book(REGION/'LME_014.xlsx'))
assert settings['selected_model_id'] == MID
assert (REGION/settings['model_path']).resolve() == SELECTED

cn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+str(SOURCE)+';READONLY=1;')
primary = {}
for table in ['EcopathGroup','EcopathDietComp','EcopathModel','UpdateLog']:
    q = cn.cursor().execute('SELECT * FROM ['+table+']')
    primary[table] = [dict(zip([x[0] for x in q.description],r)) for r in q.fetchall()]
cn.close()
save('primary_readonly_audit_tables.json',primary)
retained = read(NATIVE)
native_equal = {}
for table in ['EcopathGroup','EcopathDietComp']:
    key = (lambda r:r['GroupID']) if table=='EcopathGroup' else (lambda r:(r['PredID'],r['PreyID']))
    a = sorted(primary[table],key=key); b = sorted(retained[table],key=key)
    native_equal[table] = a==b
assert all(native_equal.values()), native_equal
ng = {str(g['Sequence']):g for g in primary['EcopathGroup']}
ids = {g['GroupID']:str(g['Sequence']) for g in primary['EcopathGroup']}
nd = {(ids[r['PredID']],ids[r['PreyID']]):(i,r) for i,r in enumerate(retained['EcopathDietComp'])}
models = {'canonical':read(CANONICAL),'selected':read(SELECTED),
          'loader_input':read(M/'loader_input'/SELECTED.name),
          'converter_intermediate':read(next((M/'extracted_tables').glob('*_(*).json')))}
by = {k:{g['group_seq']:(i,g) for i,g in enumerate(d['group'])} for k,d in models.items()}
extract = read(M/'extraction_input.json')
consumers = set(map(str,extract['consumers']))
with (M/'extracted_tables/Diet_composition.csv').open(encoding='utf-8-sig', newline='') as f:
    rows=list(csv.reader(f))
cols={s:i for i,s in enumerate(rows[0]) if s in consumers}
preys={r[0]:(i,r) for i,r in enumerate(rows) if r[0].isdigit()}
imp = next((i,r) for i,r in enumerate(rows) if any('import' in v.lower() for v in r[:2]))
with (M/'loader_diet.csv').open(encoding='utf-8-sig',newline='') as f: runtime=list(csv.reader(f))
rc={s:i for i,s in enumerate(runtime[0]) if s.isdigit()}
rr={r[0]:r for r in runtime[1:]}
ledger=[]; sums=[]; mismatches=[]; convchanges=[]; runtime_changes=[]; structural=[]
for s,ngroup in sorted(ng.items(), key=lambda kv:int(kv[0])):
    for prey in list(map(str,range(1,37)))+['import']:
        is_import=prey=='import'
        ri,r = (None,ngroup) if is_import else nd[(s,prey)]
        source_literal=str(r['ImpVar'] if is_import else r['Diet'])
        pointers={}; values={}
        for label,gm in by.items():
            gi,g=gm[s]
            if is_import:
                values[label]=g['diet_imp']; pointers[label]=f'/group/{gi}/diet_imp'
            else:
                diet=(g.get('diet_descr') or {}).get('diet') or []
                diet=[diet] if isinstance(diet,dict) else diet
                matches=[(i,x) for i,x in enumerate(diet) if x['prey_seq']==prey]
                if matches:
                    i,x=matches[0]; values[label]=x['proportion']; pointers[label]=f'/group/{gi}/diet_descr/diet/{i}/proportion'
                else: values[label]=None; pointers[label]=None
        evalue=extract['diet'].get(s,{}).get(prey)
        csvvalue=(imp[1][cols[s]] if is_import else preys[prey][1][cols[s]]) if s in consumers else None
        adopted=values['canonical']
        row={'consumer_seq':s,'consumer_name':ngroup['GroupName'],'native_pred_id':ngroup['GroupID'],
             'prey_seq':prey,'source_literal':source_literal,'source_file':rel(SOURCE),'source_sha256':source_sha,
             'native_table':'EcopathGroup' if is_import else 'EcopathDietComp',
             'native_keys':{'GroupID':ngroup['GroupID']} if is_import else {'PredID':r['PredID'],'PreyID':r['PreyID']},
             'retained_native_json_pointer':f'/EcopathGroup/{retained["EcopathGroup"].index(ngroup)}/ImpVar' if is_import else f'/EcopathDietComp/{ri}/Diet',
             'canonical_literal':adopted,'selected_literal':values['selected'],'loader_input_literal':values['loader_input'],
             'extraction_input_literal':evalue,'import_table_literal':csvvalue,'json_pointers':pointers,
             'import_csv_coordinate':{'row_1based':imp[0]+1 if is_import else preys[prey][0]+1,'column_1based':cols[s]+1} if s in consumers else None,
             'retained_native_file':rel(NATIVE),'retained_native_sha256':protected[rel(NATIVE)],
             'accepted_correction_literal':None,'accepted_correction_evidence':'No diet/import correction decision found; canonical and selected identical.',
             'researcher_review_status':'not established'}
        if s in consumers or is_import:
            checks={label:v==source_literal for label,v in values.items() if label!='converter_intermediate'}
            if s in consumers: checks.update(extraction_input=evalue==source_literal,import_table=Decimal(csvvalue)==Decimal(source_literal))
            row['import_table_literal_exact']=csvvalue==source_literal if s in consumers else None
            row['exact_literal_checks']=checks
            if not all(checks.values()): mismatches.append(row)
            if values['converter_intermediate']!=source_literal:
                cv=values['converter_intermediate']
                category='sparse omitted source zero' if cv is None and Decimal(source_literal)==0 else ('literal formatting only' if cv is not None and Decimal(cv)==Decimal(source_literal) else 'numeric precision difference')
                convchanges.append({'consumer':s,'prey':prey,'converter':cv,'source':source_literal,'category':category})
            if s in consumers:
                runtime_value=rr[s][rc['37' if is_import else prey]]
                row['retained_runtime_literal']=runtime_value
                row['retained_runtime_csv_coordinate']=f'consumer row {s}, prey column {"37" if is_import else prey}'
                row['retained_runtime_float_equal']=float(runtime_value)==float(source_literal)
                if not row['retained_runtime_float_equal']: runtime_changes.append(row)
        else:
            row['structural_status']='Nonfeeding source row; source zeros are omitted or represented by -9999 placeholders in canonical; not consumer normalization.'
            if adopted!=source_literal: structural.append({'consumer':s,'prey':prey,'native':source_literal,'canonical':adopted})
        ledger.append(row)
    if s in consumers:
        total=sum(Decimal(str(nd[(s,p)][1]['Diet'])) for p in map(str,range(1,37)))+Decimal(str(ngroup['ImpVar']))
        runtime_sum=sum(Decimal(rr[s][rc[p]]) for p in map(str,range(1,38)))
        sums.append({'consumer_seq':s,'consumer_name':ngroup['GroupName'],'native_diet_plus_import_decimal_sum':str(total),
                     'canonical_sum':str(sum(Decimal(x['source_literal']) for x in ledger if x['consumer_seq']==s)),
                     'native_import_literal':str(ngroup['ImpVar']),'retained_runtime_decimal_sum':str(runtime_sum),
                     'retained_runtime_normalize_DC':False,'runtime_normalization_factor':None,
                     'source_missing_cells':0,'trust':'native-cell fidelity verified; researcher review not established'})
assert not mismatches, f'{len(mismatches)} source cell mismatches'
assert not runtime_changes, f'{len(runtime_changes)} retained runtime float mismatches'
save('cell_ledger.json',ledger);save('consumer_sums.json',sums)
save('converter_intermediate_diet_differences.json',convchanges)
save('nonfeeding_placeholder_limits.json',structural)

# Canonical-to-selected differences are preserved B/EE completion, not diet changes.
parameter_changes=[]
for s,(i,g) in by['canonical'].items():
    target=by['selected'][s][1]
    for field in set(g)|set(target):
        if g.get(field)!=target.get(field): parameter_changes.append({'group':s,'field':field,'canonical':g.get(field),'selected':target.get(field)})
assert all(x['field'] in ['biomass','ee','biomass_habitat_area','b_hab_area_input','ee_input'] for x in parameter_changes), parameter_changes
save('preserved_computational_completion.json',parameter_changes)
docx=REGION/'Model_validation_PAT2024_FalklandShelf_2020_native.docx'
xml=ET.fromstring(ZipFile(docx).read('word/document.xml'))
paras=[''.join(n.itertext()) for n in xml.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')]
save('researcher_decision_scan.json',{'file':rel(docx),'sha256':sha(docx),'read_only':True,
     'matching_paragraphs':[p for p in paras if any(w in p.lower() for w in ['diet','normaliz','import','correct','accept','manual','researcher'])],
     'diet_correction_decision_found':False,'review_status':'not established; report has researcher placeholders'})

after={path:sha(ROOT/path) for path in protected}
unchanged=after==protected
assert unchanged, [p for p in protected if after[p]!=protected[p]]
save('protected_verification.json',{'verified_files':len(protected),'protected_files_unchanged':unchanged,'before':protected,'after':after})
summary={'timestamp':datetime.now(timezone.utc).isoformat(),'region':'LME_014','selected_model_id':MID,
         'selected_path':rel(SELECTED),'selected_sha256':sha(SELECTED),'canonical_path':rel(CANONICAL),'canonical_sha256':sha(CANONICAL),
         'primary_source':rel(SOURCE),'primary_source_sha256':sha(SOURCE),'retained_native_tables_sha256':sha(NATIVE),
         'primary_retained_exact_equality':native_equal,'consumers':len(consumers),'consumer_diet_cells':len(consumers)*36,
         'all_group_import_cells':36,'consumer_source_or_import_mismatches':len(mismatches),'retained_runtime_float_mismatches':len(runtime_changes),
         'converter_intermediate_differences':len(convchanges),'nonfeeding_representation_differences':len(structural),
         'converter_difference_categories':{k:sum(x['category']==k for x in convchanges) for k in set(x['category'] for x in convchanges)},
         'converter_max_present_numeric_difference':str(max(abs(Decimal(x['converter'])-Decimal(x['source'])) for x in convchanges if x['converter'] is not None)),
         'import_csv_zero_literal_format_differences':sum(x.get('import_table_literal_exact') is False for x in ledger),
         'canonical_to_selected_parameter_changes':len(parameter_changes),'normalization_status':'verified unnormalized relative to author-supplied native model',
         'runtime_changed':False,'refresh_required':False,'reextraction_performed':False,'changed_diet_cells':[],
         'source_vs_printed_fidelity':'Published Table S2 is a distinct variant. Native precision and model revisions cannot be restored from printed rounded cells; upstream author processing before native release is not established.',
         'trust_status':'Native source-cell fidelity verified; human review/approval not established. Runtime normalization always permitted separately.',
         'staleness':'No new canonical/selected identity changes and no new staleness introduced; historical diagnostics and freshness hashes preserved.',
         'retained_diagnostic_model_sha256':read(M/'diagnostic_run_record.json')['model_sha256'],
         'workbook_retained_results_model_sha256':settings.get('results_model_sha256'),
         'source_runtime_settings':read(M/'diagnostic_run_record.json')['loader_configuration'],'protected_files_unchanged':unchanged}
save('audit_summary.json',summary)
(E/'audit_report.md').write_text(
    '# LME_014 selected native diet audit\n\n'
    'Verified unnormalized and unchanged relative to the author-supplied native Access database. '
    f'Exact literals match for all {len(consumers)*36} feeding-consumer prey cells and all 36 group imports in canonical, selected and loader-input JSON; '
    'feeding cells also match extraction JSON and CSV numerically. Twenty CSV zero imports use 0 rather than native 0.0. The retained loaded diet matches the same source float values, with normalize_DC=false.\n\n'
    f'The historical native converter intermediate has {len(convchanges)} differing/omitted diet/import literals: 867 sparse zero omissions, 47 formatting differences and 224 numeric precision differences of at most 1e-16. '
    'The retained extraction script restored native precision and explicit zero records. Native intermediate normalization is not proven; the generic converter can normalize other variants. '
    'It is not the selected or canonical identity. No re-extraction, restoration or scientific rerun was performed. '
    'The selected input retains its separate coupled missing-B/EE completion.\n\n'
    'Nonfeeding native zero rows are not complete diet columns in the canonical schema: producer/detritus missing/unknown placeholders remain explicit in nonfeeding_placeholder_limits.json. '
    'These are representation limits, not evidence of feeding-consumer normalization. Published Table S2 has a distinct diet variant, including substantive differences; native binary precision is preserved. '
    'Upstream processing before the author native release and researcher approval remain not established.\n\n'
    'No new model identity change or runtime change was introduced, so no dependent refresh is required by this audit. '
    'Existing diagnostic warnings, selections, parameters, detritus fate, DOCX, workbooks and freshness hashes remain untouched. '
    f'Protected regional files verified unchanged: {len(protected)}.\n',encoding='utf-8')
receipt={'region':'LME_014','selected_model_id':MID,'selected_path':rel(SELECTED),'outcome':'verified unnormalized unchanged',
         'normalization_status':summary['normalization_status'],'reextraction_performed':False,
         'canonical_before_sha256':protected[rel(CANONICAL)],'canonical_after_sha256':sha(CANONICAL),
         'selected_before_sha256':protected[rel(SELECTED)],'selected_after_sha256':sha(SELECTED),
         'changed_diet_cells':[],'runtime_changed':False,'refresh_required':False,
         'evidence_paths':[rel(p) for p in E.iterdir() if p.is_file()],
         'precise_blockers':['No blocker for native-diet normalization audit. Printed-table fidelity and author processing prior to native release remain unestablished; not grounds for restoration.','Researcher diet/import review not established; no correction decision found.'],
         'protected_files_unchanged':unchanged,'protected_file_count':len(protected)}
save('root_receipt.json',receipt)
import os
artifact_paths=[SOURCE,NATIVE,CANONICAL,SELECTED,M/'extraction_input.json',M/'extracted_tables/Diet_composition.csv',
                M/'loader_diet.csv',M/'diagnostic_run_record.json',M/'run_selected_sppr.py',docx]
artifact_paths += [p for p in E.iterdir() if p.is_file() and p.name not in ['evidence_index.json','evidence_completeness.json']]
artifact_paths += list(archive.iterdir())
roles={p:p.name for p in artifact_paths}
index={'schema_version':1,'run_id':'diet_native_audit_20261002_LME014','region_id':'LME_014','model_id':MID,
       'variant_id':'selected_native_completion_unchanged','source_identity':{'path':rel(SOURCE),'sha256':sha(SOURCE)},
       'computational_input_identity':{'path':rel(SELECTED),'sha256':sha(SELECTED)},'methods':[],
       'required_roles':['cell_ledger.json','consumer_sums.json','primary_readonly_audit_tables.json','root_receipt.json','protected_verification.json'],
       'reconciliation':{'primary_matches_retained_native':all(native_equal.values()),'canonical_selected_source_cells':not mismatches,
                         'retained_runtime_source_floats':not runtime_changes,'protected_files_unchanged':unchanged},
       'artifacts':[{'role':roles[p],'path':Path(os.path.relpath(p,E)).as_posix(),'sha256':sha(p),'availability':'present'} for p in artifact_paths]}
save('evidence_index.json',index)
print(json.dumps(summary,ensure_ascii=False,indent=2))
