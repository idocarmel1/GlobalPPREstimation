"""Read-only diagnostic investigation; writes only the adjacent outputs directory."""
from pathlib import Path
import sys, json, hashlib, math, warnings, platform, copy, gzip
sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
MODEL = ROOT/'regions/LME/LME_049/papers/KUR-2019/models/49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'
EV = MODEL/'extracted_tables/evidence'
ENGINE = EV/'diagnostic_code/PPREstimation'
OUT = Path(__file__).resolve().parent.parent/'outputs'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ENGINE))
sys.path.insert(1, str(ROOT/'research/agents/regional_ge_integration_20260928/evidence'))
import numpy as np
import pandas as pd
from ModelData import ModelData
from PPRCalculator import PPRCalculator
from runtime_codec import encode, decode

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, obj): (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
def save_state(name,obj):
    raw=json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False).encode('utf-8')
    (OUT/(name+'.gz')).write_bytes(gzip.compress(raw,mtime=0))
def rel(p): return p.relative_to(ROOT).as_posix()
protected_paths = [p for p in (ROOT/'regions/LME/LME_049').rglob('*') if p.is_file() and '/work/' not in p.as_posix() and OUT.parent not in p.parents]
protected = {rel(p):sha(p) for p in protected_paths}
save('protected_before.json', protected)
hashes=json.loads((EV/'diagnostic_code_hashes.json').read_text(encoding='utf-8'))
for name in ('ModelData.py','PPRCalculator.py','utils.py'):
    expected=next(v for k,v in hashes.items() if k.endswith('PPREstimation\\'+name))
    assert sha(ENGINE/name)==expected, name
assert sha(MODEL/'model.json')=='ce1c22a1e20e2a5de8a8ac75e6ddb00c3f0db619849354df9f1527277e36d15c'
state_path=MODEL/'model_validation/evidence/source_review/diet_reextraction_20261002/reloaded_runtime_state.json'
state=json.loads(state_path.read_text(encoding='utf-8'))
c=PPRCalculator.__new__(PPRCalculator)
c.__dict__.update(decode(state))
settings=json.loads((EV/'diagnostic_settings.json').read_text(encoding='utf-8'))['loader_options']
input_dir=OUT.parent/'inputs'
input_dir.mkdir(exist_ok=True)
named_input=input_dir/(MODEL.name+'.json')
named_input.write_bytes((MODEL/'model.json').read_bytes())
assert sha(named_input)==sha(MODEL/'model.json')
with warnings.catch_warnings(record=True) as caught:
    fresh=PPRCalculator.from_modeldata(ModelData(str(named_input)), **settings)
    reconstructed_equal=encode(vars(fresh))==state
