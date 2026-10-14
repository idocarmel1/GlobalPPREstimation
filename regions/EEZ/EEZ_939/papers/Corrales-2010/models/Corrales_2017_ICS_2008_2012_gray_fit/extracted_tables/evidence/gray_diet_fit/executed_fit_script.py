"""Bounded reconstruction of censored diets; published cells remain fixed.

LP variables are a consumer normalization factor t and normalized gray fractions y.
Raw gray fractions are y/t, in [0,0.01). Printed cells become printed*t only
on the runtime-normalized copy. Exact mass balance is tested before minimax fitting.
"""
from pathlib import Path
import json,csv,sys,hashlib,datetime
import numpy as np
import pandas as pd
from scipy.optimize import linprog

ROOT=Path(__file__).resolve().parents[6];WORK=Path(__file__).resolve().parents[1]
BASE=ROOT/'regions/EEZ/EEZ_939/papers/Corrales-2010/models'
UPPER=.01-1e-10
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def table(x):
 g=pd.DataFrame(x['data'],index=x['index'],columns=x['columns'])
 return g.map(lambda v:float('nan') if isinstance(v,dict) else v)
def fit(period,derive_f=False):
 source=BASE/f'Corrales_2017_ICS_{period}_derived_fate'
 canonical=json.loads((source/'model.json').read_text(encoding='utf-8'))
 st=json.loads((source/'results/diagnostics/runtime_state.json').read_text(encoding='utf-8'))
 groups=table(st['groups']);raw=table(json.loads((source/'results/diagnostics/loaded_before.json').read_text(encoding='utf-8'))['diet'])
 gray=[]
 with (source/'extracted_tables/companions/Source_diet_cells.csv').open(encoding='utf-8',newline='') as f:
  for r in csv.DictReader(f):
   if r['status']=='censored_less_than_0.01':gray.append((int(r['consumer_seq']),int(r['prey_seq']),r))
 consumers=list(groups.index[groups.trophic_info.eq('Regular')]);targets=list(groups.index[groups.trophic_info.isin(['Regular','PP'])])
 tloc={k:i for i,k in enumerate(consumers)};N=len(consumers)+len(gray)
 sums=raw.sum(axis=1);bounds=[];equal=[];rhs=[];ineq=[];irhs=[]
 for k in consumers:
  n=sum(a==k for a,b,r in gray);s=float(sums[k]);bounds.append((1/(s+n*UPPER),1/s))
  row=np.zeros(N);row[tloc[k]]=s
  for z,(a,b,r) in enumerate(gray):
   if a==k:row[len(consumers)+z]=1
  equal.append(row);rhs.append(1.)
 for z,(a,b,r) in enumerate(gray):
  bounds.append((0,None));row=np.zeros(N);row[len(consumers)+z]=1;row[tloc[a]]=-UPPER;ineq.append(row);irhs.append(0.)
 eq=np.array(equal);ub=np.array(ineq);predmat=np.zeros((len(targets),N))
 for j,k in enumerate(targets):
  for a in consumers:predmat[j,tloc[a]]=float(groups.loc[a,'q'])*float(raw.loc[a,k])
  for z,(a,b,r) in enumerate(gray):
   if b==k:predmat[j,len(consumers)+z]=float(groups.loc[a,'q'])
 basepred=raw.div(sums,axis=0).fillna(0).mul(groups.q,axis=0);basepred.loc[~groups.trophic_info.eq('Regular')]=0;baseline=basepred.sum(axis=0)
 knowncatch={int(g['group_seq']):sum(float(g[key]) for key in ['landings_total','discards_total'] if g[key]!='-9999') for g in canonical['group']}
 with (source/'extracted_tables/companions/Article_group_outputs.csv').open(encoding='utf-8',newline='') as f:reported_outputs={int(r['import_seq']):r for r in csv.DictReader(f)}
 fcatch={};catchledger=[]
 for g in canonical['group']:
  k=int(g['group_seq']);F=reported_outputs[k]['F_per_year'];B=g['biomass'];known=knowncatch[k]
  derived=float(F)*float(B) if F and B!='-9999' else None
  if g['total_removals']!='-9999':value=float(g['total_removals']);status='known total preserved'
  elif derived is None:value=known;status='not derived; retain known subtotal, unknown components default to zero only in experiment'
  elif derived+1e-12<known:value=known;status='F*B conflicts with known subtotal; retain known subtotal, reject smaller reconstruction'
  else:value=derived;status='missing total reconstructed as published F*B'
  fcatch[k]=value;catchledger.append({'group_seq':k,'group_name':g['group_name'],'published_F_per_year':F,'published_B_t_per_km2':B,'published_known_catch_subtotal':known,'F_times_B_t_per_km2_year':derived,'experimental_removals_t_per_km2_year':value,'status':status})
 outputroot=WORK/'outputs'/f'{"removals_fit" if derive_f else "gray_fit"}_{period}'
 results={};ledgers={}
 for scenario in (['derived_F_removals'] if derive_f else ['unchanged_runtime_catch','known_catch_components_counterfactual']):
  catch=groups['catch'].copy()
  if scenario.startswith('known'):catch.update(pd.Series(knowncatch))
  if scenario=='derived_F_removals':catch.update(pd.Series(fcatch))
  target=(groups.p-catch-groups.biomass_accum-groups.net_migration+groups.detritus_import-groups.M0).loc[targets].to_numpy(dtype=float)
  scale=np.maximum(groups.p.loc[targets].to_numpy(dtype=float),1e-12)
  # Row scaling avoids large plankton flows dominating numerical feasibility.
  exact=linprog(np.zeros(N),A_ub=ub,b_ub=irhs,A_eq=np.vstack([eq,predmat/scale[:,None]]),b_eq=np.r_[rhs,target/scale],bounds=bounds,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
  # Certify the smallest possible maximum relative production residual.
  eq2=np.c_[eq,np.zeros(len(eq))];ub2=np.c_[ub,np.zeros(len(ub))]
  constraints=np.vstack([ub2,np.c_[predmat/scale[:,None],-np.ones(len(targets))],np.c_[-predmat/scale[:,None],-np.ones(len(targets))]])
  crhs=np.r_[irhs,target/scale,-target/scale];obj=np.r_[np.zeros(N),1.]
  best=linprog(obj,A_ub=constraints,b_ub=crhs,A_eq=eq2,b_eq=rhs,bounds=bounds+[(0,None)],method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
  assert best.success,best.message
  # Second-stage least total absolute scaled residual at the certified minimax optimum.
  lim=float(best.fun)+1e-9;K=len(targets)
  absconstraints=np.vstack([np.c_[ub,np.zeros((len(ub),K))],np.c_[predmat/scale[:,None],-np.eye(K)],np.c_[-predmat/scale[:,None],-np.eye(K)]])
  abseq=np.c_[eq,np.zeros((len(eq),K))]
  polished=linprog(np.r_[np.zeros(N),np.ones(K)],A_ub=absconstraints,b_ub=crhs,A_eq=abseq,b_eq=rhs,bounds=bounds+[(0,lim)]*K,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
  assert polished.success,polished.message
  solution=polished.x[:N];fitted=raw.copy();ledger=[]
  for z,(a,b,r) in enumerate(gray):
   v=max(0.,min(UPPER,float(solution[len(consumers)+z]/solution[tloc[a]])))
   fitted.loc[a,b]=v;ledger.append({**r,'fitted_raw_fraction':v,'fitted_normalized_fraction':v*float(solution[tloc[a]]),'status_after':'researcher_authorized_bounded_fit; not published'})
  fitted_norm=fitted.div(fitted.sum(axis=1),axis=0).fillna(0)
  pred=fitted_norm.mul(groups.q,axis=0);pred.loc[~groups.trophic_info.eq('Regular')]=0;pred=pred.sum(axis=0)
  issues=[];ranges=[]
  for j,k in enumerate(targets):
   r=float(pred[k]-target[j]);old=float(baseline[k]-target[j]);nm=groups.loc[k,'group_name']
   minimum=linprog(predmat[j],A_ub=ub,b_ub=irhs,A_eq=eq,b_eq=rhs,bounds=bounds,method='highs')
   maximum=linprog(-predmat[j],A_ub=ub,b_ub=irhs,A_eq=eq,b_eq=rhs,bounds=bounds,method='highs')
   low=float(minimum.fun);high=float(-maximum.fun)
   issue={'group_seq':int(k),'group_name':nm,'p':float(groups.p[k]),'q':float(groups.q[k]),'catch_used':float(catch[k]),'required_predation':float(target[j]),'baseline_predation':float(baseline[k]),'fitted_predation':float(pred[k]),'baseline_p_residual':old,'fitted_p_residual':r,'baseline_p_relative_residual':old/scale[j],'fitted_p_relative_residual':r/scale[j],'individually_min_predation':low,'individually_max_predation':high,'gray_incoming_count':sum(b==k for a,b,r in gray),'can_balance_individually':bool(low-1e-8<=target[j]<=high+1e-8)}
   issues.append(issue)
  results[scenario]={'exact_feasible':bool(exact.success),'exact_status':int(exact.status),'exact_message':exact.message,'minimax_relative_residual_lower_bound':float(best.fun),'fitted_max_relative_residual':max(abs(r['fitted_p_relative_residual']) for r in issues),'strict_mass_balance':bool(all(np.isclose(r['fitted_predation'],r['required_predation'],rtol=1e-5,atol=1e-8) for r in issues)),'gray_cell_count':len(gray),'positive_gray_values':sum(r['fitted_raw_fraction']>1e-12 for r in ledger),'gray_value_bounds':[0,UPPER],'largest_issues':sorted(issues,key=lambda r:abs(r['fitted_p_relative_residual']),reverse=True)[:12]}
  output=outputroot/scenario;output.mkdir(parents=True,exist_ok=True)
  pd.DataFrame(issues).to_csv(output/'mass_balance_by_group.csv',index=False);pd.DataFrame(ledger).to_csv(output/'fitted_gray_cells.csv',index=False);fitted.to_csv(output/'diet_raw_fitted.csv');fitted_norm.to_csv(output/'diet_runtime_normalized.csv')
  ledgers[scenario]=ledger
 record={'schema_version':1,'period':period,'parent_model_id':source.name,'parent_model_sha256':hashlib.sha256((source/'model.json').read_bytes()).hexdigest(),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Constrained LP feasibility and minimax, followed by minimum total absolute scaled residual at minimax optimum','published_numeric_diet_cells':'held fixed before runtime normalization','ordinary_blank_diet_cells':'zero on runtime copy only; source unknown marker preserved','gray_cell_constraint':'0 <= raw fraction < 0.01; no biological parameter changes','other_defaults':'Exact previously audited runtime B/PB/QB/EE/BA/GS/fate retained','catch_counterfactual':'Separately tests retention of known catch components, treating missing components as zero only on the counterfactual runtime copy. Not adopted.','raw_unit_sum_feasible_with_fixed_printed_cells':bool(all(sums[k]<=1+1e-10 and sums[k]+UPPER*sum(a==k for a,b,r in gray)>=1-1e-10 for k in consumers)),'results':results}
 if derive_f:record['catch_reconstruction']='Missing totals from published F*B where not lower than known components; known totals unchanged; contradictions retained and smaller F*B rejected.'
 dump(outputroot/'fit_summary.json',record)
 if derive_f:pd.DataFrame(catchledger).to_csv(outputroot/'catch_reconstruction.csv',index=False)
 # Retain the actual attempted gray-only candidate, even if scientifically unsuccessful.
 new_id=f'Corrales_2017_ICS_{period}_gray_fit'+('_F_removals' if derive_f else '');dest=BASE/new_id
 import shutil
 if dest.exists():raise RuntimeError('Refusing overwrite of an existing variant')
 shutil.copytree(source,dest,ignore=shutil.ignore_patterns('results','model_validation'))
 c=canonical;c['metadata']['variant']='researcher_authorized_gray_diet_fit';c['metadata']['parent_model_id']=source.name
 c['metadata']['model_number']=str(c['metadata'].get('model_number','ICS_'+period))+'_gray_fit'
 c['metadata']['reconstruction_status']='Attempted bounded reconstruction; NOT mass-balanced; non-diet biological source parameters unchanged'
 chosen='derived_F_removals' if derive_f else 'unchanged_runtime_catch'
 bycell={(int(r['consumer_seq']),int(r['prey_seq'])):r for r in ledgers[chosen]}
 for g in c['group']:
  a=int(g['group_seq'])
  if derive_f and g['total_removals']=='-9999':
   g['export']=format(fcatch[a],'.17g');g['experimental_total_removals']=g['export'];g['experimental_removals_status']=catchledger[a-1]['status'];g['export_scope']='Researcher-authorized F*B reconstruction or known-subtotal counterfactual; source fleet components retained unchanged'
  for entry in (g.get('diet_descr') or {}).get('diet',[]):
   key=(a,int(entry['prey_seq']))
   if key in bycell:entry['proportion']=format(bycell[key]['fitted_raw_fraction'],'.17g')
 # Original source-fidelity report is inherited as parent evidence, not claimed for changed diet.
 c['source_fidelity']['variant_note']='Parent source-fidelity evidence concerns original extraction. Fitted gray cells intentionally depart from missing source markers; fitted-cell ledger authenticates changes.'
 dump(dest/'model.json',c)
 ev=dest/'extracted_tables/evidence/gray_diet_fit';shutil.copytree(outputroot,ev)
 # Update EwE import on the derived copy only. Preserve axes and all non-gray cells.
 path=dest/'extracted_tables/Diet_composition.csv';rows=list(csv.reader(path.open(encoding='utf-8-sig',newline='')))
 # The import has prey IDs in column A, names in B, consumer IDs in row 1.
 for row in rows[1:]:
  if not row[0].isdigit():continue
  b=int(row[0])
  for ci,a in enumerate(rows[0][2:],2):
   if a.isdigit() and (int(a),b) in bycell:row[ci]=format(bycell[(int(a),b)]['fitted_raw_fraction'],'.17g')
 with path.open('w',encoding='utf-8',newline='') as f:csv.writer(f,lineterminator='\n').writerows(rows)
 # Retain current fitted import in its canonical embedded table; inherited round-trip
 # results remain explicitly parent evidence, never a claim for this changed variant.
 c['extraction_source_tables']['Diet_composition.csv']=rows
 dump(dest/'model.json',c)
 dump(dest/'inputs/provenance.json',{'schema_version':1,'model_id':new_id,'parent_model_id':source.name,'model_sha256':hashlib.sha256((dest/'model.json').read_bytes()).hexdigest(),'derivation':'Researcher authorized bounded reconstruction of censored gray diet cells; no source overwrite','scientific_status':'FAIL; exact gray-only mass balance infeasible','fit_summary':'../extracted_tables/evidence/gray_diet_fit/fit_summary.json'})
 print(period,json.dumps({k:{x:v[x] for x in ['exact_feasible','minimax_relative_residual_lower_bound','strict_mass_balance','positive_gray_values']} for k,v in results.items()}),flush=True)
 print('worst',results[chosen]['largest_issues'][:4],flush=True)
for period in ['1990_1994','2008_2012']:fit(period,derive_f='--derive-F' in sys.argv)
