"""Global equirectangular grids and exact area / regridding helpers.

Both products used here live on plate-carree grids that span the full globe with cell
centres at half-step offsets, row 0 at the north pole and column 0 at -180 degrees:

    4km   4320 x 8640   (1/24 deg)  Copernicus-GlobColour L4
    12th  2160 x 4320   (1/12 deg)  OSU Ocean Productivity "2x4" grid

The 4 km grid is exactly twice the 1/12 deg grid and shares its origin, so one can be
reduced to the other by a 2x2 block mean with no interpolation at all. That is the only
regridding this pipeline performs.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

#: WGS84 authalic radius, m. Chosen so that summed cell areas reproduce Earth's area.
EARTH_RADIUS_M = 6_371_007.181


@dataclass(frozen=True)
class Grid:
    """A global plate-carree grid."""

    name: str
    ny: int
    nx: int

    @property
    def dlat(self) -> float:
        return 180.0 / self.ny

    @property
    def dlon(self) -> float:
        return 360.0 / self.nx

    @property
    def size(self) -> int:
        return self.ny * self.nx

    def lat_centres(self) -> np.ndarray:
        """Latitude of each row centre, north to south."""
        return 90.0 - (np.arange(self.ny) + 0.5) * self.dlat

    def lon_centres(self) -> np.ndarray:
        return -180.0 + (np.arange(self.nx) + 0.5) * self.dlon

    def area_row(self) -> np.ndarray:
        """Cell area in m^2 for each latitude row.

        A(phi) = R^2 * dLambda * (sin(phi_top) - sin(phi_bottom)), which is exact on a
        sphere and makes cells shrink correctly toward the poles. Using a constant cell
        area instead inflates polar regions by up to an order of magnitude.
        """
        edges = np.deg2rad(np.linspace(90.0, -90.0, self.ny + 1))
        dlam = np.deg2rad(self.dlon)
        return (EARTH_RADIUS_M ** 2) * dlam * (np.sin(edges[:-1]) - np.sin(edges[1:]))

    def cell_area_flat(self, cell_ids: np.ndarray) -> np.ndarray:
        """Cell area in m^2 for flat (row-major) cell indices."""
        return self.area_row()[np.asarray(cell_ids, dtype=np.int64) // self.nx]

    def row_of(self, cell_ids: np.ndarray) -> np.ndarray:
        return np.asarray(cell_ids, dtype=np.int64) // self.nx

    def total_area_m2(self) -> float:
        return float(self.area_row().sum() * self.nx)


GRID_4KM = Grid("4km", 4320, 8640)
GRID_12TH = Grid("12th", 2160, 4320)
GRIDS = {g.name: g for g in (GRID_4KM, GRID_12TH)}


def get_grid(name: str) -> Grid:
    try:
        return GRIDS[name]
    except KeyError:
        raise ValueError(f"unknown grid {name!r}; known: {sorted(GRIDS)}") from None


def block_mean(field: np.ndarray, target: Grid) -> np.ndarray:
    """Reduce ``field`` to ``target`` by an integer-factor block mean over valid cells.

    NaN cells are excluded from each block's mean; a block with no valid cell becomes NaN.
    Requires that the source shape be an exact integer multiple of the target shape, which
    is what makes this an exact regrid rather than a resampling.
    """
    ny, nx = field.shape
    fy, fx = ny // target.ny, nx // target.nx
    if (target.ny * fy, target.nx * fx) != (ny, nx):
        raise ValueError(f"{field.shape} is not an integer multiple of {(target.ny, target.nx)}")
    if (fy, fx) == (1, 1):
        return field.astype("float32", copy=True)
    a = field.astype("float64", copy=False)
    ok = np.isfinite(a)
    s = np.where(ok, a, 0.0).reshape(target.ny, fy, target.nx, fx).sum(axis=(1, 3))
    n = ok.reshape(target.ny, fy, target.nx, fx).sum(axis=(1, 3))
    return np.where(n > 0, s / np.maximum(n, 1), np.nan).astype("float32")


def to_grid(field: np.ndarray, source: Grid, target: Grid) -> np.ndarray:
    """Put ``field`` (on ``source``) onto ``target``. Only downscaling is supported."""
    if source == target:
        return field
    if source.ny % target.ny or source.nx % target.nx:
        raise ValueError(
            f"cannot regrid {source.name} -> {target.name}: only exact integer-factor "
            "reduction is supported, and upscaling is deliberately not implemented "
            "(it would invent detail the product does not have)"
        )
    return block_mean(field, target)
