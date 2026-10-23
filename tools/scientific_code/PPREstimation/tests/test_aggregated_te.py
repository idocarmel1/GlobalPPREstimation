"""Hand-computed Lindeman flow aggregations and SPPR integration checks."""
from copy import deepcopy
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PPRCalculator import PPRCalculator


def flow_model(types, diets, consumption, respiration, detritus, catch):
    """Build controlled completed vectors without invoking model completion."""
    ids = list(types)
    calculator = PPRCalculator.__new__(PPRCalculator)
    calculator._groups_df = pd.DataFrame(index=ids)
    calculator._groups_df['trophic_info'] = pd.Series(types)
    calculator._groups_df['group_name'] = [f'Group {i}' for i in ids]
    calculator._groups_df['biomass'] = 1.
    calculator._DC = pd.DataFrame(0., index=ids, columns=ids)
    for predator, prey, fraction in diets:
        calculator._DC.loc[predator, prey] = fraction
    for name, values in {
        'q': consumption, 'respiration': respiration,
        'egestion': detritus, 'catch': catch,
    }.items():
        setattr(calculator, name, pd.Series(values, index=ids, dtype=float))
    for name in ('M0', 'growth', 'net_migration', 'immigration', 'emigration',
                 'det_export', 'external_mortality_export'):
        setattr(calculator, name, pd.Series(0., index=ids))
    consumers = calculator.get_Regular_seq()
    calculator.predation = calculator._DC.loc[consumers].mul(
        calculator.q.loc[consumers], axis=0).sum(axis=0)
    calculator.p = calculator.predation + calculator.catch
    calculator.GE = (calculator.p / calculator.q).fillna(1.)
    calculator.EE = pd.Series(1., index=ids)
    for name in ('q', 'p', 'respiration', 'egestion', 'catch', 'M0',
                 'predation', 'net_migration', 'immigration', 'emigration',
                 'external_mortality_export'):
        calculator._groups_df[name] = getattr(calculator, name)
    calculator._groups_df['biomass_accum'] = calculator.growth
    calculator._groups_df['detritus_import'] = 0.
    calculator._det_fate = pd.DataFrame(
        1., index=ids, columns=calculator.get_DET_seq())
    calculator.n_groups = len(ids)
    calculator.seq2name = calculator._groups_df.group_name.to_dict()
    calculator.name2seq = {name: seq for seq, name in calculator.seq2name.items()}
    return calculator


@pytest.fixture
def chain():
    # Consumer Q=100,10,1, with 90% going to respiration and detritus.
    # The top consumer exports .1 in catch instead of feeding a fifth level.
    return flow_model(
        {40: 'PP', 10: 'Regular', 70: 'Regular', 20: 'Regular'},
        [(10, 40, 1.), (70, 10, 1.), (20, 70, 1.)],
        [0., 100., 10., 1.], [0., 70., 7., .7],
        [0., 20., 2., .2], [0., 0., 0., .1],
    )


@pytest.fixture
def omnivory():
    # The omnivore is half level II, half level III; its predator is half
    # level III, half level IV. Whole-group bins cannot reproduce these flows.
    return flow_model(
        {40: 'PP', 10: 'Regular', 70: 'Regular', 20: 'Regular'},
        [(10, 40, 1.), (70, 40, .5), (70, 10, .5), (20, 70, 1.)],
        [0., 100., 40., 4.], [0., 60., 28., 2.8],
        [0., 20., 8., .8], [0., 0., 0., .4],
    )


def test_pure_chain_has_ten_percent_transfer_at_each_level(chain):
    actual = chain.get_aggregated_TE()
    expected = pd.DataFrame({
        'TE': [.1, .1, .1],
        'consumption': [100., 10., 1.],
        'predation': [10., 1., 0.],
        'export': [0., 0., .1],
        'respiration': [70., 7., .7],
        'flow_to_detritus': [20., 2., .2],
        'throughput': [100., 10., 1.],
    }, index=pd.Index([2, 3, 4], name='trophic_level'))
    pd.testing.assert_frame_equal(actual, expected, check_dtype=False)


def test_omnivores_contribute_fractional_flows_to_multiple_levels(omnivory):
    actual = omnivory.get_aggregated_TE()
    expected = pd.DataFrame({
        'TE': [22. / 120., .1, .1],
        'consumption': [120., 22., 2.],
        'predation': [22., 2., 0.],
        'export': [0., .2, .2],
        'respiration': [74., 15.4, 1.4],
        'flow_to_detritus': [24., 4.4, .4],
        'throughput': [120., 22., 2.],
    }, index=pd.Index([2, 3, 4], name='trophic_level'))
    pd.testing.assert_frame_equal(actual, expected, check_dtype=False)


