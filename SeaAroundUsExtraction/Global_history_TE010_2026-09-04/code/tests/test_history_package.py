import json
import zipfile
import hashlib
from pathlib import Path
import pytest
from tools.package_history_release import package_release


def fixture(tmp_path):
    project = tmp_path / 'project'
    history = project / 'history_output'
    output = tmp_path / 'release'
    (history / 'tables').mkdir(parents=True)
    (history / 'spatial').mkdir()
    output.mkdir()
    (history / 'tables/historical_run_metadata.json').write_text(json.dumps({'all_checks_passed':True}))
    (history / 'tables/selection_metrics.json').write_text(json.dumps({'validation':{'status':'passed'}}))
    (history / 'tables/annual_regions.csv').write_bytes(b'year,ppr\n1950,10\n')
    (history / 'spatial/selected_regions.geojson').write_text('{}')
    (output / 'PPR_global_summary.xlsx').write_bytes(b'checked workbook fixture')
    (output / 'saved_workbook_validation.json').write_text(json.dumps({'status':'passed',
        'output_workbook_sha256':hashlib.sha256(b'checked workbook fixture').hexdigest()}))
    (output / 'workbook_validation.json').write_text('{}')
    (project / 'HISTORY_README.md').write_text('Guide')
    return project,output


def test_packages_verified_results_with_hashes_and_without_caches(tmp_path):
    project,output=fixture(tmp_path)
    cache=project/'history_output/tables/regions/A'
    cache.mkdir(parents=True)
    (cache/'static_species.csv.gz').write_bytes(b'cache')
    (cache/'species.csv.gz').write_bytes(b'final')
    result=package_release(project,output)
    with zipfile.ZipFile(result['zip_path']) as archive:
        assert archive.testzip() is None
        assert 'tables/regions/A/species.csv.gz' in archive.namelist()
        assert 'tables/regions/A/static_species.csv.gz' not in archive.namelist()
        assert 'PPR_global_summary.xlsx' in archive.namelist()
    manifest=json.loads((output/'deliverable_manifest.json').read_text())
    assert manifest['files']['tables/annual_regions.csv']['bytes']==len('year,ppr\n1950,10\n')


def test_refuses_unverified_scientific_results(tmp_path):
    project,output=fixture(tmp_path)
    (project/'history_output/tables/historical_run_metadata.json').write_text(json.dumps({'all_checks_passed':False}))
    with pytest.raises(ValueError,match='Historical'):
        package_release(project,output)


def test_refuses_workbook_changed_after_validation(tmp_path):
    project,output=fixture(tmp_path)
    (output/'PPR_global_summary.xlsx').write_bytes(b'changed')
    with pytest.raises(ValueError,match='changed'):
        package_release(project,output)
