from __future__ import annotations

import pandas as pd
import pytest

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
    assert metrics["commercial_ppr_reconciled"] is True or metrics["commercial_ppr_reconciled"] == 1
    assert metrics["functional_ppr_reconciled"] is True or metrics["functional_ppr_reconciled"] == 1
    assert metrics["catch_coverage_fraction"] == pytest.approx(10.0 / 12.0)
    assert metrics["unmatched_taxa_count"] == 1
    assert metrics["commercial_jensen_violations"] == 0
    assert metrics["functional_jensen_violations"] == 0


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
    commercial.loc[0, "ppr_correct"] += 1.0
    result = validate_region("TEST", species, commercial, functional, 5.0)
    metrics = result.set_index("check")["value"]
    assert metrics["commercial_ppr_reconciled"] is False or metrics["commercial_ppr_reconciled"] == 0

