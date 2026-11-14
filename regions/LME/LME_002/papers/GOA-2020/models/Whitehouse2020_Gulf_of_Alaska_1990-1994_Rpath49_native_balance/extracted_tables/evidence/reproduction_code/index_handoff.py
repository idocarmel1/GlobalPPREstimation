"""Inventory and verify retained evidence without scientific execution."""
from pathlib import Path
import hashlib, importlib.util, json, os, sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
RUN=ROOT/'regions/LME/LME_002/work/2026-11-14_191000_native_balance_diagnostics'
PAPER=ROOT/'regions/LME/LME_002/papers/GOA-2020'
PARENT=PAPER/'models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49'
MODEL=PAPER/'models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance'
EV=MODEL/'extracted_tables/evidence'
sys.stdout.reconfigure(encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def rel(p,base=EV): return os.path.relpath(p,base).replace('\\','/')

scope=read(EV/'run_scope.json')
summary=read(MODEL/'results/diagnostics/diagnostic_summary.json')
independent=read(MODEL/'results/diagnostics/independent_diagnostics_review.json')
assert independent['status']=='PASS' and independent['artifact_qa_issue_count']==0
assert sha(ROOT/'regions/LME/LME_002/LME_002.xlsx')==scope['region_workbook_sha256']
assert sha(PARENT/'model.json')==scope['parent_model_sha256']
assert sha(MODEL/'model.json')==summary['identity']['variant_sha256']
native_sources=read(PAPER/'source_manifest.json')['files']
assert all(sha(PAPER/f['path'])==f['sha256'] for f in native_sources)
assert len(list(MODEL.glob('model.json')))==1
assert all(m['reload_matches'] for m in summary['methods'].values())
assert all(m['overall_grade']=='FAIL' for m in summary['methods'].values())
(EV/'reproduction_code/index_handoff.py').write_bytes(Path(__file__).read_bytes())
dump(EV/'protected_inputs_verification.json',{
    'parent_model_sha256':sha(PARENT/'model.json'),'parent_model_unchanged':True,
    'variant_model_sha256':sha(MODEL/'model.json'),'variant_unchanged_after_diagnostics':True,
    'regional_workbook_sha256':sha(ROOT/'regions/LME/LME_002/LME_002.xlsx'),'regional_workbook_unchanged':True,
    'native_source_files_verified':len(native_sources),'native_source_bytes_unchanged':True,
    'map_action':'No map build, publication or map-file write was executed in this task.',
    'regional_selection_or_mapping_written':False,'annual_PPR_calculated':False})

def role(p):
    r=p.relative_to(MODEL).as_posix()
    if r=='model.json':return 'canonical_model'
    if r=='model_notes.md':return 'model_notes'
    if r=='MODEL_PROFILE.md':return 'source_model_profile'
    if r=='inputs/provenance.json':return 'provenance'
    if r=='results/result_manifest.json':return 'diagnostic_result_manifest'
    if 'native_reproduction/' in r:
        if p.name=='native_manifest.json':return 'native_inventory'
        if p.name=='native_balanced.rds':return 'native_serialized_result'
        if p.name=='native_summary.json':return 'native_balance_verification'
        if p.name=='independent_native_variant_review.json':return 'independent_native_qa'
        if p.suffix in ('.py','.R'):return 'reproduction_code'
        return 'native_reproduction_evidence'
    if 'reproduction_code/' in r:return 'reproduction_code'
    if 'results/diagnostics/' in r:
        if p.name.startswith('initial_') and p.suffix=='.json':return 'full_diagnostic_return'
        if p.name.startswith('reload_') and p.suffix=='.json':return 'diagnostic_reload_return'
        if p.name=='run_identity.json':return 'diagnostic_configuration'
        if p.name=='diagnostic_summary.json':return 'diagnostic_reconciliation'
        if p.name=='independent_diagnostics_review.json':return 'independent_diagnostic_qa'
        if p.name=='diagnostic_budget_decomposition.json':return 'budget_decomposition'
        if p.name in ('DIAGNOSTIC_INTERPRETATION.md','direct_diagnostics.md'):return 'diagnostic_report'
        if 'ledger' in p.name or p.name=='constructor_audit.json':return 'source_runtime_ledger'
        if 'executed_code/' in r:return 'executed_diagnostic_code'
        return 'diagnostic_support'
    if p.name=='SOURCE_FIDELITY_CHECK.json':return 'roundtrip_verification'
    if p.name=='native_to_variant_ledger.json':return 'native_variant_ledger'
    if p.name=='variant_conversion.json':return 'variant_conversion'
    if p.name=='Taxonomy.xlsx':return 'candidate_taxonomy'
    if 'companions/' in r:return 'source_companion'
    if p.parent==MODEL/'extracted_tables':return 'standard_import'
    if p.name in ('cleanup_receipt.json','protected_inputs_verification.json'):return 'closeout_verification'
    return 'supporting_evidence'

artifacts=[]
for p in sorted(MODEL.rglob('*')):
    if p.is_file() and p.name not in ('evidence_index.json','evidence_completeness.json'):
        artifacts.append({'role':role(p),'path':rel(p),'sha256':sha(p),'availability':'present'})
external=[('parent_canonical_model',PARENT/'model.json'),('paper_source_manifest',PAPER/'source_manifest.json'),
          ('candidate_taxonomy_evidence',PARENT/'extracted_tables/evidence/candidate_taxonomy_evidence.json')]
external.extend(('native_source',PAPER/f['path']) for f in native_sources)
for name,p in external:artifacts.append({'role':name,'path':rel(p),'sha256':sha(p),'availability':'present'})
artifacts.append({'role':'publication_pdf','availability':'missing','reason':'The numerical native inputs and pinned code are retained. Article indexed text was read in extraction; local article download returned 403 and screenshot retrieval failed.','acquisition_status':'Unchanged from source extraction; no new acquisition required for this native execution.'})
required=['canonical_model','model_notes','provenance','diagnostic_result_manifest','native_inventory','native_serialized_result','native_balance_verification','independent_native_qa','reproduction_code','full_diagnostic_return','diagnostic_reload_return','diagnostic_configuration','diagnostic_reconciliation','independent_diagnostic_qa','budget_decomposition','diagnostic_report','source_runtime_ledger','executed_diagnostic_code','roundtrip_verification','native_variant_ledger','variant_conversion','standard_import','source_companion','closeout_verification','parent_canonical_model','paper_source_manifest','native_source']
index={
    'schema_version':1,'run_id':RUN.name,'region_id':'LME_002','model_id':MODEL.name,
    'variant_id':'pinned_native_Rpath_balance_completion',
    'source_identity':{'citation':read(PAPER/'source_manifest.json')['citation'],'commit':'fe63f6d370d942ff1786f4d649e432fbfb85f81b','parent_sha256':sha(PARENT/'model.json')},
    'computational_input_identity':{'path':rel(MODEL/'model.json'),'sha256':sha(MODEL/'model.json')},
    'methods':['native Rpath balance','GE','TE','With Egestion','fresh-process persisted-input reproduction','independent retained-evidence verification'],
    'required_roles':required,'artifacts':artifacts,
    'reconciliation':{'native_known_inputs_preserved':True,'native_variant_roundtrip':True,'persisted_constructor_state':True,'persisted_full_diagnostic_returns':True,'source_scope_sums':True,'raw_source_EE_floor_exclusions':True,'native_sources_and_regional_workbook_unchanged':True},
    'scientific_outcomes':{name:m['overall_grade'] for name,m in summary['methods'].items()},
    'scientific_eligibility':'All three PPR methods FAIL. Reproduced execution and complete evidence do not establish valid annual PPR, LME geographic suitability or researcher approval.',
    'scope_limits':['No catch mapping, annual regional PPR, selection, central registry write, map update or researcher signoff.','Study/LME overlap, local/external production split and candidate taxonomy review remain unresolved.']}
dump(EV/'evidence_index.json',index)
script=ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py'
spec=importlib.util.spec_from_file_location('evidence_check',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
for path in (PARENT/'extracted_tables/evidence/evidence_index.json',EV/'evidence_index.json'):
    result=module.check(path);dump(path.parent/'evidence_completeness.json',result)
    assert result['complete'], result
    print(json.dumps({'model':path.parents[2].name,'complete':result['complete'],'files':len(result['verified_artifacts']),'missing_roles':result['missing_roles'],'errors':result['errors']}))
