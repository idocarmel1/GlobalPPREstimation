"""Regression coverage for consumer-only biomass fallback in global mean TE."""
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PPRCalculator import PPRCalculator


@pytest.fixture
def toy():
    return PPRCalculator(str(ROOT / "real_models/ToyModels/900_900_Multi_DET_Toy_(2026).json"))


@pytest.mark.parametrize("as_matrix", [False, True])
def test_biomass_fallback_excludes_all_basal_groups(toy, as_matrix):
    toy.catch[:] = 0
    # Herbivore TE=.24 and detritivore TE=.15, with biomass weights 1:3.
    toy._groups_df.loc[2, "biomass"] = 1
    toy._groups_df.loc[3, "biomass"] = 3
    basal = toy.get_PP_seq() + toy.get_DET_seq() + toy.get_Import_seq()
    toy._groups_df.loc[basal, "biomass"] = 1e6
    result = toy.get_TE("global", as_matrix=as_matrix, weights="catch")
    assert np.allclose(result.loc[toy.get_Regular_seq()], .1725)
    assert np.allclose(result.loc[toy.get_DET_seq()], 1)


def test_existing_catch_weights_take_precedence_over_biomass(toy):
    toy._groups_df["biomass"] = 0
    result = toy.get_TE("global", as_matrix=False, weights="catch")
    assert result.loc[2] == pytest.approx(.23)  # (12*.24 + 1.5*.15)/13.5


def test_negative_catch_cannot_cancel_positive_catch_and_trigger_biomass_fallback(toy):
    toy.catch.loc[2] = 1
    toy.catch.loc[3] = -1
    with pytest.raises(ValueError, match='nonnegative consumer catch'):
        toy.get_TE('global', as_matrix=False, weights='catch')


@pytest.mark.parametrize("biomass", [0, np.nan])
def test_biomass_fallback_requires_consumer_biomass(toy, biomass):
    toy.catch[:] = 0
    toy._groups_df.loc[toy.get_Regular_seq(), "biomass"] = biomass
    with pytest.raises(ValueError, match="positive consumer biomass"):
        toy.get_TE("global", as_matrix=False, weights="catch")


def test_missing_consumer_biomass_has_zero_weight(toy):
    toy.catch[:] = 0
    toy._groups_df.loc[2, "biomass"] = np.nan
    result = toy.get_TE("global", as_matrix=False, weights="catch")
    assert result.loc[3] == pytest.approx(.15)


def test_explicit_global_te_does_not_require_biomass_or_catch(toy):
    toy.catch[:] = 0
    toy._groups_df["biomass"] = 0
    result = toy.get_TE("global", global_TE=.1, as_matrix=False)
    assert np.allclose(result.loc[toy.get_Regular_seq()], .1)


def test_default_is_consumer_consumption_even_when_catch_exists(toy):
    # Q=50 and 10: (50*.24 + 10*.15)/60 = .225.
    result = toy.get_TE('global', as_matrix=False)
    assert result.loc[2] == pytest.approx(.225)


@pytest.mark.parametrize('weights,expected', [('equal',.195),('consumption',.225),('catch',.23),('biomass',.195)])
def test_weight_choices_use_only_consumers(toy, weights, expected):
    basal = toy.get_PP_seq() + toy.get_DET_seq() + toy.get_Import_seq()
    toy._groups_df.loc[basal,'biomass'] = 1e6
    toy.catch.loc[basal] = 1e6
    toy.q.loc[basal] = 1e6
    assert toy.get_TE('global', weights=weights, as_matrix=False).loc[2] == pytest.approx(expected)


def test_zero_te_consumer_remains_in_consumption_mean(toy):
    toy.M0.loc[3] = toy.p.loc[3]
    assert toy.get_TE('global', as_matrix=False).loc[2] == pytest.approx(.2)


def test_invalid_mean_weights_raise(toy):
    with pytest.raises(ValueError, match='weights'):
        toy.get_TE('global', weights='typo')


def test_zero_consumer_consumption_raises(toy):
    toy.q.loc[toy.get_Regular_seq()] = 0
    with pytest.raises(ValueError, match='positive consumer consumption'):
        toy.get_TE('global')


@pytest.mark.parametrize('option', ['GE','TE','With Egestion'])
def test_group_specific_te_ignores_mean_weights(toy, option):
    assert toy.get_TE(option).equals(toy.get_TE(option, weights='equal'))


@pytest.mark.parametrize('method', ['SPPR_1995','SPPR_1995_TL_fix','SPPR_EwE_Ulanowicz'])
def test_mean_method_forwards_weights_and_fixed_te_is_unchanged(toy, method):
    call = getattr(toy, method)
    kwargs = {'TE_option':'global','use_EE':False} if method=='SPPR_EwE_Ulanowicz' else {}
    frame = lambda value: value[0] if isinstance(value,tuple) else value
    np.testing.assert_allclose(frame(call(global_TE='mean',**kwargs)), frame(call(global_TE=.225,**kwargs)))
    np.testing.assert_allclose(frame(call(global_TE='mean',weights='equal',**kwargs)), frame(call(global_TE=.195,**kwargs)))
    np.testing.assert_allclose(frame(call(global_TE=.1,weights='equal',**kwargs)), frame(call(global_TE=.1,**kwargs)))
