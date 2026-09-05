from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Iterable

import pandas as pd


RAW_REQUIRED_COLUMNS = {
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
}


def _catch_csv_name(zf: zipfile.ZipFile, archive: Path) -> str:
    csv_names = [name for name in zf.namelist() if name.lower().endswith(".csv")]
    if len(csv_names) != 1:
        raise ValueError(f"Expected one catch CSV in {archive}, found {len(csv_names)}.")
    return csv_names[0]


def read_catch_archive(
    path: str | Path,
    *,
    year: int | None = None,
    chunksize: int = 250_000,
    required_only: bool = False,
) -> pd.DataFrame:
    """Read a Sea Around Us catch ZIP, optionally retaining one year only."""
    archive = Path(path)
    with zipfile.ZipFile(archive) as zf:
        csv_name = _catch_csv_name(zf, archive)
        if zf.getinfo(csv_name).file_size == 0:
            return pd.DataFrame(columns=sorted(RAW_REQUIRED_COLUMNS))
        with zf.open(csv_name) as handle:
            usecols = sorted(RAW_REQUIRED_COLUMNS) if required_only else None
            if year is None:
                return pd.read_csv(handle, usecols=usecols, low_memory=False)
            selected = []
            columns: list[str] | None = None
            for chunk in pd.read_csv(
                handle,
                usecols=usecols,
                chunksize=chunksize,
                low_memory=False,
            ):
                columns = list(chunk.columns)
                numeric_year = pd.to_numeric(chunk["year"], errors="raise").astype(int)
                matches = chunk.loc[numeric_year == int(year)]
                if len(matches):
                    selected.append(matches)
            return (
                pd.concat(selected, ignore_index=True)
                if selected
                else pd.DataFrame(columns=columns or [])
            )


def available_years_from_archive(
    path: str | Path,
    *,
    chunksize: int = 500_000,
) -> set[int]:
    """Scan only the year column of a catch ZIP with bounded memory."""
    archive = Path(path)
    years: set[int] = set()
    with zipfile.ZipFile(archive) as zf:
        csv_name = _catch_csv_name(zf, archive)
        if zf.getinfo(csv_name).file_size == 0:
            return years
        with zf.open(csv_name) as handle:
            for chunk in pd.read_csv(handle, usecols=["year"], chunksize=chunksize):
                years.update(pd.to_numeric(chunk["year"], errors="raise").astype(int).unique())
    return years


def read_exploited_organisms(path: str | Path) -> pd.DataFrame:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    data = payload.get("data", [])
    frame = pd.DataFrame(data)
    if frame.empty:
        return pd.DataFrame(columns=["scientific_name", "tl"])
    return frame.rename(columns={"trophic_level": "tl"})


def available_years(frame: pd.DataFrame) -> set[int]:
    return set(pd.to_numeric(frame["year"], errors="raise").astype(int).unique())


def _category_totals(
    frame: pd.DataFrame,
    keys: list[str],
    category_column: str,
    categories: dict[str, str],
) -> pd.DataFrame:
    grouped = (
        frame.groupby(keys + [category_column], dropna=False, as_index=False)["tonnes"]
        .sum()
    )
    pivot = grouped.pivot_table(
        index=keys,
        columns=category_column,
        values="tonnes",
        aggfunc="sum",
        fill_value=0.0,
        dropna=False,
    ).reset_index()
    pivot.columns.name = None
    for raw_label, output_label in categories.items():
        if raw_label not in pivot:
            pivot[raw_label] = 0.0
        pivot = pivot.rename(columns={raw_label: output_label})
    return pivot[keys + list(categories.values())]


def standardize_catch(
    raw: pd.DataFrame,
    *,
    year: int,
    include_catch_types: Iterable[str] = ("Landings", "Discards"),
    include_reporting_status: Iterable[str] = ("Reported", "Unreported"),
) -> tuple[pd.DataFrame, dict[str, float | int | str | bool]]:
    """Filter and aggregate the full Sea Around Us schema to one row per taxon."""

    missing = RAW_REQUIRED_COLUMNS - set(raw.columns)
    if missing:
        raise KeyError(f"Missing Sea Around Us columns: {sorted(missing)}")
    year = int(year)
    if raw.empty:
        columns = [
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
        audit: dict[str, float | int | str | bool] = {
            "area_name": "",
            "area_type": "",
            "year": year,
            "raw_rows_selected": 0,
            "taxon_rows_standardized": 0,
            "raw_filtered_tonnes": 0.0,
            "standardized_tonnes": 0.0,
            "difference_tonnes": 0.0,
            "reconciled": True,
            "source_data_status": "empty_catch_archive",
        }
        return pd.DataFrame(columns=columns), audit
    if year not in available_years(raw):
        raise ValueError(f"Year {year} is not present in this catch dataset.")

    selected = raw.loc[
        (pd.to_numeric(raw["year"], errors="raise").astype(int) == year)
        & raw["catch_type"].isin(list(include_catch_types))
        & raw["reporting_status"].isin(list(include_reporting_status))
    ].copy()
    selected["tonnes"] = pd.to_numeric(selected["tonnes"], errors="raise")
    if (selected["tonnes"] < 0).any():
        raise ValueError("Sea Around Us catch contains negative tonnes.")

    for column in ["scientific_name", "common_name", "functional_group", "commercial_group"]:
        selected[column] = selected[column].fillna("Unclassified").replace("", "Unclassified")
    keys = ["scientific_name", "common_name", "functional_group", "commercial_group"]

    total = selected.groupby(keys, dropna=False, as_index=False)["tonnes"].sum()
    total = total.rename(columns={"scientific_name": "taxon", "tonnes": "catch_tonnes"})
    merge_keys = ["taxon", "common_name", "functional_group", "commercial_group"]

    catch_breakdown = _category_totals(
        selected,
        keys,
        "catch_type",
        {"Landings": "landings_tonnes", "Discards": "discards_tonnes"},
    ).rename(columns={"scientific_name": "taxon"})
    reporting_breakdown = _category_totals(
        selected,
        keys,
        "reporting_status",
        {"Reported": "reported_tonnes", "Unreported": "unreported_tonnes"},
    ).rename(columns={"scientific_name": "taxon"})

    result = total.merge(catch_breakdown, on=merge_keys, how="left").merge(
        reporting_breakdown, on=merge_keys, how="left"
    )
    raw_total = float(selected["tonnes"].sum())
    standardized_total = float(result["catch_tonnes"].sum())
    area_name = str(selected["area_name"].iloc[0]) if len(selected) else ""
    area_type = str(selected["area_type"].iloc[0]) if len(selected) else ""
    audit: dict[str, float | int | str | bool] = {
        "area_name": area_name,
        "area_type": area_type,
        "year": year,
        "raw_rows_selected": int(len(selected)),
        "taxon_rows_standardized": int(len(result)),
        "raw_filtered_tonnes": raw_total,
        "standardized_tonnes": standardized_total,
        "difference_tonnes": standardized_total - raw_total,
        "reconciled": bool(abs(standardized_total - raw_total) <= max(1e-8, abs(raw_total) * 1e-12)),
        "source_data_status": "available",
    }
    return result.sort_values("catch_tonnes", ascending=False).reset_index(drop=True), audit
