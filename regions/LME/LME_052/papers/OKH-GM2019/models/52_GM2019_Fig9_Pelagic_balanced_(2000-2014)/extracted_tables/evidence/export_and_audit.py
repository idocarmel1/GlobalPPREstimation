"""Retained-return interfaces, lossless masks, eight imports and hypothesis audit."""
from pathlib import Path
from copy import deepcopy
import csv, json, itertools, math, subprocess, sys
import reconstruct_and_verify as r
import pandas as pd
import numpy as np

H=r.HERE
native=r.read(H/'model.json')
result=r.read(H/'native_reload_result.json')
assert r.sha(H/'model.json')==result['exact_input_sha256']
def frame(x):return pd.DataFrame(x['data'],index=x['index'],columns=x['columns'])
df=frame(result['final_groups']);df.index.name='group_seq'
df.to_csv(H/'groups_df.csv',encoding='utf-8')
r.save(H/'groups_df.json',result['final_groups'])
scopes=[]; negatives=[]; masks={}; health={}; reconciliations={};arithmetic_metrics={}
for option in ['GE','TE','With Egestion']:
 tag=option.replace(' ','_');d=r.read(H/'diagnostics'/f'{tag}_full_return.json')
 sppr=frame(d['SPPR'])
 for n in sppr.index:
  scopes.append(dict(group_seq=n,group_name='diet_import' if n==23 else r.names[n],method=option,
   sppr_all=sppr.loc[n].sum(),sppr_inner=sppr.loc[n,[22,1]].sum(),sppr_pp=sppr.loc[n,1],
   sppr_import=sppr.loc[n,23],sppr_detritus=sppr.loc[n,22],biological_group=n<=22,
   units='tC basal source per tC recipient group',body_wet_per_C=1. if n==23 else r.factor[n]))
 for key in ['SPPR','A','L','TE']:
  x=frame(d[key]);vals=x.to_numpy(dtype=float)
  masks[option+' '+key]=dict(index=list(x.index),columns=list(x.columns),orientation='returned rows andcolumns unchanged',
   null_mask=x.isna().to_numpy().tolist(),nan_mask=np.isnan(vals).tolist(),
   positive_infinity_mask=np.isposinf(vals).tolist(),negative_infinity_mask=np.isneginf(vals).tolist())
  for i,j in zip(*np.where(vals < -1e-12)):
   negatives.append(dict(method=option,matrix=key,recipient_id=x.index[i],recipient_name=r.names.get(x.index[i],'diet_import'),
    source_id=x.columns[j],source_name=r.names.get(x.columns[j],'diet_import'),value=vals[i,j],tolerance=1e-12))
  reconciliations[option+' '+key+' unique_axes']=bool(x.index.is_unique and x.columns.is_unique)
  reconciliations[option+' '+key+' finite']=bool(np.isfinite(vals).all())
 report=d['report']
 health[option]=dict(overall=report['status'],model_input=report['model_input']['status'],
  main_model_balanced=report['model_input']['is_model_balanced'],divergence=report['divergence']['status'],
  ppr_balance=report['balance']['status'],ppr_is_balanced=report['balance']['is_balanced'],
  rho_living=report['divergence']['rho_living'],b=report['divergence']['b'],
  sppr_det=report['divergence']['sppr_det'],warnings=report['warnings'],
  exact_model_sha256=result['exact_input_sha256'],settings=r.SETTINGS)
 full=sppr.sum(axis=1);parts=sppr[[22,1]].sum(axis=1)+sppr[23]
 delta=(full-parts).abs(); relative=delta/full.abs().clip(lower=1.)
 # Summing three largefloating-pointcoefficients in a differentorder can differ
 # byoneULP (>1e-12 absolute forlargevalues). Quantify this anddeclarebothlimits.
 reconciliations[option+' fullmatrix_scope_identity']=bool(np.allclose(full,parts,rtol=1e-15,atol=1e-12))
 arithmetic_metrics[option]=dict(max_absolute_scope_sum_gap=float(delta.max()),max_relative_scope_sum_gap=float(relative.max()),
  absolute_tolerance=1e-12,relative_tolerance=1e-15,reason='Same retainedcells,differentfloating-pointadditionorder; no coefficient ormodelmodified')
 reconciliations[option+' no_negative_source_entries']=not any(n['method']==option and n['matrix']=='SPPR' for n in negatives)
