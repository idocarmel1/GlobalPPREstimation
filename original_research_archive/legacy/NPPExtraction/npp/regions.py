"""Sea Around Us region polygons: download, repair, and rasterise to fractional coverage.

Two things about these polygons will silently corrupt results if ignored.

**Antimeridian.** The LME GeoJSON contains longitudes down to -188.6 degrees, i.e. parts
have been unwrapped westward past the dateline instead of split at it. Clipping naively
to [-180, 180] silently deletes those parts and three Bering-sector LMEs lose a chunk of
their area. Every geometry is therefore translated by 0 and +/-360 degrees, each copy
clipped to the world box, and the union taken.

**Topology.** 43 of 66 LME and 4 of 18 high-seas features fail ``is_valid`` as delivered,
and exactextract rejects mixed-type geometry collections. Each feature is passed through
``make_valid`` and then reduced to a MultiPolygon of its positive-area polygonal parts.

Coverage is computed with exactextract, which gives the exact fraction of each grid cell
that falls inside the polygon. Centroid-in-polygon assignment would be wrong by roughly
half a cell all along every coastline, which is exactly where the production is.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely import make_valid
from shapely.affinity import translate
from shapely.geometry import MultiPolygon, box
from shapely.ops import unary_union

from .grids import Grid
from .http import get_json
from .log import log

SAU_API = "https://api.seaaroundus.org/api/v1"
WORLD = box(-180.0, -90.0, 180.0, 90.0)


# ---------------------------------------------------------------------- download
def download_geojson(layer: str, dest: Path, timeout: int = 180, retries: int = 4) -> Path:
    """Fetch one layer's FeatureCollection from the Sea Around Us API.

    The API wraps the collection in ``{"meta": ..., "data": <FeatureCollection>}``.
    Sizes as of 2026-09: lme 1.4 MB / 66 features, highseas 151 kB / 18, eez 2.5 MB / 282.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = get_json(f"{SAU_API}/{layer}/", timeout=timeout, retries=retries)
    fc = payload["data"]
    n = len(fc["features"])
    dest.write_text(json.dumps(fc))
    log(f"regions: {layer} -> {dest} ({n} features, {dest.stat().st_size/1e6:.2f} MB)")
    return dest


