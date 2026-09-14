"""Independent simple-map input must preserve catch boundaries and missingness."""
import csv
import gzip
import hashlib
import importlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


def exporter():
    spec = importlib.util.find_spec('simple_atlas_data')
    assert spec is not None, 'Independent simple-map exporter is not implemented'
    return importlib.import_module('simple_atlas_data').export_simple_units


@pytest.fixture
def source_root(tmp_path):
    for directory, records in (
        ('global_output', [('LME_001', 'Example sea', 'LME'), ('HS_018', 'No catch', 'High Seas')]),
        ('eez_output', [('EEZ_001', 'Example EEZ', 'EEZ')]),
    ):
        table = tmp_path / 'SeaAroundUsExtraction' / directory / 'tables'
        table.mkdir(parents=True)
        (table / 'units.json').write_text(json.dumps([
            {'unit_id': unit, 'name': name, 'region_type': kind} for unit, name, kind in records
        ]), encoding='utf-8')
    write_catch(tmp_path, 'LME_001', [
        [2018, 'Known fish', '', 1.23456789, 1.13456789, .1],
        [2018, 'Fish NEI', '', 2., 1., 1.],
        [2019, 'Known fish', '', 0., 0., 0.],
        [2019, 'Fish NEI', '', 5., 5., 0.],
    ])
    write_catch(tmp_path, 'EEZ_001', [[2019, 'EEZ fish', '', 2., 1., 1.]])
    write_species(tmp_path, 'global_output', 'LME_001', [('Known fish', 3), ('Fish NEI', '')])
    write_species(tmp_path, 'eez_output', 'EEZ_001', [('EEZ fish', 2)])
    central = tmp_path / 'data/LME_001/LME_001.xlsx'
    central.parent.mkdir(parents=True)
    central.write_bytes(b'fixture workbook provenance only')
    return tmp_path


def write_catch(root, unit, rows):
    target = root / f'SeaAroundUsExtraction/data/catch_by_taxon_year/{unit}.csv.gz'
    target.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(target, 'wt', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['year', 'taxon', 'common_name', 'catch_tonnes', 'landings_tonnes', 'discards_tonnes'])
        writer.writerows(rows)


def write_species(root, directory, unit, rows):
    target = root / f'SeaAroundUsExtraction/{directory}/tables/regions/{unit}/species.csv'
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['taxon', 'tl'])
        writer.writerows(rows)


def test_all_identity_sets_export_without_article_or_model_inputs(source_root):
    units = exporter()(source_root)
    assert set(units) == {'LME_001', 'HS_018', 'EEZ_001'}
    assert units['EEZ_001']['simple']['ppr'] == [10.]
    assert units['EEZ_001']['name'] == 'Example EEZ'
    assert units['EEZ_001']['type'] == 'EEZ'
    assert 'models' not in units['EEZ_001']


def test_three_bases_keep_full_precision_and_zero_differs_from_missing_tl(source_root):
    unit = exporter()(source_root)['LME_001']
    assert unit['years'] == [2018, 2019]
    simple = unit['simple']
    assert simple['ppr'] == pytest.approx([113.456789, None])
    assert simple['covered_catch'] == [1.13456789, None]
    assert simple['catch'] == [2.13456789, 5.]
    assert simple['catch_bases']['catch']['ppr'] == pytest.approx([123.456789, None])
    assert simple['catch_bases']['discards']['ppr'] == [10., 0.]
    assert simple['unidentified_zero']['ppr'] == pytest.approx([113.456789, 0.])
    assert simple['unidentified_zero']['covered_catch'] == [2.13456789, 5.]
    assert simple['unidentified_simple']['ppr'] == simple['ppr']
    assert unit['unidentified']['catch_bases']['landings']['missing_simple_catch'] == [1., 5.]
    assert 'taxa' not in unit and 'landings' not in unit


def test_no_catch_keeps_identity_without_fabricating_years_or_zeroes(source_root):
    unit = exporter()(source_root)['HS_018']
    assert unit['years'] == []
    assert unit['simple']['ppr'] == unit['simple']['catch'] == []
    assert unit['catch_accounting']['classification_status'] == []
    assert unit['catch_accounting']['sha256'] is None
    assert 'catch' not in unit['sources']


def test_missing_classification_cannot_become_landings_zero(source_root):
    write_catch(source_root, 'EEZ_001', [[2019, 'EEZ fish', '', 2., '', '']])
    unit = exporter()(source_root)['EEZ_001']
    assert unit['simple']['ppr'] == [None]
    assert unit['simple']['catch'] == [None]
    assert unit['simple']['catch_bases']['catch']['ppr'] == [20.]
    assert unit['catch_accounting']['classification_status'] == ['missing_classification']


def test_provenance_points_only_to_real_sources_with_matching_bytes(source_root):
    unit = exporter()(source_root)['LME_001']
    assert set(unit['sources']) == {'catch', 'trophic_levels', 'workbook'}
    for key, relative in unit['sources'].items():
        assert unit['source_sha256'][key] == hashlib.sha256((source_root / relative).read_bytes()).hexdigest()
    assert unit['sources']['trophic_levels'].startswith('SeaAroundUsExtraction/global_output/')


def test_duplicate_identity_is_rejected_instead_of_silently_overwriting(source_root):
    path = source_root / 'SeaAroundUsExtraction/eez_output/tables/units.json'
    path.write_text('[{"unit_id":"LME_001","name":"duplicate","region_type":"EEZ"}]', encoding='utf-8')
    with pytest.raises(ValueError, match='Duplicate ecosystem identity'):
        exporter()(source_root)


def test_network_export_retains_pilot_subset_while_exposing_independent_units(source_root):
    import build_network_atlas
    (source_root / 'data/atlas_selection.json').write_text('{"units":{}}', encoding='utf-8')
    network = build_network_atlas.export_network(source_root)
    assert network['units'] == {}
    assert set(network.get('simple_units', {})) == {'LME_001', 'HS_018', 'EEZ_001'}
    assert network['npp_years'] == [2018, 2019]
