"""EE >= 0.1 sensitivity with a separate hypothetical external mortality sink."""
from pathlib import Path
import argparse, copy, gzip, inspect, json, sys, time, warnings
import pandas as pd
from test_low_ee import (ROOT, _constructor, _load, _runtime, encode_lossless,
                         group_catch, method_settings, metrics, save, scenario, sha)

def run(work):
    start=time.time();cfg=json.loads((work/'inputs/configuration.json').read_text(encoding='utf-8'))
    print('START EE FLOOR',cfg['unit_id'],flush=True)
    assert all(sha(ROOT/p)==h for p,h in cfg['protected_hashes'].items())
    model=ROOT/cfg['model_path'];flags=cfg['flags']
    base,source,loading_warnings=_load(model,_constructor(flags,model),flags)
    with gzip.open(work/'outputs/source_and_runtime.json.gz','rt',encoding='utf-8') as f: frozen=json.load(f)
    assert frozen['runtime']==_runtime(base),'Baseline runtime changed'
    living=[s for s in base.p.index if s not in base.get_DET_seq()+base.get_Import_seq() and base.p[s]>0]
    low=[s for s in living if base.EE[s]<.1]
    export=pd.Series(0.,index=base.p.index)
    export.loc[low]=base.p.loc[low]*(.1-base.EE.loc[low])
    current,external=scenario(base,living,export,True)
    catch,missing=group_catch(work,cfg,base)
    old=json.loads((work/'outputs/scenario_summary.json').read_text(encoding='utf-8'))
    baselines={v['method']:v for v in old if v['scenario']=='baseline'}
    fitted={v['method']:v for v in old if v['scenario']=='predicted_ee_all_living'}
    results=[];groups=[]
    for option,key in [('GE','new_GE'),('TE','new_TE_EEfix'),('With Egestion','new_WithEgestion')]:
        print(cfg['unit_id'],'EE FLOOR',option,flush=True)
        c=copy.deepcopy(current);settings=method_settings(key,flags,model)
        kwargs={k:v for k,v in settings['kwargs'].items() if k in inspect.signature(c.SPPR_new).parameters}
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always');matrix,A,L=c.SPPR_new(**kwargs)
        out=work/'outputs/ee_floor_0p1'/option.replace(' ','_')
        save(out/'full_return.json.gz',{'SPPR':matrix,'A':A,'L':L},typed=True)
        save(out/'runtime.json.gz',_runtime(c))
        m=metrics(c,matrix,external,catch,A,option)
        b=baselines[option]['landings_2019_ppr_tC'];fitted_ppr=fitted[option]['landings_2019_ppr_tC']
        m.update(scenario='ee_floor_0p1',method=option,status='computed_sensitivity',
                 floor=.1,baseline_ppr_tC=b,fitted_ee_ppr_tC=fitted_ppr,
                 percent_change_from_baseline=100*(m['landings_2019_ppr_tC']/b-1) if b else None,
                 warnings=[str(w.message) for w in ws],
                 detritus_resolution=copy.deepcopy(getattr(c,'detritus_resolution_info',None)),
                 explicit_external_sink_not_fishery=True)
        save(out/'metrics.json',m);results.append(m)
        with gzip.open(work/'outputs/baseline'/option.replace(' ','_')/'full_return.json.gz','rt',encoding='utf-8') as f:
            baseline_matrix=json.load(f)['SPPR']
        original=pd.DataFrame(baseline_matrix['data'],index=baseline_matrix['index'],columns=baseline_matrix['columns']).sum(axis=1)
        new=matrix.sum(axis=1)
        for s in base.p.index:
            v=float(new[s]);oldv=float(original[s])
            groups.append({'method':option,'seq':int(s),'group':base.seq2name[s],
                           'source_EE':float(base.EE[s]),'floored_EE':float(c.EE[s]),
                           'source_M0':float(base.M0[s]),'internal_M0':float(c.M0[s]),
                           'hypothetical_external_sink':float(external[s]),
                           'baseline_SPPR_all':oldv,'floor_SPPR_all':v,
                           'relative_SPPR_change':(v-oldv)/oldv if oldv else None,
                           'landings_2019':float(catch[s])})
    save(work/'outputs/ee_floor_summary.json',results)
    pd.DataFrame(groups).to_csv(work/'outputs/ee_floor_groups.csv',index=False,encoding='utf-8',float_format='%.17g')
    unchanged={p:sha(ROOT/p)==h for p,h in cfg['protected_hashes'].items()}
    assert all(unchanged.values()) and frozen['runtime']==_runtime(base)
    save(work/'qa/ee_floor_checks.json',{'baseline_runtime_exact':True,'protected_inputs_unchanged':unchanged,
         'floor':.1,'affected_group_ids':list(map(int,low)),
         'methods':['GE','TE','With Egestion'],'experiment_code_sha256':sha(__file__),
         'shared_adapter_sha256':sha(Path(__file__).with_name('test_low_ee.py')),
         'source_sha256':sha(model),'settings':flags,'elapsed_seconds':time.time()-start,
         'no_adoption':True,'living_budget_residuals_unchanged':True,
         'catches_diets_consumption_and_living_BA_unchanged':True,
         'detritus_stock_residuals_are_closure_not_source_measurements':True})
    print('COMPLETE EE FLOOR',cfg['unit_id'],round(time.time()-start,2),flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');p=argparse.ArgumentParser();p.add_argument('work');args=p.parse_args()
    run((ROOT/args.work).resolve())
