"""Finalize portable evidence inventories and independent protection/link checks."""
from pathlib import Path,PureWindowsPath
import hashlib,importlib.util,json,os,re,sys,zipfile
from urllib.parse import unquote,urlsplit
from xml.etree import ElementTree as E
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];REGION=ROOT/'regions/LME_027'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
spec=importlib.util.spec_from_file_location('checker',ROOT/'tools/skills/original_skill_resources/combined-src/scripts/check_evidence.py');checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
checks={};protected=[];catalog_changes=[]
for r in load(HERE/'baseline/manifest.json')['protected_files']:
    p=ROOT/r['path'];actual=sha(p)
    if actual!=r['sha256']:
        assert p.parent==REGION/'papers/CAN-2014' and p.name in ('metadata.json','README.md','footprint.geojson'),r['path']
        backup=HERE/'baseline'/('CAN-2014_'+p.name);assert sha(backup)==r['sha256']
        catalog_changes.append({'path':r['path'],'old_sha256':r['sha256'],'new_sha256':actual,'preserved_original_catalog':backup.relative_to(ROOT).as_posix()})
    else:protected.append(r)
checks['all_original_publications_unrelated_models_selected_workbook_and_signed_review_unchanged']=True
save(HERE/'qa/protected_files.json',{'unchanged':protected,'authorized_catalog_updates':catalog_changes,'all_checks_passed':True})
sys.path.insert(0,str(ROOT/'tools'));from researcher_review import table_rows
with zipfile.ZipFile(ROOT/'Project.xlsx') as new,zipfile.ZipFile(HERE/'baseline/Project_before_inventory.xlsx') as old:
    diff=[n for n in old.namelist() if old.read(n)!=new.read(n)]
    assert set(diff)=={'xl/worksheets/sheet2.xml','xl/worksheets/sheet3.xml','xl/worksheets/sheet8.xml'}
    before={d['model_id']:d for _,d in table_rows(old,'Models & coverage','Models')[3]};after={d['model_id']:d for _,d in table_rows(new,'Models & coverage','Models')[3]}
    assert before['27_118_Northwest_Africa_(1987)']==after['27_118_Northwest_Africa_(1987)']
    assert sum(k.startswith('Guenette2014_BancArguin_') for k in after)==3
    assert not any('Banc_d_Arguin' in k for k in after)
checks['only_candidate_catalog_and_geography_Project_parts_changed']=True
checks['researcher1987_record_preserved_and_three_current_candidates']=True
# Check local Office relationships again after consolidation. Source originals excluded.
links=[]
for v in ('Base','M30','P30'):
    mid=f'Guenette2014_BancArguin_{v}_1991'
    for p in (REGION/f'Model_validation_{mid}.docx',REGION/f'LME027_Guenette2014_{v}_taxon_mapping_appendix.xlsx'):
        with zipfile.ZipFile(p) as z:
            for name in z.namelist():
                if not name.endswith('.rels'):continue
                for rel in E.fromstring(z.read(name)):
                    if not rel.get('Type','').endswith('/hyperlink'):continue
                    target=rel.get('Target','');part=target.partition('#')[0]
                    if not part or urlsplit(part).scheme in ('http','https','mailto'):continue
                    assert not PureWindowsPath(part).drive and not part.startswith(('/','\\')),(p.name,target)
                    path=(p.parent/unquote(part)).resolve();assert path.exists(),(p.name,target)
                    assert path.is_relative_to(ROOT)
                    links.append({'document':p.relative_to(ROOT).as_posix(),'target':target,'resolved':path.relative_to(ROOT).as_posix()})
            if 'docProps/app.xml' in z.namelist():
                for e in E.fromstring(z.read('docProps/app.xml')).iter():
                    if e.tag.endswith('HyperlinkBase'):assert not (e.text or '').strip()
