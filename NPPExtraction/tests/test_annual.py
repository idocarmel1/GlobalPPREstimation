import csv
import gzip
import io
from pathlib import Path

import pytest

from npp import config


def test_year_override_without_pinned_window_recentres():
    assert config.Config.load(year=2004).window_years == [2002, 2003, 2004, 2005, 2006]


def test_cache_identity_changes_with_science_and_reference_model():
    a = config.Config()
    b = config.Config(fill=config.FillConfig(nn_far_in_central=True))
    assert hasattr(a, 'cache_key'), 'configuration needs a scientific cache identity'
    assert a.cache_key() != b.cache_key()
    b.ensemble.reference_model = 'vgpm'
    assert a.watermask_path() != b.watermask_path()


def test_archive_grid_uses_actual_catch_years_and_rejects_wrong_identity(tmp_path):
    from npp.annual import archive_grid
    region = tmp_path / 'PPRAtlas/archive/regions/LME_001'
    region.mkdir(parents=True)
    catch = tmp_path / 'SeaAroundUsExtraction/data/catch_by_taxon_year/LME_001.csv.gz'
    catch.parent.mkdir(parents=True)
    with gzip.open(catch, 'wt') as f:
        f.write('unit_id,year\nLME_001,1950\nLME_001,1950\nLME_001,2003\n')
    assert archive_grid(tmp_path) == [('LME_001', 1950), ('LME_001', 2003)]
    with gzip.open(catch, 'wt') as f:
        f.write('unit_id,year\nEEZ_001,2003\n')
    with pytest.raises(ValueError, match='identity'):
        archive_grid(tmp_path)


def test_catalog_requires_twelve_months_not_just_endpoints():
    from npp.annual import full_years, bounded_window
    months = {str(y): {str(m): 'url' for m in range(1, 13)} for y in [1998, 1999, 2000]}
    months['1997'] = {'9': 'url', '12': 'url'}
    assert full_years(months) == [1998, 1999, 2000]
    assert bounded_window(1998, full_years(months)) == [1998, 1999, 2000]


def test_osu_source_html_allows_spaces_around_href():
    from npp import annual
    assert hasattr(annual, 'parse_osu_links')
    got = annual.parse_osu_links('<a href = "./data/vgpm.2019001.hdf.gz">January</a>', 'https://source.test/page')
    assert got == {'2019': {'1': 'https://source.test/data/vgpm.2019001.hdf.gz'}}


def test_archive_without_catch_is_reported_separately(tmp_path):
    from npp.annual import archive_grid
    (tmp_path / 'PPRAtlas/archive/regions/HS_018').mkdir(parents=True)
    missing = []
    assert archive_grid(tmp_path, missing=missing) == []
    assert missing == [{'unit_id': 'HS_018', 'status': 'no_catch', 'reason': 'catch file absent'}]


def test_output_preserves_missing_models_and_labels_ensemble_count(tmp_path):
    from npp.annual import write_annual
    out = tmp_path / 'annual.csv'
    values = {('LME_001', 2003): {'npp_antoinemorel_tC_yr': 12.0, 'status': 'partial', 'reason': 'no model retrieval'}}
    write_annual(out, [('LME_001', 1950), ('LME_001', 2003)], values, {'antoinemorel': {'2003': {str(m): 'u' for m in range(1, 13)}}})
    rows = list(csv.DictReader(out.open()))
    assert rows[0]['npp_antoinemorel_tC_yr'] == ''
    assert rows[0]['status'] == 'unsupported'
    assert rows[1]['npp_vgpm_tC_yr'] == ''
    assert rows[1]['n_models'] == '1'
    assert rows[1]['ens_median_tC_yr'] == '12.0'


def test_downloader_rejects_truncated_response(tmp_path, monkeypatch):
    from npp import http
    class Response(io.BytesIO):
        headers = {'Content-Length': '10'}
    monkeypatch.setattr(http, '_open', lambda *a, **kw: Response(b'abc'))
    monkeypatch.setattr(http.time, 'sleep', lambda _: None)
    with pytest.raises(RuntimeError, match='length'):
        http.download('https://example.invalid/file', tmp_path/'file', retries=1)
    assert not (tmp_path/'file').exists()


def test_cli_cache_rejects_a_different_fill_configuration(tmp_path):
    from npp import cli
    assert hasattr(cli, '_cache_valid')
    cfg = config.Config(raw_dir=tmp_path/'raw', work_dir=tmp_path/'work')
    result = tmp_path/'baseline.npz'
    result.write_bytes(b'completed')
    assert not cli._cache_valid(result, cfg)
    cli._cache_stamp(result, cfg)
    assert cli._cache_valid(result, cfg)
    cfg.fill.nn_far_in_central = True
    assert not cli._cache_valid(result, cfg)


