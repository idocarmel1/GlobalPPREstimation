"""Current-layout paths must work without the historical root directories."""
import csv
import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import openpyxl

from npp import annual, config


def write_catch(root, unit, years):
    region=root/'regions'/unit.split('_')[0]/unit
    write_region(region,unit)
    path = region / 'raw/catch' / f'{unit}.csv.gz'
    path.parent.mkdir(parents=True)
    with gzip.open(path, 'wt') as stream:
        stream.write('unit_id,year\n')
        for year in years:
            stream.write(f'{unit},{year}\n')
    return path


def write_region(region,unit):
    region.mkdir(parents=True,exist_ok=True)
    workbook=openpyxl.Workbook();workbook.active.append(['unit_id',unit])
    workbook.save(region/(unit+'.xlsx'));workbook.close()


def test_defaults_and_example_config_find_shared_data_from_another_cwd(tmp_path, monkeypatch):
    repo = Path(__file__).resolve().parents[4]
    monkeypatch.chdir(tmp_path)
    for cfg in (config.Config.load(), config.Config.load(
            repo / 'tools/scientific_code/NPPExtraction/config.example.yaml')):
        assert cfg.raw_dir == repo / 'common_reference_data/npp/raw'
        assert cfg.work_dir == repo / 'common_reference_data/npp/work'
        assert cfg.out_dir == repo / 'common_reference_data/npp/output/single_year'


def test_current_catch_layout_rejects_wrong_identity(tmp_path):
    path = write_catch(tmp_path, 'LME_001', [1950, 2003, 2003])
    assert annual.archive_grid(tmp_path) == [('LME_001', 1950), ('LME_001', 2003)]
    with gzip.open(path, 'wt') as stream:
        stream.write('unit_id,year\nEEZ_001,2003\n')
    with pytest.raises(ValueError, match='identity'):
        annual.archive_grid(tmp_path)


def test_plan_includes_npp_only_regions_and_uses_separate_runtime_output(tmp_path, monkeypatch):
    write_catch(tmp_path, 'LME_001', [1950, 2003])
    write_region(tmp_path/'regions/HS/HS_018','HS_018')
    output = tmp_path / 'common_reference_data/npp/output'
    output.mkdir(parents=True)
    sources = {model: {'2003': {str(m): 'https://example.invalid/source' for m in range(1, 13)}}
               for model in config.MODELS}
    (output / 'source_catalog.json').write_text(json.dumps({
        'sources': sources, 'metadata': {'errors': {}, 'full_years': {}}}))
    frozen = tmp_path / 'research/npp_extraction_2026_09/results/annual_npp.csv'
    frozen.parent.mkdir(parents=True)
    frozen.write_bytes(b'frozen research results')
    monkeypatch.chdir(tmp_path.parent)
    assert annual.main(['plan', '--root', str(tmp_path), '--years', '2003']) == 0
    with (output / 'annual_npp.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    assert {(r['unit_id'], int(r['year'])) for r in rows} == {
        ('LME_001', 1950), ('LME_001', 2003), ('HS_018', 2003)}
    assert next(r for r in rows if r['unit_id'] == 'HS_018')['status'] == 'pending'
    assert frozen.read_bytes() == b'frozen research results'
    assert not (tmp_path / 'NPPExtraction').exists()