def test_pp_detritus_and_import_are_basal_sources_only():
    calculator = flow_model(
        {40: 'PP', 5: 'DET', 9: 'Import', 10: 'Regular'},
        [(10, 40, .2), (10, 5, .3), (10, 9, .5)],
        [1e6, 1e6, 1e6, 100.], [1e6, 1e6, 1e6, 80.],
        [1e6, 1e6, 1e6, 10.], [1e6, 1e6, 1e6, 10.],
    )
    actual = calculator.get_aggregated_TE()
    assert actual.loc[2, 'consumption'] == pytest.approx(100.)
    assert actual.loc[2, 'throughput'] == pytest.approx(100.)
    assert actual.loc[2, 'TE'] == pytest.approx(.1)
    assert actual.loc[[3, 4], 'throughput'].eq(0.).all()
    assert actual.loc[[3, 4], 'TE'].isna().all()


def test_default_lindeman_aggregation_removes_cannibalism():
    calculator = flow_model(
        {40: 'PP', 10: 'Regular'},
        [(10, 40, .8), (10, 10, .2)],
        [0., 100.], [0., 60.], [0., 20.], [0., 0.],
    )
    actual = calculator.get_aggregated_TE()
    assert actual.loc[2, 'predation'] == pytest.approx(0.)
    assert actual.loc[2, 'throughput'] == pytest.approx(80.)
    assert actual.loc[2, 'TE'] == pytest.approx(0.)
    assert actual.loc[[3, 4], 'TE'].isna().all()


def test_active_isolated_consumer_cycle_cannot_disappear_from_valid_chain():
    calculator = flow_model(
        {40: 'PP', 10: 'Regular', 70: 'Regular', 20: 'Regular',
         100: 'Regular', 200: 'Regular'},
        [(10, 40, 1.), (70, 10, 1.), (20, 70, 1.),
         (100, 200, 1.), (200, 100, 1.)],
        [0., 100., 10., 1., 10., 10.],
        [0., 70., 7., .7, 5., 5.],
        [0., 20., 2., .2, 4., 4.],
        [0., 0., 0., .1, 1., 1.],
    )
    # The valid chain supplies all requested levels, so an absent-level check
    # alone misses the unsupported consumers and silently drops their flows.
    with pytest.raises(ValueError, match='(?i)basal'):
        calculator.get_aggregated_TE()
    with pytest.raises(ValueError, match='(?i)basal'):
        calculator.SPPR_1995(TE_option='aggregated')


def test_raw_diet_option_retains_cannibalism_without_renormalizing_levels():
    calculator = flow_model(
        {40: 'PP', 10: 'Regular'},
        [(10, 40, .8), (10, 10, .2)],
        [0., 100.], [0., 60.], [0., 20.], [0., 0.],
    )
    actual = calculator.get_aggregated_TE(break_cycles=False)
    # Membership is .8,.16,.032, with .008 remaining above requested level IV.
    np.testing.assert_allclose(actual['consumption'], [80., 16., 3.2])
    np.testing.assert_allclose(actual['predation'], [16., 3.2, .64])
    np.testing.assert_allclose(actual['throughput'], [80., 16., 3.2])
    np.testing.assert_allclose(actual['TE'], [.2, .2, .2])


def test_routing_and_external_mortality_shift_sinks_without_double_counting():
    calculator = flow_model(
        {40: 'PP', 10: 'Regular'}, [(10, 40, 1.)],
        [0., 100.], [0., 70.], [0., 10.], [0., 10.],
    )
    calculator.M0.loc[10] = 10.
    baseline = calculator.get_aggregated_TE()
    assert baseline.loc[2, 'TE'] == pytest.approx(.1)
    calculator.M0.loc[10] = 7.
    calculator.external_mortality_export.loc[10] = 3.
    calculator.det_export.loc[10] = 5.
    actual = calculator.get_aggregated_TE()
    assert actual.loc[2, 'export'] == pytest.approx(18.)
    assert actual.loc[2, 'flow_to_detritus'] == pytest.approx(12.)
    assert actual.loc[2, 'throughput'] == pytest.approx(100.)
    assert actual.loc[2, 'TE'] == pytest.approx(.18)


def test_net_import_is_signed_and_biomass_accumulation_is_not_export(chain):
    chain.net_migration.loc[20] = -.05
    actual = chain.get_aggregated_TE()
    assert actual.loc[4, 'export'] == pytest.approx(.05)
    assert actual.loc[4, 'throughput'] == pytest.approx(.95)
    assert actual.loc[4, 'TE'] == pytest.approx(.05 / .95)
    chain.growth.loc[20] = 100.
    chain._groups_df.loc[20, 'biomass_accum'] = 100.
    pd.testing.assert_frame_equal(chain.get_aggregated_TE(), actual)


