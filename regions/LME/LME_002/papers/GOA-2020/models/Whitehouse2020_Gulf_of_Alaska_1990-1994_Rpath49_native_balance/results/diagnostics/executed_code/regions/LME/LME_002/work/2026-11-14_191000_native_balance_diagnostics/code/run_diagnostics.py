"""Bounded, source-audited direct diagnostics for the native Rpath completion.

Does not alter scientific inputs, shared code, workbooks, selection, or maps.
Each direct method runs in a fresh process with a timeout; persisted-input reload
repeats the same three calls solely to verify state and result reproducibility.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import inspect
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
import warnings

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').is_file())
RUN = ROOT / 'regions/LME/LME_002/work/2026-11-14_191000_native_balance_diagnostics'
ENGINE = ROOT / 'tools/scientific_code/PPREstimation'
SOURCE_HASH = '10dfbf57dcc9c1ca2e57460637709a061c9264a7e29bf17e0028fadf4c919125'
OPTIONS = {'GE': 'GE', 'TE': 'TE', 'WithEgestion': 'With Egestion'}
METHOD_KEYS = {'GE': 'new_GE', 'TE': 'new_TE_EEfix', 'WithEgestion': 'new_WithEgestion'}
CONSTRUCTOR = dict(underdetermined=False, zero_catch=False,
                   zero_biomass_accum=False, default_gs=False,
                   normalize_DC=False, DC_tol=.001,
                   balance_BA_after_DC_normalization=False,
                   refresh_missing_biomass_accum=False,
                   use_ee_floor=False, ee_floor=.1, ee_threshold=.1)
DET_OPTIONS = dict(DET_TE_vals=1, det_collapse_mode='never',
                   det_open_mode='none', det_theta=1.0,
                   det_external_sppr=0.0, fix_EE_0_cases=True)
PHYSICAL_FIELDS = ('p', 'q', 'catch', 'predation', 'growth', 'immigration',
                   'emigration', 'net_migration', 'respiration', 'egestion',
                   'M0', 'det_export', 'EE', 'GE', 'GS', 'TL', '_DC', '_det_fate')
CODE_FILES = [ENGINE / name for name in
              ('ModelData.py', 'PPRCalculator.py', 'utils.py', 'create_PPRS_excel.py')]
CODE_FILES += [ROOT / 'tools/scientific_helpers/sppr/method_coverage.py', Path(__file__).resolve()]


def relative(path, base=ROOT):
    import os
    return os.path.relpath(path, base).replace('\\', '/')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                               allow_nan=False) + '\n', encoding='utf-8')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def guarded_import(expected):
    for rel, expected_sha in expected['code_sha256'].items():
        assert sha(ROOT / rel) == expected_sha, f'Code changed before execution: {rel}'
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ENGINE))
    global np, pd, ModelData, PPRCalculator, encode_lossless, runtime, extract_result
    import numpy as np
    import pandas as pd
    from ModelData import ModelData
    from PPRCalculator import PPRCalculator
    from tools.scientific_helpers.sppr.method_coverage import encode_lossless, _runtime, _extract_result
    runtime, extract_result = _runtime, _extract_result
    for rel, expected_sha in expected['code_sha256'].items():
        assert sha(ROOT / rel) == expected_sha, f'Code changed while importing: {rel}'


def check_inputs(args, expected):
    assert sha(args.parent) == expected['parent_sha256'] == SOURCE_HASH
    assert sha(args.variant) == expected['variant_sha256']
    for rel, expected_sha in expected['code_sha256'].items():
        assert sha(ROOT / rel) == expected_sha, f'Code changed during run: {rel}'


def compare_encoded(left, right, path='$', atol=1e-12, rtol=1e-12):
    """Compare typed serialized data, preserving masks, IDs, axes and strings."""
    differences = []
    if path.rsplit('.', 1)[-1] in ('index', 'columns', 'shape', 'index_names', 'column_names', 'dtypes'):
        return [] if left == right else [{'path': path, 'reason': 'axes, dimensions or types differ'}]
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            return [{'path': path, 'reason': 'dictionary keys differ'}]
        for key in left:
            differences.extend(compare_encoded(left[key], right[key], f'{path}.{key}', atol, rtol))
    elif isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return [{'path': path, 'reason': 'list lengths differ'}]
        for i, (a, b) in enumerate(zip(left, right)):
            differences.extend(compare_encoded(a, b, f'{path}[{i}]', atol, rtol))
    elif (isinstance(left, (int, float)) and not isinstance(left, bool)
          and isinstance(right, (int, float)) and not isinstance(right, bool)):
        if not math.isclose(left, right, abs_tol=atol, rel_tol=rtol):
            differences.append({'path': path, 'left': left, 'right': right,
                                'absolute_difference': abs(left-right)})
    elif type(left) is not type(right) or left != right:
        differences.append({'path': path, 'left': left, 'right': right})
    return differences


def typed_state(calculator):
    return {'runtime': runtime(calculator),
            'ee_threshold': calculator.ee_threshold,
            'discard_returns_metadata': encode_lossless(calculator.discard_returns_metadata)}


def construct(args, expected):
    check_inputs(args, expected)
    parent = ModelData(str(args.parent))
    variant = ModelData(str(args.variant))
    parent_ids = [int(g['group_seq']) for g in parent.data_json['group']]
    variant_ids = [int(g['group_seq']) for g in variant.data_json['group']]
    assert len(parent_ids) == len(variant_ids) == 49 and parent_ids == variant_ids
    assert {i: parent.seq2name[i] for i in parent_ids} == {i: variant.seq2name[i] for i in variant_ids}
    raw_parent = deepcopy(parent.groups_data)
    loaded_variant = deepcopy(variant.groups_data)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        calculator = PPRCalculator.from_modeldata(variant, **CONSTRUCTOR)
        prefloor_table = deepcopy(calculator._groups_df)
        prefloor_state = typed_state(calculator)
        physical_before = {key: deepcopy(getattr(calculator, key)) for key in PHYSICAL_FIELDS}
        # These are raw parent-source provenance fields, not new numerical inputs.
        # The constructor reads ModelData.groups_data, so solved native values must
        # not be reclassified as observed/source EE for floor eligibility.
        calculator.source_EE = raw_parent['ee'].reindex(calculator._groups_df.index).copy()
        calculator.source_M0 = raw_parent['M0'].reindex(calculator._groups_df.index).copy()
        assert calculator.source_EE.reindex(parent_ids).isna().sum() == 49
        calculator.apply_ee_floor(use_ee_floor=True, ee_floor=.1, ee_threshold=.1)
    floor_ledger = calculator.ee_floor_ledger
    assert not floor_ledger['reason'].eq('applied').any()
    living = calculator._groups_df.index[calculator._groups_df.trophic_info.isin(['Regular', 'PP'])]
    assert len(living) == 47
    assert floor_ledger.loc[living, 'reason'].eq('invalid_or_missing_input').all()
    assert (calculator.external_mortality_export == 0).all()
    for key, before in physical_before.items():
        after = getattr(calculator, key)
        if isinstance(before, pd.DataFrame):
            pd.testing.assert_frame_equal(before, after, check_exact=True)
        else:
            pd.testing.assert_series_equal(before, after, check_exact=True)
    check_inputs(args, expected)
    return calculator, parent, variant, raw_parent, loaded_variant, prefloor_table, {
        'prefloor_state': prefloor_state,
        'effective_state': typed_state(calculator),
        'warnings': [f'{w.category.__name__}: {w.message}' for w in caught],
        'raw_parent_unknown_EE_count': 49,
        'living_floor_skipped_count': 47,
        'floor_applied_count': 0,
        'physical_vectors_unchanged_by_floor': True,
        'source_provenance_adapter': 'Construct native-balanced variant with floor OFF; restore source_EE/source_M0 from unchanged sparse parent; apply configured ON floor once. Missing raw source EE remains ineligible.',
    }


def ledger_tables(parent, variant, prefloor, calculator):
    scalar_tables = {'parent_loaded': parent.groups_data, 'variant_loaded': variant.groups_data,
                     'completed_prefloor': prefloor, 'diagnostic_runtime': calculator._groups_df}
    fields = list(dict.fromkeys(c for frame in scalar_tables.values() for c in frame.columns))
    ids = sorted(set().union(*(set(frame.index) for frame in scalar_tables.values())))
    scalars = []
    for seq in ids:
        for field in fields:
            row = {'group_seq': int(seq), 'group_name': calculator.seq2name[seq], 'field': field}
            for stage, frame in scalar_tables.items():
                row[stage] = {'present': seq in frame.index and field in frame.columns,
                              'value': encode_lossless(frame.loc[seq, field]) if seq in frame.index and field in frame.columns else None}
            scalars.append(row)
    matrices = []
    for name, frames in {
        'diet': {'parent_loaded': parent.DC, 'variant_loaded': variant.DC, 'diagnostic_runtime': calculator._DC},
        'detritus_fate': {'parent_loaded': parent.det_fate, 'variant_loaded': variant.det_fate, 'diagnostic_runtime': calculator._det_fate},
    }.items():
        row_ids = sorted(set().union(*(set(frame.index) for frame in frames.values())))
        col_ids = sorted(set().union(*(set(frame.columns) for frame in frames.values())))
        for row_id in row_ids:
            for col_id in col_ids:
                row = {'matrix': name, 'row_id': int(row_id), 'column_id': int(col_id)}
                for stage, frame in frames.items():
                    row[stage] = {'present': row_id in frame.index and col_id in frame.columns,
                                  'value': encode_lossless(frame.loc[row_id, col_id]) if row_id in frame.index and col_id in frame.columns else None}
                matrices.append(row)
    return scalars, matrices


def negative_entries(result, label, calculator):
    rows = []
    for matrix_name, matrix in zip(('SPPR', 'A', 'L'), result[1:]):
        if matrix is None:
            continue
        assert isinstance(matrix, pd.DataFrame)
        values = matrix.to_numpy(dtype=float)
        for i, j in np.argwhere(values < -1e-10):
            row_id, col_id = matrix.index[i], matrix.columns[j]
            rows.append({'method': label, 'matrix': matrix_name,
                         'row_id': encode_lossless(row_id), 'column_id': encode_lossless(col_id),
                         'row_name': calculator.seq2name.get(row_id, str(row_id)),
                         'column_name': calculator.seq2name.get(col_id, str(col_id)),
                         'value': float(values[i, j]), 'tolerance': 1e-10,
                         'interpretation': 'Negative primary-production contribution' if matrix_name == 'SPPR' else
                         'Equation coefficient; sign alone is not an SPPR failure. Negative L diagonal entries arise from L=A-I.'})
    return rows


def worker(args):
    expected = read(args.identity)
    guarded_import(expected)
    receipt_path = args.outdir / f'{args.pass_name}_{args.worker}.json'
    receipt = {'method': OPTIONS[args.worker], 'pass': args.pass_name,
               'identity': expected, 'status': 'NOT_RUN'}
    start = time.monotonic()
    try:
        calculator, *_ = construct(args, expected)
        before = typed_state(calculator)
        kwargs = {**DET_OPTIONS, 'TE_option': OPTIONS[args.worker],
                  'short': False, 'flat': False, 'return_sppr': True}
        settings = {'method': METHOD_KEYS[args.worker], 'target': 'diagnose_sppr',
                    'source_resolved': True, 'kwargs': kwargs}
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            result = calculator.diagnose_sppr(**kwargs)
        assert isinstance(result, tuple) and len(result) == 4
        encoded_result = encode_lossless(result)
        receipt.update(status='returned', kwargs=encode_lossless(kwargs), raw_return=encoded_result,
                       full_report=encode_lossless(result[0]),
                       state_before=before, state_after=typed_state(calculator),
                       warnings=[f'{w.category.__name__}: {w.message}' for w in caught],
                       negative_matrix_entries=negative_entries(result, args.worker, calculator))
        dump(receipt_path, receipt)  # Preserve the actual return before reconciliation.
        extracted = extract_result(calculator, settings, result)
        receipt['reconciled_coefficients'] = extracted
        receipt['state_differences_after_method'] = compare_encoded(before, typed_state(calculator))
        assert not receipt['state_differences_after_method'], 'Method changed audited scientific state'
        # JSON reopen preserves typed matrices/masks, rather than rounded CSV display.
        assert read(receipt_path)['raw_return'] == encoded_result
        check_inputs(args, expected)
        receipt['representation_and_scope_reconciliation'] = True
    except Exception as exc:
        receipt['status'] = 'exception' if 'raw_return' not in receipt else 'returned_with_reconciliation_error'
        receipt['exception'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    receipt['elapsed_seconds'] = time.monotonic() - start
    dump(receipt_path, receipt)
    print(f"{args.pass_name} {args.worker}: {receipt['status']}", flush=True)
    return 0 if receipt['status'] == 'returned' else 1


def main(args):
    args.outdir.mkdir(parents=True, exist_ok=True)
    assert args.parent.resolve() != args.variant.resolve()
    assert args.variant.name == args.parent.name == 'model.json'
    expected = {'schema_version': 1, 'region_id': 'LME_002',
                'parent_model_id': args.parent.parent.name, 'variant_model_id': args.variant.parent.name,
                'parent_path': relative(args.parent), 'variant_path': relative(args.variant),
                'parent_sha256': sha(args.parent), 'variant_sha256': sha(args.variant),
                'code_sha256': {relative(path): sha(path) for path in CODE_FILES},
                'run_timestamp_utc': datetime.now(timezone.utc).isoformat(),
                'constructor': CONSTRUCTOR, 'effective_floor': {'use_ee_floor': True, 'ee_floor': .1, 'ee_threshold': .1},
                'diagnostic_options': DET_OPTIONS, 'method_timeout_seconds': args.timeout,
                'scope': 'Native balance computational variant, direct GE/TE/With Egestion diagnostics and reload verification only; no catch mapping, annual arithmetic, selection, registry or maps.',
                'interpretation': 'Footprints returned by diagnostics use native model catch densities. Aggregate Primary production includes outside production; engine inner/PP labels do not recover a geographically local-production partition.',
                'environment': {'python': sys.version, 'executable': sys.executable, 'platform': platform.platform()}}
    assert expected['parent_sha256'] == SOURCE_HASH
    for path in CODE_FILES:
        target = args.outdir / 'executed_code' / relative(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        assert sha(target) == expected['code_sha256'][relative(path)]
    for package in ('numpy', 'pandas', 'scipy', 'sympy', 'igraph', 'tqdm', 'openpyxl'):
        try:
            expected['environment'][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            expected['environment'][package] = None
    identity_path = args.outdir / 'run_identity.json'
    dump(identity_path, expected)
    guarded_import(expected)
    try:
        calc, parent, variant, raw_parent, loaded_variant, prefloor, admission = construct(args, expected)
        dump(args.outdir / 'constructor_audit.json', admission)
        scalar_ledger, matrix_ledger = ledger_tables(parent, variant, prefloor, calc)
        dump(args.outdir / 'scalar_transformation_ledger.json', scalar_ledger)
        dump(args.outdir / 'matrix_transformation_ledger.json', matrix_ledger)
        dump(args.outdir / 'raw_modeldata_views.json', encode_lossless({
            'parent_groups': raw_parent, 'variant_groups': loaded_variant,
            'parent_diet': parent.DC, 'variant_diet': variant.DC,
            'parent_fate': parent.det_fate, 'variant_fate': variant.det_fate,
            'parent_discard_returns': parent.discard_returns,
            'variant_discard_returns': variant.discard_returns,
            'variant_discard_metadata': variant.discard_returns_metadata}))
        reloaded, *_ = construct(args, expected)
        reload_diff = compare_encoded(typed_state(calc), typed_state(reloaded))
        dump(args.outdir / 'constructor_reload_verification.json', {'matches': not reload_diff, 'differences': reload_diff, 'atol': 1e-12, 'rtol': 1e-12})
        assert not reload_diff, 'Persisted-input constructor replay differs'
    except Exception as exc:
        failure = {'status': 'constructor_blocked', 'exception': {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()},
                   'methods': {label: {'status': 'NOT_RUN', 'reason': 'Audited construction failed'} for label in OPTIONS}, 'identity': expected}
        dump(args.outdir / 'diagnostic_summary.json', failure)
        print(json.dumps(failure, ensure_ascii=False, indent=2), flush=True)
        return 1
    outcomes = {}
    for pass_name in ('initial', 'reload'):
        for label in OPTIONS:
            command = [sys.executable, '-u', str(Path(__file__).resolve()), '--variant', str(args.variant),
                       '--parent', str(args.parent), '--outdir', str(args.outdir),
                       '--worker', label, '--pass-name', pass_name, '--identity', str(identity_path)]
            path = args.outdir / f'{pass_name}_{label}.json'
            try:
                proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                      encoding='utf-8', errors='replace', timeout=args.timeout)
                (args.outdir / f'{pass_name}_{label}.log').write_text(proc.stdout + '\nSTDERR\n' + proc.stderr, encoding='utf-8')
                result = read(path) if path.exists() else {'status': 'exception', 'reason': 'Worker returned no result', 'returncode': proc.returncode}
            except subprocess.TimeoutExpired as exc:
                result = {'status': 'timeout', 'timeout_seconds': args.timeout, 'method': OPTIONS[label], 'pass': pass_name,
                          'reason': 'Worker terminated at explicit method bound; no diagnostic grade inferred'}
                dump(path, result)
            outcomes[f'{pass_name}_{label}'] = result
            print(f"{pass_name} {label}: {result['status']}", flush=True)
    summary = {'status': 'diagnostics_completed', 'identity': expected,
               'constructor_reproduced': True, 'raw_source_EE_unknown': 49,
               'floor_applied_count': 0, 'methods': {},
               'comparison_tolerance': {'atol': 1e-12, 'rtol': 1e-12},
               'canonical_inputs_unchanged': True}
    for label in OPTIONS:
        first, replay = outcomes[f'initial_{label}'], outcomes[f'reload_{label}']
        item = {'initial_status': first['status'], 'reload_status': replay['status']}
        if first['status'] == replay['status'] == 'returned':
            differences = compare_encoded(first['raw_return'], replay['raw_return'])
            item.update(overall_grade=first['full_report'].get('status'),
                        full_report=first['full_report'],
                        coefficients=first['reconciled_coefficients'],
                        reload_matches=not differences, reload_differences=differences,
                        all_matrix_negative_entries=first['negative_matrix_entries'])
            if differences:
                summary['status'] = 'completed_with_reconciliation_limitations'
        else:
            item.update(reload_matches=False, reason='No pair of completed diagnostic returns to reconcile')
            summary['status'] = 'completed_with_unavailable_methods'
        summary['methods'][label] = item
    check_inputs(args, expected)
    dump(args.outdir / 'diagnostic_summary.json', summary)
    readable = ['# Full direct diagnostic returns', '']
    for label in OPTIONS:
        result = outcomes[f'initial_{label}']
        returned = result.get('full_report', {key: result.get(key) for key in ('status', 'reason', 'exception', 'timeout_seconds') if key in result})
        readable.extend([f'## {OPTIONS[label]}', '', '```json',
                         json.dumps(returned, ensure_ascii=False, indent=2, allow_nan=False), '```', ''])
    (args.outdir / 'direct_diagnostics.md').write_text('\n'.join(readable), encoding='utf-8')
    print(json.dumps({'status': summary['status'], 'methods': {key: {k: v for k, v in value.items() if k in ('initial_status', 'reload_status', 'overall_grade', 'reload_matches')} for key, value in summary['methods'].items()}}, indent=2), flush=True)
    return 0 if summary['status'] == 'diagnostics_completed' else 1


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', required=True, type=Path)
    parser.add_argument('--parent', required=True, type=Path)
    parser.add_argument('--outdir', type=Path, default=RUN / 'outputs/diagnostics')
    parser.add_argument('--timeout', type=float, default=180.)
    parser.add_argument('--worker', choices=tuple(OPTIONS))
    parser.add_argument('--pass-name', choices=('initial', 'reload'), default='initial')
    parser.add_argument('--identity', type=Path)
    args = parser.parse_args()
    args.variant, args.parent, args.outdir = args.variant.resolve(), args.parent.resolve(), args.outdir.resolve()
    raise SystemExit(worker(args) if args.worker else main(args))
