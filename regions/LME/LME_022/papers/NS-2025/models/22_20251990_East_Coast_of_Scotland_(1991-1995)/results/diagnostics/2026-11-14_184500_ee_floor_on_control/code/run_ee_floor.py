"""Authorized GE/TE EE-floor experiment on exact archived corrected Scotland state.

No canonical constructor, parameter repair, workbook/adoption/selection write.
Freeze commit bytes; restore audited state; verify same-engine OFF then apply ON.
"""
from __future__ import annotations
import copy
from datetime import datetime, timezone
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

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
RUN = Path(__file__).resolve().parents[1]
MODEL = RUN.parents[2]
OLD = MODEL/'results/diagnostics/2026-11-14_171200_seabird_derived_ba'
ENGINE = RUN/'code/PPREstimation'
COMMIT = '38cb75d066c5f78d47ba20fc6ab8545a9a6d5c69'
EXPECTED_ENGINE = {
    'PPRCalculator.py':'ee34361a2048c78301b1d8a5172d25c37d77034b9e67c77b7a6794d5ce784b51',
    'ModelData.py':'64c7769ed1494ccadf71dea333765989964ce8c4be9575143b6bc4cbbc6cc680',
    'utils.py':'817f969850b250d06563cfff2e5d1be0fdf70bacb7a3c4ac317bf69c805ca07f'}
OPTIONS = dict(det_collapse_mode='never',det_open_mode='none',det_theta=1,
               det_external_sppr=0,fix_EE_0_cases=True)
VARIANT = 'seabird_no_self_loop_proportional_prey_derived_ba'
SOURCE_FILES = [MODEL/'model.json',MODEL/'model_validation/validation.docx',
    MODEL/'model_validation/taxon_mapping.xlsx',MODEL/'results/regional_snapshot.xlsx',
    ROOT/'regions/LME/LME_022/LME_022.xlsx',ROOT/'Project.xlsx',
    OLD/'run_manifest.json',OLD/'inputs/runtime_state_corrected.json',
    MODEL/'model_validation/evidence/source_review/taxon_audit.json']
SOURCE_FILES += list((OLD/'outputs').glob('corrected_*.json'))

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def rel(p): return os.path.relpath(p,RUN).replace('\\','/')

def initialize():
    global np,pd,PPRCalculator,ModelData,h
    ENGINE.mkdir(parents=True,exist_ok=True)
    for name,expected in EXPECTED_ENGINE.items():
        raw = subprocess.check_output(['git','show',f'{COMMIT}:tools/scientific_code/PPREstimation/{name}'],cwd=ROOT)
        assert hashlib.sha256(raw).hexdigest()==expected,(name,'Pinned byte mismatch')
        p=ENGINE/name
        if p.exists(): assert p.read_bytes()==raw
        else: p.write_bytes(raw)
    import numpy as np
    import pandas as pd
    sys.path.insert(0,str(ENGINE))
    from PPRCalculator import PPRCalculator
    from ModelData import ModelData
    for name in ('PPRCalculator','ModelData','utils'):
        assert Path(sys.modules[name].__file__).resolve()==ENGINE/(name+'.py')
    helper=MODEL/'results/diagnostics/2026-11-14_163501_seabird_self_loop/code/check_self_loop.py'
    SOURCE_FILES.append(helper)
    spec=importlib.util.spec_from_file_location('retained_lossless_codec',helper)
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    h.np,h.pd,h.PPRCalculator,h.ModelData=np,pd,PPRCalculator,ModelData
    original=h.encode
    def encode(value):
        if isinstance(value,(PPRCalculator,ModelData)):
            return {'type':type(value).__name__,'attributes':encode(value.__dict__)}
        return original(value)
    h.encode=encode

def decode(value):
    if isinstance(value,list): return [decode(x) for x in value]
    if not isinstance(value,dict): return value
    k=value.get('type')
    if k=='float': return float(value['value'])
    if k=='dict': return {decode(a):decode(b) for a,b in value['items']}
    if k=='Series': return pd.Series(decode(value['values']),index=decode(value['index']),name=decode(value['name']))
    if k=='DataFrame': return pd.DataFrame(decode(value['values']),index=decode(value['index']),columns=decode(value['columns']))
    if k=='ndarray': return np.array(decode(value['values']),dtype=value['dtype'])
    if k=='tuple': return tuple(decode(x) for x in value['items'])
    if k in ('ModelData','PPRCalculator'):
        cls={'ModelData':ModelData,'PPRCalculator':PPRCalculator}[k]
        obj=cls.__new__(cls);obj.__dict__.update(decode(value['attributes']));return obj
    return {key:decode(v) for key,v in value.items()}

