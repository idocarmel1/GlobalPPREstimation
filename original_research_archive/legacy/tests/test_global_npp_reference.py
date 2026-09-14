import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


def geometry():
    return {'id': 'fixture_union', 'unit_ids': ['LME_001', 'HS_001'],
            'sha256': 'abc', 'geography': 'Fixed polygon union'}


def record(year=2019, **changes):
    return {'year': year, 'status': 'complete', 'geometry_sha256': 'abc',
            'expected_models': ['antoinemorel', 'vgpm', 'cafe'],
            'model_totals_tC_yr': {'antoinemorel': 100, 'vgpm': 900, 'cafe': 200},
            'provenance': 'fixture.json', **changes}


def test_reference_uses_median_of_union_totals_and_has_no_selection_input():
    from global_npp_reference import reference_payload
    result = reference_payload([1950, 2019], [record()], geometry())
    assert result['npp']['ens_median_tC_yr'] == [None, 200]
    assert result['npp']['npp_vgpm_tC_yr'] == [None, 900]
    assert result['units'] == ['LME_001', 'HS_001']
    assert result['ensemble_details']['id'] == 'median_of_union_model_totals'
    assert isinstance(result['ensemble_convention'], str)
    assert result['annual']['2019']['n_models'] == 3
    assert result['metadata']['2019']['calculation_complete'] is True
    assert result['metadata']['2019']['coverage_complete'] is False
    assert result['metadata']['2019']['coverage_limited'] is True


def test_missing_model_does_not_shrink_ensemble_or_substitute_zero():
    from global_npp_reference import reference_payload
    result = reference_payload([2019], [record(model_totals_tC_yr={'antoinemorel': 100, 'vgpm': None, 'cafe': 200})], geometry())
    assert result['npp']['ens_median_tC_yr'] == [None]
    assert result['npp']['npp_vgpm_tC_yr'] == [None]
    assert result['npp']['npp_cafe_tC_yr'] == [200]
    assert result['annual']['2019']['status'] == 'incomplete_model_support'


def test_incomplete_geography_is_a_gap_even_with_finite_totals():
    from global_npp_reference import reference_payload
    result = reference_payload([2019], [record(status='incomplete_geography')], geometry())
    assert all(values == [None] for values in result['npp'].values())


def test_wrong_geometry_and_duplicate_years_rejected():
    from global_npp_reference import reference_payload
    with pytest.raises(ValueError, match='geometry'):
        reference_payload([2019], [record(geometry_sha256='changed')], geometry())
    with pytest.raises(ValueError, match='Duplicate'):
        reference_payload([2019], [record(), record()], geometry())


def test_pre_satellite_years_stay_blank_and_proxy_is_never_implicit():
    from global_npp_reference import reference_payload
    result = reference_payload([1950, 1998, 1999, 2019], [record(1998), record()], geometry())
    assert result['npp']['ens_median_tC_yr'] == [None, 200, None, 200]
    assert result['annual']['1950']['status'] == 'outside_source_coverage'
    assert result['annual']['1999']['status'] == 'not_extracted'
    assert result['annual']['1998']['source_year'] == 1998


def test_true_zero_preserved_and_invalid_totals_rejected():
    from global_npp_reference import reference_payload
    item = record(expected_models=['antoinemorel'], model_totals_tC_yr={'antoinemorel': 0})
    assert reference_payload([2019], [item], geometry())['npp']['ens_median_tC_yr'] == [0]
    with pytest.raises(ValueError, match='NPP'):
        reference_payload([2019], [record(model_totals_tC_yr={'cafe': -1})], geometry())


def test_fixed_union_removes_overlap_instead_of_summing_polygons():
    from global_npp_reference import dissolve_geometries
    from shapely.geometry import box
    union, audit = dissolve_geometries([box(0, 0, 2, 2), box(1, 0, 3, 2)])
    assert union.area == 6
    assert audit['summed_planar_area_degrees2'] == 8
    assert audit['overlap_planar_area_degrees2'] == 2


def test_partial_cache_cannot_be_reused_with_changed_inputs(tmp_path):
    from global_npp_reference import guard_cached_inputs
    manifest = tmp_path / 'inputs.json'
    original = {'geometry': 'a', 'source': 'b', 'code': 'c'}
    guard_cached_inputs(manifest, original)
    guard_cached_inputs(manifest, original)
    for field in original:
        with pytest.raises(ValueError, match='cache inputs changed'):
            guard_cached_inputs(manifest, {**original, field: 'changed'})


