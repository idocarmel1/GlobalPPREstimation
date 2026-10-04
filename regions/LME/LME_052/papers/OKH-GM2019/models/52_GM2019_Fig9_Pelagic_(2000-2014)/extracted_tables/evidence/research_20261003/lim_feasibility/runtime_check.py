"""Bounded source-preserving LIM experiment; never edits adopted model inputs.

Run from the repository root with the existing scientific Miniconda interpreter.
The carbon fixture fixes published Figure 9 P/Q, not microbial native B/PB.
The native wet fixture remains incomplete for microbial basics/detritus currency.
Neither fixture is a validated model, and the legacy balanced copy is audited
separately because that routine can violate the user's zero-migration constraint.
"""
from pathlib import Path
from decimal import Decimal, getcontext
from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
import hashlib
import io
import json
import math
import sys
import warnings

getcontext().prec = 40
HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parents[1]
ROOT = next(p for p in HERE.parents if (p / 'Project.xlsx').exists())
SOURCE = CANDIDATE / 'assumption_variants/researcher_readings_20261003'
OUT = HERE / 'runtime'
OUT.mkdir(exist_ok=True)
ENGINE = ROOT / 'tools/scientific_code/PPREstimation'
sys.path.insert(0, str(ENGINE))
import numpy as np
import pandas as pd
import scipy
from PPRCalculator import PPRCalculator


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def clean(x):
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, (np.integer, np.floating, np.bool_)):
        x = x.item()
    if isinstance(x, float) and not math.isfinite(x):
        return None
    return x


def save(name, obj):
    (OUT / name).write_text(json.dumps(clean(obj), ensure_ascii=False,
                           indent=2, allow_nan=False) + '\n', encoding='utf-8')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


protected = [SOURCE / f for f in ['model.json', 'extraction.json',
             'carbon_reconstruction.json', 'conversion_factors.json']]
protected += [CANDIDATE / 'model.json', ROOT / 'Project.xlsx',
              ROOT / 'regions/LME_052/models/52_1_Sea_of_Okhotsk_NE_(1980)/model.json']
hashes_before = {str(p.relative_to(ROOT)): sha(p) for p in protected}
carbon = read(SOURCE / 'carbon_reconstruction.json')
factors = read(SOURCE / 'conversion_factors.json')
for row in factors:
    if row['group_id'] == 3:
        row.update(wet_per_carbon='10.0', basis='User-authorized best estimate; '
                   'dissertation p.60 paired 270 wet / 27 carbon, with wording/scope caveats',
                   assumed=True,
                   evidence='../audit/protozoa_factor_10_primary_confirmation.json')
factor = {r['group_id']: Decimal(r['wet_per_carbon'])
          if r['wet_per_carbon'] is not None else None for r in factors}
save('conversion_factors.json', factors)
names = {g['n']: g['name'] for g in carbon['groups']}
flow = {c: {p: Decimal(0) for p in names} for c in carbon['consumers']}
for f in carbon['flows']:
    flow[f['consumer_id']][f['prey_id']] += Decimal(f['adopted_carbon_flow'])
q_carbon = {c: sum(row.values()) for c, row in flow.items()}
q_wet = {}
wet_diet = {}
for c, row in flow.items():
    unknown = [p for p, v in row.items() if v and factor[p] is None]
    q_wet[c] = None if unknown else sum(v * factor[p] for p, v in row.items() if v)
    if q_wet[c] is not None:
        wet_diet[c] = {p: (v * factor[p] / q_wet[c] if v else Decimal(0))
                       for p, v in row.items()}
    elif len([v for v in row.values() if v]) == 1:
        # A single-prey diet is exactly 1 even when absolute wet intake is unknown.
        wet_diet[c] = {p: Decimal(int(v != 0)) for p, v in row.items()}
    else:
        raise ValueError('Unknown prey conversion prevents a complete wet diet')
assert len(wet_diet) == 20
assert all(abs(sum(r.values()) - 1) < Decimal('1e-35') for r in wet_diet.values())

