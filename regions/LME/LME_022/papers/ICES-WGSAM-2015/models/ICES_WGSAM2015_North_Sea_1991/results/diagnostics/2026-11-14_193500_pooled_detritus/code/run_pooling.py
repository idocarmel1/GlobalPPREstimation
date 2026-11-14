"""Authorized ICES forced pooled-detritus scaling, GE/TE only.

Exact reviewed runtime restoration; no constructor, floor, group, diet, canonical,
mapping, workbook or adoption changes. Never controls authenticate restoration.
"""
from __future__ import annotations
import copy
from datetime import datetime,timezone
import gzip
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
import warnings
sys.dont_write_bytecode=True
RUN=Path(__file__).resolve().parents[1]
MODEL=RUN.parents[2]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
OLD=MODEL/'results/diagnostics/2026-11-14_loader_repair'
ENGINE=RUN/'code/PPREstimation'
SCOT=ROOT/'regions/LME/LME_022/papers/NS-2025/models/22_20251990_East_Coast_of_Scotland_(1991-1995)'
HELPER=SCOT/'results/diagnostics/2026-11-14_163501_seabird_self_loop/code/check_self_loop.py'
MAPPING=MODEL/'model_validation/evidence/mapping/mapping_decisions.json'
COMMIT='38cb75d066c5f78d47ba20fc6ab8545a9a6d5c69'
CODE_HASHES={'PPRCalculator.py':'ee34361a2048c78301b1d8a5172d25c37d77034b9e67c77b7a6794d5ce784b51',
    'ModelData.py':'64c7769ed1494ccadf71dea333765989964ce8c4be9575143b6bc4cbbc6cc680',
    'utils.py':'817f969850b250d06563cfff2e5d1be0fdf70bacb7a3c4ac317bf69c805ca07f'}
OLD_NAMES={'GE':'new_GE','TE':'new_TE_EEfix'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return os.path.relpath(p,RUN).replace('\\','/')
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())

def initialize():
    global np,pd,PPRCalculator,ModelData,h
    ENGINE.mkdir(parents=True,exist_ok=True)
    for name,expected in CODE_HASHES.items():
        raw=subprocess.check_output(['git','show',f'{COMMIT}:tools/scientific_code/PPREstimation/{name}'],cwd=ROOT)
        assert hashlib.sha256(raw).hexdigest()==expected
        p=ENGINE/name
        if p.exists():assert p.read_bytes()==raw
        else:p.write_bytes(raw)
    import numpy as np
    import pandas as pd
    sys.path.insert(0,str(ENGINE))
    from PPRCalculator import PPRCalculator
    from ModelData import ModelData
    for name in ('PPRCalculator','ModelData','utils'):
        assert Path(sys.modules[name].__file__).resolve()==ENGINE/(name+'.py')
    spec=importlib.util.spec_from_file_location('retained_lossless_codec',HELPER)
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    h.np,h.pd,h.PPRCalculator,h.ModelData=np,pd,PPRCalculator,ModelData

def decode(v):
    """Decode retained pipeline format, restoring separate nonfinite masks."""
    if isinstance(v,list):return [decode(x) for x in v]
    if not isinstance(v,dict):return v
    kind=v.get('type')
    if kind=='dataframe':
        data=decode(v['data'])
        for mask,value in [('null',None),('nan',np.nan),('positive_infinity',np.inf),('negative_infinity',-np.inf)]:
            for i,row in enumerate(v.get('masks',{}).get(mask,[])):
                for j,flag in enumerate(row):
                    if flag:data[i][j]=value
        df=pd.DataFrame(data,index=decode(v['index']),columns=decode(v['columns']))
        for col,dtype in zip(df.columns,v.get('dtypes',[])):df[col]=df[col].astype(dtype)
        df.index.names=v.get('index_names',[None]);df.columns.names=v.get('column_names',[None])
        return df
    if kind=='series':
        frame=decode(v['frame']);return frame.iloc[:,0].rename(decode(v['name']))
    if kind in ('mapping','dict'):return {decode(a):decode(b) for a,b in v['items']}
    if kind=='tuple':return tuple(decode(x) for x in v['items'])
    if kind=='float':return float(v['value'])
    if kind=='ndarray':return np.array(decode(v.get('data',v.get('values'))),dtype=v.get('dtype'))
    return {k:decode(x) for k,x in v.items()}

