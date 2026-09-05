from __future__ import annotations

import numpy as np
import pandas as pd


def _sum_ppr(frame: pd.DataFrame) -> float:
    return float(pd.to_numeric(frame["ppr_correct"], errors="coerce").sum())


def _jensen_violations(frame: pd.DataFrame, tolerance: float) -> int:
    valid = frame[["ppr_correct", "ppr_jensen"]].dropna()
    if valid.empty:
        return 0
    threshold = tolerance * np.maximum(1.0, np.abs(valid["ppr_correct"].to_numpy()))
    return int(np.sum(valid["ppr_correct"].to_numpy() + threshold < valid["ppr_jensen"].to_numpy()))


def validate_region(
    unit_id: str,
    species: pd.DataFrame,
    commercial: pd.DataFrame,
    functional: pd.DataFrame,
    raw_filtered_tonnes: float,
    *,
    tolerance: float = 1e-10,
) -> pd.DataFrame:
    """Return long-form validation metrics for one pilot unit."""

    catch_total = float(species["catch_tonnes"].sum())
    matched = species.loc[species["tl"].notna()]
    matched_catch = float(matched["catch_tonnes"].sum())
    species_ppr = float(matched["ppr"].sum())
    commercial_ppr = _sum_ppr(commercial)
    functional_ppr = _sum_ppr(functional)

    catch_ok = bool(np.isclose(catch_total, raw_filtered_tonnes, rtol=tolerance, atol=1e-8))
    commercial_ok = bool(np.isclose(species_ppr, commercial_ppr, rtol=tolerance, atol=1e-8))
    functional_ok = bool(np.isclose(species_ppr, functional_ppr, rtol=tolerance, atol=1e-8))
    metrics: list[tuple[str, object, str]] = [
        ("raw_filtered_tonnes", float(raw_filtered_tonnes), "tonnes"),
        ("species_catch_tonnes", catch_total, "tonnes"),
        ("catch_difference_tonnes", catch_total - float(raw_filtered_tonnes), "tonnes"),
        ("catch_reconciled", catch_ok, "boolean"),
        ("matched_catch_tonnes", matched_catch, "tonnes"),
        (
            "catch_coverage_fraction",
            matched_catch / catch_total if catch_total else np.nan,
            "fraction",
        ),
        ("taxa_count", int(len(species)), "count"),
        ("matched_taxa_count", int(species["tl"].notna().sum()), "count"),
        ("unmatched_taxa_count", int(species["tl"].isna().sum()), "count"),
        ("species_ppr", species_ppr, "tonnes_primary_production_equivalent"),
        ("commercial_ppr", commercial_ppr, "tonnes_primary_production_equivalent"),
        ("functional_ppr", functional_ppr, "tonnes_primary_production_equivalent"),
        ("commercial_ppr_difference", commercial_ppr - species_ppr, "tonnes_primary_production_equivalent"),
        ("functional_ppr_difference", functional_ppr - species_ppr, "tonnes_primary_production_equivalent"),
        ("commercial_ppr_reconciled", commercial_ok, "boolean"),
        ("functional_ppr_reconciled", functional_ok, "boolean"),
        ("commercial_jensen_violations", _jensen_violations(commercial, tolerance), "count"),
        ("functional_jensen_violations", _jensen_violations(functional, tolerance), "count"),
    ]
    return pd.DataFrame(
        [{"unit_id": unit_id, "check": check, "value": value, "unit": unit} for check, value, unit in metrics]
    )

