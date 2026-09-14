from __future__ import annotations

import gzip
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from ppr_pipeline import annual_catch

RAW_HEADER = [
    "area_name", "area_type", "year", "scientific_name", "common_name",
    "functional_group", "commercial_group", "fishing_entity", "fishing_sector",
    "catch_type", "reporting_status", "gear_type", "end_use_type", "tonnes", "landed_value",
]


def _row(year: int, taxon: str, group: str, comm: str, entity: str,
         catch_type: str, status: str, tonnes: float) -> list:
    return [
        "California Current", "lme", year, taxon, f"{taxon} common",
        group, comm, entity, "Industrial", catch_type, status, "lines",
        "Direct human consumption", tonnes, tonnes * 100,
    ]


@pytest.fixture()
def archive(tmp_path: Path) -> Path:
    rows = [
        # 1950: one taxon split across two fishing entities - must sum to 3.0
        _row(1950, "Merluccius productus", "Medium benthopelagics", "Cod-likes", "USA", "Landings", "Reported", 1.0),
        _row(1950, "Merluccius productus", "Medium benthopelagics", "Cod-likes", "Canada", "Landings", "Reported", 2.0),
        # 1950: a discard, and an unreported landing
        _row(1950, "Merluccius productus", "Medium benthopelagics", "Cod-likes", "USA", "Discards", "Unreported", 0.5),
        # 1951: a different taxon
        _row(1951, "Engraulis mordax", "Small pelagics", "Anchovies", "USA", "Landings", "Reported", 7.0),
    ]
    csv = ",".join(RAW_HEADER) + "\n" + "\n".join(",".join(str(v) for v in r) for r in rows) + "\n"
    path = tmp_path / "LME_003-catch.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("LME_003-catch.csv", csv)
    return path


def test_distill_archive_returns_one_row_per_taxon_per_year(archive: Path) -> None:
    out = annual_catch.distill_archive(archive, "LME_003")

    assert list(out.columns) == [
        "unit_id", "year", "taxon", "common_name", "functional_group",
        "commercial_group", "catch_tonnes", "landings_tonnes",
        "discards_tonnes", "reported_tonnes", "unreported_tonnes",
    ]
    assert set(out["year"]) == {1950, 1951}
    assert len(out) == 2  # one taxon per year
    assert (out["unit_id"] == "LME_003").all()


def test_distill_archive_sums_over_fishing_entity(archive: Path) -> None:
    out = annual_catch.distill_archive(archive, "LME_003")
    row = out[(out["year"] == 1950)].iloc[0]

    # 1.0 + 2.0 landings + 0.5 discards
    assert row["catch_tonnes"] == pytest.approx(3.5)
    assert row["landings_tonnes"] == pytest.approx(3.0)
    assert row["discards_tonnes"] == pytest.approx(0.5)


def test_distill_archive_honours_the_catch_type_filter(archive: Path) -> None:
    out = annual_catch.distill_archive(archive, "LME_003", include_catch_types=("Landings",))
    row = out[(out["year"] == 1950)].iloc[0]

    assert row["catch_tonnes"] == pytest.approx(3.0)
    assert row["discards_tonnes"] == pytest.approx(0.0)


def test_distill_archive_returns_empty_frame_for_empty_archive(tmp_path: Path) -> None:
    path = tmp_path / "HS_999-catch.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("HS_999-catch.csv", "")

    out = annual_catch.distill_archive(path, "HS_999")
    assert out.empty
    assert list(out.columns)[:2] == ["unit_id", "year"]


def test_write_distilled_produces_a_readable_gzip(archive: Path, tmp_path: Path) -> None:
    frame = annual_catch.distill_archive(archive, "LME_003")
    out = annual_catch.write_distilled(frame, tmp_path / "LME_003.csv.gz")

    assert out.exists()
    with gzip.open(out, "rt", encoding="utf-8") as fh:
        reread = pd.read_csv(fh, float_precision="round_trip")
    assert len(reread) == len(frame)
    assert list(reread.columns) == list(frame.columns)
