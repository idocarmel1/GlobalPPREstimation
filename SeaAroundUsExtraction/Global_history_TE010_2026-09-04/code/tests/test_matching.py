from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ppr_pipeline.matching import assign_trophic_levels, normalize_taxon_name


def test_normalize_taxon_name_collapses_spacing_and_case() -> None:
    assert normalize_taxon_name("  Thunnus   Albacares ") == "thunnus albacares"


def test_matching_uses_documented_priority_and_retains_unmatched() -> None:
    catch = pd.DataFrame(
        {
            "taxon": ["A alpha", "B beta", "C delta", "D unknown", "E unknown", "F unknown"],
            "commercial_group": ["C shared", "C b", "C c", "C shared", "C e", "C f"],
            "functional_group": ["F a", "F shared", "F c", "F d", "F shared", "F f"],
            "catch_tonnes": [10.0, 9.0, 8.0, 7.0, 6.0, 5.0],
        }
    )
    supplement = pd.DataFrame(
        {
            "scientific_name": ["A alpha", "C alpha", "C beta"],
            "tl": [2.5, 2.0, 4.0],
        }
    )
    sau = pd.DataFrame(
        {
            "scientific_name": ["A alpha", "B beta"],
            "tl": [4.4, 3.2],
        }
    )

    result = assign_trophic_levels(catch, supplement, sau, min_genus_species=2)
    keyed = result.set_index("taxon")

    assert keyed.loc["A alpha", "tl"] == pytest.approx(2.5)
    assert keyed.loc["A alpha", "match_method"] == "exact_2020_supplement"
    assert keyed.loc["B beta", "tl"] == pytest.approx(3.2)
    assert keyed.loc["B beta", "match_method"] == "exact_sea_around_us"
    assert keyed.loc["C delta", "tl"] == pytest.approx(3.0)
    assert keyed.loc["C delta", "match_method"] == "genus_mean_2020"
    assert keyed.loc["D unknown", "tl"] == pytest.approx(2.5)
    assert keyed.loc["D unknown", "match_method"] == "commercial_group_mean"
    assert keyed.loc["E unknown", "tl"] == pytest.approx(3.2)
    assert keyed.loc["E unknown", "match_method"] == "functional_group_mean"
    assert np.isnan(keyed.loc["F unknown", "tl"])
    assert keyed.loc["F unknown", "match_method"] == "unmatched"
    assert keyed.loc["F unknown", "match_confidence"] == "none"


def test_group_fallback_means_are_not_catch_weighted() -> None:
    catch = pd.DataFrame(
        {
            "taxon": ["A alpha", "B beta", "C unknown"],
            "commercial_group": ["shared", "shared", "shared"],
            "functional_group": ["one", "two", "three"],
            "catch_tonnes": [1000.0, 1.0, 5.0],
        }
    )
    supplement = pd.DataFrame(
        {"scientific_name": ["A alpha", "B beta"], "tl": [2.0, 4.0]}
    )
    result = assign_trophic_levels(catch, supplement, pd.DataFrame(), min_genus_species=2)
    assert result.set_index("taxon").loc["C unknown", "tl"] == pytest.approx(3.0)


def test_sea_around_us_exact_match_is_unit_specific() -> None:
    catch = pd.DataFrame(
        {
            "unit_id": ["LME_001", "LME_002"],
            "taxon": ["Shared taxon", "Shared taxon"],
            "commercial_group": ["C", "C"],
            "functional_group": ["F", "F"],
            "catch_tonnes": [1.0, 1.0],
        }
    )
    sau = pd.DataFrame(
        {
            "unit_id": ["LME_001", "LME_002"],
            "scientific_name": ["Shared taxon", "Shared taxon"],
            "tl": [2.0, 4.0],
        }
    )
    result = assign_trophic_levels(catch, pd.DataFrame(), sau)
    assert result.set_index("unit_id")["tl"].to_dict() == {
        "LME_001": pytest.approx(2.0),
        "LME_002": pytest.approx(4.0),
    }


def test_group_fallback_builds_reference_mean_within_each_classification() -> None:
    catch = pd.DataFrame(
        {
            "taxon": ["Known species", "Known species", "Unknown species"],
            "commercial_group": ["Group A", "Group B", "Group B"],
            "functional_group": ["Function", "Function", "Function"],
            "catch_tonnes": [1.0, 1.0, 1.0],
        }
    )
    supplement = pd.DataFrame(
        {"scientific_name": ["Known species"], "tl": [3.25]}
    )

    matched = assign_trophic_levels(
        catch,
        supplement,
        pd.DataFrame(),
        allow_functional_group_fallback=False,
    )

    unknown = matched.loc[matched["taxon"] == "Unknown species"].iloc[0]
    assert unknown["match_method"] == "commercial_group_mean"
    assert unknown["tl"] == pytest.approx(3.25)
