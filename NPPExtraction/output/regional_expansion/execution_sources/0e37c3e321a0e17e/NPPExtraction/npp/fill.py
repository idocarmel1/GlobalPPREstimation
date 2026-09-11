"""Completing the year: water mask and the gap-fill hierarchy.

A plain sum over the months a satellite happened to see is not an annual total. In the
Arctic it can be a factor of ten low, and even the North Sea loses 11%. This module
decides, for every cell of a region's water mask and every month, where its value comes
from. Stages run in order; each only sees what the previous ones could not supply.

    obs      the target year's own retrieval
    dark     no sunrise anywhere in that month at that latitude -> 0
             A physical zero, not a gap. Filling it would invent impossible production.
    clim     the pixel's own mean for that month over the donor years, optionally
             rescaled by the region-month ratio of target year to climatology measured on
             the pixels where both exist, so the fill carries the target year's anomaly
    nn_near  never retrieved that month in any window year, but a valid cell lies within
             ``nn_split_km``; its value is scaled down by the ratio of top-of-atmosphere
             insolation so light is never borrowed from a brighter latitude
    nn_far   the same rule beyond that distance. In practice this is the interior of the
             pack ice, where a value borrowed from the ice edge is an over-estimate, so it
             is tracked separately and excluded from the central estimate by default.

Every stage is switchable from the config, and the per-category totals are always written
out, so any downstream user can recombine them into whatever definition they prefer.

Peak memory on the 4 km grid is roughly 2.5 GB (a dozen 150 MB rasters plus the distance
transform's index arrays); on 1/12 deg it is about a sixth of that.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .config import Config
from .grids import Grid, get_grid
from .log import log
from .solar import monthly_tables
from .sources import read_model

#: category codes, in the order they are stored on axis -1 of the accumulators
CATEGORIES = ("obs", "dark", "clim", "nn_near", "nn_far")
CAT_INDEX = {c: i for i, c in enumerate(CATEGORIES)}


def build_watermask(cfg: Config, model: str | None = None) -> np.ndarray:
    """Cells that the product ever retrieved, over every window year and month.

    This is the best available proxy for "is there water here that can be productive".
    Cells never seen in the whole window -- the permanent pack ice of the central Arctic --
    stay outside it, which keeps those regions' water areas conservative rather than
    inventing production under multi-year ice.
    """
    path = cfg.watermask_path()
    if path.exists():
        return np.load(path)
    grid = get_grid(cfg.baseline_grid)
    model = model or cfg.ensemble.reference_model
    mask = np.zeros((grid.ny, grid.nx), dtype=bool)
    for year in sorted(cfg.window_years):
        for month in range(1, 13):
            field = read_model(cfg.raw_dir, model, year, month, cache_dir=cfg.work_dir)
            if field.shape != mask.shape:
                raise ValueError(
                    f"watermask: {model} {year}-{month:02d} is {field.shape}, expected "
                    f"{mask.shape}; baseline_grid must match the reference model's native grid"
                )
            mask |= np.isfinite(field)
        log(f"watermask: through {year}, {100*mask.mean():.2f}% of cells wet")
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, mask)
    return mask


@dataclass
class MonthFields:
    """Everything the aggregator needs for one month, flattened to 1-D.

    ``clim`` is deliberately *unscaled*: the anomaly factor is a per-region-per-month
    quantity, so it can only be applied once the region is known.
    """

    month: int
    days: int
    target: np.ndarray       # target-year retrieval, NaN where absent
    clim: np.ndarray         # donor-year mean for this month, NaN where no donor had data
    clim_all: np.ndarray     # mean over all window years incl. target (the "mean year")
    dark: np.ndarray         # bool, no sunrise at that latitude in that month
    nn_value: np.ndarray     # insolation-scaled nearest-neighbour value, NaN where unused
    nn_far: np.ndarray       # bool, that nearest neighbour was beyond nn_split_km


def _nearest_neighbour(grid: Grid, source: np.ndarray, need: np.ndarray, cfg: Config,
                       q_row: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fill ``need`` from the nearest valid cell of ``source``, scaled by insolation.

    The distance transform is run on a longitudinally padded copy so a cell just east of
    the dateline can be served by one just west of it. Distances are converted to km with
    the target latitude's own cosine, which is what the ``nn_split_km`` threshold means.
    """
    from scipy import ndimage

    pad = int(cfg.fill.nn_wrap_pad)
    ny, nx = grid.ny, grid.nx
    value = np.full(ny * nx, np.nan, dtype="float32")
    far = np.zeros(ny * nx, dtype=bool)
    if not need.any():
        return value, far
    ok = np.isfinite(source).reshape(ny, nx)
    ok_padded = np.concatenate([ok[:, -pad:], ok, ok[:, :pad]], axis=1)
    iy, ix = ndimage.distance_transform_edt(~ok_padded, return_distances=False, return_indices=True)
    iy = iy[:, pad:pad + nx]
    ix = ix[:, pad:pad + nx]
    ty, tx = np.nonzero(need.reshape(ny, nx))
    sy = iy[ty, tx]
    sx = (ix[ty, tx] - pad) % nx
    del iy, ix, ok_padded
    borrowed = source.reshape(ny, nx)[sy, sx]
    # never import more light than the target latitude actually receives
    ratio = np.clip(q_row[ty] / np.maximum(q_row[sy], 1e-6), 0.0, 1.0)
    flat = ty * nx + tx
    value[flat] = np.clip(borrowed * ratio, 0.0, cfg.fill.value_max)
    dlat = (ty - sy) * grid.dlat
    dlon = ((sx - tx + nx // 2) % nx - nx // 2) * grid.dlon
    lat_t = 90.0 - (ty + 0.5) * grid.dlat
    dist_km = 111.19 * np.hypot(dlat, dlon * np.cos(np.deg2rad(lat_t)))
    far[flat] = dist_km > cfg.fill.nn_split_km
    return value, far


def prepare_month(cfg: Config, month: int, watermask: np.ndarray,
                  q_toa: np.ndarray, lit_days: np.ndarray) -> MonthFields:
    """Read the target year and its donors for one month and derive every fill input."""
    from .solar import days_in_month

    grid = get_grid(cfg.baseline_grid)
    model = cfg.ensemble.reference_model
    ny, nx = grid.ny, grid.nx

    target = read_model(cfg.raw_dir, model, cfg.year, month, cache_dir=cfg.work_dir)
    ok_target = np.isfinite(target)

    donors = cfg.donor_years()
    acc = np.zeros((ny, nx), dtype="float32")
    cnt = np.zeros((ny, nx), dtype="uint8")
    for year in donors:
        a = read_model(cfg.raw_dir, model, year, month, cache_dir=cfg.work_dir)
        ok = np.isfinite(a)
        acc[ok] += a[ok]
        cnt[ok] += 1
        del a, ok
    clim = np.divide(acc, cnt, out=np.full((ny, nx), np.nan, dtype="float32"), where=cnt > 0)
    denom = cnt + ok_target.astype("uint8")
    clim_all = np.divide(acc + np.where(ok_target, target, 0.0), denom,
                         out=np.full((ny, nx), np.nan, dtype="float32"), where=denom > 0)
    del acc, cnt, denom

    dark_row = lit_days[month - 1] == 0
    dark = np.ascontiguousarray(np.broadcast_to(dark_row[:, None], (ny, nx)))

    if cfg.fill.use_nearest_neighbour:
        source = np.where(ok_target, target, clim).ravel()
        need = (
            watermask.ravel()
            & ~ok_target.ravel()
            & ~(dark.ravel() if cfg.fill.dark_is_zero else np.zeros(ny * nx, bool))
            & ~np.isfinite(clim.ravel() if cfg.fill.use_climatology
                           else np.full(ny * nx, np.nan, "float32"))
        )
        nn_value, nn_far = _nearest_neighbour(grid, source, need, cfg, q_toa[month - 1])
        del source, need
    else:
        nn_value = np.full(ny * nx, np.nan, dtype="float32")
        nn_far = np.zeros(ny * nx, dtype=bool)

    return MonthFields(
        month=month,
        days=days_in_month(cfg.year, month),
        target=target.ravel(),
        clim=clim.ravel(),
        clim_all=clim_all.ravel(),
        dark=dark.ravel(),
        nn_value=nn_value,
        nn_far=nn_far,
    )


def solar_tables(cfg: Config) -> tuple[np.ndarray, np.ndarray]:
    grid = get_grid(cfg.baseline_grid)
    return monthly_tables(cfg.year, grid.ny)
