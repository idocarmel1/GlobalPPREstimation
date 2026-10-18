"""Render the GE and floor-ON TE subset of the verified four-panel data."""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').is_file())
OUT=RUN/'results'
data=json.loads((OUT/'method_panel_data.json').read_text(encoding='utf-8'))
prior=json.loads((OUT/'comparison.json').read_text(encoding='utf-8'))
for relative,digest in data['source_hashes'].items():
    assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest
panels=[('new_GE','GE SPPR','GE edge efficiencies'),
        ('new_TE_EEfix','TE SPPR (floor ON)','TE = GE × effective EE')]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
    'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(13,8.2),sharex=True,sharey=True)
fig.subplots_adjust(left=.075,right=.985,top=.84,bottom=.32,wspace=.09)
colors=plt.get_cmap('tab10').colors
for ax,(key,title,subtitle) in zip(axes,panels):
    for color,model in zip(colors,prior['models']):
        rows=[r for r in data['group_records'] if r['method']==key and r['unit']==model['unit'] and r['availability']=='positive']
        ax.scatter([r['TL'] for r in rows],[r['s'] for r in rows],s=25,alpha=.65,
            color=color,edgecolors='none')
    x=np.linspace(1.6,5.4,200)
    ax.plot(x,10**(x-1),ls='--',color='#333333',lw=1.4,zorder=0)
    ax.set_yscale('log');ax.set_xlim(1.6,5.4);ax.set_ylim(.8,2e8)
    ax.set_xticks([2,3,4,5]);ax.grid(axis='y',which='major',alpha=.18)
    ax.set_title(title,fontweight='bold',fontsize=15,pad=29)
    ax.text(.5,1.025,subtitle,transform=ax.transAxes,ha='center',fontsize=10,color='#555555')
    count=data['panel_counts'][key]['positive']
    ax.text(.04,.97,f"{count} plotted / {sum(data['panel_counts'][key].values())} groups",transform=ax.transAxes,va='top',fontsize=9,color='#555555')
    method='GE' if key=='new_GE' else 'TE'
    for seq,marker in [(13,'*'),(7,'D')]:
        row=next(a for a in data['focal_anchors'] if a['method']==method and a['group_id']==seq)
        ax.scatter([row['TL']],[row['sppr']],marker=marker,s=165 if seq==13 else 75,
            color='#b91823',edgecolors='white',linewidth=.7,zorder=6)
        ax.annotate(str(seq),(row['TL'],row['sppr']),xytext=(8,5),textcoords='offset points',color='#a3121c',fontsize=10)
axes[0].set_ylabel('SPPR, all basal sources (shared log scale)',labelpad=10)
fig.text(.53,.255,'Trophic level (cycle-broken; detritus treated as basal)',ha='center',fontsize=11)
fig.suptitle('GE and TE SPPR versus trophic level',y=.97,fontsize=18,fontweight='bold')
handles=[Line2D([0],[0],marker='o',ls='',markerfacecolor=color,markeredgecolor='none',markersize=6,
    label=m['unit']+' '+m['label']) for color,m in zip(colors,prior['models'])]
handles += [Line2D([0],[0],ls='--',color='#333333',label='Fixed 10% chain reference'),
    Line2D([0],[0],marker='*',ls='',color='#b91823',markersize=10,label='LME_027: 13 Mesopelagic predators'),
    Line2D([0],[0],marker='D',ls='',color='#b91823',markersize=6,label='LME_027: 7 Beaked whales')]
fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.53,.085),ncol=3,
    frameon=False,fontsize=9,columnspacing=1.5,handletextpad=.6)
fig.text(.075,.047,f"Same {len(prior['models'])} registered validated models, saved floor-enabled configurations and axis limits. Red overlays: LME_027.",fontsize=8.7,color='#444444')
fig.text(.075,.024,f"GE: {data['panel_counts']['new_GE']['positive']} positive; TE: {data['panel_counts']['new_TE_EEfix']['positive']} positive, {data['panel_counts']['new_TE_EEfix']['zero']} zero. Existing diagnostic restrictions remain.",fontsize=8.7,color='#444444')
for extension in ('png','svg'):
    fig.savefig(OUT/('sppr_ge_te_side_by_side.'+extension),dpi=200,bbox_inches='tight',facecolor='white')
plt.close(fig)
print('Saved GE/TE comparison; source hashes verified; no new scientific runs.')
