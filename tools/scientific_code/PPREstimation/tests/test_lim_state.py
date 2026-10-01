"""LIM results must propagate into the food-web flows and exported group parameters."""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PPRCalculator import PPRCalculator


def seed_state(*, missing_consumption=True, egestion=4.0):
    # The consumption equation is visited before production completion. With both
    # p and q absent it cannot fill q; production then determines p=.5+1.5=2.
    # Actual LIM must subsequently solve q=2+14+4=20 (no arbitrary optimum).
    groups = pd.DataFrame({
        "group_name": ["Producer", "Consumer", "Detritus", "diet_import"],
        "trophic_info": ["PP", "Regular", "DET", "Import"],
        "biomass": [1.0, 2.0, 1.0, 1.0],
        "p": [10.0, np.nan if missing_consumption else 2.0, np.nan, 1.0],
        "q": [10.0, np.nan if missing_consumption else 20.0, np.nan, 1.0],
        "M0": [2.0, .5, 0.0, 0.0],
        "ee": [.8, .75, 1.0, 1.0],
        "gs": [0.0, .2, 0.0, 0.0],
        "respiration": [0.0, 14.0, 0.0, 0.0],
        "egestion": [0.0, egestion, 0.0, 0.0],
        "biomass_accum": [8.0, 1.5, np.nan, 0.0],
        "catch": [0.0, 0.0, 0.0, 0.0],
        "immigration": [0.0] * 4,
        "emigration": [0.0] * 4,
        "net_migration": [0.0] * 4,
        "detritus_import": [0.0] * 4,
        "tl": [1.0, np.nan, 1.0, 1.0],
    }, index=[1, 2, 3, 4])
    diet = pd.DataFrame(0.0, index=groups.index, columns=groups.index)
    diet.loc[2, [1, 3]] = [.75, .25]
    # Half the consumer's dead matter is exported: detritus receives 2 + .5*4.5.
    fate = pd.DataFrame({3: [1.0, .5, 1.0, 0.0]}, index=groups.index)
    return {"_groups_df": groups, "_DC": diet, "_det_fate": fate,
            "seq2name": groups.group_name.to_dict(),
            "name2seq": {name: seq for seq, name in groups.group_name.items()}}


def test_solved_consumption_refreshes_predation_detritus_and_rates():
    model = PPRCalculator.from_dict(seed_state(), underdetermined=True)
    groups = model.get_groups_df()
    assert model.q.loc[2] == pytest.approx(20.0)
    assert model.predation.loc[1] == pytest.approx(15.0)
    assert model.predation.loc[3] == pytest.approx(5.0)
    assert model.get_Z(DET_as_PP=True).loc[2, 1] == pytest.approx(15.0)
    assert groups.loc[1, "predation"] == pytest.approx(15.0)
    assert groups.loc[3, "predation"] == pytest.approx(5.0)
    assert model.q.loc[3] == pytest.approx(4.25)
    assert model.p.loc[3] == pytest.approx(4.25)
    assert model.growth.loc[3] == pytest.approx(-.75)
    assert model.det_export.loc[2] == pytest.approx(2.25)
    assert groups.loc[2, "flow_to_det"] == pytest.approx(4.5)
    assert groups.loc[2, "pb"] == pytest.approx(1.0)
    assert groups.loc[2, "qb"] == pytest.approx(10.0)
    assert groups.loc[3, "pb"] == pytest.approx(4.25)
    assert groups.loc[3, "qb"] == pytest.approx(4.25)
    assert model.EE.loc[2] == pytest.approx(.75)
    assert model.GS.loc[2] == pytest.approx(.2)
    assert model.GE.loc[2] == pytest.approx(.1)
    assert model.GE.loc[3] == pytest.approx(1.0)
    # The refresh must expose, not absorb, the new producer budget residual.
    assert model.p.loc[1] == 10.0
    assert model.M0.loc[1] == 2.0
    assert model.growth.loc[1] == 8.0
    balanced, production, _ = model.is_model_balanced()
    assert not balanced
    assert production.loc[1] == pytest.approx(25.0)
    assert production.loc[3] == pytest.approx(4.25)


def test_no_consumption_change_preserves_completed_state():
    seed = seed_state(missing_consumption=False)
    deterministic = PPRCalculator.from_dict(seed, underdetermined=False)
    completed = PPRCalculator.from_dict(seed, underdetermined=True)
    pd.testing.assert_frame_equal(completed.get_groups_df(), deterministic.get_groups_df())
    pd.testing.assert_series_equal(completed.predation, deterministic.predation)
    assert deterministic.predation.loc[1] == pytest.approx(15.0)
    assert deterministic.growth.loc[3] == pytest.approx(-.75)


def test_failed_optimizer_keeps_missing_consumption_and_runtime_fallback(capsys):
    # q=2+14=16 would violate GS>=.10 when known egestion is zero.
    # Exercise real SLSQP's infeasible-constraint failure, not a mock optimizer.
    model = PPRCalculator.from_dict(seed_state(egestion=0.0), underdetermined=True)
    groups = model.get_groups_df()
    assert "LIM failed for group '2'" in capsys.readouterr().out
    assert np.isnan(groups.loc[2, "q"])
    assert model.q.loc[2] == 0.0
    assert groups.loc[2, "respiration"] == 14.0
    assert groups.loc[2, "egestion"] == 0.0
    assert model.predation.loc[1] == 0.0
    assert not model.is_model_balanced()[0]
