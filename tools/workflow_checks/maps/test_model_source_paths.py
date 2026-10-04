"""Model download links must follow declared files, not display identities."""
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.project_core.maps.original_atlas_data import datasets
from tools.project_core.calculations.regional import recalculate, set_setting
from tools.workflow_checks.calculations.test_workflow import fixture
from tools.project_core.workbooks.workbooks import ANNUAL_HEADER, rows, sha, write_book


class ModelSourcePathTests(unittest.TestCase):
    def generate(self, root, nested=True, with_sppr=True, retained=False, registered=True):
        region = root / 'regions/LME/LME_001'
        model = region / ('papers/Source-with-variants/models/m/model.json'
                          if nested else 'papers/P/models/m/model.json')
        model.parent.mkdir(parents=True)
        model.write_text('{}', encoding='utf-8')
        if with_sppr:
            model.with_name('sppr_source.xlsx').write_bytes(b'retained coefficients')
        # A stale ID-derived source must never override the declared variant.
        if nested:
            decoy = region / 'models/m/sppr_source.xlsx'
            decoy.parent.mkdir(parents=True)
            decoy.write_bytes(b'old coefficients')
        book = fixture()
        set_setting(book, 'model_path', model.relative_to(region).as_posix())
        path = region / 'LME_001.xlsx'
        recalculate(book, path)
        write_book(path, book)
        project = {
            'Regions & status': {'Regions': (
                ['unit_id', 'name', 'type', 'workbook', 'selected_model_id', 'sha256', 'status'],
                [['LME_001', 'Fixture', 'LME', 'regions/LME/LME_001/LME_001.xlsx', 'm', sha(path), 'current']])},
            'Models & coverage': {'Models': (
                ['unit_id', 'model_id', 'model_path'],
                [['LME_001', 'm', model.relative_to(root).as_posix() if nested and registered else None]])},
            'Regional PPR': {'Annual': (
                ['unit_id', *ANNUAL_HEADER],
                [['LME_001', *r] for sheet in ['Classic PPR', 'PPR'] for r in rows(book, sheet, 'Annual')])},
            'Regional NPP': {'NPP': (
                ['unit_id', 'method', 'units', *range(1950, 2020)],
                [['LME_001', *r] for r in rows(book, 'NPP', 'NPP')])},
        }
        workbook = root / 'Project.xlsx'
        write_book(workbook, project)
        context = root / 'common_reference_data/atlas_source_context'
        context.mkdir(parents=True)
        for name, payload in [('catalog', {'regions': [], 'articles': [], 'network': {'units': {}}}),
                              ('time_series', {'units': {}, 'npp_methods': []})]:
            with gzip.open(context / (name + '.json.gz'), 'wt', encoding='utf-8') as stream:
                json.dump(payload, stream)
        catalog, series, _ = datasets(workbook)
        if retained:
            other = root / 'regions/LME/LME_002/LME_002.xlsx'
            write_book(other, {'Overview': {'Settings': (['field', 'value'], [['unit_id', 'LME_002']])}})
            project['Regions & status']['Regions'][1].append(
                ['LME_002', 'Other', 'LME', 'regions/LME/LME_002/LME_002.xlsx', None, sha(other), 'migrated saved results'])
            write_book(workbook, project)
            series['units']['LME_002'] = {'models': []}
            pages = root / 'interactive_map'
            pages.mkdir()
            (pages / 'index.html').write_text('const DB=' + json.dumps(catalog) + ';', encoding='utf-8')
            (pages / 'trends.html').write_text('const SERIES_DB=' + json.dumps(series) + ';', encoding='utf-8')
            catalog, series, _ = datasets(workbook, only_units={'LME_002'})
        return [catalog['network']['units']['LME_001']['models'][0]['source'],
                series['units']['LME_001']['models'][0]['source']]

    def test_nested_declared_variant_links_its_sppr_sibling_in_both_payloads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            expected = 'regions/LME/LME_001/papers/Source-with-variants/models/m/sppr_source.xlsx'
            self.assertEqual(self.generate(root), [expected, expected])
            self.assertTrue((root / expected).is_file())

    def test_nested_variant_without_sppr_links_exact_native_model(self):
        with tempfile.TemporaryDirectory() as directory:
            expected = 'regions/LME/LME_001/papers/Source-with-variants/models/m/model.json'
            self.assertEqual(self.generate(Path(directory), with_sppr=False), [expected, expected])

    def test_discovery_without_declared_registry_path_keeps_existing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            expected = 'regions/LME/LME_001/papers/P/models/m/sppr_source.xlsx'
            self.assertEqual(self.generate(Path(directory), nested=False), [expected, expected])

    def test_scoped_build_uses_registry_path_for_retained_nested_model(self):
        with tempfile.TemporaryDirectory() as directory:
            expected = 'regions/LME/LME_001/papers/Source-with-variants/models/m/sppr_source.xlsx'
            self.assertEqual(self.generate(Path(directory), retained=True), [expected, expected])

    def test_retained_model_without_declared_path_uses_canonical_discovery(self):
        with tempfile.TemporaryDirectory() as directory:
            expected = 'regions/LME/LME_001/papers/P/models/m/sppr_source.xlsx'
            self.assertEqual(self.generate(Path(directory), nested=False, retained=True, registered=False), [expected, expected])


if __name__ == '__main__':
    unittest.main()
