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
    """Aggregate taxa to groups using the catch-weighted mean trophic level.

    This is deliberately the Jensen-affected aggregation: the catch-weighted mean TL
    is exponentiated once per group, rather than summing each taxon's PPR. Because
    ``10 ** (TL - 1)`` is convex, the result understates the taxon-level sum whenever
    a group spans more than one trophic level. That gap is the point - it is what
    makes the cost of moving from taxa to groups visible, which an Ecopath model
    cannot show on its own because it has no taxon level.

    The correctly-aggregated value is not returned. It is exactly the sum of taxon
    ``ppr`` within the group, recoverable from the taxon table with a ``groupby``.
    """

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
        "catch_tonnes_matched",
        "tl_weighted",
        "sppr",
        "ppr",
    ]
    rows: list[dict[str, Any]] = []
    for group, part in work.groupby(group_column, sort=True, dropna=False):
        matched = part.loc[part["is_tl_matched"]]
        catch_matched = float(matched[catch_column].sum())

        if catch_matched > 0:
            tl_weighted = float(
                np.average(matched[tl_column].to_numpy(), weights=matched[catch_column].to_numpy())
            )
            sppr = float(calculate_sppr(tl_weighted, te=te))
            ppr = catch_matched * sppr
        else:
            tl_weighted = np.nan
            sppr = np.nan
            ppr = np.nan

        rows.append(
            {
                group_column: group,
                "catch_tonnes_matched": catch_matched,
                "tl_weighted": tl_weighted,
                "sppr": sppr,
                "ppr": ppr,
            }
        )
    return pd.DataFrame(rows, columns=output_columns)