save(HERE/'qa/final_local_links.json',{'passed':True,'local_relationships_checked':len(links),'links':links})
checks['Office_links_resolve_after_cleanup']=True
for sub in ('extraction','mapping'):
    p=HERE/sub/'evidence_index.json';result=checker.check(p);save(HERE/sub/'completeness.json',result)
    assert result['complete'],(sub,result['errors']);checks[sub+'_inventory_valid']=True
assert load(HERE/'mapping/candidate_arithmetic_qa.json')['complete'];checks['full_grid_candidate_arithmetic_verified']=True
assert all(x['passed'] for x in load(HERE/'qa/diagnostic_reconciliation.json'));checks['full_matrices_scopes_masks_flows_verified']=True
for v in ('Base','M30','P30'):
    model=REGION/f'models/Guenette2014_BancArguin_{v}_1991/model.json';e=load(HERE/f'runtime/{v}_source_admission/execution_evidence.json');assert e['source_sha256']==sha(model)
    a=load(model.parent/'regional_assessment/assessment.json');assert a['source_model_sha256']==sha(model)
    assert a['mapping_sha256']==sha(HERE/f'mapping/{v}_mapping_evidence.json')
checks['final_canonical_diagnostic_and_arithmetic_identities_match']=True
save(HERE/'qa/final_verification.json',{'checks':checks,'all_passed':all(checks.values()),'limits':'Completed feasible candidate assessments, not successful scientific validation or researcher adoption. Eight CSV schema compatibility verified; EwE GUI import not attempted.'})
def artifact(p,role,base):return {'role':role,'availability':'present','path':Path(os.path.relpath(p,base)).as_posix(),'sha256':sha(p)}
def make_index(base,model_id,variant,files,extra_missing,source_identity,input_identity):
    artifacts=[artifact(p,role,base) for role,p in files]
    roles=[a['role'] for a in artifacts]
    assert len(roles)==len(set(roles))
    d={'schema_version':1,'run_id':'LME_027_BancArguin_20261003','region_id':'LME_027','model_id':model_id,'variant_id':variant,'source_identity':source_identity,'computational_input_identity':input_identity,'methods':['GE','TE','With Egestion'],'required_roles':roles,'artifacts':artifacts+extra_missing,'reconciliation':checks,'production_eligible':False,'selection_adopted':False,'scientific_parameterization_complete':False,'task_scope':'All feasible requested stages complete, with explicit failed/blocked numerical stages. Candidate-specific evidence does not override Overview/Project selection.'}
    save(base/'evidence_index.json',d);result=checker.check(base/'evidence_index.json');save(base/'completeness.json',result);assert result['complete'],result
    return d
for v in ('Base','M30','P30'):
    mid=f'Guenette2014_BancArguin_{v}_1991';base=REGION/'models'/mid
    files=[('canonical_source',base/'model.json'),('extraction_inventory',HERE/'extraction/evidence_index.json'),('taxonomy',base/'extracted_tables/Taxonomy.xlsx'),('mapping',HERE/f'mapping/{v}_mapping_evidence.json'),('DOCX',REGION/f'Model_validation_{mid}.docx'),('Excel_appendix',REGION/f'LME027_Guenette2014_{v}_taxon_mapping_appendix.xlsx'),('geography',HERE/'context/geographic_assessment.json'),('final_verification',HERE/'qa/final_verification.json')]
    for p in sorted((base/'extracted_tables').rglob('*')):
        if p.is_file():files.append(('extraction/'+p.relative_to(base/'extracted_tables').as_posix(),p))
    for p in sorted((base/'regional_assessment').glob('*')):
        if p.is_file():files.append(('regional/'+p.name,p))
    for p in sorted((HERE/f'runtime/{v}_source_admission').glob('*')):
        if p.is_file():files.append(('source_admission/'+p.name,p))
    missing=[{'role':'validated_source_SPPR_and_regional_model_PPR','availability':'failed' if v=='Base' else 'missing','reason':'Published-source diet admission fails and stanza P/B is incomplete.' if v=='Base' else '114 unpublished variant diet cells in14consumers; complete independent composition unavailable.','acquisition_status':'Original article/XLS/DOCX/figures and authoritative EcoBase689 reviewed; no complete verified variant recovered.'}]
    if v=='Base':
        for p in sorted((HERE/'runtime/Base_runtime_PQ_approximation').rglob('*')):
            if p.is_file():files.append(('separate_experiment/'+p.relative_to(HERE/'runtime/Base_runtime_PQ_approximation').as_posix(),p))
    make_index(base,mid,v,files,missing,{'doi':'10.1371/journal.pone.0094742','canonical_sha256':sha(base/'model.json')},load(HERE/f'runtime/{v}_source_admission/execution_evidence.json'))
