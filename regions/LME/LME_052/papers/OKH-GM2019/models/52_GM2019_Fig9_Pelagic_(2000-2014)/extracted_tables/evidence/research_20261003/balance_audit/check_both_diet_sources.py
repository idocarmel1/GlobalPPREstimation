"""Keep figure-only and text-plus-figure inputs in the balance test contract.

Partial hybrid diets are constraints, not fabricated complete diets. This check
records available energy diagnostics and explicitly withholds a global balance
verdict where stock/diet information remains incomplete.
"""
from pathlib import Path
from decimal import Decimal, localcontext
import hashlib, json, os

WORK=Path(__file__).resolve().parent
HERE=WORK.parents[1]
BASE=HERE/'assumption_variants/researcher_readings_20261003'
TEXT=HERE/'research_20261003/text_feeding_audit'
OUT=HERE/'assumption_variants/text_plus_figure_20261003'
OUT.mkdir(parents=True,exist_ok=True)
D=Decimal
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def ref(p):return Path(os.path.relpath(p,OUT)).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
partial=read(TEXT/'partial_numeric_diets.json')
links=read(TEXT/'candidate_additional_22group_links.json')
original_budgets=read(BASE/'flow_budget_checks.json')
table={r['figure_group_id']:r for r in read(HERE/'audit/table3_source_readings.json') if r['figure_group_id'] is not None}
Q_targets=read(HERE/'research_20261003/article_constraints/independent_QB_targets.json')
factors={r['group_id']:r['wet_per_carbon'] for r in read(BASE/'conversion_factors.json')}
input_paths=[BASE/'model.json',BASE/'carbon_reconstruction.json',BASE/'flow_budget_checks.json',
    TEXT/'partial_numeric_diets.json',TEXT/'primary_prose_feeding_links.json',
    TEXT/'candidate_additional_22group_links.json',
    HERE/'research_20261003/article_constraints/independent_QB_targets.json']
before={str(p):sha(p) for p in input_paths}