def test_launcher_runs_from_unrelated_directory(tmp_path):
    repo = Path(__file__).resolve().parents[4]
    result = subprocess.run([sys.executable, str(repo / 'tools/cli/npp.py'), '--help'],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'plan' in result.stdout and '--root' in result.stdout


def test_launcher_plan_uses_canonical_discovery_from_unrelated_directory(tmp_path):
    repo=Path(__file__).resolve().parents[4]
    root=tmp_path/'project';write_region(root/'regions/HS/HS_018','HS_018')
    catalog=root/'common_reference_data/npp/source_catalog.json';catalog.parent.mkdir(parents=True)
    sources={model:{'2003':{str(m):'https://example.invalid/source' for m in range(1,13)}}
             for model in config.MODELS}
    catalog.write_text(json.dumps({'sources':sources,'metadata':{'errors':{}}}))
    elsewhere=tmp_path/'elsewhere';elsewhere.mkdir()
    environment=os.environ.copy();environment.pop('PYTHONPATH',None)
    result=subprocess.run([sys.executable,str(repo/'tools/cli/npp.py'),'plan','--root',str(root),'--years','2003'],
                          cwd=elsewhere,env=environment,capture_output=True,text=True,encoding='utf-8')
    assert result.returncode==0,result.stdout+result.stderr
    with (catalog.parent/'output/annual_npp.csv').open() as stream:
        rows=list(csv.DictReader(stream))
    assert [(r['unit_id'],r['year'],r['status']) for r in rows]==[('HS_018','2003','pending')]


def test_plan_without_catalog_stays_offline(tmp_path):
    with pytest.raises(FileNotFoundError, match='probe'):
        annual.main(['plan', '--root', str(tmp_path)])


def test_plan_preserves_previously_extracted_npp_only_years(tmp_path):
    write_region(tmp_path/'regions/HS/HS_018','HS_018')
    output = tmp_path / 'common_reference_data/npp/output'
    output.mkdir(parents=True)
    sources = {model: {str(y): {str(m): 'url' for m in range(1, 13)} for y in [2003, 2004]}
               for model in config.MODELS}
    archived = tmp_path / 'common_reference_data/npp/source_catalog.json'
    archived.parent.mkdir(parents=True, exist_ok=True)
    archived.write_text(json.dumps({'sources': sources, 'metadata': {'errors': {}}}))
    annual.write_annual(output / 'annual_npp.csv', [('HS_018', 2003)],
                        {('HS_018', 2003): {'status': 'complete', 'npp_antoinemorel_tC_yr': 42}}, sources)
    assert annual.main(['plan', '--root', str(tmp_path), '--years', '2004']) == 0
    with (output / 'annual_npp.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 2
    assert rows[0]['npp_antoinemorel_tC_yr'] == '42.0'


def test_preparing_region_selection_does_not_rewrite_shared_geometry(tmp_path, monkeypatch):
    from npp import regions
    raw = tmp_path / 'raw'
    work = tmp_path / 'work'
    raw.mkdir()
    work.mkdir()
    full = {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'properties': {'region_id': n}, 'geometry': None} for n in [1, 2]]}
    (raw/'geography').mkdir()
    (raw / 'geography/sau_lme_full.geojson').write_text(json.dumps(full))
    (raw / 'geography/sau_lme.geojson').write_bytes(b'original source selection')
    inputs = []
    # Full rasterization is external to the path/selection contract being tested.
    monkeypatch.setattr(regions, 'build_coverage', lambda path, grid, out: inputs.append(path))
    assert annual.prepare_regions(tmp_path, [('LME_002', 2003)], raw, work) == ['lme']
    assert (raw / 'geography/sau_lme.geojson').read_bytes() == b'original source selection'
    assert all(path == work / 'geometry/sau_lme.geojson' for path in inputs)
    cfg = config.Config(raw_dir=raw, work_dir=work, geometry_dir=work / 'geometry')
    selected = json.loads(cfg.geojson_path('lme').read_text())
    assert [f['properties']['region_id'] for f in selected['features']] == [2]


