"""Reconcile the three independent source investigations without adopting repairs."""
from pathlib import Path
from decimal import Decimal as D, getcontext
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent
getcontext().prec = 50
CANDIDATE = HERE.parents[1]
ROOT = next(p for p in HERE.parents if (p / 'Project.xlsx').exists())


def read(rel):
    return json.loads((HERE / rel).read_text(encoding='utf-8'))


def write(rel, data):
    (HERE / rel).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


salmon = read('hyperiid_salmon/salmon_carbon_energy_bounds.json')
hyper = read('hyperiid_salmon/hyperiid_text_plus_figure_constraints.json')
jelly = read('jellyfish_text_diet/summary.json')
errors = read('jellyfish_error_audit/jellyfish_error_hypothesis_ledger.json')
assert len(errors['hypotheses']) == 16
for case in salmon:
    actual = sum(D(c['Q_million_tC']) for c in case['components'])
    assert abs(actual - D(case['known_carbon_Q_lower_bound'])) < D('1e-35')
    assert actual * D('.9') - D('.105') > 0
qj = D(jelly['mixed_2019_anchor_known_carbon_Q_lower_bound_million_tC_per_year'])
assert qj * D('.7') - D('.144') > 0
assert D(jelly['strict_missing_factor_wet_thousand_t']) == D('297.4')
assert jelly['combined_Q_thousand_wet_t'] == '3177.1'

source_checks = {}
expected = {
    'gorbatenko_melnikov_2019.pdf': '70b73d4341018e3fadb9955e9d19735188f12c8798eaed8921d1812bb6c2b860',
    'gorbatenko_2018_dissertation.pdf': 'a26ef69acf1c00b32f49772e52b66f85baa79cf1e0ba3fecefe3800827787d45'}
papers = ROOT / 'regions/LME_052/papers/OKH-GM2019'
for name, expected_hash in expected.items():
    source_checks[name] = sha(papers / name) == expected_hash
assert all(source_checks.values())
protected = json.loads((CANDIDATE / 'research_20261003/lim_feasibility/runtime/verification.json').read_text('utf-8'))['hashes']
assert all(sha(ROOT / rel) == digest for rel, digest in protected.items())

constraints = {
    'schema_version': 1,
    'status': 'SOURCE_FEEDING_RECOVERED_PARTIALLY; NOT_A_COMPLETE_MODEL',
    'primary_2019_text_constraints': '../text_feeding_audit/partial_numeric_diets.json',
    'source_Figure_flow_case': '../../assumption_variants/researcher_readings_20261003/carbon_reconstruction.json',
    'native_wet_and_carbon_Figure_LIM_results': '../lim_feasibility/runtime/case_coverage.json',
    'supporting_reconstruction': {
        'salmon': {'source_table': 'hyperiid_salmon/salmon_table_4_52_rows.json',
                   'source_prey_ledger': 'hyperiid_salmon/salmon_group8_prey_ledger.json',
                   'conditional_carbon_energy_cases': salmon,
                   'source_period': '2000-2014', 'complete_native_DC': False},
        'hyperiids': {'source_table': 'hyperiid_salmon/hyperiid_table_4_11.json',
                      'combined_text_Figure_constraints': hyper,
                      'unallocated_wet_food_million_t': '92.8002',
                      'minimum_unallocated_carbon_food_at_GS_0p10': '.947',
                      'source_period': '2000-2014', 'complete_native_DC': False},
        'jellyfish': {'source_tables': 'jellyfish_text_diet/source_tables_4_15_4_16.json',
                      'source_flows_and_conversion_cases': 'jellyfish_text_diet/wet_prey_flows_and_carbon_contributions.json',
                      'source_summary': jelly, 'source_period': '2006-2014',
                      'complete_native_DC': False,
                      'nominal_positive_respiration_at_GS_0p30': True}},
    'common_currency': 'Carbon with prey-specific conversion factors',
    'full_native_run': {'status': 'NOT_RUN_FOR_NEW_SOURCE_RECONSTRUCTION',
        'reason': 'No complete carbon DC/Q: extra prey, unknown conversions and hyperiid Other remain unresolved. '
                  'Partial diets are not normalized or filled with source-false zeros.'},
    'GS_EE_complete_valid_vector': None,
    'production_typo_correction_adopted': False,
    'source_corrections_adopted_into_selected_model': False,
    'researcher_prey_representation_decision': 'Diet imports; retain22 biological groups',
    'remaining_import_gap': 'Some quantified wet import food lacks carbon conversion, so carbon import fractions/totalQ remain unknown.'}
