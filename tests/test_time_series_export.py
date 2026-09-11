"""Annual export must preserve missingness, verified status and source precision."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))


def exporter():
    path = ROOT / 'tools/build_time_series.py'
    assert path.exists(), 'The annual time-series exporter has not been implemented'
    spec = importlib.util.spec_from_file_location('build_time_series', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_missing_samples_do_not_become_zero_and_true_zero_is_retained():
    result = exporter().annual_method(
        [1950, 1951, 1952, 1953], [1950, 1951, 1952],
        [[2, 0, None], [7, 0, None]], [10, None], 'ok')
    assert result == {'status': 'ok', 'ppr': [20, 0, None, None],
                      'covered_catch': [2, 0, None, None]}


def test_failed_method_cannot_publish_finite_source_numbers():
    result = exporter().annual_method([1950], [1950], [[4]], [100], 'FAILED diagnostic')
    assert result == {'status': 'FAILED diagnostic', 'ppr': [None], 'covered_catch': [None]}


def test_simple_uses_each_taxon_tl_before_summing_and_keeps_total_catch():
    rows = [{'taxon': 'low', 'by_year': {1950: 2, 1951: 0}},
            {'taxon': 'high', 'by_year': {1950: 3, 1951: 0}},
            {'taxon': 'unknown', 'by_year': {1950: 5, 1951: 0}}]
    result = exporter().simple_annual(rows, [1950, 1951], {'low': 2, 'high': 4})
    assert result == {'ppr': [3020, 0], 'catch': [10, 0], 'covered_catch': [5, 0]}
    assert exporter().simple_annual(rows, [1950], {}) == {
        'ppr': [None], 'catch': [10], 'covered_catch': [None]}


def test_model_versions_and_scopes_keep_their_own_values_and_default_identity():
    def model(name, coefficient):
        return {'id': name, 'label': name, 'verified': True, 'source': name + '.xlsx',
                'workbook': 'model/' + name + '.xlsx', 'scopes': {
                    'all': {'methods': ['new_GE', 'simple trophic chain'],
                            'status': {'new_GE': 'ok', 'simple trophic chain': 'ok'},
                            'values': [[coefficient, 100]]},
                    'PP': {'methods': ['new_GE'], 'status': {'new_GE': 'ok'},
                           'values': [[coefficient / 2]]}}}
    source = {'years': [1950], 'taxa': ['a'], 'catch': [[2]],
              'models': [model('old', 10), model('new', 30)], 'default_model': 1}
    models, default = exporter().export_models(source, [1950, 1951])
    assert default == 'new'
    assert [m['id'] for m in models] == ['old', 'new']
    assert models[0]['scopes']['all']['methods']['new_GE']['ppr'] == [20, None]
    assert models[1]['scopes']['PP']['methods']['new_GE']['ppr'] == [30, None]
    assert 'simple trophic chain' not in models[0]['scopes']['all']['methods']


def test_catalog_includes_missing_identities_and_all_eez_units():
    identities, sets = exporter().load_identities(ROOT)
    presets = {s['id']: s['units'] for s in sets}
    assert len(identities) == 366
    assert identities['HS_018']['name'] == 'Arctic Sea'
    assert identities['LME_064']['name'] == 'Central Arctic Ocean'
    assert {k: len(presets[k]) for k in ('global', 'pilot', 'eez', 'atlas', 'all')} == {
        'global': 84, 'pilot': 10, 'eez': 282, 'atlas': 167, 'all': 366}


def test_changed_verified_source_is_rejected(tmp_path):
    path = tmp_path / 'source.xlsx'
    path.write_bytes(b'changed')
    with pytest.raises(ValueError, match='SHA-256 mismatch'):
        exporter().verified_hash(tmp_path, 'source.xlsx', '0' * 64)


def test_model_annual_rounding_matches_persisted_workbook_accumulation():
    network = json.loads((ROOT / 'PPRAtlas/data/network_ppr.json').read_text(encoding='utf-8'))
    unit = network['units']['LME_013']
    model = next(m for m in unit['models'] if m['verified'])
    scope = model['scopes']['all']
    column = scope['methods'].index('EwE_TE_EE')
    annual = exporter().annual_method([1968], unit['years'], unit['catch'],
                                      [row[column] for row in scope['values']], 'ok')
    # Independent literal from the persisted PPR by method / 1968 workbook cell.
    assert annual['ppr'] == [619773179.892]


def test_excel_decimal_precision_is_tolerated_but_numeric_changes_are_rejected():
    module = exporter()
    module.assert_annual_equal(10556726916726.766, 10556726916726.77, 'Source writer 16-digit storage')
    with pytest.raises(ValueError, match='annual total differs'):
        module.assert_annual_equal(10556726916727.766, 10556726916726.77, 'changed coefficient')


def test_graph_years_include_npp_records_without_a_matching_catch_year():
    assert exporter().graph_years({2000, 2001}, {
        'no_catch': {'annual': {'1998': {}, '2005': {}}},
        'legacy_only': {'annual': {'2019': {}}},
    }) == [1998, 2000, 2001, 2005, 2019]
