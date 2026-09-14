"""Compare a completed run against the validated 2019 figures.

Skipped unless the outputs exist, so it costs nothing on a checkout with no data. Point it
at a finished run with:

    NPP_OUT_DIR=/path/to/data/out python -m pytest tests/test_validation.py -v

Reference values live in ``reference/expected_2019.json`` and come from the run that
produced the published tables. Tolerances are loose enough to absorb a product
reprocessing that shifts a total by a fraction of a percent, and tight enough that a real
regression -- a lost antimeridian part, a dropped fill stage, a constant cell area --
fails loudly.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
EXPECTED = json.loads((REPO / "reference" / "expected_2019.json").read_text())
OUT = Path(os.environ.get("NPP_OUT_DIR", REPO / "data" / "out"))
YEAR = EXPECTED["year"]

pytestmark = pytest.mark.skipif(
    not (OUT / f"npp_{YEAR}_baseline_by_region.csv").exists(),
    reason=f"no completed run in {OUT}; set NPP_OUT_DIR to a finished run",
)


@pytest.fixture(scope="module")
def tables():
    import pandas as pd

    base = pd.read_csv(OUT / f"npp_{YEAR}_baseline_by_region.csv")
    ens_path = OUT / f"npp_{YEAR}_ensemble_by_region.csv"
    ens = pd.read_csv(ens_path) if ens_path.exists() else None
    return base, ens


@pytest.mark.parametrize("layer", ["lme", "highseas", "eez"])
def test_region_counts_and_areas(tables, layer):
    base, _ = tables
    exp = EXPECTED["layers"][layer]
    sub = base[base.layer == layer]
    assert len(sub) == exp["n_regions"]
    assert sub.polygon_area_km2.sum() / 1e6 == pytest.approx(exp["polygon_area_Mkm2"], rel=2e-3)
    assert sub.water_area_km2.sum() / 1e6 == pytest.approx(exp["water_area_Mkm2"], rel=2e-3)


@pytest.mark.parametrize("layer", ["lme", "highseas", "eez"])
@pytest.mark.parametrize("variant", ["observed", "central", "no_nn", "all_fills"])
def test_baseline_totals(tables, layer, variant):
    base, _ = tables
    exp = EXPECTED["layers"][layer][f"npp_{variant}_PgC"]
    col = {"observed": "npp_observed_tC_yr", "central": "npp_central_tC_yr",
           "no_nn": "npp_no_nn_tC_yr", "all_fills": "npp_all_fills_tC_yr"}[variant]
    got = base[base.layer == layer][col].sum() / 1e9
    assert got == pytest.approx(exp, rel=5e-3)


def test_fill_ordering_is_monotonic(tables):
    """observed <= no spatial fill <= central <= all fills, for every single region.

    Tolerance is relative: several regions have no far fill at all, so the last two are
    the same float64 sum reached by different accumulation orders and differ in the last
    few bits -- which on a 4e9 total is a few thousand tonnes.
    """
    base, _ = tables
    def le(a, b):
        return (a <= b + 1e-9 * b.clip(lower=1.0)).all()
    assert le(base.npp_observed_tC_yr, base.npp_no_nn_tC_yr)
    assert le(base.npp_no_nn_tC_yr, base.npp_central_tC_yr)
    assert le(base.npp_central_tC_yr, base.npp_all_fills_tC_yr)


def test_polar_night_contributes_no_carbon(tables):
    """The `dark` stage exists to add area, not carbon. If it adds carbon, it is a bug."""
    base, _ = tables
    assert base.npp_dark_pct.fillna(0).max() < 0.01


def test_fill_composition(tables):
    base, _ = tables
    total = base.npp_all_fills_tC_yr.sum()
    for cat, exp in EXPECTED["fill_composition_pct_of_npp"].items():
        got = (base[f"npp_{cat}_pct"].fillna(0) * base.npp_all_fills_tC_yr).sum() / 100 / total * 100
        assert got == pytest.approx(exp, abs=0.15), cat


@pytest.mark.parametrize("layer", ["lme", "highseas", "eez"])
def test_ensemble_totals_and_spread(tables, layer):
    _base, ens = tables
    if ens is None:
        pytest.skip("ensemble stage has not been run")
    exp = EXPECTED["layers"][layer]
    sub = ens[ens.layer == layer]
    for model, want in exp["ensemble_scaled_PgC"].items():
        got = sub[f"scaled_{model}_tC_yr"].sum() / 1e9
        assert got == pytest.approx(want, rel=1e-2), model
    assert float(sub.spread_pct.median()) == pytest.approx(exp["median_region_spread_pct"], abs=1.0)
    assert int((sub.n_models < 5).sum()) == exp["regions_with_fewer_than_5_models"]


def test_the_reference_model_equals_the_baseline_central(tables):
    """By construction the reference model's scaled value IS the gap-filled baseline."""
    base, ens = tables
    if ens is None:
        pytest.skip("ensemble stage has not been run")
    m = ens.merge(base[["layer", "region_id", "npp_central_tC_yr"]], on=["layer", "region_id"])
    ok = m.ensemble_basis != "baseline only"
    assert (abs(m.scaled_antoinemorel_tC_yr[ok] - m.npp_central_tC_yr[ok])
            <= 1e-6 * m.npp_central_tC_yr[ok].clip(lower=1)).all()


def test_grid_area_constant_has_not_drifted():
    from npp.grids import GRID_4KM

    assert GRID_4KM.total_area_m2() == pytest.approx(EXPECTED["grid_total_area_m2"], rel=1e-9)
