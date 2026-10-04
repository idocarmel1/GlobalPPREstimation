"""Compare source carbon budgets with the existing wet-weight reconstruction.

Does not fit or modify values. Predation residuals are diagnostic only, with
zero catch/living BA/net migration in that specific diagnostic, not assumptions
adopted in the model. The illustrative F62/F67 readings remain illustrative.
"""
from pathlib import Path
from decimal import Decimal,localcontext
from collections import defaultdict
import json,hashlib

OUT=Path(__file__).resolve().parent
HERE=OUT.parents[1]
D=Decimal
def load(p):return json.loads(p.read_text(encoding='utf-8'))
groups=load(HERE/'carbon_reconstruction.json')['groups']
flows=load(HERE/'audit/flow_readings.json')
table=load(HERE/'audit/table3_source_readings.json')
basic=load(HERE/'extracted_tables/extraction.json')['groups']
stocks={r['figure_group_id']:r for r in table if r['figure_group_id'] is not None}
input_hashes={str(p.relative_to(HERE)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'carbon_reconstruction.json',HERE/'audit/flow_readings.json',HERE/'audit/table3_source_readings.json',HERE/'extracted_tables/extraction.json']}
incoming=defaultdict(list);outgoing=defaultdict(list)
for f in flows:incoming[f['consumer_id']].append(f);outgoing[f['prey_id']].append(f)
def total(fs,kind):
 vals=[f['readable_carbon_flow'] if f['readable_carbon_flow'] is not None else f['hypothesis_reading'] if kind=='hypothesis' else None for f in fs if kind!='clear' or f['routing_status']=='clear']
 return sum((D(x) for x in vals),D(0)) if all(v is not None for v in vals) else None
def s(v):return str(v) if v is not None else None
result=[];factors=[]
with localcontext() as ctx:
 ctx.prec=40
 for g,b in zip(groups,basic):
  n=g['n'];t=stocks.get(n);factor=t['wet_per_carbon'] if t else None
  factors.append(dict(group_id=n,group=g['name'],wet_per_carbon=factor,basis='Table 3 mapped source row' if t else 'separate microbial factors not stated in 2019 Table 3' if n in [2,3] else 'not stated',mapping_tentative=n==20))
  if n==22:continue
  P=D(g['figure_production_carbon_million_t_per_year'])
  Q=total(incoming[n],'main') if n!=1 else None
  pred=total(outgoing[n],'main');pred_clear=total(outgoing[n],'clear');pred_h=total(outgoing[n],'hypothesis')
  bc_published=D(t['biomass_carbon_million_t']) if t else None
  bc_from_factor=D(t['biomass_wet_million_t'])/D(factor) if t else None
  pb=D(t['pb_per_year']) if t else None
  p_factor=bc_from_factor*pb if t else None
  q_w=D(b['qb'])*D(t['biomass_wet_million_t']) if t and b['qb'] is not None else None
  p_w=D(t['biomass_wet_million_t'])*pb if t else None
  r_c=Q*D('.8')-P if Q is not None else None
  r_w=q_w*D('.8')-p_w if q_w is not None else None
  result.append(dict(group_id=n,group=g['name'],figure_production_carbon=s(P),incoming_carbon=s(Q),incoming_clear_carbon=s(total(incoming[n],'clear')),carbon_respiration_GS_0p2=s(r_c),carbon_energy_failure=r_c is not None and r_c<=0,wet_production_from_B_PB=s(p_w),wet_consumption_from_existing_QB=s(q_w),wet_respiration_GS_0p2=s(r_w),wet_energy_failure=r_w is not None and r_w<=0,minimum_positive_respiration_QB_wet=s(pb/D('.8')) if pb is not None and n!=1 else None,predation_main_carbon=s(pred),predation_clear_lower_bound_carbon=s(pred_clear),predation_illustrative_carbon=s(pred_h),predation_over_P_main=s(pred/P) if pred is not None else None,predation_over_P_illustrative=s(pred_h/P),clear_predation_already_exceeds_P=pred_clear>P,minimum_net_living_subsidy_if_other_losses_zero_main=s(max(D(0),pred-P)) if pred is not None else None,minimum_net_living_subsidy_illustrative=s(max(D(0),pred_h-P)),published_B_carbon=s(bc_published),B_carbon_derived_from_wet_factor=s(bc_from_factor),P_carbon_from_wet_B_factor_and_PB=s(p_factor),minimal_subsidy_to_carbon_stock_ratio_illustrative=s(max(D(0),pred_h-P)/bc_from_factor) if bc_from_factor is not None else None))
 # Prose-derived Q/B values remain separate from the figure-derived baseline.
 recoverable=[dict(group_id=4,group='Copepods',reported_Q_wet='2945',reported_B_wet='108.3',QB=s(D('2945')/D('108.3')),printed_source_page=153),dict(group_id=5,group='Euphausiids',reported_Q_wet='1445.6',reported_B_wet='58.7',QB=s(D('1445.6')/D('58.7')),printed_source_page=153)]
 # Algebraic nonidentifiability: the production budget supplies one equation
 # for catch, net migration, BA and M0, not separate observed parameter values.
 record=dict(source_input_hashes=input_hashes,units='flows million tonnes/year in indicated currency; rate /year',GS='0.2',factor_definition='wet biomass = carbon biomass * wet_per_carbon',groups=result,current_2019_conversion_factors=factors,recoverable_prose_QB=recoverable,diagnostic_closure='catch=0, living BA=0, net migration=0 only when evaluating predation/P; these remain unknown in the model',conclusions=dict(carbon_energy_failure_ids=[r['group_id'] for r in result if r['carbon_energy_failure']],wet_energy_failure_ids=[r['group_id'] for r in result if r['wet_energy_failure']],clear_route_predation_failure_ids=[r['group_id'] for r in result if r['clear_predation_already_exceeds_P']],currency_induced_chaetognath_failure=True,catch_BA_migration_not_separately_identifiable=True,source_model_ready=False))
 (OUT/'currency_and_budget_checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
assert record['conclusions']['carbon_energy_failure_ids']==[6,8,14]
assert record['conclusions']['wet_energy_failure_ids']==[6,7,8,14]
assert all(hashlib.sha256((HERE/p).read_bytes()).hexdigest()==h for p,h in input_hashes.items())
assert len(factors)==22 and sum(r['wet_per_carbon'] is not None for r in factors)==19
print(json.dumps(dict(output=str(OUT/'currency_and_budget_checks.json'),**record['conclusions']),ensure_ascii=False,indent=2))
