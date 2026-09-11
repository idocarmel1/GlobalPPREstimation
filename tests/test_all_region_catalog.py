"""Display membership is independent of the curated article archive."""
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'PPRAtlas'))
from atlas.catalog import build_catalog
from atlas.render import render_map


@pytest.fixture(scope='module')
def catalog():
    return build_catalog(ROOT / 'PPRAtlas')


def test_catalog_displays_every_identity_preserving_curated_membership(catalog):
    identities = {u['unit_id'] for folder in ('global_output', 'eez_output')
                  for u in json.loads((ROOT / 'SeaAroundUsExtraction' / folder / 'tables/units.json').read_text())}
    selected = json.loads((ROOT / 'PPRAtlas/inputs/global_estimation.json').read_text())
    curated = {u['unit_id'] for u in selected['regions']}
    regions = {u['unit_id']: u for u in catalog['regions']}
    assert set(regions) == identities
    assert set(catalog['curated_region_ids']) == curated
    assert {u['unit_id'] for u in regions.values() if u['curated_archive_member']} == curated
    for source in selected['regions']:
        assert regions[source['unit_id']]['curated_ppr_rank'] == source['rank_selected_ppr']
    assert {a['unit_id'] for a in catalog['articles']} <= curated


def test_all_identities_have_geometry_and_missing_catch_stays_missing(catalog):
    regions = {u['unit_id']: u for u in catalog['regions']}
    assert 'HS_018' in regions
    for region in regions.values():
        assert not shape(region['geometry']).is_empty
        assert -180 <= region['marker_lon'] <= 180
        assert -90 <= region['marker_lat'] <= 90
    for year, annual in catalog['annual'].items():
        assert set(annual) == set(regions)
        for unit in ('HS_018', 'LME_064'):
            assert annual[unit][:2] == [None, None], (year, unit, annual[unit])
    assert regions['HS_018']['search_status'] == 'not_in_curated_archive'
    assert regions['HS_018']['article_count'] == 0


def test_all_rank_includes_missing_regions_and_top_rank_excludes_them(catalog):
    page = render_map(ROOT / 'PPRAtlas', catalog)
    assert '<option value="all" selected>All 366</option>' in page
    assert '167 Selected Ecosystems' not in page
    assert '${r.curated_archive_member?' in page
    assert 'Article search outside curated archive' in page
    function = re.search(r'function passRegion\(r\)\{[^\n]+', page).group(0)
    script = """
const assert = require('node:assert/strict');
const controls = {rankFilter:'all',typeFilter:'all',downloadFilter:'all',search:''};
const document = {querySelector:id=>({value:controls[id.slice(1)]})};
const regionHasDownload=()=>false, byUnit={};
FUNCTION
const absent={unit_id:'HS_018',region_name:'Arctic Sea',region_type:'High Seas',ppr_rank:null};
assert.equal(passRegion(absent),true);
controls.rankFilter='100';assert.equal(passRegion(absent),false);
assert.equal(passRegion({...absent,ppr_rank:100}),true);
assert.equal(passRegion({...absent,ppr_rank:101}),false);
controls.rankFilter='all';controls.typeFilter='EEZ';assert.equal(passRegion(absent),false);
""".replace('FUNCTION', function)
    subprocess.run(['node', '-e', script], check=True, capture_output=True, text=True)


def test_catalog_refresh_accepts_existing_verified_archive_without_writes(catalog, monkeypatch):
    sys.path.insert(0, str(ROOT / 'tools'))
    import refresh_atlas_catalog as module
    writes=[]
    monkeypatch.setattr(module, 'build_catalog', lambda root: catalog)
    monkeypatch.setattr(module, 'write_text_atomic', lambda path, value: writes.append((path,value)))
    result=module.refresh_catalog(ROOT)
    assert len(result['regions'])==366
    assert len(writes)==1
    assert writes[0][0]==ROOT/'PPRAtlas/data/catalog.json'
    assert all(a['footprint_key'] for a in result['articles'])
    assert all(f['relative_path'].startswith(a['article_dir']) for a in result['articles'] for f in a['material_files'])
