"""Historical regressions: year isolation, archived catch integrity and availability."""
import importlib.util
import json
import zipfile

import numpy as np
import pandas as pd
import pytest

from ppr_pipeline.calculations import aggregate_groups


def history():
    assert importlib.util.find_spec('ppr_pipeline.history'), 'Historical calculation feature is missing'
    import ppr_pipeline.history as module
    return module


def raw_rows():
    return pd.DataFrame([
        ['Area', 'LME', 1950, 'Low fish', 'Low', 'Mixed', 'Mixed', 'Landings', 'Reported', 1.0],
        ['Area', 'LME', 1950, 'High fish', 'High', 'Mixed', 'Mixed', 'Discards', 'Unreported', 1.0],
        ['Area', 'LME', 1951, 'Low fish', 'Low', 'Mixed', 'Mixed', 'Landings', 'Unreported', 2.0],
        ['Area', 'LME', 1951, 'High fish', 'High', 'Mixed', 'Mixed', 'Landings', 'Reported', 0.0],
    ], columns=['area_name', 'area_type', 'year', 'scientific_name', 'common_name',
                'functional_group', 'commercial_group', 'catch_type', 'reporting_status', 'tonnes'])


def archive(tmp_path, frame, name='test.zip'):
    path = tmp_path / name
    with zipfile.ZipFile(path, 'w') as zf:
        zf.writestr('catch.csv', frame.to_csv(index=False))
    return path


def standardized_fixture(tmp_path):
    module = history()
    frame, audit = module.stream_standardized_archive(archive(tmp_path, raw_rows()), chunksize=2)
    frame['unit_id'] = 'LME_001'
    frame['cohort'] = 'lme_highseas'
    supplement = pd.DataFrame({'scientific_name': ['Low fish', 'High fish'], 'tl': [2.0, 4.0]})
    static = module.match_history_static(frame, supplement, pd.DataFrame())
    species, commercial, functional = module.finish_history(static, module.historical_group_means([static]))
    return species, commercial, functional, audit


def test_stream_keeps_year_and_reconciles_category_totals(tmp_path):
    # Dropping year from the grouping or dropping a second chunk must fail.
    module = history()
    frame, audit = module.stream_standardized_archive(archive(tmp_path, raw_rows()), chunksize=1)
    assert frame.groupby('year').catch_tonnes.sum().to_dict() == {1950: 2.0, 1951: 2.0}
    assert frame.landings_tonnes.sum() == 3.0
    assert frame.discards_tonnes.sum() == 1.0
    assert frame.reported_tonnes.sum() == 1.0
    assert frame.unreported_tonnes.sum() == 3.0
    assert audit.reconciled.all()
    assert audit.raw_rows_selected.tolist() == [2, 2]


def test_two_year_ppr_is_species_first_without_carbon_divisor(tmp_path):
    species, commercial, functional, _ = standardized_fixture(tmp_path)
    assert species.groupby('year').ppr.sum().to_dict() == {1950: 1010.0, 1951: 20.0}
    for groups in (commercial, functional):
        assert groups.ppr_correct.tolist() == [1010.0, 20.0]
        assert groups.ppr_jensen.tolist() == pytest.approx([200.0, 20.0])
        assert (groups.ppr_correct + 1e-9 >= groups.ppr_jensen).all()


def test_historical_groups_match_approved_group_calculation(tmp_path):
    species, commercial, functional, _ = standardized_fixture(tmp_path)
    for actual, column in [(commercial, 'commercial_group'), (functional, 'functional_group')]:
        for year, part in species.groupby('year'):
            expected = aggregate_groups(part, column)
            pd.testing.assert_frame_equal(actual[actual.year == year].drop(columns='year').reset_index(drop=True),
                                          expected, check_dtype=False, atol=1e-10, rtol=1e-12)


def test_fallback_isolated_by_year_and_release_cohort():
    module = history()
    frame = pd.DataFrame({
        'unit_id': ['LME_001'] * 4 + ['EEZ_001'] * 2,
        'cohort': ['lme_highseas'] * 4 + ['eez'] * 2,
        'year': [1950, 1950, 1951, 1951, 1950, 1950],
        'taxon': ['Low fish', 'Unknown', 'High fish', 'Unknown', 'High fish', 'Unknown'],
        'commercial_group': ['Mixed'] * 6, 'functional_group': ['Mixed'] * 6,
        'catch_tonnes': [1.0] * 6,
    })
    supplement = pd.DataFrame({'scientific_name': ['Low fish', 'High fish'], 'tl': [2.0, 4.0]})
    static = module.match_history_static(frame, supplement, pd.DataFrame())
    actual, _, _ = module.finish_history(static, module.historical_group_means([static]))
    assert actual.loc[actual.taxon == 'Unknown', 'tl'].tolist() == [2.0, 4.0, 4.0]
    assert actual.loc[actual.taxon == 'Unknown', 'match_method'].tolist() == ['commercial_group_mean'] * 3