def equal(a,b):
    if isinstance(a,pd.DataFrame):
        pd.testing.assert_frame_equal(a.sort_index().sort_index(axis=1),b.reindex(index=a.index,columns=a.columns).sort_index().sort_index(axis=1),check_exact=True,check_dtype=False)
    elif isinstance(a,pd.Series):
        pd.testing.assert_series_equal(a.sort_index(),b.reindex(a.index).sort_index(),check_exact=True,check_dtype=False,check_names=False)
    else: assert h.digest_value(a)==h.digest_value(b)

def compare_matrix(a,b):
    assert set(a.index)==set(b.index) and set(a.columns)==set(b.columns)
    b=b.loc[a.index,a.columns]
    delta=np.abs(a.to_numpy(float)-b.to_numpy(float))
    return {'exact':bool(np.array_equal(a.to_numpy(),b.to_numpy())),
        'max_abs':float(delta.max()),'max_relative':float((delta/np.maximum(np.abs(b.to_numpy(float)),1e-300)).max()),
        'within_1e12_tolerance':bool(np.allclose(a,b,rtol=1e-12,atol=1e-12))}

def run_method(calc,config,method):
    before=h.runtime(calc);t=time.monotonic()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        diagnostic,S,A,L=calc.diagnose_sppr(TE_option=method,short=False,flat=False,return_sppr=True,**OPTIONS)
    for key in before: equal(before[key],getattr(calc,key))
    negative=[]
    matrices={'SPPR':S,'A':A,'L':L}
    for label,matrix in matrices.items():
        if matrix is None: continue
        for i,j in np.argwhere(matrix.to_numpy(float)<-1e-10):
            rid,cid=matrix.index[i],matrix.columns[j]
            negative.append(dict(matrix=label,row_id=int(rid),row_name=calc.seq2name[rid],
                column_id=int(cid),column_name=calc.seq2name[cid],value=float(matrix.iloc[i,j]),tolerance=1e-10))
    result=dict(configuration=config,variant_id=VARIANT,method=method,elapsed_seconds=time.monotonic()-t,
        diagnostic=diagnostic,**matrices,negative_entries=negative,
        runtime_warnings=[{'category':w.category.__name__,'message':str(w.message)} for w in caught],
        group_names=calc.seq2name,synthetic_group_ids=[26],
        axes={'SPPR':'rows recipient groups; columns basal sources','A':'recipient by donor','L':'A-I'},
        units={'SPPR':'tonnes wet basal-source equivalents per tonne wet recipient',
               'runtime_flows':'tonnes wet weight km^-2 year^-1'},
        scope_definitions={'PP':[1],'inner':[1,25],'all':[1,25,26]},
        scientific_state_unchanged_by_diagnostic=True,options=OPTIONS,
        runtime_before=before,runtime_after=h.runtime(calc))
    h.save(RUN/f'outputs/{config}_{method}.json',result)
    if S is None: return result,{}
    assert set(S.index)==set(range(1,27)) and set(S.columns)=={1,25,26}
    assert np.isfinite(S.to_numpy(float)).all() and (S.to_numpy(float)>=0).all()
    scopes={'PP':S[[1]].sum(axis=1),'inner':S[[1,25]].sum(axis=1),'all':S.sum(axis=1)}
    h.save(RUN/f'outputs/{config}_{method}_scopes.json',scopes)
    return result,scopes