pd.DataFrame(scopes).to_csv(H/'diagnostics/scoped_SPPR.csv',index=False,encoding='utf-8')
pd.DataFrame(negatives,columns=['method','matrix','recipient_id','recipient_name','source_id','source_name','value','tolerance']).to_csv(H/'diagnostics/negative_entries.csv',index=False,encoding='utf-8')
r.save(H/'diagnostics/serialization_masks.json',masks)
r.save(H/'diagnostics/model_health.json',health)
r.save(H/'diagnostics/reconciliation.json',reconciliations)
r.save(H/'diagnostics/scope_arithmetic_metrics.json',arithmetic_metrics)
# A direct source input has unknownGS/EE/R, unlike the completed LIM state. Eight
# imports preserve those unknowns; EwE's own missingGS default is not our solvedGS.
ex=dict(metadata={'LME':'52 Sea of Okhotsk','model_number':'GM2019-Fig9-balanced',
 'model_name':'Sea of Okhotsk pelagic balanced assumption reconstruction','model_year':'2000-2014'},
 groups=[],consumers=list(range(2,22)),fleets=['Assumed zero catch'],landings={},discards={},
 detritus_groups=['Detritus'],detritus_fate={},diet={},diet_rows=22,landings_rows=22,discards_rows=22,
 companions={'Native_currency_and_assumptions.csv':{'description':'Explicitderivedmodel provenance, not authorinputs',
  'rows':[['field','value'],['currency','tC/km2 and tC/km2/year'],
   ['native_model_sha256',result['exact_input_sha256']],
   ['GS','Unknowninput; actualstandardLIMsolved; do notacceptEwEdefaultasverifiedGS'],
   ['input_identity','Authorizedassumptionvariant; sourcecanonicalunchanged']]}})
def value(x):return None if x=='-9999' else x
for g in native['group']:
 n=int(g['group_seq'])
 ex['groups'].append(dict(n=n,name=g['group_name'],hab_area='1',biomass=value(g['biomass']),
  pb=value(g['pb']),qb=value(g['qb']),ee=value(g['ee']),other_mort=value(g['other_mort']),
  pq=value(g['ge']),unassim=value(g['gs']),detritus_import='0',tl=r.sval(float(df.loc[n,'tl'])),
  ba=value(g['biomass_accum']),ba_rate=None))
 ex['landings'][str(n)]={'Assumed zero catch':'0'};ex['discards'][str(n)]={'Assumed zero catch':'0'}
 ex['detritus_fate'][str(n)]={'Detritus':'1'}
 if n in ex['consumers']:
  ex['diet'][str(n)]={c['prey_seq']:c['proportion'] for c in g['diet_descr']['diet']}
  ex['diet'][str(n)]['import']=g['diet_imp']
ex['companions']['Native_fields_not_in_eight_templates.csv']={
 'description':'Authoritative native fields unsupported bystandardEwEimportschemas; retainedseparately, notassertedEwEimports',
 'rows':[['group_seq','group_name','pp','immigration','emigration','emigration_rate','respiration','native_biomass_accum_rate'],
  *[[g[k] for k in ['group_seq','group_name','pp','immigration','emigration','emigration_rate','respiration','biomass_accum_rate']] for g in native['group']]]}
r.save(H/'export_extraction.json',ex)

