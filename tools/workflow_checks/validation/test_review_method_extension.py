"""The optional calculation-provenance audit requires exact input projection."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.project_core.validation import researcher_review as review
from tools.project_core.workbooks.workbooks import input_hash,sha


class ReviewMethodExtensionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.model = self.root / 'regions/LME/LME_001/papers/p/models/candidate'
        (self.model / 'results').mkdir(parents=True)
        self.metadata = {'model_id': 'candidate', 'unit_id': 'LME_001',
                         'model_path': (self.model / 'model.json').relative_to(self.root).as_posix()}
        self.book = {'Overview': {'Settings': (['field', 'value'], [])},
                     'Catch': {'Catch': (['taxon', 2000], [['fish', 5.]])},
                     'Selected model groups': {
                         'Groups': (['group_name'], [['fish']]),
                         'Group SPPR': (['model_id', 'group', 'scope', 'method', 'sppr'],
                                        [['candidate', 'fish', 'all', 'reviewed', 2.]])},
                     'PPR': {'Matching': (['taxon', 'group', 'weight'], [['fish', 'fish', 1.]])}}
        original = input_hash(self.book)
        self.metadata['reviewed_calculation_input_sha256'] = original
        self.book['Selected model groups']['Group SPPR'][1].append(
            ['candidate', 'fish', 'all', 'added', 3.])
        self.book['Overview']['Settings'][1].append(['calculation_input_sha256', input_hash(self.book)])
        self.extension = {'schema_version': 1, 'original_reviewed_input_sha256': original,
                          'current_input_sha256': input_hash(self.book), 'reviewed_methods': ['reviewed']}
        self.write_manifest()

    def write_manifest(self):
        (self.model / 'results/result_manifest.json').write_text(
            json.dumps({'review_extension': self.extension}), encoding='utf-8')

    def check(self):
        return review.verified_method_extension(self.root, self.metadata, self.book)

    def test_exact_original_projection_proves_only_calculation_provenance(self):
        before = copy.deepcopy(self.metadata)
        result = self.check()
        self.assertEqual(result['reviewed_methods'], ['reviewed'])
        self.assertEqual(result['added_methods'], ['added'])
        self.assertIn('after this signed review', result['note'])
        self.assertIn('does not determine researcher validation', result['note'])
        self.assertEqual(result['evidence_manifest_sha256'],sha(self.model/'results/result_manifest.json'))
        self.assertEqual(self.metadata, before)

    def test_changes_to_original_inputs_cannot_be_blessed_by_rehashing_extension(self):
        for table, index, value in [('Catch', 1, 6.), ('Group SPPR', 4, 4.), ('Matching', 2, .5)]:
            with self.subTest(table=table):
                prior = copy.deepcopy(self.book)
                sheet = {'Catch': 'Catch', 'Group SPPR': 'Selected model groups', 'Matching': 'PPR'}[table]
                self.book[sheet][table][1][0][index] = value
                self.extension['current_input_sha256'] = input_hash(self.book)
                self.book['Overview']['Settings'][1][0][1] = input_hash(self.book)
                self.write_manifest()
                with self.assertRaisesRegex(ValueError, 'reviewed inputs'):
                    self.check()
                self.book = prior

    def test_stale_extension_and_missing_evidence_are_rejected(self):
        self.extension['current_input_sha256'] = 'old'
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'current calculation'):
            self.check()
        (self.model / 'results/result_manifest.json').unlink()
        with self.assertRaisesRegex(ValueError, 'extension evidence'):
            self.check()


if __name__ == '__main__':
    unittest.main()
