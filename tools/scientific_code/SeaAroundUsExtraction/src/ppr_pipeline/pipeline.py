from __future__ import annotations

import gc
import json
from pathlib import Path
import shutil
from typing import Any

import pandas as pd
import yaml

from .calculations import add_species_ppr, aggregate_groups
from .download import load_units_from_spatial_index
from .ingest import (
    available_years_from_archive,
    read_catch_archive,
    read_exploited_organisms,
    standardize_catch,
)
from .matching import assign_trophic_levels
from .spatial import write_spatial_outputs
from .validation import validate_region
from .years import latest_common_year


def is_global_scope(scope_label: str) -> bool:
    """Return whether a named release covers the all-unit global scope."""
    return str(scope_label).casefold().startswith("global")


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_analysis_units(root: str | Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    if "pilot_units" in config:
        return list(config["pilot_units"])
    scope = config.get("scope", {})
    if "unit_index" not in scope:
        raise ValueError("Configuration must define pilot_units or scope.unit_index.")
    return load_units_from_spatial_index(Path(root) / scope["unit_index"])


def analysis_directories(
    root: str | Path, config: dict[str, Any]
) -> tuple[Path, Path]:
    root = Path(root)
    scope = config.get("scope", {})
    raw = root / scope.get("raw_directory", "raw_data/SAU_downloads")
    output = root / scope.get("output_directory", "output")
    return raw, output


def copy_spatial_deliverables(
    root: str | Path,
    output_root: str | Path,
) -> list[Path]:
    """Copy both polygon layers and their unit index into a final output."""
    root = Path(root)
    destination = Path(output_root) / "spatial"
    destination.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for name in ("LMEs.geojson", "HighSeas.geojson", "spatial_units.csv"):
        source = root / "spatial" / name
        if not source.is_file():
            raise FileNotFoundError(f"Required spatial deliverable is missing: {source}")
        target = destination / name
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def region_type(region: str) -> str:
    try:
        return {"eez": "EEZ", "lme": "LME", "highseas": "High Seas"}[region]
    except KeyError as exc:
        raise ValueError(f"Unknown Sea Around Us region type: {region}") from exc


def build_unit_manifest(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "unit_id": unit["unit_id"],
            "name": unit["name"],
            "sau_region": unit["sau_region"],
            "sau_region_id": int(unit["sau_region_id"]),
            "region_type": region_type(unit["sau_region"]),
        }
        for unit in units
    ]


