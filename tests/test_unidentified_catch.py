import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


def test_explicit_labels_only_and_reference_coefficients():
    from unidentified_catch import metadata
    rows = [
        {'taxon': 'Marine fishes not identified', 'common_name': 'Marine fishes nei', 'by_year': {2019: 3}},
        {'taxon': 'Scombridae', 'common_name': 'Mackerels', 'by_year': {2019: 7}},
        {'taxon': 'Residual crustaceans', 'common_name': 'Crustaceans NEI', 'by_year': {2019: 2}},
        {'taxon': 'Miscellaneous aquatic invertebrates', 'by_year': {2019: 5}},
    ]
    result = metadata(rows, [2018, 2019], {'Marine fishes not identified': 3})
    assert [r['name'] for r in result['taxa']] == ['Marine fishes not identified', 'Residual crustaceans']
    assert result['taxa'][0]['simple_sppr'] == 100
    assert result['taxa'][1]['simple_sppr'] is None
    assert result['catch'] == [0, 5]
    assert result['missing_simple_catch'] == [0, 2]


def test_alternates_keep_default_failure_and_scope_rules():
    from build_time_series import export_models
    scope = {'methods': ['M'], 'status': {'M': 'ok'}, 'values': [[10], [100], [None]]}
    source = {'years': [2019], 'taxa': ['named', 'unidentified', 'unknown nei'],
              'catch': [[2], [3], [4]], 'default_model': 0,
              'unidentified': {'taxa': [{'name': 'unidentified', 'simple_sppr': 20},
                                        {'name': 'unknown nei', 'simple_sppr': None}]},
              'models': [{'id': 'model', 'verified': True, 'scopes': {'all': scope, 'PP': scope}}]}
    model = export_models(source, [2019])[0][0]
    result = model['scopes']['all']['methods']['M']
    assert result['ppr'] == [320]
    assert result['unidentified_zero']['ppr'] == [20]
    assert result['unidentified_zero']['covered_catch'] == [9]
    assert result['unidentified_simple']['ppr'] == [80]
    assert result['unidentified_simple']['covered_catch'] == [5]
    assert model['scopes']['PP']['methods']['M']['unidentified_simple']['ppr'] == [None]
    scope['status']['M'] = 'FAILED'
    result = export_models(source, [2019])[0][0]['scopes']['all']['methods']['M']
    assert result['unidentified_zero']['ppr'] == [None]
    assert result['unidentified_simple']['ppr'] == [None]
    assert export_models(source, [2019])[0][0]['scopes']['PP']['methods']['M']['unidentified_simple']['status'] == 'FAILED'
    scope['status']['M'] = 'ok'
    del source['unidentified']
    result = export_models(source, [2019])[0][0]['scopes']['all']['methods']['M']
    assert result['ppr'] == [320]
    assert result['unidentified_zero']['ppr'] == [None]
    assert 'metadata is missing' in result['unidentified_zero']['status']


def test_zero_treatment_preserves_zero_years_and_all_catch_without_reference_tl():
    from unidentified_catch import metadata
    from build_time_series import simple_zero_annual
    rows = [{'taxon': 'Fishes nei', 'by_year': {2019: 4}}]
    years = [2018, 2019]
    result = simple_zero_annual(rows, years, {}, metadata(rows, years, {}))
    assert result == {'ppr': [0, 0], 'catch': [0, 4], 'covered_catch': [0, 4]}


def test_covered_catch_rounds_once_after_adding_all_eligible_taxa():
    from unidentified_catch import metadata
    from build_time_series import simple_zero_annual
    rows = [{'taxon': 'named', 'by_year': {2019: .0005}},
            {'taxon': 'Fishes nei', 'by_year': {2019: .0005}}]
    result = simple_zero_annual(rows, [2019], {'named': 3}, metadata(rows, [2019], {'named': 3}))
    assert result['covered_catch'] == result['catch'] == [.001]