def arithmetic(scopes,config):
    audit=read(MODEL/'model_validation/evidence/source_review/taxon_audit.json')
    rows=[]
    for row in audit:
        groups=row['groups'];catch=row['catch_tonnes']
        r={'taxon':row['taxon'],'catch_tonnes':catch,'confidence':row['overall_confidence'],'mapping_resolved':bool(groups),'groups':groups,'methods':{}}
        for method,source_scopes in scopes.items():
            r['methods'][method]={}
            for scope,coef in source_scopes.items():
                included=[g for g in groups if g['seq'] not in (22,23,24)]
                sppr=sum(g['weight']*coef[g['seq']] for g in included) if groups else None
                ppr=catch*sppr/9 if sppr is not None else (0. if catch==0 else None)
                r['methods'][method][scope]={'sppr_wet':sppr,'ppr_tC':ppr}
        rows.append(r)
    totals={m:{scope:sum(r['methods'][m][scope]['ppr_tC'] or 0 for r in rows) for scope in scopes[m]} for m in scopes}
    output={'configuration':config,'year':2019,'catch_basis':'catch','formula':'catch_tonnes * sum(weight * scope SPPR) / 9',
        'mapping_source':rel(MODEL/'model_validation/evidence/source_review/taxon_audit.json'),
        'signed_exclusions':[22,23,24],'signed_exclusion_treatment':'omit recipient allocations without renormalizing; retain trophic nodes',
        'excluded_allocated_catch_tonnes':sum(r['catch_tonnes']*sum(g['weight'] for g in r['groups'] if g['seq'] in (22,23,24)) for r in rows),
        'total_catch_tonnes':sum(r['catch_tonnes'] for r in rows),'unresolved_catch_tonnes':sum(r['catch_tonnes'] for r in rows if not r['mapping_resolved']),
        'totals_are_known_subtotals':True,'totals_tC':totals,'rows':rows}
    h.save(RUN/f'outputs/{config}_2019_ppr.json',output)
    return output

