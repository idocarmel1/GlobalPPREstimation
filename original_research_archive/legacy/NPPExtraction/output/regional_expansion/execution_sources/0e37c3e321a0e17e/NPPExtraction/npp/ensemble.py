"""The five-algorithm ensemble: how much of the answer is the ocean and how much the model.

All models are integrated over the **same pixels of the same grid** -- those where every
model has a retrieval in that month (the "common mask"). Without that, a model that masks
cloud more aggressively looks less productive for a reason that has nothing to do with its
photosynthesis parameterisation.

The common-mask totals are the clean comparison but they exclude the gaps the baseline
took trouble to fill. So the ensemble's actual contribution is a set of **ratios**: each
model's common-mask total relative to the reference model's, applied to the reference
model's gap-filled total for that region. The result is five absolute estimates at the
resolution and completeness of the best product.

Where the common mask is empty or negligible the ratios fall back to own-coverage totals
over whichever models cover the region at all, and ``ensemble_basis`` records that. This
is not a corner case to ignore: VGPM and Eppley-VGPM return nothing in the Black Sea and
CbPM2 returns nothing in the Persian Gulf, so 19 of 366 regions land here.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .config import MODEL_LABELS, Config
from .grids import get_grid, to_grid
from .log import log
from .regions import Coverage
from .sources import native_grid, read_model
from .solar import days_in_month

MG_TO_G = 1e-3


def run_ensemble(cfg: Config) -> Path:
    """Accumulate common-mask and own-coverage totals for every model and region."""
    cfg.ensure_dirs()
    grid = get_grid(cfg.ensemble.grid)
    models = list(cfg.ensemble.models)

    accs = {}
    for layer in cfg.layers:
        path = cfg.coverage_path(layer, cfg.ensemble.grid)
        if not path.exists():
            raise FileNotFoundError(f"missing {path}; run `npp regions` first")
        cov = Coverage(path, grid)
        accs[layer] = {
            "cov": cov,
            "common": {m: np.zeros((12, cov.n)) for m in models},
            "own": {m: np.zeros((12, cov.n)) for m in models},
            "common_area": np.zeros((12, cov.n)),
            "own_area": {m: np.zeros((12, cov.n)) for m in models},
        }

    globals_common = {m: 0.0 for m in models}
    globals_own = {m: 0.0 for m in models}
    area_row_rep = np.repeat(grid.area_row(), grid.nx)

    for month in range(1, 13):
        days = days_in_month(cfg.year, month)
        fields = {}
        for m in models:
            raw = read_model(cfg.raw_dir, m, cfg.year, month, cache_dir=cfg.work_dir)
            fields[m] = to_grid(raw, get_grid(native_grid(m)), grid).ravel()
            del raw
        common = np.ones(grid.size, dtype=bool)
        for m in models:
            common &= np.isfinite(fields[m])
        for m in models:
            f = fields[m]
            globals_common[m] += float(np.nansum(np.where(common, f, 0.0) * area_row_rep) * days * MG_TO_G)
            ok = np.isfinite(f)
            globals_own[m] += float(np.nansum(np.where(ok, f, 0.0) * area_row_rep) * days * MG_TO_G)
        for layer, a in accs.items():
            cov = a["cov"]
            cid, w, ridx, n = cov.cid, cov.weight, cov.ridx, cov.n
            c = common[cid]
            a["common_area"][month - 1] = np.bincount(ridx, weights=np.where(c, w, 0.0), minlength=n)
            for m in models:
                v = fields[m][cid]
                a["common"][m][month - 1] = np.bincount(
                    ridx, weights=np.where(c, np.nan_to_num(v), 0.0) * days * w * MG_TO_G, minlength=n)
                ok = np.isfinite(v)
                a["own"][m][month - 1] = np.bincount(
                    ridx, weights=np.where(ok, np.nan_to_num(v), 0.0) * days * w * MG_TO_G, minlength=n)
                a["own_area"][m][month - 1] = np.bincount(
                    ridx, weights=np.where(ok, w, 0.0), minlength=n)
        log(f"ensemble {cfg.year}-{month:02d}: common mask {100*common.mean():.2f}% of grid")
        del fields, common

    out = Path(cfg.work_dir) / f"ensemble_{cfg.year}_{cfg.ensemble.grid}.npz"
    payload = {}
    for layer, a in accs.items():
        for m in a["common"]:
            payload[f"{layer}_common_{m}"] = a["common"][m]
            payload[f"{layer}_own_{m}"] = a["own"][m]
            payload[f"{layer}_own_area_{m}"] = a["own_area"][m]
        payload[f"{layer}_common_area"] = a["common_area"]
        payload[f"{layer}_region_id"] = a["cov"].region_id
        payload[f"{layer}_title"] = np.array(a["cov"].title, dtype=object)
    np.savez(out, **payload, allow_pickle=True)
    log("ensemble: global totals, Pg C/yr (common mask | own coverage)")
    for m in models:
        log(f"  {MODEL_LABELS[m]:>14s}  {globals_common[m]/1e15:6.2f} | {globals_own[m]/1e15:6.2f}")
    np.savez(Path(cfg.work_dir) / f"ensemble_global_{cfg.year}.npz",
             models=np.array(models, dtype=object),
             common=np.array([globals_common[m] for m in models]),
             own=np.array([globals_own[m] for m in models]), allow_pickle=True)
    return out


def scale_to_baseline(cfg: Config, baseline_table, ensemble_npz: Path):
    """Turn common-mask totals into five absolute per-region estimates.

    ``baseline_table`` is the DataFrame from :func:`npp.report.baseline_table`; it supplies
    the gap-filled central total and the water area each ratio is applied to.
    """
    import pandas as pd

    z = np.load(ensemble_npz, allow_pickle=True)
    models = list(cfg.ensemble.models)
    ref = cfg.ensemble.reference_model
    base_central = dict(zip(zip(baseline_table.layer, baseline_table.region_id),
                            baseline_table.npp_central_tC_yr))
    base_water = dict(zip(zip(baseline_table.layer, baseline_table.region_id),
                          baseline_table.water_area_km2))
    rows = []
    for layer in cfg.layers:
        rid = z[f"{layer}_region_id"]
        title = z[f"{layer}_title"]
        carea = z[f"{layer}_common_area"]
        for i in range(len(rid)):
            key = (layer, int(rid[i]))
            common = {m: z[f"{layer}_common_{m}"][:, i].sum() / 1e6 for m in models}
            own = {m: z[f"{layer}_own_{m}"][:, i].sum() / 1e6 for m in models}
            water = base_water.get(key, np.nan)
            central = base_central.get(key, np.nan)
            common_area_km2 = carea[:, i].max() / 1e6
            common_pct = (100 * common_area_km2 / water) if water and np.isfinite(water) and water > 0 else np.nan

            if common[ref] > 0 and np.isfinite(common_pct) and common_pct >= cfg.ensemble.min_common_mask_pct:
                basis, denom, pool = "common mask", common[ref], common
            elif own[ref] > 0:
                basis, denom, pool = "own coverage", own[ref], own
            else:
                basis, denom, pool = "baseline only", 1.0, {ref: 1.0}

            scaled = {}
            for m in models:
                if basis == "baseline only":
                    scaled[m] = central if m == ref else np.nan
                else:
                    scaled[m] = central * pool[m] / denom if pool.get(m, 0.0) > 0 else np.nan
            vals = np.array([scaled[m] for m in models], dtype=float)
            fin = vals[np.isfinite(vals)]
            row = {
                "layer": layer, "region_id": int(rid[i]), "title": str(title[i]),
                "water_area_km2": water, "common_area_km2": common_area_km2,
                "common_area_pct_of_water": common_pct,
                "ensemble_basis": basis, "n_models": int(len(fin)),
                "baseline_central_tC_yr": central,
            }
            for m in models:
                row[f"common_{m}_tC_yr"] = common[m]
                row[f"own_{m}_tC_yr"] = own[m]
                row[f"scaled_{m}_tC_yr"] = scaled[m]
            row["scaled_median_tC_yr"] = float(np.median(fin)) if len(fin) else np.nan
            row["scaled_min_tC_yr"] = float(fin.min()) if len(fin) else np.nan
            row["scaled_max_tC_yr"] = float(fin.max()) if len(fin) else np.nan
            row["scaled_mean_tC_yr"] = float(fin.mean()) if len(fin) else np.nan
            med = np.median(fin) if len(fin) else np.nan
            row["spread_pct"] = float(100 * (fin.max() - fin.min()) / med) if len(fin) > 1 and med > 0 else np.nan
            row["cv_pct"] = float(100 * fin.std(ddof=1) / fin.mean()) if len(fin) > 1 and fin.mean() > 0 else np.nan
            row["model_max"] = MODEL_LABELS[models[int(np.nanargmax(vals))]] if len(fin) else ""
            row["model_min"] = MODEL_LABELS[models[int(np.nanargmin(vals))]] if len(fin) else ""
            for m in models:
                row[f"rate_{m}_mgC_m2_d"] = (
                    scaled[m] * 1e6 / (water * 1e6) / 365 * 1000
                    if np.isfinite(scaled[m]) and water else np.nan)
            rows.append(row)
    return pd.DataFrame(rows)
