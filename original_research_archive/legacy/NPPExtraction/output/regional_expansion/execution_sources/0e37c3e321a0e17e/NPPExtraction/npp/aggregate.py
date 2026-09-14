"""Zonal integration: turn filled monthly rasters into per-region annual totals.

    NPP_annual,region = SUM over months SUM over pixels
                        PP[mg C m-2 d-1] * days_in_month * pixel_area[m2] * pixel_fraction

Three details that are easy to get wrong and that change the answer materially:

* **Weight each month by its own length.** Monthly fields are daily *rates*. Averaging the
  twelve rates and multiplying by 365 biases the year by however much production
  correlates with month length.
* **Use the real cell area.** It varies by a factor of ~25 between the equator and 80
  degrees on a plate-carree grid.
* **Use fractional pixel coverage**, not centroid-in-polygon. Along a coastline the error
  is about half a cell, and coastlines are where the production is.

Results are accumulated per (month, region, fill-category) so the caller can define the
central estimate however it likes without re-running anything.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .config import Config
from .fill import CAT_INDEX, CATEGORIES, MonthFields, build_watermask, prepare_month, solar_tables
from .grids import get_grid
from .log import log
from .regions import Coverage

MG_TO_G = 1e-3


class LayerAccumulator:
    """Per-region accumulators for one region layer."""

    def __init__(self, cov: Coverage):
        self.cov = cov
        n = cov.n
        self.carbon_g = np.zeros((12, n, len(CATEGORIES)))
        self.area_m2 = np.zeros((12, n, len(CATEGORIES)))
        self.carbon_mean_year_g = np.zeros((12, n))
        self.anomaly_factor = np.ones((12, n))
        self.wet: np.ndarray | None = None

    def bind_watermask(self, watermask_flat: np.ndarray) -> None:
        self.wet = watermask_flat[self.cov.cid]

    def add_month(self, mf: MonthFields, cfg: Config) -> None:
        cov, w, ridx, n = self.cov, self.cov.weight, self.cov.ridx, self.cov.n
        cid = cov.cid
        wet = self.wet
        v = mf.target[cid]
        cl = mf.clim[cid]
        nn = mf.nn_value[cid]
        far = mf.nn_far[cid]
        dark = mf.dark[cid] if cfg.fill.dark_is_zero else np.zeros(len(cid), bool)

        is_obs = np.isfinite(v) & wet
        is_dark = wet & ~is_obs & dark
        has_clim = np.isfinite(cl) if cfg.fill.use_climatology else np.zeros(len(cid), bool)
        is_clim = wet & ~is_obs & ~is_dark & has_clim
        rest = wet & ~is_obs & ~is_dark & ~is_clim
        if cfg.fill.use_nearest_neighbour:
            is_nn_near = rest & ~far
            is_nn_far = rest & far
        else:
            is_nn_near = np.zeros(len(cid), bool)
            is_nn_far = np.zeros(len(cid), bool)

        # region-month anomaly factor, measured only where target and climatology coexist
        factor = np.ones(n)
        if cfg.fill.use_climatology and cfg.fill.anomaly_rescale:
            both = is_obs & np.isfinite(cl)
            num = np.bincount(ridx, weights=np.where(both, w * v, 0.0), minlength=n)
            den = np.bincount(ridx, weights=np.where(both, w * cl, 0.0), minlength=n)
            factor = np.divide(num, den, out=np.ones(n), where=den > 0)
            factor = np.clip(factor, *cfg.fill.anomaly_clip)
        self.anomaly_factor[mf.month - 1] = factor

        value = np.zeros(len(cid))
        value[is_obs] = v[is_obs]
        if is_clim.any():
            value[is_clim] = np.clip(cl[is_clim] * factor[ridx[is_clim]], 0.0, cfg.fill.value_max)
        for m in (is_nn_near, is_nn_far):
            if m.any():
                value[m] = np.nan_to_num(nn[m])

        del v, cl
        value *= mf.days
        value *= w
        value *= MG_TO_G
        grams = value
        for cat, mask in (("obs", is_obs), ("dark", is_dark), ("clim", is_clim),
                          ("nn_near", is_nn_near), ("nn_far", is_nn_far)):
            k = CAT_INDEX[cat]
            self.carbon_g[mf.month - 1, :, k] = np.bincount(
                ridx, weights=np.where(mask, grams, 0.0), minlength=n)
            self.area_m2[mf.month - 1, :, k] = np.bincount(
                ridx, weights=np.where(mask, w, 0.0), minlength=n)

        # the multi-year mean year, same fill logic but climatology first
        cl_all = mf.clim_all[cid]
        mean_v = np.where(np.isfinite(cl_all), cl_all,
                          np.where(is_dark, 0.0, np.nan_to_num(nn)))
        self.carbon_mean_year_g[mf.month - 1] = np.bincount(
            ridx, weights=np.where(wet, np.nan_to_num(mean_v) * mf.days * w * MG_TO_G, 0.0),
            minlength=n)


def run_baseline(cfg: Config) -> Path:
    """Fill the target year on the baseline grid and integrate over every region layer."""
    cfg.ensure_dirs()
    grid = get_grid(cfg.baseline_grid)
    watermask = build_watermask(cfg)
    q_toa, lit_days = solar_tables(cfg)
    wm_flat = watermask.ravel()

    accs: dict[str, LayerAccumulator] = {}
    for layer in cfg.layers:
        path = cfg.coverage_path(layer, cfg.baseline_grid)
        if not path.exists():
            raise FileNotFoundError(f"missing {path}; run `npp regions` first")
        acc = LayerAccumulator(Coverage(path, grid))
        acc.bind_watermask(wm_flat)
        accs[layer] = acc

    for month in range(1, 13):
        mf = prepare_month(cfg, month, watermask, q_toa, lit_days)
        for layer, acc in accs.items():
            acc.add_month(mf, cfg)
        obs_pct = 100 * np.isfinite(mf.target).mean()
        nn_pct = 100 * np.isfinite(mf.nn_value).mean()
        log(f"baseline {cfg.year}-{month:02d}: observed {obs_pct:5.2f}% of grid, "
            f"nearest-neighbour fill {nn_pct:5.2f}%")
        del mf

    out = Path(cfg.work_dir) / f"baseline_{cfg.year}_{cfg.baseline_grid}.npz"
    payload = {}
    for layer, acc in accs.items():
        payload[f"{layer}_carbon_g"] = acc.carbon_g
        payload[f"{layer}_area_m2"] = acc.area_m2
        payload[f"{layer}_mean_year_g"] = acc.carbon_mean_year_g
        payload[f"{layer}_anomaly_factor"] = acc.anomaly_factor
        payload[f"{layer}_region_id"] = acc.cov.region_id
        payload[f"{layer}_title"] = np.array(acc.cov.title, dtype=object)
        payload[f"{layer}_polygon_area_km2"] = acc.cov.polygon_area_km2()
    np.savez(out, **payload, allow_pickle=True)
    log(f"baseline: -> {out}")
    return out
