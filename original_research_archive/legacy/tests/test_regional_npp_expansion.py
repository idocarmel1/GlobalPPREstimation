"""Publication safeguards for the independent all-identity NPP extension."""
import csv
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('expand_regional_npp', Path(__file__).resolve().parents[1] / 'tools/expand_regional_npp.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def test_old_rows_keep_every_field_string():
    old = [{'unit_id': 'EEZ_001', 'year': '2019', 'value': '1.0000000000000002', 'status': 'complete'}]
    new = [{'unit_id': 'EEZ_002', 'year': '2019', 'value': '2', 'status': 'partial'}]
    result = m.merge_rows(old, new)
    assert result[0] == old[0]
    assert m.preservation_report(old, result)['preserved_rows'] == 1


def test_merge_refuses_replacement_even_if_numerically_equal():
    old = [{'unit_id': 'EEZ_001', 'year': '2019', 'value': '1.0'}]
    with pytest.raises(ValueError, match='existing'):
        m.merge_rows(old, [{'unit_id': 'EEZ_001', 'year': '2019', 'value': '1'}])


def test_preservation_fails_on_missing_row_or_changed_provenance():
    old = [{'unit_id': 'EEZ_001', 'year': '2019', 'provenance': 'original'}]
    for result in ([], [{**old[0], 'provenance': 'other'}]):
        with pytest.raises(ValueError, match='preserv'):
            m.preservation_report(old, result)


def test_source_path_cannot_escape_raw_directory(tmp_path):
    with pytest.raises(ValueError):
        m.source_file(tmp_path, 'NPPExtraction/data/raw/../../secret')


def test_record_retains_true_zero_but_no_water_is_missing():
    source = {'region_id': 2, 'ensemble_basis': 'common mask', 'water_area_km2': 3, 'scaled_antoinemorel_tC_yr': 0}
    result = m.annual_record(source, 1998, ['antoinemorel'], [1998, 1999, 2000], 'key', 'path')
    assert result['npp_antoinemorel_tC_yr'] == 0
    assert result['n_models'] == 1
    assert result['ens_median_tC_yr'] == 0
    missing = m.annual_record({**source, 'water_area_km2': 0}, 1998, ['antoinemorel'], [1998], 'key', 'path')
    assert missing['npp_antoinemorel_tC_yr'] is None
    assert missing['status'] == 'missing'


def test_incomplete_publication_is_refused():
    rows = [{'unit_id': 'EEZ_002', 'year': 1998, 'status': 'partial'}]
    with pytest.raises(ValueError, match='incomplete'):
        m.validate_new_rows(rows, [('EEZ_002', 1998), ('EEZ_002', 1999)], [1998, 1999])
    with pytest.raises(ValueError, match='failed'):
        m.validate_new_rows([{**rows[0], 'status': 'failed'}], [('EEZ_002', 1998)], [1998])


def test_no_catch_identity_is_preserved_in_record():
    source = {'layer': 'highseas', 'region_id': 18, 'ensemble_basis': 'common mask',
              'water_area_km2': 3, 'scaled_antoinemorel_tC_yr': 12}
    result = m.annual_record(source, 1998, ['antoinemorel'], [1998], 'key', 'path')
    assert result['unit_id'] == 'HS_018'
    assert 'catch' not in result


def test_truncated_npz_cannot_be_reused(tmp_path):
    import numpy as np
    path = tmp_path / 'baseline.npz'
    np.savez(path, eez_carbon_g=np.ones((12, 2, 5)), eez_area_m2=np.ones((12, 2, 5)),
             eez_mean_year_g=np.ones((12, 2)), eez_anomaly_factor=np.ones((12, 2)),
             eez_polygon_area_km2=np.ones(2), eez_region_id=np.array([1, 2]), eez_title=np.array(['one', 'two']))
    assert m.complete_checkpoint(path, 'baseline', layers=['eez'])
    path.write_bytes(path.read_bytes()[:30])
    assert not m.complete_checkpoint(path, 'baseline', layers=['eez'])


def test_original_unpublished_cell_uses_original_model_values():
    result = m.normalize_original_record({'unit_id': 'HS_067', 'year': 2008,
                'status': 'complete', 'provenance': 'original-year-provenance',
                'npp_antoinemorel_tC_yr': 1.23456789012345,
                'npp_vgpm_tC_yr': 3.0, 'npp_eppley_tC_yr': 2.0})
    assert result['npp_antoinemorel_tC_yr'] == 1.23456789012345
    assert result['ens_median_tC_yr'] == 2
    assert result['provenance'] == 'original-year-provenance'
    assert result['available_models'] == 'antoinemorel;vgpm;eppley'


def test_publication_writes_only_additions_and_keeps_no_catch_legacy(tmp_path, monkeypatch):
    output = tmp_path / m.OUTPUT
    output.mkdir(parents=True)
    canonical = tmp_path / 'NPPExtraction/output/annual_npp.csv'
    old = [{'unit_id': 'EEZ_001', 'year': '1998', 'status': 'partial', 'npp_antoinemorel_tC_yr': '1.0000000000000002',
            'provenance': 'original', 'config_key': 'original'}]
    for path in (canonical, output / 'annual_before.csv'):
        with path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(old[0]))
            writer.writeheader()
            writer.writerows(old)
    plan = {'before_path': (m.OUTPUT / 'annual_before.csv').as_posix(),
            'before_sha256': m.digest(canonical), 'geometries': {}, 'years': [1998],
            'grid': [('HS_018', 1998)], 'target_units': [{'unit_id': 'HS_018'}],
            'legacy_2019_preserved': {'path': 'unchanged-legacy.csv'}, 'npp_only_units': ['HS_018'],
            'reused_original_records': [], 'code_sha256': {},
            'source_runs': {'1998': {'path': 'source.json', 'sha256': 'source-hash', 'downloads': [], 'config': {'year': 1998}}}}
    m.atomic_json(output / 'plan.json', plan)
    write_completed_fixture(tmp_path, plan, [{'unit_id': 'HS_018', 'year': 1998,
                                             'status': 'partial', 'npp_antoinemorel_tC_yr': 2}])
    monkeypatch.setattr(m, 'verify_frozen', lambda *_: None)
    proof = m.publish(tmp_path)
    assert proof['preserved_rows'] == 1
    assert proof['new_rows'] == 1
    assert m.rows(canonical)[0] == old[0]
    assert m.rows(canonical)[1]['unit_id'] == 'HS_018'
    assert m.publish(tmp_path) == proof


