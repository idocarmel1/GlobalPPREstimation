"""Distill a Sea Around Us catch archive to one row per taxon per year.

The processed tables elsewhere in this project cover a single analysis year. This
module produces the full 1950-2019 series, which is the only place per-taxon
per-year catch exists outside the raw archives.

It reuses :func:`ingest.standardize_catch` once per year rather than reimplementing
the filtering, so a distilled table sliced to the analysis year reproduces the
existing ``species.csv`` catch figures by construction.
"""
from __future__ import annotations

import gzip
from pathlib import Path
from typing import Iterable

import pandas as pd

from .ingest import read_catch_archive, standardize_catch

COLUMNS = [
    "unit_id",
    "year",
    "taxon",
    "common_name",
    "functional_group",
    "commercial_group",
    "catch_tonnes",
    "landings_tonnes",
    "discards_tonnes",
    "reported_tonnes",
    "unreported_tonnes",
]


def distill_archive(
    archive_path: str | Path,
    unit_id: str,
    *,
    include_catch_types: Iterable[str] = ("Landings", "Discards"),
    include_reporting_status: Iterable[str] = ("Reported", "Unreported"),
) -> pd.DataFrame:
    """Return one row per taxon per year for a single catch archive.

    Tonnage is summed over fishing entity, sector, gear and end-use, honouring the
    catch-type and reporting-status filters. An archive with no rows yields an empty
    frame carrying the full column set.
    """

    raw = read_catch_archive(archive_path, required_only=True)
    if raw.empty:
        return pd.DataFrame(columns=COLUMNS)

    years = sorted(pd.to_numeric(raw["year"], errors="coerce").dropna().astype(int).unique())
    frames: list[pd.DataFrame] = []
    for year in years:
        standardized, _audit = standardize_catch(
            raw,
            year=year,
            include_catch_types=include_catch_types,
            include_reporting_status=include_reporting_status,
        )
        if standardized.empty:
            continue
        standardized = standardized.copy()
        standardized.insert(0, "year", year)
        standardized.insert(0, "unit_id", unit_id)
        frames.append(standardized)

    if not frames:
        return pd.DataFrame(columns=COLUMNS)

    out = pd.concat(frames, ignore_index=True)
    missing = [c for c in COLUMNS if c not in out.columns]
    if missing:
        raise KeyError(f"standardize_catch did not supply: {missing}")
    return out[COLUMNS].sort_values(["year", "taxon"]).reset_index(drop=True)


def write_distilled(frame: pd.DataFrame, out_path: str | Path) -> Path:
    """Write a distilled frame as gzipped CSV and return the path."""

    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        frame.to_csv(handle, index=False)
    return path