def test_group_label_alignment_is_independent_of_vector_and_matrix_order(omnivory):
    shuffled = deepcopy(omnivory)
    shuffled._groups_df = shuffled._groups_df.reindex([20, 10, 40, 70])
    shuffled._DC = shuffled._DC.reindex(index=[70, 40, 20, 10],
                                       columns=[10, 20, 70, 40])
    for name, value in list(shuffled.__dict__.items()):
        if isinstance(value, pd.Series):
            setattr(shuffled, name, value.reindex([10, 70, 40, 20]))
    pd.testing.assert_frame_equal(shuffled.get_aggregated_TE(),
                                  omnivory.get_aggregated_TE())


def test_requested_levels_preserve_order_and_missing_levels_stay_missing(chain):
    actual = chain.get_aggregated_TE(levels=(4, 2, 5))
    assert actual.index.tolist() == [4, 2, 5]
    assert actual.loc[[4, 2], 'TE'].tolist() == pytest.approx([.1, .1])
    assert actual.loc[5, 'throughput'] == 0.
    assert np.isnan(actual.loc[5, 'TE'])


def test_aggregation_does_not_mutate_diet_or_completed_flow_vectors(omnivory):
    previous = deepcopy(omnivory.__dict__)
    omnivory.get_aggregated_TE()
    for name, value in previous.items():
        if isinstance(value, pd.Series):
            pd.testing.assert_series_equal(getattr(omnivory, name), value)
        elif isinstance(value, pd.DataFrame):
            pd.testing.assert_frame_equal(getattr(omnivory, name), value)


def test_aggregated_sppr_uses_geometric_mean_and_existing_trophic_levels(omnivory):
    geometric_mean = ((22. / 120.) * .1 * .1) ** (1. / 3.)
    actual = omnivory.SPPR_1995(TE_option='aggregated')
    expected = omnivory.SPPR_1995(global_TE=geometric_mean)
    pd.testing.assert_frame_equal(actual, expected)
    # TL=2.5 for the omnivore, preserved independently of the flow aggregation.
    assert actual.loc[70, 'sppr'] == pytest.approx(geometric_mean ** -1.5)


@pytest.mark.parametrize('global_te', [.1, .25, 'mean'])
@pytest.mark.parametrize('weights', ['consumption', 'equal', 'catch', 'biomass'])
def test_explicit_global_option_preserves_existing_sppr_calls(chain, global_te, weights):
    expected = chain.SPPR_1995(global_te, weights)
    actual = chain.SPPR_1995(global_te, weights, TE_option='global')
    pd.testing.assert_frame_equal(actual, expected)


def test_legacy_mean_te_keeps_arithmetic_consumer_weighting(omnivory):
    # Existing group TE=.2,.1,.1, weighted by Q=100,40,4.
    expected = omnivory.SPPR_1995(global_TE=24.4 / 144.)
    actual = omnivory.SPPR_1995(global_TE='mean')
    pd.testing.assert_frame_equal(actual, expected)


@pytest.mark.parametrize('top_catch', [0., np.nan])
def test_aggregated_sppr_rejects_zero_or_unavailable_required_efficiency(chain, top_catch):
    chain.catch.loc[20] = top_catch
    with pytest.raises(ValueError, match='(?i)(aggregat|trophic|efficien|level)'):
        chain.SPPR_1995(TE_option='aggregated')


def test_aggregated_sppr_rejects_absent_level_four():
    calculator = flow_model(
        {40: 'PP', 10: 'Regular'}, [(10, 40, 1.)],
        [0., 100.], [0., 80.], [0., 10.], [0., 10.],
    )
    with pytest.raises(ValueError, match='(?i)(aggregat|trophic|efficien|level)'):
        calculator.SPPR_1995(TE_option='aggregated')


def test_aggregated_sppr_rejects_efficiency_above_one_without_clipping(chain):
    # A deliberately inconsistent negative respiratory residual must not become
    # an apparently valid TE through clipping or absolute-value transformations.
    chain.respiration.loc[20] = -.21
    assert chain.get_aggregated_TE().loc[4, 'TE'] > 1.
    with pytest.raises(ValueError, match='(?i)(aggregat|trophic|efficien|level)'):
        chain.SPPR_1995(TE_option='aggregated')


def test_sppr_rejects_unknown_te_option(chain):
    with pytest.raises(ValueError, match='TE_option'):
        chain.SPPR_1995(TE_option='agregated')


def test_sppr_te_option_is_keyword_only(chain):
    with pytest.raises(TypeError):
        chain.SPPR_1995(.1, 'consumption', 'aggregated')
