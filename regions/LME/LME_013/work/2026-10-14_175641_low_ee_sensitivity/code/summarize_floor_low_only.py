"""Verify the fine grid, identify geometric elbows and render unsmoothed curves."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,os,sys,time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
BASE=Path(__file__).resolve().parents[1]
FLOORS=[round(i/100,2) for i in range(1,51)]
OPTIONS=['GE','TE','With Egestion']
LABELS={'HS_077':'Eastern tropical Pacific','LME_028':'Guinea Current','LME_032':'Arabian Sea',
        'LME_034':'Bay of Bengal','LME_035':'Gulf of Thailand','LME_036':'Northern South China Sea',
        'LME_047':'East China Sea','LME_013':'Humboldt Current'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def elbow(series):
    s=series.sort_values('floor');x=s.floor.to_numpy();y=s.PPR_percent_change.to_numpy()
    result={'unit_id':s.unit_id.iloc[0],'model_name':s.model_name.iloc[0],'method':s.method.iloc[0],
            'range_start':float(x[0]),'range_end':float(x[-1]),'range_step':.01,
            'response_span_percentage_points':float(np.ptp(y)),
            'criterion':'maximum absolute deviation from endpoint chord after normalizing x and endpoint response; continuous two-segment least-squares as a second descriptive estimate',
            'interpretation':'Geometric curve feature; not an ecological optimum or validation.'}
    if (s.negative_source_entries>0).any():
        return {**result,'available':False,'reason':'range includes invalid negative source coefficients'}
    if np.ptp(y)<1:
        return {**result,'available':False,'reason':'less than one percentage point of response over tested range'}
    if abs(y[-1]-y[0])<.01:
        return {**result,'available':False,'reason':'endpoint responses too similar for endpoint normalization'}
    xn=(x-x[0])/(x[-1]-x[0]);yn=(y-y[0])/(y[-1]-y[0]);deviation=yn-xn
    k=int(np.argmax(abs(deviation[1:-1])))+1
    best=None
    for j in range(2,len(x)-2):
        design=np.column_stack([np.ones(len(x)),xn,np.maximum(0,xn-xn[j])])
        beta=np.linalg.lstsq(design,yn,rcond=None)[0];pred=design@beta
        sse=float(sum((yn-pred)**2))
        if best is None or sse<best['sse']:
            best={'floor':float(x[j]),'sse':sse,'slope_before_normalized':float(beta[1]),
                  'slope_after_normalized':float(beta[1]+beta[2]),'beta':beta.tolist()}
    return {**result,'available':True,'maximum_chord_deviation_floor':float(x[k]),
            'signed_normalized_chord_deviation':float(deviation[k]),
            'shape_at_chord_marker':'early response followed by flattening' if deviation[k]>0 else 'response accelerates later in range',
            'PPR_change_at_chord_marker':float(y[k]),'two_segment_breakpoint_floor':best['floor'],
            'two_segment_fit':best,
            'marker_bracket':[min(float(x[k]),best['floor']),max(float(x[k]),best['floor'])]}

def run():
    spec=importlib.util.spec_from_file_location('evidence_checker',ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    rows=[];groups=[];checks={};mode_changes=[]
    for entry in read(BASE/'inputs/models.json'):
        w=ROOT/entry['work'];cfg=read(w/'inputs/configuration.json');out=w/'outputs/floor_low_only'
        if not (out/'run_manifest.json').exists():
            print('WAITING FOR COMPLETED MODEL',entry['unit_id'],flush=True)
            deadline=time.monotonic()+600
            while not (out/'run_manifest.json').exists():
                if time.monotonic()>deadline:raise RuntimeError('Fine-grid model did not complete: '+entry['unit_id'])
                time.sleep(2)
        manifest=read(out/'run_manifest.json');summary=read(out/'scenario_summary.json')
        assert len(summary)==150 and {(r['floor'],r['method']) for r in summary}=={(f,m) for f in FLOORS for m in OPTIONS}
        assert manifest['baseline_runtime_exact'] and not manifest['failed_outcomes']
        protected=read(w/'inputs/floor_low_only_configuration.json')['protected_hashes']
        assert all(sha(ROOT/p)==h for p,h in protected.items())
        g=pd.read_csv(out/'group_comparison.csv',float_precision='round_trip');groups.append(g)
        assert set(g.floor)==set(FLOORS)
        coarse={(r['floor'],r['method']):r for r in read(w/'outputs/floor_grid/scenario_summary.json')}
        previous_modes={}
        for r in summary:
            assert r['status']=='computed_sensitivity' and r['finite_coefficients']
            folder=out/('floor_'+str(r['floor']).replace('.','p'))/r['method'].replace(' ','_')
            with gzip.open(folder/'full_return.json.gz','rt',encoding='utf-8') as f:ret=json.load(f)
            for name,mat in ret.items():
                assert mat['type']=='dataframe' and mat['shape']==[len(mat['index']),len(mat['columns'])]
                assert len(set(mat['index']))==len(mat['index']) and len(set(mat['columns']))==len(mat['columns'])
                assert len(mat['data'])==mat['shape'][0] and all(len(v)==mat['shape'][1] for v in mat['data'])
                assert all(len(mask)==mat['shape'][0] and all(len(v)==mat['shape'][1] for v in mask) for mask in mat['masks'].values())
            totals=pd.DataFrame(ret['SPPR']['data'],index=ret['SPPR']['index'],columns=ret['SPPR']['columns']).sum(axis=1)
            convenient=g[(g.floor==r['floor'])&(g.method==r['method'])].set_index('seq')
            eligible=r['eligible_group_ids']
            held=convenient.loc[~convenient.index.isin(eligible)]
            assert (held.source_EE==held.effective_EE).all()
            assert (held.source_M0==held.internal_M0).all()
            assert (held.hypothetical_external_sink==0).all()
            selected=convenient.loc[convenient.index.isin(eligible)]
            assert (selected.source_EE<.1).all()
            np.testing.assert_allclose(selected.effective_EE,np.maximum(selected.source_EE,r['floor']),rtol=0,atol=1e-15)
            np.testing.assert_allclose(totals.sort_index(),convenient.SPPR_all.sort_index(),rtol=1e-12,atol=1e-8)
            np.testing.assert_allclose(convenient.landings_2019_PPR_tC.sum(),r['landings_2019_ppr_tC'],rtol=1e-12,atol=1e-6)
            if r['floor']<=.1 and (r['floor'],r['method']) in coarse:
                assert r['landings_2019_ppr_tC']==coarse[(r['floor'],r['method'])]['landings_2019_ppr_tC']
            rec=r['recycling'];flags=[]
            if r['negative_source_entries']:flags.append('invalid negative source coefficients')
            if abs(r['relative_pp_budget_gap_with_external_sink'])>.01:flags.append('extended PP budget gap > 1%')
            if rec.get('unpooled_detritus_recycling_radius',0)>=1:flags.append('unpooled detritus recycling diverges')
            if rec.get('pooled_recycling_failure'):flags.append('pooled detritus recycling also diverges')
            if r['detritus_growth_negative']:flags.append('negative detritus stock residual retained')
            resolution=r.get('detritus_resolution') or {}
            # SPPR_new's TE branch scales basal DET columns directly and does not
            # update detritus_resolution_info. A retained GE label is therefore
            # stale metadata, not evidence that TE switched solver branches.
            if r['method']=='TE':
                mode='TE_direct_basal_scaling'
                resolution_note='TE branch verified in pinned engine; raw recycling-solver metadata is inapplicable and may be stale.'
            else:
                mode=resolution.get('method')
                assert mode in ('single_detritus','multi_detritus','pooled_detritus_scaling'),resolution
                resolution_note='Retained GE / With Egestion recycling-solver metadata.'
            before=previous_modes.get(r['method'])
            if before and before[1]!=mode:
                mode_changes.append({'unit_id':r['unit_id'],'method':r['method'],'floor_before':before[0],
                    'floor_after':r['floor'],'mode_before':before[1],'mode_after':mode})
            previous_modes[r['method']]=(r['floor'],mode)
            rows.append({'unit_id':r['unit_id'],'model_name':LABELS[r['unit_id']],'model_id':r['model_id'],
                'floor':r['floor'],'method':r['method'],'affected_group_count':r['affected_group_count'],
                'eligible_group_count':r['eligible_group_count'],'eligibility_threshold':.1,
                'baseline_PPR_tC':r['baseline_ppr_tC'],'PPR_tC':r['landings_2019_ppr_tC'],
                'PPR_percent_change':r['percent_change_from_baseline'],'native_is_sppr_balanced':r['native_is_sppr_balanced'],
                'native_PP_budget_gap_percent':100*r['native_relative_pp_gap'],
                'extended_PP_budget_gap_percent':100*r['relative_pp_budget_gap_with_external_sink'],
                'extended_PP_budget_strictly_balanced':r['strict_pp_budget_balanced_with_external_sink'],
                'hypothetical_external_sink_flow':r['hypothetical_external_sink_flow'],'external_sink_PP':r['hypothetical_external_sink_pp'],
                'negative_source_entries':r['negative_source_entries'],
                'unpooled_detritus_recycling_radius':rec.get('unpooled_detritus_recycling_radius'),
                'pooled_recycling_b':rec.get('pooled_recycling_b'),'rho_living':rec['rho_living'],
                'detritus_resolution_method':mode,'detritus_resolution_note':resolution_note,'scientific_flags':'; '.join(flags),
                'origin':r['origin'],'status':'unadopted numerical sensitivity'})
        verified={'outcomes':150,'matrices_and_masks_reopened':True,'group_and_PPR_sums_reconciled':True,
            'matching_unrestricted_points_through_0p1_match_exactly':True,'protected_inputs_unchanged':True,
            'baseline_runtime_exact':True,'native_and_extended_budgets_separate':True,
            'ineligible_groups_EE_M0_sink_unchanged':True,'fixed_eligibility_threshold':.1}
        save(w/'qa/floor_low_only_verification.json',verified)
        index=w/'qa/evidence_index.json';evidence=read(index)
        def add(role,p):
            item={'role':role,'path':Path(os.path.relpath(p,index.parent)).as_posix(),'sha256':sha(p),'availability':'present'}
            evidence['artifacts']=[a for a in evidence['artifacts'] if a['role']!=role]+[item]
            if role not in evidence['required_roles']:evidence['required_roles'].append(role)
        for role,p in [('floor_low_only_code',BASE/'code/test_floor_low_only.py'),('floor_low_only_summary_code',Path(__file__)),
                       ('floor_low_only_manifest',out/'run_manifest.json'),('floor_low_only_summary',out/'scenario_summary.json'),
                       ('floor_low_only_groups',out/'group_comparison.csv'),('floor_low_only_verification',w/'qa/floor_low_only_verification.json'),
                       ('floor_low_only_configuration',w/'inputs/floor_low_only_configuration.json')]:add(role,p)
        for r in summary:
            folder=out/('floor_'+str(r['floor']).replace('.','p'))/r['method'].replace(' ','_')
            for filename in ['full_return.json.gz','runtime.json.gz','metrics.json']:
                add('low_only_'+str(r['floor'])+'_'+r['method']+'_'+filename,folder/filename)
        save(index,evidence);complete=checker.check(index);save(w/'qa/completeness.json',complete)
        assert complete['complete'],complete
        checks[entry['unit_id']]=verified
        print('VERIFIED FINE MODEL',entry['unit_id'],flush=True)

    data=pd.DataFrame(rows);out=BASE/'outputs/floor_low_only'
    prior=pd.read_csv(BASE/'outputs/floor_fine/eight_model_fine_sensitivity.csv',float_precision='round_trip')
    prior=prior.rename(columns={'PPR_percent_change':'unrestricted_PPR_percent_change','PPR_tC':'unrestricted_PPR_tC'})
    data=data.merge(prior[['unit_id','floor','method','unrestricted_PPR_percent_change','unrestricted_PPR_tC']],on=['unit_id','floor','method'],validate='one_to_one')
    data['restricted_minus_unrestricted_percentage_points']=data.PPR_percent_change-data.unrestricted_PPR_percent_change
    np.testing.assert_allclose(data.loc[data.floor<=.1,'PPR_percent_change'],data.loc[data.floor<=.1,'unrestricted_PPR_percent_change'],rtol=1e-11,atol=1e-10)
    data.to_csv(out/'eight_model_fine_sensitivity.csv',index=False,encoding='utf-8',float_format='%.17g')
    combined=pd.concat(groups,ignore_index=True)
    combined.to_csv(out/'eight_model_group_sensitivity.csv',index=False,encoding='utf-8',float_format='%.17g')
    knees=[elbow(s) for _,s in data.groupby(['unit_id','method'],sort=False)]
    save(out/'knee_candidates.json',knees)
    pd.DataFrame([{k:v for k,v in r.items() if k not in ['two_segment_fit','marker_bracket']} for r in knees]).to_csv(
        out/'knee_candidates.csv',index=False,encoding='utf-8',float_format='%.17g')
    save(out/'detritus_mode_changes.json',mode_changes)
    save(BASE/'qa/eight_model_floor_low_only_verification.json',checks)

    colors=['#375e97','#4d9078','#99621e','#8064a2','#d16a44','#438aa4','#bf5b83','#172e3c']
    fig,axes=plt.subplots(1,3,figsize=(15,6))
    for ax,option in zip(axes,OPTIONS):
        for (unit,label),color in zip(LABELS.items(),colors):
            s=data[(data.unit_id==unit)&(data.method==option)].sort_values('floor')
            ax.plot(s.floor,s.PPR_percent_change,marker='.',lw=2.5 if unit=='LME_013' else 1.3,
                    markersize=3,alpha=.9,c=color,label=label)
            invalid=s[s.negative_source_entries>0]
            if len(invalid):ax.scatter(invalid.floor,invalid.PPR_percent_change,c='#b21e35',marker='x',s=25,zorder=5)
        ax.set_xlim(.005,.505);ax.set_xticks([.01,.05,.1,.2,.3,.4,.5]);ax.axvline(.1,color='#aaa',ls=':',lw=.8)
        ax.axhline(0,color='#aaa',lw=.8);ax.grid(alpha=.15);ax.set_title(option,fontsize=13)
        ax.set_xlabel('EE floor (linear spacing)');ax.set_ylabel('Change in 2019 landings PPR (%)')
        ax.spines[['top','right']].set_visible(False)
    if data[data.method=='With Egestion'].PPR_percent_change.abs().max()>50:
        axes[2].set_yscale('symlog',linthresh=5,linscale=1)
        axes[2].yaxis.set_major_formatter(ScalarFormatter())
        axes[2].set_title('With Egestion\n(symmetric log outside ±5%)',fontsize=11)
    fig.suptitle('EE-floor sensitivity restricted to original EE < 0.1',fontsize=16,y=.97)
    fig.text(.5,.90,'Floors 0.01–0.50, step 0.01; fixed eligible groups, original 2019 landings and allocations. No smoothing.',ha='center',fontsize=10)
    handles,names=axes[0].get_legend_handles_labels()
    fig.legend(handles,names,loc='lower center',ncol=4,bbox_to_anchor=(.5,.055),frameon=False,fontsize=9)
    fig.text(.5,.02,'External mortality is hypothetical; calculations are unadopted. Native and extended budgets are separate in the data.',ha='center',fontsize=9)
    fig.subplots_adjust(left=.055,right=.985,top=.80,bottom=.27,wspace=.32)
    fig.savefig(out/'ee_floor_low_only_all_models.png',dpi=180);plt.close(fig)

    # Per-model panels keep the smaller restricted responses visible while
    # showing exactly which later response the fixed eligible set removes.
    fig,axes=plt.subplots(2,4,figsize=(15,7))
    for ax,(unit,label) in zip(axes.flat,LABELS.items()):
        s=data[(data.unit_id==unit)&(data.method=='TE')].sort_values('floor')
        ax.plot(s.floor,s.PPR_percent_change,c='#176b87',lw=2,label='Only original EE < 0.1')
        ax.plot(s.floor,s.unrestricted_PPR_percent_change,c='#999',lw=1.4,ls='--',label='Previous: all eligible groups')
        ax.axvline(.1,c='#aaa',lw=.7,ls=':');ax.axhline(0,c='#aaa',lw=.7)
        ax.set_title(label+' (n='+str(int(s.eligible_group_count.iloc[0]))+')',fontsize=10)
        ax.set_xlim(.01,.5);ax.grid(alpha=.15);ax.spines[['top','right']].set_visible(False)
        ax.set_xlabel('EE floor');ax.set_ylabel('PPR change (%)')
    handles,names=axes.flat[0].get_legend_handles_labels()
    fig.legend(handles,names,loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(.5,.015))
    fig.suptitle('TE sensitivity: fixed original EE < 0.1 groups versus previous sweep',fontsize=15)
    fig.text(.5,.94,'Panel scales differ; n is the fixed eligible group count. Both curves use the same baseline and 2019 catch allocations.',ha='center',fontsize=10)
    fig.tight_layout(rect=[0,.08,1,.91]);fig.savefig(out/'TE_restricted_vs_previous_by_model.png',dpi=180);plt.close(fig)

    hum=data[data.unit_id=='LME_013'];te=hum[hum.method=='TE'].sort_values('floor')
    candidate=next(k for k in knees if k['unit_id']=='LME_013' and k['method']=='TE')
    fig,(full,zoom)=plt.subplots(1,2,figsize=(13,5.5),gridspec_kw={'width_ratios':[1.2,1]})
    method_colors={'GE':'#d16a44','TE':'#176b87','With Egestion':'#4d9078'}
    for option,color in method_colors.items():
        s=hum[hum.method==option].sort_values('floor')
        full.plot(s.floor,s.PPR_percent_change,'o-',c=color,markersize=3,lw=1.7,label=option+' restricted')
        full.plot(s.floor,s.unrestricted_PPR_percent_change,'--',c=color,lw=1.2,alpha=.6,label=option+' previous')
    z=te[te.floor<=.15];zoom.plot(z.floor,z.PPR_percent_change,'o-',c=method_colors['TE'],markersize=5,lw=2)
    if candidate['available']:
        lo,hi=candidate['marker_bracket']
        for ax in [full,zoom]:
            ax.axvspan(lo,hi,color='#eab85b',alpha=.22)
            ax.axvline(candidate['maximum_chord_deviation_floor'],c='#a16b0b',ls='--',lw=1)
            ax.axvline(candidate['two_segment_breakpoint_floor'],c='#a16b0b',ls=':',lw=1)
        zoom.text(.98,.97,f"Elbow estimates: {lo:.2f}–{hi:.2f}\nDashed: chord deviation\nDotted: two-segment fit",transform=zoom.transAxes,
                  ha='right',va='top',fontsize=9,bbox={'facecolor':'white','edgecolor':'#ddd','alpha':.9})
    base_groups=pd.read_csv(BASE/'outputs/group_comparison.csv',float_precision='round_trip')
    conger=float(base_groups[(base_groups.scenario=='baseline')&(base_groups.method=='GE')&(base_groups.group=='Conger')].source_EE.iloc[0])
    zoom.axvline(conger,c='#999',ls='-',lw=.7)
    zoom.annotate(f'Conger enters the floor\nat EE = {conger:.4f}',xy=(conger,float(z.PPR_percent_change.iloc[0])),
                  xytext=(.022,-20),fontsize=8,color='#666',arrowprops={'arrowstyle':'->','color':'#999','lw':.8})
    for ax in [full,zoom]:
        ax.grid(alpha=.15);ax.set_xlabel('EE floor');ax.set_ylabel('Change in 2019 landings PPR (%)')
        ax.spines[['top','right']].set_visible(False)
    full.set_xlim(.005,.505);full.set_title('Humboldt: solid restricted / dashed previous')
    handles,_=full.get_legend_handles_labels()
    full.legend(handles[::2],OPTIONS,frameon=False,loc='center right',bbox_to_anchor=(.98,.4),fontsize=9)
    zoom.set_xlim(.008,.152);zoom.set_xticks([.01,.03,.05,.07,.1,.15]);zoom.set_title('TE close-up: early response and flattening')
    fig.suptitle('Humboldt: floor only for original EE < 0.1',fontsize=15,y=.97)
    fig.text(.5,.035,'Shading spans two geometric elbow estimates on 0.01–0.50. It is not an ecological calibration or a recommended floor.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.08,1,.91]);fig.savefig(out/'humboldt_knee_detail.png',dpi=200);plt.close(fig)

    # Identify the groups driving the initial TE drop without changing allocations.
    hum_groups=combined[(combined.unit_id=='LME_013')&(combined.method=='TE')]
    a=hum_groups[hum_groups.floor==.01].set_index('seq')
    b=hum_groups[hum_groups.floor==.05].set_index('seq')
    drivers=(b.landings_2019_PPR_tC-a.landings_2019_PPR_tC).sort_values()
    driver_records=[{'seq':int(s),'group':str(b.loc[s,'group']),'PPR_change_tC_0p01_to_0p05':float(v)} for s,v in drivers.head(10).items()]
    save(out/'humboldt_early_TE_drivers.json',driver_records)
    data[data.floor.isin([.01,.05,.07,.1,.2,.3,.5])].to_csv(out/'selected_floors_comparison.csv',index=False,encoding='utf-8',float_format='%.17g')
    print('RESTRICTED ENDPOINTS',data[data.floor==.5][['unit_id','method','eligible_group_count','PPR_percent_change','unrestricted_PPR_percent_change']].to_dict('records'),flush=True)
    print('HUMBOLDT TE ELBOW',json.dumps(candidate,ensure_ascii=False),flush=True)
    print('MODE CHANGES',mode_changes,flush=True)
    print('NEGATIVE OUTCOMES',data[data.negative_source_entries>0][['unit_id','floor','method','negative_source_entries']].to_dict('records'),flush=True)
    print('TE EARLY DRIVERS',driver_records[:3],flush=True)
    print('VERIFIED FINE GRID',len(checks),'models',len(data),'outcomes',flush=True)

if __name__=='__main__':sys.stdout.reconfigure(encoding='utf-8');run()
