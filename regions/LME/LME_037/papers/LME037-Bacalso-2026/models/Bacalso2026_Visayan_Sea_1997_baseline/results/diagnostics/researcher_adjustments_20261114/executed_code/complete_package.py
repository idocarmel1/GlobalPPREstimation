"""Final packaging only: authoritative source reference and independent QA receipt."""
from pathlib import Path
import hashlib,json,shutil
RUN=Path(__file__).resolve().parents[1];MODEL=RUN.parents[2];OUT=RUN/'outputs/scientific'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
index=json.loads((OUT/'evidence_index.json').read_text(encoding='utf-8'))
evidence=json.loads((OUT/'execution_evidence.json').read_text(encoding='utf-8'))
snapshot=OUT/'source_model.json'
if snapshot.exists():
    assert snapshot.resolve().parent==OUT.resolve() and sha(snapshot)==sha(MODEL/'model.json')
    snapshot.unlink()
index['artifacts']=[a for a in index['artifacts'] if a['role']!='source_model']
index['required_roles']=['source_model_reference' if r=='source_model' else r for r in index['required_roles']]
def put(name,value,role):
    (OUT/name).write_bytes(raw(value));register(name,role)
def register(name,role):
    index['artifacts']=[a for a in index['artifacts'] if a['path']!=name]
    index['artifacts'].append({'path':name,'role':role,'sha256':sha(OUT/name),'availability':'present'})
put('source_model_reference.json',{'path_from_model_root':'model.json','sha256':sha(MODEL/'model.json'),'resolution':'Nearest ancestor model.json; sole authoritative canonical source representation.'},'source_model_reference')
evidence.pop('source_model_snapshot',None)
evidence['source_model_reference']='source_model_reference.json'
groups=json.loads((OUT/'groups.json').read_text(encoding='utf-8'))
negative_ba=[{'seq':g['seq'],'group_name':g['group_name'],'biomass_accum':g['biomass_accum']} for g in groups if g['biomass_accum'] is not None and g['biomass_accum']<0]
put('negative_ba_residuals.json',{'interpretation':'Derived closure/depletion residuals, not observed source stock change. No clipping applied.','groups':negative_ba},'negative_ba_residuals')
evidence['negative_ba_count']=len(negative_ba)
evidence['negative_ba_ledger']='negative_ba_residuals.json'
qa=RUN/'qa/root_scientific_check.json'
assert qa.exists()
shutil.copyfile(qa,OUT/'independent_arithmetic_check.json')
register('independent_arithmetic_check.json','independent_scientific_check')
evidence['independent_arithmetic_check']='independent_arithmetic_check.json'
for script in ['finalize_scientific.py','complete_package.py']:
    shutil.copyfile(RUN/'code'/script,OUT/'executed_code'/script)
    register('executed_code/'+script,'postprocessing_driver')
register('reproduce.py','reproducer')
put('execution_evidence.json',evidence,'execution_evidence')
for artifact in index['artifacts']:assert sha(OUT/artifact['path'])==artifact['sha256']
assert all(index['reconciliation'].values())
(OUT/'evidence_index.json').write_bytes(raw(index))
for script in ['reproduce.py','executed_code/run_scientific.py','executed_code/finalize_scientific.py','executed_code/complete_package.py']:
    compile((OUT/script).read_text(encoding='utf-8'),script,'exec')
receipt={'package_ready':True,'artifacts_verified':len(index['artifacts']),'evidence_index_sha256':sha(OUT/'evidence_index.json'),'execution_evidence_sha256':sha(OUT/'execution_evidence.json'),'runtime_content_sha256':evidence['runtime_content_sha256'],'runtime_file_sha256':evidence['runtime_file_sha256'],'canonical_sha256':sha(MODEL/'model.json'),'negative_ba_count':len(negative_ba),'duplicate_source_representation':False,'additional_scientific_solves':0}
(RUN/'qa/final_package_check.json').write_bytes(raw(receipt))
print(json.dumps(receipt))
