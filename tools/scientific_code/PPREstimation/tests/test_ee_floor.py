"""Self-contained EE-floor conservation tests; no external model fixtures."""
import copy
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PPRCalculator import PPRCalculator


def state(ee=0., pools=1, fate=1.):
    ids = [3, 2, *range(1, 1-pools, -1)]
    df = pd.DataFrame(index=ids)
    df['group_name'] = ['Consumer', 'Producer', *[f'Detritus {n}' for n in range(pools)]]
    df['trophic_info'] = ['Regular', 'PP', *['DET']*pools]
    for key in ('catch', 'predation', 'biomass_accum', 'immigration', 'emigration',
                'net_migration', 'egestion', 'respiration', 'detritus_import'):
        df[key] = 0.
    df['biomass'] = 10.
    df['p'] = [10., 1000., *[0.]*pools]
    df['q'] = [100., 1000., *[0.]*pools]
    df['ee'] = [ee, .9, *[1.]*pools]
    df['M0'] = df.p*(1-df.ee)
    df['gs'] = [0.2, 0., *[0.]*pools]
    df.loc[3, ['egestion', 'respiration']] = [20., 70.]
    df.loc[3, 'biomass_accum'] = 10.*ee
    df.loc[2, 'biomass_accum'] = 810.
    dc = pd.DataFrame(0., index=ids, columns=ids)
    dc.loc[3, 2] = .9
    dc.loc[3, ids[2:]] = .1/pools
    routing = pd.DataFrame(0., index=ids, columns=ids[2:])
    routing.loc[[3, 2], :] = fate/pools
    return {'_groups_df': df, '_DC': dc, '_det_fate': routing,
            'n_groups': len(ids), 'seq2name': df.group_name.to_dict(),
            'name2seq': {v:k for k,v in df.group_name.items()}}


def calc(**kwargs):
    data = kwargs.pop('data', state())
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return PPRCalculator.from_dict(data, **kwargs)


def test_default_floor_changes_mortality_and_actual_balances():
    c = calc()
    assert c.EE[3] == .1
    assert c.M0[3] == 9.
    assert c.external_mortality_export[3] == 1.
    assert c.EE_before_floor[3] == 0.
    assert c.M0_before_floor[3] == 10.
    assert c.is_model_balanced()[0]
    sppr, _, _ = c.SPPR_new(TE_option='GE')
    assert c.is_sppr_balanced(sppr)[0]
    c.external_mortality_export.loc[3] = 0.
    assert not c.is_model_balanced()[0]
    assert not c.is_sppr_balanced(sppr)[0]


def test_off_retains_audited_living_and_detritus_values():
    c = calc(use_ee_floor=False)
    assert c.EE[3] == 0.
    assert c.M0[3] == 10.
    expected = 10.+1000.*(1-.9)+20.
    assert c.p[1] == c.q[1] == expected
    assert c.growth[1] == expected-10.
    assert c.external_mortality_export.eq(0).all()
    assert c.is_model_balanced()[0]


@pytest.mark.parametrize('ee', [0., 1e-12, .099, .1, .6, 1.])
def test_boundary_and_unchanged_living_flows(ee):
    off = calc(data=state(ee), use_ee_floor=False)
    on = calc(data=state(ee))
    assert on.EE[3] == pytest.approx(max(ee, .1))
    if ee >= .1:
        pd.testing.assert_series_equal(on.EE, off.EE)
    assert np.isclose(on.external_mortality_export[3], 10.*max(.1-ee, 0.))
    living = [3, 2]
    for name in ('p', 'q', 'catch', 'predation', 'growth', 'net_migration',
                 'immigration', 'emigration', 'egestion', 'respiration'):
        pd.testing.assert_series_equal(getattr(off, name).loc[living], getattr(on, name).loc[living])
    pd.testing.assert_frame_equal(off._DC, on._DC)
    pd.testing.assert_frame_equal(off._det_fate, on._det_fate)


