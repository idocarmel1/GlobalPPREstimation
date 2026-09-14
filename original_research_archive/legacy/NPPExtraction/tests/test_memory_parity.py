"""Numeric parity with the supplied ZIP before changes to array lifetimes/types."""
import types
import zipfile
from pathlib import Path

import numpy as np

from npp.aggregate import LayerAccumulator
from npp.config import Config
from npp.fill import MonthFields
from npp.grids import Grid
from npp.regions import Coverage


def test_optimized_coverage_and_accumulator_match_original_exactly(tmp_path):
    archive = Path(__file__).resolve().parents[1] / 'ppr-npp.zip'
    with zipfile.ZipFile(archive) as z:
        source = z.read('ppr-npp/npp/aggregate.py').decode()
    old = types.ModuleType('npp._original_aggregate')
    old.__package__ = 'npp'
    exec(compile(source, 'original-aggregate.py', 'exec'), old.__dict__)
    path = tmp_path/'coverage.npz'
    ids = np.arange(16,dtype='int32')
    fractions = np.linspace(.1,1,16,dtype='float32')
    regions = np.repeat(np.arange(2,dtype='int16'),8)
    np.savez(path,cid=ids,cov=fractions,ridx=regions,region_id=np.array([1,2]),title=np.array(['A','B']))
    grid = Grid('small',4,4)
    cov = Coverage(path,grid)
    before_cov = Coverage(path,grid)
    before_cov.cid = ids.astype('int64')
    before_cov.cov = fractions.astype('float64')
    before_cov.weight = before_cov.cov * grid.cell_area_flat(before_cov.cid)
    np.testing.assert_array_equal(cov.weight,before_cov.weight)
    actual, expected = LayerAccumulator(cov), old.LayerAccumulator(before_cov)
    wet = np.ones(16,dtype=bool)
    actual.bind_watermask(wet); expected.bind_watermask(wet)
    rng = np.random.default_rng(42)
    target = rng.random(16,dtype='float32')*1000
    clim = rng.random(16,dtype='float32')*500
    target[::2]=np.nan
    clim[::3]=np.nan
    mf=MonthFields(2,29,target,clim,np.ones(16,dtype='float32')*200,
                   ids%7==0,rng.random(16,dtype='float32')*300,ids%5==0)
    cfg=Config(year=2020,window_years=[2020])
    actual.add_month(mf,cfg); expected.add_month(mf,cfg)
    for field in ('carbon_g','area_m2','carbon_mean_year_g','anomaly_factor'):
        np.testing.assert_array_equal(getattr(actual,field),getattr(expected,field))
