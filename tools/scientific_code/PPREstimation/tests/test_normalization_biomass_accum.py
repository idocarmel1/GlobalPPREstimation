"""Diet normalization must preserve coefficients and source inputs without hiding imbalance."""
from copy import deepcopy
from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
import pytest

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator


def toy(*, total=0.9999, producer_ba=0.001, producer_p=20.0):
    model = ModelData.__new__(ModelData)
    model.groups_data = pd.DataFrame([
        dict(group_name="consumer", trophic_info="Regular", biomass=1., p=2., q=10.,
             ee=.75, M0=.5, catch=1., biomass_accum=.5, egestion=2., respiration=6.),
        dict(group_name="producer", trophic_info="PP", biomass=1., p=producer_p, q=producer_p,
             ee=.5, M0=10., catch=0., biomass_accum=producer_ba, egestion=0., respiration=0.),
        dict(group_name="detritus", trophic_info="DET", biomass=1., p=np.nan, q=np.nan,
             ee=1., M0=0., catch=0., biomass_accum=np.nan, egestion=0., respiration=0.),
    ], index=[1, 2, 3])
    for col in ["gs", "pb", "qb", "tl"]:
        model.groups_data[col] = np.nan
    for col in ["immigration", "emigration", "net_migration", "detritus_import"]:
        model.groups_data[col] = 0.
    model.DC = pd.DataFrame(0., index=[1, 2, 3], columns=[1, 2, 3])
    model.DC.loc[1, 2] = total
    model.det_fate = model.DC * 0
    model.det_fate[3] = 1.
    model.seq2name = dict(model.groups_data.group_name)
    model.name2seq = {v: k for k, v in model.seq2name.items()}
    return model


