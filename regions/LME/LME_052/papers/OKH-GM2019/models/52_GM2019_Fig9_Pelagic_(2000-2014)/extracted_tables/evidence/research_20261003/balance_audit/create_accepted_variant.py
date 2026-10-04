"""Save accepted researcher readings and traced corrections as a new variant.

The original extraction remains immutable. This program recomputes diets and
budget diagnostics; it does not fit source values or claim an EwE load/balance.
"""
from pathlib import Path
from collections import defaultdict, Counter
from decimal import Decimal, localcontext
from datetime import datetime, timezone
import copy, csv, hashlib, json, os

WORK = Path(__file__).resolve().parent
HERE = WORK.parents[1]
ROOT = HERE.parents[3]
PAPERS = HERE.parents[1] / 'papers/OKH-GM2019'
OUT = HERE / 'assumption_variants/researcher_readings_20261003'
OUT.mkdir(parents=True, exist_ok=True)
D = Decimal
CONSUMERS = list(range(2, 22))

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def literal(value):
    return format(value, 'f') if value is not None else None

protected = [HERE / name for name in ['model.json', 'carbon_reconstruction.json',
    'carbon_label_hypothesis.json', 'READINESS.json', 'DC_reconstruction_review.xlsx',
    'audit/flow_readings.json', 'audit/table3_source_readings.json',
    'extracted_tables/extraction.json', 'assumption_variants/user_defaults_20261003/model.json']]
protected += list(PAPERS.glob('*.pdf'))
protected += [ROOT / 'regions/LME_052/models/52_1_Sea_of_Okhotsk_NE_(1980)/model.json']
before = {str(p): sha(p) for p in protected}
baseline = read(HERE / 'carbon_reconstruction.json')
source_flows = read(HERE / 'audit/flow_readings.json')
table = {row['figure_group_id']: row for row in read(HERE / 'audit/table3_source_readings.json')
         if row['figure_group_id'] is not None}
proposals = read(HERE / 'research_20261003/arrow_audit/proposed_route_changes.json')
model = read(HERE / 'assumption_variants/user_defaults_20261003/model.json')
ext = read(HERE / 'assumption_variants/user_defaults_20261003/extraction.json')
assumptions = read(HERE / 'assumption_variants/user_defaults_20261003/assumptions.json')
names = {g['n']: g['name'] for g in baseline['groups']}
factors = {n: D(t['wet_per_carbon']) for n, t in table.items()}
factors[2] = D('9.4')

decisions = {
    'recorded_utc': datetime.now(timezone.utc).isoformat(),
    'baseline_source_readings_preserved': True,
    'human_readings': {
        'F62': {'preferred': '0.023', 'alternative': '0.025',
            'basis': 'Direct researcher answer on 2026-10-03: final digit 3 or 5, prefers 3',
            'route_confirmed_by_human_reading': False},
        'F67': {'adopted': '0.05', 'basis': 'Direct researcher answer on 2026-10-03',
            'route_confirmed_by_human_reading': False}},
    'route_changes': proposals['proposals'],
    'bacteria_conversion': {'wet_per_carbon': '9.4', 'basis': 'Explicit supporting source, not a separate 2019 row',
        'source': Path(os.path.relpath(PAPERS / 'gorbatenko_2018_dissertation.pdf', OUT)).as_posix(),
        'source_printed_page': 60, 'source_pdf_page_1_based': 60,
        'source_sha256': sha(PAPERS / 'gorbatenko_2018_dissertation.pdf'),
        'verification': 'Parent independently checked original text and rendered page'},
    'protozoa_conversion': {'adopted': None, 'sensitivity_candidate': '10',
        'basis': 'Dissertation p60 270 wet / 27 C implies 10, but conflicts with its whole-Sea total; not adopted'},
    'detritus_conversion': {'adopted': None, 'basis': 'No justified factor recovered'},
    'inherited_user_assumptions': 'Copied from ../user_defaults_20261003/assumptions.json',
    'source_parameters_adjusted_to_force_balance': False,
    'selected_model_changed': False,
}