# Quantitative alternative test. Search 10x/100x reductions in each deficit prey's
# retained arrows. Fixed human labels are never candidates. F62both sensitivities
# must fit availability; source-completeconsumer8/14 paths aren't oldFigurelinks.
z=r.figure_flows(.025,False);r.replace_source_diets(z,complete_text=True)
alternatives=[]
for prey in [9,10,11,13,16,19]:
 outgoing=[f for f in r.CARBON['flows'] if f['prey_id']==prey and f['consumer_id'] not in [8,14] and f['flow_id'] not in ['F62','F67']]
 d=sum(row[prey] for row in z.values());capacity=.95*r.P[prey]
 feasible=[]
 for powers in itertools.product([0,1,2],repeat=len(outgoing)):
  after=d-sum(float(f['adopted_carbon_flow'])*(1-10**(-k)) for f,k in zip(outgoing,powers))
  if after<=capacity+1e-12:
   feasible.append((sum(k>0 for k in powers),sum(powers),d-after,powers,after))
 best=min(feasible) if feasible else None
 selected=[f for f in outgoing if f['flow_id'] in r.CORRECTIONS]
 chosen_after=d-sum(float(f['adopted_carbon_flow'])-r.CORRECTIONS[f['flow_id']] for f in selected)
 stock_mult=d/capacity
 q=sum(z[prey].values())
 alternatives.append(dict(group_id=prey,group=r.names[prey],source_P=r.P[prey],unrepaired_text_predation=d,
  sustainable_capacity=capacity,chosen_predation=chosen_after,selected_arrow_count=len(selected),
  minimum_arrow_count=best[0] if best else None,minimal_total_decimal_exponent=best[1] if best else None,
  selected_set_minimum_arrow_count=bool(best and len(selected)==best[0]),
  minimum_search_scenario=[dict(flow_id=f['flow_id'],before=float(f['adopted_carbon_flow']),after=float(f['adopted_carbon_flow'])*10**(-k),decimal_exponent=k) for f,k in zip(outgoing,best[3]) if k] if best else [],
  stock_or_PB_minimum_multiplier_preserving_outgoing=stock_mult,
  alternative_P=d/.95,alternative_pb=(d/.95)/r.B[prey],source_pb=tablepb if (tablepb:=r.table[prey]['pb_per_year']) else None,
  available_unrepaired_Q=q,production_only_alternative_energy_feasible=d/.95<=.9*q,
  rejected_production_reason='Requiresmajorunsupportedstock/PBchange despiteindependentlyconfirmedproduction; endpointinversionsambiguous; not an established error',
  assumptions='Thiscombinatorialcheck minimizeschangedlabels amongdecimalhypothesesonly. It does not prove asource typo or globallyoptimalecologicalrepair.'))
r.save(H/'alternative_hypotheses.json',alternatives)
# Complete before/after arrow andprey tables include unchanged/source-overridden
# labels, rather than hiding labels which weren't computationally adopted.
finalflows=r.read(H/'carbon_food_flows.json');all_arrows=[]
for f in r.CARBON['flows']:
 n=f['consumer_id'];p=f['prey_id']
 all_arrows.append(dict(flow_id=f['flow_id'],prey_id=p,consumer_id=n,
  source_literal=f['source_literal'],accepted_figure_carbon=float(f['adopted_carbon_flow']),
  assumed_figure_carbon=r.CORRECTIONS.get(f['flow_id'],float(f['adopted_carbon_flow'])),
  final_aggregate_pair_carbon=finalflows[str(n)][str(p)],routing_status=f['routing_status'],
  final_pair_basis='QuantitativetextreplacesFigureconsumerdiet' if n in [4,5,6,7,8,10,11,12,13,14] else ('Textaggregatewithretainedpathsandimportcompletion' if n in [9,16] else 'RetainedFigurepathswithdecimalhypotheses'),
  exact_source_error_proven=False,
  interpretation='Duplicatepairlabels cannotbe individuallyassigned in finaldiet; final_pair is not one label andmustnotbesummedonceperduplicate.' ))
r.save(H/'all_arrow_decisions.json',all_arrows)
pd.DataFrame(all_arrows).to_csv(H/'all_arrow_decisions.csv',index=False,encoding='utf-8')
changes=r.read(H/'source_to_final_ledger.json')
changes['alternative_hypotheses']='alternative_hypotheses.json';changes['all_unchanged_and_overridden_arrows']='all_arrow_decisions.json'
changes['GS_and_EE_final_numeric_per_group']='native_reload_result.json.rows'
changes['initial_microbe_split_rejected']='trials/initial_microbe_split/model.json: protozoaEE0.957892; sourceQandpooledfractionpreserved by smallcopepodsplitchange2/3wet'
r.save(H/'source_to_final_ledger.json',changes)
print('Export interfaces written; model unchanged',r.sha(H/'model.json'))
print('Minimal arrow audit',[(a['group_id'],a['selected_arrow_count'],a['minimum_arrow_count'],a['selected_set_minimum_arrow_count']) for a in alternatives])
