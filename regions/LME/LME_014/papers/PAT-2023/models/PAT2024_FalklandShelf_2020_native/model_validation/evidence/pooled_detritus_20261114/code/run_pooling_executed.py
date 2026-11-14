"""Bounded GE/TE pooled-attribution sensitivity; no parameter or result adoption."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
import importlib.util
import hashlib
import json
import os
import platform
import sys
import time
import traceback
import warnings

HERE = Path(__file__).resolve().parents[1]
MODEL = HERE.parents[2]
ROOT = next(p for p in HERE.parents if (p / 'Project.xlsx').exists())
PREVIOUS = MODEL / 'model_validation/evidence/discards_reconciliation_20261114'
OUT = HERE / 'outputs'
spec = importlib.util.spec_from_file_location('previous_run_helpers', PREVIOUS / 'code/run_discard_comparison.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
import numpy as np
import pandas as pd
sys.path.insert(0, str(PREVIOUS / 'code/engine'))
from PPRCalculator import PPRCalculator, DEFAULT_DIAGNOSTIC_THRESHOLDS


def load(path):
    return helper.decode(json.loads(path.read_text(encoding='utf-8')))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return Path(os.path.relpath(path, HERE)).as_posix()


def main():
    start = datetime.now(timezone.utc).isoformat()
    canonical = MODEL / 'model.json'
    state_path = PREVIOUS / 'outputs/diagnostics/source_exact_returns_to_36/effective_floor_on.json'
    source_path = MODEL / 'model_validation/evidence/ee_floor_on_review/initialization_and_floor.json'
    baseline_paths = {m: PREVIOUS / f'outputs/diagnostics/source_exact_returns_to_36/{m}_full_return.json' for m in ['GE', 'TE']}
    protected_paths = [canonical, MODEL / 'model_notes.md', MODEL / 'sppr_source.xlsx',
                       MODEL / 'model_validation/validation.docx', MODEL / 'model_validation/taxon_mapping.xlsx',
                       ROOT / 'regions/LME/LME_014/LME_014.xlsx', state_path, source_path, *baseline_paths.values()]
    protected = {rel(p): sha(p) for p in protected_paths}
    assert sha(canonical) == '9880e521a406974367530ffb06f13392714dba57b9645c38a1b1448926d83d17'
    for name, digest in helper.EXPECTED.items():
        assert sha(PREVIOUS / 'code/engine' / name) == digest
    saved = load(state_path)
    state = saved['runtime']
    source = load(source_path)['source']['groups_before_calculator_completion']
    assert state['use_ee_floor'] is True and state['ee_floor'] == .1
    assert np.isclose(state['_discard_returns'].to_numpy().sum(), .005859524956463247, atol=1e-15)
    assert state['_discard_returns'][35].eq(0).all()
    summaries = []
    negative_entries = []
    for option in ['GE', 'TE']:
        model = PPRCalculator.__new__(PPRCalculator)
        model.__dict__.update(deepcopy(state))
        model.n_groups = len(model._groups_df)
        model.is_underdetermined = False
        model.n_balance_runs = 0
        model._source_groups_before_completion = source.copy(deep=True)
        model._model = SimpleNamespace(groups_data=source.copy(deep=True), model_name=MODEL.name, model_year='2020')
        assert model.get_DET_seq() == [35, 36]
        before_runtime = helper.encode(helper.runtime(model))
        call = dict(TE_option=option, short=False, flat=False, return_sppr=True,
                    det_collapse_mode='always', det_open_mode='none')
        record = {'method': option, 'call': call, 'execution': 'not_run',
                  'scenario': 'source_exact_returns_to_36_pooled_attribution',
                  'floor': 'Restored authenticated effective ON state; floor not applied again.'}
        begun = time.perf_counter()
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                diagnostic, sppr, a, l = model.diagnose_sppr(**call)
            record.update(execution='returned', diagnostic=diagnostic,
                          detritus_resolution_info=deepcopy(model.detritus_resolution_info),
                          SPPR=helper.matrix(sppr, model, 'SPPR'), A=helper.matrix(a, model, 'A'),
                          L=helper.matrix(l, model, 'L'), warnings=[str(w.message) for w in caught])
            assert model.detritus_resolution_info['method'] == 'pooled_detritus_scaling'
            baseline = load(baseline_paths[option])
            baseline_sppr = baseline['SPPR']['dataframe']
            assert sppr.index.equals(baseline_sppr.index) and sppr.columns.equals(baseline_sppr.columns)
            scopes = baseline['source_scopes']
            record['source_scopes'] = scopes
            record['scope_coefficients'] = {scope: sppr[cols].sum(axis=1) for scope, cols in scopes.items()}
            totals = sppr.sum(axis=1)
            old_totals = baseline_sppr.sum(axis=1)
            group_changes = pd.DataFrame({'name': [model.seq2name[g] for g in sppr.index],
                'catch': model.catch, 'separate_sppr': old_totals, 'pooled_sppr': totals,
                'sppr_delta': totals-old_totals,
                'separate_catch_ppr': model.catch*old_totals, 'pooled_catch_ppr': model.catch*totals})
            group_changes['catch_ppr_delta'] = group_changes.pooled_catch_ppr-group_changes.separate_catch_ppr
            group_changes['sppr_percent_change'] = ((totals/old_totals)-1)*100
            record['group_changes'] = group_changes
            pieces = {key: float(vector.dot(totals)) for key, vector in [
                ('total_catch', model.catch), ('internal_return', model._discard_return_matrix().sum(axis=1)),
                ('external_catch', model._external_catch()), ('growth', model.growth),
                ('net_migration', model.net_migration), ('det_export', model.det_export),
                ('external_mortality_sink', model.external_mortality_export)]}
            pieces['outflow'] = sum(pieces[k] for k in ['external_catch', 'growth', 'net_migration', 'det_export', 'external_mortality_sink'])
            pieces['inflow'] = float(model.p.loc[model.get_PP_seq()+model.get_Import_seq()].sum())
            record['weighted_budget'] = pieces
            record['checks'] = {
                'runtime_unchanged': before_runtime == helper.encode(helper.runtime(model)),
                'A_unchanged': a.equals(baseline['A']['dataframe']),
                'L_unchanged': l.equals(baseline['L']['dataframe']),
                'non_detritus_source_columns_unchanged': sppr.drop(columns=[35,36]).equals(baseline_sppr.drop(columns=[35,36])),
                'all_SPPR_finite': bool(np.isfinite(sppr.to_numpy()).all()),
                'no_negative_SPPR': bool((sppr.to_numpy() >= -1e-10).all()),
                'fishery_total_reconciles': bool(np.isclose(pieces['total_catch'], diagnostic['footprint']['ppr_all'], rtol=1e-12, atol=1e-12)),
                'external_plus_return_reconciles': bool(np.isclose(pieces['total_catch'], pieces['external_catch']+pieces['internal_return'], rtol=1e-12, atol=1e-12))}
            for label, frame in [('SPPR', sppr), ('A', a), ('L', l)]:
                for i,j in zip(*np.where(frame.to_numpy() < -1e-10)):
                    row, col = frame.index[i], frame.columns[j]
                    negative_entries.append({'method': option, 'matrix': label, 'row_id': int(row),
                        'row_name': model.seq2name[row], 'column_id': int(col),
                        'column_name': model.seq2name[col], 'value': float(frame.iloc[i,j]), 'tolerance': 1e-10})
            old = baseline['diagnostic']['footprint']['ppr_all']
            new = diagnostic['footprint']['ppr_all']
            summaries.append({'method': option, 'separate_ppr': old, 'pooled_ppr': new,
                'absolute_change': new-old, 'percent_change': (new/old-1)*100,
                'status': diagnostic['status'], 'balance': diagnostic['balance'],
                'detritus_resolution_info': record['detritus_resolution_info'], 'checks': record['checks'],
                'separate_sppr_det': baseline['diagnostic']['divergence']['sppr_det'],
                'pooled_sppr_det': diagnostic['divergence']['sppr_det'],
                'pp_only_ppr': diagnostic['footprint']['ppr_pp_only'],
                'top_catch_ppr_changes': group_changes.sort_values('catch_ppr_delta', ascending=False).head(8)})
        except Exception:
            record.update(execution='exception', exception=traceback.format_exc())
        record['seconds'] = time.perf_counter()-begun
        record['runtime_after'] = helper.runtime(model)
        helper.save(OUT / f'{option}_pooled_full_return.json', record)
        print(option, record['execution'], record.get('diagnostic', {}).get('status'), record.get('exception',''), flush=True)
    after = {rel(p): sha(p) for p in protected_paths}
    helper.save(HERE / 'qa/protected_files.json', {'before': protected, 'after': after, 'unchanged': protected==after,
        'shared_write_scope': 'No Project.xlsx, map, trends, shared code or coordinator messaging.'})
    helper.save(OUT / 'negative_entries.json', {'entries': negative_entries, 'negative_SPPR_entries': [r for r in negative_entries if r['matrix']=='SPPR'],
        'operator_note': 'Negative L living diagonal entries are equation terms, not negative SPPR.'})
    helper.save(OUT / 'comparison.json', {'model_id': MODEL.name, 'run_id': HERE.name,
        'scenarios': 'Source-reconciled separate pools (reused) versus pooled SPPR attribution (new).',
        'summaries': summaries, 'physical_pool_budgets_unchanged': saved['pool_budget'],
        'aggregate_inflow': sum(p['runtime_p'] for p in saved['pool_budget']),
        'aggregate_consumption': sum(p['predation_outflow'] for p in saved['pool_budget']),
        'aggregate_residual': sum(p['detritus_stock_residual'] for p in saved['pool_budget']),
        'limit': 'Existing collapse option shares detritus SPPR scaling; it does not merge physical group identities or document missing offal.'})
    helper.save(OUT / 'provenance.json', {'started_utc': start, 'finished_utc': datetime.now(timezone.utc).isoformat(),
        'python': sys.version, 'platform': platform.platform(), 'numpy': np.__version__, 'pandas': pd.__version__,
        'engine_sha256': helper.EXPECTED, 'engine_location': rel(PREVIOUS/'code/engine'),
        'effective_state': rel(state_path), 'effective_state_sha256': sha(state_path),
        'source_initialization': rel(source_path), 'source_initialization_sha256': sha(source_path),
        'canonical': rel(canonical), 'canonical_sha256': sha(canonical),
        'reused_baselines': {m: {'path': rel(p), 'sha256': sha(p)} for m,p in baseline_paths.items()},
        'thresholds': DEFAULT_DIAGNOSTIC_THRESHOLDS, 'methods': ['GE','TE'],
        'new_solver_calls': 2, 'runtime_floor_application_count': 0, 'inherited_floor_application_count': 1,
        'group_crosswalk': [{'id':35,'name':'Discards','pool':'shared DET attribution'}, {'id':36,'name':'Detritus','pool':'shared DET attribution'}],
        'units': 'Source model mass/area/year; source t/km² over 2020, wet versus dry mass not explicitly established.'})
    assert protected==after
    assert len(summaries)==2 and all(all(s['checks'].values()) for s in summaries)
    print(json.dumps(helper.encode(summaries), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
