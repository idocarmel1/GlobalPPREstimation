"""Compare four saved coefficient methods using fixed axes and group identities."""
from pathlib import Path
import hashlib
import json
import math
import sys
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT))
from tools.project_core.registry.discovery import region_directory,discover_models
from tools.project_core.validation.researcher_review import table_rows
from cohort import assert_cohort_current, validate_pairs

OUT=RUN/'results'; QA=RUN/'evidence'
prior=json.loads((OUT/'comparison.json').read_text(encoding='utf-8'))
panels=[('new_GE','GE SPPR','Full network; GE edge efficiencies'),
        ('EwE_TE_EE','EwE SPPR × EE','Simple paths; TE edge efficiencies'),
        ('EwE_TE_noEE','EwE SPPR without × EE','Simple paths; TE edge efficiencies'),
        ('new_TE_EEfix','TE SPPR (floor ON)','Full network; TE edge efficiencies')]
inputs={};rows=[];inventory=[];identities=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    inputs[p.relative_to(ROOT).as_posix()]=sha(p)
    return json.loads(p.read_text(encoding='utf-8'))
def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
cohort=assert_cohort_current(ROOT,RUN/'inputs/cohort.json')
inputs['Project.xlsx']=sha(ROOT/'Project.xlsx')
for relative,digest in json.loads((RUN/'inputs/source_hashes.json').read_text(encoding='utf-8')).items():
    assert sha(ROOT/relative)==digest,('Analysis source changed',relative)
    inputs[relative]=digest
for source in (OUT/'comparison.json',Path(__file__)):
    inputs[source.relative_to(ROOT).as_posix()]=sha(source)
with zipfile.ZipFile(ROOT/'Project.xlsx') as archive:
    identities=sorted((r['unit_id'],r['model_id']) for _,r in table_rows(archive,'Models & coverage','Models')[3]
                      if r.get('researcher_review_status')=='Validated by researcher')
identities=validate_pairs(identities)
assert identities==sorted((m['unit'],m['model_id']) for m in prior['models'])
for unit,mid in identities:
    source=discover_models(region_directory(ROOT,unit))[mid]
    model=read(source); manifest=read(source.parent/'results/result_manifest.json')
    assert manifest['model_id']==mid and manifest['canonical_model_sha256']==sha(source)
    constructor=manifest['effective_flags']['constructor']
    assert constructor['use_ee_floor'] is True and constructor['ee_floor']==.1
    assert constructor.get('ee_threshold',.1)==.1
    outcomes=manifest['method_coverage']['methods']
    fixed=outcomes['SPPR_1995_TE0.1']['scopes']['all']
    groups={g['group_name']:g for g in model['group'] if str(g.get('pp'))=='0'}
    snapshot=source.parent/'results/regional_snapshot.xlsx'
    inputs[snapshot.relative_to(ROOT).as_posix()]=sha(snapshot)
    assert sha(snapshot)==manifest['snapshot_sha256']
    with zipfile.ZipFile(snapshot) as archive:
        table=[r for _,r in table_rows(archive,'Selected model groups','Group SPPR')[3]
               if r.get('model_id')==mid and r.get('scope')=='all']
    saved={(r['group'],r['method']):r.get('sppr') for r in table}
    for key,title,description in panels:
        outcome=outcomes.get(key,{})
        values=outcome.get('scopes',{}).get('all',{})
        counts={'positive':0,'zero':0,'negative':0,'missing':0}
        for name,g in groups.items():
            baseline=fixed.get(name)
            assert finite(baseline) and baseline>0
            value=values.get(name)
            literal=saved.get((name,key))
            if not finite(value):
                assert literal in (None,'')
                kind='missing'
            else:
                assert literal is not None and math.isclose(value,float(literal),rel_tol=1e-12,abs_tol=1e-12)
                kind='positive' if value>0 else 'zero' if value==0 else 'negative'
            counts[kind]+=1
            rows.append({'unit':unit,'model_id':mid,'group_id':int(g['group_seq']),'group':name,
                         'method':key,'TL':1+math.log10(baseline),'s':value,'availability':kind,
                         'execution_status':outcome.get('status'),'reason':outcome.get('reason'),
                         'annual_status':outcome.get('annual_status',{}).get('all'),
                         'effective_constructor':constructor})
        inventory.append({'unit':unit,'method':key,'n_groups':len(groups),'counts':counts,
                          'execution_status':outcome.get('status'),'reason':outcome.get('reason'),
                          'annual_status':outcome.get('annual_status',{}).get('all')})

focal_path=ROOT/'regions/LME/LME_027/papers/CAN-2009/models/27_118_Northwest_Africa_(1987)/model_validation/work/2026-10-15_091756_ee_floor_comparison/outputs/comparison.json'
focal=read(focal_path)
assert focal['ee_floor']==focal['ee_threshold']==.1
anchors=[a for a in prior['LME027_anchors'] if a['case']=='ON' and a['method'] in ('GE','TE')]
assert len(anchors)==4
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
                     'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,4,figsize=(23,7),sharex=True,sharey=True)
