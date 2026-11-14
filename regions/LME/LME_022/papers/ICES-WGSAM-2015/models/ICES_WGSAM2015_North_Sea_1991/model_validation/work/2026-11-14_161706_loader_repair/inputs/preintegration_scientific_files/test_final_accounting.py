"""Final-flow BA completion and formulation-specific external export accounting."""
import copy

import numpy as np
import pandas as pd
import pytest

from test_lim_state import seed_state
from test_ee_floor import calc, state, imported_state
from PPRCalculator import PPRCalculator


def test_refreshes_only_source_missing_ba_after_final_consumption():
    seed = seed_state()
    seed['_groups_df'].loc[1, 'biomass_accum'] = np.nan
    seed['_groups_df'].loc[4, 'biomass_accum'] = 1.  # unused import production exits as BA
    before = copy.deepcopy(seed)
    legacy = PPRCalculator.from_dict(seed, underdetermined=True,
                                    zero_biomass_accum=False, use_ee_floor=False)
    model = PPRCalculator.from_dict(seed, underdetermined=True,
        zero_biomass_accum=False, use_ee_floor=False, refresh_missing_biomass_accum=True)
    assert legacy.growth.loc[1] == 8.
    assert model.growth.loc[1] == pytest.approx(-7.)
    assert model.growth.loc[2] == 1.5  # source-reported BA remains fixed
    assert model.is_model_balanced()[0]
    assert model.missing_biomass_accum_ledger.loc[1, 'applied']
    assert model.missing_biomass_accum_ledger.loc[2, 'reason'] == 'source_ba_known'
    for field in ('p', 'q', 'M0', 'egestion', 'respiration', 'predation'):
        pd.testing.assert_series_equal(getattr(model, field), getattr(legacy, field))
    pd.testing.assert_frame_equal(seed['_groups_df'], before['_groups_df'])
    copied = PPRCalculator.from_dict(model.__dict__)
    assert copied._initialization_settings['refresh_missing_biomass_accum'] is True
    pd.testing.assert_series_equal(copied.growth, model.growth)


def test_zero_ba_default_and_known_ba_are_not_repaired():
    for source_ba, zero_ba, expected in [(np.nan, True, 0.), (8., False, 8.)]:
        seed = seed_state()
        seed['_groups_df'].loc[1, 'biomass_accum'] = source_ba
        model = PPRCalculator.from_dict(seed, underdetermined=True,
            zero_biomass_accum=zero_ba, use_ee_floor=False,
            refresh_missing_biomass_accum=True)
        assert model.growth.loc[1] == expected
        assert not model.is_model_balanced()[0]


def test_failed_consumption_does_not_turn_unknown_prey_ba_into_balanced_result():
    seed = seed_state(egestion=0.)
    seed['_groups_df'].loc[1, 'biomass_accum'] = np.nan
    model = PPRCalculator.from_dict(seed, underdetermined=True,
        zero_biomass_accum=False, use_ee_floor=False, refresh_missing_biomass_accum=True)
    assert model.missing_biomass_accum_ledger.loc[1, 'reason'] == 'incomplete_final_predation'
    assert not model.missing_biomass_accum_ledger.loc[1, 'applied']


@pytest.mark.parametrize('option', ['GE', 'TE', 'With Egestion'])
@pytest.mark.parametrize('producer_fate', [1., .6])
def test_open_routing_budget_closes_without_double_counting(option, producer_fate):
    data = state(ee=.2)
    data['_det_fate'].loc[3, :] = .25
    data['_det_fate'].loc[2, :] = producer_fate
    model = calc(data=data)
    report, matrix, _, _ = model.diagnose_sppr(TE_option=option, return_sppr=True)
    assert model.is_model_balanced()[0]
    assert model.is_sppr_balanced(matrix, TE_option=option)[0]
    assert report['balance']['is_balanced']
    total = matrix.sum(axis=1)
    old = (model._with_external_mortality(model.catch + model.growth + model.net_migration)*total).sum()
    exported = (1-producer_fate)*model.M0[2]*total[2]
    if option != 'TE':
        exported += .75*model.M0[3]*total[3]
    if option == 'With Egestion':
        exported += .75*model.egestion[3]*(model._DC@total)[3]
    assert report['balance']['outflow'] == pytest.approx(old+exported)
    if option == 'GE':
        assert not np.isclose(exported, (model.det_export*total).sum())


