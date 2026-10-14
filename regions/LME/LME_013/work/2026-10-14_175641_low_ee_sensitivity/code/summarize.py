"""Reopen evidence, verify baselines and conservation, and draw EE/TL fits."""
from pathlib import Path
import csv, gzip, hashlib, importlib.util, json, os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

labels={'HS_077':'Eastern tropical Pacific','LME_028':'Guinea Current','LME_032':'Arabian Sea',
        'LME_034':'Bay of Bengal','LME_035':'Gulf of Thailand','LME_036':'Northern South China Sea',
        'LME_047':'East China Sea','LME_013':'Humboldt Current'}
sys.stdout.reconfigure(encoding='utf-8')
entries=read(BASE/'inputs/models.json')
assert len(entries)==8
all_summaries=[];checks={};fig,axes=plt.subplots(2,4,figsize=(15,7),sharey=True)
checker_path=ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py'
spec=importlib.util.spec_from_file_location('evidence_checker',checker_path)
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
for entry,ax in zip(entries,axes.flat):
    work=ROOT/entry['work'];cfg=read(work/'inputs/configuration.json');model=ROOT/cfg['model_path']
    report=read(work/'outputs/run_manifest.json');fits=read(work/'outputs/regressions.json')
    scenarios=read(work/'outputs/scenario_summary.json')
    assert all(v['status']=='computed_sensitivity' for v in scenarios)
    changed=[p for p,h in cfg['protected_hashes'].items() if sha(ROOT/p)!=h]
    assert not changed,(entry['unit_id'],changed)
    frames=pd.read_csv(work/'outputs/group_comparison.csv')
    snapshot=read_book(model.parent/'results/regional_snapshot.xlsx',sheets=['Selected model groups'])
    saved={(row['method'],row['group']):row['sppr'] for row in records(snapshot,'Selected model groups','Group SPPR')
           if row['scope']=='all' and row['model_id']==cfg['model_id']}
    parity={}
    method_keys={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}
    for method,key in method_keys.items():
        base=frames[(frames.scenario=='baseline')&(frames.method==method)]
        diffs=[];matches=[]
        for row in base.itertuples():
            value=saved.get((key,row.group))
            if value is None:continue
            diffs.append(abs(row.sppr_all-value));matches.append(np.isclose(row.sppr_all,value,rtol=1e-10,atol=1e-10))
        assert len(matches)==len(base) and all(matches),(entry['unit_id'],key,max(diffs,default=0),len(matches),len(base))
        parity[key]={'groups_compared':len(matches),'max_absolute_difference':float(max(diffs,default=0)),
                     'all_match_rtol_1e_10_atol_1e_10':bool(all(matches))}
        matched=frames[(frames.scenario=='routing_only_matched')&(frames.method==method)].sort_values('seq')
        predicted=frames[(frames.scenario=='predicted_ee_all_living')&(frames.method==method)].sort_values('seq')
        if method!='TE': assert np.array_equal(matched.sppr_all.to_numpy(),predicted.sppr_all.to_numpy())
    baseline={v['method']:v for v in scenarios if v['scenario']=='baseline'}
    row={'unit_id':entry['unit_id'],'name':labels[entry['unit_id']],'model_id':cfg['model_id'],
         'n_training':fits['all_living']['n'],'low_EE_groups':len(report['low_ee_group_ids']),
         'R_squared_all_living':fits['all_living']['r_squared'],
         'R_squared_consumers_only':fits['consumers_only']['r_squared'],
         'leave_one_out_RMSE':fits['all_living']['leave_one_out_rmse'],
         'low_group_names':'; '.join(frames[(frames.scenario=='baseline')&(frames.method=='GE')&
                           frames.seq.isin(report['low_ee_group_ids'])].group)}
    for method in method_keys:
        values=next(v for v in scenarios if v['scenario']=='predicted_ee_all_living' and v['method']==method)
        b=baseline[method]['landings_2019_ppr_tC'];value=values['landings_2019_ppr_tC']
        row[method+'_PPR_percent_change']=100*(value/b-1) if b else None
        row[method+'_extended_PP_gap']=values['relative_pp_budget_gap_with_external_sink']
        row[method+'_baseline_PP_gap']=baseline[method]['relative_pp_budget_gap_with_external_sink']
        row[method+'_unpooled_recycling_radius']=values['recycling'].get('unpooled_detritus_recycling_radius')
        row[method+'_negative_entries']=values['negative_source_entries']
    all_summaries.append(row)
    qa={'baseline_saved_coefficient_reconciliation':parity,'protected_inputs_unchanged':True,
        'GE_and_WithEgestion_predicted_and_routing_only_coefficients_exactly_equal':True,
        'all_scenarios_computed':True,'scenario_count':len(scenarios),
        'PP_budget_results_are_findings_not_success_gates':True}
    save(work/'qa/numerical_verification.json',qa)
    index=work/'qa/evidence_index.json';artifacts=[]
    def artifact(role,p):
        artifacts.append({'role':role,'path':Path(os.path.relpath(p,index.parent)).as_posix(),
                          'sha256':sha(p),'availability':'present'})
    for role,p in [('source_model',model),('source_notes',model.parent/'model_notes.md'),
                   ('configuration',work/'inputs/configuration.json'),('experiment_code',BASE/'code/test_low_ee.py'),
                   ('source_and_runtime',work/'outputs/source_and_runtime.json.gz'),
                   ('regression',work/'outputs/regressions.json'),('summary',work/'outputs/scenario_summary.json'),
                   ('group_comparison',work/'outputs/group_comparison.csv'),
                   ('numerical_verification',work/'qa/numerical_verification.json')]: artifact(role,p)
    for v in scenarios:
        out=work/'outputs'/v['scenario']/v['method'].replace(' ','_')
        artifact(v['scenario']+'_'+v['method']+'_matrix',out/'full_return.json.gz')
        artifact(v['scenario']+'_'+v['method']+'_runtime',out/'runtime.json.gz')
        artifact(v['scenario']+'_'+v['method']+'_metrics',out/'metrics.json')
        with gzip.open(out/'full_return.json.gz','rt',encoding='utf-8') as f:
            content=json.load(f)
        for name in ['SPPR','A','L']:
            m=content[name];assert m['type']=='dataframe' and m['shape']==[len(m['index']),len(m['columns'])]
            assert len(set(m['index']))==len(m['index']) and len(set(m['columns']))==len(m['columns'])
            assert len(m['data'])==m['shape'][0]
            for mask in m['masks'].values():assert len(mask)==m['shape'][0] and all(len(v)==m['shape'][1] for v in mask)
        if v['scenario']=='baseline':artifact(v['method']+'_direct_diagnostics',out/'direct_diagnostic.json.gz')
    roles=[v['role'] for v in artifacts]
    save(index,{'schema_version':1,'run_id':cfg['run_id'],'region_id':cfg['unit_id'],
         'model_id':cfg['model_id'],'variant_id':'unadopted_low_ee_sensitivity',
         'source_identity':{'path':cfg['model_path'],'sha256':sha(model)},
         'computational_input_identity':{'source':sha(model),'configuration':sha(work/'inputs/configuration.json')},
         'methods':list(method_keys),'required_roles':roles,'artifacts':artifacts,
         'reconciliation':{'baselines_match_saved_coefficients':True,'protected_inputs_unchanged':True,
                          'matrices_axes_and_masks_verified':True}})
    completeness=checker.check(index);save(work/'qa/completeness.json',completeness)
    assert completeness['complete'],completeness
    checks[cfg['unit_id']]=qa
    data=frames[(frames.scenario=='predicted_ee_all_living')&(frames.method=='GE')].copy()
    living=data[(data.source_EE>.1)&(data.TL>1) | data.seq.isin(fits['all_living']['training_group_ids'])]
    low=data[data.seq.isin(report['low_ee_group_ids'])]
    ax.scatter(living.TL,living.source_EE,s=22,c='#176b87',alpha=.75,label='EE > 0.1')
    if len(low):
        ax.scatter(low.TL,low.source_EE,s=34,c='#b84735',label='Low source EE')
        ax.scatter(low.TL,low.scenario_EE,s=40,c='#b84735',marker='^',label='Predicted EE')
        for r in low.itertuples():ax.plot([r.TL,r.TL],[r.source_EE,r.scenario_EE],c='#b84735',alpha=.45,lw=.8)
    xx=np.linspace(max(.9,float(data.TL.min())),float(data.TL.max())+.1,100)
    for name,color,style in [('all_living','#176b87','-'),('consumers_only','#7a7770','--')]:
        f=fits[name];ax.plot(xx,f['intercept']+f['slope']*xx,color=color,ls=style,lw=1.3)
    ax.axhline(.1,color='#aaa',ls=':',lw=.8);ax.set_ylim(-.03,1.06)
    ax.set_title(labels[cfg['unit_id']]+'\n'+f"R² = {row['R_squared_all_living']:.3f}; {row['low_EE_groups']} low-EE groups",fontsize=10)
    ax.set_xlabel('Trophic level');ax.grid(alpha=.12);ax.spines[['top','right']].set_visible(False)
