"""Reproduce the retained Scotland runtime; no canonical model edits or new repairs."""
from pathlib import Path
import sys, json, hashlib, shutil, math
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
MODEL=HERE.parent/'22_20251990_East_Coast_of_Scotland_(1991-1995)'
sys.path.insert(0,str(MODEL/'diagnostic_code/PPREstimation'))
import numpy as np
import pandas as pd
from ModelData import ModelData
from PPRCalculator import PPRCalculator
from create_PPRS_excel import build_groups_table, _source_sums

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def encode(x):
    if isinstance(x,PPRCalculator):return {'type':'PPRCalculator','attributes':encode(vars(x))}
    if isinstance(x,ModelData):return {'type':'ModelData','attributes':encode(vars(x))}
    if isinstance(x,pd.DataFrame): return {'type':'DataFrame','index':encode(list(x.index)),'columns':encode(list(x.columns)),'values':encode(x.to_numpy().tolist())}
    if isinstance(x,pd.Series): return {'type':'Series','index':encode(list(x.index)),'values':encode(x.tolist()),'name':encode(x.name)}
    if isinstance(x,np.ndarray): return {'type':'ndarray','values':encode(x.tolist())}
    if isinstance(x,dict): return {'type':'dict','items':[[encode(k),encode(v)] for k,v in x.items()]}
    if isinstance(x,tuple): return {'type':'tuple','values':[encode(v) for v in x]}
    if isinstance(x,list): return [encode(v) for v in x]
    if isinstance(x,np.generic): x=x.item()
    if isinstance(x,float) and not math.isfinite(x):return {'type':'float','value':str(x)}
    if x is None or isinstance(x,(str,int,float,bool)):return x
    raise TypeError(type(x))
def decode(x):
    if isinstance(x,list):return [decode(v) for v in x]
    if not isinstance(x,dict):return x
    t=x['type']
    if t in ('ModelData','PPRCalculator'):
        cls=ModelData if t=='ModelData' else PPRCalculator
        obj=cls.__new__(cls);obj.__dict__.update(decode(x['attributes']));return obj
    if t=='dict':return {decode(k):decode(v) for k,v in x['items']}
    if t=='DataFrame':return pd.DataFrame(decode(x['values']),index=decode(x['index']),columns=decode(x['columns']))
    if t=='Series':return pd.Series(decode(x['values']),index=decode(x['index']),name=decode(x['name']))
    if t=='ndarray':return np.array(decode(x['values']))
    if t=='tuple':return tuple(decode(x['values']))
    if t=='float':return float(x['value'])
    raise ValueError(t)
def dump(name,x): (HERE/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def main():
    identities=json.loads((MODEL/'diagnostic_code_hashes.json').read_text(encoding='utf-8'))
    for name,expected in identities.items():assert sha(ROOT/Path(name))==expected,name
    inp=HERE/'input'/f'{MODEL.name}.json';inp.parent.mkdir(exist_ok=True)
    shutil.copy2(MODEL/'model.json',inp)
    settings=dict(underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=True,weight_flow=1.,weight_guess=1.,normalize_DC=True,DC_tol=.001)
    config=dict(det_collapse_mode='never',det_external_sppr=0,det_open_mode='none',det_theta=1)
    md=ModelData(str(inp));c=PPRCalculator.from_modeldata(md,**settings)
    print('Loaded retained runtime',flush=True)
    dump('computational_state.json',encode(vars(c)))
    restored=PPRCalculator.__new__(PPRCalculator)
    restored.__dict__.update(decode(json.loads((HERE/'computational_state.json').read_text(encoding='utf-8'))))
    assert encode(vars(c))==encode(vars(restored))
    build_groups_table(c).to_csv(HERE/'loaded_groups.csv',encoding='utf-8')
    old=pd.read_csv(MODEL/'loaded_groups.csv',index_col=0)
    new=build_groups_table(c)
    pd.testing.assert_frame_equal(new,old,check_dtype=False,check_exact=False,rtol=1e-11,atol=1e-10)
    ledger=[]
    for seq in md.groups_data.index:
        for field in md.groups_data.columns:
            if field not in c._groups_df.columns:continue
            a=md.groups_data.loc[seq,field];b=c._groups_df.loc[seq,field]
            if encode(a)!=encode(b):ledger.append({'seq':int(seq),'group':c.seq2name[seq],'field':field,'modeldata':encode(a),'runtime':encode(b)})
    for seq in md.DC.index:
        for prey in md.DC.columns:
            a=md.DC.loc[seq,prey];b=c._DC.loc[seq,prey]
            if a!=b:ledger.append({'seq':int(seq),'prey':int(prey),'field':'diet','modeldata':encode(a),'runtime':encode(b)})
    dump('loader_transformations.json',ledger)
    results={};health=[];reproduced=[]
    retained=json.loads((MODEL/'SPPR_DIAGNOSTICS.json').read_text(encoding='utf-8'))
    for option,key in [('GE','new_GE'),('TE','new_TE_EEfix'),('With Egestion','new_WithEgestion')]:
        ret=c.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,**config)
        report,sppr,A,L=ret
        dump(f'direct_{key}.json',encode(ret))
        (HERE/f'direct_{key}.txt').write_text(repr(report),encoding='utf-8')
        again=restored.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,**config)
        assert encode(ret)==encode(again),option
        flat=c._flatten_diagnostics(report)
        health.append(flat);results[key]=sppr
        old_health=next(r for r in retained['health'] if r['TE_option']==option)
        for field in ['status','divergence_rho_living','balance_rel_gap']:
            a=flat[field];b=old_health[field]
            assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12) if isinstance(a,(int,float)) else a==b,(field,a,b)
        reproduced.append({'option':option,'status':flat['status'],'exact_saved_state_reload':True,'retained_health_matches':True})
        print(option,flat['status'],flush=True)
    # Direct diagnostic returns may order basal rows differently from SPPR_new.
    # Align by native group ID, never the export helper's positional to_numpy join.
    tables={}
    for scope,sumkey in [('pp','SUM_PP'),('inner','SUM_INNER'),('all','SUM_ALL')]:
        table=pd.DataFrame(index=new.index)
        table['group_name']=[c.seq2name[int(s)] for s in table.index]
        for key,sppr in results.items():table[key]=_source_sums(c,sppr,True)[sumkey].reindex(table.index)
        tables[scope]=table
    for scope,table in tables.items():
        table.to_csv(HERE/f'group_sppr_{scope}.csv',encoding='utf-8')
        old=pd.read_excel(MODEL/'sppr_source.xlsx',sheet_name='sppr_'+('PP' if scope=='pp' else scope),index_col=0)
        for key in results:np.testing.assert_allclose(table[key],old.loc[table.index,key],rtol=1e-10,atol=1e-9)
    dump('health.json',health)
    dump('runtime_verification.json',{'canonical_sha256':sha(MODEL/'model.json'),'input_copy_sha256':sha(inp),'computational_state_sha256':sha(HERE/'computational_state.json'),'constructor':settings,'diagnostics_config':config,'engine_hashes_verified':identities,'methods':reproduced,'coefficients_match_retained_export':True,'loaded_groups_match_retained':True,'transformations':len(ledger),'state_format':'Typed JSON of all calculator attributes after audited constructor; restored without rerunning defaults. Source-faithful JSON plus exact constructor retained separately. Not a source model or author measurements.'})

if __name__=='__main__':main()