flows = copy.deepcopy(source_flows)
for f in flows:
    f['baseline_note'] = f['note']
    f['baseline_source_reference'] = f['source_pdf']
    f['source_pdf'] = Path(os.path.relpath(PAPERS / 'gorbatenko_melnikov_2019.pdf', OUT)).as_posix()
    f['baseline_route'] = {k: f[k] for k in ['prey_id', 'consumer_id', 'routing_status']}
    f['adopted_carbon_flow'] = f['readable_carbon_flow']
    f['numeric_basis'] = 'Readable source label'
    if f['flow_id'] in decisions['human_readings']:
        h = decisions['human_readings'][f['flow_id']]
        f['adopted_carbon_flow'] = h.get('preferred', h.get('adopted'))
        f['numeric_basis'] = h['basis']
        f['routing_status'] = 'tentative'
        f['alternative_carbon_flow'] = h.get('alternative')
        f['note'] = 'Numeric value adopted from researcher reading; source route remains tentative.'
    for proposal in proposals['proposals']:
        if proposal['flow_id'] == f['flow_id']:
            f.update(proposal['proposed'])
            f['route_basis'] = proposal['justification']
            f['route_audit'] = '../../research_20261003/arrow_audit/proposed_route_changes.json'
            f['note'] = 'Route independently retraced; see route_basis and preserved baseline_note.'
    f['prey'], f['consumer'] = names[f['prey_id']], names[f['consumer_id']]

def calculate(flow_records):
    pairs = defaultdict(list)
    for f in flow_records:
        pairs[f['prey_id'], f['consumer_id']].append(f)
    carbon, wet, dcc, dcw, qc, qw = {}, {}, {}, {}, {}, {}
    for j in CONSUMERS:
        for i in range(1, 23):
            fs = pairs.get((i, j), [])
            c = sum((D(f['adopted_carbon_flow']) for f in fs), D(0))
            carbon[i, j] = c
            wet[i, j] = D(0) if not fs else c * factors[i] if i in factors else None
        qc[j] = sum((carbon[i, j] for i in range(1, 23)), D(0))
        qw[j] = sum((wet[i, j] for i in range(1, 23)), D(0)) if all(wet[i, j] is not None for i in range(1, 23)) else None
        positive_wet = [i for i in range(1, 23) if wet[i, j] != 0]
        for i in range(1, 23):
            dcc[i, j] = carbon[i, j] / qc[j]
            w = wet[i, j]
            dcw[i, j] = D(0) if w == 0 else D(1) if len(positive_wet) == 1 else w / qw[j] if w is not None and qw[j] is not None else None
    return pairs, carbon, wet, dcc, dcw, qc, qw

def diet_dict(matrix):
    return {str(j): {str(i): literal(matrix[i, j]) for i in range(1, 23)} for j in CONSUMERS}

def write_matrix(path, matrix):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\r\n')
        writer.writerow(['Prey ID', 'Prey'] + [f'{j} {names[j]}' for j in CONSUMERS])
        for i in range(1, 23):
            writer.writerow([i, names[i]] + [literal(matrix[i, j]) for j in CONSUMERS])

