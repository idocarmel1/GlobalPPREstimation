"""Turn the accumulators into the CSV tables that are the pipeline's actual product."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import MODEL_LABELS, Config
from .fill import CAT_INDEX, CATEGORIES
from .log import log
from .solar import days_in_month

SYSTEM_LABEL = {"lme": "LME", "highseas": "HighSeas", "eez": "EEZ"}


def _sau_reference(cfg: Config, layer: str) -> pd.DataFrame | None:
    path = cfg.sau_reference_path(layer)
    if not path.exists():
        return None
    df = pd.read_csv(path)
    keep = [c for c in ("region_id", "sau_area_km2", "sau_shelf_km2", "sau_ifa_km2",
                        "sau_coral_pct_world", "sau_pp_mgC_m2_d") if c in df.columns]
    return df[keep]


def baseline_table(cfg: Config, baseline_npz: Path) -> pd.DataFrame:
    """One row per region: the gap-filled annual total and the full fill accounting.

    Column definitions
        ``npp_central_tC_yr``      the headline number: the categories the config marks central
        ``npp_observed_tC_yr``     retrievals only -- what a naive sum over observed months gives
        ``npp_all_fills_tC_yr``    every category, including the pack-ice nearest-neighbour fill
        ``npp_no_nn_tC_yr``        observed + polar-night zeros + climatology, no spatial fill
        ``npp_mean_year_tC_yr``    the same integration on the multi-year mean field
        ``area_<cat>_pct``         share of the region's water area that came from each stage
        ``npp_<cat>_pct``          share of its annual carbon that came from each stage
    """
    z = np.load(baseline_npz, allow_pickle=True)
    central = set(cfg.fill.central_categories())
    rows, monthly = [], []
    for layer in cfg.layers:
        C = z[f"{layer}_carbon_g"]
        A = z[f"{layer}_area_m2"]
        MY = z[f"{layer}_mean_year_g"]
        AF = z[f"{layer}_anomaly_factor"]
        rid = z[f"{layer}_region_id"]
        title = z[f"{layer}_title"]
        parea = z[f"{layer}_polygon_area_km2"]
        for i in range(len(rid)):
            tot_all = C[:, i, :].sum()
            water = A[0, i, :].sum()
            by_cat = {c: C[:, i, CAT_INDEX[c]].sum() for c in CATEGORIES}
            tot_central = sum(v for c, v in by_cat.items() if c in central)
            row = {
                "system": SYSTEM_LABEL[layer], "layer": layer, "region_id": int(rid[i]),
                "title": str(title[i]),
                "polygon_area_km2": float(parea[i]),
                "water_area_km2": water / 1e6,
                "npp_central_tC_yr": tot_central / 1e6,
                "npp_observed_tC_yr": by_cat["obs"] / 1e6,
                "npp_no_nn_tC_yr": (by_cat["obs"] + by_cat["dark"] + by_cat["clim"]) / 1e6,
                "npp_all_fills_tC_yr": tot_all / 1e6,
                "npp_mean_year_tC_yr": MY[:, i].sum() / 1e6,
                "fill_uplift_pct": (100 * (tot_central / by_cat["obs"] - 1)) if by_cat["obs"] else np.nan,
                "mean_rate_mgC_m2_d": (tot_central / water / 365 * 1000) if water else np.nan,
            }
            for c in CATEGORIES:
                denom_a = A[:, i, :].sum()
                row[f"area_{c}_pct"] = 100 * A[:, i, CAT_INDEX[c]].sum() / denom_a if denom_a else np.nan
                row[f"npp_{c}_pct"] = 100 * by_cat[c] / tot_all if tot_all else np.nan
            row["anomaly_factor_min"] = float(AF[:, i].min())
            row["anomaly_factor_max"] = float(AF[:, i].max())
            rows.append(row)
            for m in range(12):
                am = A[m, i, :].sum()
                dd = days_in_month(cfg.year, m + 1)
                cm = sum(C[m, i, CAT_INDEX[c]] for c in central)
                rec = {"system": SYSTEM_LABEL[layer], "layer": layer, "region_id": int(rid[i]),
                       "title": str(title[i]), "month": m + 1, "days": dd,
                       "npp_central_tC": cm / 1e6, "npp_observed_tC": C[m, i, CAT_INDEX["obs"]] / 1e6,
                       "rate_central_gC_m2_d": (cm / am / dd) if am else np.nan,
                       "anomaly_factor": float(AF[m, i])}
                for c in CATEGORIES:
                    rec[f"area_{c}_pct"] = 100 * A[m, i, CAT_INDEX[c]] / am if am else np.nan
                monthly.append(rec)
    df = pd.DataFrame(rows)
    mdf = pd.DataFrame(monthly)
    parts = []
    for layer in cfg.layers:
        sub = df[df.layer == layer]
        ref = _sau_reference(cfg, layer)
        if ref is not None:
            sub = sub.merge(ref, on="region_id", how="left")
        parts.append(sub)
    df = pd.concat(parts, ignore_index=True)
    if "sau_pp_mgC_m2_d" in df.columns:
        df["ratio_vs_sau"] = df.mean_rate_mgC_m2_d / df.sau_pp_mgC_m2_d
    df = df.sort_values(["layer", "region_id"]).reset_index(drop=True)
    out = Path(cfg.out_dir) / f"npp_{cfg.year}_baseline_by_region.csv"
    mout = Path(cfg.out_dir) / f"npp_{cfg.year}_baseline_monthly.csv"
    Path(cfg.out_dir).mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    mdf.to_csv(mout, index=False)
    log(f"report: {out} ({len(df)} regions)  {mout} ({len(mdf)} rows)")
    return df


def ensemble_table(cfg: Config, df: pd.DataFrame) -> Path:
    df = df.sort_values(["layer", "region_id"]).reset_index(drop=True)
    df.insert(0, "system", df.layer.map(SYSTEM_LABEL))
    out = Path(cfg.out_dir) / f"npp_{cfg.year}_ensemble_by_region.csv"
    df.to_csv(out, index=False)
    log(f"report: {out} ({len(df)} regions)")
    return out


def summarise(cfg: Config, base: pd.DataFrame, ens: pd.DataFrame) -> str:
    """A short human-readable summary, also written next to the CSVs."""
    models = list(cfg.ensemble.models)
    lines = [f"NPP {cfg.year} -- summary", "=" * 46, ""]
    lines.append(f"fill stages in the central estimate: {', '.join(cfg.fill.central_categories())}")
    lines.append(f"climatology donor years: {cfg.donor_years() or 'none'}")
    lines.append("")
    lines.append("baseline (reference model, gap-filled), Pg C/yr")
    for layer in cfg.layers:
        s = base[base.layer == layer]
        lines.append(
            f"  {SYSTEM_LABEL[layer]:9s} n={len(s):4d}  water {s.water_area_km2.sum()/1e6:7.2f} M km2"
            f"  observed {s.npp_observed_tC_yr.sum()/1e9:6.2f}  central {s.npp_central_tC_yr.sum()/1e9:6.2f}"
            f"  all fills {s.npp_all_fills_tC_yr.sum()/1e9:6.2f}")
    lines.append("")
    lines.append("ensemble scaled onto that baseline, Pg C/yr")
    header = "  " + " " * 10 + "".join(f"{MODEL_LABELS[m]:>15s}" for m in models)
    lines.append(header)
    for layer in cfg.layers:
        s = ens[ens.layer == layer]
        lines.append("  " + f"{SYSTEM_LABEL[layer]:10s}" +
                     "".join(f"{s[f'scaled_{m}_tC_yr'].sum()/1e9:15.2f}" for m in models))
    lines.append("")
    lines.append("per-region algorithm spread (max-min as % of median)")
    for layer in cfg.layers:
        s = ens[ens.layer == layer]
        lines.append(f"  {SYSTEM_LABEL[layer]:9s} median {s.spread_pct.median():5.1f}%  "
                     f"IQR {s.spread_pct.quantile(.25):5.1f}-{s.spread_pct.quantile(.75):5.1f}%")
    odd = ens[ens.n_models < len(models)]
    if len(odd):
        lines.append("")
        lines.append(f"regions where not every model has data ({len(odd)}):")
        for _, r in odd.iterrows():
            lines.append(f"  {SYSTEM_LABEL[r.layer]:9s} {r.region_id:5d} {r.title[:34]:34s} "
                         f"{r.n_models} models, basis '{r.ensemble_basis}'")
    text = "\n".join(lines)
    (Path(cfg.out_dir) / f"summary_{cfg.year}.txt").write_text(text + "\n")
    return text
