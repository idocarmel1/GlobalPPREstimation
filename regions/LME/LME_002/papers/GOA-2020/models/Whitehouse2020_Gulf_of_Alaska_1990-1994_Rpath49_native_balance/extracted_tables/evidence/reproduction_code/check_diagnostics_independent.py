"""Read-only independent audit of saved diagnostic evidence; never imports solver code."""
from __future__ import annotations
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

RUN = Path(__file__).resolve().parents[1]
ROOT = RUN.parents[4]
OUT = RUN / 'outputs/diagnostics'
DEST = RUN / 'qa/independent_diagnostics_review.json'
ATOL = RTOL = 1e-12
issues = []
counts = Counter()

def check(ok, label, details=None):
    counts['assertions'] += 1
    if not ok:
        issues.append({'check': label, 'details': details})

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'),
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))

def close(a, b):
    return math.isclose(float(a), float(b), rel_tol=RTOL, abs_tol=ATOL)

def numeric(x):
    if x is None:
        return np.nan
    if isinstance(x, dict) and x.get('type') == 'float':
        return {'nan': np.nan, 'positive_infinity': np.inf,
                'negative_infinity': -np.inf}[x['value']]
    return x

def mask_kind(x):
    if x is None:
        return 'null'
    if isinstance(x, dict) and x.get('type') == 'float':
        return x['value']
    return None

def frame_data(frame):
    return np.array([[numeric(x) for x in row] for row in frame['data']], dtype=float)

def vector(series):
    f = series['frame']
    return {seq: numeric(row[0]) for seq, row in zip(f['index'], f['data'])}

def table(frame):
    return {seq: dict(zip(frame['columns'], row))
            for seq, row in zip(frame['index'], frame['data'])}

def same(a, b, label):
    # Exact types/axes/masks; floating values may differ only within declared tolerance.
    if isinstance(a, dict) and isinstance(b, dict):
        check(set(a) == set(b), label + ':keys')
        for k in set(a) & set(b):
            same(a[k], b[k], label + '/' + str(k))
    elif isinstance(a, list) and isinstance(b, list):
        check(len(a) == len(b), label + ':length')
        for i, (x, y) in enumerate(zip(a, b)):
            same(x, y, label + '/' + str(i))
    elif isinstance(a, (float, int)) and not isinstance(a, bool) and isinstance(b, (float, int)) and not isinstance(b, bool):
        check(close(a, b), label + ':numeric', [a, b] if not close(a, b) else None)
    else:
        check(type(a) == type(b) and a == b, label + ':exact')

def validate_encoded(value, label):
    if isinstance(value, dict):
        if value.get('type') == 'dataframe':
            n, m = value['shape']
            check(len(value['index']) == n and len(value['columns']) == m, label + ':axis_lengths')
            check(len(set(value['index'])) == n and len(set(value['columns'])) == m, label + ':unique_axes')
            check(len(value['dtypes']) == m, label + ':dtypes')
            check(len(value['data']) == n and all(len(r) == m for r in value['data']), label + ':data_shape')
            check(set(value['masks']) == {'null', 'nan', 'positive_infinity', 'negative_infinity'}, label + ':mask_kinds')
            for kind, mask in value['masks'].items():
                check(len(mask) == n and all(len(r) == m for r in mask), label + ':mask_shape/' + kind)
                for i, row in enumerate(value['data']):
                    for j, cell in enumerate(row):
                        check(type(mask[i][j]) == bool and mask[i][j] == (mask_kind(cell) == kind), label + f':mask/{kind}/{i}/{j}')
            counts['encoded_frames_validated'] += 1
            counts['encoded_frame_cells_validated'] += n * m
            return
        if value.get('type') == 'float':
            check(value.get('value') in {'nan', 'positive_infinity', 'negative_infinity'}, label + ':float_tag')
            return
        for k, v in value.items():
            validate_encoded(v, label + '/' + str(k))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            validate_encoded(v, label + '/' + str(i))

identity = read('run_identity.json')
summary = read('diagnostic_summary.json')
audit = read('constructor_audit.json')
raw = read('raw_modeldata_views.json')
ledger = read('scalar_transformation_ledger.json')
for label, obj in [('audit', audit), ('raw', raw), ('ledger', ledger)]:
    validate_encoded(obj, label)
for key in ['parent', 'variant']:
    check(sha(ROOT / identity[key + '_path']) == identity[key + '_sha256'], key + ':canonical_sha256_unchanged')
for rel, expected in identity['code_sha256'].items():
    check(sha(OUT / 'executed_code' / rel) == expected, 'archived_executed_code_sha256:' + rel)