@pytest.mark.parametrize('ee, expected', [
    (0., .95), (1e-12, .95), (.099, .95), (.1, .1), (.6, .6), (1., 1.),
])
def test_high_floor_only_replaces_groups_below_default_threshold(ee, expected):
    c = calc(data=state(ee), ee_floor=.95)
    assert c.EE[3] == pytest.approx(expected)
    assert c.EE[2] == .9  # A producer below the target, above the selection threshold.
    assert c.M0[3] == pytest.approx(10.*(1.-expected))
    assert c.external_mortality_export[3] == pytest.approx(10.*(expected-ee))
    assert c.is_model_balanced()[0]
    sppr, _, _ = c.SPPR_new(TE_option='GE')
    assert c.is_sppr_balanced(sppr)[0]


@pytest.mark.parametrize('ee, threshold, expected', [
    (.05, .05, .05), (.05, .051, .95), (.15, .2, .95), (0., 0., 0.),
])
def test_custom_threshold_selects_groups_independently_of_floor(ee, threshold, expected):
    c = calc(data=state(ee), ee_floor=.95, ee_threshold=threshold)
    assert c.EE[3] == pytest.approx(expected)
    assert c.EE[2] == .9


@pytest.mark.parametrize('threshold', [-.1, 1.1, np.nan, np.inf, True, '0.1'])
def test_invalid_selection_threshold_rejected_even_off(threshold):
    with pytest.raises(ValueError, match='ee_threshold'):
        calc(use_ee_floor=False, ee_threshold=threshold)


def test_threshold_survives_copies_and_reapplication_uses_original_ee():
    c = calc(data=state(.025), ee_floor=.95, ee_threshold=.05)
    before = c.get_groups_df()
    c.apply_ee_floor(True, .95, .05)
    pd.testing.assert_frame_equal(c.get_groups_df(), before)
    for copied in (copy.deepcopy(c), PPRCalculator.from_dict(c.__dict__),
                   PPRCalculator.from_dict(c.__dict__, normalize_DC=False), c.balance_model()):
        assert copied.ee_threshold == .05
        assert copied.EE[3] == .95
        assert copied.external_mortality_export[3] == pytest.approx(9.25)
        assert copied.is_model_balanced()[0]
    c.apply_ee_floor(True, .95, .01)
    assert c.EE[3] == pytest.approx(.025)
    assert c.external_mortality_export.eq(0.).all()
    assert c._initialization_settings['ee_threshold'] == .01
    c = PPRCalculator.from_dict(c.__dict__, ee_threshold=.05)
    assert c.EE_before_floor[3] == pytest.approx(.025)
    assert c.EE[3] == .95
    assert c.external_mortality_export[3] == pytest.approx(9.25)
    c.apply_ee_floor(False, .95, .05)
    assert c.EE[3] == pytest.approx(.025)
    assert c.external_mortality_export.eq(0.).all()


def test_custom_threshold_primary_producer_and_diagnostics():
    data = state(.15)
    data['_groups_df'].loc[2, ['ee', 'M0', 'biomass_accum']] = [.05, 950., -40.]
    c = calc(data=data, ee_floor=.95, ee_threshold=.1)
    assert c.EE[3] == pytest.approx(.15)
    assert c.EE[2] == .95
    assert c.M0[2] == pytest.approx(50.)
    assert c.external_mortality_export[2] == pytest.approx(900.)
    assert c.ee_floor_info['ee_threshold'] == .1
    report = c.diagnose_sppr(TE_option='GE')
    assert report['config']['ee_threshold'] == .1
    assert report['config']['ee_floor'] == .95


def test_from_modeldata_propagates_custom_threshold_without_changing_source():
    from ModelData import ModelData
    data = state(.15)
    model = ModelData.__new__(ModelData)
    model.groups_data = data['_groups_df'].copy()
    model.DC, model.det_fate = data['_DC'], data['_det_fate']
    model.seq2name, model.name2seq = data['seq2name'], data['name2seq']
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        c = PPRCalculator.from_modeldata(model, ee_floor=.95, ee_threshold=.2)
    assert c.EE[3] == .95
    assert c.EE[2] == .9
    pd.testing.assert_frame_equal(model.groups_data, data['_groups_df'])


