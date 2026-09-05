from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _validate_te(te: float) -> None:
    if not 0 < te < 1:
        raise ValueError("Transfer efficiency must be between 0 and 1.")


def calculate_sppr(tl: Any, te: float = 0.1) -> Any:
    """Return specific PPR, `(1 / te) ** (tl - 1)`.

    Scalars remain scalars; pandas Series and numpy arrays preserve their
    vector shape. Missing TL values propagate as missing SPPR values.
    """

    _validate_te(te)
    return np.power(1.0 / te, tl - 1.0)


def add_species_ppr(
    frame: pd.DataFrame,
    te: float = 0.1,
    catch_column: str = "catch_tonnes",
    tl_column: str = "tl",
) -> pd.DataFrame:
    """Add `sppr` and `ppr` to species/taxon catch rows."""

    _validate_te(te)
    result = frame.copy()
    catch = pd.to_numeric(result[catch_column], errors="raise")
    if (catch < 0).any():
        raise ValueError("Catch must be non-negative.")
    tl = pd.to_numeric(result[tl_column], errors="raise")
    result[catch_column] = catch
    result[tl_column] = tl
    result["sppr"] = calculate_sppr(tl, te=te)
    result["ppr"] = catch * result["sppr"]
    return result


def aggregate_groups(
    species: pd.DataFrame,
    group_column: str,
    te: float = 0.1,
    catch_column: str = "catch_tonnes",
    tl_column: str = "tl",
) -> pd.DataFrame:
    """Aggregate species PPR correctly and with the intentional Jensen error."""

    _validate_te(te)
    required = {group_column, catch_column, tl_column, "ppr"}
    missing = required - set(species.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    work = species.copy()
    work[group_column] = work[group_column].fillna("Unclassified").replace("", "Unclassified")
    work[catch_column] = pd.to_numeric(work[catch_column], errors="raise")
    if (work[catch_column] < 0).any():
        raise ValueError("Catch must be non-negative.")
    work[tl_column] = pd.to_numeric(work[tl_column], errors="raise")
    work["is_tl_matched"] = work[tl_column].notna()

    output_columns = [
        group_column,
        "taxon_count_total",
        "taxon_count_matched",
        "catch_tonnes_total",
        "catch_tonnes_matched",
        "catch_tonnes_missing_tl",
        "catch_coverage_fraction",
        "sppr_correct",
        "ppr_correct",
        "tl_weighted_jensen",
        "sppr_jensen",
        "ppr_jensen",
        "jensen_difference",
        "jensen_ratio_correct_to_error",
        "jensen_percent_difference",
    ]
    rows: list[dict[str, Any]] = []
    for group, part in work.groupby(group_column, sort=True, dropna=False):
        matched = part.loc[part["is_tl_matched"]].copy()
        catch_total = float(part[catch_column].sum())
        catch_matched = float(matched[catch_column].sum())
        ppr_correct = float(matched["ppr"].sum()) if len(matched) else np.nan

        if catch_matched > 0:
            tl_weighted = float(
                np.average(matched[tl_column].to_numpy(), weights=matched[catch_column].to_numpy())
            )
            sppr_correct = ppr_correct / catch_matched
            sppr_jensen = float(calculate_sppr(tl_weighted, te=te))
            ppr_jensen = catch_matched * sppr_jensen
            difference = ppr_correct - ppr_jensen
            ratio = ppr_correct / ppr_jensen if ppr_jensen else np.nan
            percent = difference / ppr_jensen if ppr_jensen else np.nan
        else:
            tl_weighted = np.nan
            sppr_correct = np.nan
            sppr_jensen = np.nan
            ppr_jensen = np.nan
            difference = np.nan
            ratio = np.nan
            percent = np.nan

        rows.append(
            {
                group_column: group,
                "taxon_count_total": int(len(part)),
                "taxon_count_matched": int(len(matched)),
                "catch_tonnes_total": catch_total,
                "catch_tonnes_matched": catch_matched,
                "catch_tonnes_missing_tl": catch_total - catch_matched,
                "catch_coverage_fraction": catch_matched / catch_total if catch_total else np.nan,
                "sppr_correct": sppr_correct,
                "ppr_correct": ppr_correct,
                "tl_weighted_jensen": tl_weighted,
                "sppr_jensen": sppr_jensen,
                "ppr_jensen": ppr_jensen,
                "jensen_difference": difference,
                "jensen_ratio_correct_to_error": ratio,
                "jensen_percent_difference": percent,
            }
        )
    return pd.DataFrame(rows, columns=output_columns)