def manifest_fixture(tmp_path):
    """A fresh clone has original inputs and a tracked manifest, no runtime metadata."""
    cfg = config.Config(year=2003, window_years=[2003], raw_dir=tmp_path / 'raw',
                        out_dir=tmp_path / 'output',
                        ensemble=config.EnsembleConfig(models=['antoinemorel']))
    cfg.out_dir.mkdir()
    sources = {'antoinemorel': {'2003': {}}}
    records = []
    for month in range(1, 13):
        path = annual.copernicus.local_path(cfg.raw_dir, 2003, month)
        path.parent.mkdir(parents=True, exist_ok=True)
        content = f'original monthly source {month}'.encode()
        path.write_bytes(content)
        url = f'https://example.invalid/month/{month}'
        sources['antoinemorel']['2003'][str(month)] = url
        records.append({'path': path.relative_to(cfg.raw_dir).as_posix(), 'url': url,
                        'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)})
    manifest = tmp_path / 'source_manifest.json'
    manifest.write_text(json.dumps({'files': records}))
    return cfg, sources, manifest


def test_fresh_clone_reuses_hash_verified_raw_without_runtime_download_records(tmp_path, monkeypatch):
    from npp import http
    cfg, sources, _ = manifest_fixture(tmp_path)
    def unexpected_network(*args, **kwargs):
        raise AssertionError('verified original sources must not contact the network')
    monkeypatch.setattr(http, '_open', unexpected_network)
    records = annual.fetch_year(cfg, sources, 2, cfg.out_dir)
    assert len(records) == 12
    assert all(record['status'] == 'downloaded' for record in records)
    assert (cfg.out_dir / 'downloads_2003.json').is_file()


def test_manifest_reuse_hashes_bytes_and_preserves_corrupt_raw_for_review(tmp_path, monkeypatch):
    from npp import http
    cfg, sources, _ = manifest_fixture(tmp_path)
    path = annual.copernicus.local_path(cfg.raw_dir, 2003, 1)
    original = path.read_bytes()
    # Same length and restored modification time must not bypass content verification.
    import os
    stamp = path.stat()
    path.write_bytes(b'x' * len(original))
    os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    def unexpected_network(*args, **kwargs):
        raise AssertionError('altered original sources must not be downloaded over')
    monkeypatch.setattr(http, '_open', unexpected_network)
    with pytest.raises(RuntimeError, match='original source.*SHA-256'):
        annual.fetch_year(cfg, sources, 2, cfg.out_dir)
    assert path.read_bytes() == b'x' * len(original)


def test_tracked_manifest_cannot_point_outside_raw(tmp_path, monkeypatch):
    cfg, sources, manifest = manifest_fixture(tmp_path)
    records = json.loads(manifest.read_text())
    records['files'][0]['path'] = '../outside.nc'
    manifest.write_text(json.dumps(records))
    monkeypatch.setattr(annual, 'download', lambda *a, **kw: (_ for _ in ()).throw(AssertionError('network')))
    with pytest.raises(ValueError, match='raw-relative'):
        annual.fetch_year(cfg, sources, 2, cfg.out_dir)


def test_runtime_same_url_conflicting_hash_is_explicit(tmp_path, monkeypatch):
    cfg, sources, manifest = manifest_fixture(tmp_path)
    record = json.loads(manifest.read_text())['files'][0]
    record.update(status='downloaded', sha256='0' * 64)
    (cfg.out_dir / 'downloads_2003.json').write_text(json.dumps([record]))
    monkeypatch.setattr(annual, 'download', lambda *a, **kw: (_ for _ in ()).throw(AssertionError('network')))
    with pytest.raises(ValueError, match='conflicting.*SHA-256'):
        annual.fetch_year(cfg, sources, 2, cfg.out_dir)


def test_changed_source_url_does_not_replace_versioned_original(tmp_path, monkeypatch):
    from npp import http
    cfg, sources, _ = manifest_fixture(tmp_path)
    path = annual.copernicus.local_path(cfg.raw_dir, 2003, 1)
    original = path.read_bytes()
    sources['antoinemorel']['2003']['1'] = 'https://example.invalid/new-release'
    monkeypatch.setattr(http, '_open', lambda *a, **kw: (_ for _ in ()).throw(AssertionError('network')))
    with pytest.raises(RuntimeError, match='original source.*URL'):
        annual.fetch_year(cfg, sources, 2, cfg.out_dir)
    assert path.read_bytes() == original


@pytest.mark.parametrize('matching', [True, False])
def test_missing_original_is_published_only_after_manifest_hash_validation(tmp_path, monkeypatch, matching):
    from npp import http
    cfg, sources, _ = manifest_fixture(tmp_path)
    path = annual.copernicus.local_path(cfg.raw_dir, 2003, 1)
    original = path.read_bytes()
    path.unlink()
    payload = original if matching else b'changed backend payload'
    requests = []
    class Response(io.BytesIO):
        headers = {'Content-Length': str(len(payload))}
    def response(url, *args, **kwargs):
        requests.append(url)
        return Response(payload)
    monkeypatch.setattr(http, '_open', response)
    if matching:
        annual.fetch_year(cfg, sources, 2, cfg.out_dir)
        assert path.read_bytes() == original
    else:
        with pytest.raises(RuntimeError, match='original source.*SHA-256'):
            annual.fetch_year(cfg, sources, 2, cfg.out_dir)
        assert not path.exists()
    assert requests == ['https://example.invalid/month/1']