@pytest.mark.parametrize('option', ['GE', 'TE', 'With Egestion'])
def test_forced_balance_uses_same_formulation_export_identity(option):
    data = state(ee=.2)
    data['_det_fate'].loc[3, :] = 0.
    model = calc(data=data)
    matrix, scale = model._sample_SPPR_new_forced_balance(TE_option=option)
    assert scale == pytest.approx(1.)
    assert model.is_sppr_balanced(matrix, TE_option=option)[0]


@pytest.mark.parametrize('option', ['GE', 'TE', 'With Egestion'])
def test_symbolic_import_checker_uses_selected_export_weight(option):
    data = imported_state()
    data['_det_fate'].loc[3, :] = .25
    model = calc(data=data)
    import sympy as sm
    _, matrix, equations, variables = model.SPPR_symbolic(TE_option=option, diet_import_option='as_DC')
    assert 4 not in matrix.index  # actual as_DC numeric return omits the Import recipient
    actual = model.is_sppr_balanced(matrix, (equations, variables), TE_option=option)
    total = matrix.sum(axis=1)
    solved = dict(zip(variables, list(sm.linsolve(equations, variables))[0]))
    pp = {sm.Symbol('SPPR_' + model.seq2name[s].replace(' ', '_')): 1
          for s in model.get_PP_seq()}
    diet_cost = float(solved[sm.Symbol('DIET_SPPR_Consumer')].subs(pp))
    exports = 0. if option == 'TE' else .75*model.M0[3]*total[3]
    if option == 'With Egestion':
        exports += .75*model.egestion[3]*diet_cost
        truncated = (model._DC.loc[3, total.index]*total).sum()
        assert not np.isclose(diet_cost, truncated)
    base = model._with_external_mortality(model.catch + model.growth + model.net_migration)
    assert actual[2] == pytest.approx(base.mul(total, fill_value=1).sum()+exports)


def test_export_registry_declares_actual_formulation_and_import_basis():
    from create_PPRS_excel import SPEC_BY_KEY
    assert SPEC_BY_KEY['new_TE_EEfix'].balance_TE_option == 'TE'
    assert SPEC_BY_KEY['new_GE'].balance_TE_option == 'GE'
    assert SPEC_BY_KEY['sym_WithEgestion_asDC'].balance_TE_option == 'With Egestion'
    assert SPEC_BY_KEY['sym_WithEgestion_asDC'].balance_diet_import
    assert not SPEC_BY_KEY['sym_GE_asPP'].balance_diet_import
    assert SPEC_BY_KEY['MC_new_GE'].balance_TE_option is None
    assert SPEC_BY_KEY['SPPR_1986'].balance_TE_option is None


def test_exporter_preserves_absent_import_recipient_in_symbolic_balance():
    from create_PPRS_excel import build_model_tables
    data = imported_state()
    data['_det_fate'].loc[3, :] = .25
    model = calc(data=data)
    tables = build_model_tables(model, method_keys=['sym_GE_asDC', 'sym_TE_asDC',
        'sym_WithEgestion_asDC'], method_timeout=0)
    assert set(tables.method_status.values()) == {'ok'}
    assert not any('is_sppr_balanced raised' in issue['detail'] for issue in tables.issues)
    # Existing With Egestion symbolic partial-routing limitation stays visible.
    assert any(issue['kind']=='sppr_balance' and issue['method']=='sym_WithEgestion_asDC'
               for issue in tables.issues)