def matrix_diff(a,b):
    assert list(a.index)==list(b.index) and list(a.columns)==list(b.columns)
    av,bv=a.to_numpy(float),b.to_numpy(float);delta=np.abs(av-bv)
    return {'exact':bool(np.array_equal(av,bv)),'max_abs':float(delta.max()),
        'within_1e12':bool(np.allclose(av,bv,rtol=1e-12,atol=1e-12))}

def scientific(calc,fields):return {key:copy.deepcopy(getattr(calc,key)) for key in fields}

def pooling_ledger(calc,S,baseline,method,info):
    ids=list(calc.get_DET_seq());assert set(ids)=={67,68,69}
    q_total=sum(float(calc.q[i]) for i in ids if calc.q[i]>0)
    fate=calc._det_fate.reindex(index=calc.M0.index,columns=ids).fillna(0).sum(axis=1).clip(lower=0,upper=1)
    returned=calc._discard_return_matrix().sum(axis=1).reindex(calc.M0.index,fill_value=0)
    basal=calc.get_PP_seq()+calc.get_Import_seq()
    mortality=calc.M0.where(calc.M0.index.isin(basal),0.) if method=='TE' else calc.M0
    weights=((mortality*fate+returned)/q_total).fillna(0)
    raw=baseline[ids].div(pd.Series({i:baseline.loc[i,i] for i in ids}),axis=1)
    non_det=baseline[basal].sum(axis=1)
    a=float(weights@non_det);b=float(weights@raw.sum(axis=1));scalar=a/(1-b)
    assert math.isclose(a,info['collapse_a'],rel_tol=1e-12,abs_tol=1e-12)
    assert math.isclose(b,info['collapse_b'],rel_tol=1e-12,abs_tol=1e-12)
    assert math.isclose(scalar,info['collapse_scalar'],rel_tol=1e-12,abs_tol=1e-12)
    assert np.allclose(S[ids],raw*scalar,rtol=1e-12,atol=1e-10)
    return {'semantics':'Shared detritus SPPR scaling a/(1-b) across retained source columns; no physical group/diet merge',
        'detritus_group_ids':ids,'detritus_group_names':[calc.seq2name[i] for i in ids],
        'q_combined':q_total,'internal_discard_return_total':float(returned.sum()),
        'retained_original_discard_returns':calc._discard_returns,'fate_to_modeled':fate,
        'method_mortality':mortality,'returned_by_donor':returned,'pooled_weights':weights,
        'raw_detritus_basis_from_retained_control':raw,'non_detritus_SPPR':non_det,
        'independent_a':a,'independent_b':b,'independent_scalar':scalar,
        'detritus_resolution_info':info,'all_living_parameters_and_flows_unchanged':True,
        'source_destinations_preserved_but_common_scaling_assumed':True}

def arithmetic(all_scopes,config,mapping):
    rows=[]
    for item in mapping['rows']:
        groups=item['groups'];assert groups and math.isclose(sum(g['weight'] for g in groups),1,rel_tol=1e-12,abs_tol=1e-12)
        r={'taxon':item['taxon'],'catch_tonnes':item['catch_tonnes'],'overall_confidence':item['overall_confidence'],'groups':groups,'methods':{}}
        for method,scopes in all_scopes.items():
            r['methods'][method]={}
            for scope,coef in scopes.items():
                sppr=sum(g['weight']*coef[g['group_id']] for g in groups)
                r['methods'][method][scope]={'sppr_wet':sppr,'ppr_tC':item['catch_tonnes']*sppr/9}
        rows.append(r)
    totals={m:{scope:sum(r['methods'][m][scope]['ppr_tC'] for r in rows) for scope in sc} for m,sc in all_scopes.items()}
    report={'configuration':config,'year':2019,'catch_basis':'catch = landings plus discards','formula':'catch_tonnes * sum(weight * scope coefficient) / 9',
        'mapping_status':mapping['status'],'mapping_sha256':sha(MAPPING),'taxa':len(rows),'total_catch_tonnes':sum(r['catch_tonnes'] for r in rows),
        'unresolved_taxa':0,'totals_tC':totals,'rows':rows,'adopted':False}
    h.save(RUN/f'outputs/{config}_2019_ppr.json',report);return report

