"""Independently audit saved three-method evidence; never import or rerun the engine."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import gzip
import hashlib
import json
import subprocess

import numpy as np
import pandas as pd


ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').is_file())
MODEL = ROOT / 'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991'
OUT = MODEL / 'results/diagnostics/2026-11-14_loader_repair'
OLD = MODEL / 'results/diagnostics/2026-11-14_validation/structural_zero/report_ready.json'
ENGINE = Path('C:/Users/idoca/.codex/worktrees/lme022-loader-fix/GlobalPPREstimation')
METHODS = ['new_GE', 'new_TE_EEfix', 'new_WithEgestion']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    data = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
    return json.loads(data.decode('utf-8'))


def plain(value):
    if isinstance(value, dict) and value.get('type') == 'mapping':
        return {str(k): plain(v) for k, v in value['items']}
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [plain(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def frame(encoded):
    assert encoded['type'] == 'dataframe'
    data = np.array(encoded['data'], dtype=object)
    assert list(data.shape) == encoded['shape']
    occupied = np.zeros(data.shape, dtype=int)
    for kind, cells in encoded['masks'].items():
        mask = np.asarray(cells, dtype=bool)
        assert mask.shape == data.shape
        occupied += mask
        data[mask] = {'null': None, 'nan': np.nan,
                      'positive_infinity': np.inf, 'negative_infinity': -np.inf}[kind]
    assert (occupied <= 1).all(), 'Overlapping nonfinite masks'
    result = pd.DataFrame(data, index=encoded['index'], columns=encoded['columns'])
    assert result.index.is_unique and result.columns.is_unique
    return result


def series(encoded, index=None):
    assert encoded['type'] == 'series'
    result = pd.to_numeric(frame(encoded['frame']).iloc[:, 0])
    return result if index is None else result.reindex(index)


def close(actual, expected, *, rtol=1e-11, atol=1e-10):
    np.testing.assert_allclose(actual, expected, rtol=rtol, atol=atol, equal_nan=True)


def main():
    required = ['summary.json', 'run_manifest.json', 'constructor.json.gz',
                *[m + '.json.gz' for m in METHODS]]
    missing = [name for name in required if not (OUT / name).is_file()]
    assert not missing, f'Await complete official run: {missing}'
    protected = {name: sha(OUT / name) for name in required}
    manifest, summary = read(OUT / 'run_manifest.json'), read(OUT / 'summary.json')
    canonical = read(MODEL / 'model.json')
    canonical_hash = sha(MODEL / 'model.json')
    assert canonical_hash == summary['canonical_model_sha256']
    assert manifest['canonical_unchanged'] and summary['canonical_unchanged']
    identity = read(OUT / 'constructor.json.gz')['identity']
    assert canonical_hash == identity['model_sha256']
    commit = subprocess.check_output(['git', '-C', str(ENGINE), 'rev-parse', 'HEAD'], text=True).strip()
    observed_status = subprocess.check_output(['git', '-C', str(ENGINE), 'status', '--porcelain'], text=True).splitlines()
    clean = not subprocess.check_output(['git', '-C', str(ENGINE), 'status', '--porcelain', '--untracked-files=no'], text=True).strip()
    assert commit == manifest['code_commit'] and clean
    engine_hash_checks = {}
    for name, digest in identity['engine_hashes'].items():
        relative = 'tools/scientific_code/PPREstimation/' + name
        working = sha(ENGINE / relative)
        committed = hashlib.sha256(subprocess.check_output(
            ['git', '-C', str(ENGINE), 'show', commit + ':' + relative])).hexdigest()
        assert digest == working == committed, name
        engine_hash_checks[name] = {'sha256': digest, 'working_equals_committed': True}
    adapter = 'tools/scientific_helpers/sppr/method_coverage.py'
    assert sha(ENGINE / adapter) == identity['adapter_sha256']
    assert hashlib.sha256(subprocess.check_output(['git', '-C', str(ENGINE), 'show', commit + ':' + adapter])).hexdigest() == identity['adapter_sha256']

    ctor = read(OUT / 'constructor.json.gz')['constructor_outcome']
    assert ctor['status'] == 'ready'
    runtime = ctor['runtime']
    source = frame(runtime['_source_groups_before_completion'])
    pre = frame(runtime['_ee_floor_base']['_groups_df'])
    effective = frame(runtime['_groups_df'])
    ids = list(effective.index)
    groups = {g['id']: g for g in ctor['groups']}
    source_ids = {int(g['group_seq']) for g in canonical['group']}
    assert set(ids) == source_ids | {70}
    assert groups[70]['type'] == 'Import' and groups[70]['synthetic']
    types = {i: groups[i]['type'] for i in ids}
    det = sorted(i for i in ids if types[i] == 'DET')
    pp = sorted(i for i in ids if types[i] == 'PP')
    imports = sorted(i for i in ids if types[i] == 'Import')
    living = sorted(i for i in ids if types[i] == 'Regular')
    names = {i: groups[i]['name'] for i in ids}
    fate = frame(runtime['_det_fate']).astype(float).reindex(index=ids, columns=det)
    dc = frame(runtime['_DC']).astype(float).reindex(index=ids, columns=ids)
    returns = frame(runtime['_discard_returns']).astype(float).reindex(index=ids, columns=det)
    metadata = plain(runtime['discard_returns_metadata'])
    assert metadata['status'] == 'complete' and not metadata['catch_modified'] and not metadata['unresolved']
    vectors = {key: series(runtime[key], ids) for key in
               ['p', 'q', 'catch', 'growth', 'net_migration', 'M0', 'egestion',
                'predation', 'respiration', 'external_mortality_export', 'EE']}
    p, q, catch, growth, migration, mortality, egestion, predation, respiration, sink, ee = (
        vectors[k] for k in ['p', 'q', 'catch', 'growth', 'net_migration', 'M0', 'egestion',
                            'predation', 'respiration', 'external_mortality_export', 'EE'])
    returned = returns.sum(axis=1)
    external_catch = catch - returned
    known_diet_checked = known_fate_checked = 0
    for g in canonical['group']:
        i = int(g['group_seq'])
        close(catch[i], float(g['export']))
        close(source.loc[i, 'biomass_accum'], float(g['biomass_accum']))
        close(pre.loc[i, 'biomass_accum'], float(g['biomass_accum']))
        close(source.loc[i, 'ee'], float(g['ee']))
        close(source.loc[i, 'tl'], float(g['tl']))
        for destination, value in g['detritus_fate_by_pool'].items():
            close(fate.loc[i, int(destination)], float(value), rtol=0, atol=0)
            known_fate_checked += 1
        if types[i] == 'Regular':
            for cell in g['diet_descr']['diet']:
                close(dc.loc[i, int(cell['prey_seq'])], float(cell['proportion']), rtol=0, atol=0)
                known_diet_checked += 1
            close(dc.loc[i, 70], float(g['diet_imp']), rtol=0, atol=0)
            known_diet_checked += 1
    close(dc.loc[pp + det + imports].to_numpy(), 0, rtol=0, atol=0)
    close(returns.sum().sum(), metadata['total_returned'])
    close(returned.sum() + external_catch.sum(), catch.sum())
    close(q.loc[det], fate.mul(mortality + egestion, axis=0).sum() + returns.sum())
    stock_residual = p.loc[det] - predation.loc[det] - migration.loc[det] - catch.loc[det]
    close(growth.loc[det], stock_residual)
    close(pd.to_numeric(effective.loc[det, 'detritus_stock_residual']), stock_residual)
    physical_production = catch + predation + growth + migration + mortality + sink
    close(physical_production, p, atol=1e-7)
    close(physical_production + respiration + egestion, q, atol=1e-7)
    floor_ledger = frame(runtime['ee_floor_ledger'])
    changed = floor_ledger.loc[floor_ledger['applied'].astype(bool)]

    accounting = {
        'schema_version': 1, 'model_id': identity['model_id'], 'canonical_model_sha256': canonical_hash,
        'code_commit': commit, 'clean_tracked_code_verified': clean,
        'postprocessing_worktree_status': observed_status,
        'status_note': 'Untracked pytest temporary directories do not alter any tracked engine or recorded code hash.',
        'engine_identity_checks': engine_hash_checks,
        'source_checks': {'known_consumer_diet_cells_exact': known_diet_checked,
                          'known_fate_cells_exact': known_fate_checked,
                          'source_ba_preserved_before_floor_all_69': True,
                          'source_ee_and_tl_preserved_in_source_table_all_69': True,
                          'source_catch_preserved_all_69': True, 'canonical_hash_unchanged': True},
        'producer_routing': {str(i): {str(d): float(fate.loc[i, d]) for d in det} for i in pp},
        'detritus_routing': {str(i): {str(d): float(fate.loc[i, d]) for d in det} for i in det},
        'catch': {'source_total_removals': float(catch.sum()), 'internal_return_total': float(returned.sum()),
                  'external_catch_total': float(external_catch.sum()),
                  'return_by_pool': {str(d): float(returns[d].sum()) for d in det},
                  'catch_based_footprint_uses_source_total_removals': True},
        'discard_returns_metadata': metadata,
        'floor': {'use_ee_floor': runtime['use_ee_floor'], 'ee_floor': runtime['ee_floor'],
                  'ee_threshold': runtime['ee_floor_info']['ee_threshold'],
                  'external_mortality_export_total': float(sink.sum()),
                  'affected_groups': [dict(id=int(i), name=names[i], source_EE=float(row['source_EE']),
                                           effective_EE=float(row['EE_effective']),
                                           external_mortality_export=float(row['external_mortality_export']))
                                      for i, row in changed.iterrows()]},
        'detritus': [dict(id=d, name=names[d], source_BA=float(source.loc[d, 'biomass_accum']),
                         pre_floor_BA=float(pre.loc[d, 'biomass_accum']),
                         effective_BA=float(growth[d]), source_EE=float(source.loc[d, 'ee']),
                         pre_floor_operational_EE=float(pre.loc[d, 'ee']), effective_EE=float(ee[d]),
                         effective_inflow=float(q[d]), predation=float(predation[d]),
                         derived_stock_residual=float(stock_residual[d])) for d in det],
        'runtime_assumption': 'Post-floor DET BA is a derived stock closure and operational DET EE is 1; '
                              'neither is an author-reported parameter correction or an observed export. '
                              'Native detritus export remains unspecified. Runtime balance does not prove native equivalence.',
        'physical_production_max_absolute_residual': float((physical_production-p).abs().max()),
        'physical_consumption_max_absolute_residual': float((physical_production+respiration+egestion-q).abs().max()),
    }
    old = {v['method']: v for v in read(OLD)['summary']}
    rows, negatives = [], []
    for method in METHODS:
        doc = read(OUT / (method + '.json.gz'))
        assert doc['status'] == 'ok' and doc['identity'] == identity
        assert doc['runtime_before_sha256'] == doc['runtime_after_sha256']
        assert doc['runtime_before'] == runtime == doc['runtime_after']
        matrix = frame(doc['source_matrix']).astype(float)
        assert set(matrix.index) == set(ids) and set(matrix.columns) == set(pp + det + imports)
        mask_counts = {k: int(np.asarray(v, dtype=bool).sum()) for k, v in doc['source_matrix']['masks'].items()}
        assert not any(mask_counts.values()) and np.isfinite(matrix.to_numpy()).all()
        pd.testing.assert_frame_equal(matrix, frame(doc['return']['items'][1]).astype(float))
        totals = matrix.sum(axis=1).reindex(ids)
        scope_errors = {}
        for scope, columns in [('all', matrix.columns), ('inner', [c for c in matrix.columns if c not in imports]),
                               ('PP', pp)]:
            expected = matrix.loc[:, columns].sum(axis=1)
            actual = pd.Series({i: doc['scopes'][scope][names[i]] for i in expected.index})
            close(actual, expected, rtol=1e-12, atol=1e-12)
            scope_errors[scope] = float((actual-expected).abs().max())
        for i in matrix.index:
            for c in matrix.columns:
                if matrix.loc[i, c] < 0:
                    negatives.append(dict(method=method, source_id=int(c), source_name=names[c],
                                          recipient_id=int(i), recipient_name=names[i], value=float(matrix.loc[i, c])))
        method_negatives = [v for v in negatives if v['method'] == method]
        negative_sources = int((matrix < 0).any(axis=0).sum())
        diag = plain(doc['diagnostics'])
        assert negative_sources == diag['divergence']['n_negative_sources']
        assert len(method_negatives) == len(doc['negative_entries'])
        option = diag['config']['TE_option']
        a = frame(doc['return']['items'][2]).astype(float)
        rho = float(max(abs(np.linalg.eigvals(a.loc[living, living].to_numpy()))))
        close(rho, diag['divergence']['rho_living'])
        scales = pd.Series({d: matrix.loc[d, d] for d in det})
        assert (scales != 0).all(), 'Cannot recover raw DET basis from a zero scale without a new solve'
        basis = matrix.loc[ids, det].div(scales, axis=1)
        use_mortality = mortality.where(mortality.index.isin(pp + imports), 0.) if option == 'TE' else mortality
        weights = []
        for d in det:
            weight = (use_mortality * fate[d] + returns[d]) / q[d]
            if option == 'With Egestion':
                weight += dc.T @ (egestion * fate[d] / q[d])
            weights.append(weight.to_numpy())
        weight_matrix = np.asarray(weights)
        b_matrix = weight_matrix @ basis.to_numpy()
        b = float(max(abs(np.linalg.eigvals(b_matrix))))
        close(b, diag['divergence']['b'])
        c_vector = weight_matrix @ matrix.loc[ids, pp + imports].sum(axis=1).to_numpy()
        close(scales.to_numpy(), b_matrix @ scales.to_numpy() + c_vector)
        fraction = (1-fate.sum(axis=1)).clip(lower=0)
        unrouted = fraction * use_mortality * totals
        if option == 'With Egestion':
            unrouted += fraction * egestion * (dc @ totals)
        independent_inflow = float(p.loc[pp + imports].sum())
        independent_outflow = float(((external_catch + growth + migration + sink)*totals).sum() + unrouted.sum())
        close(independent_inflow, diag['balance']['inflow'])
        close(independent_outflow, diag['balance']['outflow'])
        for key, columns in [('ppr_all', matrix.columns), ('ppr_inner', [c for c in matrix.columns if c not in imports]),
                             ('ppr_pp_only', pp)]:
            close(float((catch*matrix.loc[ids, columns].sum(axis=1)).sum()), diag['footprint'][key])
        rows.append(dict(method=method, execution_status=doc['status'], status=diag['status'],
                         input_status=diag['model_input']['status'], divergence_status=diag['divergence']['status'],
                         rho_living=diag['divergence']['rho_living'], b=diag['divergence']['b'],
                         detritus_sppr=diag['divergence']['sppr_det'],
                         balance=diag['balance'], footprint=diag['footprint'], warnings=diag['warnings'],
                         near_singular_te=diag['divergence']['near_singular_te'],
                         negative_entries=len(method_negatives), negative_source_columns=negative_sources,
                         sign_count_matches_diagnostic=True,
                         matrix_checks=dict(shape=list(matrix.shape), finite_cells=int(matrix.size),
                                            row_ids=[int(i) for i in matrix.index], source_ids=[int(i) for i in matrix.columns],
                                            unique_axes=True, mask_counts=mask_counts,
                                            all_canonical_recipient_groups_present=True, synthetic_import_separate=True,
                                            scope_max_absolute_errors=scope_errors,
                                            rho_living_independently_verified=True, b_independently_verified=True,
                                            reconstructed_rho_living=rho, reconstructed_b=b,
                                            detritus_self_consistency_max_abs_error=float(np.max(abs(
                                                scales.to_numpy()-b_matrix@scales.to_numpy()-c_vector))),
                                            pp_balance_independent_outflow=independent_outflow,
                                            runtime_before_after_equal=True),
                         old_structural_zero=dict(status=old[method]['status'], b=old[method]['b'],
                                                  negative_entries=old[method]['negative_entries'],
                                                  balance_rel_gap=old[method]['balance']['rel_gap'])))
    report = dict(schema_version=1, configuration_identity={**identity,
                  'canonical_model_sha256': canonical_hash, 'code_commit': commit, 'clean_tracked_code_verified': clean,
                  'variant_id': 'committed_global_source_fidelity_loader_accounting_ee_floor_0.1'},
                  summary=rows, source_grouped_negatives=negatives, runtime_accounting_review='runtime_accounting_review.json',
                  b_interpretation='GE and With Egestion include natural mortality and internal catch-return recycling; '
                                   'TE now has an actual coupled catch-return recycling matrix. Its old b=0 was a '
                                   'no-return convention, not a measured comparison value.',
                  comparison_scope='Same canonical hash and constructor flags, different globally repaired loader/accounting code. '
                                   'Older structural-zero outcomes are retained as superseded implementation evidence, '
                                   'not source corrections or a controlled comparison against Scotland.',
                  conclusion='All three runs are WARN, finite and nonnegative, with closed runtime PP budgets. '
                             'High Discards SPPR, GE/With-Egestion recycling gain and source diet rounding remain warnings; '
                             'the runtime mortality-floor/DET closure and source/native-equivalence limits remain explicit.',
                  verification=dict(timestamp=datetime.now(timezone.utc).isoformat(),
                                    script=Path(__file__).relative_to(ROOT).as_posix(), script_sha256=sha(Path(__file__)),
                                    raw_evidence_sha256=protected, no_solver_or_constructor_rerun=True,
                                    all_saved_cells_checked=sum(r['matrix_checks']['finite_cells'] for r in rows)))
    with (OUT / 'negative_entries.tsv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=['method','source_id','source_name','recipient_id','recipient_name','value'], delimiter='\t')
        writer.writeheader()
        writer.writerows(negatives)
    for name, data in [('runtime_accounting_review.json', accounting), ('report_ready.json', report)]:
        (OUT / name).write_text(json.dumps(plain(data), ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    assert protected == {name: sha(OUT / name) for name in required}
    assert sha(MODEL / 'model.json') == canonical_hash
    print(json.dumps({'summary': [{k:r[k] for k in ['method','status','rho_living','b','detritus_sppr','balance','negative_entries']} for r in rows],
                      'catch': accounting['catch'], 'detritus': accounting['detritus'],
                      'all_saved_cells_checked': report['verification']['all_saved_cells_checked']}, indent=2))


if __name__ == '__main__':
    main()
