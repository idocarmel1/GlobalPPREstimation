"""Verify saved GE outputs, without invoking the calculator or modifying source models."""
from pathlib import Path
import json,hashlib
import pandas as pd
import numpy as np
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
c=pd.read_csv(P/'all_groups_comparison.csv',index_col=0)
full=pd.DataFrame({'name':c['name']});stats={};routes=[];reports={};inputs={}
for y in [1985,2013]:
 s=pd.read_csv(P/str(y)/'SPPR.csv',index_col=0).sort_index();s.columns=s.columns.astype(int)
 a=pd.read_csv(P/str(y)/'A.csv',index_col=0).sort_index();a.columns=a.columns.astype(int)
 g=pd.read_csv(P/str(y)/'groups.csv',index_col=0).sort_index()
 r=json.loads((P/str(y)/'direct_diagnose_sppr_GE.json').read_text())['direct_diagnose_sppr_return'];reports[y]=r
 expected=c[f'SPPR_all_{y}'];assert np.allclose(s.sum(axis=1),expected,rtol=1e-14,atol=1e-14)
 original=P.parent.parent/f'50_50{y}_Coastal_Kyoto_Inoue_({y})'
 assert r==json.loads((original/'evidence/diagnose_sppr_GE.json').read_text())['direct_diagnose_sppr_return']
 assert pd.read_csv(P/str(y)/'groups.csv').equals(pd.read_csv(original/'evidence/loaded_groups.csv'))
 assert sha(original/'model.json')==json.loads((P/str(y)/'provenance.json').read_text())['source_sha256']
 for col,label in [(39,'PP'),(40,'DET'),(41,'Import')]:full[f'{label}_{y}']=s[col]
 full[f'all_{y}']=s.sum(axis=1);full[f'unfished_{y}']=g['catch'].eq(0);full[f'GE_{y}']=g.p/g.q
 consumers=g.index[g.trophic_info=='Regular'];allv=s.sum(axis=1).loc[consumers];pp=s.loc[consumers,39]
 def desc(v):return {'minimum':float(v.min()),'median':float(v.median()),'mean':float(v.mean()),'maximum':float(v.max()),'maximum_group':g.loc[v.idxmax(),'group_name']}
 stats[str(y)]={'groups_total':len(g),'consumers':len(consumers),'unfished_consumers':int(g.loc[consumers,'catch'].eq(0).sum()),'negative_total_coefficients':int(s.sum(axis=1).lt(0).sum()),'negative_source_cells':int(s.lt(0).sum().sum()),'nonfinite_source_cells':int((~np.isfinite(s)).sum().sum()),'all_source_consumer_stats':desc(allv),'pp_only_consumer_stats':desc(pp),'minimum_consumer_GE':float((g.p/g.q).loc[consumers].min()),'maximum_absolute_linear_equation_residual':float(np.abs((a@s).loc[consumers]-s.loc[consumers]).to_numpy().max())}
 assert stats[str(y)]['maximum_absolute_linear_equation_residual']<1e-11
 for pred in [4,5,8,9,11,31]:
  for prey,weight in a.loc[pred].items():
   if weight:
    routes.append({'year':y,'predator_seq':pred,'predator_name':g.loc[pred,'group_name'],'prey_seq':int(prey),'prey_name':g.loc[prey,'group_name'],'normalized_diet':float(weight*g.loc[pred,'ge']),'GE_inverse':float(1/g.loc[pred,'ge']),'prey_SPPR':float(s.loc[prey].sum()),'SPPR_contribution':float(weight*s.loc[prey].sum())})
 for name in ['SPPR.csv','A.csv','groups.csv','direct_diagnose_sppr_GE.json']:inputs[f'{y}/{name}']=sha(P/str(y)/name)
full['all_change_pct']=(full.all_2013/full.all_1985-1)*100
full['PP_change_pct']=np.where(full.PP_1985!=0,(full.PP_2013/full.PP_1985-1)*100,np.nan)
full.to_csv(P/'GE_GROUP_RELIABILITY_FULL.csv',index_label='source_group_seq')
routes=pd.DataFrame(routes);routes.to_csv(P/'GE_HIGH_GROUP_PREY_CONTRIBUTIONS.csv',index=False)
stats['direction_counts_38_consumers']={'all_lower_2013':int(full.loc[1:38,'all_change_pct'].lt(0).sum()),'all_higher_2013':int(full.loc[1:38,'all_change_pct'].gt(0).sum()),'PP_lower_2013':int((full.loc[1:38,'PP_2013']<full.loc[1:38,'PP_1985']).sum()),'PP_higher_2013':int((full.loc[1:38,'PP_2013']>full.loc[1:38,'PP_1985']).sum()),'PP_equal':int((full.loc[1:38,'PP_2013']==full.loc[1:38,'PP_1985']).sum())}
dump(P/'GE_RELIABILITY_VERIFICATION.json',{'status':'PASS','method':'saved-output verification only; no calculator reruns or model changes','stats':stats,'input_sha256':inputs,'canonical_hashes_unchanged':True,'original_direct_returns_equal':True,'original_loaded_groups_equal':True})
print(json.dumps(stats,indent=2))
print('FOCUS GROUPS');print(full.loc[[4,5,8,9,11,31]].to_string())
print('STINGRAY PREY ROUTES');print(routes[routes.predator_seq.eq(11)].sort_values(['year','SPPR_contribution'],ascending=[True,False]).to_string(index=False))