with localcontext() as ctx:
    ctx.prec=40
    wet_checks=[]
    for target in Q_targets:
        n=target['group_id']
        if n not in table:
            continue  # Pooled squid Q cannot identify individual tierIII/IV rates.
        t=table[n]
        q=D(target['source_Qwet_million_t_per_year'])
        p=D(t['biomass_wet_million_t'])*D(t['pb_per_year'])
        r=D('.8')*q-p
        wet_checks.append(dict(group_id=n,group=target['group'],source_Q_wet=str(q),
            P_wet_from_B_PB=str(p),R_wet_GS_0p2=str(r),nonpositive_wet_residual=r<=0,
            source=target['source'],scope='Source-Q-only wet diagnostic; not a complete hybrid network test'))
    carbon_lower_bounds=[]
    for diet in partial:
        ids=diet.get('consumer_ids')
        if not ids or len(ids)!=1 or diet.get('Qwet') is None:continue
        n=ids[0];q=D(diet['Qwet']);known=D(0);known_prey=[]
        for f in diet['known_wet_fractions']:
            prey=f.get('prey_ids')
            if prey and len(prey)==1 and factors.get(prey[0]) is not None:
                known+=q*D(f['fraction'])/D(factors[prey[0]])
                known_prey.append(prey[0])
        if n==7:
            # Prefer explicit281.4Mt prey mass over its rounded87.9% representation.
            known=D(diet['separately_printed_copepod_Qwet'])/D(factors[4])
        if not known_prey:
            continue
        p=D(next(r for r in original_budgets if r['group_id']==n)['figure_P_carbon'])
        r_min=D('.8')*known-p
        carbon_lower_bounds.append(dict(group_id=n,known_prey_ids=known_prey,
            carbon_Q_lower_bound=str(known),P_carbon=str(p),R_carbon_lower_bound_GS_0p2=str(r_min),
            energy_status='Positive even using only quantified text prey' if r_min>0 else 'Indeterminate: remaining prey not quantified',
            not_a_negative_respiration_proof=r_min<=0))
    smelt=next(d for d in partial if d.get('consumer_ids')==[11])
    assert smelt['dc_wet_by_prey_group_id']=={'4':'0.407','5':'0.461'}
    assert D(smelt['unallocated_fraction'])==D('.132')
    assert sum(D(f['fraction']) for f in smelt['known_wet_fractions'])+D('.132')==1
    assert next(x for x in links if x['prey_id']==7 and x['consumer_id']==7)['numeric_wet_DC'] is None
    assert next(x for x in links if x['prey_id']==4 and x['consumer_id']==11)['numeric_wet_DC']=='0.407'
    hybrid=dict(case_id='text_plus_figure',status='PARTIAL_CONSTRAINT_DATASET_NOT_A_COMPLETE_MODEL',
        source_figure_inputs=ref(BASE/'carbon_reconstruction.json'),
        source_figure_model=ref(BASE/'model.json'),
        primary_text_links=ref(TEXT/'primary_prose_feeding_links.json'),
        primary_text_partial_diets=ref(TEXT/'partial_numeric_diets.json'),
        partial_diets=partial,additional_named_links=links,
        reconciliation_rule='Preserve both source observations; explicitly reconcile conflicts before assembling a complete hybrid DC. Direct printed diet fractions remain separate from normalized figure-flow fractions.',
        unknown_rule='Unspecified remainder and ambiguous percentages are unknown, not zero; do not normalize partial fractions.',
        source_figure_zero_rule='Retained only in the separate Figure-only case; prose-established links must not be tested as absent zero cells in the combined case.',
        full_balance_ready=False,native_model_ready=False,selected=False)
    save(OUT/'diet_constraints.json',hybrid)
    result=dict(mandatory_case_ids=['figure_only','text_plus_figure'],
        user_instruction='2026-10-03: later balance checks must also test text+figure extracted diets',
        figure_only=dict(input=ref(BASE/'model.json'),
            balance_diagnostics_executed=True,full_balance_passed=False,
            carbon_energy_failure_ids=[r['group_id'] for r in original_budgets if r['energy_failure_carbon']],
            wet_energy_failure_ids=[r['group_id'] for r in original_budgets if r['energy_failure_wet']],
            predation_excess_ids=[r['group_id'] for r in original_budgets if r['predation_failure_carbon']]),
        text_plus_figure=dict(input='diet_constraints.json',
            partial_energy_diagnostics_executed=True,
            source_Q_wet_diagnostics=wet_checks,quantified_text_prey_carbon_lower_bounds=carbon_lower_bounds,
            complete_DC_and_basic_input_checks='INCOMPLETE',
            full_network_predation_EE_detritus_and_native_load_checks='NOT_RUN: unresolved diets, crosswalks and microbial basics',
            full_balance_passed=None,
            required_on_resume=True),
        verdict='No complete balanced model. A partial combined test is not a pass.',
        source_inputs_unchanged=before)
    save(OUT/'balance_check_coverage.json',result)
    save(HERE/'BALANCE_CHECK_INPUTS.json',dict(required_case_ids=['figure_only','text_plus_figure'],
        figure_only='assumption_variants/researcher_readings_20261003/model.json',
        text_plus_figure='assumption_variants/text_plus_figure_20261003/diet_constraints.json',
        latest_coverage='assumption_variants/text_plus_figure_20261003/balance_check_coverage.json',
        runner='research_20261003/balance_audit/check_both_diet_sources.py',
        policy='Every later completed balance review must cover both cases and report missing coverage; never treat partial or skipped hybrid checks as passing.'))
    assert all(sha(Path(p))==h for p,h in before.items())
    assert [r['group_id'] for r in wet_checks if r['nonpositive_wet_residual']]==[7]
    assert [r['group_id'] for r in carbon_lower_bounds if r['R_carbon_lower_bound_GS_0p2'][0]!='-' and D(r['R_carbon_lower_bound_GS_0p2'])>0]==[7,11]

(OUT/'README.md').write_text('''# Text-plus-figure balance case

This separate case preserves the complete Figure9 observations and all primary2019 prose feeding constraints. It adds the text-established copepod→smelt link and chaetognath cannibalism as source evidence. Smelt wet DC4=.407,DC5=.461 leaves.132 unallocated; cannibalism's printed2.0% has an ambiguous denominator and is not adopted as DC.

This is an incomplete constraint dataset, not a balanced or selected model. Source diet fractions, grouped prey and rounded quantities can conflict with Figure-derived fractions; both observations are preserved for explicit reconciliation. Unspecified remainders are not zeros. No complete hybrid model.json or forced normalization is generated.

BALANCE_CHECK_INPUTS.json at the model root requires both figure_only and text_plus_figure cases in later balance reviews. balance_check_coverage.json records the initial partial checks:9 wet source-Q energy diagnostics and5 known-prey carbon lower-bound checks. Full-network predation,detritus and native-model load checks remain incomplete.

The direct-source Q removes the hyperiid wet energy failure. Chaetognath wet R is−.2milliontonnes/year using Table3B×PB and proseQ320, a small source/currency discrepancy; its quantified copepod carbon intake alone yields positive energy residual. Smelt's quantified text prey also yields a positive carbon lower-bound residual. These results do not establish global balance.
''',encoding='utf-8')
print(json.dumps(dict(required_case_ids=result['mandatory_case_ids'],partial_combined_checks_saved=True,
    wet_source_Q_checks=len(wet_checks),carbon_lower_bound_checks=len(carbon_lower_bounds),
    full_combined_balance_passed=None,source_inputs_unchanged=True),indent=2))
