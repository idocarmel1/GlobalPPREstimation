"""Regression checks for regional-to-central serialized result verification."""
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('integration_check', HERE / 'verify_integrated_regional_tables.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SerializationReconciliationTests(unittest.TestCase):
    def test_actual_patagonia_roundtrip(self):
        diagnosis = json.loads((HERE / 'verification/ready_batch_08_annual_roundtrip_diagnosis.json').read_text(encoding='utf-8'))
        differences = next(r['diffs'] for r in diagnosis['regions'] if r['unit_id'] == 'LME_013')
        self.assertEqual(len(differences), 760)
        expected = [d['key'] + [d['field'], d['regional']] for d in differences]
        actual = [d['key'] + [d['field'], d['central']] for d in differences]
        result = module.compare_rows(expected, actual, 'retained actual annual cells')
        self.assertFalse(result['exact_multiset_match'])
        self.assertTrue(result['xlsx_serialization_multiset_match'])
        self.assertEqual(result['serialization_adjusted_cells'], 760)

    def test_substantive_numeric_change_is_rejected(self):
        with self.assertRaises(AssertionError):
            module.compare_rows([['model', 46157234.223347425]], [['model', 46157234.224]], 'changed number')

    def test_identity_status_and_missing_are_not_normalized(self):
        for expected, actual in [([['model', 'WARN', 1.0]], [['other', 'WARN', 1.0]]),
                                 ([['model', 'WARN', 1.0]], [['model', 'OK', 1.0]]),
                                 ([['model', None]], [['model', 0]])]:
            with self.subTest(expected=expected, actual=actual):
                with self.assertRaises(AssertionError):
                    module.compare_rows(expected, actual, 'changed identity or missingness')

    def test_duplicate_or_lost_records_are_rejected(self):
        with self.assertRaises(AssertionError):
            module.compare_rows([['a', 1], ['b', 2]], [['a', 1], ['a', 1]], 'duplicated key')

    def test_exact_rows_still_report_exact(self):
        self.assertTrue(module.compare_rows([['model', None, 1.5]], [['model', None, 1.5]], 'unchanged')['exact_multiset_match'])


if __name__ == '__main__':
    unittest.main()
