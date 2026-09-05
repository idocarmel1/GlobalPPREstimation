from __future__ import annotations

import zipfile

import pandas as pd
import pytest

from ppr_pipeline.ingest import (
    available_years,
    available_years_from_archive,
    read_catch_archive,
    standardize_catch,
)


def _raw_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "area_name": ["Test"] * 6,
            "area_type": ["lme"] * 6,
            "year": [2018, 2019, 2019, 2019, 2019, 2019],
            "scientific_name": ["A alpha", "A alpha", "A alpha", "B beta", "B beta", "C gamma"],
            "common_name": ["A", "A", "A", "B", "B", "C"],
            "functional_group": ["F1", "F1", "F1", "F2", "F2", "F3"],
            "commercial_group": ["C1", "C1", "C1", "C2", "C2", "C3"],
            "fishing_entity": ["X", "X", "Y", "X", "X", "X"],
            "fishing_sector": ["Industrial"] * 6,
            "catch_type": ["Landings", "Landings", "Discards", "Landings", "Discards", "Landings"],
            "reporting_status": ["Reported", "Reported", "Unreported", "Unreported", "Reported", "Reported"],
            "gear_type": ["trawl"] * 6,
            "end_use_type": ["food", "food", None, "food", None, "food"],
            "tonnes": [100.0, 10.0, 2.0, 20.0, 3.0, 5.0],
            "landed_value": [1.0] * 6,
        }
    )


def test_available_years_reads_unique_integer_years() -> None:
    assert available_years(_raw_fixture()) == {2018, 2019}


def test_archive_year_scan_and_filtered_read_are_chunk_safe(tmp_path) -> None:
    archive = tmp_path / "catch.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("catch.csv", _raw_fixture().to_csv(index=False))
    assert available_years_from_archive(archive, chunksize=2) == {2018, 2019}
    selected = read_catch_archive(archive, year=2019, chunksize=2)
    assert set(selected["year"]) == {2019}
    assert len(selected) == 5


def test_archive_reader_can_skip_unused_raw_dimensions(tmp_path) -> None:
    archive = tmp_path / "catch.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("catch.csv", _raw_fixture().to_csv(index=False))

    selected = read_catch_archive(
        archive,
        year=2019,
        chunksize=2,
        required_only=True,
    )

    assert "landed_value" not in selected
    assert "fishing_entity" not in selected
    assert set(selected.columns) == set(
        [
            "area_name",
            "area_type",
            "year",
            "scientific_name",
            "common_name",
            "functional_group",
            "commercial_group",
            "catch_type",
            "reporting_status",
            "tonnes",
        ]
    )


def test_empty_sea_around_us_archive_is_a_valid_zero_catch_dataset(tmp_path) -> None:
    archive = tmp_path / "empty-catch.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SAU HighSeas 18 v50-1.csv", b"")

    assert available_years_from_archive(archive) == set()
    raw = read_catch_archive(archive, year=2019)
    result, audit = standardize_catch(raw, year=2019)

    assert result.empty
    assert set(["taxon", "catch_tonnes", "landings_tonnes", "discards_tonnes"]).issubset(result)
    assert audit["raw_filtered_tonnes"] == 0.0
    assert audit["source_data_status"] == "empty_catch_archive"


def test_standardize_catch_sums_all_dimensions_without_double_counting() -> None:
    result, audit = standardize_catch(
        _raw_fixture(),
        year=2019,
        include_catch_types=["Landings", "Discards"],
        include_reporting_status=["Reported", "Unreported"],
    )
    keyed = result.set_index("taxon")
    assert result["catch_tonnes"].sum() == pytest.approx(40.0)
    assert audit["raw_filtered_tonnes"] == pytest.approx(40.0)
    assert keyed.loc["A alpha", "catch_tonnes"] == pytest.approx(12.0)
    assert keyed.loc["A alpha", "landings_tonnes"] == pytest.approx(10.0)
    assert keyed.loc["A alpha", "discards_tonnes"] == pytest.approx(2.0)
    assert keyed.loc["B beta", "reported_tonnes"] == pytest.approx(3.0)
    assert keyed.loc["B beta", "unreported_tonnes"] == pytest.approx(20.0)
    assert audit["difference_tonnes"] == pytest.approx(0.0)
    assert audit["source_data_status"] == "available"


def test_standardize_catch_can_select_landings_only() -> None:
    result, audit = standardize_catch(
        _raw_fixture(),
        year=2019,
        include_catch_types=["Landings"],
        include_reporting_status=["Reported", "Unreported"],
    )
    assert result["catch_tonnes"].sum() == pytest.approx(35.0)
    assert audit["raw_filtered_tonnes"] == pytest.approx(35.0)


def test_standardize_catch_rejects_absent_year() -> None:
    with pytest.raises(ValueError, match="not present"):
        standardize_catch(_raw_fixture(), year=2020)


def test_category_breakdown_retains_observed_taxon_keys_only() -> None:
    from ppr_pipeline.ingest import _category_totals
    raw = _raw_fixture().loc[lambda frame: frame.year == 2019]
    keys = ['scientific_name','common_name','functional_group','commercial_group']
    result = _category_totals(raw, keys, 'catch_type',
                              {'Landings':'landings','Discards':'discards'})
    assert len(result) == len(raw[keys].drop_duplicates()) == 3
    assert result['landings'].sum() == pytest.approx(35)
    assert result['discards'].sum() == pytest.approx(5)