@pytest.mark.parametrize('options, expected', [({}, .15), ({'ee_threshold': .2}, .95)])
def test_primary_constructor_uses_selection_threshold(monkeypatch, options, expected):
    from ModelData import ModelData
    data = state(.15)

    def load_memory(model, model_number):
        # Replace only file loading; the calculator runs its actual completion pipeline.
        model.groups_data = data['_groups_df'].copy()
        model.DC, model.det_fate = data['_DC'], data['_det_fate']
        model.seq2name, model.name2seq = data['seq2name'], data['name2seq']

    monkeypatch.setattr(ModelData, '__init__', load_memory)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        c = PPRCalculator('in-memory test input', ee_floor=.95, **options)
    assert c.EE[3] == pytest.approx(expected)
    assert c.EE[2] == .9


@pytest.mark.parametrize('ee, expected', [
    (np.nextafter(.1, 0.), .95), (.1, .1), (np.nextafter(.1, 1.), np.nextafter(.1, 1.)),
])
def test_threshold_comparison_does_not_exclude_representable_values_below_cutoff(ee, expected):
    data = state()
    data['_groups_df'].loc[2, ['ee', 'M0']] = [ee, 1000.*(1-ee)]
    c = calc(data=data, ee_floor=.95)
    assert c.EE[2] == expected


@pytest.mark.parametrize('pools', [1, 2])
def test_partial_routing_does_not_double_count_export(pools):
    off = calc(data=state(pools=pools, fate=.4), use_ee_floor=False)
    on = calc(data=state(pools=pools, fate=.4))
    np.testing.assert_allclose(off.q.loc[on.get_DET_seq()]-on.q.loc[on.get_DET_seq()], .4/pools)
    assert np.isclose(off.det_export[3]-on.det_export[3], .6)
    assert on.external_mortality_export[3] == 1.


def test_primary_producer_is_included():
    data = state()
    data['_groups_df'].loc[2, ['ee', 'M0', 'biomass_accum']] = [.05, 950., -40.]
    c = calc(data=data)
    assert c.EE[2] == .1
    assert c.M0[2] == 900.
    assert c.external_mortality_export[2] == 50.


def test_application_copy_sort_reload_and_balance_are_idempotent():
    c = calc()
    initial = c.get_groups_df()
    c.apply_ee_floor()
    c._sort()
    pd.testing.assert_frame_equal(c.get_groups_df(), initial)
    for copied in (copy.deepcopy(c), PPRCalculator.from_dict(copy.deepcopy(c.__dict__)), c.balance_model()):
        assert copied.external_mortality_export[3] == 1.
        assert copied.EE_before_floor[3] == 0.
        assert copied.M0_before_floor[3] == 10.
        assert copied.is_model_balanced()[0]
        assert copied.get_groups_df().loc[3, 'external_mortality_export'] == 1.


@pytest.mark.parametrize('floor', [-.1, 1.1, np.nan, np.inf, True, '0.1'])
def test_invalid_threshold_rejected_even_off(floor):
    with pytest.raises((ValueError, TypeError), match='ee_floor'):
        calc(use_ee_floor=False, ee_floor=floor)


def test_invalid_missing_ee_and_nonfeeding_pools_are_excluded():
    for value in (-.1, np.nan, np.inf, 1.1):
        data = state()
        data['_groups_df'].loc[3, 'ee'] = value
        data['_groups_df'].loc[3, 'M0'] = 10.
        c = calc(data=data)
        assert c.external_mortality_export[3] == 0.
        assert c.ee_floor_ledger.loc[3, 'reason'] == 'invalid_or_missing_input'
    for field in ('operational_pool', 'is_synthetic'):
        data = state()
        data['_groups_df'][field] = False
        data['_groups_df'].loc[3, field] = True
        c = calc(data=data)
        assert c.EE[3] == 0.
        assert c.external_mortality_export[3] == 0.
    data = state()
    data['_DC'].loc[3, :] = 0.
    c = calc(data=data)
    assert c.ee_floor_ledger.loc[3, 'reason'] == 'excluded_nonfeeding_pool'
    assert c.external_mortality_export[3] == 0.


def test_toggle_off_and_zero_floor_restore_baseline_and_balanced_copy():
    c = calc()
    c.apply_ee_floor(False, .1)
    assert c.EE[3] == 0.
    assert c.M0[3] == 10.
    assert c.external_mortality_export.eq(0).all()
    assert c.balanced_model.external_mortality_export.eq(0).all()
    c.apply_ee_floor(True, 0.)
    assert c.external_mortality_export.eq(0).all()
    c.apply_ee_floor(True, .1)
    assert c.external_mortality_export[3] == 1.


def imported_state():
    data = state()
    df = data['_groups_df']
    df.loc[4] = df.loc[2].copy()
    df.loc[4, ['group_name','trophic_info','p','q','ee','M0','biomass_accum']] = ['Imports','Import',20.,20.,1.,0.,0.]
    df.loc[2, 'biomass_accum'] = 830.
    data['_DC'] = data['_DC'].reindex(index=df.index, columns=df.index, fill_value=0.)
    data['_DC'].loc[3, [2,4]] = [.7,.2]
    data['_det_fate'] = data['_det_fate'].reindex(index=df.index, fill_value=0.)
    data.update(n_groups=4, seq2name=df.group_name.to_dict(), name2seq={v:k for k,v in df.group_name.items()})
    return data


def test_diet_import_branch_counts_the_sink_on_actual_symbolic_return():
    c = calc(data=imported_state())
    _, matrix, equations, variables = c.SPPR_symbolic(TE_option='GE', diet_import_option='as_DC')
    assert c.is_sppr_balanced(matrix, (equations, variables))[0]
    assert c.external_mortality_export[4] == 0.
    assert c.ee_floor_ledger.loc[4, 'reason'] == 'excluded_trophic_type'
    counted = c.is_sppr_balanced(matrix, (equations, variables))[2]
    c.external_mortality_export.loc[3] = 0.
    omitted = c.is_sppr_balanced(matrix, (equations, variables))[2]
    assert np.isclose(counted-omitted, matrix.sum(axis=1)[3])
    assert not c.is_sppr_balanced(matrix, (equations, variables))[0]


def test_monte_carlo_keeps_floor_and_sink_across_draws():
    c = calc()
    before = c.get_groups_df()
    saved = np.random.get_state()
    try:
        np.random.seed(42)
        c.monte_carlo_SPPR(n_samples=3, TE_option='GE', exclude_diverged=True, return_diagnostics=True)
    finally:
        np.random.set_state(saved)
    pd.testing.assert_frame_equal(c.get_groups_df(), before)
    assert c.external_mortality_export[3] == 1.


def test_completed_copy_explicit_loader_override_reinitializes_once():
    c = calc()
    copied = PPRCalculator.from_dict(copy.deepcopy(c.__dict__), normalize_DC=False)
    assert copied._initialization_settings['normalize_DC'] is False
    assert copied.external_mortality_export[3] == 1.
    assert copied.EE_before_floor[3] == 0.
    assert copied.M0_before_floor[3] == 10.
    assert copied.is_model_balanced()[0]


def test_skipped_living_table_cells_keep_source_missingness_and_rates():
    data = state()
    data['_groups_df'].loc[3, ['ee','qb']] = [np.nan, np.nan]
    off = calc(data=copy.deepcopy(data), use_ee_floor=False)
    on = calc(data=copy.deepcopy(data))
    assert pd.isna(on.source_EE[3])
    assert on.ee_floor_ledger.loc[3, 'reason'] == 'invalid_or_missing_input'
    pd.testing.assert_series_equal(off.get_groups_df().loc[3, off.get_groups_df().columns],
                                   on.get_groups_df().loc[3, off.get_groups_df().columns])


def test_negative_detritus_stock_residual_remains_explicit():
    data = state()
    # Baseline detritus supply is 130. Reducing M0 by one makes this
    # deliberately near-balanced stock residual negative without source supply.
    data['_groups_df'].loc[1, 'catch'] = 119.5
    c = calc(data=data)
    assert c.growth[1] < 0.
    assert c.ee_floor_info['negative_detritus_stock_residuals']
    assert c.external_mortality_export[3] == 1.


def test_forced_balance_solver_counts_sink_on_balanced_copy():
    original = calc()
    c = original.balance_model()
    matrix, detritus_scale = c._sample_SPPR_new_forced_balance(TE_option='GE')
    assert np.isfinite(detritus_scale)
    assert c.external_mortality_export[3] == 1.
    assert c.is_model_balanced()[0]
    assert c.is_sppr_balanced(matrix)[0]
    c.external_mortality_export.loc[3] = 0.
    assert not c.is_sppr_balanced(matrix)[0]
    assert original.external_mortality_export[3] == 1.


