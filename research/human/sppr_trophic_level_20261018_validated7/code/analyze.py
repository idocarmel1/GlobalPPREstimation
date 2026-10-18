"""Read saved model-local coefficients only; never construct/run a calculator."""
from pathlib import Path
import hashlib
import json
import math
import sys
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT))
from tools.project_core.registry.discovery import region_directory,discover_models
from tools.project_core.validation.researcher_review import table_rows
from cohort import capture_cohort, validate_pairs

OUT=RUN/'results'; QA=RUN/'evidence'
OUT.mkdir(parents=True,exist_ok=True);QA.mkdir(exist_ok=True);(RUN/'inputs').mkdir(exist_ok=True)
inputs={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    inputs[p.relative_to(ROOT).as_posix()]=sha(p)
    return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def finite(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)

cohort=capture_cohort(ROOT,RUN/'inputs/cohort.json')
inputs['Project.xlsx']=cohort['project_sha256']
inputs[(RUN/'inputs/cohort.json').relative_to(ROOT).as_posix()]=sha(RUN/'inputs/cohort.json')
for review in cohort['pairs']+cohort['excluded_pairs']:
    inputs[review['validation_report_path']]=sha(ROOT/review['validation_report_path'])
for source in (Path(__file__),RUN/'code/cohort.py'):
    inputs[source.relative_to(ROOT).as_posix()]=sha(source)
with zipfile.ZipFile(ROOT/'Project.xlsx') as z:
    meta=[r for _,r in table_rows(z,'Models & coverage','Models')[3]
          if r.get('researcher_review_status')=='Validated by researcher']
identities=[(r['unit_id'],r['model_id']) for r in meta]
identities=validate_pairs(identities)
records=[]; summaries=[]; exclusions=[]
labels={'HS_077':'Eastern tropical Pacific','LME_013':'Northern Humboldt',
        'LME_032':'Arabian Sea','LME_034':'Bay of Bengal',
        'LME_035':'Gulf of Thailand','LME_036':'South China Sea','LME_047':'East China Sea'}
methods={'new_GE':'GE','new_TE_EEfix':'TE','new_WithEgestion':'With Egestion'}
for unit,mid in sorted(identities):
    model=discover_models(region_directory(ROOT,unit))[mid]
    source=read(model); folder=model.parent; manifest=read(folder/'results/result_manifest.json')
    assert manifest['model_id']==mid and manifest['canonical_model_sha256']==sha(model)
    snapshot=folder/'results/regional_snapshot.xlsx'
    inputs[snapshot.relative_to(ROOT).as_posix()]=sha(snapshot)
    assert inputs[snapshot.relative_to(ROOT).as_posix()]==manifest['snapshot_sha256']
    outcomes=manifest['method_coverage']['methods']
    fixed=outcomes['SPPR_1995_TE0.1']['scopes']['all']
    groups={g['group_name']:g for g in source['group'] if str(g.get('pp'))=='0'}
    assert len(groups)==len([g for g in source['group'] if str(g.get('pp'))=='0'])
    for key,option in methods.items():
        outcome=outcomes[key]; values=outcome['scopes']['all']
        diag=outcome.get('retained_diagnostics_flat',{})
        # Fresh method results retain their report under diagnostic fields;
        # use the manifest diagnostic summary where available.
        if not diag:
            raw_diag=outcome.get('diagnostics',{})
            diag={'status':raw_diag.get('status'),
                  'divergence_rho_living':raw_diag.get('divergence',{}).get('rho_living')}
        for name,g in groups.items():
            baseline=fixed.get(name); value=values.get(name)
            if not finite(baseline) or baseline<=0:
                exclusions.append({'unit':unit,'group':name,'method':option,'reason':'missing positive fixed-10% coefficient/TL'})
                continue
            tl=1+math.log10(baseline)
            records.append({'unit':unit,'model_id':mid,'group_id':int(g['group_seq']),
                'group':name,'method':option,'scope':'all','TL':tl,'TL_source':'inverted saved SPPR_1995_TE0.1 = 10^(TL-1)',
                's':value,'fixed10_s':baseline,'s_over_fixed10':value/baseline if finite(value) else None,
                'source_pp':g['pp'],'source_EE':g.get('ee'),'source_GE':g.get('ge'),
                'diagnostic_status':diag.get('status'),'rho_living':diag.get('divergence_rho_living'),
                'annual_status':outcome.get('annual_status',{}).get('all'),
                'coefficient_source':(folder/'results/result_manifest.json').relative_to(ROOT).as_posix(),
                'effective_constructor':manifest['effective_flags']['constructor']})
    model_rows=[x for x in records if x['unit']==unit]
    stats={}
    for option in methods.values():
        rows=[x for x in model_rows if x['method']==option]
        positive=[x for x in rows if finite(x['s']) and x['s']>0]
        near4=[x for x in positive if 3.5<=x['TL']<4.5]
        stats[option]={'n_groups':len(rows),'n_positive':len(positive),'n_zero':sum(x['s']==0 for x in rows),
            'n_negative':sum(finite(x['s']) and x['s']<0 for x in rows),
            'n_missing':sum(not finite(x['s']) for x in rows),
            'near_TL4_n':len(near4),'near_TL4_median':float(np.median([x['s'] for x in near4])) if near4 else None,
            'maximum':max((x['s'] for x in positive),default=None),
            'spearman_TL_log_s':float(spearmanr([x['TL'] for x in positive],[math.log10(x['s']) for x in positive]).statistic),
            'status':rows[0]['diagnostic_status'],'rho_living':rows[0]['rho_living'],
            'annual_status':rows[0]['annual_status']}
    summaries.append({'unit':unit,'label':labels[unit],'model_id':mid,'stats':stats})
    # Reconcile manifest coefficients with their saved workbook, without reading
    # unrelated annual catch/PPR tables or changing either source.
    with zipfile.ZipFile(snapshot) as z:
        saved=[r for _,r in table_rows(z,'Selected model groups','Group SPPR')[3]
               if r.get('model_id')==mid and r.get('scope')=='all']
    saved={(r['group'],r['method']):r.get('sppr') for r in saved}
    for row in model_rows:
        key=next(k for k,v in methods.items() if v==row['method'])
        literal=saved[(row['group'],key)]
        if row['s'] is None:
            assert literal in (None,'')
        else:
            assert math.isclose(row['s'],float(literal),rel_tol=1e-12,abs_tol=1e-12)
        assert math.isclose(row['fixed10_s'],float(saved[(row['group'],'SPPR_1995_TE0.1')]),rel_tol=1e-12,abs_tol=1e-12)

comparison=ROOT/'regions/LME/LME_027/papers/CAN-2009/models/27_118_Northwest_Africa_(1987)/model_validation/work/2026-10-15_091756_ee_floor_comparison'
focal=read(comparison/'outputs/comparison.json')
coeff=read(comparison/'outputs/group_scope_coefficients.json')
anchors=[]
for seq,tl in [(13,focal['cases']['OFF']['TE']['divergence']['max_sppr_group']['tl']),
               (7,focal['cases']['ON']['TE']['divergence']['max_sppr_group']['tl'])]:
    for case in ('OFF','ON'):
        for option in methods.values():
            row=next(x for x in coeff if x['case']==case and x['method']==option and x['scope']=='all' and x['group_id']==seq)
            anchors.append({**row,'TL':tl,'fixed10_s':10**(tl-1),'s_over_fixed10':row['sppr']/10**(tl-1)})
a=read(comparison/'outputs/ON/TE_matrices.json')['A']
self_gain=a['data'][a['index'].index(13)][a['columns'].index(13)]
on13=next(x for x in anchors if x['group_id']==13 and x['case']=='ON' and x['method']=='TE')
decomposition={'group13_self_gain':self_gain,'feedback_amplification':1/(1-self_gain),
    'ON_group13_s':on13['sppr'],'ON_other_prey_contribution_u13':on13['sppr']*(1-self_gain),
    'interpretation':'Algebraic decomposition using saved prey coefficients, not a diet modification or new model scenario.'}
bins=[]
for lo,hi in [(2,3),(3,4),(4,5)]:
    rows=[x for x in records if x['method']=='TE' and finite(x['s']) and x['s']>0 and lo<=x['TL']<hi]
    vals=[x['s'] for x in rows]
    bins.append({'TL_interval':[lo,hi],'n':len(rows),'median':float(np.median(vals)),
                 'p10':float(np.quantile(vals,.1)),'p90':float(np.quantile(vals,.9))})
save(OUT/'group_records.json',records)
save(OUT/'comparison.json',{'scope':'all basal sources; unfished groups included; no catch weighting',
    'population':f'{len(identities)} registered researcher-validated model-region pairs as of 18 October 2026, not a universal ecological reference range.',
    'cohort_manifest':'../inputs/cohort.json',
    'TL_definition':'TL reconstructed from saved fixed-0.1 chain coefficient, matching the engine cycle-broken, detritus-as-basal TL.',
    'methods':methods,'models':summaries,'LME027_anchors':anchors,'decomposition':decomposition,
    'TE_TL_bins':bins,'excluded_TL_rows':exclusions,
    'restrictions':'All saved diagnostic/annual restrictions retained; registration does not approve transformed calculations. Positive finite values are described, not promoted to scientific eligibility.'})

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(10.8,6.7),layout='constrained')
colors=plt.get_cmap('tab10').colors
for k,item in enumerate(summaries):
    rows=[x for x in records if x['unit']==item['unit'] and x['method']=='TE' and finite(x['s']) and x['s']>0]
    ax.scatter([x['TL'] for x in rows],[x['s'] for x in rows],s=21,color=colors[k],alpha=.63,
               label=item['unit']+' '+item['label'],edgecolors='none')