fig.subplots_adjust(left=.05,right=.99,top=.83,bottom=.32,wspace=.09)
colors=plt.get_cmap('tab10').colors
models=prior['models']
xs=np.linspace(1.6,5.4,200)
totals={}
for ax,(key,title,description) in zip(axes,panels):
    for color,m in zip(colors,models):
        points=[r for r in rows if r['unit']==m['unit'] and r['method']==key and r['availability']=='positive']
        ax.scatter([r['TL'] for r in points],[r['s'] for r in points],s=21,alpha=.64,
                   color=color,edgecolors='none')
    ax.plot(xs,10**(xs-1),color='#333333',lw=1.3,ls='--',zorder=0)
    ax.set_yscale('log');ax.set_xlim(1.6,5.4);ax.set_ylim(.8,2e8)
    ax.set_xticks([2,3,4,5]);ax.grid(axis='y',which='major',alpha=.18)
    ax.set_title(title,fontweight='bold',fontsize=14,pad=32)
    ax.text(.5,1.035,description,transform=ax.transAxes,ha='center',fontsize=10,color='#555555')
    chosen=[x for x in rows if x['method']==key]
    counts={k:sum(x['availability']==k for x in chosen) for k in ('positive','zero','negative','missing')}
    totals[key]=counts
    ax.text(.04,.97,f"{counts['positive']} plotted / {len(chosen)} groups",transform=ax.transAxes,va='top',fontsize=9,color='#444444')
    if key in ('new_GE','new_TE_EEfix'):
        option='GE' if key=='new_GE' else 'TE'
        for seq,marker in [(13,'*'),(7,'D')]:
            a=next(a for a in anchors if a['method']==option and a['group_id']==seq)
            ax.scatter([a['TL']],[a['sppr']],marker=marker,s=145 if seq==13 else 65,
                       color='#b91823',edgecolors='white',linewidth=.7,zorder=6)
            ax.annotate(str(seq),(a['TL'],a['sppr']),xytext=(7,5),textcoords='offset points',fontsize=9,color='#a3121c')
    else:
        ax.text(.04,.035,'LME_027: no saved floor-ON EwE values',transform=ax.transAxes,fontsize=8,color='#777777')
    if counts['missing']:
        ax.text(.04,.90,'Bay of Bengal: 44 unavailable\n(saved method timeout)',transform=ax.transAxes,
                va='top',fontsize=9,color='#7c5027')
axes[0].set_ylabel('SPPR, all basal sources (shared log scale)',labelpad=9)
fig.text(.52,.245,'Trophic level (cycle-broken; detritus treated as basal)',ha='center',fontsize=12)
fig.suptitle(f'SPPR versus trophic level across {len(identities)} registered validated models',
             y=.98,fontsize=17,fontweight='bold')
legend=[Line2D([0],[0],marker='o',ls='',markerfacecolor=color,markeredgecolor='none',markersize=6,
               label=m['unit']+' '+m['label']) for color,m in zip(colors,models)]
legend += [Line2D([0],[0],color='#333333',ls='--',label='Fixed 10% chain reference'),
           Line2D([0],[0],marker='*',ls='',color='#b91823',markersize=10,label='LME_027: 13 Mesopelagic predators'),
           Line2D([0],[0],marker='D',ls='',color='#b91823',markersize=6,label='LME_027: 7 Beaked whales')]
fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.52,.09),ncol=4,frameon=False,fontsize=9.5,
           columnspacing=2.1,handletextpad=.6)
fig.text(.05,.055,'All panels use saved floor-enabled configurations (floor 0.1); identical colors, TL values, source scope and axis limits. Unfished consumers are included.',fontsize=9,color='#444444')
omissions='; '.join(label+' '+str(totals[key]['zero'])+' / '+str(totals[key]['missing'])
    for key,label in [('new_GE','GE'),('EwE_TE_EE','EwE × EE'),('EwE_TE_noEE','EwE without × EE'),('new_TE_EEfix','TE')])
fig.text(.05,.025,'Log plots omit zeros / missing values: '+omissions+'. Saved diagnostic and provisional restrictions remain.',fontsize=9,color='#444444')
fig.savefig(OUT/'sppr_methods_side_by_side.png',dpi=200,facecolor='white',bbox_inches='tight')
fig.savefig(OUT/'sppr_methods_side_by_side.svg',facecolor='white',bbox_inches='tight')
plt.close(fig)
# Check plot bounds and cohort consistency independently of graphics rendering.
expected_group_count=sum(m['stats']['TE']['n_groups'] for m in models)
assert len(rows)==expected_group_count*len(panels)
assert all(t['negative']==0 for t in totals.values())
assert all(1.6<r['TL']<5.4 and .8<r['s']<2e8 for r in rows if r['availability']=='positive')
assert all(sha(ROOT/p)==digest for p,digest in inputs.items())
save(OUT/'method_panel_data.json',{'methods':[{'key':k,'title':t,'description':d} for k,t,d in panels],
     'group_records':rows,'model_method_inventory':inventory,'panel_counts':totals,
     'focal_anchors':anchors,'focal_EwE_availability':'not computed in retained floor-ON diagnostic comparison',
     'TL_definition':prior['TL_definition'],'scope':'all basal sources','source_hashes':inputs,
     'interpretation':'Saved variants, not a new scientific run or renewed researcher approval.'})
save(QA/'method_panel_verification.json',{'same_registered_pair_cohort':True,'validated_pairs':len(identities),
     'all_manifest_coefficients_match_saved_snapshots':True,'all_sources_byte_unchanged':True,
     'all_positive_points_inside_shared_axes':True,'source_files':len(inputs),'panel_counts':totals,
     'engine_invocations':0,'workbook_writes':0,'signed_review_writes':0})
print(json.dumps({'panel_counts':totals,'source_files':len(inputs),'all_sources_unchanged':True},indent=2))