def main():
    initialize()
    for name in ('inputs','outputs','qa'):(RUN/name).mkdir(exist_ok=True)
    protected=[MODEL/'model.json',MODEL/'model_validation/validation.docx',MODEL/'model_validation/taxon_mapping.xlsx',MAPPING,
        ROOT/'regions/LME/LME_022/LME_022.xlsx',ROOT/'Project.xlsx',HELPER]
    protected+=list(OLD.iterdir())
    hashes={rel(p):sha(p) for p in protected if p.is_file()}
    assert sha(MODEL/'model.json')=='450e0f43822a34a02d4d26ad71358aeef32af8daaff7fcf07cd95ef2131cf97a'
    assert sha(MAPPING)=='b0be4c37e3f5b1827f2c0e64f08f5cb84a5f963368f71f1fc63e20fe32fe3c81'
    saved={m:read(OLD/(name+'.json.gz')) for m,name in OLD_NAMES.items()}
    restored=decode(saved['GE']['runtime_before']);fields=list(restored)
    assert h.digest_value(restored)==h.digest_value(decode(saved['TE']['runtime_before']))
    calc=PPRCalculator.__new__(PPRCalculator);calc.__dict__.update(copy.deepcopy(restored))
    calc.n_groups=len(calc._groups_df);calc.is_underdetermined=False;calc.n_balance_runs=0
    calc.is_balanced=calc.is_model_balanced()[0]
    assert calc.n_groups==70 and set(calc.get_DET_seq())=={67,68,69}
    assert calc.use_ee_floor is True and calc.ee_floor==.1 and calc._has_discard_returns()
    h.save(RUN/'inputs/restored_runtime.json',scientific(calc,fields))
    h.save(RUN/'inputs/source_state.json',read(OLD/'constructor.json.gz')['constructor_outcome']['source_state'])
    manifest={'schema_version':1,'run_id':RUN.name,'model_id':MODEL.name,'variant_id':'reviewed_ICES_EE_floor_ON0.1_forced_pooled_detritus_scaling',
        'started_utc':datetime.now(timezone.utc).isoformat(),'authorization':'Explicit user request for ICES pooled detritus results; GE/TE sensitivity only',
        'engine_commit':COMMIT,'engine_sha256':CODE_HASHES,'canonical_sha256':sha(MODEL/'model.json'),
        'runtime_source':rel(OLD/'new_GE.json.gz'),'runtime_source_field':'runtime_before','constructor':'No constructor/floor replay; exact saved runtime restore',
        'restored_metadata':{'n_groups':70,'is_underdetermined':False,'n_balance_runs':0,'is_balanced':'derived strict check only, no balancing routine'},
        'floor':{'use_ee_floor':True,'ee_floor':.1,'ee_threshold':.1},'methods':['GE','TE'],
        'configurations':{'control_never':'never','pooled_always':'always'},'pool_group_ids':[67,68,69],
        'semantics':'Shared SPPR detritus scaling; retained70groups and source columns, diets, fate, discard return matrix and all flows',
        'baseline_options':{m:saved[m]['settings']['kwargs'] for m in saved},
        'protected_inputs_before':hashes,'python':sys.version,'platform':platform.platform(),
        'modules':{x:importlib.metadata.version(x) for x in ('numpy','pandas','scipy','sympy','igraph')},
        'excluded_from_scope':['With Egestion rerun','source/canonical edits','mapping changes','literal group merge','workbook/selection/adoption'],
        'expected_execution':'2 bounded matching controls +2 pooled calls, no other methods', 'complete':False}
    h.save(RUN/'run_manifest.json',manifest)
    mapping=read(MAPPING);assert len(mapping['rows'])==384
    for row in mapping['rows']:
        for group in row['groups']:
            assert calc.seq2name[group['group_id']]==group['group_name']
            assert group['group_id'] not in (66,67,68,69,70)
    outcomes={};parity={};totals={};all_scopes={}
    for config,collapse in [('control_never','never'),('pooled_always','always')]:
        all_scopes[config]={}
        for method in ('GE','TE'):
            kwargs=copy.deepcopy(saved[method]['settings']['kwargs']);kwargs['det_collapse_mode']=collapse
            before=scientific(calc,fields);t=time.monotonic()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always');d,S,A,L=calc.diagnose_sppr(**kwargs)
            after=scientific(calc,fields);assert h.digest_value(before)==h.digest_value(after)
            info=copy.deepcopy(getattr(calc,'detritus_resolution_info',{}))
            negative=[]
            for label,mat in [('SPPR',S),('A',A),('L',L)]:
                if mat is None:continue
                for i,j in np.argwhere(mat.to_numpy(float)<-1e-10):
                    rid,cid=mat.index[i],mat.columns[j]
                    negative.append({'matrix':label,'row_id':int(rid),'row_name':calc.seq2name[rid],
                        'column_id':int(cid),'column_name':calc.seq2name[cid],'value':float(mat.iloc[i,j]),'tolerance':1e-10})
            output={'configuration':config,'method':method,'diagnostic':d,'SPPR':S,'A':A,'L':L,
                'runtime_before':before,'runtime_after':after,'scientific_state_unchanged':True,
                'settings':kwargs,'detritus_resolution_info':info,'elapsed_seconds':time.monotonic()-t,
                'runtime_warnings':[{'category':w.category.__name__,'message':str(w.message)} for w in caught],
                'group_names':calc.seq2name,'synthetic_group_ids':[70],
                'source_scopes':{'PP':[66],'inner':[66,67,68,69],'all':[66,67,68,69,70]},
                'orientation':'SPPR rows=recipient group; columns=basal source; A/L recipient by donor',
                'units':'SPPR wet basal-source equivalents per wet recipient; runtime flows t wet km^-2 year^-1',
                'negative_entries':negative}
            h.save(RUN/f'outputs/{config}_{method}.json',output)
            outcome={'status':d['status'],'strict_model_balanced':d['model_input']['is_model_balanced'],
                'strict_SPPR_balanced':d['balance']['is_balanced'],'rho_living':d['divergence']['rho_living'],
                'diagnostic_b_original_coupled_rho_B':d['divergence']['b'],'pooling_info':info,'warnings':d['warnings']}
            outcomes[f'{config}_{method}']=outcome
            if S is None:
                print(json.dumps({'config':config,'method':method,'outcome':outcome},default=str),flush=True);continue
            assert set(S.index)==set(range(1,71)) and set(S.columns)=={66,67,68,69,70}
            if config=='control_never':
                raw=decode(saved[method]['return']);parity[method]={name:matrix_diff(mat,old) for name,mat,old in zip(('SPPR','A','L'),(S,A,L),raw[1:])}
                assert all(v['within_1e12'] for v in parity[method].values()),parity[method]
            else:
                ledger=pooling_ledger(calc,S,decode(saved[method]['source_matrix']),method,info)
                h.save(RUN/f'outputs/pooled_{method}_aggregation_ledger.json',ledger)
            scopes={'PP':S[[66]].sum(axis=1),'inner':S[[66,67,68,69]].sum(axis=1),'all':S.sum(axis=1)}
            h.save(RUN/f'outputs/{config}_{method}_scopes.json',scopes);all_scopes[config][method]=scopes
            print(json.dumps({'config':config,'method':method,'outcome':outcome},default=str),flush=True)
        totals[config]=arithmetic(all_scopes[config],config,mapping)['totals_tC']
    assert all(sha((RUN/p).resolve())==value for p,value in hashes.items())
    manifest.update(complete=True,completed_utc=datetime.now(timezone.utc).isoformat(),
        outcomes=outcomes,baseline_parity=parity,protected_inputs_unchanged=True,regional_totals_tC=totals)
    h.save(RUN/'run_manifest.json',manifest)
    h.save(RUN/'qa/verification.json',{'protected_inputs_unchanged':True,'all38runtimefields_unchanged':True,
        'all70group_ids_retained':True,'all57mappedlivinggroups_retained':True,'baseline_parity':parity,
        'discard_return_matrix_preserved':True,'pool_scalar_formula_reconciled':True,'regional_totals_tC':totals})
    print(json.dumps({'complete':True,'regional_totals_tC':totals}),flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    try:main()
    except Exception:
        (RUN/'qa').mkdir(parents=True,exist_ok=True)
        (RUN/'qa/execution_error.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