files=[]
for p in sorted(HERE.iterdir()):
    if p.is_file() and p.name not in ('evidence_index.json','completeness.json'):files.append(('handoff/'+p.name,p))
for sub in ('context','qa'):
    for p in sorted((HERE/sub).rglob('*')):
        if p.is_file() and p.suffix.lower() in ('.json','.pdf','.png','.geojson','.md'):files.append((sub+'/'+p.relative_to(HERE/sub).as_posix(),p))
for sub in ('extraction','mapping'):
    for name in ('evidence_index.json','completeness.json'):files.append((sub+'/'+name,HERE/sub/name))
for p in sorted((HERE/'runtime').glob('*')):
    if p.is_file():files.append(('runtime/'+p.name,p))
for p in sorted((HERE/'runtime/engine').glob('*.py')):files.append(('engine/'+p.name,p))
for p in sorted((HERE/'runtime/EcoBase689_native_companion').glob('*')):
    if p.is_file():files.append(('native689/'+p.name,p))
for p in sorted((REGION/'papers/CAN-2014/recovery_20261003').rglob('*')):
    if p.is_file():files.append(('authoritative_recovery/'+p.relative_to(REGION/'papers/CAN-2014/recovery_20261003').as_posix(),p))
for v in ('Base','M30','P30'):
    base=REGION/f'models/Guenette2014_BancArguin_{v}_1991'
    for name in ('evidence_index.json','completeness.json'):files.append((v+'/'+name,base/name))
for name in ('manifest.json','superseded_Banc_evidence.zip','Project_before_inventory.xlsx','inventory_before.json'):files.append(('baseline/'+name,HERE/'baseline'/name))
for role,p in [('current_Project',ROOT/'Project.xlsx'),('current_paper_index',REGION/'papers/CAN-2014/extracted/MASTER_INDEX.md'),('active_atlas_adapter',ROOT/'tools/original_atlas_data.py'),('active_HTML_builder',ROOT/'tools/build_html.py')]:files.append((role,p))
make_index(HERE,'Guenette2014_BancArguin_1991_family','Base;M30;P30',files,[{'role':'researcher_adoption','availability':'inapplicable','reason':'User explicitly prohibited automatic regional selection or replacement of selected outputs.','acquisition_status':'No adoption attempted; current selection and signed disqualification retained.'}],{'doi':'10.1371/journal.pone.0094742','models':{v:sha(REGION/f'models/Guenette2014_BancArguin_{v}_1991/model.json') for v in ('Base','M30','P30')}},{'Base_source':'runtime/Base_source_admission/execution_evidence.json','Base_experiment':'runtime/Base_runtime_PQ_approximation/execution_evidence.json','M30_source':'runtime/M30_source_admission/execution_evidence.json','P30_source':'runtime/P30_source_admission/execution_evidence.json','EcoBase689_distinct_companion':'runtime/EcoBase689_native_companion/execution_evidence.json'})
print(json.dumps({'final_checks':checks,'protected_unchanged':len(protected),'root_index_artifacts':len(files),'candidate_indexes':3}))