def download_sau_reference(layer: str, dest: Path, timeout: int = 180, retries: int = 4) -> Path:
    """Fetch each region's published metrics, including their own NPP value.

    Note the endpoint has NO trailing slash: ``/api/v1/lme/1`` returns the region record,
    while ``/api/v1/lme/1/`` returns only API metadata. There is no bulk endpoint, so this
    is one request per region (282 for EEZs, a couple of minutes).

    The published NPP is a 1998-2007 SeaWiFS climatology at 9 km, so it is a sanity check
    on our numbers, not ground truth. Their published *areas* are also inconsistent with
    their own polygons for several revised Arctic LMEs -- prefer areas measured from the
    polygons.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    fc = get_json(f"{SAU_API}/{layer}/", timeout=timeout, retries=retries)["data"]
    ids = [(f["properties"]["region_id"], f["properties"].get("title") or "") for f in fc["features"]]
    area_keys = ("LME area", "HighSeas area", "EEZ area", "Area", "Total area")
    rows = []
    for rid, title in ids:
        rec = get_json(f"{SAU_API}/{layer}/{rid}", timeout=timeout, retries=retries).get("data") or {}
        metrics = {}
        for m in rec.get("metrics") or []:
            key = str(m.get("title", "")).replace("<sup>", "").replace("</sup>", "")
            metrics[key] = m.get("value")
        area = next((metrics[k] for k in area_keys if k in metrics), None)
        rows.append(
            {
                "region_id": rid,
                "title": rec.get("title") or title,
                "sau_area_km2": area,
                "sau_shelf_km2": metrics.get("Shelf Area"),
                "sau_ifa_km2": metrics.get("Inshore Fishing Area (IFA)"),
                "sau_coral_pct_world": metrics.get("Tropical Coral Reefs"),
                "sau_pp_mgC_m2_d": metrics.get("Primary production"),
            }
        )
    with dest.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    log(f"regions: {layer} SAU reference metrics -> {dest} ({len(rows)} regions)")
    return dest


# ---------------------------------------------------------------------- geometry repair
def clean_geometry(geom):
    """Repair topology and unwrap the antimeridian. Returns a MultiPolygon or None."""
    if geom is None:
        return None
    g = make_valid(geom)
    parts = []
    for offset in (0.0, 360.0, -360.0):
        shifted = translate(g, xoff=offset) if offset else g
        b = shifted.bounds
        if b[0] > 180.0 or b[2] < -180.0:
            continue
        inter = shifted.intersection(WORLD)
        if not inter.is_empty and inter.area > 0:
            parts.append(inter)
    if not parts:
        return None
    merged = make_valid(unary_union(parts))
    polys: list = []

    def collect(x):
        if x is None or x.is_empty:
            return
        if x.geom_type == "Polygon":
            polys.append(x)
        elif x.geom_type in ("MultiPolygon", "GeometryCollection"):
            for sub in x.geoms:
                collect(sub)

    collect(merged)
    polys = [p for p in polys if p.area > 0]
    return MultiPolygon(polys) if polys else None


def load_layer(geojson: Path) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(geojson)
    gdf["geometry"] = [clean_geometry(g) for g in gdf.geometry]
    gdf = gdf[gdf.geometry.notna()].reset_index(drop=True)
    if "region_id" not in gdf.columns:
        raise ValueError(f"{geojson} has no region_id property")
    if "title" not in gdf.columns:
        gdf["title"] = gdf.region_id.astype(str)
    return gdf


# ---------------------------------------------------------------------- rasterise
def build_coverage(geojson: Path, grid: Grid, dest: Path, max_cells_in_memory: int = 60_000_000) -> Path:
    """Write exact fractional coverage for one layer on one grid.

    Output ``.npz`` is a sparse triple:
        ``cid``   int32   flat cell index (row * nx + col)
        ``cov``   float32 fraction of that cell inside the region, 0 < cov <= 1
        ``ridx``  int16   index into ``region_id`` / ``title``
    Regions within a layer are stored independently, so overlaps between regions of the
    same layer (rare, but present in the EEZ layer) are preserved rather than collapsed.
    """
    from exactextract import exact_extract
    from exactextract.raster import NumPyRasterSource

    gdf = load_layer(geojson)
    dummy = np.zeros((grid.ny, grid.nx), dtype="float32")
    src = NumPyRasterSource(
        dummy, xmin=-180.0, ymin=-90.0, xmax=180.0, ymax=90.0, srs_wkt="EPSG:4326"
    )
    res = exact_extract(
        src, gdf, ["cell_id", "coverage"], output="pandas",
        max_cells_in_memory=max_cells_in_memory,
    )
    cids, covs, ridx = [], [], []
    for i, row in res.iterrows():
        cid = np.asarray(row["cell_id"], dtype="int64")
        cov = np.asarray(row["coverage"], dtype="float64")
        keep = cov > 1e-6
        cid, cov = cid[keep], cov[keep]
        # a MultiPolygon can report the same cell once per part; merge those
        order = np.argsort(cid, kind="stable")
        cid, cov = cid[order], cov[order]
        uniq, starts = np.unique(cid, return_index=True)
        if len(uniq) != len(cid):
            cov = np.add.reduceat(cov, starts)
            cid = uniq
        cids.append(cid.astype("int32"))
        covs.append(np.clip(cov, 0.0, 1.0).astype("float32"))
        ridx.append(np.full(len(cid), i, dtype="int16"))
    dest.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        dest,
        cid=np.concatenate(cids),
        cov=np.concatenate(covs),
        ridx=np.concatenate(ridx),
        region_id=gdf.region_id.to_numpy().astype("int32"),
        title=gdf.title.to_numpy().astype(object),
        grid=np.array([grid.name, str(grid.ny), str(grid.nx)], dtype=object),
        allow_pickle=True,
    )
    total = sum(len(c) for c in cids)
    log(f"regions: coverage {geojson.stem} on {grid.name} -> {dest} ({len(gdf)} regions, {total:,} cells)")
    return dest


class Coverage:
    """Loaded fractional coverage for one layer on one grid."""

    def __init__(self, path: Path, grid: Grid):
        z = np.load(path, allow_pickle=True)
        self.cid = z["cid"].astype(np.int32, copy=False)
        self.cov = z["cov"].astype(np.float32, copy=False)
        self.ridx = z["ridx"].astype(np.int64)
        self.region_id = z["region_id"]
        self.title = [str(t) for t in z["title"]]
        self.grid = grid
        self.n = len(self.region_id)
        #: area in m^2 of the region's share of each listed cell
        self.weight = self.cov * grid.area_row()[self.cid // grid.nx]

    def polygon_area_km2(self) -> np.ndarray:
        return np.bincount(self.ridx, weights=self.weight, minlength=self.n) / 1e6

    def sum_by_region(self, per_cell: np.ndarray) -> np.ndarray:
        return np.bincount(self.ridx, weights=per_cell, minlength=self.n)