check(summary['identity'] == identity, 'summary_identity')
check(summary['canonical_inputs_unchanged'] is True, 'summary_input_guard_reported')

pre = audit['prefloor_state']['runtime']
runtime = audit['effective_state']['runtime']
groups = table(runtime['_groups_df'])
parent_groups = table(raw['parent_groups'])
variant_groups = table(raw['variant_groups'])
pre_groups = table(pre['_groups_df'])
names = dict(runtime['seq2name']['items'])
check(set(names) == set(range(1, 51)), '49_real_groups_plus_synthetic_import')
for seq in range(1, 50):
    check(names[seq] == parent_groups[seq]['group_name'] == variant_groups[seq]['group_name'], f'group_identity/{seq}')
    check(mask_kind(parent_groups[seq]['ee']) == 'nan', f'raw_source_EE_unknown/{seq}')
    check(math.isnan(vector(runtime['source_EE'])[seq]), f'runtime_source_EE_unknown/{seq}')

physical = ['p', 'q', 'catch', 'predation', 'growth', 'immigration', 'emigration',
            'net_migration', 'respiration', 'egestion', 'M0', 'det_export',
            'EE', 'GE', 'GS', 'TL', '_DC', '_det_fate']
for field in physical:
    same(pre[field], runtime[field], 'floor_physical_unchanged/' + field)
floor = table(runtime['ee_floor_ledger'])
for seq in range(1, 51):
    check(floor[seq]['applied'] is False, f'floor_not_applied/{seq}')
    check(floor[seq]['external_mortality_export'] == 0, f'floor_external_export_zero/{seq}')
    if seq <= 47:
        check(floor[seq]['reason'] == 'invalid_or_missing_input', f'source_EE_floor_ineligible/{seq}')
    else:
        check(floor[seq]['reason'] == 'excluded_trophic_type', f'floor_excluded_basal_type/{seq}')
check(runtime['use_ee_floor'] is True and runtime['ee_floor'] == .1, 'effective_floor_setting')
check(audit['floor_applied_count'] == 0 and audit['living_floor_skipped_count'] == 47, 'floor_counts')

stages = {'parent_loaded': parent_groups, 'variant_loaded': variant_groups,
          'completed_prefloor': pre_groups, 'diagnostic_runtime': groups}
for row in ledger:
    for stage, data in stages.items():
        fields = data[row['group_seq']]
        check(row[stage]['present'] == (row['field'] in fields), 'scalar_ledger_presence')
        if row['field'] in fields:
            same(row[stage]['value'], fields[row['field']], 'scalar_ledger_value')

native = list(csv.DictReader((RUN / 'outputs/native_balance/groups.csv').open(encoding='utf-8-sig', newline='')))
check(len(native) == 49, 'native_group_count')
det_changes = []
for seq in [48, 49]:
    n = native[seq - 1]
    check(n['Group'] == names[seq], 'native_DET_identity')
    b, pb, ee = (float(n[k]) for k in ['Biomass', 'PB', 'EE'])
    supply = b * pb
    demand = supply * ee
    residual = supply - demand
    g = groups[seq]
    check(close(numeric(variant_groups[seq]['biomass']), b), f'native_DET_B/{seq}')
    check(close(numeric(variant_groups[seq]['pb']), pb), f'native_DET_PB/{seq}')
    check(close(numeric(variant_groups[seq]['ee']), ee), f'native_DET_EE/{seq}')
    check(close(numeric(g['p']), supply) and close(numeric(g['q']), supply), f'runtime_DET_supply/{seq}')
    check(close(numeric(g['predation']), demand), f'runtime_DET_predation/{seq}')
    check(close(numeric(g['detritus_stock_residual']), residual), f'runtime_DET_residual/{seq}')
    check(g['ee'] == 1 and g['pb'] == 0 and g['M0'] == 0 and g['det_export'] == 0 and g['biomass_accum'] == 0, f'runtime_DET_convention/{seq}')
    det_changes.append({'group_seq': seq, 'group_name': names[seq], 'native_EE': ee,
                        'runtime_EE': g['ee'], 'native_PB': pb, 'runtime_PB': g['pb'],
                        'native_B': b, 'runtime_B': g['biomass'],
                        'inflow': supply, 'predation': demand,
                        'native_nonutilized_flow': residual,
                        'runtime_stock_residual': g['detritus_stock_residual'],
                        'runtime_M0': g['M0'], 'runtime_det_export': g['det_export'],
                        'runtime_known_BA': g['biomass_accum'],
                        'relative_unclosed_production': residual / supply})