def test_publish_rejects_stale_output_even_with_valid_output_hash(tmp_path):
    """Review reproduction: a valid current plan cannot bless an obsolete run."""
    output = tmp_path / m.OUTPUT
    output.mkdir(parents=True)
    (tmp_path / 'tools').mkdir()
    shutil.copyfile(SPEC.origin, tmp_path / 'tools/expand_regional_npp.py')
    canonical = tmp_path / 'NPPExtraction/output/annual_npp.csv'
    canonical.write_text('unit_id,year,status,npp_antoinemorel_tC_yr\nEEZ_001,1998,partial,1\n')
    shutil.copyfile(canonical, output / 'annual_before.csv')
    legacy = tmp_path / 'legacy.csv'
    legacy.write_text('legacy bytes')
    source = tmp_path / 'source.json'
    source.write_text('{}')
    plan = {'before_path': (m.OUTPUT / 'annual_before.csv').as_posix(),
            'before_sha256': m.digest(canonical), 'geometries': {}, 'years': [1998],
            'grid': [('EEZ_002', 1998)], 'target_units': [{'unit_id': 'EEZ_002'}],
            'legacy_2019_preserved': {'path': 'legacy.csv', 'sha256': m.digest(legacy)},
            'npp_only_units': [], 'reused_original_records': [], 'reused_original_sources': [],
            'source_runs': {'1998': {'path': 'source.json', 'sha256': m.digest(source), 'config': {'year': 1998}, 'downloads': []}},
            'code_sha256': m.code_hashes(tmp_path)}
    m.atomic_json(output / 'plan.json', plan)
    directory = output / 'years/1998/OLD_RUN'
    m.atomic_json(directory / 'annual_records.json', [{'unit_id': 'EEZ_002', 'year': 1998,
                  'status': 'partial', 'npp_antoinemorel_tC_yr': 999}])
    m.atomic_json(directory / 'provenance.json', {
        'runtime_code': {'sha256': {'old.py': 'wrong'}},
        'source_configuration': {'path': 'obsolete.json', 'sha256': 'wrong'},
        'geometries': {'wrong': {}}, 'outputs': [{'path': (directory / 'annual_records.json').relative_to(tmp_path).as_posix(),
        'sha256': m.digest(directory / 'annual_records.json')}]})
    m.verify_frozen(tmp_path, plan)
    before = canonical.read_bytes()
    with pytest.raises(ValueError, match='incomplete|stale|identity'):
        m.publish(tmp_path)
    assert canonical.read_bytes() == before