settings = dict(underdetermined=True, zero_catch=True, zero_biomass_accum=False,
                default_gs=False, weight_flow=1., weight_guess=1.,
                normalize_DC=False, balance_BA_after_DC_normalization=False)
assumptions = {
    'protozoa_tonnes_wet_per_tonne_carbon': '10.0',
    'protozoa_factor_status': 'Best estimate authorized by researcher; not a recovered coefficient',
    'catch': 0, 'immigration': 0, 'emigration': 0, 'net_migration': 0,
    'GS': 'Unknown and optimized, not supplied as 0.2',
    'living_biomass_accumulation': 'Unknown/free; zero is not assumed',
    'detritus_import': 0, 'detritus_export': 0,
    'mortality_and_egestion_to_detritus': '100% for each living group',
    'detritus_biomass_accumulation': 'Residual of inflow and consumption',
    'LIM_GS_bounds': [0.10, 0.35], 'LIM_EE_bounds': [0, 0.95],
    'accepted_source_decisions': {'F62': '0.023 (alternative 0.025 retained)',
                                'F67': '0.05', 'F77_prey': 15},
    'runtime_settings': settings,
    'scientific_model_ready': False,
}
save('assumptions.json', assumptions)

# Native wet input: preserve original source B and PB, complete only authorized
# conversion/catch/migration/GS fields and Figure-derived diets/QB where possible.
native = deepcopy(read(SOURCE / 'model.json'))
area = Decimal(str(native['_reconstruction']['area_km2']))
changes = []
for g in native['group']:
    n = int(g['group_seq'])
    for key in ['export', 'immigration', 'emigration', 'detritus_import']:
        old = g.get(key)
        g[key] = '0'
        changes.append({'group': n, 'field': key, 'before': old, 'after': '0',
                        'basis': 'Latest researcher zero assumption'})
    if n in carbon['consumers']:
        old = g.get('gs')
        g['gs'] = '-9999'
        changes.append({'group': n, 'field': 'gs', 'before': old, 'after': '-9999',
                        'basis': 'GS free for standard runtime LIM'})
        b = Decimal(g['biomass'])
        if b != Decimal('-9999') and q_wet[n] is not None:
            old = g['qb']
            g['qb'] = str(q_wet[n] * Decimal(1000000) / (area * b))
            g['qb_input'] = 'true'
            changes.append({'group': n, 'field': 'qb', 'before': old, 'after': g['qb'],
                            'basis': 'Sum accepted Figure flows multiplied by prey wet/C factor / source stock'})
        for cell in g['diet_descr']['diet']:
            p = int(cell['prey_seq'])
            old = cell['proportion']
            cell['proportion'] = str(wet_diet[n][p])
            if old != cell['proportion']:
                changes.append({'group': n, 'field': 'diet', 'prey': p,
                                'before': old, 'after': cell['proportion']})
    for cell in (g.get('diet_descr') or {}).get('diet', []):
        cell['detritus_fate'] = '1' if int(cell['prey_seq']) == 22 else '0'
native['_reconstruction'].update(
    status='COMPUTATIONAL_LIM_TEST_INPUT_NOT_BALANCED', selected=False,
    unknown_wet_conversion_prey_ids=[22],
    latest_assumptions='assumptions.json',
    computational_input_limit='Unknown bacterial/protozoan native B/PB/QB and '
                              'detritus wet/C remain missing; Figure microbial P/Q '
                              'not stored in native basic fields')
save('native_wet_input.json', native)
save('transformation_ledger.json', changes)
save('converted_intakes.json', [{'group_id': c, 'group': names[c],
    'carbon_million_t_per_year': str(q_carbon[c]),
    'wet_million_t_per_year': str(q_wet[c]) if q_wet[c] is not None else None,
    'wet_diet': {str(p): str(v) for p, v in wet_diet[c].items()}}
    for c in carbon['consumers']])

