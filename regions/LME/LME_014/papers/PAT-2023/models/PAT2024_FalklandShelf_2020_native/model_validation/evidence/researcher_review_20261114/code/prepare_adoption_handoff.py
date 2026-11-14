"""Prepare authenticated retained-output handoff. No calculator, solve or adoption."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
WORK = Path(__file__).resolve().parents[1]
MODEL = WORK.parents[2]
ROOT = next(p for p in WORK.parents if (p / 'Project.xlsx').exists())
sys.path.insert(0, str(ROOT))
from openpyxl import load_workbook
from tools.project_core.workbooks.workbooks import read_book, records, overview

FINAL = MODEL / 'model_validation/evidence/researcher_review_20261114'
EVIDENCE = MODEL / 'model_validation/evidence/discards_reconciliation_20261114'
SCENARIO = EVIDENCE / 'outputs/diagnostics/source_exact_returns_to_36'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def path_ref(path, pointer=None):
    value = {'path': Path(os.path.relpath(path, FINAL)).as_posix(), 'sha256': sha(path)}
    if pointer is not None:
        value['json_pointer'] = pointer
    return value


def typed_series(value):
    frame = value['frame']
    assert value['type'] == 'series' and frame['type'] == 'dataframe'
    return dict(zip(frame['index'], [row[0] for row in frame['data']]))


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-11)


def main():
    region = ROOT / 'regions/LME/LME_014/LME_014.xlsx'
    source_book = MODEL / 'sppr_source.xlsx'
    canonical = MODEL / 'model.json'
    manifest_path = MODEL / 'results/result_manifest.json'
    snapshot = MODEL / 'results/regional_snapshot.xlsx'
    provenance_path = EVIDENCE / 'outputs/diagnostics/run_provenance.json'
    ledger_path = EVIDENCE / 'outputs/source/source_fisheries_ledger.json'
    state_path = SCENARIO / 'effective_floor_on.json'
    pre_path = SCENARIO / 'post_returns_before_floor.json'
    old_initialization = MODEL / 'model_validation/evidence/ee_floor_on_review/initialization_and_floor.json'
    provenance = read(provenance_path)
    ledger = read(ledger_path)
    native_path = ROOT / ledger['source_identity']['path']
    protected_paths = [canonical, source_book, region, manifest_path, snapshot, state_path,
                       pre_path, provenance_path, ledger_path, native_path]
    protected_before = {Path(os.path.relpath(p, FINAL)).as_posix(): sha(p) for p in protected_paths}
    assert sha(canonical) == provenance['canonical_model_sha256'] == '9880e521a406974367530ffb06f13392714dba57b9645c38a1b1448926d83d17'
    assert sha(ledger_path) == provenance['source_ledger_sha256']
    assert sha(old_initialization) == provenance['prior_state_sha256']
    assert sha(native_path) == ledger['source_identity']['sha256']
    code = {}
    for name, expected in provenance['engine_hashes'].items():
        path = EVIDENCE / 'code/engine' / name
        assert sha(path) == expected
        code[name] = path_ref(path)
    runner = EVIDENCE / 'code/run_discard_comparison.py'
    assert sha(runner) == provenance['script_sha256']
    code['executed_runner'] = path_ref(runner)
    state = read(state_path)['runtime']
    names = dict(state['seq2name']['items'])
    assert len(names) == 37 and names[35] == 'Discards' and names[36] == 'Detritus'
    assert state['use_ee_floor'] is True and state['ee_floor'] == .1 and state['ee_threshold'] == .1
    frame = state['_groups_df']
    assert {i: row[frame['columns'].index('group_name')] for i, row in zip(frame['index'], frame['data'])} == names
    book = read_book(region, sheets=['Overview', 'Selected model groups', 'Diagnostics'])
    settings = overview(book)
    assert settings['results_model_id'] == MODEL.name
    regional_coefficients = {(r['group'], r['scope'], r['method']): r['sppr']
                             for r in records(book, 'Selected model groups', 'Group SPPR')}
    workbook = load_workbook(source_book, read_only=True, data_only=True)
    sheets = {sheet.title: list(sheet.values) for sheet in workbook}
    workbook.close()
    def table(name):
        rows = sheets[name]
        return [dict(zip(rows[0], row)) for row in rows[1:] if any(v is not None for v in row)]
    coefficient_records, method_records, comparison = [], {}, []
    for method, alias in [('GE', 'new_GE'), ('TE', 'new_TE_EEfix')]:
        output_path = SCENARIO / f'{method}_full_return.json'
        saved = read(output_path)
        diag = saved['diagnostic']
        assert saved['execution'] == 'returned' and diag['status'] == 'WARN'
        assert diag['config']['use_ee_floor'] is True and diag['config']['ee_floor'] == .1
        assert diag['config']['det_collapse_mode'] == 'never' and diag['config']['det_open_mode'] == 'none'
        matrix = saved['SPPR']['dataframe']
        assert matrix['shape'] == [37, 5]
        values = dict(zip(matrix['index'], matrix['data']))
        colpos = {c: i for i, c in enumerate(matrix['columns'])}
        for scope, sheet_name in [('all', 'sppr_all'), ('inner', 'sppr_inner'), ('PP', 'sppr_PP')]:
            new = typed_series(saved['scope_coefficients'][scope])
            old = {r['seq']: r[alias] for r in table(sheet_name)}
            changed = []
            for seq in sorted(new):
                value = new[seq]
                assert math.isfinite(value) and value >= 0
                expected = sum(values[seq][colpos[c]] for c in saved['source_scopes'][scope])
                assert close(value, expected)
                assert close(old[seq], regional_coefficients[(names[seq], scope, alias)])
                if not close(old[seq], value):
                    changed.append(seq)
                coefficient_records.append({'model_id': MODEL.name, 'group_id': seq,
                    'group_name': names[seq], 'scope': scope, 'method': alias,
                    'diagnostic_method': method, 'sppr': value,
                    'diagnostic_status': 'WARN', 'configuration_id': 'source_exact_returns_to_36'})
            comparison.append({'method': alias, 'scope': scope, 'checked': len(new),
                'changed_cells': len(changed), 'changed_group_ids': changed,
                'max_abs_difference': max(abs(old[i]-new[i]) for i in new)})
        catch = typed_series(state['catch'])
        computed_ppr = sum(catch[i] * sum(values[i]) for i in values)
        assert close(computed_ppr, diag['footprint']['ppr_all'])
        old_footprint = next(r for r in table('footprint') if r['method'] == alias)
        method_records[alias] = {'diagnostic_method': method,
            'saved_full_return': path_ref(output_path), 'diagnostic_json_pointer': '/diagnostic',
            'scope_coefficients_json_pointer': '/scope_coefficients',
            'SPPR_json_pointer': '/SPPR/dataframe', 'A_json_pointer': '/A/dataframe', 'L_json_pointer': '/L/dataframe',
            'actual_call': saved['call'], 'status': diag['status'], 'diagnostic': diag,
            'source_model_footprint': diag['footprint'], 'recomputed_catch_weighted_ppr_all': computed_ppr,
            'historical_workbook_footprint': old_footprint,
            'percent_change_from_historical_source_model_ppr': (diag['footprint']['ppr_all']/old_footprint['ppr_all']-1)*100}
    keys = {(r['model_id'], r['group_id'], r['scope'], r['method']) for r in coefficient_records}
    assert len(keys) == len(coefficient_records) == 222
    historical = []
    for scope, sheet_name in [('all', 'sppr_all'), ('inner', 'sppr_inner'), ('PP', 'sppr_PP')]:
        for row in table(sheet_name):
            value = row['new_WithEgestion']
            assert close(value, regional_coefficients[(row['group_name'], scope, 'new_WithEgestion')])
            historical.append({'model_id': MODEL.name, 'group_id': row['seq'], 'group_name': row['group_name'],
                               'scope': scope, 'method': 'new_WithEgestion', 'sppr': value})
    assert len(historical) == 111
    old_manifest = read(manifest_path)
    restrictions = [
        'Prepared handoff only; no numeric adoption, regional recalculation, review registration or publication was performed by this builder.',
        'Primary scope is only source_exact_returns_to_36 with separate Discards35 and Detritus36, EE floor ON0.1 threshold0.1, det_collapse_mode=never and det_open_mode=none.',
        'Both approved GE/TE diagnostics retain WARN: Discards35 physical stock residual is -0.20750363203745528 with no evidenced supply.',
        'Physical detritus merging and attribution pooling are sensitivity-only; neither result may replace these primary coefficients.',
        'Canonical scientific input, selections, catch, taxon mappings/weights and NPP must remain unchanged.',
        'Source-model fishery PPR totals are not regional annual totals; use retained regional catches and mappings for dependent arithmetic.',
        'Preserve existing provisional/mapping/missingness restrictions independently of the signed researcher review.',
        'new_WithEgestion is preserved below as historical only; it has not been rerun under the approved floor/return configuration and must not inherit new global flags or reviewed approval.',
        'If current storage cannot distinguish historical method settings, retain the historical data but mark its current-configuration availability pending rather than relabeling it.',
        'Source paper mass basis does not explicitly establish wet versus dry mass; project runtime wet-weight convention remains a disclosed limitation.',
        'Recheck current artifact hashes immediately before applying. The researcher DOCX/appendix are being updated separately and are intentionally outside this audit guard.'
    ]
    payload = {'schema_version': 1, 'kind': 'authenticated_retained_GE_TE_adoption_handoff',
        'prepared_utc': datetime.now(timezone.utc).isoformat(), 'unit_id': 'LME_014', 'model_id': MODEL.name,
        'prepared_only': True, 'adopted': False,
        'path_base': {'convention': 'All path fields are relative to the intended permanent evidence directory, not the outputs subdirectory.',
                      'repository_relative_directory': FINAL.relative_to(ROOT).as_posix()},
        'user_decision_context': {'reviewer': 'Ido Carmel', 'date': '2026-11-14',
            'primary_configuration': 'source_exact_returns_to_36',
            'physical_merge': 'sensitivity_only', 'signed_DOCX_binding': 'Root supplies final signed DOCX identity; this payload is not a review signature.'},
        'canonical_input': path_ref(canonical), 'native_source': path_ref(native_path),
        'execution_provenance': path_ref(provenance_path), 'executed_code': code,
        'actual_configuration': {'use_ee_floor': True, 'ee_floor': .1, 'ee_threshold': .1,
            'det_collapse_mode': 'never', 'det_open_mode': 'none', 'det_theta': 1., 'det_external_sppr': 0.,
            'detritus_ids': [35, 36], 'initialization': 'Restored authenticated completed initialization; no loader rerun.',
            'loader_settings': state['_initialization_settings'], 'floor_applications': 1,
            'fishery_return_total': ledger['totals']['discards'], 'fishery_return_destination': 36,
            'negative_discard_stock_residual': -.20750363203745528},
        'input_state_references': {'audited_initialization': path_ref(old_initialization),
            'source_reconciled_pre_floor': path_ref(pre_path, '/runtime'),
            'effective_runtime': path_ref(state_path, '/runtime'),
            'effective_37_group_metadata': path_ref(state_path, '/runtime/_groups_df'),
            'floor_ledger': path_ref(state_path, '/runtime/ee_floor_ledger'),
            'floor_info': path_ref(state_path, '/runtime/ee_floor_info'),
            'source_return_matrix': path_ref(EVIDENCE/'outputs/diagnostics/source_return_matrix.json', '/matrix'),
            'effective_return_matrix': path_ref(state_path, '/runtime/_discard_returns'),
            'source_fisheries_ledger': path_ref(ledger_path)},
        'method_aliases': {'GE': 'new_GE', 'TE': 'new_TE_EEfix'},
        'coefficient_records': coefficient_records, 'methods': method_records,
        'historical_WithEgestion_preservation': {'method': 'new_WithEgestion',
            'classification': 'historical_not_recomputed_not_approved_under_primary_configuration',
            'source_workbook_at_preparation': path_ref(source_book), 'execution_flags': None, 'code_identity': None,
            'historical_manifest': old_manifest, 'coefficient_records': historical,
            'model_health': next(r for r in table('model_health') if r['TE_option'] == 'With Egestion'),
            'footprint': next(r for r in table('footprint') if r['method'] == 'new_WithEgestion'),
            'historical_group_metadata': table('groups_df'), 'historical_run_notes': table('run_notes'),
            'matrix_availability': 'Historical workbook retains scope sums; no full per-source matrix is asserted in this preservation payload.'},
        'current_regional_status': {k: settings.get(k) for k in ['production_eligible', 'calculation_status', 'source_note', 'calculation_input_sha256', 'calculation_result_sha256']},
        'protected_artifact_hashes_at_preparation': protected_before,
        'adoption_operations_needed': [
            'Preserve current regional/source workbook bytes under existing transaction/snapshot policy before replacement.',
            'Adopt all222 keyed GE/TE scope coefficients and corresponding effective37group runtime metadata, diagnostics, floor ledger and actual provenance.',
            'Keep historical WithEgestion coefficients/diagnostics explicitly historical; preserve other unaffected data and mapping decisions.',
            'Recalculate affected taxon SPPR/PPR, annual PPR and PPR-NPP arithmetic from unchanged regional catches, mappings and NPP; invalidate genuinely affected historical sensitivity bounds.',
            'Update exact-model snapshot/result manifest and truthful per-method execution identity; do not substitute fresh loader/default-constructor provenance.',
            'Coordinator registers the final signed Word source and publishes only the exact LME_014/PAT2024_FalklandShelf_2020_native scope with normal hash/freshness/transaction guards.'
        ], 'restrictions': restrictions}
    protected_after = {Path(os.path.relpath(p, FINAL)).as_posix(): sha(p) for p in protected_paths}
    assert protected_before == protected_after
    output = WORK / 'outputs/adoption_handoff.json'
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    audit = {'schema_version': 1, 'passed': True, 'prepared_utc': payload['prepared_utc'],
        'scope': 'Read-only saved coefficient/runtime/source audit plus this prepared data handoff. No engine/runner imports and no fresh solves.',
        'path_base': payload['path_base'], 'primary_coefficient_count': 222,
        'historical_WithEgestion_coefficient_count': 111, 'unique_primary_keys': len(keys),
        'regional_matches_coefficient_workbook': True, 'comparison_to_approved_run': comparison,
        'changed_primary_coefficient_count': sum(r['changed_cells'] for r in comparison),
        'primary_coefficients_reconcile_full_saved_matrices': True,
        'source_model_footprints_reconcile_catch_dot_products': True,
        'source_and_engine_hashes_authenticated': True, 'protected_artifacts_unchanged': True,
        'protected_before': protected_before, 'protected_after': protected_after,
        'historical_manifest_flags_and_code_unknown': old_manifest.get('effective_flags') is None and old_manifest.get('code_identity') is None,
        'handoff_path': 'outputs/adoption_handoff.json', 'handoff_sha256': sha(output),
        'builder_path': 'code/prepare_adoption_handoff.py', 'builder_sha256': sha(Path(__file__)),
        'review_condition_parser_note': 'Conditions must be in parser-exported SPPR/GE/TE text; Review and reproducibility exports identity/date/verdict only. No dedicated numeric configuration predicate is asserted.'}
    (WORK/'qa/adoption_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'passed': True, 'primary_coefficients': 222, 'historical_WithEgestion_coefficients': 111,
                      'changed_primary_coefficients': audit['changed_primary_coefficient_count'],
                      'handoff_sha256': audit['handoff_sha256']}, indent=2))


if __name__ == '__main__':
    main()
