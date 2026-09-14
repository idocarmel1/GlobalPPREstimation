from __future__ import annotations

import re
import unicodedata

import numpy as np
import pandas as pd


def normalize_taxon_name(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    text = unicodedata.normalize("NFKC", str(value)).strip()
    return re.sub(r"\s+", " ", text).casefold()


def _standardize_reference(frame: pd.DataFrame, source: str) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame(columns=["unit_id", "scientific_name", "taxon_key", "tl", "source"])
    name_column = "scientific_name" if "scientific_name" in frame else "Scientific name"
    if "tl" in frame:
        tl_column = "tl"
    elif "MeanTL" in frame:
        tl_column = "MeanTL"
    else:
        tl_column = "trophic_level"
    columns = (["unit_id"] if "unit_id" in frame else []) + [name_column, tl_column]
    ref = frame[columns].copy()
    ref = ref.rename(columns={name_column: "scientific_name", tl_column: "tl"})
    ref["tl"] = pd.to_numeric(ref["tl"], errors="coerce")
    ref["taxon_key"] = ref["scientific_name"].map(normalize_taxon_name)
    ref = ref.loc[(ref["taxon_key"] != "") & ref["tl"].notna()].copy()
    group_keys = (["unit_id"] if "unit_id" in ref else []) + ["taxon_key"]
    ref = (
        ref.groupby(group_keys, as_index=False)
        .agg(scientific_name=("scientific_name", "first"), tl=("tl", "mean"))
    )
    ref["source"] = source
    return ref


def _set_matches(
    out: pd.DataFrame,
    mask: pd.Series,
    values: pd.Series,
    method: str,
    source: str,
    confidence: str,
    reference: pd.Series | str,
) -> None:
    out.loc[mask, "tl"] = values.loc[mask]
    out.loc[mask, "match_method"] = method
    out.loc[mask, "tl_source"] = source
    out.loc[mask, "match_confidence"] = confidence
    if isinstance(reference, pd.Series):
        out.loc[mask, "reference_taxon"] = reference.loc[mask]
    else:
        out.loc[mask, "reference_taxon"] = reference


def assign_trophic_levels(
    catch: pd.DataFrame,
    supplement: pd.DataFrame,
    sau_reference: pd.DataFrame,
    *,
    min_genus_species: int = 2,
    allow_commercial_group_fallback: bool = True,
    allow_functional_group_fallback: bool = True,
) -> pd.DataFrame:
    """Assign TL values using explicit, ordered matches and transparent fallbacks."""

    if min_genus_species < 2:
        raise ValueError("min_genus_species must be at least 2")
    required = {"taxon", "commercial_group", "functional_group", "catch_tonnes"}
    missing = required - set(catch.columns)
    if missing:
        raise KeyError(f"Missing required catch columns: {sorted(missing)}")

    out = catch.copy()
    out["taxon_key"] = out["taxon"].map(normalize_taxon_name)
    out["tl"] = np.nan
    out["match_method"] = "unmatched"
    out["tl_source"] = "Missing"
    out["match_confidence"] = "none"
    out["reference_taxon"] = ""

    sup = _standardize_reference(supplement, "2020 supplement MeanTL")
    sau = _standardize_reference(sau_reference, "Sea Around Us exploited organisms")

    sup_tl = out["taxon_key"].map(sup.set_index("taxon_key")["tl"] if len(sup) else {})
    sup_name = out["taxon_key"].map(
        sup.set_index("taxon_key")["scientific_name"] if len(sup) else {}
    )
    exact_sup = sup_tl.notna()
    _set_matches(
        out,
        exact_sup,
        sup_tl,
        "exact_2020_supplement",
        "2020 supplement MeanTL",
        "high",
        sup_name,
    )

    if len(sau) and "unit_id" in out and "unit_id" in sau:
        lookup = sau.set_index(["unit_id", "taxon_key"])[["tl", "scientific_name"]]
        joined = out[["unit_id", "taxon_key"]].join(
            lookup, on=["unit_id", "taxon_key"], how="left"
        )
        sau_tl = joined["tl"]
        sau_name = joined["scientific_name"]
    else:
        sau_tl = out["taxon_key"].map(
            sau.set_index("taxon_key")["tl"] if len(sau) else {}
        )
        sau_name = out["taxon_key"].map(
            sau.set_index("taxon_key")["scientific_name"] if len(sau) else {}
        )
    exact_sau = out["tl"].isna() & sau_tl.notna()
    _set_matches(
        out,
        exact_sau,
        sau_tl,
        "exact_sea_around_us",
        "Sea Around Us exploited organisms",
        "high",
        sau_name,
    )

    genus_source = sup.loc[sup["taxon_key"].str.split().str.len() >= 2].copy()
    genus_source["genus_key"] = genus_source["taxon_key"].str.split().str[0]
    genus_stats = genus_source.groupby("genus_key").agg(
        genus_tl=("tl", "mean"), species_count=("taxon_key", "nunique")
    )
    genus_stats = genus_stats.loc[genus_stats["species_count"] >= min_genus_species]
    catch_genus = out["taxon_key"].str.split().str[0]
    genus_tl = catch_genus.map(genus_stats["genus_tl"])
    genus_match = out["tl"].isna() & genus_tl.notna()
    _set_matches(
        out,
        genus_match,
        genus_tl,
        "genus_mean_2020",
        "2020 supplement genus mean",
        "medium",
        catch_genus,
    )

    base_matched = out.loc[out["tl"].notna()].copy()
    commercial_reference = (
        base_matched.groupby(["commercial_group", "taxon_key"], as_index=False)["tl"]
        .mean()
    )
    functional_reference = (
        base_matched.groupby(["functional_group", "taxon_key"], as_index=False)["tl"]
        .mean()
    )
    commercial_means = commercial_reference.groupby("commercial_group")["tl"].mean()
    functional_means = functional_reference.groupby("functional_group")["tl"].mean()

    if allow_commercial_group_fallback:
        commercial_tl = out["commercial_group"].map(commercial_means)
        commercial_match = out["tl"].isna() & commercial_tl.notna()
        _set_matches(
            out,
            commercial_match,
            commercial_tl,
            "commercial_group_mean",
            "Exact/genus matched-taxa commercial-group mean",
            "low",
            out["commercial_group"],
        )

    if allow_functional_group_fallback:
        functional_tl = out["functional_group"].map(functional_means)
        functional_match = out["tl"].isna() & functional_tl.notna()
        _set_matches(
            out,
            functional_match,
            functional_tl,
            "functional_group_mean",
            "Exact/genus matched-taxa functional-group mean",
            "low",
            out["functional_group"],
        )

    return out
