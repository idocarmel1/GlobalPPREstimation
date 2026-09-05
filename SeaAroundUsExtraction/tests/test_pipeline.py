from __future__ import annotations

import pandas as pd
import pytest

from ppr_pipeline.calculations import add_species_ppr, aggregate_groups
from ppr_pipeline.pipeline import (
    analysis_directories,
    build_unit_manifest,
    copy_spatial_deliverables,
    load_analysis_units,
    load_trophic_reference,
    summarize_pilot,
    summarize_units,
)


def test_copy_spatial_deliverables_puts_both_polygon_layers_in_output(tmp_path) -> None:
    spatial = tmp_path / "spatial"
    spatial.mkdir()
    for name, content in {
        "LMEs.geojson": '{"type":"FeatureCollection","features":[]}',
        "HighSeas.geojson": '{"type":"FeatureCollection","features":[]}',
        "spatial_units.csv": "unit_id,name\n",
    }.items():
        (spatial / name).write_text(content, encoding="utf-8")

    copied = copy_spatial_deliverables(tmp_path, tmp_path / "global_output")

    assert {path.name for path in copied} == {
        "LMEs.geojson",
        "HighSeas.geojson",
        "spatial_units.csv",
    }
    assert all(path.parent == tmp_path / "global_output" / "spatial" for path in copied)


def test_load_trophic_reference_uses_self_contained_frozen_csv(tmp_path) -> None:
    frozen = tmp_path / "trophic_levels_2020.csv"
    pd.DataFrame(
        {"scientific_name": ["Species alpha"], "habitat": ["Pelagic"], "tl": [3.2]}
    ).to_csv(frozen, index=False)
    reference = load_trophic_reference(frozen)
    assert reference.loc[0, "scientific_name"] == "Species alpha"
    assert reference.loc[0, "tl"] == pytest.approx(3.2)


def test_load_analysis_units_uses_global_spatial_index(tmp_path) -> None:
    (tmp_path / "spatial").mkdir()
    (tmp_path / "spatial" / "spatial_units.csv").write_text(
        "unit_id,name,type,sau_region,sau_region_id\n"
        "LME_001,East Bering Sea,LME,lme,1\n"
        "HS_071,Pacific Western Central,High Seas,highseas,71\n",
        encoding="utf-8",
    )
    units = load_analysis_units(
        tmp_path,
        {"scope": {"unit_index": "spatial/spatial_units.csv"}},
    )
    assert [unit["unit_id"] for unit in units] == ["LME_001", "HS_071"]


def test_analysis_directories_route_global_outputs_separately(tmp_path) -> None:
    raw, output = analysis_directories(
        tmp_path,
        {
            "scope": {
                "raw_directory": "raw_data/SAU_downloads",
                "output_directory": "global_output",
            }
        },
    )
    assert raw == tmp_path / "raw_data" / "SAU_downloads"
    assert output == tmp_path / "global_output"


def test_build_unit_manifest_adds_readable_region_type() -> None:
    manifest = build_unit_manifest(
        [
            {"unit_id": "LME_001", "name": "East Bering Sea", "sau_region": "lme", "sau_region_id": 1},
            {"unit_id": "HS_071", "name": "Pacific", "sau_region": "highseas", "sau_region_id": 71},
        ]
    )
    assert [row["region_type"] for row in manifest] == ["LME", "High Seas"]


def test_summarize_units_labels_global_fraction_and_rank() -> None:
    species = add_species_ppr(
        pd.DataFrame(
            {
                "commercial_group": ["C"],
                "functional_group": ["F"],
                "catch_tonnes": [10.0],
                "tl": [2.0],
            }
        )
    )
    results = {
        "LME_001": {
            "name": "East Bering Sea",
            "region_type": "LME",
            "year": 2019,
            "species": species,
            "commercial": aggregate_groups(species, "commercial_group"),
            "functional": aggregate_groups(species, "functional_group"),
        }
    }
    summary = summarize_units(results, scope_label="global")
    assert summary.loc[0, "fraction_global_ppr"] == pytest.approx(1.0)
    assert summary.loc[0, "rank_global_ppr"] == 1


def test_summarize_units_assigns_deterministic_sequential_ranks_for_ties() -> None:
    empty_species = pd.DataFrame(columns=["catch_tonnes", "tl", "ppr"])
    empty_commercial = aggregate_groups(
        pd.DataFrame(columns=["commercial_group", "catch_tonnes", "tl", "ppr"]),
        "commercial_group",
    )
    empty_functional = aggregate_groups(
        pd.DataFrame(columns=["functional_group", "catch_tonnes", "tl", "ppr"]),
        "functional_group",
    )
    results = {
        unit_id: {
            "name": unit_id,
            "region_type": "High Seas",
            "year": 2019,
            "species": empty_species,
            "commercial": empty_commercial,
            "functional": empty_functional,
        }
        for unit_id in ["HS_018", "LME_064"]
    }

    summary = summarize_units(results, scope_label="global")

    assert summary["unit_id"].tolist() == ["HS_018", "LME_064"]
    assert summary["rank_global_ppr"].tolist() == [1, 2]


def test_summarize_pilot_ranks_units_and_calculates_pilot_fraction() -> None:
    species_a = add_species_ppr(
        pd.DataFrame(
            {
                "commercial_group": ["C"],
                "functional_group": ["F"],
                "catch_tonnes": [10.0],
                "tl": [2.0],
            }
        )
    )
    species_b = add_species_ppr(
        pd.DataFrame(
            {
                "commercial_group": ["C"],
                "functional_group": ["F"],
                "catch_tonnes": [10.0],
                "tl": [3.0],
            }
        )
    )
    results = {
        "A": {
            "name": "A unit",
            "region_type": "lme",
            "year": 2019,
            "species": species_a,
            "commercial": aggregate_groups(species_a, "commercial_group"),
            "functional": aggregate_groups(species_a, "functional_group"),
        },
        "B": {
            "name": "B unit",
            "region_type": "highseas",
            "year": 2019,
            "species": species_b,
            "commercial": aggregate_groups(species_b, "commercial_group"),
            "functional": aggregate_groups(species_b, "functional_group"),
        },
    }
    summary = summarize_pilot(results).set_index("unit_id")
    assert summary.loc["B", "rank_pilot_ppr"] == 1
    assert summary.loc["A", "rank_pilot_ppr"] == 2
    assert summary.loc["A", "fraction_pilot_ppr"] == pytest.approx(1.0 / 11.0)
    assert summary.loc["B", "fraction_pilot_ppr"] == pytest.approx(10.0 / 11.0)
    assert summary.loc["A", "ppr_species"] == pytest.approx(
        summary.loc["A", "ppr_commercial_correct"]
    )
