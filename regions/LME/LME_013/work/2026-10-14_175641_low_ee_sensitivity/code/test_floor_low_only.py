"""Fine grid restricted to the fixed original EE<0.1 group set.

Native balance checks and extended-sink balances are reported separately.
No canonical scientific input, saved calculation, selection or review is written.
"""
from pathlib import Path
import argparse, copy, gzip, inspect, json, sys, time, traceback, warnings
import numpy as np
import pandas as pd
from test_low_ee import (ROOT, _constructor, _load, _runtime, decode_frame,
                         engine_identity, group_catch, method_settings, metrics,
                         save, scenario, sha)

FLOORS=tuple(round(i/100,2) for i in range(1,51))
OPTIONS={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}
HERE=Path(__file__).resolve().parent

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def gzread(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)
def floor_label(f):return 'floor_'+str(f).replace('.','p')

def run(work):
    start=time.time();cfg=read(work/'inputs/configuration.json')
    print('START FINE GRID',cfg['unit_id'],flush=True)
    protection=read(work/'inputs/floor_low_only_configuration.json')
    assert all(sha(ROOT/p)==h for p,h in protection['protected_hashes'].items()),'Current protected file changed'
    assert sha(ROOT/cfg['model_path'])==cfg['protected_hashes'][cfg['model_path']],'Canonical model changed since matched baseline'
    model=ROOT/cfg['model_path'];flags=cfg['flags']
    base,source,loader_warnings=_load(model,_constructor(flags,model),flags)
    frozen=gzread(work/'outputs/source_and_runtime.json.gz')
    assert frozen['runtime']==_runtime(base),'Baseline runtime changed'
    baseline_code=read(work/'outputs/run_manifest.json')['engine_identity']
    actual_engine=engine_identity(flags,model)
    assert all(baseline_code[k]==actual_engine[k] for k in ['PPRCalculator.py','ModelData.py','utils.py']),'Audited engine bytes changed'
    catch,missing=group_catch(work,cfg,base)
    assert not missing,'Current landings or mapping support differs from baseline'
    prior_groups=pd.read_csv(work/'outputs/floor_fine/group_comparison.csv',float_precision='round_trip')
    prior_catch=prior_groups[(prior_groups.floor==.01)&(prior_groups.method=='GE')].set_index('seq').landings_2019_tonnes
    np.testing.assert_allclose(catch.sort_index(),prior_catch.sort_index(),rtol=0,atol=0)
    living=[s for s in base.p.index if s not in base.get_DET_seq()+base.get_Import_seq() and base.p[s]>0]
    source_groups=decode_frame(source['groups'])
    eligible=[s for s in living if np.isfinite(base.EE[s]) and 0<=base.EE[s]<.1
              and np.isfinite(base.M0[s]) and base.M0[s]>=0
              and np.isfinite(source_groups.loc[s,'ee']) and 0<=source_groups.loc[s,'ee']<=1]
    print('FIXED ELIGIBLE SET',cfg['unit_id'],[(int(s),base.seq2name[s],float(base.EE[s])) for s in eligible],flush=True)
    zero=pd.Series(0.,index=base.p.index)
    baseline_rows={r['method']:r for r in read(work/'outputs/scenario_summary.json') if r['scenario']=='baseline'}
    summaries=[];groups=[];unchanged=protection['protected_hashes']
    for floor in FLOORS:
        affected=[s for s in eligible if base.EE[s]<floor]
        export=zero.copy();export.loc[affected]=base.p.loc[affected]*(floor-base.EE.loc[affected])
        current,external=scenario(base,living,export,True)
        held=[s for s in living if s not in eligible]
        assert current.M0.loc[held].equals(base.M0.loc[held])
        current.EE.loc[held]=base.EE.loc[held]
        current._groups_df.loc[held,'ee']=base.EE.loc[held]
        # Record the actual stock production check before adding the experimental sink.
        native_model_balanced,production,consumption=current.is_model_balanced()
        extended_residual=production+external-current.p
        original_residual=base.catch+base.predation+base.growth+base.net_migration+base.M0-base.p
        assert np.allclose(extended_residual.loc[living],original_residual.loc[living],rtol=1e-10,atol=1e-10)
        for option,key in OPTIONS.items():
            output=work/'outputs/floor_low_only'/floor_label(floor)/option.replace(' ','_')
            c=copy.deepcopy(current);settings=method_settings(key,flags,model)
            kwargs={k:v for k,v in settings['kwargs'].items() if k in inspect.signature(c.SPPR_new).parameters}
            print(cfg['unit_id'],floor,option,flush=True)
            saved_warning_strings=[]
            cache=None
            coarse=work/'outputs/floor_fine'/floor_label(floor)/option.replace(' ','_')
            if (coarse/'full_return.json.gz').is_file() and gzread(coarse/'runtime.json.gz')==_runtime(c):
                cache=coarse
                assert gzread(cache/'runtime.json.gz')==_runtime(c),'Previous coarse-grid runtime differs'
                saved_warning_strings=read(cache/'metrics.json').get('warnings',[])
                origin='retained_all_group_fine_grid_exact_runtime'
            elif not affected:
                cache=work/'outputs/baseline'/option.replace(' ','_')
                origin='retained_baseline_no_affected_groups'
            else:origin='fresh_SPPR_new'
            try:
                with warnings.catch_warnings(record=True) as ws:
                    warnings.simplefilter('always')
                    if cache:
                        ret=gzread(cache/'full_return.json.gz')
                        matrix,A,L=(decode_frame(ret[k]) for k in ['SPPR','A','L'])
                        cached_metrics=read(cache/'metrics.json')
                        resolution=cached_metrics.get('detritus_resolution')
                    else:
                        matrix,A,L=c.SPPR_new(**kwargs)
                        resolution=copy.deepcopy(getattr(c,'detritus_resolution_info',None))
                save(output/'full_return.json.gz',{'SPPR':matrix,'A':A,'L':L},typed=True)
                save(output/'runtime.json.gz',_runtime(c))
                totals=matrix.sum(axis=1)
                native_balanced,native_in,native_out=c.is_sppr_balanced(matrix)
                m=metrics(c,matrix,external,catch,A,option)
                assert np.isclose(native_in,m['pp_inflow']) and np.isclose(native_out,m['pp_outflow_existing_sinks'])
                old_ppr=baseline_rows[option]['landings_2019_ppr_tC']
                m.update(unit_id=cfg['unit_id'],model_id=cfg['model_id'],floor=floor,method=option,
                         status='computed_sensitivity',origin=origin,
                         affected_group_ids=list(map(int,affected)),affected_group_names=[base.seq2name[s] for s in affected],
                         affected_group_count=len(affected),baseline_ppr_tC=old_ppr,
                         eligibility_threshold=.1,eligible_group_ids=list(map(int,eligible)),eligible_group_count=len(eligible),
                         percent_change_from_baseline=100*(m['landings_2019_ppr_tC']/old_ppr-1) if old_ppr else None,
                         native_is_sppr_balanced=bool(native_balanced),native_pp_inflow=float(native_in),
                         native_pp_outflow=float(native_out),native_relative_pp_gap=float((native_out-native_in)/native_in),
                         native_is_model_balanced=bool(native_model_balanced),
                         maximum_living_production_residual_with_external_sink=float(abs(extended_residual.loc[living]).max()),
                         warnings=saved_warning_strings+[str(w.message) for w in ws],detritus_resolution=resolution,
                         conservation_note='External sink included only in the extended experimental budget; stock calculator is unchanged.')
                save(output/'metrics.json',m);summaries.append(m)
                # Source matrices retain all scopes; convenient group table reports all/inner/PP.
                imports=set(base.get_Import_seq());pp=set(base.get_PP_seq())
                inner=matrix[[s for s in matrix.columns if s not in imports]].sum(axis=1)
                pp_only=matrix[[s for s in matrix.columns if s in pp]].sum(axis=1)
                original=decode_frame(gzread(work/'outputs/baseline'/option.replace(' ','_')/'full_return.json.gz')['SPPR']).sum(axis=1)
                for s in base.p.index:
                    groups.append({'unit_id':cfg['unit_id'],'model_id':cfg['model_id'],'floor':floor,'method':option,
                         'seq':int(s),'group':base.seq2name[s],'source_EE':float(base.EE[s]),'effective_EE':float(c.EE[s]),
                         'source_M0':float(base.M0[s]),'internal_M0':float(c.M0[s]),'hypothetical_external_sink':float(external[s]),
                         'source_TL':float(base.TL[s]),'baseline_SPPR_all':float(original[s]),'SPPR_all':float(totals[s]),
                         'SPPR_inner':float(inner[s]),'SPPR_PP':float(pp_only[s]),'landings_2019_tonnes':float(catch[s]),
                         'landings_2019_PPR_tC':float(catch[s]*totals[s]/9)})
                np.testing.assert_allclose(sum(r['landings_2019_PPR_tC'] for r in groups
                    if r['floor']==floor and r['method']==option),m['landings_2019_ppr_tC'],rtol=1e-12,atol=1e-6)
            except Exception as exc:
                failure={'unit_id':cfg['unit_id'],'model_id':cfg['model_id'],'floor':floor,'method':option,
                         'status':'failed','reason':str(exc),'traceback':traceback.format_exc()}
                save(output/'failure.json',failure);summaries.append(failure)
    out=work/'outputs/floor_low_only'
    save(out/'scenario_summary.json',summaries)
    pd.DataFrame(groups).to_csv(out/'group_comparison.csv',index=False,encoding='utf-8',float_format='%.17g')
    preserved={p:sha(ROOT/p)==h for p,h in unchanged.items()}
    assert all(preserved.values()) and frozen['runtime']==_runtime(base)
    save(out/'run_manifest.json',{'run_id':cfg['run_id'],'extension':'EE floor 0.01 to 0.50, step 0.01, only original EE<0.1','unit_id':cfg['unit_id'],
         'model_id':cfg['model_id'],'source_sha256':sha(model),'floors':list(FLOORS),'methods':list(OPTIONS),
         'constructor_and_settings':flags,'engine_identity':engine_identity(flags,model),
         'experiment_code_sha256':sha(__file__),'adapter_sha256':sha(HERE/'test_low_ee.py'),
         'baseline_runtime_exact':True,'loading_warnings':loader_warnings,'protected_input_hashes':unchanged,
         'protected_inputs_unchanged':preserved,'elapsed_seconds':time.time()-start,
         'basis':'2019 landings, all mapped groups, original allocation weights; wet PPR / 9 = tC',
         'eligibility':'Fixed before-floor completed EE<0.1; valid source EE required. Each floor is max(original EE,floor) within this fixed set. Other living groups remain unchanged.',
         'eligible_group_ids':list(map(int,eligible)),'eligible_group_names':[base.seq2name[s] for s in eligible],
         'historical_protected_hash_differences':{p:{'historical':h,'current':unchanged[p]} for p,h in cfg['protected_hashes'].items() if unchanged[p]!=h},
         'source_fidelity':'Canonical inputs unchanged. Floors and external mortality are unadopted experimental assumptions.',
         'native_vs_extended_balance_reported_separately':True,'outcome_count':len(summaries),
         'failed_outcomes':sum(r['status']=='failed' for r in summaries)})
    print('COMPLETE FINE GRID',cfg['unit_id'],round(time.time()-start,2),'failures',sum(r['status']=='failed' for r in summaries),flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');p=argparse.ArgumentParser();p.add_argument('work');args=p.parse_args()
    run((ROOT/args.work).resolve())
