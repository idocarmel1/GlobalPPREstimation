"""Data sources. Each exposes ``NATIVE_GRID``, ``local_path``, ``fetch`` and ``read``."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from . import copernicus, osu

#: model key -> module providing it
PROVIDER = {"antoinemorel": copernicus, **{m: osu for m in osu.MODELS}}


def native_grid(model: str) -> str:
    return PROVIDER[model].NATIVE_GRID


def read_model(raw_dir: Path, model: str, year: int, month: int,
               cache_dir: Path | None = None) -> np.ndarray:
    """Read one model-month on that model's native grid, NaN where there is no data."""
    if model == "antoinemorel":
        return copernicus.read(raw_dir, year, month)
    return osu.read(raw_dir, model, year, month, cache_dir=cache_dir)


def fetch_model_year(raw_dir: Path, model: str, year: int, **kw) -> list[Path]:
    if model == "antoinemorel":
        return copernicus.fetch(raw_dir, year, **kw)
    return osu.fetch(raw_dir, year, models=[model], **kw)