write('candidate_constraints.json', constraints)

coverage = {
    'schema_version': 1,
    'figure_only': {'status': 'EXECUTED; FAILED',
        'native_wet_result': '../lim_feasibility/runtime/native_wet_result.json',
        'fixed_carbon_result': '../lim_feasibility/runtime/fixed_figure_carbon_result.json',
        'LIM_unsolved_groups': [6, 8, 14]},
    'text_plus_figure': {'status': 'PARTIAL_CHECKS_COMPLETED; INCOMPLETE_DC',
        'primary_prose_checks': '../lim_feasibility/audit/text_plus_figure_wet_GS_intervals.json',
        'source_reconstruction_constraints': 'candidate_constraints.json',
        'hypereiid_residual_other_constraint_tested': True,
        'salmon_and_jellyfish_nominal_carbon_energy_feasible': True,
        'complete_balanced_model': False},
    'scientific_model_ready': False,
    'valid_GS_EE_vector_available': False,
    'prey_mean_factors_not_exact_stage_measurements': True,
    'source_Q_not_fully_independent_of_assimilation_growth_assumptions': True}
write('balance_check_coverage.json', coverage)
contract = CANDIDATE / 'BALANCE_CHECK_INPUTS.json'
c = json.loads(contract.read_text('utf-8'))
c['latest_coverage'] = 'research_20261003/source_feeding_repairs/balance_check_coverage.json'
c['supporting_text_feeding_case'] = 'research_20261003/source_feeding_repairs/candidate_constraints.json'
contract.write_text(json.dumps(c, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

currency = read('currency_audit.json')
currency['jellyfish_matched_source_prey_lower_bound']['group_mean_factor_assumptions'] = (
    'Nominal subtotal conditional on published taxonomic group means applying to actual prey/stages; not an unconditional statistical bound.')
currency['jellyfish_matched_source_prey_lower_bound']['GS_0p30_scope'] = (
    'Feasible illustration in carbon; source70% concerns calorie assimilation and requires equivalence for carbon GS.')
write('currency_audit.json', currency)

report = '''# Source feeding recovery and jellyfish error investigation

Text and supporting tables can remove the nominal carbon-energy contradictions for salmon and jellyfish while preserving published production. Hyperiid Other food remains quantitatively unallocated. These are source constraints, not a complete balanced model or solved GS/EE vector.

| Group | Recovered evidence | Energy implication | Remaining diet gap |
|---|---|---|---|
| Salmon III | Full source wet Q 1.79694 million t/year; six converted food categories give nominal carbon Q ≥0.117323–0.133915 million tC/year, depending on recorded factor case | Positive respiration possible at GS=.10 with Figure P=.105; Amphipoda-to-hyperiid aggregate is explicit | Extra prey categories, decapod/gelatinous conversions, fish/squid allocation and rounded0.14kt closure difference |
| Jellyfish | Full source wet Q3.1771 million t/year; accounted carbon Q0.210428 with2019 anchors or0.228011 with seasonal factors | At GS=.30 and P=.144, accounted R is +.003299 or+.015608 million tC/year |297.4kt wet in six categories lack matched factors; some converted prey also lack22-group allocations |
| Hyperiids | Copepod56.7million wet/year =4.05million tC; retain clear Figure euphausiid.283C inside sourceOther95.8million wet | Known Q=4.333C; residual food must contribute more than.947C for positive R atGS=.10 |92.8002million wet/year remain unallocated; residual effective wet/C must be below97.993875 for that energy condition |

Carbon is the common currency. Food is converted with each prey's factor, not the consumer-body factor. Jellyfish wet production41 divided by285.2 equals.1437588 carbon, which rounds to Figure.144; a production decimal correction is unsupported. The audit tested16 hypotheses, including wet/carbon mix-ups, decimals, production/consumption confusion and arrow directions. It found genuine header/content and small rounding inconsistencies, but none establishes a tenfold production/intake correction. The reconstructed Figure intake.0505C is our sum of three tentative routes, not a printed author total.

The jellyfish supporting feeding period is2006–2014; the primary model period is2000–2014. Group-mean chemical factors, prey-stage applicability and source expert estimates remain explicit. Source70% assimilation belongs to a calorie-based ration calculation; GS=.30 in carbon requires an equivalence assumption and is not a solved full-model GS value.

Detailed source tables and checks: [hyperiid/salmon](hyperiid_salmon/FINDINGS.md), [jellyfish diet](jellyfish_text_diet/FINDINGS.md), [16 jellyfish hypotheses](jellyfish_error_audit/FINDINGS.txt). [Coverage](balance_check_coverage.json) retains both mandatory Figure-only and text-plus-Figure cases. [Candidate constraints](candidate_constraints.json) preserve missing carbon food and diet entries as unknown.

The researcher chose diet imports for quantified prey absent from the22-group diagram. Keep22 biological groups and track those food inputs outside the internal prey budgets. Their placement is decided; some carbon conversions and the hyperiid Other composition still need evidence or explicit assumptions. Individual microbial B/PB remain missing. No source production correction, selected model, validation document or map update was made.
'''
(HERE / 'REPORT.md').write_text(report, encoding='utf-8')

write('verification.json', {'source_hashes_unchanged': source_checks,
    'protected_source_candidate_selected_workbook_hashes_unchanged': True,
    'salmon_carbon_components_recomputed': True,
    'jellyfish_nominal_energy_recomputed': True,
    'jellyfish_hypotheses': 16,
    'no_complete_DC_fabricated': True,
    'both_required_cases_covered_with_missing_full_runtime_explicit': True,
    'scientific_model_ready': False})

roles = {'REPORT.md': 'consolidated_findings', 'verification.json': 'parent_verification',
         'candidate_constraints.json': 'source_constraint_dataset',
         'balance_check_coverage.json': 'mandatory_case_coverage',
         'currency_audit.json': 'currency_and_assumption_evidence',
         'hyperiid_salmon/FINDINGS.md': 'hyperiid_salmon_findings',
         'jellyfish_text_diet/FINDINGS.md': 'jellyfish_feeding_findings',
         'jellyfish_error_audit/jellyfish_error_hypothesis_ledger.json': 'error_hypotheses',
         'hyperiid_salmon/verification.json': 'source_cell_verification',
         'jellyfish_text_diet/verification.json': 'source_cell_verification',
         'jellyfish_error_audit/verification.json': 'source_cell_verification'}
artifacts = []
for f in sorted(HERE.rglob('*')):
    if f.is_file() and f.name not in ['evidence_index.json', 'evidence_integrity.json']:
        rel = f.relative_to(HERE).as_posix()
        artifacts.append({'role': roles.get(rel, 'supporting_source_evidence'),
                          'availability': 'present', 'path': rel, 'sha256': sha(f)})
for name in expected:
    f = papers / name
    artifacts.append({'role': 'original_source_pdf', 'availability': 'present',
                      'path': os.path.relpath(f, HERE).replace('\\', '/'), 'sha256': sha(f)})
artifacts.append({'role': 'complete_balanced_model', 'availability': 'missing',
    'reason': 'Source prey categories/conversions and hyperiid Other split are unresolved; no native complete DC is identified.',
    'acquisition_status': 'Source feeding recovery complete for available tables; diet imports chosen and remaining carbon conversions/assumptions needed.'})
write('evidence_index.json', {'schema_version': 1,
    'run_id': 'LME052-GM2019-20261003-SOURCE-FEEDING-RECOVERY', 'region_id': 'LME_052',
    'model_id': CANDIDATE.name, 'variant_id': 'source_supported_constraints_not_native_model',
    'source_identity': expected,
    'computational_input_identity': {'constraints_sha256': sha(HERE/'candidate_constraints.json'),
                                    'settings': '../lim_feasibility/runtime/assumptions.json'},
    'methods': ['Original source feeding-table transcription', 'Independent source-cell and sum checks',
                'Prey-specific carbon energy feasibility bounds', '16 likely-human-error hypotheses'],
    'required_roles': sorted(set(roles.values()) | {'original_source_pdf'}),
    'artifacts': artifacts,
    'reconciliation': {'sources_preserved': True, 'numeric_components_verified': True,
                       'unknown_remainders_preserved': True, 'partial_cases_explicit': True},
    'scientific_model_ready': False})
print('Reconciled source feeding,16 error hypotheses and both mandatory cases.')
print('Protected source/model/workbook hashes unchanged; complete model NOT ready.')
print('Indexed',len(artifacts),'portable artifacts.')
