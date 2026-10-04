"""Independent bounded review of saved runtime inputs/results. Never reruns or edits model."""
from pathlib import Path
import hashlib,json,math
HERE=Path(__file__).resolve().parent
LIM=HERE.parent
CANDIDATE=HERE.parents[2]
ROOT=HERE.parents[6]
RUN=LIM/'runtime'
hashes={}
def read(p):
 data=p.read_bytes();hashes[str(p)]=hashlib.sha256(data).hexdigest()
 return json.loads(data.decode('utf-8'))
def close(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10)
fig=read(CANDIDATE/'assumption_variants/researcher_readings_20261003/carbon_reconstruction.json')
seed=read(RUN/'fixed_carbon_seed.json')
native=read(RUN/'native_wet_input.json')
carbon=read(RUN/'fixed_figure_carbon_result.json')
wet=read(RUN/'native_wet_result.json')
assumptions=read(RUN/'assumptions.json')
verification=read(RUN/'verification.json')
script=LIM/'runtime_check.py';hashes[str(script)]=hashlib.sha256(script.read_bytes()).hexdigest()
living={g['n']:g for g in fig['groups'] if g['n']<=21}
consumers=fig['consumers']
rows={g['group_seq']:g for g in seed['group_rows']}
flows={}
for f in fig['flows']:
 key=(f['consumer_id'],f['prey_id'])
 flows[key]=flows.get(key,0)+float(f['adopted_carbon_flow'])
sourceQ={c:sum(v for (cc,p),v in flows.items() if cc==c) for c in consumers}
output={g['group_id']:g for g in carbon['main']['rows']}
check={
 'carbon_input_catch_zero':all(g['catch']==0 for g in rows.values()),
 'carbon_input_all_migration_terms_zero':all(g[k]==0 for g in rows.values() for k in ['immigration','emigration','net_migration','detritus_import']),
 'carbon_input_living_BA_unknown':all(rows[n]['biomass_accum'] is None for n in living),
 'carbon_input_consumer_GS_and_egestion_unknown':all(rows[n]['gs'] is None and rows[n]['egestion'] is None for n in consumers),
 'default_gs_disabled':assumptions['runtime_settings']['default_gs'] is False,
 'zero_living_BA_default_disabled':assumptions['runtime_settings']['zero_biomass_accum'] is False,
 'runtime_diet_normalization_disabled':assumptions['runtime_settings']['normalize_DC'] is False,
 'carbon_input_living_P_fixed_to_Figure':all(close(rows[n]['p'],float(g['figure_production_carbon_million_t_per_year'])) for n,g in living.items()),
 'carbon_input_consumer_Q_fixed_to_Figure':all(close(rows[n]['q'],sourceQ[n]) for n in consumers),
 'carbon_input_all_living_fate_to_detritus_one':all(seed['detritus_fate'][str(n)]['22']==1 for n in living),
 'carbon_output_living_P_preserved':all(close(output[n]['P'],float(g['figure_production_carbon_million_t_per_year'])) for n,g in living.items()),
 'carbon_output_consumer_Q_preserved':all(close(output[n]['Q'],sourceQ[n]) for n in consumers),
 'carbon_output_source_flows_preserved':all(close(output[c]['Q']*seed['DC'][str(c)][str(p)],v) for (c,p),v in flows.items()),
 'both_main_states_catch_all_migration_and_detritus_export_zero':all(r['main'][k] for r in [carbon,wet] for k in ['catch_zero','migration_zero','immigration_zero','emigration_zero','detritus_export_zero']),
 'both_main_states_algebraically_unbalanced':all(r['main']['algebraic_balance'] is False for r in [carbon,wet]),
 'both_legacy_states_migration_nonzero':all(r['legacy_balanced_copy']['migration_zero'] is False for r in [carbon,wet]),
 'both_legacy_states_algebraically_unbalanced':all(r['legacy_balanced_copy']['algebraic_balance'] is False for r in [carbon,wet]),
 'both_results_labelled_not_valid_complete_models':all(r['valid_complete_model'] is False for r in [carbon,wet]),
 'protected_source_candidate_selected_and_workbook_hashes_match':all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in verification['hashes'].items()),
 'native_consumer_GS_cleared':all(g['gs']=='-9999' for g in native['group'] if int(g['group_seq']) in consumers),
 'native_migration_fields_zero':all(g[k]=='0' for g in native['group'] for k in ['immigration','emigration','detritus_import','export']),
}
failed={name:[g['group_id'] for g in r['main']['rows'] if g['table_unsolved_fields']] for name,r in [('fixed_figure_carbon',carbon),('native_wet',wet)]}
check['both_unsolved_group_lists_exactly_6_8_14']=all(ids==[6,8,14] for ids in failed.values())
check['failed_GS_EE_table_values_not_estimates']=all(output[n]['GS_table'] is None and output[n]['EE_table'] is None for n in [6,8,14])
check['solved_carbon_regular_groups_GS_EE_within_standard_bounds']=all(.10-1e-8<=output[n]['GS_table']<=.35+1e-8 and -1e-8<=output[n]['EE_table']<=.95+1e-8 and output[n]['respiration']>=-1e-8 for n in consumers if n not in [6,8,14])
det=output[22]
inflow=sum(output[n]['mortality']+output[n]['egestion'] for n in living)
check['main_detritus_BA_is_computed_residual']=close(det['BA'],inflow-det['predation'])
assert all(check.values()),{k:v for k,v in check.items() if not v}
result={'review_scope':'Saved input/code/result review; no new runtime fit or model edit',
 'checks':check,'unsolved_groups':failed,
 'direct_fixed_carbon_energy_residuals_Q_minus_P_R_U':{str(n):output[n]['Q']-output[n]['P']-output[n]['respiration']-output[n]['egestion'] for n in [6,8,14]},
 'GS_vector_0_EE_vector_1_for_failed_groups_are_fallbacks_not_solutions':True,
 'detritus_balance_partial_inflow_caveat':'Residual is computed from finalized runtime vectors; failed consumer mortality/egestion are fallback0, so this is not a valid complete ecological detritus budget.',
 'synthetic_import_scaffolding':{'group':23,'P':rows[23]['p'],'Q':rows[23]['q'],'incoming_outgoing_living_diet_links':0,'assessment':'Disconnected helper row does not affect source living equations; P=Q=1 must not be included in scientific system totals/SPPR. Fixture is labelled native_model=False.'},
 'runtime_validity_verdict':'Both constructors succeeded, but neither produced a complete balanced model satisfying physical/source constraints. Legacy copies are separately noncompliant with zero migration and remain algebraically unbalanced.',
 'hashes':hashes,
 'inputs_still_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==s for p,s in hashes.items())}
assert result['inputs_still_unchanged']
(HERE/'runtime_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Independent checks passed:',len(check),'checks; scientific feasibility remains failed.')
