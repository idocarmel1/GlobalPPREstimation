"""Model-local source-exact discard-return comparison; no scientific input adoption.

Restores the authenticated completed pre-floor state, preserves living flows,
and compares zero returns with source-backed native fleet returns to pool 36.
"""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
import warnings
from types import SimpleNamespace

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
WORK=Path(__file__).resolve().parents[1]
MODEL=WORK.parents[2]
OUT=WORK/'outputs/diagnostics'
PINNED=WORK/'code/engine'
SHARED=ROOT/'tools/scientific_code/PPREstimation'
LEDGER=WORK/'outputs/source/source_fisheries_ledger.json'
SAVED=MODEL/'model_validation/evidence/ee_floor_on_review/initialization_and_floor.json'
EXPECTED={'PPRCalculator.py':'5bd249eb73d61c1db77279a8a527465e4673944f377c40ca9e6100a2da0cc877',
          'ModelData.py':'64c7769ed1494ccadf71dea333765989964ce8c4be9575143b6bc4cbbc6cc680',
          'utils.py':'817f969850b250d06563cfff2e5d1be0fdf70bacb7a3c4ac317bf69c805ca07f'}
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def relative(p,base=OUT):
    return Path(os.path.relpath(p,base)).as_posix()

def mask_kind(value):
    if value is None: return 'null'
    if isinstance(value,(float,np.floating)):
        if np.isnan(value): return 'nan'
        if np.isposinf(value): return 'positive_infinity'
        if np.isneginf(value): return 'negative_infinity'
    return None

def encode(value):
    if isinstance(value,pd.DataFrame):
        raw=value.to_numpy(dtype=object)
        return {'type':'dataframe','index':encode(value.index.tolist()),'index_names':encode(list(value.index.names)),
                'columns':encode(value.columns.tolist()),'column_names':encode(list(value.columns.names)),
                'dtypes':[str(x) for x in value.dtypes],'shape':list(raw.shape),'data':encode(raw.tolist()),
                'masks':{kind:[[mask_kind(x)==kind for x in row] for row in raw]
                         for kind in ('null','nan','positive_infinity','negative_infinity')}}
    if isinstance(value,pd.Series): return {'type':'series','name':encode(value.name),'frame':encode(value.to_frame())}
    if isinstance(value,np.ndarray): return encode(value.tolist())
    kind=mask_kind(value)
    if kind: return None if kind=='null' else {'type':'float','value':kind}
    if isinstance(value,np.generic): return encode(value.item())
    if isinstance(value,dict):
        return ({k:encode(v) for k,v in value.items()} if all(isinstance(k,str) for k in value)
                else {'type':'mapping','items':[[encode(k),encode(v)] for k,v in value.items()]})
    if isinstance(value,tuple): return {'type':'tuple','items':[encode(v) for v in value]}
    if isinstance(value,(list,set)): return [encode(v) for v in value]
    if isinstance(value,Path): return str(value)
    if isinstance(value,(str,int,float,bool)) or value is None: return value
    raise TypeError(str(type(value)))

