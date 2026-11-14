"""Independent saved-evidence audit. Imports no calculator or runner; runs no solver."""
from pathlib import Path
import ast
import hashlib
import json
import numpy as np
import pandas as pd

WORK = Path(__file__).resolve().parents[1]
EVIDENCE = WORK.parents[1] / 'evidence'
PREVIOUS = EVIDENCE / 'discards_reconciliation_20261114'
POOLED = EVIDENCE / 'pooled_detritus_20261114'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def decode(value):
    if isinstance(value, list):
        return [decode(v) for v in value]
    if not isinstance(value, dict):
        return value
    kind = value.get('type')
    if kind == 'float':
        return {'nan': float('nan'), 'positive_infinity': float('inf'),
                'negative_infinity': -float('inf')}[value['value']]
    if kind == 'mapping':
        return {decode(k): decode(v) for k, v in value['items']}
    if kind == 'tuple':
        return tuple(decode(v) for v in value['items'])
    if kind == 'dataframe':
        frame = pd.DataFrame(decode(value['data']), index=decode(value['index']),
                             columns=decode(value['columns']))
        frame.index.names = decode(value['index_names'])
        frame.columns.names = decode(value['column_names'])
        for col, dtype in zip(frame.columns, value['dtypes']):
            frame[col] = frame[col].astype(dtype)
        return frame
    if kind == 'series':
        series = decode(value['frame']).iloc[:, 0]
        series.name = decode(value['name'])
        return series
    return {k: decode(v) for k, v in value.items()}


def close(a, b):
    return bool(np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float),
                           rtol=1e-11, atol=1e-11, equal_nan=True))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state_sha(raw):
    return hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True,
                                    allow_nan=False).encode('utf-8')).hexdigest()


def check_masks(value):
    count = 0
    if isinstance(value, dict):
        if value.get('type') == 'dataframe':
            assert value['shape'] == [len(value['index']), len(value['columns'])]
            assert len(value['data']) == len(value['index'])
            assert all(len(row) == len(value['columns']) for row in value['data'])
            for kind, mask in value['masks'].items():
                actual = [[x is None if kind == 'null' else isinstance(x, dict)
                           and x.get('type') == 'float' and x.get('value') == kind
                           for x in row] for row in value['data']]
                assert actual == mask, ('mask', kind)
            count += 1
        for child in value.values():
            count += check_masks(child)
    elif isinstance(value, list):
        count += sum(check_masks(child) for child in value)
    return count


def merged_columns(frame):
    result = frame.drop(index=35).copy()
    result[36] = result[35] + result[36]
    return result.drop(columns=35)