xs=np.linspace(1,5.4,200)
ax.plot(xs,10**(xs-1),color='#333333',ls='--',lw=1.5,label='Fixed 10% chain: 10^(TL - 1)')
for seq,offset,label in [(13,(-140,17),'LME_027 Mesopelagic predators'),(7,(-175,-31),'LME_027 Beaked whales')]:
    row=next(x for x in anchors if x['group_id']==seq and x['case']=='ON' and x['method']=='TE')
    ax.scatter([row['TL']],[row['sppr']],s=180,marker='*',color='#b91823',edgecolor='white',linewidth=.7,zorder=6)
    ax.annotate(label,(row['TL'],row['sppr']),xytext=offset,textcoords='offset points',fontsize=9,
                color='#9f101c',arrowprops={'arrowstyle':'-','color':'#9f101c','lw':.7})
ax.set_yscale('log');ax.set_xlim(1.6,5.4);ax.set_ylim(.8,2e8)
ax.set_xlabel('Trophic level (cycle-broken, detritus treated as basal)')
ax.set_ylabel('Saved TE SPPR, all basal sources (log scale)')
ax.set_title('Trophic level explains the broad increase; feedback can produce large departures',loc='left',fontweight='bold',pad=16)
ax.grid(axis='y',which='major',alpha=.17)
ax.legend(loc='upper left',fontsize=8,frameon=False,ncol=2)
te_rows=[r for r in records if r['method']=='TE']
positive_count=sum(finite(r['s']) and r['s']>0 for r in te_rows)
zero_count=sum(r['s']==0 for r in te_rows)
missing_count=sum(not finite(r['s']) for r in te_rows)
fig.text(.01,-.025,f'{len(te_rows)} consumer groups in {len(identities)} registered models; {positive_count} positive TE values plotted. Zeros: {zero_count}; unavailable: {missing_count}.\nSaved floor-enabled configurations; WARN/FAIL and annual restrictions remain. Red stars: LME_027 floor ON, threshold = floor = 0.1.',fontsize=8,color='#444444')
fig.savefig(OUT/'sppr_vs_tl.png',dpi=180,bbox_inches='tight',facecolor='white')
plt.close(fig)
assert all(sha(ROOT/p)==digest for p,digest in inputs.items())
save(RUN/'inputs/source_hashes.json',inputs)
save(QA/'verification.json',{'all_source_bytes_unchanged':True,'validated_pairs':len(identities),
    'unique_consumer_groups':len({(x['unit'],x['group_id']) for x in records}),
    'records':len(records),'excluded_TL_records':len(exclusions),
    'saved_only':True,'engine_invocations':0,'canonical_or_workbook_writes':0,
    'all_manifest_coefficients_reconcile_with_saved_snapshots':True})
print(json.dumps({'models':[{'unit':m['unit'],'n_TL4':m['stats']['TE']['near_TL4_n'],
    'median_TE_TL4':m['stats']['TE']['near_TL4_median'],'rho_TE':m['stats']['TE']['rho_living'],
    'status_TE':m['stats']['TE']['status'],'rho_spearman_TE':m['stats']['TE']['spearman_TL_log_s']} for m in summaries],
    'decomposition':decomposition,'TE_TL_bins':bins},indent=2))