def build(model, normalize=True, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return PPRCalculator.from_modeldata(model, normalize_DC=normalize,
                                            zero_biomass_accum=False, **kwargs)


def test_normalized_production_balance_and_nonzero_source_ba_are_preserved():
    # Hand balance: raw feeding=9.999; 20 = 9.999 + M0 10 + BA .001.
    model = toy()
    source = deepcopy(model.__dict__)
    pc = build(model)
    assert pc.is_model_balanced()[0]
    assert pc.is_balanced
    assert pc.growth.loc[2] == pytest.approx(0., abs=1e-12)
    assert pc._groups_df.loc[2, "biomass_accum"] == pc.growth.loc[2]
    assert pc.growth.loc[1] == .5
    assert pc.EE.loc[1] == .75
    assert pc.EE.loc[2] == .5
    assert pc.M0.loc[1] == .5
    assert pc.M0.loc[2] == 10.
    assert pc.q.loc[3] == 12.5
    assert pc.growth.loc[3] == 12.5
    assert pc._groups_df.loc[1, 'flow_to_det'] == 2.5
    assert pc._groups_df.loc[2, 'flow_to_det'] == 10.
    pd.testing.assert_frame_equal(model.groups_data, source["groups_data"])
    pd.testing.assert_frame_equal(model.DC, source["DC"])
    pd.testing.assert_frame_equal(model.det_fate, source["det_fate"])


def test_genuine_raw_imbalance_is_not_repaired():
    pc = build(toy(producer_p=21.))
    assert not pc.is_model_balanced()[0]
    assert pc.growth.loc[2] == .001
    assert pc.balanced_model.n_balance_runs > 0


def test_small_existing_raw_residual_is_retained_not_erased():
    pc = build(toy(producer_ba=.0011))
    assert pc.growth.loc[2] == pytest.approx(.0001, abs=1e-12)
    assert pc.diet_normalization_balance_ledger.loc[2, 'runtime_production_residual'] == pytest.approx(.0001)


@pytest.mark.parametrize("normalize,total,ba", [(False, .9999, .001), (True, 1., 0.)])
def test_disabled_or_unchanged_normalization_does_not_adjust_ba(normalize, total, ba):
    pc = build(toy(total=total, producer_ba=ba), normalize=normalize)
    assert pc.growth.loc[2] == ba
    assert pc.balanced_model.n_balance_runs > 0


def test_incomplete_runtime_production_is_not_repaired():
    model = toy()
    pc = build(model)
    df = pc._groups_df.copy()
    df.loc[2, ["p", "M0"]] = np.nan
    df.loc[2, "biomass_accum"] = .001
    result = pc._reconcile_normalized_diet_biomass_accum(df, model.DC, True)
    assert result.loc[2, "biomass_accum"] == .001
    assert pc.diet_normalization_balance_ledger.loc[2, "reason"] == "incomplete_production_terms"


def test_unknown_donor_consumption_cannot_be_treated_as_zero():
    model = toy()
    pc = build(model)
    df = pc._groups_df.copy()
    df.loc[1, 'q'] = np.nan
    df.loc[2, 'biomass_accum'] = .001
    result = pc._reconcile_normalized_diet_biomass_accum(df, model.DC, True)
    assert result.loc[2, 'biomass_accum'] == .001
    assert pc.diet_normalization_balance_ledger.loc[2, 'reason'] == 'incomplete_predation_counterfactual'


def test_real_model_balance_improves_with_exact_sppr_invariance(monkeypatch):
    repo = ENGINE.parents[2]
    path = repo / "regions/LME_027/models/27_118_Northwest_Africa_(1987)/model.json"
    model = ModelData(str(path))
    before = deepcopy(model.__dict__)
    # Independently run the unchanged normalization/completion pipeline. This
    # baseline catches any unintended flow mutation inside reconciliation.
    with monkeypatch.context() as context:
        context.setattr(PPRCalculator, '_reconcile_normalized_diet_biomass_accum',
                        lambda self, df, *args: df.copy())
        old = build(model, underdetermined=True)
    pc = build(model, underdetermined=True)
    disabled = build(model, underdetermined=True, balance_BA_after_DC_normalization=False)
    pd.testing.assert_frame_equal(disabled._groups_df, old._groups_df, check_exact=True)
    pd.testing.assert_series_equal(disabled.growth, old.growth, check_exact=True)
    assert pc.is_balanced
    ledger = pc.diet_normalization_balance_ledger
    assert ledger.applied.any()
    assert not old.is_model_balanced()[0]
    pd.testing.assert_frame_equal(pc._groups_df.drop(columns='biomass_accum'),
                                  old._groups_df.drop(columns='biomass_accum'), check_exact=True)
    for attr in ["EE", "M0", "p", "q", "catch", "predation", "net_migration", "respiration",
                 "egestion", "det_export", "_DC", "_det_fate"]:
        assert getattr(pc, attr).equals(getattr(old, attr))
    pd.testing.assert_frame_equal(pc.get_Z(DET_as_PP=False), old.get_Z(DET_as_PP=False), check_exact=True)
    assert pc.growth.loc[pc.get_DET_seq()].equals(old.growth.loc[old.get_DET_seq()])
    for option in ["GE", "TE", "With Egestion"]:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            new_result = pc.diagnose_sppr(option, return_sppr=True, det_collapse_mode="never",
                                          det_open_mode="none", det_theta=1., det_external_sppr=0.)
            old_result = old.diagnose_sppr(option, return_sppr=True, det_collapse_mode="never",
                                           det_open_mode="none", det_theta=1., det_external_sppr=0.)
        for new, previous in zip(new_result[1:], old_result[1:]):
            pd.testing.assert_frame_equal(new, previous, check_exact=True)
    pd.testing.assert_frame_equal(model.groups_data, before["groups_data"])
    pd.testing.assert_frame_equal(model.DC, before["DC"])


@pytest.mark.parametrize('loader', ['from_modeldata', 'from_dict', '__init__'])
@pytest.mark.parametrize('enabled', [False, True])
def test_all_loaders_control_new_correction_without_mutating_input(loader, enabled):
    repo = ENGINE.parents[2]
    path = repo / 'regions/LME_027/models/27_118_Northwest_Africa_(1987)/model.json'
    model = ModelData(str(path))
    original_groups = model.groups_data.copy(deep=True)
    original_diet = model.DC.copy(deep=True)
    settings = dict(underdetermined=True, zero_biomass_accum=False, normalize_DC=True,
                    DC_tol=.001, balance_BA_after_DC_normalization=enabled)
    seed = dict(_groups_df=model.groups_data.copy(), _DC=model.DC.copy(),
                _det_fate=model.det_fate.copy(), seq2name=model.seq2name.copy(),
                name2seq=model.name2seq.copy(), n_groups=len(model.groups_data), _model=model)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        if loader == 'from_modeldata':
            pc = PPRCalculator.from_modeldata(model, **settings)
        elif loader == 'from_dict':
            pc = PPRCalculator.from_dict(seed, **settings)
        else:
            pc = PPRCalculator(str(path), **settings)
    assert pc.balance_BA_after_DC_normalization is enabled
    assert pc.is_balanced is enabled
    assert bool(pc.diet_normalization_balance_ledger.applied.any()) is enabled
    if not enabled:
        assert pc.growth.loc[24] == 0.
        assert pc.diet_normalization_balance_ledger.loc[24, 'reason'] == 'ba_balance_disabled'
    pd.testing.assert_frame_equal(model.groups_data, original_groups, check_exact=True)
    pd.testing.assert_frame_equal(model.DC, original_diet, check_exact=True)
    pd.testing.assert_frame_equal(seed['_groups_df'], original_groups, check_exact=True)
    pd.testing.assert_frame_equal(seed['_DC'], original_diet, check_exact=True)


def test_disabled_dict_reload_preserves_existing_ba_and_replaces_stale_ledger():
    original = build(toy())
    original_ba = original._groups_df.biomass_accum.copy()
    pc = PPRCalculator.from_dict(original.__dict__, normalize_DC=True,
                                zero_biomass_accum=False,
                                balance_BA_after_DC_normalization=False)
    pd.testing.assert_series_equal(pc.growth, original_ba, check_exact=True)
    assert not pc.diet_normalization_balance_ledger.applied.any()
    assert pc.balanced_model.n_balance_runs > 0
    assert original.diet_normalization_balance_ledger.applied.any()


@pytest.mark.parametrize('normalize,total,ba', [(False, .9999, .001), (True, 1., 0.)])
def test_binary_ba_flag_has_no_effect_without_changed_normalization(normalize, total, ba):
    off = build(toy(total=total, producer_ba=ba), normalize=normalize,
                balance_BA_after_DC_normalization=False)
    on = build(toy(total=total, producer_ba=ba), normalize=normalize,
               balance_BA_after_DC_normalization=True)
    pd.testing.assert_frame_equal(off._groups_df, on._groups_df, check_exact=True)
    pd.testing.assert_series_equal(off.growth, on.growth, check_exact=True)


def test_corrected_balanced_copy_retains_runtime_table_vectors_and_ledger():
    pc = build(toy())
    assert pc.is_balanced
    assert pc.balanced_model.is_model_balanced()[0]
    assert pc.balanced_model.n_balance_runs == 0
    pd.testing.assert_series_equal(pc.balanced_model.growth, pc.growth, check_exact=True)
    pd.testing.assert_series_equal(pc.balanced_model.growth,
                                   pc.balanced_model._groups_df.biomass_accum,
                                   check_exact=True, check_names=False)
    pd.testing.assert_frame_equal(pc.balanced_model.diet_normalization_balance_ledger,
                                  pc.diet_normalization_balance_ledger, check_exact=True)


def test_ledger_accounts_for_computational_adjustment_and_skip_reason():
    pc = build(toy())
    entries = pc.diet_normalization_balance_ledger
    pp = entries.loc[2]
    assert pp["applied"]
    assert pp["raw_predation"] == pytest.approx(9.999)
    assert pp["normalized_predation"] == 10.
    assert pp["biomass_accum_adjustment"] == pytest.approx(-.001)
    assert pp['source_biomass_accum'] == .001
    assert pp['original_runtime_biomass_accum'] == .001
    assert np.isnan(entries.loc[3, 'source_biomass_accum'])
    assert entries.loc[3, "reason"] == "excluded_trophic_type"
    bad = build(toy(producer_p=21.))
    bad_pp = bad.diet_normalization_balance_ledger.loc[2]
    assert bad_pp["reason"] == "raw_production_unbalanced"
