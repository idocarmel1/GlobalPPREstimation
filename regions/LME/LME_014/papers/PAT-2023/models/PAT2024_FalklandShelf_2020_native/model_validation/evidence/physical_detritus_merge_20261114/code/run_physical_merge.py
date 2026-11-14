"""Isolated physical Discards35+Detritus36 merge with EE floor ON; no adoption."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
import importlib.util
import hashlib
import json
import os
import platform
import sys
import time
import traceback
import warnings

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
MODEL = HERE.parents[2]
ROOT = next(p for p in HERE.parents if (p/'Project.xlsx').exists())
EVIDENCE = MODEL/'model_validation/evidence'
PREVIOUS = EVIDENCE/'discards_reconciliation_20261114'
POOLED = EVIDENCE/'pooled_detritus_20261114'
VARIANT = MODEL.name+'__physical_merge_35_36_ee_floor_on'
MERGED_NAME = 'Detritus including Discards'
spec = importlib.util.spec_from_file_location('serialization_helpers', PREVIOUS/'code/run_discard_comparison.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
import numpy as np
import pandas as pd
sys.path.insert(0,str(PREVIOUS/'code/engine'))
from PPRCalculator import PPRCalculator, DEFAULT_DIAGNOSTIC_THRESHOLDS


def load(path): return helper.decode(json.loads(path.read_text(encoding='utf-8')))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path): return Path(os.path.relpath(path,HERE)).as_posix()
def state_hash(state):
    return hashlib.sha256(json.dumps(helper.encode(state),ensure_ascii=False,sort_keys=True,allow_nan=False).encode('utf-8')).hexdigest()
def close(a,b): return bool(np.allclose(np.asarray(a,dtype=float),np.asarray(b,dtype=float),rtol=1e-12,atol=1e-12,equal_nan=True))


def sum_series(series):
    result=series.drop(index=35).copy()
    result.loc[36]=series.loc[[35,36]].sum(skipna=False)
    return result


def merge_state(original, source):
    state=deepcopy(original)
    df=state['_groups_df'].drop(index=35).copy(deep=True)
    additive=['catch','biomass','p','q','predation','M0','egestion','respiration','biomass_accum',
              'emigration','immigration','net_migration','flow_to_det','detritus_import','det_export','detritus_stock_residual']
    for col in additive:
        df.loc[36,col]=original['_groups_df'].loc[[35,36],col].sum(skipna=False)
    df.loc[36,'group_name']=MERGED_NAME
    df.loc[36,'taxon_descr']='Experimental physical aggregation of source Discards35 and Detritus36; complete mixing assumed.'
    df.loc[36,'pb']=df.loc[36,'p']/df.loc[36,'biomass']
    df.loc[36,'qb']=df.loc[36,'q']/df.loc[36,'biomass']
    df.loc[36,'ge']=df.loc[36,'p']/df.loc[36,'q']
    df.loc[36,'gs']=df.loc[36,'egestion']/df.loc[36,'q']
    df.loc[36,'ee']=1-df.loc[36,'M0']/df.loc[36,'p']
    assert original['TL'].loc[[35,36]].eq(1).all()
    df.loc[36,'tl']=1.
    state['_groups_df']=df
    extensive=['p','q','catch','predation','growth','immigration','emigration','net_migration',
               'respiration','egestion','M0','det_export']
    for key in extensive: state[key]=sum_series(original[key])
    for key,col in [('EE','ee'),('GE','ge'),('GS','gs'),('TL','tl')]:
        state[key]=original[key].drop(index=35).copy()
        state[key].loc[36]=df.loc[36,col]
    state['source_EE']=original['source_EE'].drop(index=35).copy()
    state['source_EE'].loc[36]=np.nan
    state['source_M0']=sum_series(original['source_M0'])
    state['seq2name']={i:n for i,n in original['seq2name'].items() if i!=35}
    state['seq2name'][36]=MERGED_NAME
    state['name2seq']={n:i for i,n in state['seq2name'].items()}
    dc=original['_DC'].copy(deep=True)
    assert dc.loc[[35,36]].eq(0).all().all()
    dc[36]=dc[[35,36]].sum(axis=1,skipna=False)
    state['_DC']=dc.drop(index=35,columns=35)
    fate=original['_det_fate'].copy(deep=True)
    fate[36]=fate[[35,36]].sum(axis=1,skipna=False)
    assert fate.loc[35,36]==fate.loc[36,36]==1.
    state['_det_fate']=fate.drop(index=35,columns=35)
    returns=original['_discard_returns'].copy(deep=True)
    returns[36]=returns[[35,36]].sum(axis=1,skipna=False)
    returns.loc[36]=returns.loc[[35,36]].sum(axis=0,skipna=False)
    state['_discard_returns']=returns.drop(index=35,columns=35)
    state['discard_returns_metadata']={**deepcopy(original['discard_returns_metadata']),
        'scenario':VARIANT,'recipient_crosswalk':{'35':36,'36':36},
        'interpretation':'Original source returns preserved once; their recipient becomes the physically merged pool.'}
    state['_initialization_settings']={**deepcopy(original['_initialization_settings']),
        'scenario_id':VARIANT,'physical_merge':{'original_ids':[35,36],'retained_id':36},
        'initialization_mode':'Restored source-reconciled audited pre-floor state; exact physical aggregation; no loader rerun.'}
    source_view=source.drop(index=35).copy(deep=True)
    for col in source.columns:
        if col in additive:
            source_view.loc[36,col]=source.loc[[35,36],col].sum(skipna=False)
        elif col in ['pb','qb','ee','ge','gs']:
            source_view.loc[36,col]=np.nan
    source_view.loc[36,'group_name']=MERGED_NAME
    if 'taxon_descr' in source_view:
        source_view.loc[36,'taxon_descr']='Derived scenario; original component source rows retained separately.'
    living=original['_groups_df'].index[original['_groups_df'].trophic_info.isin(['Regular','PP'])]
    checks={
        'one_fewer_group':len(df)==len(original['_groups_df'])-1,
        'only_retained_detritus_id':df.index[df.trophic_info.eq('DET')].tolist()==[36],
        'living_group_table_exact':df.loc[living].equals(original['_groups_df'].loc[living]),
        'living_diet_sums_preserved':close(state['_DC'].loc[living].sum(axis=1),original['_DC'].loc[living].sum(axis=1)),
        'non_detritus_diet_cells_exact':state['_DC'].loc[living].drop(columns=36).equals(original['_DC'].loc[living].drop(columns=[35,36])),
        'merged_diet_column_is_sum':state['_DC'].loc[living,36].equals(original['_DC'].loc[living,[35,36]].sum(axis=1)),
        'total_returns_preserved':close(state['_discard_returns'].to_numpy().sum(),original['_discard_returns'].to_numpy().sum()),
        'total_catch_preserved':close(state['catch'].sum(),original['catch'].sum()),
        'total_biomass_preserved':close(df.biomass.sum(),original['_groups_df'].biomass.sum()),
        'source_BA_sum_zero':source_view.loc[36,'biomass_accum']==0,
        'source_EE_merged_unavailable':bool(pd.isna(state['source_EE'][36]))}
    checks.update({f'living_{key}_exact':state[key].loc[living].equals(original[key].loc[living]) for key in extensive+['EE','GE','GS','TL','source_EE','source_M0']})
    assert all(checks.values()),checks
    return state,source_view,checks


def restore(state,source_view):
    model=PPRCalculator.__new__(PPRCalculator)
    model.__dict__.update(deepcopy(state))
    model.n_groups=len(model._groups_df)
    model.is_underdetermined=False
    model.n_balance_runs=0
    model._source_groups_before_completion=source_view.copy(deep=True)
    model._model=SimpleNamespace(groups_data=source_view.copy(deep=True),model_name=VARIANT,model_year='2020')
    model._initialize_discard_returns()
    return model


def main():
    start=datetime.now(timezone.utc).isoformat()
    paths={'canonical':MODEL/'model.json',
        'pre_floor':PREVIOUS/'outputs/diagnostics/source_exact_returns_to_36/post_returns_before_floor.json',
        'separate_effective':PREVIOUS/'outputs/diagnostics/source_exact_returns_to_36/effective_floor_on.json',
        'source_initialization':EVIDENCE/'ee_floor_on_review/initialization_and_floor.json'}
    protected=[*paths.values(),MODEL/'model_notes.md',MODEL/'sppr_source.xlsx',MODEL/'model_validation/validation.docx',
        MODEL/'model_validation/taxon_mapping.xlsx',ROOT/'regions/LME/LME_014/LME_014.xlsx']
    protected_before={rel(p):sha(p) for p in protected}
    shared=[ROOT/'Project.xlsx',ROOT/'interactive_map/index.html',ROOT/'interactive_map/trends.html']
    shared_before={rel(p):sha(p) for p in shared}
    assert sha(paths['canonical'])=='9880e521a406974367530ffb06f13392714dba57b9645c38a1b1448926d83d17'
    for name,digest in helper.EXPECTED.items(): assert sha(PREVIOUS/'code/engine'/name)==digest
    original=load(paths['pre_floor'])['runtime']
    separate_effective=load(paths['separate_effective'])['runtime']
    source=load(paths['source_initialization'])['source']['groups_before_calculator_completion']
    assert '_ee_floor_base' not in original
    merged,source_view,merge_checks=merge_state(original,source)
    helper.save(HERE/'inputs/merge_specification.json',{'variant_id':VARIANT,'source_model_id':MODEL.name,
        'crosswalk':[{'original_id':35,'original_name':'Discards','merged_id':36,'merged_name':MERGED_NAME},
                     {'original_id':36,'original_name':'Detritus','merged_id':36,'merged_name':MERGED_NAME}],
        'source_component_rows':source.loc[[35,36]],'pre_floor_component_rows':original['_groups_df'].loc[[35,36]],
        'source_component_EE':original['source_EE'].loc[[35,36]],'source_component_M0':original['source_M0'].loc[[35,36]],
        'rules':'Sum stocks and extensive flows; sum prey and recipient columns; both zero diet donor rows become zero; collapsed fate donor rows both equal one. Derive rates/efficiencies from sums. Merged source EE is unavailable, not averaged.',
        'assumption':'Discards and ordinary detritus form one completely mixed physical food pool; no new supply introduced.',
        'scope':'Isolated runtime scenario, no canonical model creation, registration or adoption.'})
    model=restore(merged,source_view)
    pre_floor_state=helper.runtime(model)
    pre_floor_balance=bool(model.is_model_balanced()[0])
    assert pre_floor_balance
    model.apply_ee_floor(use_ee_floor=True,ee_floor=.1,ee_threshold=.1)
    effective=helper.runtime(model)
    living=model._groups_df.index[model._groups_df.trophic_info.isin(['Regular','PP'])]
    floor_checks={f'living_{key}_matches_separate':getattr(model,key).loc[living].equals(separate_effective[key].loc[living]) for key in
        ['p','q','catch','predation','growth','immigration','emigration','net_migration','respiration','egestion','M0','EE','GE','GS','TL','external_mortality_export']}
    floor_checks.update({f'pool_{key}_equals_component_sum':close(getattr(model,key).loc[36],separate_effective[key].loc[[35,36]].sum()) for key in
        ['p','q','catch','predation','growth','immigration','emigration','net_migration','respiration','egestion','M0','det_export','external_mortality_export']})
    floor_checks['affected_living_groups_unchanged']=model.ee_floor_info['affected_groups']==separate_effective['ee_floor_info']['affected_groups']
    floor_checks['floor_application_count_one']=bool(model.use_ee_floor and model.ee_floor==.1 and '_ee_floor_base' in effective)
    floor_checks['negative_merged_stock_residual_absent']=not model.ee_floor_info['negative_detritus_stock_residuals']
    assert all(floor_checks.values()),floor_checks
    stage_path=HERE/'outputs/merge_and_floor.json'
    helper.save(stage_path,{'pre_floor':pre_floor_state,'effective':effective,'source_view':source_view,
        'merge_checks':merge_checks,'floor_checks':floor_checks,'floor_application_count':1,
        'source_BA_comparison':'Original component source BA values sum to zero; positive runtime growth remains calculated closure, not measured accumulation.'})
    # Reopen the exact persisted scenario state before the two method calls.
    reopened=load(stage_path)
    assert state_hash(reopened['effective'])==state_hash(effective)
    summaries=[]
    negatives=[]
    for option in ['GE','TE']:
        calc=restore(reopened['effective'],reopened['source_view'])
        before=state_hash(helper.runtime(calc))
        call=dict(TE_option=option,short=False,flat=False,return_sppr=True,det_collapse_mode='never',det_open_mode='none')
        record={'variant_id':VARIANT,'method':option,'call':call,'runtime_source':'merge_and_floor.json#effective',
            'runtime_before_sha256':before,'execution':'not_run'}
        begun=time.perf_counter()
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                diag,sppr,a,l=calc.diagnose_sppr(**call)
            record.update(execution='returned',diagnostic=diag,SPPR=helper.matrix(sppr,calc,'SPPR'),
                A=helper.matrix(a,calc,'A'),L=helper.matrix(l,calc,'L'),detritus_resolution_info=deepcopy(calc.detritus_resolution_info),
                warnings=[str(w.message) for w in caught])
            separate_path=PREVIOUS/f'outputs/diagnostics/source_exact_returns_to_36/{option}_full_return.json'
            pooled_path=POOLED/f'outputs/{option}_pooled_full_return.json'
            separate=load(separate_path);pooled=load(pooled_path)
            old_sppr=separate['SPPR']['dataframe'];pooled_sppr=pooled['SPPR']['dataframe']
            expected=pooled_sppr.drop(index=35).copy()
            expected[36]=expected[[35,36]].sum(axis=1)
            expected=expected.drop(columns=35).reindex(index=sppr.index,columns=sppr.columns)
            scopes={'all':list(sppr.columns),'inner':[i for i in sppr.columns if calc._groups_df.loc[i,'trophic_info']!='Import'],
                    'PP':[i for i in sppr.columns if calc._groups_df.loc[i,'trophic_info']=='PP']}
            record['source_scopes']=scopes
            record['scope_coefficients']={s:sppr[ids].sum(axis=1) for s,ids in scopes.items()}
            totals=sppr.sum(axis=1)
            old_totals=old_sppr.sum(axis=1).reindex(sppr.index)
            groups=pd.DataFrame({'name':pd.Series(calc.seq2name),'catch':calc.catch,'separate_sppr':old_totals,
                'physical_merge_sppr':totals,'sppr_change':totals-old_totals,
                'sppr_percent_change':(totals/old_totals-1)*100,
                'separate_catch_ppr':calc.catch*old_totals,'physical_merge_catch_ppr':calc.catch*totals},index=sppr.index)
            groups['catch_ppr_change']=groups.physical_merge_catch_ppr-groups.separate_catch_ppr
            record['group_comparison']=groups
            pieces={key:float(vector.dot(totals)) for key,vector in [('total_catch',calc.catch),
                ('internal_returns',calc._discard_return_matrix().sum(axis=1)),('external_catch',calc._external_catch()),
                ('growth',calc.growth),('net_migration',calc.net_migration),('det_export',calc.det_export),
                ('external_mortality_sink',calc.external_mortality_export)]}
            pieces['inflow']=float(calc.p.loc[calc.get_PP_seq()+calc.get_Import_seq()].sum())
            pieces['outflow']=sum(pieces[k] for k in ['external_catch','growth','net_migration','det_export','external_mortality_sink'])
            record['weighted_budget']=pieces
            checks={'runtime_unchanged':before==state_hash(helper.runtime(calc)),
                'one_physical_detritus_group':calc.get_DET_seq()==[36],
                'group_count_36':len(calc._groups_df)==36,'SPPR_shape_36_by_4':sppr.shape==(36,4),
                'no_removed_group_in_axes':35 not in sppr.index and 35 not in sppr.columns,
                'all_sppr_finite':bool(np.isfinite(sppr.to_numpy()).all()),
                'no_negative_sppr':bool((sppr.to_numpy()>=-1e-10).all()),
                'source_column_crosswalk_matches_prior_pooling':close(sppr,expected),
                'non_detritus_source_columns_match_separate':close(sppr.drop(columns=36),old_sppr.reindex(index=sppr.index).drop(columns=[35,36]).reindex(columns=sppr.drop(columns=36).columns)),
                'fishery_total_reconciles':close(pieces['total_catch'],diag['footprint']['ppr_all']),
                'internal_return_counted_once':close(pieces['total_catch'],pieces['external_catch']+pieces['internal_returns'])}
            record['checks']=checks
            record['comparison_references']={key:{'path':rel(p),'sha256':sha(p)} for key,p in [('separate',separate_path),('attribution_pooled',pooled_path)]}
            record['maximum_abs_SPPR_difference_from_attribution_pooling']=float(np.abs(sppr.to_numpy()-expected.to_numpy()).max())
            for label,frame in [('SPPR',sppr),('A',a),('L',l)]:
                for i,j in zip(*np.where(frame.to_numpy() < -1e-10)):
                    row,col=frame.index[i],frame.columns[j]
                    negatives.append({'method':option,'matrix':label,'row_id':int(row),'row_name':calc.seq2name[row],
                        'column_id':int(col),'column_name':calc.seq2name[col],'value':float(frame.iloc[i,j]),'tolerance':1e-10})
            old=separate['diagnostic']['footprint']['ppr_all'];new=diag['footprint']['ppr_all']
            summaries.append({'method':option,'status':diag['status'],'separate_status':separate['diagnostic']['status'],
                'separate_ppr':old,'physical_merge_ppr':new,'attribution_pooling_ppr':pooled['diagnostic']['footprint']['ppr_all'],
                'percent_change_vs_separate':(new/old-1)*100,'difference_from_attribution_pooling':new-pooled['diagnostic']['footprint']['ppr_all'],
                'balance':diag['balance'],'warnings':diag['warnings'],'detritus_resolution_info':record['detritus_resolution_info'],
                'checks':checks,'seabirds':groups.loc[25],'pp_only_ppr':diag['footprint']['ppr_pp_only']})
        except Exception:
            record.update(execution='exception',exception=traceback.format_exc())
        record['seconds']=time.perf_counter()-begun
        record['runtime_after_sha256']=state_hash(helper.runtime(calc))
        helper.save(HERE/f'outputs/{option}_physical_merge_full_return.json',record)
        print(option,record['execution'],record.get('diagnostic',{}).get('status'),record.get('exception',''),flush=True)
    after={rel(p):sha(p) for p in protected}
    shared_after={rel(p):sha(p) for p in shared}
    helper.save(HERE/'qa/protected_files.json',{'before':protected_before,'after':after,'all_protected_unchanged':protected_before==after,
        'shared_before':shared_before,'shared_after':shared_after,'shared_changed_by_this_task':False,
        'shared_drift_observed':[p for p in shared_before if shared_before[p]!=shared_after[p]],'coordinator_messages_sent':False})
    helper.save(HERE/'outputs/negative_entries.json',{'entries':negatives,'negative_SPPR_entries':[r for r in negatives if r['matrix']=='SPPR'],
        'operator_note':'Negative L living diagonal entries are equation terms, not negative source attribution.'})
    helper.save(HERE/'outputs/comparison.json',{'variant_id':VARIANT,'base_model_id':MODEL.name,'summaries':summaries,
        'merged_stock_biomass':model._groups_df.loc[36,'biomass'],'merged_inflow':model.p[36],
        'merged_consumption':model.predation[36],'merged_stock_residual':model.growth[36],
        'total_fishery_returns':float(model._discard_return_matrix().to_numpy().sum()),
        'floor_sink_total':float(model.external_mortality_export.sum()),'merge_checks':merge_checks,'floor_checks':floor_checks,
        'interpretation':'A diagnostic grade applies only to this complete-mixing scenario; constituent source attribution remains unresolved.'})
    helper.save(HERE/'outputs/provenance.json',{'variant_id':VARIANT,'started_utc':start,'finished_utc':datetime.now(timezone.utc).isoformat(),
        'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,
        'engine_sha256':helper.EXPECTED,'engine_location':rel(PREVIOUS/'code/engine'),
        'inputs':{key:{'path':rel(p),'sha256':sha(p)} for key,p in paths.items()},
        'executed_runner':{'path':'code/run_physical_merge.py','sha256':sha(Path(__file__))},
        'methods':['GE','TE'],'new_diagnostic_calls':2,'floor_application_count':1,
        'restored_persisted_scenario_for_calls':True,'effective_state_sha256':state_hash(effective),
        'thresholds':DEFAULT_DIAGNOSTIC_THRESHOLDS,'options':{'use_ee_floor':True,'ee_floor':.1,'ee_threshold':.1,'det_collapse_mode':'never','det_open_mode':'none'},
        'units':'Source model mass/area/year; t/km² during 2020, wet versus dry mass not explicitly established.',
        'adoption':'None; canonical model, workbooks, map, trends, source views and researcher review preserved.'})
    assert protected_before==after
    assert len(summaries)==2 and all(all(s['checks'].values()) for s in summaries)
    print(json.dumps([{'method':s['method'],'status':s['status'],'ppr':s['physical_merge_ppr'],'change_percent':s['percent_change_vs_separate']} for s in summaries]),flush=True)


if __name__=='__main__': main()