def write_completed_fixture(root, plan, records):
    inputs, key = m.expected_year_identity(root, plan, 1998)
    directory = root / m.OUTPUT / 'years/1998' / key
    records = [{**r, 'config_key': key, 'provenance': (directory / 'provenance.json').relative_to(root).as_posix()} for r in records]
    m.atomic_json(directory / 'annual_records.json', records)
    for name in ('baseline_by_region', 'baseline_monthly', 'ensemble_by_region'):
        (directory / f'npp_1998_{name}.csv').write_text('fixture ledger\n')
    files = [directory / 'annual_records.json', *directory.glob('*.csv')]
    provenance = m.expected_year_provenance(root, plan, 1998, key, inputs)
    provenance['outputs'] = [{'path': p.relative_to(root).as_posix(), 'sha256': m.digest(p)} for p in files]
    m.atomic_json(directory / 'provenance.json', provenance)
    return directory


@pytest.mark.parametrize('field', ['runtime_code', 'geometries', 'source_configuration', 'config', 'inputs', 'outputs'])
def test_current_key_also_requires_matching_provenance(tmp_path, field):
    plan = {'geometries': {}, 'code_sha256': {}, 'grid': [('EEZ_002', 1998)],
            'source_runs': {'1998': {'path': 'source.json', 'sha256': 'source-hash', 'downloads': [], 'config': {'year': 1998}}}}
    directory = write_completed_fixture(tmp_path, plan, [{'unit_id': 'EEZ_002', 'year': 1998, 'status': 'partial'}])
    assert m.completed_year_records(tmp_path, plan, 1998)[0]['unit_id'] == 'EEZ_002'
    path = directory / 'provenance.json'
    provenance = json.loads(path.read_text())
    provenance[field] = [] if field == 'outputs' else {'old': 'wrong'}
    m.atomic_json(path, provenance)
    with pytest.raises(ValueError, match='identity|output set'):
        m.completed_year_records(tmp_path, plan, 1998)


def test_valid_zip_with_missing_arrays_or_wrong_shape_is_not_complete(tmp_path):
    import numpy as np
    path = tmp_path / 'baseline.npz'
    np.savez(path, eez_carbon_g=np.ones((12, 2, 5)))
    assert not m.complete_checkpoint(path, 'baseline', layers=['eez'])
    arrays = {'eez_carbon_g': np.ones((12, 2, 5)), 'eez_area_m2': np.ones((12, 2, 5)),
              'eez_mean_year_g': np.ones((12, 2)), 'eez_anomaly_factor': np.ones((12, 2)),
              'eez_polygon_area_km2': np.ones(2), 'eez_region_id': np.array([1, 2]), 'eez_title': np.array(['one', 'two'])}
    np.savez(path, **arrays)
    assert m.complete_checkpoint(path, 'baseline', layers=['eez'])
    arrays['eez_area_m2'] = np.ones((11, 2, 5))
    np.savez(path, **arrays)
    assert not m.complete_checkpoint(path, 'baseline', layers=['eez'])


def test_ensemble_and_coverage_require_all_members(tmp_path):
    import numpy as np
    path = tmp_path / 'ensemble.npz'
    arrays = {'eez_common_area': np.ones((12, 2)), 'eez_region_id': np.array([1, 2]), 'eez_title': np.array(['one', 'two'])}
    np.savez(path, **arrays)
    assert not m.complete_checkpoint(path, 'ensemble', layers=['eez'], models=['antoinemorel'])
    arrays.update({f'eez_{prefix}_antoinemorel': np.ones((12, 2)) for prefix in ('common', 'own', 'own_area')})
    np.savez(path, **arrays)
    assert m.complete_checkpoint(path, 'ensemble', layers=['eez'], models=['antoinemorel'])
    path = tmp_path / 'coverage.npz'
    coverage = {'cid': np.array([1]), 'cov': np.array([.5]), 'ridx': np.array([0]),
                'region_id': np.array([1]), 'title': np.array(['one']), 'grid': np.array(['4km', '4320', '8640'])}
    np.savez(path, **coverage)
    assert m.complete_checkpoint(path, 'coverage', grid='4km')
    coverage.pop('title')
    np.savez(path, **coverage)
    assert not m.complete_checkpoint(path, 'coverage', grid='4km')
