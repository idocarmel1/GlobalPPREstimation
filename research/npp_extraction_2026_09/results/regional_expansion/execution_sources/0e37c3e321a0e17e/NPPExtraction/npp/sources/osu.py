"""OSU Ocean Productivity monthly NPP: VGPM, Eppley-VGPM, CbPM2 and CAFE.

Grid      2160 x 4320 (1/12 deg), OSU's "2x4" product, row 0 at +90, column 0 at -180
Format    gzipped HDF4, one SDS named ``npp``, float32, mg C m-2 day-1
No-data   -9999.0 (the file calls it the "Hole Value")
Naming    ``<prefix>.<year><day-of-year-of-month-start>.hdf.gz``, e.g. ``vgpm.2019001.hdf.gz``

**Why these four and not the OC-CCI five-model product.** Ryan-Keogh et al. (2023,
doi 10.5194/essd-15-4829-2023) is the better product on paper: five algorithms on one set
of OC-CCI v6 inputs. But it is distributed only as five monolithic 8-day archives of
2.4-4.5 GB each, 20 GB in total, with no monthly version, and the zip members are
deflate-compressed so no HTTP byte range can reach a single year. The four OSU products
here all run on one MODIS R2022 input chain, which preserves the property that makes an
ensemble meaningful -- the spread is algorithm choice, not input processing -- while being
one small file per model per month and 1/12 deg rather than 25 km.

**Coverage gaps that matter.** These are real and will bite anyone using the ensemble on
semi-enclosed seas: VGPM and Eppley-VGPM return nothing at all in the Black Sea, and
CbPM2 returns nothing in the Persian Gulf. ``npp.ensemble`` detects this per region and
records which models contributed. The site also stopped updating in September 2024, which
is irrelevant for years up to 2023 but means it will not follow new reprocessings.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

BASE = "https://orca.science.oregonstate.edu/data/2x4/monthly"
NATIVE_GRID = "12th"
SDS = "npp"
HOLE_VALUE = -9999.0

#: model key -> (filename prefix, directory on the OSU server)
DIRS: dict[str, tuple[str, str]] = {
    "vgpm": ("vgpm", "vgpm.r2022.m.chl.m.sst"),
    "eppley": ("eppley", "eppley.r2022.m.chl.m.sst"),
    "cbpm": ("cbpm", "cbpm2.modis.r2022"),
    "cafe": ("cafe", "cafe.modis.r2022"),
}

MODELS = tuple(DIRS)


def local_name(model: str, year: int, month: int) -> str:
    from ..solar import month_start_doy

    prefix, _ = DIRS[model]
    return f"{prefix}.{year}{month_start_doy(year, month):03d}.hdf.gz"


def url(model: str, year: int, month: int) -> str:
    prefix, directory = DIRS[model]
    return f"{BASE}/{directory}/hdf/{local_name(model, year, month)}"


def local_path(raw_dir: Path, model: str, year: int, month: int) -> Path:
    """Prefers ``raw_dir/osu/``, accepts a flat ``raw_dir/``."""
    name = local_name(model, year, month)
    nested = Path(raw_dir) / "osu" / name
    flat = Path(raw_dir) / name
    if flat.exists() and not nested.exists():
        return flat
    return nested


def fetch(raw_dir: Path, year: int, models=MODELS, timeout: int = 180, retries: int = 4,
          overwrite: bool = False) -> list[Path]:
    from ..http import download

    out = []
    for model in models:
        for month in range(1, 13):
            existing = local_path(raw_dir, model, year, month)
            if existing.exists() and not overwrite:
                out.append(existing)
                continue
            dest = Path(raw_dir) / "osu" / local_name(model, year, month)
            out.append(download(url(model, year, month), dest, timeout, retries, overwrite))
    return out


def read(raw_dir: Path, model: str, year: int, month: int, cache_dir: Path | None = None) -> np.ndarray:
    """Return the monthly NPP field on the native 1/12 deg grid, NaN where there is no data.

    pyhdf cannot read from a file object, so the gzip is expanded once into ``cache_dir``
    (default: alongside the archive) and reused on later calls.
    """
    import gzip
    import shutil
    import tempfile
    import os

    from pyhdf.SD import SD, SDC

    gz = local_path(raw_dir, model, year, month)
    if not gz.exists():
        raise FileNotFoundError(f"osu: missing {gz} (run `npp fetch --source osu`)")
    cache = Path(cache_dir) if cache_dir else gz.parent
    cache.mkdir(parents=True, exist_ok=True)
    plain = cache / gz.name[:-3]  # strip .gz
    if not plain.exists() or plain.stat().st_size == 0:
        with gzip.open(gz, "rb") as fin, plain.open("wb") as fout:
            shutil.copyfileobj(fin, fout)
    # HDF4's native fopen also lacks Unicode support on Windows.
    temporary = None
    native_path = plain
    if os.name == "nt" and not str(plain).isascii():
        temporary = tempfile.TemporaryDirectory(prefix="ppr-npp-hdf-")
        native_path = Path(temporary.name) / "monthly.hdf"
        shutil.copyfile(plain, native_path)
    try:
        handle = SD(str(native_path), SDC.READ)
        try:
            field = handle.select(SDS)
            try:
                arr = field.get().astype("float32")
            finally:
                field.endaccess()
        finally:
            handle.end()
    finally:
        if temporary is not None:
            temporary.cleanup()
    return np.where(arr <= HOLE_VALUE + 1.0, np.nan, arr)
