from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from ppr_pipeline import calculations
from ppr_pipeline.calculations import (
    add_species_ppr,
    aggregate_groups,
    calculate_sppr,
)


@pytest.mark.parametrize("tl, expected", [(1.0, 1.0), (2.0, 10.0), (3.0, 100.0)])
def test_calculate_sppr_uses_te_point_one(tl: float, expected: float) -> None:
    assert calculate_sppr(tl) == pytest.approx(expected)


def test_calculate_sppr_rejects_invalid_transfer_efficiency() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        calculate_sppr(3.0, te=1.0)


def test_add_species_ppr_preserves_unmatched_rows() -> None:
    frame = pd.DataFrame(
        {"taxon": ["matched", "unmatched"], "catch_tonnes": [5.0, 7.0], "tl": [2.0, np.nan]}
    )
    result = add_species_ppr(frame)
    assert result.loc[0, "sppr"] == pytest.approx(10.0)
    assert result.loc[0, "ppr"] == pytest.approx(50.0)
    assert math.isnan(result.loc[1, "sppr"])
    assert math.isnan(result.loc[1, "ppr"])
    assert result["catch_tonnes"].sum() == pytest.approx(12.0)


def test_add_species_ppr_rejects_negative_catch() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        add_species_ppr(pd.DataFrame({"catch_tonnes": [-1.0], "tl": [2.0]}))


def test_group_aggregation_returns_catch_weighted_jensen_values() -> None:
    species = pd.DataFrame(
        {
            "commercial_group": ["Cod-likes", "Cod-likes"],
            "catch_tonnes": [5.0, 5.0],
            "tl": [2.0, 3.0],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    result = calculations.aggregate_groups(species, "commercial_group", te=0.1)

    assert list(result.columns) == [
        "commercial_group",
        "catch_tonnes_matched",
        "tl_weighted",
        "sppr",
        "ppr",
    ]
    row = result.iloc[0]
    assert row["catch_tonnes_matched"] == pytest.approx(10.0)
    # catch-weighted mean TL of 2.0 and 3.0 at equal catch
    assert row["tl_weighted"] == pytest.approx(2.5)
    # 10 ** (2.5 - 1)
    assert row["sppr"] == pytest.approx(31.6227766017)
    assert row["ppr"] == pytest.approx(316.227766017)


def test_group_aggregation_matches_taxon_sum_for_uniform_trophic_level() -> None:
    """With one TL there is no Jensen gap, so the group value equals the taxon sum."""
    species = pd.DataFrame(
        {
            "commercial_group": ["Anchovies", "Anchovies"],
            "catch_tonnes": [4.0, 6.0],
            "tl": [3.0, 3.0],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    result = calculations.aggregate_groups(species, "commercial_group", te=0.1)

    assert result.iloc[0]["ppr"] == pytest.approx(float(species["ppr"].sum()))


def test_group_aggregation_underestimates_taxon_sum_when_trophic_levels_differ() -> None:
    """The retained group figure is deliberately the Jensen-affected one."""
    species = pd.DataFrame(
        {
            "commercial_group": ["Mixed", "Mixed"],
            "catch_tonnes": [5.0, 5.0],
            "tl": [2.0, 4.0],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    result = calculations.aggregate_groups(species, "commercial_group", te=0.1)

    taxon_sum = float(species["ppr"].sum())
    assert result.iloc[0]["ppr"] < taxon_sum


def test_group_aggregation_returns_nan_when_no_taxon_has_a_trophic_level() -> None:
    species = pd.DataFrame(
        {
            "commercial_group": ["Unknown"],
            "catch_tonnes": [10.0],
            "tl": [float("nan")],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    result = calculations.aggregate_groups(species, "commercial_group", te=0.1)

    row = result.iloc[0]
    assert row["catch_tonnes_matched"] == pytest.approx(0.0)
    assert pd.isna(row["tl_weighted"])
    assert pd.isna(row["sppr"])
    assert pd.isna(row["ppr"])


def test_group_aggregation_returns_schema_for_zero_catch_unit() -> None:
    species = pd.DataFrame(
        columns=["commercial_group", "catch_tonnes", "tl", "ppr"]
    )

    result = aggregate_groups(species, "commercial_group")

    assert result.empty
    assert list(result.columns) == [
        "commercial_group",
        "catch_tonnes_matched",
        "tl_weighted",
        "sppr",
        "ppr",
    ]


def test_group_aggregation_uses_matched_catch_only_for_a_partly_matched_group() -> None:
    """A group where some taxa have a TL and some do not.

    Every group figure must be built from the TL-matched catch alone. Substituting
    the group's total catch would inflate both ``catch_tonnes_matched`` and ``ppr``
    by the unmatched 90 tonnes, which no happy-path test would notice.
    """
    species = pd.DataFrame(
        {
            "commercial_group": ["Mixed", "Mixed", "Mixed"],
            "catch_tonnes": [4.0, 6.0, 90.0],
            "tl": [2.0, 3.0, float("nan")],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    result = calculations.aggregate_groups(species, "commercial_group", te=0.1)

    row = result.iloc[0]
    # 4 + 6 matched, not the 100 tonnes the group actually landed.
    assert row["catch_tonnes_matched"] == pytest.approx(10.0)
    # (4 * 2.0 + 6 * 3.0) / 10, weighted by matched catch only.
    assert row["tl_weighted"] == pytest.approx(2.6)
    assert row["sppr"] == pytest.approx(10.0**1.6)
    assert row["ppr"] == pytest.approx(10.0 * 10.0**1.6)
    # Still one-sided against the taxon sum (which itself skips the unmatched taxon).
    assert row["ppr"] < float(species["ppr"].sum())
