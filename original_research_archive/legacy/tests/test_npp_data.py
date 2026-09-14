import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_annual_lookup_does_not_repeat_2019(tmp_path):
    from npp_data import load_npp, npp_for_year
    write_csv(tmp_path / 'NPPExtraction/output/annual_npp.csv', [
        {'unit_id': 'LME_034', 'year': 1950, 'ens_median_tC_yr': '', 'status': 'outside_source_coverage'},
        {'unit_id': 'LME_034', 'year': 2018, 'ens_median_tC_yr': '100', 'status': 'ok'},
        {'unit_id': 'LME_034', 'year': 2019, 'ens_median_tC_yr': '200', 'status': 'ok'},
    ])
    data = load_npp(tmp_path)['LME_034']
    assert npp_for_year(data, 1950)['ens_median_tC_yr'] is None
    assert npp_for_year(data, 2018)['ens_median_tC_yr'] == 100
    assert npp_for_year(data, 2019)['ens_median_tC_yr'] == 200
    assert npp_for_year(data, 2020) == {}


def test_legacy_is_only_a_2019_record(tmp_path):
    from npp_data import load_npp, npp_for_year
    write_csv(tmp_path / 'NPPExtraction/NPP_2019_filled_SAU_regions.csv', [
        {'layer': 'lme', 'region_id': 34, 'ens_median_tC_yr': '100', 'npp_cafe_tC_yr': '0'},
    ])
    data = load_npp(tmp_path)['LME_034']
    assert data['ens_median_tC_yr'] == 100
    assert npp_for_year(data, 2019)['npp_cafe_tC_yr'] == 0
    assert npp_for_year(data, 1950) == {}


def test_canonical_missing_overrides_legacy_value(tmp_path):
    from npp_data import load_npp, npp_for_year
    write_csv(tmp_path / 'NPPExtraction/NPP_2019_filled_SAU_regions.csv', [
        {'layer': 'lme', 'region_id': 34, 'ens_median_tC_yr': '100', 'scaled_median_tC_yr': '300'},
    ])
    write_csv(tmp_path / 'NPPExtraction/output/annual_npp.csv', [
        {'unit_id': 'LME_034', 'year': 2019, 'ens_median_tC_yr': '', 'status': 'failed'},
    ])
    assert npp_for_year(load_npp(tmp_path)['LME_034'], 2019)['ens_median_tC_yr'] is None


def test_duplicate_or_invalid_annual_values_rejected(tmp_path):
    from npp_data import load_npp
    path = tmp_path / 'NPPExtraction/output/annual_npp.csv'
    row = {'unit_id': 'LME_034', 'year': 2019, 'ens_median_tC_yr': '100'}
    write_csv(path, [row, row])
    with pytest.raises(ValueError, match='Duplicate'):
        load_npp(tmp_path)
    for value in ['-1', 'NaN', 'inf', 'bad']:
        write_csv(path, [{**row, 'ens_median_tC_yr': value}])
        with pytest.raises(ValueError):
            load_npp(tmp_path)


def test_annual_arrays_keep_missing_years_and_metadata(tmp_path):
    from npp_data import annual_arrays, annual_metadata
    record = {'annual': {'2000': {'npp_cafe_tC_yr': 10, 'status': 'ok', 'provenance': 'source'}}}
    assert annual_arrays(record, [1999, 2000, 2001])['npp_cafe_tC_yr'] == [None, 10, None]
    assert annual_metadata(record)['2000']['provenance'] == 'source'


def test_legacy_scaled_columns_supply_full_regional_estimates(tmp_path):
    from npp_data import load_npp, npp_for_year, annual_metadata, LEGACY_PATH
    row = {'layer': 'lme', 'region_id': 34, 'water_area_km2': '123'}
    expected = {}
    for i, model in enumerate(('antoinemorel', 'vgpm', 'eppley', 'cbpm', 'cafe'), 1):
        row[f'npp_{model}_tC_yr'] = i * 10
        row[f'scaled_{model}_tC_yr'] = i * 100
        expected[f'npp_{model}_tC_yr'] = i * 100
    for label, common, scaled in [('median', 30, 300), ('min', 10, 100), ('max', 50, 500)]:
        row[f'ens_{label}_tC_yr'] = common
        row[f'scaled_{label}_tC_yr'] = scaled
        expected[f'ens_{label}_tC_yr'] = scaled
    write_csv(tmp_path / LEGACY_PATH, [row])
    data = load_npp(tmp_path)['LME_034']
    annual = npp_for_year(data, 2019)
    assert {key: annual[key] for key in expected} == expected
    assert annual['water_area_km2'] == 123
    assert annual['provenance'] == LEGACY_PATH
    assert 'scaled_' in annual_metadata(data)['2019']['method']
    assert 'regional' in annual['reason']


def test_legacy_scaled_schema_preserves_blank_and_absent_scaled_fields(tmp_path):
    from npp_data import load_npp, npp_for_year, LEGACY_PATH
    write_csv(tmp_path / LEGACY_PATH, [{
        'layer': 'lme', 'region_id': 34, 'ens_median_tC_yr': 100,
        'npp_cafe_tC_yr': 100, 'npp_cbpm_tC_yr': 100, 'npp_vgpm_tC_yr': 100,
        'scaled_median_tC_yr': '', 'scaled_cafe_tC_yr': '', 'scaled_vgpm_tC_yr': 0,
    }])
    annual = npp_for_year(load_npp(tmp_path)['LME_034'], 2019)
    assert annual['ens_median_tC_yr'] is None
    assert annual['npp_cafe_tC_yr'] is None
    assert annual['npp_cbpm_tC_yr'] is None
    assert annual['npp_vgpm_tC_yr'] == 0


def test_canonical_values_are_not_scaled_again_or_replaced_by_scaled_named_columns(tmp_path):
    from npp_data import load_npp, npp_for_year, LEGACY_PATH
    write_csv(tmp_path / LEGACY_PATH, [{
        'layer': 'lme', 'region_id': 34, 'ens_median_tC_yr': 10, 'scaled_median_tC_yr': 100,
    }])
    write_csv(tmp_path / 'NPPExtraction/output/annual_npp.csv', [{
        'unit_id': 'LME_034', 'year': 2019, 'npp_antoinemorel_tC_yr': 200,
        'npp_cafe_tC_yr': '', 'ens_median_tC_yr': 200,
        'scaled_antoinemorel_tC_yr': 9999, 'scaled_cafe_tC_yr': 9999,
        'scaled_median_tC_yr': 9999, 'baseline_central_tC_yr': 1000,
        'provenance': 'canonical source', 'status': 'complete',
    }])
    annual = npp_for_year(load_npp(tmp_path)['LME_034'], 2019)
    assert annual['npp_antoinemorel_tC_yr'] == 200
    assert annual['ens_median_tC_yr'] == 200
    assert annual['npp_cafe_tC_yr'] is None
    assert annual['provenance'] == 'canonical source'