with localcontext() as context:
    context.prec = 40
    pairs, carbon, wet, dcc, dcw, qc, qw = calculate(flows)
    cells = [dict(prey_id=i, consumer_id=j, flow_ids=[f['flow_id'] for f in pairs.get((i, j), [])],
        carbon_flow=literal(carbon[i, j]), wet_flow=literal(wet[i, j]),
        carbon_dc=literal(dcc[i, j]), wet_dc=literal(dcw[i, j]),
        basis='No displayed arrow: user instructed zero' if not pairs.get((i, j)) else 'Adopted readings; route confidence recorded separately')
        for j in CONSUMERS for i in range(1, 23)]
    budgets = []
    for n in range(1, 22):
        pc = D(baseline['groups'][n-1]['figure_production_carbon_million_t_per_year'])
        mc = sum((carbon[n, j] for j in CONSUMERS), D(0))
        clear_mc = sum((D(f['adopted_carbon_flow']) for f in flows if f['prey_id'] == n and f['routing_status'] == 'clear'), D(0))
        tw = table.get(n)
        pw = D(tw['biomass_wet_million_t']) * D(tw['pb_per_year']) if tw else None
        mw = sum((wet[n, j] for j in CONSUMERS), D(0)) if all(wet[n, j] is not None for j in CONSUMERS) else None
        rc = D('.8') * qc[n] - pc if n in CONSUMERS else None
        rw = D('.8') * qw[n] - pw if n in CONSUMERS and qw[n] is not None and pw is not None else None
        budgets.append(dict(group_id=n, group=names[n], figure_P_carbon=literal(pc), Q_carbon=literal(qc.get(n)),
            respiration_carbon_GS_0p2=literal(rc), energy_failure_carbon=rc is not None and rc <= 0,
            P_wet_from_B_times_PB=literal(pw), Q_wet=literal(qw.get(n)),
            respiration_wet_GS_0p2=literal(rw), energy_failure_wet=rw is not None and rw <= 0,
            predation_carbon=literal(mc), predation_clear_lower_bound_carbon=literal(clear_mc),
            predation_over_figure_P=literal(mc/pc), predation_failure_carbon=mc > pc,
            clear_predation_already_exceeds_figure_P=clear_mc > pc,
            predation_over_wet_P=literal(mw/pw) if mw is not None and pw is not None else None,
            predation_failure_wet=mw is not None and pw is not None and mw > pw))
    for g, b in zip(model['group'], ext['groups']):
        n = b['n']
        if n in CONSUMERS:
            for cell in g['diet_descr']['diet']:
                value = literal(dcw[int(cell['prey_seq']), n])
                cell['proportion'] = '-9999' if value is None else value
            ext['diet'][str(n)] = {**diet_dict(dcw)[str(n)], 'import': '0'}
            b['qb'] = literal(qw[n] / D(table[n]['biomass_wet_million_t'])) if n in table and qw[n] is not None else None
            g['qb'] = b['qb'] if b['qb'] is not None else '-9999'
            g['qb_input'] = 'true' if b['qb'] is not None else 'false'
    carbon_dataset = copy.deepcopy(baseline)
    carbon_dataset.update(variant='researcher_readings_20261003', status='PROVISIONAL_NOT_BALANCED',
        flows=flows, diet=diet_dict(dcc), decisions_file='accepted_decisions.json')
    carbon_dataset['duplicate_pair_flags'] = [dict(prey_id=i, consumer_id=j, flow_ids=[f['flow_id'] for f in fs],
        status='Unresolved route hypotheses; summed labels not independently verified as one author pair')
        for (i, j), fs in pairs.items() if len(fs) > 1]
    alt_flows = copy.deepcopy(flows)
    next(f for f in alt_flows if f['flow_id'] == 'F62')['adopted_carbon_flow'] = '0.025'
    _, ac, aw, adc, adw, aqc, aqw = calculate(alt_flows)
    sensitivity = dict(status='RESEARCHER_SPECIFIED_ALTERNATIVE_NOT_SELECTED', F62='0.025', F67='0.05',
        change_from_preferred=dict(baleen_Q_carbon=literal(aqc[18]-qc[18]), baleen_Q_wet=literal(aqw[18]-qw[18])),
        baleen_Q_carbon=literal(aqc[18]), baleen_Q_wet=literal(aqw[18]),
        baleen_QB_wet=literal(aqw[18]/D(table[18]['biomass_wet_million_t'])),
        diet_carbon=diet_dict(adc), diet_wet=diet_dict(adw),
        limits='Routes, stocks and production unchanged. Cannot repair any current energy failure.')
    readiness = dict(status='BLOCKED', user_readiness_gate='Loadable and balanced before researcher validation',
        native_Ecopath_load_tested=False, balanced=False, ready_for_researcher_validation=False,
        unresolved_numeric_label_ids=[], researcher_preferred_reading_alternative={'F62': ['0.023', '0.025']},
        route_status_counts=dict(Counter(f['routing_status'] for f in flows)),
        carbon_complete_columns=sum(all(dcc[i,j] is not None for i in range(1,23)) for j in CONSUMERS),
        wet_complete_columns=sum(all(dcw[i,j] is not None for i in range(1,23)) for j in CONSUMERS),
        incomplete_wet_diet_group_ids=[j for j in CONSUMERS if any(dcw[i,j] is None for i in range(1,23))],
        missing_living_biomass_group_ids=[2,3], missing_living_PB_group_ids=[2,3],
        missing_consumer_QB_in_figure_variant=[g['n'] for g in ext['groups'] if g['n'] in CONSUMERS and g['qb'] is None],
        prose_recoverable_QB_ids=[4,5], unknown_wet_conversion_prey_ids=[3,22],
        carbon_energy_failure_ids=[b['group_id'] for b in budgets if b['energy_failure_carbon']],
        wet_energy_failure_ids=[b['group_id'] for b in budgets if b['energy_failure_wet']],
        carbon_predation_failure_ids=[b['group_id'] for b in budgets if b['predation_failure_carbon']],
        clear_carbon_predation_failure_ids=[b['group_id'] for b in budgets if b['clear_predation_already_exceeds_figure_P']],
        living_catch_BA_net_migration='Not identified; zero only in labeled predation/P diagnostics',
        detritus_BA='Uncomputed residual, not assumed zero',
        source_values_adjusted_to_force_balance=False)
    model['_reconstruction'].update(status='BLOCKED_RESEARCHER_READINGS_VARIANT', variant='researcher_readings_20261003',
        accepted_decisions_file='accepted_decisions.json', unresolved_label_readings=[],
        tentative_routes=readiness['route_status_counts']['tentative'], unknown_wet_conversion_prey_ids=[3,22],
        ee_gs_catches_ba_migration_and_routing_not_estimated=False,
        ee_catches_living_ba_migration_not_estimated=True,
        limitations='20/20 carbon and 18/20 wet diets are numerically identifiable under adopted routes; missing basic inputs, uncertain routes and balance failures remain. Native EwE load untested.')
    ext.update(variant='researcher_readings_20261003', overprinted_label_values_not_adopted=False,
        adopted_human_readings=decisions['human_readings'], adopted_cross_source_conversion={'2':'9.4'},
        readiness=readiness)
    assumptions.update(diet_and_conversion_changes='F62=.023, alternative .025; F67=.05; F77 source corrected to15; F13/F22 confidence upgrades; bacteria9.4 from dissertationp60. All recorded separately.',
        ready=False, variant='researcher_readings_20261003')
    for filename, obj in [('accepted_decisions.json', decisions), ('flow_readings.json', flows),
        ('diet_cell_ledger.json', cells), ('flow_budget_checks.json', budgets), ('model.json', model),
        ('extraction.json', ext), ('assumptions.json', assumptions), ('carbon_reconstruction.json', carbon_dataset),
        ('F62_0p025_sensitivity.json', sensitivity), ('READINESS.json', readiness)]:
        save(OUT / filename, obj)
    for filename, matrix in [('Food_flows_carbon.csv', carbon), ('Food_flows_wet.csv', wet),
        ('Diet_composition_carbon.csv', dcc), ('Diet_composition_wet.csv', dcw)]:
        write_matrix(OUT / filename, matrix)
    factor_records = [dict(group_id=n, group=names[n], wet_per_carbon=literal(factors.get(n)),
        basis='Dissertation p60, explicit supporting-source factor' if n==2 else '2019 Table3' if n in table else 'Unknown',
        mapping_tentative=n==20) for n in range(1,23)]
    save(OUT / 'conversion_factors.json', factor_records)
    assert len(flows)==78 and len(cells)==440 and len(model['group'])==22
    assert sum(not c['flow_ids'] for c in cells)==365
    assert all(c['carbon_dc']=='0' and c['wet_dc']=='0' for c in cells if not c['flow_ids'])
    for j in CONSUMERS:
        assert abs(sum(dcc[i,j] for i in range(1,23))-1) < D('1e-35')
        if all(dcw[i,j] is not None for i in range(1,23)):
            assert abs(sum(dcw[i,j] for i in range(1,23))-1) < D('1e-35')
    assert readiness['carbon_complete_columns']==20 and readiness['wet_complete_columns']==18
    assert readiness['incomplete_wet_diet_group_ids']==[4,5]
    assert readiness['carbon_energy_failure_ids']==[6,8,14]
    assert readiness['wet_energy_failure_ids']==[6,7,8,14]
    assert readiness['clear_carbon_predation_failure_ids']==[11,13,16]
    assert next(f for f in flows if f['flow_id']=='F77')['prey_id']==15
    assert len([f for f in flows if f['readable_carbon_flow'] is None])==2
    baseline_assumed = read(HERE / 'assumption_variants/user_defaults_20261003/model.json')
    for old, new in zip(baseline_assumed['group'], model['group']):
        assert all(old[k]==new[k] for k in ['biomass','pb','ee','gs','biomass_accum','immigration','emigration','export'])
        if old['group_seq'] != '18':
            assert old['qb']==new['qb']
    assert all(sha(Path(p))==h for p,h in before.items())
    verification=dict(artifact_arithmetic_passed=True, biological_balance_passed=False,
        unknown_values_preserved=True, protected_original_hashes_unchanged=before,
        groups=22, consumers=20, flow_labels=78, diet_cells=440, missing_arrow_zero_cells=365,
        complete_carbon_diets=20, complete_wet_diets=18,
        accepted_human_readings={'F62':'0.023','F67':'0.05'}, F62_alternative_preserved='0.025',
        F77_corrected_source=15, unchanged_original_B_and_PB=True,
        only_changed_input_QB_group_id=18, native_EwE_load_tested=False, model_ready=False)
    save(OUT / 'verification.json', verification)

print(json.dumps({'output':str(OUT), 'readiness':readiness,
    'baleen_Q_carbon':literal(qc[18]), 'baleen_Q_wet':literal(qw[18]),
    'baleen_QB_wet':ext['groups'][17]['qb']}, ensure_ascii=False, indent=2))
