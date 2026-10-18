"""Conditional taxon-resolution transport of saved TE SPPR, never a solver run.

Run from any directory with Python 3.11+, numpy and matplotlib. The script reads
the existing experiment, current published allocation payload, and prior bounded
decomposition. It writes only this study's derived results/evidence/figures.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

STUDY = Path(__file__).resolve().parents[1]
ROOT = next(p for p in STUDY.parents if (p/'Project.xlsx').is_file())
RESULTS, EVIDENCE, INPUTS = [STUDY/x for x in ('results','evidence','inputs')]
for p in (RESULTS,EVIDENCE,INPUTS): p.mkdir(parents=True,exist_ok=True)
EXPERIMENT=ROOT/'research/human/sppr_trophic_level_20261018_validated7'
PRIOR=ROOT/'regions/LME/LME_028/work/2026-10-18_121535_trophic_aggregation_validated7/outputs/decomposition.json'
HASHES={}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def register(p,role):
    HASHES[p.relative_to(ROOT).as_posix()]={'sha256':sha(p),'role':role}
def read_json(p,role):
    register(p,role)
    return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,data):
    p.write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def finite(x): return isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x)
def close(a,b,rel=1e-10):
    assert math.isclose(a,b,rel_tol=rel,abs_tol=1e-9),(a,b)
def weighted_mean(x,w): return float(np.dot(x,w)/w.sum())

register(Path(__file__),'Successor analysis implementation')
register(Path(__file__).with_name('render_report.py'),'Successor report generator implementation')
prior=read_json(PRIOR,'Current seven-cohort 2019 allocation/Jensen decomposition; read-only cross-check')
records=read_json(EXPERIMENT/'results/group_records.json','Saved consumer-group SPPR and effective classic TL; TE records used')
experiment_summary=read_json(EXPERIMENT/'results/comparison.json','Existing model diagnostic and descriptive summaries')
lineage=read_json(EXPERIMENT/'inputs/source_hashes.json','Existing experiment source identity ledger')
register(EXPERIMENT/'code/analyze.py','Interpretation of saved experiment definitions')
html=ROOT/'interactive_map/trends.html'
register(html,'Published default model selection, group exclusions, catch/taxon/group coefficients')
db=json.loads(re.search(r'const SERIES_DB=(.*?);</script>',html.read_text(encoding='utf-8'),re.S).group(1))
from cohort_guard import validate_cohort
cohort_manifest,cohort_pairs,expected_counts=validate_cohort(ROOT,STUDY,EXPERIMENT,PRIOR,records,prior,db,'TE',register)

for name,digest in prior['sources_sha256'].items():
    p=ROOT/name
    assert sha(p)==digest,('Prior consumed input changed',name)
    register(p,'Published catch/Classic PPR source verified by prior decomposition')
te=[r for r in records if r['method']=='TE']
assert len(te)==expected_counts['consumer_groups']
te_by_key={(r['unit'],r['group']):r for r in te}
assert len(te_by_key)==len(te)
units=sorted({r['unit'] for r in te})
assert set((r['unit'],r['model_id']) for r in te)==cohort_pairs
labels={r['unit']:r['label'] for r in experiment_summary['models']}
models={}; omitted_groups={}; source_checks=[]
for uid in units:
    u=db['units'][uid];m=next(x for x in u['models'] if x['id']==u['default_model'])
    assert m['researcher_review']['status']=='Validated by researcher'
    models[uid]=m;omitted_groups[uid]=m['display_ppr_excluded_group_ids']
    # Recheck original model-local scientific/result sources relevant to this
    # manifest-defined study. Project authority and transitive source hashes are checked.
    paths={r['coefficient_source'] for r in te if r['unit']==uid}
    assert len(paths)==1
    manifest_path=ROOT/paths.pop()
    for p in (manifest_path,manifest_path.parent/'regional_snapshot.xlsx',manifest_path.parents[1]/'model.json'):
        relative=p.relative_to(ROOT).as_posix()
        assert sha(p)==lineage[relative],('Experiment source changed',relative)
        register(p,'Relevant model-local source whose identity backs the existing experiment')
        source_checks.append({'path':relative,'matches_upstream_experiment':True})

prior_groups={(g['unit_id'],g['group']):g for g in prior['groups']}
groups=[];pairs=[];n_positive_taxa=0;missing=[]
for uid in units:
    u=db['units'][uid]; m=models[uid];inp=u['group_inputs'];gd=m['group_data'];yi=inp['years'].index(2019)
    bins={}
    for ti,name in enumerate(inp['taxa']):
        c=inp['full_precision_catch'][ti][yi]
        if not finite(c) or c<=0:continue
        mappings=[(gi,w) for gi,w in gd['mappings'][ti] if gd['groups'][gi]['id'] not in omitted_groups[uid] and finite(w) and w>0]
        if not mappings:continue
        s=inp['simple_sppr'][ti]
        if not finite(s) or s<=0:
            missing.append({'unit':uid,'taxon':name,'catch':c});continue
        n_positive_taxa+=1
        for gi,w in mappings:
            gname=gd['groups'][gi]['id'];key=(uid,gname)
            row={'unit':uid,'group':gname,'taxon':name,'catch_allocated':c*w,'allocation_weight':w,'TL':1+math.log10(s),'simple_sppr':s}
            bins.setdefault(key,[]).append(row);pairs.append(row)
    for key,rows in bins.items():
        old=prior_groups[key];exp=te_by_key[key]
        assert exp['model_id']==m['id']
        C=sum(r['catch_allocated'] for r in rows)
        mu=sum(r['catch_allocated']*r['TL'] for r in rows)/C
        S=exp['s'];T=exp['TL']
        assert finite(S) and S>0
        close(C,old['catch_tonnes']);close(mu,old['taxon_tl_mean']);close(S,old['new_te']['all::new_TE_EEfix']);close(T,old['effective_classic_tl'])
        groups.append({'unit':uid,'group':key[1],'model_id':m['id'],'C':C,'S':S,'T':T,'mu':mu,'tl_delta':mu-T,'simple_total_wet':sum(r['catch_allocated']*r['simple_sppr'] for r in rows),'classic_total_wet':C*exp['fixed10_s'],'base_tC':C*S/9,'n_taxa':len(rows),'TL_min':min(r['TL'] for r in rows),'TL_max':max(r['TL'] for r in rows),'rows':rows,'annual_status':exp['annual_status'],'diagnostic_status':exp['diagnostic_status'],'rho_living':exp['rho_living']})
assert not missing
assert len(groups)==expected_counts['catch_groups'] and n_positive_taxa==expected_counts['region_taxon_records']
assert len(pairs)==expected_counts['taxon_group_allocations']
assert set((g['unit'],g['model_id']) for g in groups)==cohort_pairs
assert set((g['unit'],g['group']) for g in groups)==set(prior_groups)
group_by_key={(g['unit'],g['group']):g for g in groups}
base=sum(g['base_tC'] for g in groups)
simple=sum(g['simple_total_wet']/9 for g in groups)
classic=sum(g['classic_total_wet']/9 for g in groups)
close(base,prior['new_te_scenarios'][0]['base_tC'])
close(simple,prior['aggregate']['simple']/9)
close(classic,prior['aggregate']['saved_group_classic']/9)

# A group is an observation. Weights below are descriptive choices, not a claim
# of independent species observations, precision weights or statistical validity.
fitrows=[]
for r in te:
    g=group_by_key.get((r['unit'],r['group']))
    fitrows.append({**r,'C':g['C'] if g else 0.,'PPR':g['base_tC'] if g else 0.,'default_included':r['group'] not in omitted_groups[r['unit']]})

def fit(rows,weight='uniform',mode='pooled'):
    rr=[r for r in rows if finite(r['s']) and r['s']>0 and (weight=='uniform' or r[weight]>0)]
    x=np.array([r['TL'] for r in rr]);y=np.log10([r['s'] for r in rr]);w=np.array([1. if weight=='uniform' else r[weight] for r in rr]);u=np.array([r['unit'] for r in rr])
    n_groups=len(rr);model_ids=sorted(set(u))
    xraw=x.copy();yraw=y.copy();wraw=w.copy()
    if mode=='between':
        means=[]
        for uid in model_ids:
            z=u==uid;means.append((weighted_mean(x[z],w[z]),weighted_mean(y[z],w[z]),w[z].sum()))
        x,y,_=np.array(means).T
        # Equal weight per model prevents the between-model comparison merely
        # repeating differences in number of included groups or fishing scale.
        w=np.ones(len(model_ids));u=np.array(model_ids)
    xmean=weighted_mean(x,w);ymean=weighted_mean(y,w)
    if mode=='within':
        xc=x.copy();yc=y.copy();intercepts={}
        for uid in model_ids:
            z=u==uid;xc[z]-=weighted_mean(x[z],w[z]);yc[z]-=weighted_mean(y[z],w[z])
    else:xc=x-xmean;yc=y-ymean
    b=float(np.dot(w*xc,yc)/np.dot(w*xc,xc))
    if mode=='within':
        intercepts={uid:weighted_mean(y[u==uid],w[u==uid])-b*weighted_mean(x[u==uid],w[u==uid]) for uid in model_ids}
        pred=np.array([intercepts[uid] for uid in u])+b*x
        sst=float(np.dot(w*yc,yc))
    else:
        intercepts={'pooled':ymean-b*xmean};pred=intercepts['pooled']+b*x;sst=float(np.dot(w*yc,yc))
    residual=y-pred;sse=float(np.dot(w*residual,residual));r2=1-sse/sst if sst else None
    # Smearing is descriptive only: anchored transport preserves each observed
    # group residual, so multiplying transport by this factor would double count.
    smear=weighted_mean(10**residual,w)
    return {'slope':b,'log10_intercepts':intercepts,'r2':r2,'r2_definition':'weighted within-model variation' if mode=='within' else 'weighted centered log10(SPPR) variation','n_observations':len(x),'n_source_groups':n_groups,'n_models':len(model_ids),'models':model_ids,'TL_range':[float(xraw.min()),float(xraw.max())],'fit_TL_range':[float(x.min()),float(x.max())],'SPPR_range':[float(10**yraw.min()),float(10**yraw.max())],'residual_rmse_log10':float(math.sqrt(sse/w.sum())),'descriptive_residual_smearing_factor':smear,'weight':weight,'mode':mode,'between_model_weight':'equal per model; within-model centroids use selected group weighting' if mode=='between' else None}

cohorts={
    'all_consumer_uniform':(fitrows,'uniform'),
    'review_included_uniform':([r for r in fitrows if r['default_included']],'uniform'),
    'fished_uniform':([r for r in fitrows if r['C']>0],'uniform'),
    'fished_catch':(fitrows,'C'),
    'fished_ppr':(fitrows,'PPR'),
}
regressions={}
for calibration_name,(rows,weight) in cohorts.items():
    for mode in ('pooled','within','between'):
        regressions[calibration_name+'__'+mode]=fit(rows,weight,mode)
per_model=[]
for uid in units:
    for weight in ('uniform','C','PPR'):
        z=fit([r for r in fitrows if r['unit']==uid and r['default_included']],weight)
        per_model.append({'unit':uid,**z})

def transport(b):
    totals={'base_tC':0.,'shift_only_tC':0.,'full_tC':0.,'centered_jensen_only_tC':0.}
    regional={uid:{**totals,'simple_tC':0.,'classic_tC':0.} for uid in units};detail=[]
    for g in groups:
        dx=np.array([r['TL']-g['mu'] for r in g['rows']]);cw=np.array([r['catch_allocated'] for r in g['rows']])/g['C']
        shift=10**(b*g['tl_delta']);J=float(np.dot(cw,10**(b*dx)));factor=shift*J
        entry={'unit':g['unit'],'group':g['group'],'b':b,'C':g['C'],'S':g['S'],'T':g['T'],'mu':g['mu'],'tl_delta':g['tl_delta'],'shift_factor':shift,'within_group_J':J,'full_factor':factor,'base_tC':g['base_tC'],'shift_only_tC':g['base_tC']*shift,'full_tC':g['base_tC']*factor,'centered_jensen_only_tC':g['base_tC']*J,'change_tC':g['base_tC']*(factor-1)}
        # Independent per-taxon sum verifies shift/Jensen factorization.
        direct=sum(r['catch_allocated']*g['S']*10**(b*(r['TL']-g['T']))/9 for r in g['rows'])
        close(direct,entry['full_tC'])
        for k in totals:totals[k]+=entry[k];regional[g['unit']][k]+=entry[k]
        regional[g['unit']]['simple_tC']+=g['simple_total_wet']/9
        regional[g['unit']]['classic_tC']+=g['classic_total_wet']/9
        detail.append(entry)
    for uid,r in regional.items():
        r.update({'unit':uid,'label':labels[uid],'full_over_base':r['full_tC']/r['base_tC'],'full_over_classic':r['full_tC']/r['classic_tC'],'full_over_simple':r['full_tC']/r['simple_tC'],'baseline_share':r['base_tC']/base,'scenario_share':r['full_tC']/totals['full_tC'],'change_tC':r['full_tC']-r['base_tC']})
    totals.update({'b':b,'full_over_base':totals['full_tC']/base,'shift_over_base':totals['shift_only_tC']/base,'full_over_shift_jensen':totals['full_tC']/totals['shift_only_tC'],'centered_jensen_over_base':totals['centered_jensen_only_tC']/base,'full_over_classic':totals['full_tC']/classic,'full_over_simple':totals['full_tC']/simple,'regional':list(regional.values())})
    return totals,detail

scenario_defs=[('identity_b0',0.,'Identity: retain saved group coefficients'),('unit_slope_b1',1.,'Assume one log10 SPPR unit per trophic level')]
scenario_defs += [(k,regressions[k]['slope'],'Conditional anchored transport using descriptive '+k) for k in regressions if not k.endswith('__between')]
scenarios=[];group_scenarios={}
for name,b,description in scenario_defs:
    t,d=transport(b);scenarios.append({'id':name,'description':description,**t});group_scenarios[name]=d

lomo=[]
for calibration_name,(rows,weight) in cohorts.items():
    for mode in ('pooled','within'):
        for omitted in units:
            f=fit([r for r in rows if r['unit']!=omitted],weight,mode)
            t,_=transport(f['slope'])
            held=next(x for x in t['regional'] if x['unit']==omitted)
            lomo.append({'fit':calibration_name+'__'+mode,'omitted_model':omitted,'training_slope':f['slope'],'training_r2':f['r2'],'full_cohort_total_tC':t['full_tC'],'full_cohort_factor':t['full_over_base'],'held_out_model_factor':held['full_over_base'],'note':'Omission changes slope fitting only. Scenario is reapplied to the same full manifest-defined catch cohort.'})

b1=next(s for s in scenarios if s['id']=='unit_slope_b1');b1g=group_scenarios['unit_slope_b1']
for g in b1g:
    g['baseline_share']=g['base_tC']/base;g['scenario_share']=g['full_tC']/b1['full_tC']
extreme={}
for criterion,reverse in [('base_tC',True),('full_tC',True),('change_tC',True),('change_tC',False),('full_factor',True),('full_factor',False)]:
    extreme[criterion+('_largest' if reverse else '_smallest')]=sorted(b1g,key=lambda g:g[criterion],reverse=reverse)[:10]
influence=[]
for k in (1,3,5,10):
    top=sorted(b1g,key=lambda g:g['base_tC'],reverse=True)[:k]
    removed=sum(g['base_tC'] for g in top);remain_full=b1['full_tC']-sum(g['full_tC'] for g in top)
    influence.append({'top_n_by_baseline_PPR':k,'removed_baseline_share':removed/base,'remaining_full_factor':remain_full/(base-removed),'removed_groups':[(g['unit'],g['group']) for g in top],'interpretation':'Influence diagnostic only; removing these groups is not an authorized scientific selection.'})

diagnostics=[]
for uid in units:
    z=next(x for x in experiment_summary['models'] if x['unit']==uid)['stats']['TE']
    diagnostics.append({'unit':uid,'model_id':models[uid]['id'],'excluded_groups':omitted_groups[uid],'diagnostic_status':z['status'],'rho_living':z['rho_living'],'annual_status':z['annual_status'],'published_annual_status':models[uid]['scopes']['all']['methods']['new_TE_EEfix']['status'],'use_ee_floor':next(r['effective_constructor']['use_ee_floor'] for r in te if r['unit']==uid),'ee_floor':next(r['effective_constructor']['ee_floor'] for r in te if r['unit']==uid)})

assert cohort_manifest == json.loads((INPUTS/'cohort.json').read_text(encoding='utf-8-sig'))
summary={
 'purpose':'Describe conditional total taxon-resolution PPR scenarios, not estimate an identified true correction.',
 'cohort':cohort_manifest,
 'expected_counts':expected_counts,
 'state':{'year':2019,'basis':'catch (landings plus discards)','scope':'all','unidentified':'method','model_selection':'manifest-defined published validated default models','groups':'signed-review default exclusions retained, original allocation weights never renormalized','taxon_TL':'1+log10(saved simple coefficient), previously reconciled to current Classic PPR Taxa','group_TL':'1+log10(saved SPPR_1995_TE0.1), cycle-broken/detritus-basal effective TL','engine_runs':0},
 'sample':{'consumer_groups_in_experiment':len(te),'positive_TE_groups_in_experiment':sum(finite(r['s']) and r['s']>0 for r in te),'zero_TE_groups_in_experiment':sum(r['s']==0 for r in te),'review_included_positive':regressions['review_included_uniform__pooled']['n_observations'],'positive_catch_groups':len(groups),'region_taxon_records':n_positive_taxa,'taxon_group_allocations':len(pairs),'regions':len(units),'covered_catch_tonnes':sum(g['C'] for g in groups),'missing_positive_catch_coefficients':missing},
 'baseline':{'new_TE_tC':base,'classic_model_tC':classic,'simple_taxon_tC':simple,'new_over_classic':base/classic,'new_over_simple':base/simple,'simple_over_classic':simple/classic},
 'transport_definition':{'anchored_taxon_coefficient':'s_ig(b)=S_g * 10**(b*(T_i-T_g)); different mapped groups retain their own anchors','group_shift':'10**(b*(mu_g-T_g))','within_group_jensen':'sum_i q_ig * 10**(b*(T_i-mu_g))','group_total':'C_g*S_g*shift_g*J_g /9','assumptions':['The fitted between-group TL relation is assumed to transport within a functional group, although this is untested.','Each taxon retains its group-specific multiplicative residual/efficiency/feedback factor.','Diet, network structure, EE/TE, catch allocations and source decomposition are not recomputed.','Reference taxon TL and effective model TL are treated as comparable despite different source/definition conventions.'],'not_a_confidence_interval':'The scenario spread and leave-one-model-out range are sensitivity analyses, not calibrated uncertainty bounds for true PPR.'},
 'retransformation':{'log_regression_estimand':'A log-linear fit describes conditional log SPPR/geometric location, not automatically arithmetic mean SPPR.','anchored_identity':'If log10 S_g=a_model+b*T_g+e_g, anchoring gives log10 s_ig=a_model+b*T_i+e_g. Each observed group residual is retained.','smearing':'No extra smearing multiplier is applied. Multiplying anchored estimates by a fitted residual smearing factor would count the same observed group heterogeneity again. Unknown new within-group residual variation remains unidentified.','expectation':'The arithmetic sum over observed catch taxa is exact under the stipulated anchored coefficients. It is not an identified expectation over unobserved true taxon coefficients.'},
 'scenario_totals':[{k:v for k,v in s.items() if k!='regional'} for s in scenarios],
 'unit_slope_scenario':b1,'extreme_b1_groups':extreme,'top_group_influence':influence,'diagnostics':diagnostics,
}
assert summary['cohort'] == json.loads((INPUTS/'cohort.json').read_text(encoding='utf-8-sig'))
save(RESULTS/'summary.json',summary)
save(RESULTS/'regressions.json',{'definition':'Weighted least squares in log10 SPPR against effective classic TL; no independent-species inference. Between-model fits use one mean per manifest model with equal model weights. Within fits include a separate intercept per model.','fits':regressions,'per_model':per_model,'leave_one_model_out':lomo})
save(RESULTS/'scenarios.json',scenarios)
save(RESULTS/'group_transport.json',group_scenarios)
save(RESULTS/'joined_groups.json',[{k:v for k,v in g.items() if k!='rows'} for g in groups])
with (RESULTS/'taxon_group_allocations.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(pairs[0]));w.writeheader();w.writerows(pairs)
with (RESULTS/'scenario_totals.csv').open('w',encoding='utf-8',newline='') as f:
    rows=[{k:v for k,v in s.items() if k!='regional'} for s in scenarios];w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

# Static scientific figures: same quantitative definitions as the result JSON.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
colors=dict(zip(units,plt.get_cmap('tab10').colors))
fig,axs=plt.subplots(1,2,figsize=(13,5.6),layout='constrained')
for uid in units:
    rr=[r for r in fitrows if r['unit']==uid and finite(r['s']) and r['s']>0]
    axs[0].scatter([r['TL'] for r in rr],np.log10([r['s'] for r in rr]),s=22,alpha=.65,color=colors[uid],label=labels[uid],edgecolor='none')
    ff=[r for r in rr if r['C']>0];x=np.array([r['TL'] for r in ff]);y=np.log10([r['s'] for r in ff]);w=np.array([r['C'] for r in ff])
    axs[1].scatter(x-weighted_mean(x,w),y-weighted_mean(y,w),s=25,alpha=.65,color=colors[uid],edgecolor='none')
x=np.linspace(1.8,5.4,100);f=regressions['all_consumer_uniform__pooled']
axs[0].plot(x,f['log10_intercepts']['pooled']+f['slope']*x,color='#172e3a',lw=2,label=f"Pooled fit: b={f['slope']:.2f}, R^2={f['r2']:.2f}")
axs[0].plot(x,x-1,'--',color='#606060',lw=1,label='Fixed 10% chain')
f=regressions['fished_catch__within'];x=np.linspace(-1.5,1.5,100)
axs[1].plot(x,f['slope']*x,color='#172e3a',lw=2,label=f"Within-model catch-weighted b={f['slope']:.2f}, R^2={f['r2']:.2f}")
axs[0].set(xlabel='Effective model-group trophic level',ylabel='log10(saved TE SPPR)',title=f"All positive consumer groups (n={sum(finite(r['s']) and r['s']>0 for r in te)})")
axs[1].set(xlabel='TL minus the model catch-weighted mean',ylabel='log10(SPPR) minus the model mean',title=f'Catch-bearing groups centered within models (n={len(groups)})')
for ax in axs:ax.grid(alpha=.15);ax.legend(fontsize=7,frameon=False,loc='upper left')
fig.suptitle('Group-level TL associations describe the data; they do not establish taxon-level slopes',fontsize=13,fontweight='bold')
fig.savefig(RESULTS/'tl_associations.png',dpi=180,bbox_inches='tight');fig.savefig(RESULTS/'tl_associations.svg',bbox_inches='tight');plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(13,5.4),layout='constrained')
chosen=['identity_b0','unit_slope_b1','all_consumer_uniform__pooled','all_consumer_uniform__within','review_included_uniform__within','fished_catch__within','fished_ppr__within']
names=['Reconstructed group total','Unit slope b=1','Pooled, all consumers','Within model, all consumers','Within model, review-included','Within model, catch weights','PPR-weighted stress test']
ss=[next(s for s in scenarios if s['id']==name) for name in chosen]
y=np.arange(len(ss));bars=axs[0].barh(y,[s['full_tC']/1e9 for s in ss],color=['#6d828c']+['#087b80']*(len(ss)-2)+['#c5cbd0'])
bars[-1].set_hatch('///');bars[-1].set_edgecolor('#7b858a')
for i,s in enumerate(ss):axs[0].text(s['full_tC']/1e9+.05,i,f"{s['full_tC']/1e9:.2f}  (x{s['full_over_base']:.2f}; b={s['b']:.2f})",va='center',fontsize=8)
axs[0].set_yticks(y,names);axs[0].invert_yaxis();axs[0].set_xlabel('Conditional total PPR (billion tC/year)');axs[0].set_xlim(0,max(s['full_tC'] for s in ss)/1e9*1.36);axs[0].set_title('Total PPR under explicit slope assumptions')
grid=np.linspace(0,2.0,101);curves=[transport(float(b))[0] for b in grid]
axs[1].plot(grid,[t['full_over_base'] for t in curves],color='#087b80',lw=2.5,label='Full TL transport: shift x dispersion')
axs[1].plot(grid,[t['shift_over_base'] for t in curves],color='#d07b34',lw=1.8,label='Mean TL shift only')
axs[1].plot(grid,[t['centered_jensen_over_base'] for t in curves],color='#5d6eab',lw=1.5,ls='--',label='Centered dispersion only')
axs[1].axhline(1,color='#777',lw=.8);axs[1].axvline(1,color='#777',lw=.8,ls=':');axs[1].set(xlabel='Assumed within-group slope b in log10(SPPR) per TL',ylabel='Multiple of reconstructed group TE PPR',title='Sensitivity is not an uncertainty interval')
axs[1].legend(frameon=False,fontsize=8);axs[1].grid(alpha=.15)
fig.suptitle(f'2019 common catch; {len(units)} reviewed model selections; original exclusions retained',fontsize=13,fontweight='bold')
fig.savefig(RESULTS/'conditional_totals.png',dpi=180,bbox_inches='tight');fig.savefig(RESULTS/'conditional_totals.svg',bbox_inches='tight');plt.close(fig)

for name,item in HASHES.items():assert sha(ROOT/name)==item['sha256'],('Consumed source changed during analysis',name)
save(INPUTS/'source_hashes.json',HASHES)
save(EVIDENCE/'verification.json',{'timestamp_utc':datetime.now(timezone.utc).isoformat(),'all_consumed_inputs_unchanged':True,'experiment_source_checks':source_checks,'exact_join_groups':len(groups),'original_group_coefficients_and_TLs_reconcile':True,'prior_totals_reconcile':True,'direct_taxon_sums_equal_shift_times_Jensen_for_every_scenario':True,'source_write_count':0,'engine_invocations':0,'scenario_count':len(scenarios),'regression_count':len(regressions),'lomo_fits':len(lomo),'missing_positive_catch_coefficients':len(missing),'study_code_sha256':sha(Path(__file__)),'runtime':{'python':sys.version,'executable':sys.executable,'numpy':np.__version__,'matplotlib':matplotlib.__version__}})
run_stdout={'sample':summary['sample'],'baseline':summary['baseline'],'fits':{k:{j:v[j] for j in ('slope','r2','n_observations')} for k,v in regressions.items()},'scenarios':summary['scenario_totals'],'b1_regions':b1['regional'],'top_b1_groups':extreme['base_tC_largest'][:5]}
save(EVIDENCE/'run_stdout.json',run_stdout)
print(json.dumps(run_stdout,indent=2))