def test_fallback_means_deduplicate_taxa_across_region_rows():
    module = history()
    frame = pd.DataFrame({'unit_id': ['LME_001', 'LME_002', 'LME_003', 'LME_001'],
                          'cohort': ['lme_highseas'] * 4, 'year': [1950] * 4,
                          'taxon': ['Low fish', 'Low fish', 'High fish', 'Unknown'],
                          'commercial_group': ['Mixed'] * 4, 'functional_group': ['Mixed'] * 4,
                          'catch_tonnes': [1.0] * 4})
    supplement = pd.DataFrame({'scientific_name': ['Low fish', 'High fish'], 'tl': [2.0, 4.0]})
    static = module.match_history_static(frame, supplement, pd.DataFrame())
    actual, _, _ = module.finish_history(static, module.historical_group_means([static]))
    assert actual.loc[actual.taxon == 'Unknown', 'tl'].iloc[0] == 3.0


def test_missing_and_empty_are_not_observed_zero(tmp_path):
    module = history()
    zero = raw_rows().iloc[[3]].copy()
    frame, audit = module.stream_standardized_archive(archive(tmp_path, zero), chunksize=1)
    frame['unit_id'] = 'LME_001'
    frame['cohort'] = 'lme_highseas'
    static = module.match_history_static(frame, pd.DataFrame({'scientific_name': ['High fish'], 'tl': [4.0]}), pd.DataFrame())
    species, commercial, functional = module.finish_history(static, module.historical_group_means([static]))
    unit = {'unit_id': 'LME_001', 'name': 'Area', 'sau_region': 'lme'}
    annual = module.summarize_history(unit, [1950, 1951], species, commercial, functional, {1951})
    assert annual.source_data_status.tolist() == ['missing_year', 'available']
    assert np.isnan(annual.ppr_species.iloc[0])
    assert annual.ppr_species.iloc[1] == 0.0
    empty = module.summarize_history(unit, [1950, 1951], species.iloc[:0], commercial.iloc[:0], functional.iloc[:0], set())
    assert empty.source_data_status.tolist() == ['empty_catch_archive'] * 2
    assert empty.ppr_species.isna().all()


def test_negative_tonnes_rejected_and_zero_byte_archive_supported(tmp_path):
    module = history()
    frame = raw_rows()
    frame.loc[0, 'tonnes'] = -1
    with pytest.raises(ValueError, match='negative'):
        module.stream_standardized_archive(archive(tmp_path, frame))
    empty = tmp_path / 'empty.zip'
    with zipfile.ZipFile(empty, 'w') as zf:
        zf.writestr('catch.csv', '')
    standardized, audit = module.stream_standardized_archive(empty)
    assert standardized.empty
    assert audit.empty


def test_pipeline_runs_resumes_and_marks_missing_data(tmp_path):
    module = history()
    root = tmp_path / 'project'
    raw = root / 'raw_data/SAU_downloads'
    raw.mkdir(parents=True)
    (root / 'spatial').mkdir()
    (root / 'input').mkdir()
    pd.DataFrame([{'unit_id': 'LME_001', 'name': 'Area', 'sau_region': 'lme', 'sau_region_id': 1}]).to_csv(root / 'spatial/spatial_units.csv', index=False)
    pd.DataFrame(columns=['unit_id', 'name', 'sau_region', 'sau_region_id']).to_csv(root / 'spatial/eez_units.csv', index=False)
    pd.DataFrame({'scientific_name': ['Low fish', 'High fish'], 'tl': [2.0, 4.0]}).to_csv(root / 'input/trophic_levels_2020.csv', index=False)
    archive(raw, raw_rows(), name='LME_001-catch.zip')
    (raw / 'LME_001-exploited.json').write_text(json.dumps({'data': []}))
    result = module.run_history_pipeline(root, chunksize=1, progress=None)
    assert result['summary'].ppr_species.tolist() == [1010.0, 20.0]
    assert result['metadata']['all_checks_passed']
    annual_file = root / 'history_output/tables/regions/LME_001/species.csv.gz'
    modified = annual_file.stat().st_mtime_ns
    rerun = module.run_history_pipeline(root, chunksize=2, progress=None)
    assert annual_file.stat().st_mtime_ns == modified
    assert rerun['metadata']['resumed_units'] == 1
    records = json.loads((root / 'history_output/tables/annual_regions.json').read_text())
    assert records[0]['ppr_species'] == 1010.0


