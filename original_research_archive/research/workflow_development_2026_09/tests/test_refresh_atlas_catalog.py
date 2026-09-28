"""Catalog refresh retains the verified archive without rewriting its files."""
import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))


def fixture_catalogs(tmp_path):
    old_article = {'article_id':'source__EEZ_001', 'source_article_id':'source',
                   'geometry':None, 'footprint_key':'source_verified_footprint',
                   'material_files':[{'sha256':'abc', 'role':'main', 'relative_path':'archive/regions/EEZ_001/source/paper.pdf',
                                      'canonical_relative_path':'research/downloads/paper.pdf', 'local_filename':'paper.pdf'}]}
    old = {'regions':[{'unit_id':'EEZ_001'}], 'articles':[old_article]}
    fresh = {'regions':[{'unit_id':'EEZ_001'}, {'unit_id':'HS_018'}], 'articles':[copy.deepcopy(old_article)],
             'curated_region_ids':['EEZ_001']}
    fresh['articles'][0]['material_files'] = [{'sha256':'abc', 'role':'main', 'relative_path':'research/downloads/paper.pdf'}]
    fresh['articles'][0].pop('footprint_key')
    path = tmp_path / 'PPRAtlas/data/catalog.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(old), encoding='utf-8')
    archive = tmp_path / 'PPRAtlas/archive/regions/EEZ_001/source/paper.pdf'
    archive.parent.mkdir(parents=True)
    archive.write_bytes(b'verified existing scientific bytes')
    return old, fresh, path, archive


def test_refresh_is_repeatable_and_preserves_localized_material_and_footprint(tmp_path, monkeypatch):
    import refresh_atlas_catalog as module
    old, fresh, path, archive = fixture_catalogs(tmp_path)
    monkeypatch.setattr(module, 'build_catalog', lambda root: copy.deepcopy(fresh))
    before = archive.stat().st_mtime_ns
    for _ in range(2):
        result = module.refresh_catalog(tmp_path)
        assert result['regions'] == fresh['regions']
        assert result['articles'][0]['material_files'] == old['articles'][0]['material_files']
        assert result['articles'][0]['footprint_key'] == old['articles'][0]['footprint_key']
        assert json.loads(path.read_text(encoding='utf-8')) == result
        assert archive.stat().st_mtime_ns == before
        assert archive.read_bytes() == b'verified existing scientific bytes'


@pytest.mark.parametrize('change', ['source_hash', 'geometry', 'assignment'])
def test_refresh_rejects_changed_archive_evidence_before_replacing_catalog(tmp_path, monkeypatch, change):
    import refresh_atlas_catalog as module
    _, fresh, path, _ = fixture_catalogs(tmp_path)
    original = path.read_bytes()
    if change == 'source_hash': fresh['articles'][0]['material_files'][0]['sha256'] = 'changed'
    elif change == 'geometry': fresh['articles'][0]['geometry'] = {'type':'Polygon', 'coordinates':[]}
    else: fresh['articles'][0]['article_id'] = 'different__EEZ_001'
    monkeypatch.setattr(module, 'build_catalog', lambda root: copy.deepcopy(fresh))
    with pytest.raises(ValueError, match='archive'):
        module.refresh_catalog(tmp_path)
    assert path.read_bytes() == original