def test_downloaded_bytes_must_match_source_manifest(tmp_path):
    from global_npp_reference import verify_source_files, sha256
    raw = tmp_path / 'NPPExtraction/data/raw/copernicus/fixture.nc'
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b'original')
    source = [{'path': str(raw), 'bytes': 8, 'sha256': sha256(raw)}]
    assert verify_source_files(tmp_path, source)[0]['sha256'] == sha256(raw)
    original_stat = raw.stat()
    raw.write_bytes(b'changed!')
    # Replacements and timestamp-preserving copies can retain all cache metadata.
    os.utime(raw, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
    assert raw.stat().st_mtime_ns == original_stat.st_mtime_ns
    assert raw.stat().st_size == original_stat.st_size
    with pytest.raises(ValueError, match='source checksum'):
        verify_source_files(tmp_path, source)


def test_interrupted_npz_is_not_accepted_as_completed_cache(tmp_path):
    from global_npp_reference import complete_npz
    import numpy as np
    path = tmp_path / 'stage.npz'
    path.write_bytes(b'PK\x03\x04 unfinished zip file')
    assert complete_npz(path, ['totals']) is False
    assert not path.exists()
    assert path.with_suffix('.incomplete.npz').read_bytes() == b'PK\x03\x04 unfinished zip file'
    np.savez(path, totals=np.array([1, 2]))
    assert complete_npz(path, ['totals']) is True


def test_coverage_limited_record_retains_finite_reference_and_honest_flags():
    from global_npp_reference import reference_payload
    result = reference_payload([2019], [record(status='coverage_limited',
        coverage={'water_area_pct_of_polygon': 80})], geometry())
    assert result['values'] == [200]
    annual = result['metadata']['2019']
    assert annual['status'] == 'coverage_limited'
    assert annual['calculation_complete'] is True
    assert annual['geometry_complete'] is True
    assert annual['coverage_complete'] is False
    assert annual['water_area_pct_of_polygon'] == 80


def test_source_configuration_follows_canonical_rows_after_fresh_clone_rerun(tmp_path):
    from global_npp_reference import source_configuration_path
    import csv
    directory = tmp_path / 'NPPExtraction/output/years/2019'
    for key in ['historical', 'fresh_clone']:
        path = directory / key / 'provenance.json'
        path.parent.mkdir(parents=True)
        path.write_text('{}')
    canonical = tmp_path / 'NPPExtraction/output/annual_npp.csv'
    with canonical.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['unit_id', 'year', 'provenance'])
        writer.writeheader()
        writer.writerow({'unit_id': 'LME_034', 'year': 2019,
                         'provenance': 'NPPExtraction/output/years/2019/fresh_clone/provenance.json'})
    assert source_configuration_path(tmp_path, 2019) == directory / 'fresh_clone/provenance.json'


def test_conflicting_canonical_source_configurations_rejected(tmp_path):
    from global_npp_reference import source_configuration_path
    path = tmp_path / 'NPPExtraction/output/annual_npp.csv'
    path.parent.mkdir(parents=True)
    path.write_text('unit_id,year,provenance\nLME_001,2019,NPPExtraction/output/years/2019/a/provenance.json\n'
                    'LME_002,2019,NPPExtraction/output/years/2019/b/provenance.json\n')
    with pytest.raises(ValueError, match='Conflicting canonical'):
        source_configuration_path(tmp_path, 2019)


def test_reference_source_ignores_separate_eez_expansion(tmp_path):
    """Regional EEZ publication cannot change the fixed LME/high-seas source run."""
    from global_npp_reference import source_configuration_path
    directory = tmp_path / 'NPPExtraction/output/years/2019/original'
    directory.mkdir(parents=True)
    original = directory / 'provenance.json'
    original.write_text('{}')
    import hashlib
    expanded = tmp_path / 'NPPExtraction/output/regional_expansion/years/2019/provenance.json'
    expanded.parent.mkdir(parents=True)
    expanded.write_text(json.dumps({'source_configuration': {
        'path': 'NPPExtraction/output/years/2019/original/provenance.json',
        'sha256': hashlib.sha256(original.read_bytes()).hexdigest()}}))
    canonical = tmp_path / 'NPPExtraction/output/annual_npp.csv'
    canonical.write_text('unit_id,year,provenance\n'
        'LME_001,2019,NPPExtraction/output/years/2019/original/provenance.json\n'
        'EEZ_001,2019,NPPExtraction/output/regional_expansion/years/2019/provenance.json\n')
    assert source_configuration_path(tmp_path, 2019) == original


def test_reference_source_rejects_changed_expansion_parent(tmp_path):
    from global_npp_reference import source_configuration_path
    directory = tmp_path / 'NPPExtraction/output/years/2019/original'
    directory.mkdir(parents=True)
    (directory / 'provenance.json').write_text('{}')
    expanded = tmp_path / 'NPPExtraction/output/regional_expansion/years/2019/provenance.json'
    expanded.parent.mkdir(parents=True)
    expanded.write_text(json.dumps({'source_configuration': {
        'path': 'NPPExtraction/output/years/2019/original/provenance.json', 'sha256': 'wrong'}}))
    (tmp_path / 'NPPExtraction/output/annual_npp.csv').write_text(
        'unit_id,year,provenance\nEEZ_001,2019,NPPExtraction/output/regional_expansion/years/2019/provenance.json\n')
    with pytest.raises(ValueError, match='checksum'):
        source_configuration_path(tmp_path, 2019)