def test_reference_check_detects_wrong_ppr_but_documents_legacy_empty_zero(tmp_path):
    # An accidental unconditional pass in the reproduction audit must fail.
    module = history()
    first = dict.fromkeys(module.ANNUAL_COLUMNS, 0.0)
    first.update(unit_id='LME_001', region_name='Area', region_type='LME', year=2019,
                 source_data_status='available', ppr_species=1010.0)
    empty = dict(first, unit_id='EEZ_001', region_type='EEZ', ppr_species=0.0)
    reference = pd.DataFrame([first, empty])
    reference_path = tmp_path / 'reference.csv'
    reference.to_csv(reference_path, index=False)
    actual = reference.copy()
    actual.loc[0, 'ppr_species'] = 1011.0
    actual.loc[1, 'source_data_status'] = 'empty_catch_archive'
    actual.loc[1, module.ANNUAL_COLUMNS[4:-1]] = np.nan
    audit = module._compare_reference(actual, reference_path)
    failed = audit.loc[~audit.passed]
    assert failed[['unit_id', 'metric']].to_dict('records') == [{'unit_id': 'LME_001', 'metric': 'ppr_species'}]
    assert set(audit.loc[audit.unit_id == 'EEZ_001', 'comparison_status']) == {'legacy_empty_zero_to_missing'}


def test_functional_fallback_does_not_reuse_commercial_imputed_values():
    module = history()
    frame = pd.DataFrame({'unit_id': ['LME_001'] * 3, 'cohort': ['lme_highseas'] * 3,
                          'year': [1950] * 3, 'taxon': ['Low fish', 'Unknown A', 'Unknown B'],
                          'commercial_group': ['A', 'A', 'B'], 'functional_group': ['X', 'Y', 'Y'],
                          'catch_tonnes': [1.0] * 3})
    supplement = pd.DataFrame({'scientific_name': ['Low fish'], 'tl': [2.0]})
    static = module.match_history_static(frame, supplement, pd.DataFrame())
    result, _, _ = module.finish_history(static, module.historical_group_means([static]))
    assert result.loc[result.taxon == 'Unknown A', 'tl'].iloc[0] == 2.0
    assert result.loc[result.taxon == 'Unknown B', 'tl'].isna().all()
    assert result.loc[result.taxon == 'Unknown B', 'match_method'].iloc[0] == 'unmatched'


def test_metadata_failure_count_stays_zero_when_empty_archive_is_present(tmp_path):
    # Empty validation frames can coerce booleans to objects; ~True then equals -2.
    module = history()
    raw = tmp_path / 'raw_data/SAU_downloads'
    raw.mkdir(parents=True)
    (tmp_path / 'spatial').mkdir()
    (tmp_path / 'input').mkdir()
    pd.DataFrame([{'unit_id': 'LME_001', 'name': 'Area', 'sau_region': 'lme', 'sau_region_id': 1}]).to_csv(tmp_path / 'spatial/spatial_units.csv', index=False)
    pd.DataFrame([{'unit_id': 'EEZ_001', 'name': 'Empty', 'sau_region': 'eez', 'sau_region_id': 1}]).to_csv(tmp_path / 'spatial/eez_units.csv', index=False)
    pd.DataFrame({'scientific_name': ['Low fish', 'High fish'], 'tl': [2.0, 4.0]}).to_csv(tmp_path / 'input/trophic_levels_2020.csv', index=False)
    archive(raw, raw_rows(), name='LME_001-catch.zip')
    archive(raw, raw_rows().iloc[:0], name='EEZ_001-catch.zip')
    for unit_id in ['LME_001', 'EEZ_001']:
        (raw / f'{unit_id}-exploited.json').write_text(json.dumps({'data': []}))
    result = module.run_history_pipeline(tmp_path, progress=None)
    assert result['metadata']['validation_count'] == 14
    assert result['metadata']['validation_failures'] == 0
    assert result['metadata']['all_checks_passed']
