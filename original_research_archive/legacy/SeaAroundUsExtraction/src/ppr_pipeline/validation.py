from __future__ import annotations

import numpy as np
import pandas as pd


def _sum_ppr(frame: pd.DataFrame) -> float:
    return float(pd.to_numeric(frame["ppr"], errors="coerce").sum())


def validate_region(
    unit_id: str,
    species: pd.DataFrame,
    commercial: pd.DataFrame,
    functional: pd.DataFrame,
    raw_filtered_tonnes: float,
    *,
    tolerance: float = 1e-10,
) -> pd.DataFrame:
    """Return long-form validation metrics for one unit.

    ``commercial_ppr_difference`` and ``functional_ppr_difference`` are the group PPR
    minus the taxon-summed PPR. Because the group figures use the catch-weighted mean
    trophic level, these differences are the Jensen gap and are expected to be
    negative wherever a group spans more than one trophic level.

    ``group_ppr_within_convexity_bound`` asserts the one-sided invariant that pairs
    with those differences. ``calculate_sppr`` is ``(1 / te) ** (TL - 1)``, which is
    convex, so exponentiating a catch-weighted mean TL can never exceed the sum of
    the individual taxa: group PPR <= taxon-summed PPR, always. The taxon-summed
    value is ``species_ppr``, which is still computed here - it is the corrected
    figure the Jensen-affected group value is meant to be read against. A sign error,
    a weighting error, or a switch to an unweighted mean TL would push a difference
    positive, and this check is what catches that. The bound is one-sided and uses
    the same relative/absolute pair as the catch reconciliation above.

    ``tl_coverage_complete`` guards the decision to drop the per-group coverage
    columns: it is False as soon as any taxon lacks a trophic level, which would make
    the group PPR a silent underestimate.
    """

    catch_total = float(species["catch_tonnes"].sum())
    matched = species.loc[species["tl"].notna()]
    matched_catch = float(matched["catch_tonnes"].sum())
    species_ppr = float(matched["ppr"].sum())
    commercial_ppr = _sum_ppr(commercial)
    functional_ppr = _sum_ppr(functional)

    catch_ok = bool(np.isclose(catch_total, raw_filtered_tonnes, rtol=tolerance, atol=1e-8))
    # One-sided form of the np.isclose bound used for the catch reconciliation: a
    # difference may be arbitrarily negative (that is the Jensen gap) but may only
    # exceed zero by floating-point noise.
    convexity_bound = tolerance * abs(species_ppr) + 1e-8
    convexity_ok = bool(
        commercial_ppr - species_ppr <= convexity_bound
        and functional_ppr - species_ppr <= convexity_bound
    )
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
        ("group_ppr_within_convexity_bound", convexity_ok, "boolean"),
        ("tl_coverage_complete", bool(species["tl"].notna().all()), "boolean"),
    ]
    return pd.DataFrame(
        [{"unit_id": unit_id, "check": check, "value": value, "unit": unit} for check, value, unit in metrics]
    )