def main():
    original_path = PREVIOUS / 'outputs/diagnostics/source_exact_returns_to_36/post_returns_before_floor.json'
    separate_path = PREVIOUS / 'outputs/diagnostics/source_exact_returns_to_36/effective_floor_on.json'
    original = decode(read(original_path))['runtime']
    separate = decode(read(separate_path))['runtime']
    stage_path = WORK / 'outputs/merge_and_floor.json'
    stage_raw = read(stage_path)
    stage = decode(stage_raw)
    pre, eff = stage['pre_floor'], stage['effective']
    spec = decode(read(WORK / 'inputs/merge_specification.json'))
    g0, gp, ge = original['_groups_df'], pre['_groups_df'], eff['_groups_df']
    retained = g0.index.drop(35)
    non_det = g0.index.difference([35, 36])
    assert len(gp) == 36 and set(gp.index) == set(retained)
    assert gp.index[gp.trophic_info.eq('DET')].tolist() == [36]
    assert 37 in gp.index and 35 not in gp.index
    assert gp.loc[non_det].equals(g0.loc[non_det])
    extensive = ['p', 'q', 'catch', 'predation', 'growth', 'immigration', 'emigration',
                 'net_migration', 'respiration', 'egestion', 'M0', 'det_export']
    additive = ['catch', 'biomass', 'p', 'q', 'predation', 'M0', 'egestion',
                'respiration', 'biomass_accum', 'emigration', 'immigration',
                'net_migration', 'flow_to_det', 'detritus_import', 'det_export',
                'detritus_stock_residual']
    for key in extensive:
        assert pre[key].loc[non_det].equals(original[key].loc[non_det]), key
        assert close(pre[key][36], original[key].loc[[35, 36]].sum(skipna=False)), key
        assert close(pre[key].sum(skipna=False), original[key].sum(skipna=False)), key
    for col in additive:
        assert close(gp.loc[36, col], g0.loc[[35, 36], col].sum(skipna=False)), col
    for key in ['EE', 'GE', 'GS', 'TL', 'source_EE', 'source_M0']:
        assert pre[key].loc[non_det].equals(original[key].loc[non_det]), key
    assert np.isnan(pre['source_EE'][36]) and np.isnan(stage['source_view'].loc[36, 'ee'])
    assert close(pre['source_M0'][36], original['source_M0'].loc[[35, 36]].sum(skipna=False))
    assert stage['source_view'].loc[36, 'biomass_accum'] == 0
    assert spec['source_component_EE'].equals(original['source_EE'].loc[[35, 36]])
    assert spec['source_component_M0'].equals(original['source_M0'].loc[[35, 36]])
    for state in [pre, eff]:
        df = state['_groups_df']
        assert close(df.loc[36, 'pb'], state['p'][36] / df.loc[36, 'biomass'])
        assert close(df.loc[36, 'qb'], state['q'][36] / df.loc[36, 'biomass'])
        assert close(state['GE'][36], state['p'][36] / state['q'][36])
        assert close(state['GS'][36], state['egestion'][36] / state['q'][36])
        assert close(state['EE'][36], 1 - state['M0'][36] / state['p'][36])
        assert state['TL'][36] == 1
        assert state['seq2name'] == df.group_name.to_dict()
        assert state['name2seq'] == {name: i for i, name in state['seq2name'].items()}
        assert set(state['_DC'].index) == set(retained) == set(state['_DC'].columns)
        assert state['_DC'].loc[36].eq(0).all()
        assert state['_DC'].loc[non_det, 36].equals(original['_DC'].loc[non_det, [35, 36]].sum(axis=1))
        assert state['_DC'].loc[non_det, non_det].equals(original['_DC'].loc[non_det, non_det])
        assert close(state['_DC'].loc[non_det].sum(axis=1), original['_DC'].loc[non_det].sum(axis=1))
        assert state['_det_fate'].columns.tolist() == [36]
        assert state['_det_fate'][36].equals(original['_det_fate'].sum(axis=1).drop(index=35))
        assert original['_det_fate'].loc[[35, 36]].sum(axis=1).eq(1).all()
        assert original['M0'].loc[[35, 36]].eq(0).all() and original['egestion'].loc[[35, 36]].eq(0).all()
        expected_return = original['_discard_returns'].sum(axis=1).drop(index=35)
        expected_return.loc[36] += original['_discard_returns'].loc[35].sum()
        assert state['_discard_returns'].columns.tolist() == [36]
        assert state['_discard_returns'][36].equals(expected_return)
        assert close(state['_discard_returns'].to_numpy().sum(), original['_discard_returns'].to_numpy().sum())
        assert (state['_discard_returns'].sum(axis=1) <= state['catch'] + 1e-12).all()
        consumption = state['_DC'].loc[non_det].mul(state['q'].loc[non_det], axis=0)
        assert close(consumption.sum(axis=0).reindex(retained), state['predation'].reindex(retained))
        sink = state.get('external_mortality_export', state['p'] * 0)
        production = state['catch'] + state['predation'] + state['growth'] + state['net_migration'] + state['M0'] + sink
        assert close(production, state['p'])
        assert close(production + state['respiration'] + state['egestion'], state['q'])
    assert '_ee_floor_base' not in pre
    assert eff['use_ee_floor'] is True and eff['ee_floor'] == .1 and eff['ee_threshold'] == .1
    assert stage['floor_application_count'] == 1
    for key, raw in stage_raw['effective']['_ee_floor_base'].items():
        assert raw == stage_raw['pre_floor'][key], ('floor base', key)
    for key in extensive + ['EE', 'GE', 'GS', 'TL', 'external_mortality_export']:
        assert eff[key].loc[non_det].equals(separate[key].loc[non_det]), ('floor preservation', key)
    for key in extensive + ['external_mortality_export']:
        assert close(eff[key][36], separate[key].loc[[35, 36]].sum(skipna=False)), ('floor pool', key)
    assert eff['ee_floor_info']['affected_groups'] == separate['ee_floor_info']['affected_groups']
    assert eff['ee_floor_info']['negative_detritus_stock_residuals'] == {}
    assert eff['growth'][36] > 0
    effective_hash = state_sha(stage_raw['effective'])
    comparison = decode(read(WORK / 'outputs/comparison.json'))
    methods = []
    mask_count = check_masks(stage_raw)
    for method in ['GE', 'TE']:
        path = WORK / f'outputs/{method}_physical_merge_full_return.json'
        raw = read(path)
        row = decode(raw)
        pooled = decode(read(POOLED / f'outputs/{method}_pooled_full_return.json'))
        old = decode(read(PREVIOUS / f'outputs/diagnostics/source_exact_returns_to_36/{method}_full_return.json'))
        mask_count += check_masks(raw)
        assert row['execution'] == 'returned'
        assert row['runtime_before_sha256'] == row['runtime_after_sha256'] == effective_hash
        s, a, l = (row[k]['dataframe'] for k in ['SPPR', 'A', 'L'])
        assert s.shape == (36, 4) and a.shape == l.shape == (36, 36)
        assert set(s.index) == set(a.index) == set(a.columns) == set(l.index) == set(l.columns) == set(retained)
        assert set(s.columns) == {12, 22, 36, 37}
        assert np.isfinite(s.to_numpy()).all() and (s.to_numpy() >= 0).all()
        for key in ['SPPR', 'A', 'L']:
            mat = row[key]['dataframe']
            assert row[key]['row_names'] == [eff['seq2name'][i] for i in mat.index]
            assert row[key]['column_names'] == [eff['seq2name'][i] for i in mat.columns]
        expected = merged_columns(pooled['SPPR']['dataframe']).reindex(index=s.index, columns=s.columns)
        assert close(s, expected)
        for key, mat in [('A', a), ('L', l)]:
            exp = merged_columns(pooled[key]['dataframe']).reindex(index=mat.index, columns=mat.columns)
            assert close(mat, exp), ('operator merge', key)
        assert close(s.drop(columns=36), old['SPPR']['dataframe'].reindex(s.index).drop(columns=[35, 36]).reindex(columns=s.drop(columns=36).columns))
        null_relative = float(np.max(abs((l @ s.loc[l.columns]).to_numpy())) / max(1, np.max(abs(s.to_numpy()))))
        assert null_relative < 1e-11
        totals = s.sum(axis=1)
        for scope, cols in row['source_scopes'].items():
            assert row['scope_coefficients'][scope].equals(s[cols].sum(axis=1))
        pieces = {key: float(vector.dot(totals)) for key, vector in [
            ('total_catch', eff['catch']), ('internal_returns', eff['_discard_returns'].sum(axis=1)),
            ('external_catch', eff['catch']-eff['_discard_returns'].sum(axis=1)), ('growth', eff['growth']),
            ('net_migration', eff['net_migration']), ('det_export', eff['det_export']),
            ('external_mortality_sink', eff['external_mortality_export'])]}
        outflow = sum(pieces[k] for k in ['external_catch', 'growth', 'net_migration', 'det_export', 'external_mortality_sink'])
        inflow = float(eff['p'].loc[ge.index[ge.trophic_info.isin(['PP', 'Import'])]].sum())
        for key, value in pieces.items():
            assert close(value, row['weighted_budget'][key]), ('budget', key)
        assert close(outflow, inflow)
        diag = row['diagnostic']
        assert diag['status'] == 'OK' and diag['balance']['is_balanced'] is True
        assert diag['warnings'] == [] and diag['model_input']['negative_detritus_stock_residuals'] == {}
        assert diag['config']['det_collapse_mode'] == 'never'
        assert row['detritus_resolution_info']['method'] == 'single_detritus'
        assert close(pieces['total_catch'], diag['footprint']['ppr_all'])
        assert close(pieces['total_catch'], pooled['diagnostic']['footprint']['ppr_all'])
        table = row['group_comparison']
        assert all(table.loc[i, 'name'] == eff['seq2name'][i] for i in table.index)
        assert close(table.physical_merge_sppr, totals.reindex(table.index))
        assert close(table.catch, eff['catch'].reindex(table.index))
        summary = next(su for su in comparison['summaries'] if su['method'] == method)
        assert close(summary['physical_merge_ppr'], pieces['total_catch'])
        old_ppr = old['diagnostic']['footprint']['ppr_all']
        assert close(summary['percent_change_vs_separate'], (pieces['total_catch']/old_ppr-1)*100)
        methods.append({'method': method, 'passed': True, 'status': diag['status'],
                        'physical_merge_ppr': pieces['total_catch'], 'separate_ppr': old_ppr,
                        'percent_change_vs_separate': (pieces['total_catch']/old_ppr-1)*100,
                        'maximum_abs_SPPR_difference_from_attribution_pooling': float(np.max(abs(s.to_numpy()-expected.to_numpy()))),
                        'nullspace_relative_residual': null_relative,
                        'weighted_balance_relative_gap': abs(outflow-inflow)/inflow,
                        'merged_detritus_SPPR': float(s.loc[36, 36]),
                        'seabirds_id': 25, 'seabirds_SPPR': float(totals[25]),
                        'full_return_sha256': sha(path)})
    tree = ast.parse((WORK / 'code/run_physical_merge.py').read_text(encoding='utf-8'))
    floor_calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'apply_ee_floor']
    assert len(floor_calls) == 1
    provenance = read(WORK / 'outputs/provenance.json')
    assert provenance['floor_application_count'] == 1 and provenance['new_diagnostic_calls'] == 2
    assert provenance['effective_state_sha256'] == effective_hash
    protection = read(WORK / 'qa/protected_files.json')
    assert protection['all_protected_unchanged']
    result = {'passed': True,
              'scope': 'Independent audit of persisted source, transformed states and full-return arrays. No calculator or runner import; no new solver call.',
              'transformation_verified': True, 'source_missingness_preserved': True,
              'living_flows_preserved': True, 'floor_application_count': 1,
              'noncontiguous_ids_supported_in_saved_outputs': True,
              'typed_dataframes_masks_checked': mask_count,
              'merged_biomass': float(ge.loc[36, 'biomass']),
              'merged_inflow': float(eff['p'][36]), 'merged_consumption': float(eff['predation'][36]),
              'merged_stock_residual': float(eff['growth'][36]),
              'methods': methods, 'effective_state_sha256': effective_hash,
              'verification_code_sha256': sha(Path(__file__)),
              'interpretation_limit': 'OK applies to this complete-mixing scenario; it does not establish source provenance or ecological interchangeability.'}
    (WORK / 'qa/independent_physical_merge_verification.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