def prepare_trophic_reference(source_workbook: Path, output_csv: Path) -> pd.DataFrame:
    raw = pd.read_excel(source_workbook, sheet_name="SPPR of species in database ", header=0)
    reference = raw[["Scientific name", "Habitat", "MeanTL"]].copy()
    reference.columns = ["scientific_name", "habitat", "tl"]
    reference["tl"] = pd.to_numeric(reference["tl"], errors="coerce")
    reference = reference.dropna(subset=["scientific_name", "tl"])
    reference["scientific_name"] = reference["scientific_name"].astype(str).str.strip()
    reference = (
        reference.groupby("scientific_name", as_index=False)
        .agg(habitat=("habitat", "first"), tl=("tl", "mean"), source_rows=("tl", "size"))
        .sort_values("scientific_name")
        .reset_index(drop=True)
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    reference.to_csv(output_csv, index=False, encoding="utf-8-sig")
    return reference


def load_trophic_reference(frozen_csv: str | Path) -> pd.DataFrame:
    """Load and validate the self-contained trophic reference snapshot."""
    reference = pd.read_csv(frozen_csv, encoding="utf-8-sig")
    required = {"scientific_name", "tl"}
    missing = required - set(reference.columns)
    if missing:
        raise ValueError(f"Frozen trophic reference is missing columns: {sorted(missing)}")
    reference["scientific_name"] = reference["scientific_name"].astype(str).str.strip()
    reference["tl"] = pd.to_numeric(reference["tl"], errors="coerce")
    return reference.dropna(subset=["scientific_name", "tl"]).reset_index(drop=True)


def summarize_units(
    results: dict[str, dict[str, Any]],
    *,
    scope_label: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for unit_id, data in results.items():
        species = data["species"]
        commercial = data["commercial"]
        functional = data["functional"]
        catch_total = float(species["catch_tonnes"].sum())
        catch_matched = float(species.loc[species["tl"].notna(), "catch_tonnes"].sum())
        ppr_species = float(species["ppr"].sum())
        rows.append(
            {
                "unit_id": unit_id,
                "region_name": data["name"],
                "region_type": data["region_type"],
                "year": int(data["year"]),
                "total_catch_tonnes": catch_total,
                "matched_catch_tonnes": catch_matched,
                "missing_tl_catch_tonnes": catch_total - catch_matched,
                "catch_tl_coverage_fraction": catch_matched / catch_total if catch_total else float("nan"),
                "taxa_count": int(len(species)),
                "matched_taxa_count": int(species["tl"].notna().sum()),
                "ppr_species": ppr_species,
                # Group values use the catch-weighted mean TL, so they are the
                # Jensen-affected aggregation. ppr_species is the taxon-level truth.
                "ppr_commercial": float(commercial["ppr"].sum()),
                "ppr_functional": float(functional["ppr"].sum()),
            }
        )
    summary = pd.DataFrame(rows)
    total_ppr = float(summary["ppr_species"].sum())
    fraction_column = f"fraction_{scope_label}_ppr"
    rank_column = f"rank_{scope_label}_ppr"
    summary[fraction_column] = summary["ppr_species"] / total_ppr if total_ppr else float("nan")
    summary = summary.sort_values(
        ["ppr_species", "unit_id"], ascending=[False, True]
    ).reset_index(drop=True)
    summary[rank_column] = pd.Series(range(1, len(summary) + 1), dtype="Int64")
    return summary


def summarize_pilot(results: dict[str, dict[str, Any]]) -> pd.DataFrame:
    return summarize_units(results, scope_label="pilot")


def summarize_spatial_alternatives(summary: pd.DataFrame) -> pd.DataFrame:
    """Compare overlapping spatial systems without a cross-system denominator."""
    if summary['year'].nunique() != 1:
        raise ValueError('All spatial alternatives must use the same analysis year')
    result = summary.sort_values(
        ['region_type', 'ppr_species', 'unit_id'], ascending=[True, False, True]
    ).reset_index(drop=True).copy()
    totals = result.groupby('region_type')['ppr_species'].transform('sum').replace(0, float('nan'))
    result['fraction_type_ppr'] = result['ppr_species'] / totals
    result['rank_type_ppr'] = result.groupby('region_type').cumcount() + 1
    result['accumulated_fraction_type'] = result.groupby('region_type')['fraction_type_ppr'].cumsum()
    return result


def _coverage_table(species: pd.DataFrame) -> pd.DataFrame:
    totals = species.groupby("unit_id").agg(
        unit_catch_tonnes=("catch_tonnes", "sum"), unit_taxa=("taxon", "size")
    )
    table = species.groupby(["unit_id", "match_method", "tl_source", "match_confidence"], as_index=False).agg(
        taxa_count=("taxon", "size"), catch_tonnes=("catch_tonnes", "sum")
    )
    table = table.merge(totals, on="unit_id", how="left")
    table["taxa_fraction"] = table["taxa_count"] / table["unit_taxa"]
    table["catch_fraction"] = table["catch_tonnes"] / table["unit_catch_tonnes"]
    return table.sort_values(["unit_id", "catch_tonnes"], ascending=[True, False])


def run_analysis(
    project_root: str | Path,
    config_path: str | Path,
    *,
    requested_year: int | None = None,
    progress=print,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    config = load_config(config_path)
    units = load_analysis_units(root, config)
    scope_label = str(config.get("scope", {}).get("name", "pilot"))
    raw_dir, output_root = analysis_directories(root, config)
    table_dir = output_root / "tables"
    regions_dir = table_dir / "regions"
    table_dir.mkdir(parents=True, exist_ok=True)
    regions_dir.mkdir(parents=True, exist_ok=True)
    if is_global_scope(scope_label):
        copy_spatial_deliverables(root, output_root)
    (table_dir / "units.json").write_text(
        json.dumps(build_unit_manifest(units), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if "pilot_units" in config:
        write_spatial_outputs(
            raw_dir / "lme_regions_spatial.json",
            raw_dir / "highseas_regions_spatial.json",
            units,
            root / "spatial",
        )
    frozen_reference = root / "input" / "trophic_levels_2020.csv"
    if frozen_reference.exists():
        supplement = load_trophic_reference(frozen_reference)
    else:
        supplement = prepare_trophic_reference(
            root.parent / "sources" / "2020 sup.xlsx",
            frozen_reference,
        )

    year_sets: list[set[int]] = []
    unit_year_sets: list[set[int]] = []
    year_audit = []
    for index, unit in enumerate(units, start=1):
        unit_id = unit["unit_id"]
        years = available_years_from_archive(raw_dir / f"{unit_id}-catch.zip")
        unit_year_sets.append(years)
        if years:
            year_sets.append(years)
        year_audit.append(
            {
                "unit_id": unit_id,
                "region_name": unit["name"],
                "first_year": min(years) if years else None,
                "last_year": max(years) if years else None,
                "year_count": len(years),
                "source_data_status": "available" if years else "empty_catch_archive",
                "constrains_common_year": bool(years),
            }
        )
        if progress:
            span = f"{min(years)}-{max(years)}" if years else "empty catch archive"
            progress(f"Year scan [{index}/{len(units)}] {unit_id}: {span}")
    configured_year = config["analysis"].get("year")
    year = latest_common_year(
        year_sets,
        requested=requested_year if requested_year is not None else configured_year,
    )
    year_audit_frame = pd.DataFrame(year_audit)
    year_audit_frame["selected_common_year"] = year
    year_audit_frame["contains_selected_year"] = [
        year in years for years in unit_year_sets
    ]
    year_audit_frame.to_csv(
        table_dir / "year_availability.csv", index=False, encoding="utf-8-sig"
    )

    standardized = []
    ingestion_audits = []
    sau_refs = []
    for index, unit in enumerate(units, start=1):
        unit_id = unit["unit_id"]
        raw = read_catch_archive(
            raw_dir / f"{unit_id}-catch.zip",
            year=year,
            chunksize=50_000,
            required_only=True,
        )
        frame, audit = standardize_catch(
            raw,
            year=year,
            include_catch_types=config["analysis"]["include_catch_types"],
            include_reporting_status=config["analysis"]["include_reporting_status"],
        )
        del raw
        gc.collect()
        frame.insert(0, "year", year)
        frame.insert(0, "region_type", region_type(unit["sau_region"]))
        frame.insert(0, "region_name", unit["name"])
        frame.insert(0, "unit_id", unit_id)
        standardized.append(frame)
        ingestion_audits.append({"unit_id": unit_id, **audit})
        ref = read_exploited_organisms(raw_dir / f"{unit_id}-exploited.json")
        ref["unit_id"] = unit_id
        sau_refs.append(ref)
        if progress:
            progress(
                f"Catch [{index}/{len(units)}] {unit_id}: "
                f"{audit['taxon_rows_standardized']} taxa, {audit['standardized_tonnes']:.2f} t"
            )

    all_catch = pd.concat(standardized, ignore_index=True)
    all_sau_reference = pd.concat(sau_refs, ignore_index=True)
    match_config = config["analysis"]["matching"]
    all_species = assign_trophic_levels(
        all_catch,
        supplement,
        all_sau_reference,
        min_genus_species=int(match_config["min_genus_species"]),
        allow_commercial_group_fallback=bool(match_config["allow_commercial_group_fallback"]),
        allow_functional_group_fallback=bool(match_config["allow_functional_group_fallback"]),
    )
    te = float(config["method"]["transfer_efficiency"])
    all_species = add_species_ppr(all_species, te=te)

    results: dict[str, dict[str, Any]] = {}
    validations = []
    for index, (unit, audit) in enumerate(zip(units, ingestion_audits, strict=True), start=1):
        unit_id = unit["unit_id"]
        species = all_species.loc[all_species["unit_id"] == unit_id].copy()
        commercial = aggregate_groups(species, "commercial_group", te=te)
        functional = aggregate_groups(species, "functional_group", te=te)
        validation = validate_region(
            unit_id,
            species,
            commercial,
            functional,
            float(audit["raw_filtered_tonnes"]),
        )
        unit_dir = regions_dir / unit_id
        unit_dir.mkdir(parents=True, exist_ok=True)
        species.to_csv(unit_dir / "species.csv", index=False, encoding="utf-8-sig")
        commercial.to_csv(unit_dir / "commercial.csv", index=False, encoding="utf-8-sig")
        functional.to_csv(unit_dir / "functional.csv", index=False, encoding="utf-8-sig")
        species.loc[species["tl"].isna()].to_csv(
            unit_dir / "missing_tl.csv", index=False, encoding="utf-8-sig"
        )
        validation.to_csv(unit_dir / "validation.csv", index=False, encoding="utf-8-sig")
        results[unit_id] = {
            "name": unit["name"],
            "region_type": region_type(unit["sau_region"]),
            "year": year,
            "species": species,
            "commercial": commercial,
            "functional": functional,
            "validation": validation,
        }
        validations.append(validation)
        if progress:
            progress(f"Output [{index}/{len(units)}] {unit_id}")

    summary = summarize_units(results, scope_label=scope_label)
    validation_table = pd.concat(validations, ignore_index=True)
    coverage = _coverage_table(all_species)

    summary.to_csv(
        table_dir / f"{scope_label}_summary.csv", index=False, encoding="utf-8-sig"
    )
    validation_table.to_csv(table_dir / "validation.csv", index=False, encoding="utf-8-sig")
    coverage.to_csv(table_dir / "tl_coverage.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(ingestion_audits).to_csv(
        table_dir / "ingestion_audit.csv", index=False, encoding="utf-8-sig"
    )
    run_metadata = {
        "scope": (
            "all Sea Around Us LMEs and High Seas units"
            if is_global_scope(scope_label)
            else "all Sea Around Us EEZ units; overlapping alternatives to LMEs"
            if scope_label == "eez"
            else "five-region pilot; not a global estimate"
        ),
        "scope_label": scope_label,
        "unit_count": len(units),
        "lme_count": sum(unit["sau_region"] == "lme" for unit in units),
        "highseas_count": sum(unit["sau_region"] == "highseas" for unit in units),
        "eez_count": sum(unit["sau_region"] == "eez" for unit in units),
        "zero_catch_unit_count": sum(not years for years in unit_year_sets),
        "year": year,
        "transfer_efficiency": te,
        "apply_wet_weight_to_carbon_divisor": False,
        "catch_types": config["analysis"]["include_catch_types"],
        "reporting_status": config["analysis"]["include_reporting_status"],
        "ppr_unit": "tonnes_primary_production_equivalent",
    }
    (table_dir / "run_metadata.json").write_text(
        json.dumps(run_metadata, indent=2), encoding="utf-8"
    )
    return {"year": year, "summary": summary, "validation": validation_table, "results": results}


def run_pipeline(project_root: str | Path, requested_year: int | None = None) -> dict[str, Any]:
    root = Path(project_root).resolve()
    return run_analysis(
        root,
        root / "config" / "pilot.yml",
        requested_year=requested_year,
    )


def run_global_pipeline(
    project_root: str | Path, requested_year: int | None = None
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    return run_analysis(
        root,
        root / "config" / "global.yml",
        requested_year=requested_year,
    )