vecs = {k: vector(runtime[k]) for k in physical if runtime[k].get('type') == 'series'}
ext = vector(runtime['external_mortality_export'])
residuals = []
for seq in range(1, 51):
    production = sum(vecs[k][seq] for k in ['catch', 'predation', 'growth', 'net_migration', 'M0']) + ext[seq]
    consumption = production + vecs['egestion'][seq] + vecs['respiration'][seq]
    p, q = vecs['p'][seq], vecs['q'][seq]
    residuals.append({'group_seq': seq, 'p_absolute': p-production,
                      'q_absolute': q-consumption,
                      'p_relative': abs(p-production) / max(abs(p), 1e-12),
                      'q_relative': abs(q-consumption) / max(abs(q), 1e-12)})
pmax = max(x['p_relative'] for x in residuals)
qmax = max(x['q_relative'] for x in residuals)

method_reviews = {}
receipt_hashes = {}
for method in ['GE', 'TE', 'WithEgestion']:
    first = read('initial_' + method + '.json')
    second = read('reload_' + method + '.json')
    for phase, receipt in [('initial', first), ('reload', second)]:
        validate_encoded(receipt, method + '/' + phase)
        receipt_hashes[phase + '_' + method + '.json'] = sha(OUT / (phase + '_' + method + '.json'))
        check(receipt['identity'] == identity, method + '/' + phase + ':identity')
        check(receipt['status'] == 'returned', method + '/' + phase + ':return_status')
        raw_return = receipt['raw_return']
        check(raw_return['type'] == 'tuple' and len(raw_return['items']) == 4, method + '/' + phase + ':complete_tuple')
        same(raw_return['items'][0], receipt['full_report'], method + '/' + phase + ':report_copy')
        same(receipt['state_before'], receipt['state_after'], method + '/' + phase + ':no_runtime_mutation')
        same(receipt['state_before'], audit['effective_state'], method + '/' + phase + ':constructor_state')
        sppr, a, l = raw_return['items'][1:]
        for name, f in [('SPPR', sppr), ('A', a), ('L', l)]:
            check(set(f['index']) == set(range(1, 51)), method + '/' + phase + ':' + name + ':all_groups')
            check(f['shape'] == ([50, 4] if name == 'SPPR' else [50, 50]), method + '/' + phase + ':' + name + ':shape')
            check(set(f['columns']) == ({47,48,49,50} if name == 'SPPR' else set(range(1,51))), method + '/' + phase + ':' + name + ':columns')
            check(all(dt == 'float64' for dt in f['dtypes']), method + '/' + phase + ':' + name + ':float64')
            check(all(not any(any(r) for r in mask) for mask in f['masks'].values()), method + '/' + phase + ':' + name + ':finite')
        sm, am, lm = map(frame_data, (sppr, a, l))
        check(a['index'] == l['index'] and a['columns'] == l['columns'], method + '/' + phase + ':A_L_axes')
        # L=A-I uses matrix positions after the engine's recorded permutation.
        check(np.allclose(lm, am - np.eye(50), atol=ATOL, rtol=RTOL), method + '/' + phase + ':L_equals_A_minus_I')
        saved_source = receipt['reconciled_coefficients']['source_matrix']
        for key in ['index','columns','column_names','dtypes','shape','data','masks']:
            same(sppr[key], saved_source[key], method + '/' + phase + ':source_matrix/' + key)
        scopes = {}
        catch_vec = np.array([vecs['catch'][seq] for seq in sppr['index']])
        for scope, sources in [('all', {47,48,49,50}), ('inner', {47,48,49}), ('PP', {47})]:
            cols = [i for i, c in enumerate(sppr['columns']) if c in sources]
            values = sm[:, cols].sum(axis=1)
            expected = receipt['reconciled_coefficients']['scopes'][scope]
            check(set(expected) == set(names.values()), method + '/' + phase + ':' + scope + ':all_names')
            for seq, value in zip(sppr['index'], values):
                check(close(value, expected[names[seq]]), method + '/' + phase + ':' + scope + '/' + str(seq))
            footprint = float(values @ catch_vec)
            target = {'all':'ppr_all', 'inner':'ppr_inner', 'PP':'ppr_pp_only'}[scope]
            check(close(footprint, receipt['full_report']['footprint'][target]), method + '/' + phase + ':catch_weighted_' + scope)
            scopes[scope] = footprint
        report = receipt['full_report']
        check(close(report['model_input']['p_max_rel_residual'], pmax), method + '/' + phase + ':independent_p_residual')
        check(close(report['model_input']['q_max_rel_residual'], qmax), method + '/' + phase + ':independent_q_residual')
        check(close(report['footprint']['npp'], vecs['p'][47]), method + '/' + phase + ':native_PP_denominator')
        check(close(report['model_input']['total_catch'], sum(vecs['catch'].values())), method + '/' + phase + ':catch_sum')
        if phase == 'initial':
            method_reviews[method] = {
                'complete_tuple_shapes': [sppr['shape'],a['shape'],l['shape']],
                'groups_retained': 49, 'synthetic_import_retained': True,
                'source_columns': sppr['columns'], 'all_numeric_masks_empty': True,
                'scope_footprints_independently_reconciled': scopes,
                'footprint_units': 'native catch-density basis, t primary-production equivalent km^-2 yr^-1',
                'SPPR_negative_cells': int((sm < -1e-10).sum()),
                'A_negative_cells': int((am < -1e-10).sum()),
                'L_negative_cells': int((lm < -1e-10).sum()),
                'overall_scientific_grade': report['status'],
                'input_grade': report['model_input']['status'],
                'convergence_grade': report['divergence']['status'],
                'living_rho': report['divergence']['rho_living'],
                'detritus_loop_b': report['divergence']['b'],
                'near_singular_TE_groups': report['divergence']['near_singular_te'],
                'PP_closure_relative_gap': report['balance']['rel_gap'],
                'PP_budget_outflow': report['balance']['outflow']}
    for key in ['raw_return','full_report','state_before','state_after','reconciled_coefficients',
                'negative_matrix_entries','representation_and_scope_reconciliation']:
        same(first[key], second[key], method + ':independent_fresh_reload/' + key)
    same(first['full_report'], summary['methods'][method]['full_report'], method + ':summary_report')
    same(first['reconciled_coefficients'], summary['methods'][method]['coefficients'], method + ':summary_coefficients')
    check(summary['methods'][method]['reload_matches'] is True, method + ':reported_reload_match')
    method_reviews[method]['independent_reload_comparison'] = 'completed; see artifact_qa_issues for any mismatch'

