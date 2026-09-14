"""Invariants that hold with no data downloaded.

These are the checks that would have caught the real bugs found while building this:
a polar-night month treated as a gap, an antimeridian polygon silently truncated, a
constant cell area, and a NaN written into a spreadsheet.
"""

from __future__ import annotations

import numpy as np
import pytest

from npp.config import Config, FillConfig
from npp.grids import GRID_4KM, GRID_12TH, Grid, block_mean, get_grid, to_grid
from npp.regions import clean_geometry
from npp.solar import monthly_tables, month_start_doy


# ---------------------------------------------------------------- grids
def test_total_area_matches_earth():
    for grid in (GRID_4KM, GRID_12TH):
        assert np.isclose(grid.total_area_m2(), 5.100656e14, rtol=1e-6)


def test_cell_area_shrinks_toward_the_poles():
    a = GRID_4KM.area_row()
    assert a[GRID_4KM.ny // 2] > 10 * a[0]          # equator vs the top row
    assert np.isclose(a[0], a[-1], rtol=1e-9)        # symmetric about the equator
    assert np.all(np.diff(a[: GRID_4KM.ny // 2]) > 0)


def test_grids_are_exactly_two_times_related():
    assert GRID_4KM.ny == 2 * GRID_12TH.ny
    assert GRID_4KM.nx == 2 * GRID_12TH.nx
    assert np.isclose(GRID_4KM.lat_centres()[0], 90 - 0.5 / 24, atol=1e-9)
    assert np.isclose(GRID_12TH.lon_centres()[0], -180 + 0.5 / 12, atol=1e-9)


def test_block_mean_ignores_nan_and_conserves_a_constant_field():
    src = np.full((4, 8), 3.0, dtype="float32")
    src[0, 0] = np.nan
    out = block_mean(src, Grid("t", 2, 4))
    assert out.shape == (2, 4)
    assert np.allclose(out, 3.0)                     # the NaN is excluded, not counted as 0


def test_block_mean_yields_nan_for_an_all_nan_block():
    src = np.full((2, 2), np.nan, dtype="float32")
    assert np.isnan(block_mean(src, Grid("t", 1, 1))[0, 0])


def test_regrid_refuses_upscaling_and_non_integer_factors():
    with pytest.raises(ValueError):
        to_grid(np.zeros((GRID_12TH.ny, GRID_12TH.nx), "float32"), GRID_12TH, GRID_4KM)
    with pytest.raises(ValueError):
        to_grid(np.zeros((100, 100), "float32"), Grid("odd", 100, 100), Grid("t", 30, 30))


def test_get_grid_rejects_unknown_names():
    with pytest.raises(ValueError):
        get_grid("nope")


# ---------------------------------------------------------------- solar
def test_polar_night_and_polar_day_are_detected():
    q, lit = monthly_tables(2019, 180)               # 1 degree rows is plenty
    lat = 90.0 - (np.arange(180) + 0.5)
    north = int(np.abs(lat - 85).argmin())
    south = int(np.abs(lat + 85).argmin())
    assert lit[0, north] == 0 and q[0, north] == 0.0   # January, high north: dark
    assert lit[0, south] == 31 and q[0, south] > 300   # January, high south: lit all month
    assert lit[6, north] == 31 and lit[6, south] == 0  # July: reversed


def test_the_tropics_are_never_dark():
    _q, lit = monthly_tables(2019, 180)
    lat = 90.0 - (np.arange(180) + 0.5)
    tropics = np.abs(lat) < 23.0
    assert (lit[:, tropics] > 0).all()


def test_annual_insolation_peaks_at_the_equator_and_is_lowest_at_the_poles():
    q, _lit = monthly_tables(2019, 180)
    annual = q.mean(axis=0)
    assert annual.argmax() in range(85, 95)
    assert annual[0] < annual[90]


def test_month_start_doy_handles_leap_years():
    assert month_start_doy(2019, 1) == 1
    assert month_start_doy(2019, 3) == 60
    assert month_start_doy(2020, 3) == 61          # leap
    assert month_start_doy(2019, 12) == 335


# ---------------------------------------------------------------- geometry repair
def test_antimeridian_polygon_is_split_not_truncated():
    from shapely.geometry import Polygon

    # a box straddling the dateline, written the way the SAU LME file writes it
    poly = Polygon([(-185, 50), (-175, 50), (-175, 60), (-185, 60)])
    fixed = clean_geometry(poly)
    assert fixed is not None
    # both halves survive: one against +180, one against -180
    assert np.isclose(fixed.area, poly.area, rtol=1e-9)
    xs = [x for g in fixed.geoms for x, _ in g.exterior.coords]
    assert max(xs) > 179 and min(xs) < -179
    assert fixed.bounds[0] >= -180 and fixed.bounds[2] <= 180


def test_self_intersecting_polygon_is_repaired_to_a_multipolygon():
    from shapely.geometry import Polygon

    bowtie = Polygon([(0, 0), (2, 2), (2, 0), (0, 2)])
    assert not bowtie.is_valid
    fixed = clean_geometry(bowtie)
    assert fixed is not None and fixed.is_valid
    assert fixed.geom_type == "MultiPolygon"


def test_a_normal_polygon_is_left_alone():
    from shapely.geometry import box

    b = box(10, 10, 20, 20)
    fixed = clean_geometry(b)
    assert np.isclose(fixed.area, b.area, rtol=1e-12)


# ---------------------------------------------------------------- config
def test_central_categories_follow_the_switches():
    assert FillConfig().central_categories() == ["obs", "dark", "clim", "nn_near"]
    off = FillConfig(dark_is_zero=False, use_climatology=False, use_nearest_neighbour=False)
    assert off.central_categories() == ["obs"]
    withfar = FillConfig(nn_far_in_central=True)
    assert "nn_far" in withfar.central_categories()


def test_donor_years_exclude_the_target():
    cfg = Config(year=2019, window_years=[2017, 2018, 2019, 2020, 2021])
    assert cfg.donor_years() == [2017, 2018, 2020, 2021]
    pinned = Config(year=2019, window_years=[2019],
                    fill=FillConfig(climatology_years=[2010, 2019, 2011]))
    assert pinned.donor_years() == [2010, 2011]


def test_config_rejects_a_window_without_the_target_year():
    with pytest.raises(ValueError):
        Config(year=2019, window_years=[2020, 2021]).validate()


def test_config_rejects_unknown_layers_and_models():
    with pytest.raises(ValueError):
        Config(layers=["lme", "atlantis"]).validate()


def test_workbook_turns_nan_into_a_blank_cell():
    from npp.workbook import _clean

    assert _clean(float("nan")) is None
    assert _clean(np.nan) is None
    assert _clean(3.5) == 3.5
    assert _clean("text") == "text"
    assert _clean(None) is None
