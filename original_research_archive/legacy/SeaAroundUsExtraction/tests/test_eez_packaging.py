"""All final targets must be checked before creating a release."""
import importlib.util
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location('eez_packaging', Path(__file__).parents[1]/'tools/package_eez_release.py')
packaging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packaging)


@pytest.mark.parametrize('collision', ['directory', 'results_zip', 'complete_zip', 'delivery_report'])
def test_release_targets_refuse_every_existing_target(tmp_path, collision):
    destination = tmp_path/'release'
    targets = packaging.release_targets(destination)
    conflict = targets[collision]
    if collision == 'directory':
        conflict.mkdir()
    else:
        conflict.write_text('previous release', encoding='utf-8')
    with pytest.raises(FileExistsError, match='Refusing to replace'):
        packaging.preflight_targets(targets)
    if collision != 'directory':
        assert conflict.read_text() == 'previous release'
        assert not destination.exists()


def test_preflight_is_read_only(tmp_path):
    targets = packaging.release_targets(tmp_path/'release')
    packaging.preflight_targets(targets)
    assert list(tmp_path.iterdir()) == []


def test_release_excludes_runtime_caches_and_inspection_sidecars():
    names=['node_modules','__pycache__','.pytest_cache','book.xlsx.inspect.ndjson','book.xlsx','spatial_validation.json','catch.zip']
    assert packaging.ignored_release_names('',names) == set(names[:4])
