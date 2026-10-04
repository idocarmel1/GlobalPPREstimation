"""Extraction must preserve source diets; normalization belongs to runtime copies."""
import importlib.util
import json
import sys
import tempfile
import unittest
import logging
import warnings
from pathlib import Path
from decimal import Decimal

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
ACTIVE = ROOT / 'tools/skills/paper-to-ppr/resources/extraction/scripts'
PERSONAL = Path.home() / '.agents/skills/ecopath-extraction/scripts'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0,str(path.parent))
    try:spec.loader.exec_module(module)
    finally:sys.path.pop(0)
    return module


class DietPreservationTests(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logger = logging.getLogger('EwE_Converter')
        for handler in logger.handlers:
            handler.close()
        logger.handlers.clear()
        logging.disable(logging.NOTSET)

    def convert(self, converter, directory):
        try:
            sys.path.insert(0,str(Path(converter.csv_to_json.__func__.__code__.co_filename).parent))
            try:return converter.csv_to_json(str(directory))
            finally:sys.path.pop(0)
        finally:
            for handler in converter.logger.handlers:
                handler.close()
            converter.logger.handlers.clear()

    def fixture(self, directory, proportions):
        writer = load(ACTIVE / 'write_outputs.py', 'diet_writer')
        model = {'groups': [
            {'n': 1, 'name': 'Consumer', 'biomass': 1, 'pb': 1, 'qb': 2, 'ee': .5},
            {'n': 2, 'name': 'Producer', 'biomass': 2, 'pb': 2, 'qb': 0, 'ee': .5},
            {'n': 3, 'name': 'Detritus', 'biomass': 1, 'pb': 0, 'qb': 0, 'ee': .5}],
            'consumers': [1], 'diet': {'1': proportions}}
        writer.write_csv(directory / 'Basic_input.csv', writer.basic_input(model))
        writer.write_csv(directory / 'Diet_composition.csv', writer.diet_composition(model))
        (directory / 'metadata.csv').write_text(
            'model_number,1\nmodel_name,Test\nmodel_year,2000\nlme,1\n')
        return model

    def test_converter_retains_rounding_deficit_excess_and_material_deficit(self):
        cases = [('0.600', '0.200', '0.199'),
                 ('0.600', '0.200', '0.201'),
                 ('0.500', '0.200', '0.200'),
                 ('0.600', '0.400', '0.000')]
        for script in [ACTIVE / 'database_json.py', PERSONAL / 'database_json.py']:
            converter = load(script, 'diet_converter').EwEConverter()
            for prey1, prey2, imported in cases:
                with self.subTest(script=str(script), total=str(sum(map(Decimal, (prey1, prey2, imported))))):
                    with tempfile.TemporaryDirectory() as tmp:
                        directory = Path(tmp)
                        # A complete source column includes explicit zero prey
                        # cells. Omitting a cell means unknown, never zero.
                        self.fixture(directory, {'1': prey1, '2': prey2, '3': '0', 'import': imported})
                        result = json.loads(Path(self.convert(converter, directory)).read_text())
                        group = result['group'][0]
                        self.assertEqual(group['diet_imp'], imported)
                        self.assertEqual({d['prey_seq']: d['proportion'] for d in group['diet_descr']['diet']},
                                         {'1': prey1, '2': prey2, '3': '0'})
                        receipt = json.loads((directory / 'DIET_SOURCE_SUMS.json').read_text())
                        record = receipt['consumers'][0]
                        self.assertEqual(Decimal(record['diet_plus_import_sum']),
                                         sum(map(Decimal, (prey1, prey2, imported))))
                        self.assertFalse(record['extraction_normalized'])
                        self.assertEqual(record['review_status'], 'not_established_by_conversion')

    def test_roundtrip_preserves_raw_cells_and_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.fixture(directory, {'1': '0.6', '2': '0.2', '3': '0', 'import': '0.199'})
            converter = load(ACTIVE / 'database_json.py', 'roundtrip_converter').EwEConverter()
            output = self.convert(converter, directory)
            workbook = directory / 'roundtrip.xlsx'
            converter.json_to_excel(output, str(workbook))
            diet = pd.read_excel(workbook, sheet_name='Diet_composition', header=None).set_index(1)
            self.assertEqual(diet.at['Consumer', 2], .6)
            self.assertEqual(diet.at['Producer', 2], .2)
            self.assertEqual(diet.at['Detritus', 2], 0)
            self.assertEqual(diet.at['Import', 2], .199)
            self.assertAlmostEqual(diet.at['Sum', 2], .999)
            fidelity=json.loads((directory/'SOURCE_FIDELITY_CHECK.json').read_text())
            self.assertTrue(fidelity['numeric_value_and_missing_mask_match'])

    def test_runtime_normalization_is_allowed_and_preserves_input(self):
        sys.path.insert(0, str(ROOT / 'tools/scientific_code/PPREstimation'))
        from ModelData import ModelData
        raw = pd.DataFrame([[.5, .2, .2], [0., 0., 0.]], index=[1, 2])
        groups = pd.DataFrame({'trophic_info': ['Regular', 'PP'], 'group_name': ['Consumer', 'Producer']}, index=[1, 2])
        original = raw.copy()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            normalized = ModelData.validate_DC(raw, groups, normalize=True)
        pd.testing.assert_frame_equal(raw, original)
        self.assertAlmostEqual(normalized.loc[1].sum(), 1.)
        self.assertAlmostEqual(normalized.loc[1, 2], .2 / .9)
        self.assertEqual(normalized.loc[2].sum(), 0.)

    def test_diet_conversion_preserves_detritus_fate(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.fixture(directory, {'1': '0', '2': '0.700', '3': '0', 'import': '0.200'})
            (directory / 'Detritus_fate.csv').write_text(
                'No,Group name,Detritus,Export\n1,Consumer,0.75,0.25\n')
            converter = load(ACTIVE / 'database_json.py', 'fate_converter').EwEConverter()
            result = json.loads(Path(self.convert(converter, directory)).read_text())
            group = result['group'][0]
            diet = {d['prey_seq']: d for d in group['diet_descr']['diet']}
            self.assertEqual(diet['2']['proportion'], '0.700')
            self.assertEqual(group['diet_imp'], '0.200')
            self.assertEqual(diet['3']['detritus_fate'], '0.75')
            self.assertEqual(diet['3']['proportion'], '0')

    def test_explicit_unknown_import_stays_unknown_through_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.fixture(directory, {'1': '0', '2': '0.900', '3': '0', 'import': None})
            csv_import = (directory / 'Diet_composition.csv').read_text().splitlines()[-3]
            self.assertEqual(csv_import, ',Import,')
            converter = load(ACTIVE / 'database_json.py', 'unknown_converter').EwEConverter()
            result_path = self.convert(converter, directory)
            result = json.loads(Path(result_path).read_text())
            self.assertEqual(result['group'][0]['diet_imp'], '-9999')
            receipt = json.loads((directory / 'DIET_SOURCE_SUMS.json').read_text())['consumers'][0]
            self.assertIsNone(receipt['diet_plus_import_sum'])
            workbook = directory / 'roundtrip.xlsx'
            converter.json_to_excel(result_path, str(workbook))
            diet = pd.read_excel(workbook, sheet_name='Diet_composition', header=None).set_index(1)
            self.assertTrue(pd.isna(diet.at['Import', 2]))
            self.assertTrue(pd.isna(diet.at['Sum', 2]))

    def test_absent_prey_cell_stays_unknown_in_json_and_source_workbook(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            self.fixture(directory, {'1': '0.6', '2': '0.2', 'import': '0.199'})
            converter=load(ACTIVE/'database_json.py','missing_prey_converter').EwEConverter()
            result_path=self.convert(converter,directory)
            result=json.loads(Path(result_path).read_text())
            diet={r['prey_seq']:r['proportion'] for r in result['group'][0]['diet_descr']['diet']}
            self.assertEqual(diet['3'],'-9999')
            record=json.loads((directory/'DIET_SOURCE_SUMS.json').read_text())['consumers'][0]
            self.assertIsNone(record['diet_plus_import_sum'])
            self.assertEqual(record['unknown_prey_ids'],['3'])
            workbook=directory/'roundtrip.xlsx';converter.json_to_excel(result_path,str(workbook))
            reconstructed=pd.read_excel(workbook,sheet_name='Diet_composition',header=None).set_index(1)
            self.assertTrue(pd.isna(reconstructed.at['Detritus',2]))

    def test_numeric_missing_sentinel_imports_stay_unknown(self):
        for script in [ACTIVE / 'database_json.py', PERSONAL / 'database_json.py']:
            for sentinel in ['-9999.0', '-9999.000']:
                with self.subTest(script=str(script), sentinel=sentinel), tempfile.TemporaryDirectory() as tmp:
                    directory = Path(tmp)
                    self.fixture(directory, {'1': '0', '2': '0.900', '3': '0', 'import': None})
                    csv_path = directory / 'Diet_composition.csv'
                    csv_path.write_text(csv_path.read_text().replace(',Import,\n', ',Import,' + sentinel + '\n'))
                    converter = load(script, 'sentinel_converter').EwEConverter()
                    result_path = self.convert(converter, directory)
                    result = json.loads(Path(result_path).read_text())
                    self.assertEqual(Decimal(result['group'][0]['diet_imp']), Decimal('-9999'))
                    receipt = json.loads((directory / 'DIET_SOURCE_SUMS.json').read_text())['consumers'][0]
                    self.assertTrue(receipt['import_unknown'])
                    self.assertIsNone(receipt['diet_plus_import_sum'])
                    workbook = directory / 'roundtrip.xlsx'
                    converter.json_to_excel(result_path, str(workbook))
                    diet = pd.read_excel(workbook, sheet_name='Diet_composition', header=None).set_index(1)
                    self.assertEqual(diet.at['Import', 2], -9999)
                    self.assertTrue(pd.isna(diet.at['Sum', 2]))


if __name__ == '__main__':
    unittest.main()
