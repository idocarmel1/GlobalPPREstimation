from __future__ import annotations

import pandas as pd
import pytest

from ppr_pipeline import calculations, validation
from ppr_pipeline.calculations import add_species_ppr, aggregate_groups
from ppr_pipeline.validation import validate_region


def test_validate_region_reconciles_catch_ppr_coverage_and_jensen() -> None:
    species = add_species_ppr(
        pd.DataFrame(
            {
                "taxon": ["A", "B", "C"],
                "commercial_group": ["C1", "C1", "C2"],
                "functional_group": ["F1", "F2", "F2"],
                "catch_tonnes": [5.0, 5.0, 2.0],
                "tl": [2.0, 3.0, float("nan")],
            }
        )
    )
    commercial = aggregate_groups(species, "commercial_group")
    functional = aggregate_groups(species, "functional_group")
    result = validate_region(
        unit_id="TEST",
        species=species,
        commercial=commercial,
        functional=functional,
        raw_filtered_tonnes=12.0,
    )
    metrics = result.set_index("check")["value"]
    assert metrics["catch_reconciled"] is True or metrics["catch_reconciled"] == 1
    assert metrics["catch_coverage_fraction"] == pytest.approx(10.0 / 12.0)
    assert metrics["unmatched_taxa_count"] == 1


def test_validate_region_detects_group_ppr_mismatch() -> None:
    species = add_species_ppr(
        pd.DataFrame(
            {
                "taxon": ["A"],
                "commercial_group": ["C1"],
                "functional_group": ["F1"],
                "catch_tonnes": [5.0],
                "tl": [2.0],
            }
        )
    )
    commercial = aggregate_groups(species, "commercial_group")
    functional = aggregate_groups(species, "functional_group")
    commercial.loc[0, "ppr"] += 1.0
    result = validate_region("TEST", species, commercial, functional, 5.0)
    metrics = result.set_index("check")["value"]
    assert metrics["commercial_ppr_difference"] == pytest.approx(1.0)


def test_validate_region_flags_complete_trophic_level_coverage() -> None:
    species = pd.DataFrame(
        {
            "commercial_group": ["Cod-likes", "Anchovies"],
            "functional_group": ["Large demersals", "Small pelagics"],
            "catch_tonnes": [10.0, 5.0],
            "tl": [4.0, 3.0],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    commercial = calculations.aggregate_groups(species, "commercial_group", te=0.1)
    functional = calculations.aggregate_groups(species, "functional_group", te=0.1)

    metrics = validation.validate_region(
        "LME_003", species, commercial, functional, raw_filtered_tonnes=15.0
    ).set_index("check")["value"].to_dict()

    assert metrics["tl_coverage_complete"] is True
    assert "commercial_jensen_violations" not in metrics
    assert "functional_jensen_violations" not in metrics


def test_validate_region_reports_incomplete_trophic_level_coverage() -> None:
    species = pd.DataFrame(
        {
            "commercial_group": ["Cod-likes", "Unknown"],
            "functional_group": ["Large demersals", "Unknown"],
            "catch_tonnes": [10.0, 5.0],
            "tl": [4.0, float("nan")],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    commercial = calculations.aggregate_groups(species, "commercial_group", te=0.1)
    functional = calculations.aggregate_groups(species, "functional_group", te=0.1)

    metrics = validation.validate_region(
        "LME_003", species, commercial, functional, raw_filtered_tonnes=15.0
    ).set_index("check")["value"].to_dict()

    assert metrics["tl_coverage_complete"] is False
    assert metrics["unmatched_taxa_count"] == 1



def test_validate_region_holds_the_convexity_bound_for_the_real_aggregation() -> None:
    """`10 ** (TL - 1)` is convex, so the group PPR can never exceed the taxon sum."""
    species = add_species_ppr(
        pd.DataFrame(
            {
                "taxon": ["A", "B", "C"],
                # C1 spans two trophic levels (a real Jensen gap); C2 spans one.
                "commercial_group": ["C1", "C1", "C2"],
                "functional_group": ["F1", "F1", "F1"],
                "catch_tonnes": [5.0, 5.0, 7.0],
                "tl": [2.0, 4.0, 3.0],
            }
        )
    )
    commercial = aggregate_groups(species, "commercial_group")
    functional = aggregate_groups(species, "functional_group")

    metrics = validate_region(
        "TEST", species, commercial, functional, 17.0
    ).set_index("check")["value"]

    assert metrics["group_ppr_within_convexity_bound"] is True
    # The gap is one-sided: the group aggregation underestimates, never overshoots.
    assert metrics["commercial_ppr_difference"] < 0
    assert metrics["functional_ppr_difference"] < 0


def test_validate_region_flags_group_ppr_above_the_taxon_sum() -> None:
    """A weighting error that inflates group PPR past the taxon sum must not pass."""
    species = add_species_ppr(
        pd.DataFrame(
            {
                "taxon": ["A", "B"],
                "commercial_group": ["C1", "C1"],
                "functional_group": ["F1", "F1"],
                "catch_tonnes": [100.0, 1.0],
                "tl": [2.0, 4.0],
            }
        )
    )
    commercial = aggregate_groups(species, "commercial_group")
    functional = aggregate_groups(species, "functional_group")

    # Reproduce an unweighted-mean-TL aggregation bug. The plain mean of 2.0 and 4.0
    # is 3.0, far above the catch-weighted mean of ~2.02, so the group PPR lands
    # above the taxon sum - impossible for a convex 10 ** (TL - 1).
    unweighted_tl = 3.0
    matched_catch = float(species["catch_tonnes"].sum())
    commercial.loc[0, "tl_weighted"] = unweighted_tl
    commercial.loc[0, "sppr"] = float(calculations.calculate_sppr(unweighted_tl))
    commercial.loc[0, "ppr"] = matched_catch * commercial.loc[0, "sppr"]

    metrics = validate_region(
        "TEST", species, commercial, functional, 101.0
    ).set_index("check")["value"]

    assert metrics["commercial_ppr_difference"] > 0
    assert metrics["group_ppr_within_convexity_bound"] is False