def main():
    initialize()
    for p in ('inputs','outputs','qa'): (RUN/p).mkdir(exist_ok=True)
    protected={rel(p):sha(p) for p in SOURCE_FILES}
    assert sha(MODEL/'model.json')=='5cda503a847a6ea9bdcda077c184ac20119e0d8b47b064f93b72b72e3d7df691'
    assert sha(MODEL/'model_validation/validation.docx')=='500a5734b3e6de8924af64c5b0abf59ed0c368f91fd1b817dabda4ff79e3fbf5'
    assert sha(OLD/'inputs/runtime_state_corrected.json')=='cff44376eb16b9ea1df62898230cdef976bee9d2361242ef6f950d1709b02d4a'
    old_manifest=read(OLD/'run_manifest.json')
    manifest={'schema_version':1,'run_id':RUN.name,'model_id':MODEL.name,'variant_id':VARIANT,
        'started_utc':datetime.now(timezone.utc).isoformat(),'methods':['GE','TE'],
        'authorization':'User requested EE floor ON for Scotland comparison; parent authorized same-engine OFF control to isolate floor effect',
        'constructor':'No canonical constructor or from_dict replay; exact __new__ archived corrected-state restore',
        'calculation_engine_upgrade':'ee_floor_v1','frozen_engine_commit':COMMIT,'frozen_engine_sha256':EXPECTED_ENGINE,
        'historical_base_engine_sha256':old_manifest['historical_engine_sha256'],
        'historical_constructor_record':old_manifest['historical_constructor_record'],
        'historical_corrected_runtime_path':rel(OLD/'inputs/runtime_state_corrected.json'),
        'canonical_model_sha256':sha(MODEL/'model.json'),'method_options':OPTIONS,
        'ee_floor':.1,'ee_threshold':.1,'configurations':{'control_off':False,'ee_floor_on':True},
        'excluded_from_scope':['With Egestion rerun','Monte Carlo','adoption','selection','workbook writes','canonical changes'],
        'expected_bound':'4 diagnostic calls (OFF/ON x GE/TE); no scientific inventory; local evidence only',
        'protected_inputs_before':protected,'python':sys.version,'platform':platform.platform(),
        'modules':{x:importlib.metadata.version(x) for x in ('numpy','pandas','scipy','sympy','igraph')},
        'executed_module_paths':{x:rel(Path(sys.modules[x].__file__)) for x in ('PPRCalculator','ModelData','utils')}}
    h.save(RUN/'run_manifest.json',manifest)
    calc=PPRCalculator.__new__(PPRCalculator)
    calc.__dict__.update(decode(read(OLD/'inputs/runtime_state_corrected.json')))
    restored=h.runtime(calc)
    source_groups={int(g['group_seq']):g for g in read(MODEL/'model.json')['group']}
    assert all(float(g['other_mort'])==-9999 for g in source_groups.values()),'Source M0 needs separate interpretation'
    calc.source_EE=pd.Series({i:float(g['ee']) if float(g['ee'])!=-9999 else np.nan for i,g in source_groups.items()}).reindex(calc.p.index)
    calc.source_M0=pd.Series(np.nan,index=calc.p.index)
    calc._source_groups_before_completion=calc._model.groups_data.copy(deep=True)
    calc._initialization_settings={'initialization':'exact archived corrected state; historical constructor record authoritative',
        'source_missing_M0':'All canonical other_mort=-9999; independent source M0 is unknown',
        'calculation_engine_upgrade':'ee_floor_v1'}
    h.save(RUN/'inputs/exact_restored_state.json',calc.__dict__)
    calc.apply_ee_floor(False,.1,.1)
    for key in restored: equal(restored[key],getattr(calc,key))
    h.save(RUN/'inputs/control_off_state.json',calc.__dict__)
    results={};summaries={};parity={};all_scopes={}
    for config,on in [('control_off',False),('ee_floor_on',True)]:
        if on:
            base=h.runtime(calc)
            calc.apply_ee_floor(True,.1,.1)
            living=[i for i in calc.p.index if i in source_groups and source_groups[i]['pp']!='2']
            for key in ('_DC','_det_fate','catch','predation','immigration','emigration','net_migration','respiration','egestion','GE','GS','TL'):
                equal(base[key],getattr(calc,key))
            for key in ('p','q','growth'): equal(base[key].loc[living],getattr(calc,key).loc[living])
            for col in ('biomass','pb','qb'):
                equal(base['_groups_df'].loc[living,col],calc._groups_df.loc[living,col])
            assert set(calc.ee_floor_info['affected_groups'])=={22,23,24}
            assert math.isclose(calc.external_mortality_export.sum(),.000508,rel_tol=1e-12,abs_tol=1e-15)
            h.save(RUN/'inputs/ee_floor_on_state.json',calc.__dict__)
        h.save(RUN/f'inputs/{config}_floor_ledger.json',{'ledger':calc.ee_floor_ledger,'info':calc.ee_floor_info,
            'source_EE':calc.source_EE,'source_M0':calc.source_M0,'EE_before_floor':calc.EE_before_floor,'M0_before_floor':calc.M0_before_floor,
            'EE_effective':calc.EE,'M0_effective':calc.M0,'external_mortality_export':calc.external_mortality_export,
            'detritus_accounting':[dict(group_id=int(i),name=calc.seq2name[i],inflow=float(calc.p[i]),stock_residual=float(calc.growth[i]),
                predation=float(calc.predation[i]),catch=float(calc.catch[i]),net_migration=float(calc.net_migration[i]),effective_EE=float(calc.EE[i])) for i in calc.get_DET_seq()]})
        results[config]={};all_scopes[config]={}
        for method in ('GE','TE'):
            result,scopes=run_method(calc,config,method)
            results[config][method]=result;all_scopes[config][method]=scopes
            d=result['diagnostic']
            summaries[f'{config}_{method}']={'status':d['status'],'rho_living':d['divergence']['rho_living'],'b':d['divergence']['b'],
                'strict_model_balanced':d['model_input']['is_model_balanced'],'strict_sppr_balanced':d['balance']['is_balanced'],
                'warnings':d['warnings'],'runtime_warnings':result['runtime_warnings']}
            if config=='control_off':
                historical=decode(read(OLD/f'outputs/corrected_{method}.json'))
                parity[method]={name:compare_matrix(result[name],historical[name]) for name in ('SPPR','A','L')}
                assert all(v['within_1e12_tolerance'] for v in parity[method].values()),('Historical OFF differs',parity[method])
            print(json.dumps({'configuration':config,'method':method,**summaries[f'{config}_{method}']},ensure_ascii=False),flush=True)
        arithmetic(all_scopes[config],config)
    protected_after={rel(p):sha(p) for p in SOURCE_FILES}
    assert protected==protected_after,'Protected input changed during execution'
    h.save(RUN/'qa/verification.json',{'protected_inputs_unchanged':True,'exact_restored_scientific_state_preserved_by_OFF':True,
        'floor_preserves_living_biology':True,'historical_OFF_parity':parity,'diagnostics':summaries,
        'floor_info':calc.ee_floor_info,'methods_called':4,'no_Egestion_rerun':True})
    manifest.update(completed_utc=datetime.now(timezone.utc).isoformat(),protected_inputs_after=protected_after,
        complete=True,historical_off_parity=parity,diagnostic_summary=summaries)
    h.save(RUN/'run_manifest.json',manifest)
    print(json.dumps({'completed':rel(RUN/'run_manifest.json'),'floor_info':calc.ee_floor_info},ensure_ascii=False),flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    try: main()
    except Exception:
        (RUN/'qa').mkdir(parents=True,exist_ok=True)
        (RUN/'qa/execution_error.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise
