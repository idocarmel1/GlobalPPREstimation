"""Source-preserving basal completion and independently checked PP export budgets."""
import copy

import numpy as np
import pandas as pd
import pytest

from test_ee_floor import calc, state, imported_state
from PPRCalculator import PPRCalculator


def open_state(producer_fate=1.):
    data = state(ee=.2)
    data['_groups_df'].loc[1, 'biomass_accum'] = np.nan
    data['_det_fate'].loc[3, :] = .25
    data['_det_fate'].loc[2, :] = producer_fate
    return data


@pytest.mark.parametrize('option,producer_fate,det_cost,consumer_cost', [
    ('GE', 1., 118/105, 9+118/105),
    ('GE', .6, 1.2, 10.2),
    ('TE', 1., 100/107, 45+5*100/107),
    ('TE', .6, 60/67, 45+5*60/67),
    ('With Egestion', 1., 118.9/104.9, 7.2+.8*118.9/104.9),
    ('With Egestion', .6, 78.9/64.9, 7.2+.8*78.9/64.9),
])
def test_partial_routing_export_closes_selected_pp_currency(option, producer_fate,
                                                           det_cost, consumer_cost):
    model = calc(data=open_state(producer_fate), use_ee_floor=False)
    report, matrix, _, _ = model.diagnose_sppr(TE_option=option, return_sppr=True)
    total = matrix.sum(axis=1)
    assert total[1] == pytest.approx(det_cost)
    assert total[3] == pytest.approx(consumer_cost)
    assert model.is_model_balanced()[0]
    assert model.is_sppr_balanced(matrix, TE_option=option) == pytest.approx((True, 1000., 1000.))
    assert report['balance']['is_balanced']


@pytest.mark.parametrize('option', ['GE', 'TE', 'With Egestion'])
def test_forced_balance_retains_unit_scale_for_already_balanced_open_system(option):
    data = open_state()
    data['_det_fate'].loc[3, :] = 0.
    model = calc(data=data, use_ee_floor=False)
    _, scale = model._sample_SPPR_new_forced_balance(TE_option=option)
    assert scale == pytest.approx(1.)


@pytest.mark.parametrize('method', ['SPPR_new', 'SPPR_EwE_Ulanowicz'])
def test_nonfeeding_null_placeholders_do_not_erase_basal_source(method):
    data = open_state()
    data['_DC'].loc[[1, 2], 3] = np.nan
    before = copy.deepcopy(data)
    model = calc(data=data, use_ee_floor=False)
    result, _, _ = getattr(model, method)(TE_option='GE')
    assert {1, 2}.issubset(result.columns)
    assert np.isfinite(result.to_numpy()).all()
    pd.testing.assert_frame_equal(data['_DC'], before['_DC'])
    assert model._DC.loc[[1, 2], 3].isna().all()


@pytest.mark.parametrize('underdetermined', [False, True])
def test_known_detritus_ba_is_not_replaced_by_stock_residual(underdetermined):
    data = open_state()
    data['_groups_df'].loc[1, 'biomass_accum'] = 4.
    model = calc(data=data, use_ee_floor=False, underdetermined=underdetermined)
    assert model.growth[1] == 4.
    assert model.get_groups_df().loc[1, 'detritus_stock_residual'] == pytest.approx(97.)
    assert not model.is_model_balanced()[0]
    assert data['_groups_df'].loc[1, 'biomass_accum'] == 4.


def test_source_known_detritus_ba_and_floor_residual_have_distinct_provenance():
    data = state(ee=0.)
    data['_groups_df'].loc[1, 'biomass_accum'] = 4.
    model = calc(data=data)
    assert model._source_groups_before_completion.loc[1, 'biomass_accum'] == 4.
    assert model._ee_floor_base['growth'][1] == 4.
    assert model.growth[1] == pytest.approx(119.)
    model.apply_ee_floor(False)
    assert model.growth[1] == 4.


def test_symbolic_import_export_values_entire_diet_including_external_prey():
    import sympy as sm
    data = imported_state()
    data['_groups_df'].loc[1, 'biomass_accum'] = np.nan
    data['_det_fate'].loc[3, :] = .25
    model = calc(data=data)
    _, matrix, equations, variables = model.SPPR_symbolic(
        TE_option='With Egestion', diet_import_option='as_DC')
    total = matrix.sum(axis=1)
    solved = dict(zip(variables, list(sm.linsolve(equations, variables))[0]))
    cost = float(solved[sm.Symbol('DIET_SPPR_Consumer')].subs({'SPPR_Producer': 1}))
    expected = (model._with_external_mortality(model.catch+model.growth+model.net_migration)
                .mul(total, fill_value=1).sum()+.75*model.M0[3]*total[3]+15*cost)
    _, _, outflow = model.is_sppr_balanced(matrix, (equations, variables), TE_option='With Egestion')
    assert outflow == pytest.approx(expected)
    assert not np.isclose(cost, (model._DC.loc[3, total.index]*total).sum())


def test_exporter_uses_method_specific_balance_without_fabricating_legacy_identity():
    from create_PPRS_excel import build_model_tables
    model = calc(data=open_state(), use_ee_floor=False)
    tables = build_model_tables(model, method_keys=['new_GE', 'new_TE_EEfix',
        'new_WithEgestion', 'SPPR_1986'], method_timeout=0)
    assert not any(issue['kind']=='sppr_balance' for issue in tables.issues)
    assert any(issue['kind']=='sppr_balance_unavailable' and issue['method']=='SPPR_1986'
               for issue in tables.issues)


