"""Copernicus-GlobColour monthly primary production (the Antoine-Morel product).

Product   OCEANCOLOUR_GLO_BGC_L4_MY_009_104
Dataset   cmems_obs-oc_glo_bgc-pp_my_l4-multi-4km_P1M
Algorithm Antoine & Morel, depth- and wavelength-resolved, chlorophyll-based
Grid      4320 x 8640 (1/24 deg), row 0 at +90, column 0 at -180
Variable  ``PP``, mg C m-2 day-1, NaN outside the retrieval
Coverage  1997 to present, monthly

The native monthly NetCDF files sit on public object storage and need **no Copernicus
account** -- the S3 bucket is anonymously readable and supports plain HTTPS GET. That is
much simpler than the authenticated Toolbox/subsetter path, and it is what this module
uses. The bucket and dataset version are discovered from the STAC catalogue so a dataset
reprocessing does not silently break the URLs; ``NATIVE_ROOT_FALLBACK`` is only used if
STAC is unreachable.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

STAC_ROOT = "https://stac.marine.copernicus.eu/metadata"
PRODUCT_ID = "OCEANCOLOUR_GLO_BGC_L4_MY_009_104"
DATASET_PREFIX = "cmems_obs-oc_glo_bgc-pp_my_l4-multi-4km_P1M"
#: Verified working 2026-09; only used when the STAC catalogue cannot be reached.
NATIVE_ROOT_FALLBACK = (
    "https://s3.waw3-1.cloudferro.com/mdl-native-16/native/"
    f"{PRODUCT_ID}/{DATASET_PREFIX}_202603"
)
NATIVE_GRID = "4km"
VARIABLE = "PP"


def _stac_native_root(timeout: int, retries: int) -> str:
    from ..http import get_json
    from ..log import log

    try:
        product = get_json(f"{STAC_ROOT}/{PRODUCT_ID}/product.stac.json", timeout, retries)
        link = next(l for l in product.get("links", []) if DATASET_PREFIX in (l.get("href") or ""))
        ds = get_json(f"{STAC_ROOT}/{PRODUCT_ID}/{link['href']}", timeout, retries)
        root = ds["assets"]["native"]["href"].split("?")[0].rstrip("/")
        log(f"copernicus: native root from STAC -> {root}")
        return root
    except Exception as exc:  # noqa: BLE001 - any failure means fall back
        log(f"copernicus: STAC lookup failed ({exc}); using pinned fallback root")
        return NATIVE_ROOT_FALLBACK


def list_year(year: int, timeout: int = 180, retries: int = 4) -> dict[int, str]:
    """Map month -> download URL for one year, by listing the S3 prefix."""
    from ..http import get_text

    root = _stac_native_root(timeout, retries)
    bucket, _, key_root = root.partition("/native/")
    prefix = f"native/{key_root}/{year}/"
    xml = get_text(
        f"{bucket}?list-type=2&max-keys=200&prefix={prefix.replace('/', '%2F')}", timeout, retries
    )
    urls: dict[int, str] = {}
    for key in re.findall(r"<Key>([^<]+)</Key>", xml):
        name = key.rsplit("/", 1)[-1]
        m = re.match(rf"({year})(\d{{2}})\d{{2}}-\d{{8}}_{re.escape(DATASET_PREFIX)}\.nc$", name)
        if m:
            urls[int(m.group(2))] = f"{bucket}/{key}"
    if len(urls) != 12:
        from ..log import log

        log(f"copernicus: WARNING only {len(urls)}/12 months found for {year}")
    return urls


def local_name(year: int, month: int) -> str:
    """Canonical native filename, e.g. ``20190101-20190131_cmems_...P1M.nc``."""
    import calendar

    last = calendar.monthrange(year, month)[1]
    return f"{year}{month:02d}01-{year}{month:02d}{last:02d}_{DATASET_PREFIX}.nc"


def local_path(raw_dir: Path, year: int, month: int) -> Path:
    """Where the file lives. Prefers ``raw_dir/copernicus/``, accepts a flat ``raw_dir/``."""
    name = local_name(year, month)
    nested = Path(raw_dir) / "copernicus" / name
    flat = Path(raw_dir) / name
    if flat.exists() and not nested.exists():
        return flat
    return nested


def fetch(raw_dir: Path, year: int, timeout: int = 180, retries: int = 4, overwrite: bool = False) -> list[Path]:
    """Download the twelve monthly files for ``year`` (skipping any already present)."""
    from ..http import download
    from ..log import log

    missing = [m for m in range(1, 13) if not local_path(raw_dir, year, m).exists()]
    if not missing and not overwrite:
        log(f"copernicus: {year} already complete in {raw_dir}")
        return [local_path(raw_dir, year, m) for m in range(1, 13)]
    urls = list_year(year, timeout, retries)
    out = []
    for month in range(1, 13):
        dest = Path(raw_dir) / "copernicus" / local_name(year, month)
        existing = local_path(raw_dir, year, month)
        if existing.exists() and not overwrite:
            out.append(existing)
            continue
        if month not in urls:
            raise FileNotFoundError(f"copernicus: no file listed for {year}-{month:02d}")
        out.append(download(urls[month], dest, timeout, retries, overwrite))
    return out


def read(raw_dir: Path, year: int, month: int) -> np.ndarray:
    """Return the monthly PP field on the native 4 km grid, NaN where there is no data."""
    from netCDF4 import Dataset

    path = local_path(raw_dir, year, month)
    if not path.exists():
        raise FileNotFoundError(f"copernicus: missing {path} (run `npp fetch --source copernicus`)")
    # A year is read repeatedly by overlapping five-year fill windows. Keep an
    # exact decoded float32 array outside raw_dir, and map it without another copy.
    import hashlib
    stamp = f"{path.resolve()}:{path.stat().st_size}:{path.stat().st_mtime_ns}:float32-v1"
    cache = Path(raw_dir).parent / "decoded" / "copernicus"
    cache.mkdir(parents=True, exist_ok=True)
    decoded = cache / (path.stem + "_" + hashlib.sha256(stamp.encode()).hexdigest()[:16] + ".npy")
    if decoded.exists():
        try:
            return np.load(decoded, mmap_mode="r")
        except (OSError, ValueError):
            decoded.unlink()
    # Windows netCDF-C cannot open Unicode paths on some wheel builds. Python can
    # open the same file, so the supported in-memory API avoids lossy path encoding.
    import os
    kwargs = {"memory": path.read_bytes()} if os.name == "nt" and not str(path).isascii() else {}
    with Dataset("inmemory.nc" if kwargs else str(path), "r", **kwargs) as ds:
        data = ds.variables[VARIABLE][0].astype("float32")
        array = np.ma.filled(data, np.nan)
    part = decoded.with_suffix(".npy.part")
    with part.open("wb") as fh:
        np.save(fh, array)
    part.replace(decoded)
    return np.load(decoded, mmap_mode="r")
