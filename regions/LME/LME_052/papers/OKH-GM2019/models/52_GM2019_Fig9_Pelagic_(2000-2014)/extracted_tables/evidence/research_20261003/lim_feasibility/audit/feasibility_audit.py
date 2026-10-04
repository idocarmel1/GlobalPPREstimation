"""Read-only feasibility bounds. No fitting, model editing, or runtime completion."""
from pathlib import Path
from decimal import Decimal as D, getcontext
import csv, hashlib, json
getcontext().prec=40
HERE=Path(__file__).resolve().parent
CANDIDATE=HERE.parents[2]
ROOT=HERE.parents[6]
FIG=CANDIDATE/'assumption_variants/researcher_readings_20261003'
TEXT=CANDIDATE/'assumption_variants/text_plus_figure_20261003'
inputs={}
def read(path):
 data=path.read_bytes();inputs[str(path)]=hashlib.sha256(data).hexdigest()
 return json.loads(data.decode('utf-8-sig'))
def save(name,data):
 (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
fig=read(FIG/'carbon_reconstruction.json')
budgets=read(FIG/'flow_budget_checks.json')
basic=read(FIG/'model.json')
factors={r['group_id']:r['wet_per_carbon'] for r in read(FIG/'conversion_factors.json')}
factors[3]='10.0' # Latest user-authorized best guess; not original group-specific source datum.
hybrid=read(TEXT/'diet_constraints.json')
coverage=read(TEXT/'balance_check_coverage.json')
groups={g['group_id']:g for g in budgets}
wetQ={g['n']:D(0) for g in fig['groups']}
wet_missing={g['n']:set() for g in fig['groups']}
for f in fig['flows']:
 value=D(f['adopted_carbon_flow'])
 if value==0:continue
 factor=factors[f['prey_id']]
 if factor is None:wet_missing[f['consumer_id']].add(f['prey_id'])
 else:wetQ[f['consumer_id']]+=value*D(factor)

def interval(P,Q):
 if P is None or Q is None:return dict(status='UNDETERMINED',physical_GS_interval=None,standard_LIM_GS_interval=None)
 P,Q=D(P),D(Q)
 ceiling=1-P/Q
 physical=None if ceiling<0 else ['0',str(min(D(1),ceiling))]
 lim=None if ceiling<D('.10') else ['.10',str(min(D('.35'),ceiling))]
 return dict(status='INFEASIBLE_EVEN_GS_ZERO' if ceiling<0 else ('INFEASIBLE_STANDARD_LIM_GS_RANGE' if ceiling<D('.10') else 'ENERGY_FEASIBLE_RANGE_ONLY'),P=str(P),Q=str(Q),GS_ceiling_for_R_nonnegative=str(ceiling),physical_GS_interval=physical,standard_LIM_GS_interval=lim,positive_respiration_requires_GS_strictly_below_ceiling=True,unique_GS_identified=False)

figure_records=[]
for i in range(2,22):
 b=groups[i]
 for currency in ['carbon','wet']:
  P=b['figure_P_carbon'] if currency=='carbon' else b['P_wet_from_B_times_PB']
  Q=b['Q_carbon'] if currency=='carbon' else (None if wet_missing[i] else str(wetQ[i]))
  r=dict(case='figure_only',group_id=i,group=b['group'],currency=currency,production_basis='Accepted Figure9 box' if currency=='carbon' else 'Native wet biomass times source P/B; not Figure9 production multiplied by factor',Q_basis='Sum accepted Figure9 arrows; wet Q converts each prey separately using bacteria9.4/protozoa10',missing_prey_conversion_ids=sorted(wet_missing[i]) if currency=='wet' else [],source_scope='2019pp.154,157; accepted flow readings and latest user-authorized proto factor10')
  r.update(interval(P,Q));figure_records.append(r)
save('figure_only_GS_intervals.json',figure_records)

text_records=[]
for r in coverage['text_plus_figure']['source_Q_wet_diagnostics']:
 b=groups[r['group_id']]
 result=dict(case='text_plus_figure_partial',group_id=r['group_id'],group=r['group'],currency='wet',production_basis='Native wet biomass times P/B',Q_basis='Independent primary2019 prose total Q; no allocation/rescaling of Figure9 arrows',source=r['source'],full_network_balance_claim=False)
 result.update(interval(b['P_wet_from_B_times_PB'],r['source_Q_wet']));text_records.append(result)
save('text_plus_figure_wet_GS_intervals.json',text_records)

# Carbon lower bounds: pooled microbial prey can be bacteria9.4 or protozoa10;
# unallocated diet remainder remains unknown. A negative lower-bound residual
# is not a proof of negative total respiration.
lower_bounds=[]
for part in hybrid['partial_diets']:
 ids=part['consumer_ids']
 if ids is None or len(ids)!=1:continue
 i=ids[0]
 known=D(0);components=[]
 for prey in part['known_wet_fractions']:
  pids=prey['prey_ids']
  if not pids or any(factors[p] is None for p in pids):continue
  wet=D(part['Qwet'])*D(prey['fraction'])
  if i==7 and pids==[4]:wet=D(part['separately_printed_copepod_Qwet'])
  if i==6 and pids==[4]:wet=D('56.7')
  factor=max(D(factors[p]) for p in pids)
  amount=wet/factor;known+=amount
  components.append(dict(prey_ids=pids,wet_Q=str(wet),carbon_lower_bound=str(amount),factor_for_lower_bound=str(factor),pooled_group_split_unresolved=len(pids)>1))
 P=D(groups[i]['figure_P_carbon'])
 ceiling=1-P/known if known else None
 lower_bounds.append(dict(case='text_plus_figure_partial',group_id=i,group=groups[i]['group'],P_carbon=str(P),known_carbon_Q_lower_bound=str(known),components=components,GS_ceiling_guaranteed_by_known_prey_only=str(ceiling) if ceiling is not None else None,entire_standard_LIM_GS_range_energy_safe_on_lower_bound=known*D('.65')>P,remaining_prey_unknown=True,negative_lower_bound_residual_is_not_infeasibility_proof=True,total_Q_carbon_identified=False))
save('text_plus_figure_carbon_lower_bound_constraints.json',lower_bounds)

EE=[]
for i,b in groups.items():
 P,Dpred=D(b['figure_P_carbon']),D(b['predation_carbon'])
 EE.append(dict(group_id=i,group=b['group'],currency='million tC/year',P=str(P),predation=str(Dpred),catch='0',net_migration='0',equations=['M0=P*(1-EE)','BA=P*EE-predation'],EE_physical_interval=['0','1'],BA_corresponding_physical_interval=[str(-Dpred),str(P-Dpred)],EE_standard_LIM_interval_if_M0_is_free=['0','.95'],BA_corresponding_standard_LIM_interval=[str(-Dpred),str(D('.95')*P-Dpred)],EE_if_BA_were_zero=str(Dpred/P),BA_zero_is_not_assumed=True,requires_negative_BA_for_all_physical_EE=Dpred>P,EE_and_BA_identified=False,source_flow_routes_tentative_where_not_clear=b['predation_clear_lower_bound_carbon']!=b['predation_carbon']))
save('EE_BA_feasibility_families.json',EE)

code=ROOT/'tools/scientific_code/PPREstimation/PPRCalculator.py'
codebytes=code.read_bytes();inputs[str(code)]=hashlib.sha256(codebytes).hexdigest()
runtime=dict(code_path=str(code),sha256=inputs[str(code)],read_only_execution_audit=False,standard_GS_bounds=[.10,.35],GS_constraint_code_lines=[779,793],standard_EE_bounds=[0,.95],EE_constraint_code_lines=[763,777],respiration_egestion_M0_nonnegative_bounds_code_lines=[707,716],biomass_accum_bounds='unbounded signed',zero_biomass_accum_default=True,required_to_keep_living_BA_free='zero_biomass_accum=False',required_to_make_GS_free='Clear user-default gs on a separate runtime copy and set default_gs=False; this option alone does not erase supplied gs=.2.',missing_biomass_default='1',biomass_fallback_code_line=471,solver_variables=['q','p','respiration','egestion','M0','biomass_accum'],flow_completion_code_lines=[669,679],source_microbe_parameters_recovered_by_runtime=False,microbial_missing_parameters=[dict(group=int(g['group_seq']),missing=[k for k in ['biomass','pb','qb','ee'] if g[k]=='-9999']) for g in basic['group'] if g['group_seq'] in ['2','3']],figure_production_values_not_loaded_into_microbe_model_basics=True,warning='LIM can choose missing p/q and derive PB/QB using default biomass1. That is computational completion, not source recovery; Figure9 microbial production/flow constraints must be explicitly loaded and checked to preserve them.',legacy_balanced_copy_changes_growth_or_migration=True,legacy_balancer_code_lines=[843,871])
save('runtime_constraint_provenance.json',runtime)
save('input_hashes.json',inputs)

carbonfails=[r['group_id'] for r in figure_records if r['currency']=='carbon' and r['physical_GS_interval'] is None]
wetfails=[r['group_id'] for r in figure_records if r['currency']=='wet' and r.get('status')!='UNDETERMINED' and r['standard_LIM_GS_interval'] is None]
summary=dict(catch_assumption=0,net_migration_assumption=0,GS_solved_not_fixed=True,proto_factor_assumption='10.0',bacteria_factor='9.4',living_BA_assumption='Unknown/free; not zero',detritus_assumption='All M0/GS to sole detritus; imports/export zero; stock BA is residual',figure_only_physical_carbon_energy_failure_ids=carbonfails,figure_only_standard_LIM_wet_energy_failure_ids=wetfails,figure_only_balanced_physical_model_possible_with_fixed_P_and_Q=False,text_plus_figure_status='Incomplete source constraints, not a full diet matrix',text_plus_figure_with_unchanged_salmon_jellyfish_figure_columns_physical_energy_failure_ids=[8,14],text_can_resolve_hyperiid_wet_energy_failure=True,text_cannot_yet_identify_total_hyperiid_carbon_Q=True,unique_GS_or_EE_identified=False,model_or_original_modified=False,fit_performed=False,input_hashes_unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==s for p,s in inputs.items()))
assert carbonfails==[6,8,14] and wetfails==[6,8,14] and summary['input_hashes_unchanged']
save('summary.json',summary)
print(json.dumps(summary))