receipt = {
    'schema_version': 1, 'reviewed_utc': datetime.now(timezone.utc).isoformat(),
    'review_scope': 'Independent read-only validation of saved receipts and arithmetic; no constructor, diagnostics, solvers, scientific code imports or scientific file edits.',
    'status': 'PASS' if not issues else 'FAIL',
    'tolerances': {'absolute': ATOL, 'relative': RTOL, 'negative_cell_reporting': 1e-10},
    'counts': dict(counts), 'artifact_qa_issue_count': len(issues),
    'artifact_qa_issues': issues,
    'input_identity': identity,
    'receipt_sha256': receipt_hashes,
    'checker_sha256': sha(Path(__file__)),
    'source_EE_floor': {'raw_real_group_unknown_EE_count':49,
                       'living_ineligible_count':47,'applied_count':0,
                       'physical_vectors_unchanged_by_floor':True,
                       'explanation':'Native-computed EE values do not become reported-source EE. The provenance adapter retains raw missingness and does not qualify any living group for the floor.'},
    'constructor_detritus_changes': det_changes,
    'independent_runtime_input_residuals': {'max_production_relative':pmax,
        'max_consumption_relative':qmax,
        'max_living_absolute':max(max(abs(r['p_absolute']),abs(r['q_absolute'])) for r in residuals if r['group_seq'] <= 47),
        'above_1e_10_absolute':[r for r in residuals if abs(r['p_absolute'])>1e-10 or abs(r['q_absolute'])>1e-10]},
    'methods': method_reviews,
    'scientific_failures_separate_from_artifact_qa': [
        'All three methods return FAIL. This is a retained scientific diagnostic result, not a failed extraction or serialization assertion.',
        'The runtime constructor preserves known DET BA=0 but changes native DET EE to 1 and removes native non-utilized flow from M0. It records that positive amount as detritus_stock_residual, without adding it to growth/BA or det_export. The two DET groups therefore fail the runtime production and consumption identities; the largest relative residual equals 1 minus native pelagic DET EE.',
        'All methods pass the two reported convergence bounds and contain no negative SPPR cells; this does not establish PP budget closure. Each method fails its reported PP closure check.',
        'GE has 2 near-singular TE warnings, TE has 12, and With Egestion has none. The EE floor cannot remedy this while original source EE remains unknown.',
        'Negative diagonal L entries follow L=A-I and do not imply negative source-resolved SPPR.',
        'Native catch-density footprints are diagnostic arithmetic, not mapped LME annual PPR estimates. Primary production includes outside production, so engine inner/PP labels do not establish a geographically local production boundary.'
    ]}
DEST.write_text(json.dumps(receipt, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')
print(json.dumps({'status':receipt['status'], 'assertions':counts['assertions'],
                  'issues':len(issues), 'first_issues':issues[:5], 'receipt':str(DEST)}, ensure_ascii=False))
