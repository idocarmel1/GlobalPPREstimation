from pathlib import Path
import json,itertools,math,hashlib
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;MODELS=HERE.parent.parent
def dump(name,x): (HERE/name).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
c=pd.read_csv(HERE/'all_groups_comparison.csv',index_col=0)
summary=json.loads((HERE/'COMPARISON.json').read_text())
source={y:json.loads((MODELS/f'50_50{y}_Coastal_Kyoto_Inoue_({y})/model.json').read_text(encoding='utf8'))['group'] for y in [1985,2013]}
params=[];diet_equal=True
for g,h in zip(source[1985],source[2013]):
 assert g['group_seq']==h['group_seq'] and g['group_name']==h['group_name']
 diet_equal &= (g['diet_descr']==h['diet_descr'] and g['diet_imp']==h['diet_imp'])
 for k in ['biomass','pb','qb','ee','ge','export','gs','biomass_accum','emigration','immigration','detritus_import']:
  if g[k]!=h[k]:params.append({'seq':int(g['group_seq']),'name':g['group_name'],'parameter':k,'source_1985':g[k],'source_2013':h[k]})
pd.DataFrame(params).to_csv(HERE/'all_changed_source_parameters.csv',index=False)
As={};basis={};flow={}
for y in [1985,2013]:
 for name,out in [('A.csv',As),('unscaled_basal_basis.csv',basis)]:
  m=pd.read_csv(HERE/str(y)/name,index_col=0);m.columns=m.columns.astype(int);out[y]=m.sort_index().sort_index(axis=1)
 flow[y]=pd.read_csv(HERE/str(y)/'detritus_flow_decomposition.csv',index_col=0)
assert diet_equal
changed=[int(i) for i in As[1985].index if not np.allclose(As[1985].loc[i],As[2013].loc[i],rtol=1e-12,atol=1e-12)]
basal=[39,40,41];living=[i for i in As[1985].index if i not in basal]
def solve_basis(a):
 b=pd.DataFrame(0.,index=a.index,columns=basal);b.loc[basal,basal]=np.eye(3)
 b.loc[living]=np.linalg.solve(np.eye(len(living))-a.loc[living,living].to_numpy(),a.loc[living,basal].to_numpy())
 return b
for y in [1985,2013]:assert np.allclose(solve_basis(As[y]),basis[y],rtol=1e-11,atol=1e-11)
mean_catch=(c.catch_1985+c.catch_2013)/2
f85=summary['years']['1985']['detritus_factor'];f13=summary['years']['2013']['detritus_factor'];mf=(f85+f13)/2
def value(s):return float((mean_catch*(s[39]+s[41]+s[40]*mf)).sum())
values={}
for n in range(len(changed)+1):
 for subset in itertools.combinations(changed,n):
  a=As[2013].copy()
  for i in subset:a.loc[i]=As[1985].loc[i]
  values[frozenset(subset)]=value(solve_basis(a))
attrs=[]
dump('ALGEBRAIC_HYBRID_CHECKS.json',{'scope':'32 explanatory GE matrix-row combinations at symmetric mean catch and detritus factor; not balanced or adopted alternative models','values':[{'rows_taken_from_1985':sorted(k),'PPR':v} for k,v in values.items()]})
N=len(changed)
for i in changed:
 result=0.
 for subset,v in values.items():
  if i in subset:continue
  weight=math.factorial(len(subset))*math.factorial(N-len(subset)-1)/math.factorial(N)
  result+=weight*(values[subset|{i}]-v)
 attrs.append({'seq':i,'name':c.loc[i,'name'],'GE1985':c.loc[i,'GE_1985'],'GE2013':c.loc[i,'GE_2013'],'coefficient_difference_PPR_attribution':result})
det_effect=float((mean_catch*(basis[1985][40]+basis[2013][40])/2*(f85-f13)).sum())
basis_effect=values[frozenset(changed)]-values[frozenset()]
assert np.isclose(basis_effect+det_effect,summary['coefficient_effect_symmetric'])
assert np.isclose(sum(a['coefficient_difference_PPR_attribution'] for a in attrs),basis_effect)
pd.DataFrame(attrs).to_csv(HERE/'GE_parameter_counterfactual_attribution.csv',index=False)
fd=pd.DataFrame({'name':flow[1985]['name']})
for y in [1985,2013]:
 for k in ['M0','q','egestion','m_eff','c_contribution','b_contribution']:fd[f'{k}_{y}']=flow[y][k]
fd.to_csv(HERE/'detritus_flow_comparison.csv')
delta=float(c.PPR_difference_1985_minus_2013.sum());sard=float(c.loc[1,'PPR_difference_1985_minus_2013'])
stats={'canonical_diet_and_import_cells_identical':bool(diet_equal),'changed_source_parameter_counts':pd.Series([p['parameter'] for p in params]).value_counts().to_dict(),'GE_changed_A_rows':changed,'ratio_PPR_all':float(c.PPR_all_1985.sum()/c.PPR_all_2013.sum()),'ratio_catch':float(c.catch_1985.sum()/c.catch_2013.sum()),'PPR_gap':delta,'sardine_share_of_gap_pct':sard/delta*100,'catch_effect_share_pct':summary['catch_effect_symmetric']/delta*100,'coefficient_effect_share_pct':summary['coefficient_effect_symmetric']/delta*100,'weighted_mean_SPPR_1985':float(c.PPR_all_1985.sum()/c.catch_1985.sum()),'weighted_mean_SPPR_2013':float(c.PPR_all_2013.sum()/c.catch_2013.sum()),'living_GE_basis_effect':basis_effect,'detritus_multiplier_effect':det_effect,'living_GE_parameter_attribution':attrs,'algebra_validation':'Both matrix-solve basal bases match direct diagnose_sppr outputs within 1e-11; all contribution decompositions sum to original GE gap. These hybrid matrices are explanatory algebra, not model candidates; no loader or source balancing performed for them.'}
dump('DECOMPOSITION.json',stats)
print(json.dumps(stats,indent=2));print(c.sort_values('coefficient_effect_symmetric',ascending=False)[['name','coefficient_effect_symmetric']].head(10).to_string());print(fd.sort_values('c_contribution_1985',ascending=False).head(10).to_string())
print('LOWEST COEFFICIENT RATIOS');print(c.sort_values('SPPR_ratio_1985_to_2013')[['name','SPPR_all_1985','SPPR_all_2013','SPPR_ratio_1985_to_2013']].head(8).to_string())