named_input.unlink()
input_dir.rmdir()
fresh_encoded=encode(vars(fresh))
state_differences=[]
def compare_state(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        for k in set(a)|set(b): compare_state(a.get(k),b.get(k),path+'/'+str(k))
    elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        for i,(x,y) in enumerate(zip(a,b)):compare_state(x,y,path+'/'+str(i))
    elif a!=b: state_differences.append({'path':path,'saved':a,'fresh':b})
compare_state(state,fresh_encoded)
save('fresh_state_differences.json',state_differences)
save('fresh_groups.json',encode(fresh._groups_df))
save('reconstruction.json', {'saved_runtime_sha256':sha(state_path),'constructor':settings,'fresh_complete_state_exact_equal':reconstructed_equal,'warnings':[str(w.message) for w in caught], 'engine':{n:sha(ENGINE/n) for n in ('ModelData.py','PPRCalculator.py','utils.py')},'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'runtime_used':'unchanged saved audited state; fresh initialization compared separately','ee_floor':'archived pre-floor engine; no floor transformation'})
DC=c.get_DC(DET_as_PP=True,normalize=False)
flow=c.get_Z(DET_as_PP=True)
pred_from_diet=flow.sum(axis=0).reindex(c.predation.index)
delta=pred_from_diet-c.predation
source=json.loads((MODEL/'model.json').read_text(encoding='utf-8'))
source_groups={int(g['group_seq']):g for g in source['group']}
audit=pd.DataFrame({'name':pd.Series(c.seq2name),'p':c.p,'q':c.q,'M0':c.M0,'EE':c.EE,'GE':c.GE,'catch':c.catch,'BA':c.growth,'net_migration':c.net_migration,'predation_stored':c.predation,'predation_from_loaded_diet':pred_from_diet,'predation_difference':delta,'TE':c.get_TE('TE',as_matrix=False)})
audit.to_csv(OUT/'flow_audit.csv',index_label='group_id')
flow.to_csv(OUT/'loaded_consumption_flows.csv',index_label='consumer_id')
results={}
negative=[]
for option in ('GE','TE','With Egestion'):
    key=option.replace(' ','_')
    # Isolated object per option prevents diagnostic caches crossing method boundaries.
    calc=copy.deepcopy(c)
    before=encode(vars(calc))
    with warnings.catch_warnings(record=True) as caught:
        ret=calc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
    report,S,A,L=ret
    save(key+'_full_return.json',encode(ret))
    save_state(key+'_state_before.json',before)
    save_state(key+'_state_after.json',encode(vars(calc)))
    save(key+'_diagnostic.json',report)
    S.to_csv(OUT/(key+'_source_coefficients.csv'),index_label='recipient_id')
    A.to_csv(OUT/(key+'_A.csv'),index_label='recipient_id')
    L.to_csv(OUT/(key+'_L.csv'),index_label='recipient_id')
    s=S.sum(axis=1).reindex(c.p.index)
    diet_s=DC.reindex(index=s.index,columns=s.index)@s
    budget=(c.catch+c.growth+c.net_migration)*s
    production_res=(c.catch+c.predation+c.growth+c.net_migration+c.M0-c.p)
    detail=pd.DataFrame({'name':pd.Series(c.seq2name),'SPPR':s,'diet_weighted_SPPR':diet_s,'catch_weighted':c.catch*s,'BA_weighted':c.growth*s,'migration_weighted':c.net_migration*s,'budget_outflow':budget,'predation_mismatch_weighted':delta*s,'production_residual':production_res,'production_residual_weighted':production_res*s,'p_SPPR':c.p*s,'q_diet_SPPR':c.q*diet_s,'M0_SPPR':c.M0*s})
    detail.to_csv(OUT/(key+'_budget_decomposition.csv'),index_label='group_id')
    for recipient in S.index:
        for basal in S.columns:
            value=float(S.loc[recipient,basal])
            if value<0: negative.append({'method':option,'matrix':'SPPR','recipient_id':int(recipient),'recipient_name':c.seq2name[recipient],'source_id':int(basal),'source_name':c.seq2name[basal],'value':value,'comparison_tolerance':0})
    old=json.loads((EV/'evidence'/('diagnose_sppr_'+key+'.json')).read_text(encoding='utf-8'))['direct_diagnose_sppr_return']
    results[option]={'report_equal_saved':json.loads(json.dumps(report))==old,'status':report['status'],'balance':report['balance'],'warnings':[str(w.message) for w in caught], 'predation_mismatch_weighted_sum':float((delta*s).sum()),'production_residual_weighted_sum':float((production_res*s).sum()),'seabird':detail.loc[3].to_dict(),'toothed_whale':detail.loc[2].to_dict(),'all_coefficients_finite':bool(np.isfinite(S.to_numpy()).all()),'full_return_roundtrip_equal':encode(decode(json.loads((OUT/(key+'_full_return.json')).read_text(encoding='utf-8'))))==encode(ret)}
    print(option, json.dumps({k:results[option][k] for k in ('report_equal_saved','status','balance','predation_mismatch_weighted_sum','production_residual_weighted_sum')}),flush=True)
save('negative_entries.json',negative)
save('summary.json',{'methods':results,'seabird_source':source_groups[3],'toothed_whale_source':source_groups[2],'seabird_runtime':audit.loc[3].to_dict(),'toothed_whale_runtime':audit.loc[2].to_dict(),'predation_delta_equals_seabird_consumption':bool(np.allclose(delta,flow.loc[3].reindex(delta.index),atol=1e-12,rtol=0)),'predation_delta_max':float(delta.abs().max()),'input_state_unchanged':encode(vars(c))==state})
changed=[p for p,h in protected.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
save('preservation.json',{'protected_files':len(protected),'changed':changed,'canonical_unchanged':sha(MODEL/'model.json')==protected[rel(MODEL/'model.json')],'no_adoption':True})
assert not changed
assert all(v['full_return_roundtrip_equal'] for v in results.values())
print('fresh_state_equal',reconstructed_equal,'protected_files',len(protected),'changed',changed,flush=True)