def decode(value):
    if isinstance(value,list): return [decode(v) for v in value]
    if not isinstance(value,dict): return value
    kind=value.get('type')
    if kind=='float': return {'nan':float('nan'),'positive_infinity':float('inf'),'negative_infinity':-float('inf')}[value['value']]
    if kind=='mapping': return {decode(k):decode(v) for k,v in value['items']}
    if kind=='tuple': return tuple(decode(v) for v in value['items'])
    if kind=='dataframe':
        frame=pd.DataFrame(decode(value['data']),index=decode(value['index']),columns=decode(value['columns']))
        frame.index.names=decode(value['index_names']);frame.columns.names=decode(value['column_names'])
        for col,dtype in zip(frame.columns,value['dtypes']): frame[col]=frame[col].astype(dtype)
        return frame
    if kind=='series':
        series=decode(value['frame']).iloc[:,0];series.name=decode(value['name']);return series
    return {k:decode(v) for k,v in value.items()}

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(encode(value),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def runtime(model):
    names=['_groups_df','_DC','_det_fate','p','q','catch','predation','growth','immigration','emigration','net_migration',
           'respiration','egestion','M0','det_export','EE','GE','GS','TL','seq2name','name2seq','source_EE','source_M0',
           '_discard_returns','discard_returns_metadata','EE_before_floor','M0_before_floor','external_mortality_export',
           'ee_floor_ledger','ee_floor_info','_initialization_settings','use_ee_floor','ee_floor','ee_threshold','_ee_floor_base']
    return {k:deepcopy(getattr(model,k)) for k in names if hasattr(model,k)}

def protected_check(base,model):
    living=base['_groups_df'].index[base['_groups_df'].trophic_info.isin(['Regular','PP'])]
    result={k:base[k].loc[living].equals(getattr(model,k).loc[living]) for k in
            ['p','q','catch','predation','growth','immigration','emigration','net_migration','respiration','egestion','GE','GS','TL']}
    result['living_biomass']=base['_groups_df'].loc[living,'biomass'].equals(model._groups_df.loc[living,'biomass'])
    result['diet']=base['_DC'].equals(model._DC)
    result['natural_detritus_fate']=base['_det_fate'].equals(model._det_fate)
    result['entire_catch_vector']=base['catch'].equals(model.catch)
    assert all(result.values()),result
    return result

def pool_budget(model,source_ba):
    returns=model._discard_return_matrix()
    records=[]
    for pool in model.get_DET_seq():
        mortality=float((model.M0*model._det_fate[pool]).sum())
        egestion=float((model.egestion*model._det_fate[pool]).sum())
        fishery=float(returns[pool].sum())
        imported=float(model._groups_df.loc[pool,'detritus_import'])
        demand=float(model.predation[pool])
        net_migration=float(model.net_migration[pool])
        catch=float(model.catch[pool])
        inflow=mortality+egestion+fishery
        residual=inflow-demand-net_migration-catch
        source=float(source_ba.loc[pool])
        records.append({'pool_id':int(pool),'pool_name':model.seq2name[pool],
            'mortality_inflow':mortality,'egestion_inflow':egestion,'fishery_return_inflow':fishery,
            'detritus_import':imported,'runtime_p':float(model.p[pool]),'predation_outflow':demand,
            'catch_outflow':catch,'net_migration_outflow_including_import_convention':net_migration,
            'detritus_stock_residual':residual,'runtime_derived_BA':float(model.growth[pool]),
            'source_BA':source,'source_BA_balance_gap':residual-source,
            'units':'t wet weight km^-2 yr^-1',
            'interpretation':'Runtime BA is inherited/recomputed closure; source BA is separately preserved and is not this residual.'})
        assert np.isclose(inflow,model.p[pool],rtol=1e-12,atol=1e-12)
        assert np.isclose(residual,model.growth[pool],rtol=1e-12,atol=1e-12)
    return records

def matrix(frame,model,label):
    if frame is None: return {'availability':'unavailable','reason':'direct method returned no matrix'}
    return {'dataframe':frame,'orientation':'rows=recipient groups; columns=basal sources' if label=='SPPR' else 'rows/columns=group axes',
        'row_ids':frame.index.tolist(),'row_names':[model.seq2name.get(i,str(i)) for i in frame.index],
        'column_ids':frame.columns.tolist(),'column_names':[model.seq2name.get(i,str(i)) for i in frame.columns],
        'units':'wet-weight-equivalent coefficient' if label=='SPPR' else 'dimensionless operator'}

def main():
    OUT.mkdir(parents=True,exist_ok=True);PINNED.mkdir(parents=True,exist_ok=True)
    protected=[MODEL/'model.json',MODEL/'sppr_source.xlsx',MODEL/'results/result_manifest.json',MODEL/'results/regional_snapshot.xlsx',
               ROOT/'regions/LME/LME_014/LME_014.xlsx',SAVED]
    before={relative(p):sha(p) for p in protected}
    for name,digest in EXPECTED.items():
        assert sha(SHARED/name)==digest,f'Coordinator pin changed: {name}'
        (PINNED/name).write_bytes((SHARED/name).read_bytes())
        assert sha(PINNED/name)==digest
    sys.path.insert(0,str(PINNED))
    from PPRCalculator import PPRCalculator,DEFAULT_DIAGNOSTIC_THRESHOLDS
    saved=json.loads(SAVED.read_text(encoding='utf-8'))
    baseline=decode(saved['completed_before_floor'])
    source_groups=decode(saved['source']['groups_before_calculator_completion'])
    source_ba=source_groups['biomass_accum'].copy()
    assert source_ba.loc[[35,36]].eq(0).all()
    source_ee=decode(saved['effective_after_floor']['source_EE'])
    source_m0=decode(saved['effective_after_floor']['source_M0'])
    assert LEDGER.is_file(),str(LEDGER)
    ledger_bytes=LEDGER.read_bytes();ledger=json.loads(ledger_bytes)
    assert ledger['completeness']['all_group_fleet_pairs_present_once']
    assert ledger['completeness']['finite_nonnegative_catches']
    assert ledger['completeness']['all_discard_mortality_one']
    # Only explicit native sequence/name crosswalks, never Access IDs or row position.
    returns=pd.DataFrame(0.,index=baseline['_groups_df'].index,columns=[36,35])
    landings=pd.Series(0.,index=returns.index);discards=landings.copy()
    for row in ledger['rows']:
        donor=int(row['donor_seq'])
        assert baseline['seq2name'][donor]==row['donor_name'],row
        landings.loc[donor]+=float(row['landings']);discards.loc[donor]+=float(row['discards'])
        amount_sum=0.
        for destination in row['recipients']:
            pool=int(destination['recipient_seq'])
            assert baseline['seq2name'][pool]==destination['recipient_name'],destination
            amount=float(destination['amount']);fraction=float(destination['fraction'])
            assert np.isclose(amount,float(row['discards'])*fraction,rtol=1e-12,atol=1e-12)
            returns.loc[donor,pool]+=amount;amount_sum+=amount
        assert np.isclose(amount_sum,row['discards'],rtol=1e-12,atol=1e-12)
    assert returns[35].eq(0).all()
    assert np.allclose((landings+discards).values,baseline['catch'].values,rtol=1e-12,atol=1e-12)
    assert np.allclose(returns.sum(axis=1),discards,rtol=1e-12,atol=1e-12)
    save(OUT/'source_return_matrix.json',{'matrix':returns,'landings':landings,'discards':discards,
         'source_ledger':relative(LEDGER),'source_ledger_sha256':hashlib.sha256(ledger_bytes).hexdigest(),
         'total_return':float(returns.to_numpy().sum()),'destination':'native Detritus=36; no rerouting to Discards=35',
         'native_pool_rows':ledger['native_pool_rows'],
         'native_export_boundary':'Native EcopathGroup.Export is distinct from fleet returns and canonical export=total catch. Negative native Export is recorded here; no new import or canonical catch change is inferred or applied.'})
    save(OUT/'audited_completed_before_injection.json',baseline)
    call={'short':False,'flat':False,'return_sppr':True,'det_collapse_mode':'never','det_open_mode':'none'}
    summaries=[]
    negative_entries=[]
    for scenario in ['control_no_returns','source_exact_returns_to_36']:
        folder=OUT/scenario;folder.mkdir(exist_ok=True)
        model=PPRCalculator.__new__(PPRCalculator)
        model.__dict__.update(deepcopy(baseline))
        model.n_groups=len(model._groups_df);model.is_underdetermined=False;model.n_balance_runs=0
        model._source_groups_before_completion=source_groups.copy(deep=True)
        model._model=SimpleNamespace(groups_data=source_groups.copy(deep=True),model_name=MODEL.name,model_year='2020')
        model.source_EE=source_ee.copy();model.source_M0=source_m0.copy()
        model._initialization_settings={'underdetermined':False,'zero_catch':True,'zero_biomass_accum':True,
            'default_gs':True,'normalize_DC':False,'DC_tol':.001,
            'initialization_mode':'restored authenticated completed pre-floor state; loader not rerun'}
        model._discard_returns=returns.copy() if scenario=='source_exact_returns_to_36' else returns*0
        model.discard_returns_metadata={'status':'complete','source':relative(LEDGER),'source_sha256':hashlib.sha256(ledger_bytes).hexdigest(),
            'scenario':scenario,'units':'t wet weight km^-2 yr^-1','native_recipient_seq':36,
            'control_note':'explicit zero-return comparison only' if scenario=='control_no_returns' else None}
        model._initialize_discard_returns()
        # Apply added pool input once before the floor, retaining the audited closure convention.
        for pool in model.get_DET_seq():
            amount=float(model._discard_returns[pool].sum())
            model.p.loc[pool]+=amount;model.q.loc[pool]+=amount;model.growth.loc[pool]+=amount
            for col,value in [('p',model.p[pool]),('q',model.q[pool]),('biomass_accum',model.growth[pool]),
                              ('detritus_stock_residual',model.growth[pool]),('pb',model.p[pool]/model._groups_df.loc[pool,'biomass']),
                              ('qb',model.q[pool]/model._groups_df.loc[pool,'biomass'])]: model._groups_df.loc[pool,col]=value
        preservation_before=protected_check(baseline,model)
        save(folder/'post_returns_before_floor.json',{'runtime':runtime(model),'pool_budget':pool_budget(model,source_ba),
             'living_preservation':preservation_before})
        model.apply_ee_floor(use_ee_floor=True,ee_floor=.1,ee_threshold=.1)
        preservation=protected_check(baseline,model)
        save(folder/'effective_floor_on.json',{'runtime':runtime(model),'pool_budget':pool_budget(model,source_ba),
             'living_preservation':preservation,'floor_application_count':1,
             'source_BA_comparison':'Source DET BA=0. The pinned floor implementation recomputes runtime DET BA as closure; source-BА gaps below are independent arithmetic, not a source-preserving solve.'})
        summary={'scenario':scenario,'pool_budget':pool_budget(model,source_ba),'floor_info':model.ee_floor_info,
            'input_balance':bool(model.is_model_balanced()[0]),'living_preservation':preservation,'methods':[]}
        for option in ['GE','TE']:
            started=time.perf_counter();record={'scenario':scenario,'method':option,'call':{'TE_option':option,**call}}
            try:
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always')
                    diagnostic,SPPR,A,L=model.diagnose_sppr(TE_option=option,**call)
                record.update(execution='returned',diagnostic=diagnostic,SPPR=matrix(SPPR,model,'SPPR'),
                              A=matrix(A,model,'A'),L=matrix(L,model,'L'),warnings=[str(w.message) for w in caught])
                if SPPR is not None:
                    record['source_scopes']={'all':list(SPPR.columns),
                        'inner':[i for i in SPPR.columns if model._groups_df.loc[i,'trophic_info']!='Import'],
                        'PP':[i for i in SPPR.columns if model._groups_df.loc[i,'trophic_info']=='PP']}
                    record['scope_coefficients']={scope:SPPR[ids].sum(axis=1) for scope,ids in record['source_scopes'].items()}
                    totals=SPPR.sum(axis=1).reindex(model.catch.index)
                    internal_return=model._discard_return_matrix().sum(axis=1)
                    external_catch=model._external_catch()
                    pieces={name:float(series.dot(totals)) for name,series in
                        [('total_catch',model.catch),('internal_return',internal_return),('external_catch',external_catch),
                         ('growth',model.growth),('net_migration',model.net_migration),('det_export',model.det_export),
                         ('external_mortality_sink',model.external_mortality_export)]}
                    pieces['weighted_outflow']=sum(pieces[k] for k in ['external_catch','growth','net_migration','det_export','external_mortality_sink'])
                    pieces['inflow']=float(model.p.loc[model.get_PP_seq()+model.get_Import_seq()].sum())
                    pieces['source_BA0_weighted_gap']=sum((source_ba[i]-model.growth[i])*totals[i] for i in model.get_DET_seq())
                    pieces['source_BA0_outflow_arithmetic_only']=pieces['weighted_outflow']+pieces['source_BA0_weighted_gap']
                    pieces['total_equals_external_plus_return']=bool(np.isclose(pieces['total_catch'],pieces['external_catch']+pieces['internal_return'],rtol=1e-12,atol=1e-12))
                    pieces['fishery_footprint_retains_total_catch']=bool(np.isclose(pieces['total_catch'],diagnostic['footprint']['ppr_all'],rtol=1e-12,atol=1e-12))
                    record['weighted_budget']=pieces
                    record['matrix_check']={'shape':list(SPPR.shape),'all_group_ids':list(SPPR.index),
                        'negative_SPPR_count':int((SPPR.to_numpy() < -1e-10).sum()),'nonfinite_SPPR_count':int((~np.isfinite(SPPR.to_numpy())).sum()),
                        'unfished_recipient_ids':[int(i) for i in SPPR.index if model.catch[i]==0]}
                    for matrix_name,frame in [('SPPR',SPPR),('A',A),('L',L)]:
                        if frame is not None:
                            for i,j in zip(*np.where(frame.to_numpy() < -1e-10)):
                                row,col=frame.index[i],frame.columns[j]
                                negative_entries.append({'scenario':scenario,'method':option,'matrix':matrix_name,
                                  'recipient_id':int(row),'recipient_name':model.seq2name[row],
                                  'source_id':int(col),'source_name':model.seq2name[col],'value':float(frame.iloc[i,j]),'tolerance':1e-10})
                    assert pieces['total_equals_external_plus_return'] and pieces['fishery_footprint_retains_total_catch']
            except Exception:
                record.update(execution='exception',exception=traceback.format_exc())
            record['seconds']=time.perf_counter()-started
            save(folder/f'{option}_full_return.json',record)
            summary['methods'].append({k:record[k] for k in ['method','execution','diagnostic','weighted_budget','matrix_check','exception'] if k in record})
            print(scenario,option,record['execution'],record.get('diagnostic',{}).get('status'),flush=True)
        summaries.append(summary)
        save(folder/'summary.json',summary)
    save(OUT/'negative_entries.json',{'entries':negative_entries,'SPPR_pairings':[r for r in negative_entries if r['matrix']=='SPPR'],
         'operator_note':'L=A−I living diagonal negatives are equation terms, separate from source-recipient SPPR.'})
    after={relative(p):sha(p) for p in protected}
    checks={'protected_files_unchanged':before==after,'source_ledger_unchanged':LEDGER.read_bytes()==ledger_bytes,
            'engine_pins_retained':all(sha(PINNED/name)==digest for name,digest in EXPECTED.items()),
            'four_calls_returned':all(m['execution']=='returned' for s in summaries for m in s['methods']),
            'living_preserved':all(all(s['living_preservation'].values()) for s in summaries)}
    save(WORK/'qa/diagnostic_protected_verification.json',{'before':before,'after':after,'checks':checks})
    save(OUT/'comparison_summary.json',{'model_id':MODEL.name,'run_id':WORK.name,'summaries':summaries,'checks':checks,
        'native_pool_rows':ledger['native_pool_rows'],
        'source_scope_limit':'Only explicit fleet-return amounts/routing are reconciled in this comparison. Native EcopathGroup.Export remains separate retained evidence; no new negative-catch/import substitution is made.',
        'source_BA_semantics':'Pinned apply_ee_floor unconditionally recomputes DET growth as flow closure. Native BA=0 is retained separately; independent source-BA0 gaps are not additional solves or adopted changes.'})
    save(OUT/'run_provenance.json',{'run_id':WORK.name,'timestamp':datetime.now(timezone.utc).isoformat(),'model_id':MODEL.name,
        'canonical_model_sha256':sha(MODEL/'model.json'),'prior_state_path':relative(SAVED),'prior_state_sha256':sha(SAVED),
        'source_ledger_path':relative(LEDGER),'source_ledger_sha256':sha(LEDGER),'engine_hashes':EXPECTED,
        'engine_paths':{name:relative(PINNED/name) for name in EXPECTED},'script_path':relative(Path(__file__)),'script_sha256':sha(Path(__file__)),
        'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,
        'effective_thresholds':DEFAULT_DIAGNOSTIC_THRESHOLDS,'diagnostic_settings':call,
        'floor':{'use_ee_floor':True,'ee_floor':.1,'ee_threshold':.1,'applications_per_scenario':1},
        'scope':'GE/TE no-return and native source-return comparisons only; no model/workbook/report/Project/map/trends adoption'})
    print(json.dumps(checks),flush=True)
    assert all(checks.values()),checks

if __name__=='__main__': main()