def returned_state():
    data = state(ee=.2, pools=2)
    data['_groups_df'].loc[[1, 0], 'biomass_accum'] = np.nan
    data['_groups_df'].loc[3, ['catch', 'biomass_accum']] = [4., -2.]
    data['_det_fate'].loc[2, [1, 0]] = [.6, .4]
    data['_det_fate'].loc[3, [1, 0]] = [.25, .75]
    returns = pd.DataFrame(0., index=data['_groups_df'].index, columns=[1, 0])
    returns.loc[3] = [1., 2.]
    data['_discard_returns'] = returns
    data['discard_returns_metadata'] = {'status': 'complete'}
    return data


@pytest.mark.parametrize('option,consumer,det1,det0,gain', [
    ('GE', 10.671601786853861, 1.3531589023611998, 1.990044671346522, .08555088702147526),
    ('TE', 55.20401426119108, 1.6941766803116334, 2.387429024164796, .11612978524743231),
    ('With Egestion', 8.523031052101782, 1.3367056994686612, 1.9708719307857954, .08402194211017741),
])
def test_returned_catch_routes_once_and_carries_donor_ancestry(option,consumer,det1,det0,gain):
    # Hand solution: qDET=(68,63); Sconsumer=9+.5*(S1+S0) for GE,
    # 45+2.5*(S1+S0) for TE, 7.2+.4*(S1+S0) for With Egestion.
    # DET numerators (60+a*Sconsumer,40+b*Sconsumer), with a,b respectively
    # (3,8), (1,2), and (29/8,79/8); the return amounts are (1,2).
    data = returned_state()
    model = calc(data=data, use_ee_floor=False)
    assert model.catch[3] == 4.
    assert model.q[1] == pytest.approx(68.)
    assert model.q[0] == pytest.approx(63.)
    assert model.get_Z().loc[1].sum() == pytest.approx(68.)
    assert model.get_Z().loc[0].sum() == pytest.approx(63.)
    assert model.is_model_balanced()[0]
    report, matrix, _, _ = model.diagnose_sppr(TE_option=option, return_sppr=True)
    total = matrix.sum(axis=1)
    assert total[3] == pytest.approx(consumer)
    assert total[1] == pytest.approx(det1)
    assert total[0] == pytest.approx(det0)
    assert model.is_sppr_balanced(matrix, TE_option=option) == pytest.approx((True,1000.,1000.))
    assert report['divergence']['b'] == pytest.approx(gain)
    assert data['_groups_df'].loc[3,'catch'] == 4.


@pytest.mark.parametrize('option', ['GE', 'TE', 'With Egestion'])
def test_explicit_zero_return_preserves_legacy_result(option):
    data = open_state()
    no_return = calc(data=data, use_ee_floor=False)
    data['_discard_returns'] = pd.DataFrame(0., index=[3,2,1], columns=[1])
    zero_return = calc(data=data, use_ee_floor=False)
    pd.testing.assert_frame_equal(no_return.SPPR_new(TE_option=option)[0],
                                  zero_return.SPPR_new(TE_option=option)[0])


def test_incomplete_return_evidence_cannot_silently_produce_result():
    data = returned_state()
    data['_discard_returns'] = None
    data['discard_returns_metadata'] = {'status':'incomplete'}
    with pytest.raises(ValueError, match='discard'):
        calc(data=data)


def test_symbolic_methods_explicitly_reject_unsupported_nonzero_returns():
    model = calc(data=returned_state(), use_ee_floor=False)
    with pytest.raises(NotImplementedError, match='discard'):
        model.SPPR_symbolic(TE_option='GE')


def test_floor_keeps_internal_returns_once_when_refreshing_pool_supply():
    data = returned_state()
    data['_groups_df'].loc[3, ['ee', 'M0', 'biomass_accum']] = [0., 10., -4.]
    model = calc(data=data)
    assert model.external_mortality_export[3] == 1.
    assert model.q[1] == pytest.approx(68.25)
    assert model.q[0] == pytest.approx(63.75)
    assert model.catch[3] == 4.
    assert model._external_catch()[3] == 1.
    for option in ('GE', 'TE', 'With Egestion'):
        matrix = model.SPPR_new(TE_option=option)[0]
        assert model.is_sppr_balanced(matrix, TE_option=option)[0]
    model.apply_ee_floor(False)
    assert model.q[1] == pytest.approx(68.5)
    assert model.q[0] == pytest.approx(64.5)


def test_return_coupling_cannot_silently_ignore_requested_zero_te_recredit():
    data = returned_state()
    data['_groups_df'].loc[3, ['ee', 'M0', 'biomass_accum']] = [0., 10., -4.]
    model = calc(data=data, use_ee_floor=False)
    with pytest.raises(NotImplementedError, match='dead-end'):
        model.SPPR_new(TE_option='TE', fix_EE_0_cases=True)


def test_complete_return_metadata_requires_its_matrix():
    data = returned_state()
    data['_discard_returns'] = None
    with pytest.raises(ValueError, match='discard'):
        calc(data=data)


def test_flat_diagnostics_recurses_into_assumption_ledger_and_counts_lists():
    report = {
        'config': {'ee_floor_assumption': {
            'affected_groups': [], 'negative_detritus_stock_residuals': {},
            'nested': {'groups': [3, 4], 'enabled': True}}},
        'divergence': {'b': .25, 'sppr_det': {1: 1.5}},
        'warnings': ['example'],
    }
    assert PPRCalculator._flatten_diagnostics(report) == {
        'config_ee_floor_assumption_n_affected_groups': 0,
        'config_ee_floor_assumption_nested_n_groups': 2,
        'config_ee_floor_assumption_nested_enabled': True,
        'divergence_b': .25, 'divergence_sppr_det_1': 1.5, 'n_warnings': 1,
    }
