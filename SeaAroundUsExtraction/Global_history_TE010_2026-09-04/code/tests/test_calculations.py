from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

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


def test_group_aggregation_reports_correct_and_jensen_results() -> None:
    species = add_species_ppr(
        pd.DataFrame(
            {
                "commercial_group": ["mixed", "mixed", "mixed"],
                "catch_tonnes": [5.0, 5.0, 2.0],
                "tl": [2.0, 3.0, np.nan],
            }
        )
    )
    row = aggregate_groups(species, "commercial_group").iloc[0]

    assert row["catch_tonnes_total"] == pytest.approx(12.0)
    assert row["catch_tonnes_matched"] == pytest.approx(10.0)
    assert row["catch_tonnes_missing_tl"] == pytest.approx(2.0)
    assert row["tl_weighted_jensen"] == pytest.approx(2.5)
    assert row["sppr_correct"] == pytest.approx(55.0)
    assert row["ppr_correct"] == pytest.approx(550.0)
    assert row["sppr_jensen"] == pytest.approx(31.6227766017)
    assert row["ppr_jensen"] == pytest.approx(316.227766017)
    assert row["jensen_difference"] == pytest.approx(233.772233983)
    assert row["jensen_ratio_correct_to_error"] > 1.0


def test_jensen_difference_is_zero_for_uniform_trophic_level() -> None:
    species = add_species_ppr(
        pd.DataFrame(
            {
                "functional_group": ["uniform", "uniform"],
                "catch_tonnes": [2.0, 8.0],
                "tl": [3.0, 3.0],
            }
        )
    )
    row = aggregate_groups(species, "functional_group").iloc[0]
    assert row["ppr_correct"] == pytest.approx(row["ppr_jensen"])
    assert row["jensen_difference"] == pytest.approx(0.0, abs=1e-10)


def test_group_aggregation_returns_schema_for_zero_catch_unit() -> None:
    species = pd.DataFrame(
        columns=["commercial_group", "catch_tonnes", "tl", "ppr"]
    )

    result = aggregate_groups(species, "commercial_group")

    assert result.empty
    assert [
        "commercial_group",
        "catch_tonnes_total",
        "ppr_correct",
        "ppr_jensen",
        "jensen_difference",
    ] == [
        column
        for column in result.columns
        if column
        in {
            "commercial_group",
            "catch_tonnes_total",
            "ppr_correct",
            "ppr_jensen",
            "jensen_difference",
        }
    ]