# Source-flow fixture: all Figure living P and consumer Q are explicitly fixed.
# Known stocks use Table 3 wet B / wet:C; unknown microbial stocks remain NaN,
# then standard runtime's biomass=1 fallback is logged, not adopted as biology.
table = read(CANDIDATE / 'audit/table3_source_readings.json')
known_b = {r['figure_group_id']: float(Decimal(r['biomass_wet_million_t']) /
          Decimal(r['wet_per_carbon'])) for r in table if r['figure_group_id'] is not None}
rows = []
for g in carbon['groups']:
    n = g['n']
    p = g.get('figure_production_carbon_million_t_per_year')
    rows.append(dict(group_seq=n, group_name=names[n],
        trophic_info='PP' if n == 1 else ('DET' if n == 22 else 'Regular'),
        biomass=known_b.get(n, np.nan), p=float(p) if p is not None else np.nan,
        q=float(q_carbon[n]) if n in q_carbon else np.nan,
        M0=np.nan, ee=np.nan, gs=np.nan, respiration=np.nan, egestion=np.nan,
        biomass_accum=np.nan, catch=0., immigration=0., emigration=0.,
        net_migration=0., detritus_import=0., tl=np.nan))
rows.append(dict(group_seq=23, group_name='diet_import', trophic_info='Import',
    biomass=1., p=1., q=1., M0=0., ee=1., gs=0., respiration=0., egestion=0.,
    biomass_accum=0., catch=0., immigration=0., emigration=0., net_migration=0.,
    detritus_import=0., tl=1.))
df = pd.DataFrame(rows).set_index('group_seq')
dc = pd.DataFrame(0., index=df.index, columns=df.index)
for c in carbon['consumers']:
    for p, v in carbon['diet'][str(c)].items():
        dc.loc[c, int(p)] = float(v)
fate = pd.DataFrame({22: [1. if n <= 22 else 0. for n in df.index]}, index=df.index)
seed = dict(_groups_df=df, _DC=dc, _det_fate=fate,
            seq2name=df.group_name.to_dict(),
            name2seq={name: n for n, name in df.group_name.items()})
save('fixed_carbon_seed.json', {'group_rows': rows,
    'DC_orientation': 'consumer rows, prey columns', 'DC': dc.to_dict('index'),
    'detritus_fate': fate.to_dict('index'), 'units': 'million tC and million tC/year',
    'native_model': False, 'microbial_B_PB_guesses_adopted': False})


def snapshot(calc):
    balanced, prod, cons = calc.is_model_balanced()
    table = calc.get_groups_df()
    records = []
    for n in sorted(calc.p.index):
        records.append(dict(group_id=int(n), group=calc.seq2name[n],
            P=calc.p.loc[n], Q=calc.q.loc[n], catch=calc.catch.loc[n],
            immigration=calc.immigration.loc[n], emigration=calc.emigration.loc[n],
            net_migration=calc.net_migration.loc[n], BA=calc.growth.loc[n],
            mortality=calc.M0.loc[n], respiration=calc.respiration.loc[n],
            egestion=calc.egestion.loc[n], predation=calc.predation.loc[n],
            detritus_export=calc.det_export.loc[n],
            GS_vector=calc.GS.loc[n], EE_vector=calc.EE.loc[n],
            GS_table=table.loc[n, 'gs'], EE_table=table.loc[n, 'ee'],
            table_unsolved_fields=[k for k in ['p','q','respiration','egestion','M0','biomass_accum']
                                   if pd.isna(table.loc[n, k])],
            production_residual=prod.loc[n]-calc.p.loc[n],
            consumption_residual=cons.loc[n]-calc.q.loc[n]))
    return clean(dict(algebraic_balance=bool(balanced), rows=records,
        catch_zero=bool((calc.catch.abs() < 1e-9).all()),
        migration_zero=bool((calc.net_migration.abs() < 1e-9).all()),
        immigration_zero=bool((calc.immigration.abs() < 1e-9).all()),
        emigration_zero=bool((calc.emigration.abs() < 1e-9).all()),
        detritus_export_zero=bool((calc.det_export.abs() < 1e-9).all())))


