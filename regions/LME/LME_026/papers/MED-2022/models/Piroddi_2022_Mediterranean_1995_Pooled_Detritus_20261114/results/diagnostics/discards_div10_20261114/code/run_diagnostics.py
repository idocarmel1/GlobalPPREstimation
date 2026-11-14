"""Run the authorized six-group discards-divided-by-ten pooled sensitivity.

No workbook, selection, shared code or base model is changed. The canonical
variant must already exist. A fresh output directory is required. The runtime
bridge explicitly stages unlisted landings as zero and returns known fishery
discards to the sole pooled detritus group once; routing is a scenario assumption.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path
import platform
import sys
import time
import traceback
import warnings

sys.dont_write_bytecode = True
MODEL_ID = 'Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114'
VARIANT_ID = MODEL_ID + '__discards_div10_six_groups'
DISCARD_FACTOR = 0.1
SCALED_GROUPS = (1, 2, 3, 4, 11, 12)
BASE_ID = 'Piroddi_2022_Mediterranean_1995'
BASE_HASH = 'f038707bf7837962933eec3e6daeae53eb0b9a7f48837763b0ce621edcdc3a9e'
EXPECTED_ENGINE = {
    'PPRCalculator.py': '5bd249eb73d61c1db77279a8a527465e4673944f377c40ca9e6100a2da0cc877',
    'ModelData.py': '64c7769ed1494ccadf71dea333765989964ce8c4be9575143b6bc4cbbc6cc680',
    'utils.py': '817f969850b250d06563cfff2e5d1be0fdf70bacb7a3c4ac317bf69c805ca07f',
}
CONSTRUCTOR = dict(underdetermined=False, zero_catch=False,
                   zero_biomass_accum=True, default_gs=True,
                   normalize_DC=False, DC_tol=0.001,
                   balance_BA_after_DC_normalization=False,
                   refresh_missing_biomass_accum=False,
                   use_ee_floor=True, ee_floor=0.1, ee_threshold=0.1)
METHODS = ('GE', 'TE', 'With Egestion')
METHOD_OPTIONS = dict(short=False, flat=False, return_sppr=True,
                      det_collapse_mode='never', det_open_mode='none',
                      det_theta=1.0, det_external_sppr=0.0,
                      fix_EE_0_cases=False)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fishery_totals(source, source_ids):
    """Sum source fleet amounts; only absent landings become an explicit zero."""
    fisheries = source['source_fisheries']
    fleets = set(fisheries['fleets'])
    totals = {'landings': Decimal(0), 'discards': Decimal(0)}
    missing = []
    for seq in source_ids:
        key = str(seq)
        for kind in totals:
            values = fisheries[kind].get(key)
            if values is None and kind == 'landings':
                missing.append(seq)
                continue
            if not isinstance(values, dict) or set(values) != fleets:
                raise ValueError(f'Incomplete {kind} fleet values for source group {seq}')
            numbers = [Decimal(str(value)) for value in values.values()]
            if any(not value.is_finite() or value < 0 for value in numbers):
                raise ValueError(f'Unknown/negative {kind} amount for source group {seq}')
            totals[kind] += sum(numbers, Decimal(0))
    return {**{kind: float(value) for kind, value in totals.items()},
            'catch': float(totals['landings'] + totals['discards']),
            'assumed_zero_landings_groups': missing}


def negative_entries(matrix, method, names):
    """Strict signs, preserving row/column identity rather than sorted positions."""
    import numpy as np
    rows = []
    for group, values in matrix.iterrows():
        for source, value in values.items():
            if np.isfinite(value) and value < 0:
                rows.append({'method': method, 'matrix': 'SPPR',
                             'source_id': int(source), 'source_name': names[int(source)],
                             'group_id': int(group), 'group_name': names[int(group)],
                             'sppr_value': float(value), 'comparison_tolerance': 0.0})
    return rows


def verify_fishery_crosswalk(variant, base, pool):
    """Allow only the recorded aggregation of source pools 70 and 71."""
    actual, original = variant['source_fisheries'], base['source_fisheries']
    for key in ('fleets', 'units', 'landings'):
        if actual[key] != original[key]:
            raise ValueError(f'Original fishery {key} evidence changed')
    if set(actual['discards']) != {str(i) for i in range(1, 70)} | {str(pool)}:
        raise ValueError('Derived discard donor identities do not match the pooled crosswalk')
    for seq in range(1, 70):
        if actual['discards'][str(seq)] != original['discards'][str(seq)]:
            raise ValueError(f'Original living-group discard evidence changed: {seq}')
    for fleet in original['fleets']:
        expected = sum((Decimal(str(original['discards'][str(seq)][fleet]))
                        for seq in (70, 71)), Decimal(0))
        if Decimal(str(actual['discards'][str(pool)][fleet])) != expected:
            raise ValueError(f'Pooled discard amount disagrees with source: {fleet}')


def roots():
    model = Path(__file__).resolve().parents[4]
    repo = next(p for p in model.parents if (p / 'tools/scientific_code/PPREstimation').is_dir())
    return model, repo


def run(output):
    import numpy as np
    import pandas as pd
    model_dir, repo = roots()
    if model_dir.name != MODEL_ID:
        raise ValueError('Runner is outside its exact authorized variant')
    output = output.resolve()
    permitted = model_dir / 'results/diagnostics/discards_div10_20261114'
    if not output.is_relative_to(permitted.resolve()) or output.exists():
        raise ValueError('Use a new output directory within this model-local diagnostic run')
    model_path = model_dir / 'model.json'
    base_path = model_dir.parent / BASE_ID / 'model.json'
    pinned_root = Path(__file__).resolve().parent / 'executed_engine'
    engine = pinned_root / 'tools/scientific_code/PPREstimation'
    serializer = pinned_root / 'tools/scientific_helpers/sppr/method_coverage.py'
    if sha(model_path) != '281d8543a165bf67652168cbc47f09db224e51bddb6768e9365f8c52d03ac956':
        raise ValueError('Pooled baseline model changed')
    if sha(serializer) != 'f855b88eebeb52d8814b0eb1dc8e9ed37e943fe62ed77d5bec88522b1cf19905':
        raise ValueError('Pinned serializer changed')
    if sha(engine / 'create_PPRS_excel.py') != '5f94a4d885643e706a57a9e8faa1bf9fa5338e8626831d74dfe59f2d833158a1':
        raise ValueError('Pinned exporter changed')
    if sha(base_path) != BASE_HASH:
        raise ValueError('Original model hash differs from the audited input')
    for name, expected in EXPECTED_ENGINE.items():
        if sha(engine / name) != expected:
            raise ValueError(f'Frozen engine changed: {name}')
    watched = [model_path, base_path, Path(__file__).resolve(),
               *(engine / name for name in (*EXPECTED_ENGINE, 'create_PPRS_excel.py')),
               serializer]
    before_hashes = {str(p.relative_to(repo)): sha(p) for p in watched}
    variant = json.loads(model_path.read_text(encoding='utf-8-sig'))
    base = json.loads(base_path.read_text(encoding='utf-8-sig'))
    source_groups = {int(g['group_seq']): g for g in base['group']}
    variant_groups = {int(g['group_seq']): g for g in variant['group']}
    pools = [seq for seq, group in variant_groups.items() if int(group['pp']) == 2]
    if len(pools) != 1 or len(variant_groups) != 70:
        raise ValueError('Expected 69 original living groups and one pooled detritus group')
    pool = pools[0]
    verify_fishery_crosswalk(variant, base, pool)
    if set(variant_groups) - {pool} != set(range(1, 70)):
        raise ValueError('Living group identity changed')
    for seq in range(1, 70):
        for field in ('biomass', 'pb', 'qb', 'ee', 'gs', 'biomass_accum',
                      'immigration', 'emigration', 'diet_imp'):
            if variant_groups[seq].get(field) != source_groups[seq].get(field):
                raise ValueError(f'Unapproved living field change: {seq}/{field}')
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(engine))
    import importlib.util
    spec = importlib.util.spec_from_file_location('pinned_sensitivity_serializer', serializer)
    serialization = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(serialization)
    encode_lossless = serialization.encode_lossless
    from ModelData import ModelData
    from PPRCalculator import PPRCalculator
    output.mkdir(parents=True)
    artifacts = []

    def save(name, value, role):
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(encode_lossless(value), ensure_ascii=False, indent=2, allow_nan=False)
        path.write_text(text + '\n', encoding='utf-8')
        if json.loads(path.read_text(encoding='utf-8')) != json.loads(text):
            raise AssertionError(f'JSON roundtrip failed: {name}')
        artifacts.append({'role': role, 'path': name, 'sha256': sha(path), 'availability': 'present'})

    def table(name, frame, role):
        save(name + '.json', frame, role)
        frame.to_csv(output / (name + '.csv'), encoding='utf-8', float_format='%.17g')
        artifacts.append({'role': role + '_display_csv', 'path': name + '.csv',
                          'sha256': sha(output / (name + '.csv')), 'availability': 'present'})

    def state(calc):
        attrs = ('_groups_df', '_DC', '_det_fate', 'p', 'q', 'catch', 'predation',
                 'growth', 'net_migration', 'immigration', 'emigration', 'M0',
                 'egestion', 'respiration', 'EE', 'GS', 'GE', 'det_export',
                 'external_mortality_export', 'EE_before_floor', 'M0_before_floor',
                 'source_EE', 'source_M0', 'ee_floor_ledger', 'ee_floor_info',
                 '_initialization_settings', '_discard_returns', 'discard_returns_metadata')
        return {key: getattr(calc, key) for key in attrs if hasattr(calc, key)}

    def construct(retain):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            md = ModelData(str(model_path))
            if retain:
                table('source_groups_before_staging', md.groups_data, 'source_group_table')
            non_import = md.groups_data.index[~md.groups_data.trophic_info.eq('Import')]
            if list(md.det_fate.columns) != [pool] or not np.array_equal(
                    md.det_fate.loc[non_import, pool].to_numpy(), np.ones(len(non_import))):
                raise ValueError('Variant does not explicitly route 100% of each non-import row to the pool')
            returns = pd.DataFrame(0., index=md.groups_data.index, columns=[pool])
            ledger = []
            for seq in non_import:
                source_ids = [70, 71] if seq == pool else [int(seq)]
                totals = fishery_totals(base, source_ids)
                baseline_totals = copy.deepcopy(totals)
                factor = DISCARD_FACTOR if int(seq) in SCALED_GROUPS else 1.0
                if factor != 1.0:
                    totals['discards'] = float(Decimal(str(totals['discards'])) * Decimal(str(factor)))
                    totals['catch'] = float(Decimal(str(totals['landings'])) + Decimal(str(totals['discards'])))
                previous = md.groups_data.at[seq, 'catch']
                md.groups_data.at[seq, 'catch'] = totals['catch']
                returns.at[seq, pool] = totals['discards']
                ledger.append({'group_id': int(seq), 'group_name': md.seq2name[seq],
                               'source_group_ids': source_ids, 'loaded_catch_before_staging': previous,
                               **totals, 'baseline_landings': baseline_totals['landings'],
                               'baseline_discards': baseline_totals['discards'],
                               'baseline_catch': baseline_totals['catch'],
                               'discard_multiplier': factor,
                               'destination_pool_id': pool, 'fraction_returned': 1.0,
                               'routing_provenance': 'User-authorized pooled scenario; not source-observed'})
            md.discard_returns = returns
            md.discard_returns_metadata = {
                'status': 'complete', 'unresolved': [],
                'provenance': 'User-authorized 100% pooled routing experiment, 2026-11-14',
                'amounts_source_repository_relative': base_path.relative_to(repo).as_posix()+'#source_fisheries',
                'amounts_source_sha256': BASE_HASH,
                'routing_is_assumption': True, 'fraction_returned': 1.0,
                'discard_scaling_is_assumption': True,
                'discard_multiplier': DISCARD_FACTOR, 'scaled_group_ids': list(SCALED_GROUPS),
                'scope': 'Hypothetical sensitivity; not a published-parameter correction',
                'pool_id': pool, 'total_discards': float(returns.to_numpy().sum()),
                'total_returned': float(returns.to_numpy().sum()), 'external_discard_remainder': 0.,
                'donors': ledger,
            }
            if retain:
                save('catch_and_discard_staging.json', ledger, 'catch_discard_transformation_ledger')
                table('staged_source_groups', md.groups_data, 'staged_group_table')
                table('diet_matrix', md.DC, 'runtime_diet_matrix')
                table('detritus_fate', md.det_fate, 'runtime_fate_matrix')
                table('discard_returns', returns, 'absolute_discard_return_matrix')
                save('discard_returns_metadata.json', md.discard_returns_metadata, 'discard_routing_assumptions')
            calc = PPRCalculator.from_modeldata(md, **CONSTRUCTOR)
        return calc, [f'{w.category.__name__}: {w.message}' for w in caught]

    summary = {'schema_version': 1, 'unit_id': 'LME_026', 'model_id': MODEL_ID,
               'variant_id': VARIANT_ID, 'run_id': 'discards_div10_20261114',
               'scenario': {'discard_multiplier': DISCARD_FACTOR, 'scaled_group_ids': list(SCALED_GROUPS),
                            'biological_parameters_changed': False, 'canonical_input_changed': False},
               'base_model_id': BASE_ID, 'created_at': datetime.now(timezone.utc).isoformat(),
               'constructor': CONSTRUCTOR, 'method_options': METHOD_OPTIONS,
               'runtime_initialization': 'custom_audited_pooled_discard_bridge_div10_six_groups',
               'runtime_initialization_description': 'This saved runner multiplies donor discards and pooled returns by 0.1 for IDs1,2,3,4,11,12 before construction, preserving biology and applying EE floor ON0.1 once. This is hypothetical, not an extraction correction. A stock constructor cannot reproduce this runtime.',
               'protected_hashes_before': before_hashes,
               'status': 'STARTED', 'methods': [], 'adopted': False,
               'diagnosed_state': 'original constructed calculator; never its balanced_model copy'}
    save('run_identity.json', {**summary, 'python': sys.version, 'platform': platform.platform(),
         'packages': {p: importlib.metadata.version(p) for p in ('numpy', 'pandas', 'scipy', 'sympy', 'igraph')},
         'diagnose_sppr_defaults': {k: str(v.default) for k, v in inspect.signature(
             PPRCalculator.diagnose_sppr).parameters.items()},
         'SPPR_new_defaults': {k: str(v.default) for k, v in inspect.signature(
             PPRCalculator.SPPR_new).parameters.items()}}, 'execution_identity')
    save('source_parameter_provenance.json', {'M0_provenance':
         'The engine source_M0 field is derived from source B*PB*(1-EE); raw other_mort is unreported and is not an observed mortality flow.',
         'living_groups': [{'group_id': seq, 'source_B': source_groups[seq]['biomass'],
             'source_PB': source_groups[seq]['pb'], 'source_EE': source_groups[seq]['ee'],
             'raw_other_mort': source_groups[seq]['other_mort'],
             'raw_GS': source_groups[seq]['gs'], 'raw_BA': source_groups[seq]['biomass_accum']}
             for seq in range(1,70)]}, 'raw_source_missingness_and_derived_M0_provenance')
    try:
        calc, constructor_warnings = construct(True)
        save('constructor_warnings.json', constructor_warnings, 'constructor_warnings')
        initial = state(calc)
        save('initialization_evidence.json', initial, 'tagged_runtime_tables_and_vectors')
        table('pre_floor_groups', calc._ee_floor_base['_groups_df'], 'completed_pre_floor_group_table')
        table('effective_groups', calc._groups_df, 'effective_group_table')
        table('ee_floor_ledger', calc.ee_floor_ledger, 'ee_floor_transformation_ledger')
        save('ee_floor_info.json', calc.ee_floor_info, 'ee_floor_summary')
        # Reload only initialization; do not repeat any SPPR diagnostic solve.
        reproduced, repeat_warnings = construct(False)
        exact = encode_lossless(initial) == encode_lossless(state(reproduced))
        save('initialization_reproduction.json', {'exact_tagged_state_equality': exact,
             'diagnostics_called_during_reproduction': False, 'warnings': repeat_warnings}, 'initialization_reproduction')
        if not exact:
            raise ValueError('Reloaded initialization differs; diagnostic execution stopped')
        del reproduced
        names = {int(k): v for k, v in calc.seq2name.items()}
        save('group_inventory.json', [{'group_id': int(seq), 'name': names[seq],
             'trophic_type': calc._groups_df.at[seq, 'trophic_info'],
             'synthetic': calc._groups_df.at[seq, 'trophic_info'] == 'Import'}
             for seq in calc._groups_df.index], 'group_identity_and_roles')
        pre = calc._ee_floor_base['_groups_df']
        living = calc._groups_df.index[calc._groups_df.trophic_info.isin(['Regular', 'PP'])]
        consistency = pd.DataFrame(index=living)
        consistency['source_EE'] = calc.source_EE.reindex(living)
        consistency['pre_floor_EE'] = calc.EE_before_floor.reindex(living)
        consistency['pre_floor_1_minus_M0_over_P'] = 1-calc.M0_before_floor.reindex(living)/pre.p.reindex(living)
        consistency['effective_EE'] = calc.EE.reindex(living)
        consistency['effective_1_minus_M0_over_P'] = 1-calc.M0.reindex(living)/calc.p.reindex(living)
        consistency['M0_before'] = calc.M0_before_floor.reindex(living)
        consistency['M0_effective_to_detritus'] = calc.M0.reindex(living)
        consistency['external_mortality_sink'] = calc.external_mortality_export.reindex(living)
        consistency['egestion_to_detritus'] = calc.egestion.reindex(living)
        consistency['fishery_discards_to_detritus'] = calc._discard_return_matrix().sum(axis=1).reindex(living)
        consistency['production_residual_with_sink'] = (calc.p-calc.predation-calc.catch-calc.growth
             -calc.net_migration-calc.M0-calc.external_mortality_export).reindex(living)
        table('living_ee_and_flow_reconciliation', consistency, 'living_ee_flow_and_residual_reconciliation')
        equation_ok = bool(np.allclose(consistency.effective_EE,
             consistency.effective_1_minus_M0_over_P, rtol=1e-12, atol=1e-12, equal_nan=False))
        sink_ok = bool(np.allclose(consistency.M0_before,
             consistency.M0_effective_to_detritus+consistency.external_mortality_sink, rtol=1e-12, atol=1e-12))
        biological = float(((calc.M0+calc.egestion)*calc.get_det_fate()[pool]).sum())
        returns_total = float(calc._discard_return_matrix()[pool].sum())
        routing_checks = {'EE_equals_1_minus_M0_over_P': equation_ok,
             'mortality_partition_conserved': sink_ok,
             'pool_inflow_equals_reduced_biological_plus_discard_returns_once': bool(np.isclose(
                 calc.q[pool], biological+returns_total, rtol=1e-12, atol=1e-12)),
             'pool_inflow': float(calc.q[pool]), 'routed_M0_plus_egestion': biological,
             'returned_fishery_discards': returns_total,
             'fishery_total_catch': float(calc.catch.sum()),
             'external_fishery_catch_after_returns': float(calc._external_catch().sum()),
             'external_mortality_sink': float(calc.external_mortality_export.sum()),
             'fin_whale_production_residual_with_sink': float(consistency.loc[4, 'production_residual_with_sink']),
             'original_living_biology_repaired': False}
        save('flow_reconciliation.json', routing_checks, 'exactly_once_flow_reconciliation')
        if not all(routing_checks[k] for k in ('EE_equals_1_minus_M0_over_P',
                'mortality_partition_conserved', 'pool_inflow_equals_reduced_biological_plus_discard_returns_once')):
            raise ValueError('Scenario accounting checks failed; diagnostics stopped')
        for method in METHODS:
            slug = method.lower().replace(' ', '_')
            started = time.perf_counter()
            try:
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always')
                    raw = calc.diagnose_sppr(TE_option=method, **METHOD_OPTIONS)
                report, sppr, A, L = raw
                save(f'{slug}/full_return.json', raw, f'{slug}_lossless_direct_return')
                save(f'{slug}/diagnostic_report.json', report, f'{slug}_diagnostic_report')
                save(f'{slug}/python_warnings.json', [f'{w.category.__name__}: {w.message}' for w in caught], f'{slug}_warnings')
                item = {'method': method, 'execution': 'RETURNED', 'status': report['status'],
                        'elapsed_seconds': time.perf_counter()-started,
                        'divergence': report.get('divergence'), 'balance': report.get('balance')}
                if sppr is not None:
                    for label, matrix in (('SPPR', sppr), ('A', A), ('L', L)):
                        if not matrix.index.is_unique or not matrix.columns.is_unique:
                            raise ValueError(f'Duplicate axes in returned {label}')
                        table(f'{slug}/{label}', matrix, f'{slug}_{label}_matrix')
                    negative = negative_entries(sppr, method, names)
                    save(f'{slug}/negative_entries.json', negative, f'{slug}_all_strict_negative_entries')
                    scopes = {'all': list(sppr.columns),
                              'inner': [c for c in sppr.columns if c not in calc.get_Import_seq()],
                              'PP': [c for c in sppr.columns if c in calc.get_PP_seq()]}
                    coefficients = pd.DataFrame({scope: sppr.loc[:, cols].sum(axis=1, skipna=False)
                                                 for scope, cols in scopes.items()})
                    table(f'{slug}/coefficients', coefficients, f'{slug}_scope_coefficients')
                    negative_columns = len({entry['source_id'] for entry in negative})
                    item.update(negative_entries=len(negative), negative_source_columns=negative_columns,
                                negative_count_matches_return=negative_columns == report['divergence'].get('n_negative_sources'),
                                matrix_shape=list(sppr.shape), nonfinite_entries=int((~np.isfinite(sppr.to_numpy())).sum()))
                    save(f'{slug}/matrix_metadata.json', {'orientation': 'recipient group rows by basal-source columns',
                         'units': 'primary-production mass required per unit group mass; same mass basis as model',
                         'row_ids': [int(x) for x in sppr.index], 'column_ids': [int(x) for x in sppr.columns],
                         'row_names': [names[int(x)] for x in sppr.index], 'column_names': [names[int(x)] for x in sppr.columns],
                         'source_scopes': scopes, 'negative_test': 'finite value < 0 before rounding',
                         'matching_negative_source_count': item['negative_count_matches_return']}, f'{slug}_matrix_identity')
                else:
                    item.update(matrix_available=False, matrix_unavailable_reason=report.get('divergence', {}).get('solve_error'))
                summary['methods'].append(item)
            except Exception as exc:
                error = {'method': method, 'execution': 'EXCEPTION', 'status': None,
                         'exception_type': type(exc).__name__, 'exception': str(exc),
                         'traceback': traceback.format_exc(), 'elapsed_seconds': time.perf_counter()-started}
                save(f'{slug}/exception.json', error, f'{slug}_execution_exception')
                summary['methods'].append(error)
        save('state_after_diagnostics.json', state(calc), 'post_diagnostic_tagged_tables_and_vectors')
        summary['status'] = 'COMPLETE_OUTCOME_INVENTORY'
    except Exception as exc:
        error = {'exception_type': type(exc).__name__, 'exception': str(exc), 'traceback': traceback.format_exc()}
        save('construction_or_reconciliation_exception.json', error, 'blocked_execution_evidence')
        summary['status'] = 'BLOCKED'
        summary['blocking_error'] = error
        present = {item['method'] for item in summary['methods']}
        summary['methods'].extend({'method': method, 'execution': 'NOT_RUN', 'status': None,
                                  'reason': str(exc)} for method in METHODS if method not in present)
    finally:
        after = {str(p.relative_to(repo)): sha(p) for p in watched}
        summary['protected_hashes_after'] = after
        summary['protected_bytes_unchanged'] = before_hashes == after
        summary['completed_at'] = datetime.now(timezone.utc).isoformat()
        save('summary.json', summary, 'machine_readable_outcome_summary')
        verified = all(sha(output/a['path']) == a['sha256'] for a in artifacts)
        index = {'schema_version': 1, 'run_id': 'discards_div10_20261114', 'unit_id': 'LME_026',
                 'model_id': MODEL_ID, 'variant_id': VARIANT_ID, 'required_methods': list(METHODS), 'artifacts': artifacts,
                 'artifact_hashes_rechecked': verified,
                 'reconciliation': {'protected_inputs_unchanged': before_hashes == after},
                 'approval': 'Experimental calculation only; no selection, adoption or researcher validation'}
        (output/'artifact_manifest.json').write_text(json.dumps(index, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': summary['status'], 'methods': [
        {k: item.get(k) for k in ('method', 'execution', 'status')} for item in summary['methods']],
        'output': str(output), 'protected_bytes_unchanged': summary['protected_bytes_unchanged']}))
    return 0 if summary['status'] == 'COMPLETE_OUTCOME_INVENTORY' and summary['protected_bytes_unchanged'] else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1]/'outputs')
    args = parser.parse_args()
    raise SystemExit(run(args.output))