for ax in axes[:,0]:ax.set_ylabel('Ecotrophic efficiency')
fig.suptitle('EE–TL regressions: eight researcher-validated models',fontsize=15)
fig.text(.5,.02,'Blue line: all living groups with EE > 0.1. Dashed: consumers only. Red triangles: hypothetical predictions; no scientific adoption.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.06,1,.94]);fig.savefig(BASE/'outputs/ee_tl_fits.png',dpi=180);plt.close(fig)
pd.DataFrame(all_summaries).to_csv(BASE/'outputs/eight_model_comparison.csv',index=False,encoding='utf-8',float_format='%.17g')
save(BASE/'qa/eight_model_verification.json',checks)
save(BASE/'outputs/eight_model_comparison.json',all_summaries)
for row in all_summaries:
    print(row['unit_id'],'low',row['low_EE_groups'],'R2',round(row['R_squared_all_living'],4),
          'GE%',round(row['GE_PPR_percent_change'],4),'TE%',round(row['TE_PPR_percent_change'],4),
          'egestion%',round(row['With Egestion_PPR_percent_change'],4),
          'GE gap',round(row['GE_extended_PP_gap'],6),'TE gap',round(row['TE_extended_PP_gap'],6),flush=True)
print('VERIFIED',len(checks),'models',sum(v['scenario_count'] for v in checks.values()),'scenario/method results',flush=True)