results = {}
for name, constructor in [
    ('native_wet', lambda: PPRCalculator(str(OUT / 'native_wet_input.json'), **settings)),
    ('fixed_figure_carbon', lambda: PPRCalculator.from_dict(deepcopy(seed), **settings))]:
    log = io.StringIO()
    with redirect_stdout(log), redirect_stderr(log), warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            calc = constructor()
            result = dict(constructor='SUCCESS', main=snapshot(calc),
                          legacy_balanced_copy=snapshot(calc.balanced_model))
            if name == 'fixed_figure_carbon':
                result['living_P_preserved'] = all(np.isclose(calc.p.loc[n], df.loc[n,'p'])
                                                  for n in range(1,22))
                result['consumer_Q_preserved'] = all(np.isclose(calc.q.loc[n], float(q_carbon[n]))
                                                     for n in carbon['consumers'])
                result['living_flow_preserved'] = all(np.isclose(calc.q.loc[c] * calc._DC.loc[c,p], float(v))
                    for c, r in flow.items() for p, v in r.items())
            result['biomass_fallback_groups'] = [2,3,22]
            result['valid_complete_model'] = False
            result['missing_GS_or_EE_is_not_runtime_fallback_zero_or_one'] = True
        except Exception as exc:
            result = dict(constructor='EXCEPTION', exception_type=type(exc).__name__, exception=str(exc),
                          valid_complete_model=False)
    result['warnings'] = [str(w.message) for w in caught]
    (OUT / (name + '.log')).write_text(log.getvalue(), encoding='utf-8')
    results[name] = result
    save(name + '_result.json', result)

required = read(CANDIDATE / 'BALANCE_CHECK_INPUTS.json')
coverage = dict(required_case_contract='../../../BALANCE_CHECK_INPUTS.json',
    figure_only=dict(status='EXECUTED_NATIVE_WET_AND_FIXED_CARBON_LIM',
                     valid_balanced_model=False, results=list(results)),
    text_plus_figure=dict(status='PARTIAL_ENERGY_AND_EE_BA_CHECKS_COMPLETED; FULL_RUNTIME_NOT_RUN',
        reason='Primary text diets contain unallocated prey and pooled microbial/squid categories; '
               'a full 22-group DC matrix is not identified. Missing remainders are unknown, not zero.',
        evidence=['../audit/text_plus_figure_wet_GS_intervals.json',
                  '../audit/text_plus_figure_carbon_lower_bound_constraints.json'],
        valid_balanced_model=False),
    required_cases_found=required,
    GS_EE_complete_valid_vector_available=False)
save('case_coverage.json', coverage)
hashes_after = {str(p.relative_to(ROOT)): sha(p) for p in protected}
assert hashes_before == hashes_after
verification = dict(protected_inputs_unchanged=True, hashes=hashes_after,
    input_wet_diet_columns=20, input_GS_all_consumers_missing=True,
    engine_hashes={p.name: sha(p) for p in [ENGINE/'PPRCalculator.py', ENGINE/'ModelData.py', ENGINE/'utils.py']},
    interpreter=sys.executable, scipy_version=scipy.__version__,
    runtime_complete=True, scientific_model_ready=False)
save('verification.json', verification)
for name, result in results.items():
    print(name, result['constructor'])
    if result['constructor'] == 'SUCCESS':
        main = result['main']
        print(' main algebraic balance:', main['algebraic_balance'], 'migration zero:', main['migration_zero'])
        print(' unresolved groups:', [r['group_id'] for r in main['rows'] if r['table_unsolved_fields']])
        print(' legacy balance:', result['legacy_balanced_copy']['algebraic_balance'],
              'migration zero:', result['legacy_balanced_copy']['migration_zero'])
print('Protected source/candidate/selected-model/workbook inputs unchanged.')
