"""Verify and summarize the requested five-floor experiment; no publication."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,os,sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
BASE=Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
labels={'HS_077':'Eastern tropical Pacific','LME_028':'Guinea Current','LME_032':'Arabian Sea',
        'LME_034':'Bay of Bengal','LME_035':'Gulf of Thailand','LME_036':'Northern South China Sea',
        'LME_047':'East China Sea','LME_013':'Humboldt Current'}
floors=[.01,.05,.1,.3,.95];options=['GE','TE','With Egestion']
spec=importlib.util.spec_from_file_location('evidence_checker',ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
rows=[];group_frames=[];checks={}
for entry in read(BASE/'inputs/models.json'):
    w=ROOT/entry['work'];cfg=read(w/'inputs/configuration.json');out=w/'outputs/floor_grid'
    manifest=read(out/'run_manifest.json');summary=read(out/'scenario_summary.json')
    assert len(summary)==15 and {(r['floor'],r['method']) for r in summary}=={(f,m) for f in floors for m in options}
    assert manifest['baseline_runtime_exact'] and not manifest['failed_outcomes']
    assert all(sha(ROOT/p)==h for p,h in cfg['protected_hashes'].items())
    group_data=pd.read_csv(out/'group_comparison.csv',float_precision='round_trip');group_frames.append(group_data)
    assert set(group_data['floor'])==set(floors), 'CSV floor labels did not round-trip'
    for r in summary:
        assert r['status']=='computed_sensitivity' and r['finite_coefficients']
        folder=out/('floor_'+str(r['floor']).replace('.','p'))/r['method'].replace(' ','_')
        with gzip.open(folder/'full_return.json.gz','rt',encoding='utf-8') as f:ret=json.load(f)
        for name,mat in ret.items():
            assert mat['type']=='dataframe'
            assert mat['shape']==[len(mat['index']),len(mat['columns'])]
            assert len(set(mat['index']))==len(mat['index']) and len(set(mat['columns']))==len(mat['columns'])
            assert len(mat['data'])==mat['shape'][0] and all(len(row)==mat['shape'][1] for row in mat['data'])
            assert all(len(mask)==mat['shape'][0] and all(len(row)==mat['shape'][1] for row in mask) for mask in mat['masks'].values())
        sppr=pd.DataFrame(ret['SPPR']['data'],index=ret['SPPR']['index'],columns=ret['SPPR']['columns']).sum(axis=1)
        convenient=group_data[(group_data.floor==r['floor'])&(group_data.method==r['method'])].set_index('seq')
        np.testing.assert_allclose(sppr.sort_index(),convenient.SPPR_all.sort_index(),rtol=1e-12,atol=1e-8)
        np.testing.assert_allclose(convenient.landings_2019_PPR_tC.sum(),r['landings_2019_ppr_tC'],rtol=1e-12,atol=1e-6)
        if r['floor']==.1:
            prior=next(v for v in read(w/'outputs/ee_floor_summary.json') if v['method']==r['method'])
            assert r['landings_2019_ppr_tC']==prior['landings_2019_ppr_tC']
        rec=r['recycling'];flags=[]
        if r['negative_source_entries']:flags.append('invalid negative source coefficients')
        if abs(r['relative_pp_budget_gap_with_external_sink'])>.01:flags.append('extended PP budget gap > 1%')
        if rec.get('unpooled_detritus_recycling_radius',0)>=1:flags.append('unpooled detritus recycling diverges')
        if rec.get('pooled_recycling_failure'):flags.append('pooled detritus recycling also diverges')
        if r['detritus_growth_negative']:flags.append('negative detritus stock residual retained')
        rows.append({'unit_id':r['unit_id'],'model_name':labels[r['unit_id']],'model_id':r['model_id'],
             'floor':r['floor'],'method':r['method'],'affected_group_count':r['affected_group_count'],
             'baseline_PPR_tC':r['baseline_ppr_tC'],'PPR_tC':r['landings_2019_ppr_tC'],
             'PPR_percent_change':r['percent_change_from_baseline'],
             'native_is_sppr_balanced':r['native_is_sppr_balanced'],
             'native_PP_budget_gap_percent':100*r['native_relative_pp_gap'],
             'extended_PP_budget_gap_percent':100*r['relative_pp_budget_gap_with_external_sink'],
             'extended_PP_budget_strictly_balanced':r['strict_pp_budget_balanced_with_external_sink'],
             'hypothetical_external_sink_flow':r['hypothetical_external_sink_flow'],
             'external_sink_PP':r['hypothetical_external_sink_pp'],'negative_source_entries':r['negative_source_entries'],
             'unpooled_detritus_recycling_radius':rec.get('unpooled_detritus_recycling_radius'),
             'pooled_recycling_b':rec.get('pooled_recycling_b'),
             'rho_living':rec['rho_living'],'scientific_flags':'; '.join(flags),
             'origin':r['origin'],'status':'unadopted numerical sensitivity'})
    verified={'outcomes':15,'matrices_and_masks_reopened':True,'group_and_PPR_sums_reconciled':True,
              'floor_0p1_matches_previous_experiment_exactly':True,'protected_inputs_unchanged':True,
              'baseline_runtime_exact':True,'native_and_extended_budgets_separate':True}
    save(w/'qa/floor_grid_verification.json',verified)
    index=w/'qa/evidence_index.json';evidence=read(index)
    def add(role,p):
        item={'role':role,'path':Path(os.path.relpath(p,index.parent)).as_posix(),'sha256':sha(p),'availability':'present'}
        evidence['artifacts']=[a for a in evidence['artifacts'] if a['role']!=role]+[item]
        if role not in evidence['required_roles']:evidence['required_roles'].append(role)
    for role,p in [('floor_grid_code',BASE/'code/test_floor_grid.py'),('floor_grid_summary_code',Path(__file__)),
                   ('floor_grid_manifest',out/'run_manifest.json'),('floor_grid_summary',out/'scenario_summary.json'),
                   ('floor_grid_groups',out/'group_comparison.csv'),('floor_grid_verification',w/'qa/floor_grid_verification.json')]:add(role,p)
    for r in summary:
        folder=out/('floor_'+str(r['floor']).replace('.','p'))/r['method'].replace(' ','_')
        for filename in ['full_return.json.gz','runtime.json.gz','metrics.json']:
            add('grid_'+str(r['floor'])+'_'+r['method']+'_'+filename,folder/filename)
    save(index,evidence);complete=checker.check(index);save(w/'qa/completeness.json',complete)
    assert complete['complete'],complete
    checks[entry['unit_id']]=verified

data=pd.DataFrame(rows);output=BASE/'outputs/floor_grid'
data.to_csv(output/'eight_model_floor_sensitivity.csv',index=False,encoding='utf-8',float_format='%.17g')
pd.concat(group_frames,ignore_index=True).to_csv(output/'eight_model_group_sensitivity.csv',index=False,encoding='utf-8',float_format='%.17g')
save(output/'eight_model_floor_sensitivity.json',rows)
save(BASE/'qa/eight_model_floor_grid_verification.json',checks)

colors=['#375e97','#4d9078','#99621e','#8064a2','#d16a44','#438aa4','#bf5b83','#172e3c']
fig,axes=plt.subplots(1,3,figsize=(15,6))
for ax,option in zip(axes,options):
    for (unit,label),color in zip(labels.items(),colors):
        series=data[(data.unit_id==unit)&(data.method==option)].sort_values('floor')
        ax.plot(series.floor,series.PPR_percent_change,marker='o',lw=2.5 if unit=='LME_013' else 1.4,
                markersize=5,alpha=.9,c=color,label=label)
        invalid=series[series.negative_source_entries>0]
        if len(invalid):ax.scatter(invalid.floor,invalid.PPR_percent_change,c='#b21e35',marker='x',s=95,lw=2,zorder=5)
    ax.set_xscale('log');ax.set_xticks(floors,labels=['0.01','0.05','0.1','0.3','0.95'])
    ax.minorticks_off();ax.axhline(0,color='#aaa',lw=.8);ax.grid(alpha=.15)
    ax.set_title(option,fontsize=13);ax.set_xlabel('EE floor (logarithmic spacing)')
    ax.spines[['top','right']].set_visible(False)
    ax.set_ylabel('Change in 2019 landings PPR (%)')
axes[2].set_yscale('symlog',linthresh=5,linscale=1)
axes[2].set_yticks([-1000,-100,-10,-5,0,5]);axes[2].yaxis.set_major_formatter(ScalarFormatter())
axes[2].set_title('With Egestion\n(symmetric log scale outside ±5%)',fontsize=11)
axes[2].annotate('Invalid negative coefficients\nBay of Bengal, floor 0.95',xy=(.95,-753.2207),xytext=(.018,-230),
                 fontsize=8,color='#b21e35',arrowprops={'arrowstyle':'->','color':'#b21e35','lw':.8})
fig.suptitle('Sensitivity to EE floors — eight validated models',fontsize=16,y=.97)
fig.text(.5,.90,'2019 landings; original allocations; changes relative to no-floor baseline. External mortality is hypothetical.',ha='center',fontsize=10)
handles,legend_labels=axes[0].get_legend_handles_labels()
fig.legend(handles,legend_labels,loc='lower center',ncol=4,bbox_to_anchor=(.5,.06),frameon=False,fontsize=9)
fig.text(.5,.025,'Numerical sensitivity only. Existing diagnostic restrictions remain; native and extended balance checks are separate in the data.',ha='center',fontsize=9)
fig.subplots_adjust(left=.055,right=.985,top=.80,bottom=.27,wspace=.32)
fig.savefig(output/'ee_floor_sensitivity.png',dpi=180);plt.close(fig)

for option in options:
    print('\n',option)
    print(data[data.method==option].pivot(index='unit_id',columns='floor',values='PPR_percent_change').round(4).to_string())
invalid=data[data.negative_source_entries>0]
print('INVALID NEGATIVE OUTCOMES',invalid[['unit_id','floor','method','PPR_tC','negative_source_entries']].to_dict('records'))
print('VERIFIED GRID',len(checks),'models,',len(data),'outcomes; 0.1 exact parity; all protected inputs unchanged.')