def test_synthetic_extraction_weights_month_days_and_keeps_model_gaps(tmp_path, monkeypatch):
    import numpy as np
    from npp import aggregate, ensemble, fill, annual
    from npp.grids import Grid
    cfg = config.Config(year=2020, window_years=[2020], layers=['lme'],
                        raw_dir=tmp_path/'raw', work_dir=tmp_path/'work', out_dir=tmp_path/'out',
                        fill=config.FillConfig(use_climatology=False, use_nearest_neighbour=False))
    cfg.ensure_dirs()
    cfg.geojson_path('lme').write_text('{}')
    small = Grid('4km', 2, 4)
    for mod in (aggregate, ensemble, fill):
        monkeypatch.setattr(mod, 'get_grid', lambda name: small)
    def source(raw, model, year, month, cache_dir=None):
        a = np.full((2, 4), 100.0 * (config.MODELS.index(model) + 1), dtype='float32')
        if model == 'vgpm':
            a[1, 0] = np.nan
        return a
    monkeypatch.setattr(fill, 'read_model', source)
    monkeypatch.setattr(ensemble, 'read_model', source)
    digest = annual.hashlib.sha256(b'{}').hexdigest()[:12]
    cache = cfg.work_dir/'coverage'
    cache.mkdir()
    for g in ('4km', '12th'):
        np.savez(cache/f'lme_{g}_{digest}.npz', cid=np.array([0,4]), cov=np.array([1.,1.]),
                 ridx=np.array([0,1]), region_id=np.array([1,2]), title=np.array(['A','B']))
    rows = annual.extract_year(cfg, cfg.work_dir, cfg.out_dir, [])
    expect = 100 * small.cell_area_flat(np.array([0]))[0] * 366 * 1e-9
    assert rows[0]['npp_antoinemorel_tC_yr'] == pytest.approx(expect)
    assert rows[0]['npp_cafe_tC_yr'] == pytest.approx(expect * 5)
    assert rows[1]['npp_vgpm_tC_yr'] is None
    assert rows[1]['status'] == 'partial'


def test_source_content_changes_invalidate_completion_key(tmp_path):
    from npp import annual
    assert hasattr(annual, 'completion_key')
    cfg = config.Config(raw_dir=tmp_path)
    first = [{'url':'https://source/v1', 'sha256':'aaa'}]
    changed = [{'url':'https://source/v1', 'sha256':'bbb'}]
    assert annual.completion_key(cfg, first) != annual.completion_key(cfg, changed)


def test_copernicus_read_accepts_unicode_directory(tmp_path):
    import numpy as np
    from netCDF4 import Dataset
    from npp.sources import copernicus
    ascii_path = tmp_path/'source.nc'
    with Dataset(str(ascii_path), 'w') as ds:
        for name, size in [('time',1), ('latitude',2), ('longitude',4)]:
            ds.createDimension(name,size)
        v=ds.createVariable('PP', 'f4', ('time','latitude','longitude'), fill_value=-9999)
        v[:] = np.full((1,2,4), 123.)
        v[0,0,0] = -9999
    raw = tmp_path/'מחקר'
    path = copernicus.local_path(raw,2019,1)
    path.parent.mkdir(parents=True)
    path.write_bytes(ascii_path.read_bytes())
    got = copernicus.read(raw,2019,1)
    assert np.isnan(got[0,0])
    assert got[1,1] == 123.


def test_osu_read_accepts_unicode_directory_and_closes_native_file(tmp_path):
    import numpy as np
    from pyhdf.SD import SD, SDC
    from npp.sources import osu
    source = tmp_path/'source.hdf'
    handle = SD(str(source), SDC.WRITE | SDC.CREATE)
    field = handle.create('npp', SDC.FLOAT32, (2, 4))
    field[:] = np.array([[-9999,1,2,3],[4,5,6,7]],dtype='float32')
    field.endaccess(); handle.end()
    raw = tmp_path/'מחקר'
    archive = osu.local_path(raw,'vgpm',2019,1)
    archive.parent.mkdir(parents=True)
    archive.write_bytes(gzip.compress(source.read_bytes()))
    got = osu.read(raw,'vgpm',2019,1)
    assert np.isnan(got[0,0])
    assert got[1,1] == 5
    # A leaked HDF native file handle prevents unlink on Windows.
    archive.with_suffix('').unlink()


def test_decoded_copernicus_cache_is_lossless_and_changes_with_source(tmp_path):
    import numpy as np
    from netCDF4 import Dataset
    from npp.sources import copernicus
    raw = tmp_path/'raw'
    source = copernicus.local_path(raw,2019,1)
    source.parent.mkdir(parents=True)
    def write(value):
        with Dataset(str(source),'w') as ds:
            for name, n in [('time',1),('lat',1),('lon',2)]: ds.createDimension(name,n)
            v = ds.createVariable('PP','f4',('time','lat','lon'),fill_value=-9999)
            v[:] = np.array([[[value,-9999]]],dtype='float32')
    write(42.)
    first = copernicus.read(raw,2019,1)
    assert isinstance(first,np.memmap), 'monthly decoding should be reused across overlapping annual windows'
    assert first[0,0] == 42 and np.isnan(first[0,1])
    second = copernicus.read(raw,2019,1)
    np.testing.assert_array_equal(first,second)
    write(84.)
    third = copernicus.read(raw,2019,1)
    assert third[0,0] == 84.


def test_region_omitted_after_geometry_repair_is_explicitly_missing():
    from npp import annual
    assert hasattr(annual,'complete_year_records')
    records = [{'unit_id':'LME_001','year':2019,'status':'complete'}]
    grid=[('LME_001',2019),('LME_002',2019)]
    result = annual.complete_year_records(records,grid,2019,'provenance.json')
    assert result[1]['unit_id'] == 'LME_002'
    assert result[1]['status'] == 'missing'
    assert 'geometry' in result[1]['reason']
