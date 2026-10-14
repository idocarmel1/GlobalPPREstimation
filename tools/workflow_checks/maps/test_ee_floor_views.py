"""Calculation assumptions and source/effective values stay model-specific."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.project_core.maps import original_atlas_data
from tools.project_core.maps.build_html import linked_layout
from tools.project_core.maps.ee_floor_layout import source_provenance_layout
from tools.project_core.calculations.regional import set_result_hash
from tools.project_core.workbooks.workbooks import input_hash, sha, write_book


def floor_tables(enabled=True, affected=True):
    return {
        'EE floor': (['field', 'value'], [
            ['use_ee_floor', enabled], ['ee_floor', .1],
            ['assumption', 'Hypothetical external nonfishery mortality sink'],
            ['affected_group_count', int(enabled and affected)],
            ['external_mortality_export_total', 1.5 if enabled and affected else 0.],
            ['provenance', 'Explicit calculation migration']]),
        'EE floor groups': (['group_seq', 'group_name', 'source_EE', 'source_M0',
            'EE_before_floor', 'M0_before_floor', 'EE_effective', 'M0_effective',
            'external_mortality_export', 'applied', 'reason'], [[
                1, 'fish group', .02, None, .025, 19.5,
                .1 if enabled and affected else .025, 18. if enabled and affected else 19.5,
                1.5 if enabled and affected else 0., enabled and affected,
                'EE below floor' if enabled and affected else 'floor disabled']])}


class EeFloorViewsTests(unittest.TestCase):
    def book(self, enabled=True, affected=True):
        flags = {'constructor': {'det_collapse_mode': 'auto', 'use_ee_floor': enabled, 'ee_floor': .1},
                 'calculation_engine_upgrade': 'ee_floor_v1', 'calculation_engine_sha256': 'e' * 64}
        return {
            'Overview': {'Settings': (['field', 'value'], [['effective_loader_flags', json.dumps(flags)]])},
            'Selected model groups': {'Groups': (['seq', 'group_name', 'ge', 'ee'], [[1, 'fish group', .2, .02]])},
            'Diagnostics': floor_tables(enabled, affected)}

    def test_detail_uses_saved_effective_ee_and_preserves_unknown_source_mortality(self):
        book = self.book(); before = copy.deepcopy(book)
        _, model = original_atlas_data.detail_from_book(book, 'LME_001', 'm')
        group = model['group_data']['groups'][0]
        self.assertEqual(group['ee'], .1)
        self.assertEqual(group['source_ee'], .02)
        self.assertIsNone(group['source_m0'])
        self.assertEqual(group['ee_before_floor'], .025)
        self.assertEqual(group['m0_before_floor'], 19.5)
        self.assertEqual(group['m0_effective'], 18.)
        self.assertEqual(group['external_mortality_export'], 1.5)
        self.assertAlmostEqual(group['te'], .02)
        self.assertEqual(book, before, 'Publishing effective values never rewrites the source table')

    def test_constructor_flags_are_exported_for_on_off_and_no_affected_groups(self):
        for enabled, affected in [(True, True), (True, False), (False, False)]:
            with self.subTest(enabled=enabled, affected=affected):
                _, model = original_atlas_data.detail_from_book(self.book(enabled, affected), 'LME_001', 'm')
                provenance = model.get('calculation_provenance', {})
                self.assertIs(provenance.get('use_ee_floor'), enabled)
                self.assertEqual(provenance.get('ee_floor'), .1)
                self.assertEqual(provenance.get('effective_loader_flags', {}).get('constructor', {}).get('use_ee_floor'), enabled)
                self.assertEqual(provenance.get('calculation_engine_upgrade'), 'ee_floor_v1')
                self.assertEqual(provenance.get('calculation_engine_sha256'), 'e' * 64)
                self.assertEqual(provenance.get('affected_group_count'), int(enabled and affected))
                self.assertEqual(provenance.get('external_mortality_export_total'), 1.5 if enabled and affected else 0.)

    def test_unrecorded_historical_floor_is_not_inferred_from_calculator_defaults(self):
        book = self.book(); book.pop('Overview'); book.pop('Diagnostics')
        _, model = original_atlas_data.detail_from_book(book, 'LME_001', 'm')
        self.assertNotIn('calculation_provenance', model)
        self.assertEqual(model['group_data']['groups'][0]['ee'], .02)

    def test_completed_mortality_is_not_relabelled_as_an_unknown_original_source(self):
        book = {'Selected model groups': {'Groups': (['group_name', 'ee', 'M0'], [['fish group', .02, 19.6]])}}
        _, model = original_atlas_data.detail_from_book(book, 'LME_001', 'm')
        group = model['group_data']['groups'][0]
        self.assertIsNone(group['source_m0'])
        self.assertEqual(group['m0_effective'], 19.6)

    def test_candidate_snapshot_carries_its_own_settings_to_both_payloads(self):
        from tools.workflow_checks.maps.test_candidate_method_publication import CandidatePublicationTests
        fixture = CandidatePublicationTests(); fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.book['Overview']['Settings'][1].extend(self.book()['Overview']['Settings'][1])
        fixture.book['Selected model groups']['Groups'][1][0][-1] = .02
        fixture.book['Diagnostics'] = floor_tables()
        for row in fixture.book['Overview']['Settings'][1]:
            if row[0] == 'calculation_input_sha256': row[1] = input_hash(fixture.book)
        set_result_hash(fixture.book); write_book(fixture.snapshot, fixture.book)
        manifest = fixture.model / 'results/result_manifest.json'
        record = json.loads(manifest.read_text()); record['snapshot_sha256'] = sha(fixture.snapshot)
        manifest.write_text(json.dumps(record))
        series = {'default_model': 'other', 'models': [{'id': 'other', 'scopes': {}}]}
        network = {'default_model': 0, 'models': [{'id': 'other', 'scopes': {}}]}
        with patch.object(original_atlas_data, 'review_display', return_value=(fixture.review, None)):
            original_atlas_data.add_source_reviews(fixture.root, 'LME_001', fixture.metadata, (series, network))
        self.assertEqual(series['models'][1]['calculation_provenance'], network['models'][1]['calculation_provenance'])
        self.assertEqual(network['models'][1]['group_data']['groups'][0]['ee'], .1)
        self.assertEqual(network['models'][1]['group_data']['groups'][0]['source_ee'], .02)
        self.assertEqual(series['models'][1]['researcher_review'], fixture.review)
        self.assertEqual((series['default_model'], network['default_model']), ('other', 0))

    def test_efficiency_enrichment_reads_source_and_effective_values_for_both_models(self):
        import openpyxl
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); region = root / 'regions/LME/LME_001'
            region.mkdir(parents=True)
            book = self.book()
            book['Overview']['Settings'][1].extend([['selected_model_id', 'alternative'], ['results_model_id', 'current']])
            write_book(region / 'LME_001.xlsx', book)
            for model_id in ['current', 'alternative']:
                native = region / 'papers/P/models' / model_id / 'model.json'
                native.parent.mkdir(parents=True); native.write_text('{}')
            export = openpyxl.Workbook(); export.active.title = 'groups_df'
            export.active.append(['group_name', 'ge', 'ee', 'M0', 'source_EE', 'source_M0',
                                  'EE_before_floor', 'M0_before_floor', 'external_mortality_export'])
            export.active.append(['fish group', .3, .1, 9., .05, None, .05, 9.5, .5])
            source = region / 'papers/P/models/alternative/sppr_source.xlsx'
            export.save(source); export.close()
            units = {'LME_001': {'models': [{'id': model_id, 'group_data': {'groups': [{'id': 'fish group'}]}}
                                           for model_id in ['current', 'alternative']]}}
            preserved = {path: path.read_bytes() for path in region.rglob('*.xlsx')}
            original_atlas_data.add_group_efficiencies(root, units)
            current, alternative = [model['group_data']['groups'][0] for model in units['LME_001']['models']]
            self.assertEqual((current['ee'], current['source_ee'], current['external_mortality_export']), (.1, .02, 1.5))
            self.assertEqual((alternative['ee'], alternative['source_ee'], alternative['external_mortality_export']), (.1, .05, .5))
            self.assertIsNone(alternative['source_m0'])
            self.assertAlmostEqual(alternative['te'], .03)
            for path, data in preserved.items(): self.assertEqual(path.read_bytes(), data)

    def test_source_view_lists_candidate_settings_and_exact_saved_provenance_links(self):
        catalog = {'regions': [{'unit_id': 'LME_001'}], 'network': {'units': {'LME_001': {'models': [
            {'id': 'selected', 'calculation_provenance': {'use_ee_floor': False, 'ee_floor': .1},
             'workbook': 'regions/LME/LME_001/LME_001.xlsx'},
            {'id': 'candidate', 'label': 'Candidate <model>',
             'calculation_provenance': {'use_ee_floor': True, 'ee_floor': .1},
             'workbook': 'regions/LME/LME_001/papers/P/models/candidate/results/regional_snapshot.xlsx',
             'source': 'regions/LME/LME_001/papers/P/models/candidate/sppr_source.xlsx'}]}}}}
        page = '<details><summary>Region <small>LME_001 · 0 studies</small></summary><p>Retained source prose</p></details>'
        updated = source_provenance_layout(page, catalog)
        self.assertIn('EE floor OFF', updated); self.assertIn('EE floor ON (0.1)', updated)
        self.assertIn('Candidate &lt;model&gt;', updated)
        self.assertIn('href="../regions/LME/LME_001/papers/P/models/candidate/results/regional_snapshot.xlsx"', updated)
        self.assertIn('href="../regions/LME/LME_001/papers/P/models/candidate/sppr_source.xlsx"', updated)
        self.assertIn('<p>Retained source prose</p>', updated)

    @unittest.skipUnless(shutil.which('node'), 'Node required for display/export checks')
    def test_generated_pages_show_settings_without_changing_review_and_exports(self):
        root = Path(__file__).resolve().parents[3]
        with tempfile.TemporaryDirectory() as directory:
            pages = []
            for name in ['index.html', 'trends.html']:
                page = Path(directory) / name
                page.write_text(linked_layout((root / 'tools/project_core/maps/original_html_layout' / name).read_text('utf-8')), encoding='utf-8')
                pages.append(str(page))
            result = subprocess.run([shutil.which('node'), str(Path(__file__).with_name('check_ee_floor_views.js')), *pages],
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__': unittest.main()
