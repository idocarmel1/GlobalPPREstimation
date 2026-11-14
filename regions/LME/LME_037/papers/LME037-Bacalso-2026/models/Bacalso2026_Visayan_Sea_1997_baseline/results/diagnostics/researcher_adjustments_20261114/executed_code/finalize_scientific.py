"""Finalize already-computed evidence without running scientific methods again."""
from pathlib import Path
import gzip, hashlib, importlib.util, json, math, os, shutil, sys
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
RUN=Path(__file__).resolve().parents[1]
MODEL=RUN.parents[2]
ROOT=MODEL.parents[6]
OUT=RUN/'outputs/scientific'
def raw(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
summary=json.loads((RUN/'outputs/scientific_summary.json').read_text(encoding='utf-8'))
config=load('configuration.json')
index=load('evidence_index.json')
assert all(m['outcome']=='returned' for m in summary['methods'])
sys.path.insert(0,str(OUT/'executed_code'))
from PPRCalculator import PPRCalculator
codec_source=ROOT/'research/agents/regional_ge_integration_20260928/evidence/runtime_codec.py'
shutil.copyfile(codec_source,OUT/'runtime_codec.py')
spec=importlib.util.spec_from_file_location('packaged_runtime_codec',OUT/'runtime_codec.py')
codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
runtime=codec.decode(json.loads(gzip.decompress((OUT/'runtime_before.json.gz').read_bytes())))
calc=PPRCalculator.__new__(PPRCalculator);calc.__dict__.update(runtime)
def save(n,x,role):
    (OUT/n).write_bytes(raw(x))
    index['artifacts']=[a for a in index['artifacts'] if a['path']!=n]
    index['artifacts'].append({'path':n,'role':role,'sha256':sha(OUT/n),'availability':'present'})
    return n
model_health=[]
concise=[]
matrices=load('matrix_inspections.json')
for item in summary['methods']:
    report=item['diagnostic']
    flattened=PPRCalculator._flatten_diagnostics(report)
    model_health.append({'model_id':summary['model_id'],'TE_option':item['option'],**flattened})
    matrix=next(x for x in matrices if x['method']==item['option'])['matrices'][0]
    concise.append({'method':item['method_key'],'option':item['option'],'status':report['status'],'model_input':report['model_input'],'divergence':report['divergence'],'balance':report['balance'],'strict_negative_pairs':matrix['negative_entries'],'SPPR_shape':matrix['shape'],'warnings':report.get('warnings',[]),'all_sources_and_unfished_included':True})
save('model_health.json',model_health,'model_health')
save('concise_metrics.json',concise,'concise_metrics')
old_inventory=RUN/'outputs/integration_inventory.json'
annual={'policy':'Preserve existing scope-specific provisional annual restrictions and geography/allocation missingness; diagnostic status alone does not establish annual readiness.','method_diagnostic_status':{x['method_key']:x['status'] for x in summary['methods']},'stock_adapter_reconstructible':False}
if old_inventory.exists():annual['integration_inventory_path']='../integration_inventory.json'
save('annual_status_guidance.json',annual,'annual_status_guidance')
source=json.loads((MODEL/'model.json').read_text(encoding='utf-8'))
index['artifacts']=[a for a in index['artifacts'] if a['role']!='source_model']
index['required_roles']=['source_model_reference' if r=='source_model' else r for r in index['required_roles']]
save('source_model_reference.json',{'path_from_model_root':'model.json','sha256':sha(MODEL/'model.json'),'resolution':'Nearest ancestor model.json; sole authoritative canonical source representation.'},'source_model_reference')
missingness=[]
for group in source['group']:
    for field,value in group.items():
        if value in ('-9999',-9999,None):missingness.append({'group_id':int(group['group_seq']),'group_name':group['group_name'],'field':field,'source_value':value})
save('canonical_group_missingness.json',missingness,'source_missingness')
shutil.copyfile(RUN/'qa/constructor_attempt1.json',OUT/'constructor_attempt1_NOT_RUN.json')
shutil.copyfile(RUN/'qa/evidence_writer_attempt2.json',OUT/'evidence_writer_attempt2_NOT_RUN.json')
shutil.copyfile(RUN/'code/run_scientific.py',OUT/'executed_code/run_scientific.py')
shutil.copyfile(RUN/'code/finalize_scientific.py',OUT/'executed_code/finalize_scientific.py')
permanent='results/diagnostics/researcher_adjustments_20261114'
engine_sources={n:f'{permanent}/executed_code/{n}' for n in config['engine_hashes']}
effective={**config['constructor'],'runtime_initialization':{'diet_import_unknown_to_zero_group_ids':config['input_transformations']['diet_imp_unknown_to_zero_group_ids'],'single_detritus_routing':config['input_transformations']['single_detritus_routing']},'configuration_evidence':f'{permanent}/configuration.json','engine_sources':engine_sources,'stock_adapter_reconstructible':False,'reproducer':f'{permanent}/reproduce.py'}
save('effective_loader_flags.json',effective,'effective_loader_flags')
identity={'kind':'authenticated_current_engine','sha256':config['engine_hashes'],'paths':engine_sources,'engine_bytes_unchanged':summary['engine_bytes_unchanged']}
save('code_identity.json',identity,'code_identity')
summary.update({'stock_adapter_reconstructible':False,'custom_reproducer_required':True,'effective_loader_flags':effective,'code_identity':identity,'permanent_package':permanent,'constructor_attempt1':'constructor_attempt1_NOT_RUN.json','model_health_path':'model_health.json','groups_path':'groups.json','group_sppr_path':'group_sppr.json','runtime_file':{'path':'runtime_before.json.gz','sha256':sha(OUT/'runtime_before.json.gz')},'input_missingness_ledger':'canonical_group_missingness.json','explicit_historical_routing_replayed':True,'configuration_evidence':'configuration.json','reproducer':'reproduce.py','summary_origin':'Postprocessing of retained fresh full returns; no additional diagnostic solves.'})
for item in summary['methods']:
    for key in ['full_return','diagnostic_file']:item[key]['path']=Path(item[key]['path']).name
summary['runtime_content_sha256']=hashlib.sha256(gzip.decompress((OUT/'runtime_before.json.gz').read_bytes())).hexdigest()
summary['runtime_file_sha256']=sha(OUT/'runtime_before.json.gz')
summary['runtime_identity_definition']='SHA256 of decompressed typed canonical JSON bytes in runtime_before.json.gz; file SHA is separately retained.'
summary['source_model_reference']='source_model_reference.json'
changed_diet=load('normalized_diet_changed_cells.json')
summary['normalization_changed_finite_diet_cell_count']=sum(not r['old_missing'] and not r['new_missing'] for r in changed_diet)
summary['basal_missingness_completion_cell_count']=sum(r['old_missing'] or r['new_missing'] for r in changed_diet)
summary['evidence_writer_attempt2']='evidence_writer_attempt2_NOT_RUN.json'
save('execution_evidence.json',summary,'execution_evidence')
for name,role in [('runtime_codec.py','runtime_codec'),('reproduce.py','reproducer'),('constructor_attempt1_NOT_RUN.json','constructor_attempt_history'),('executed_code/run_scientific.py','execution_driver'),('executed_code/finalize_scientific.py','postprocessing_driver')]:
    index['artifacts']=[a for a in index['artifacts'] if a['path']!=name]
    index['artifacts'].append({'path':name,'role':role,'sha256':sha(OUT/name),'availability':'present'})
index['required_roles']+=['runtime_codec','reproducer','execution_evidence','model_health','source_missingness','constructor_attempt_history']
index['artifacts'].append({'path':'evidence_writer_attempt2_NOT_RUN.json','role':'evidence_writer_attempt_history','sha256':sha(OUT/'evidence_writer_attempt2_NOT_RUN.json'),'availability':'present'})
index['required_roles']=list(dict.fromkeys(index['required_roles']))
index['reconciliation']['full_runtime_before_after_exact']=(OUT/'runtime_before.json.gz').read_bytes()==(OUT/'runtime_after.json.gz').read_bytes()
index['reconciliation']['all_SPPR_entries_finite_nonnegative']=all(not any(m['matrices'][0][k] for k in ['negative_entries','null','nan','positive_infinity','negative_infinity']) for m in matrices)
assert all(index['reconciliation'].values()),index['reconciliation']
for artifact in index['artifacts']:
    assert sha(OUT/artifact['path'])==artifact['sha256'],artifact
(OUT/'evidence_index.json').write_bytes(raw(index))
receipt={'artifact_hashes_verified':len(index['artifacts']),'reconciliation':index['reconciliation'],'canonical_sha256':sha(MODEL/'model.json'),'engine_sha256':{n:sha(ROOT/'tools/scientific_code/PPREstimation'/n) for n in config['engine_hashes']},'additional_scientific_solves':0}
assert receipt['canonical_sha256']==summary['canonical_sha256']
assert receipt['engine_sha256']==config['engine_hashes']
(RUN/'qa/scientific_postcheck.json').write_bytes(raw(receipt))
print(json.dumps({'package':str(OUT),'model_health_rows':len(model_health),'methods':[{'method':x['method'],'status':x['status'],'divergence':x['divergence'],'balance':x['balance'],'model_input':x['model_input']} for x in concise],'postcheck':receipt},ensure_ascii=False))
