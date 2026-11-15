"""Authenticate both original singleton and named execution references."""
import copy
from pathlib import Path
import tempfile
import unittest

from tools.project_core.calculations import coverage
from tools.project_core.workbooks.workbooks import sha


class ExecutionEvidenceReferenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.model = Path(temporary.name) / 'model'
        self.diagnostics = self.model / 'results/diagnostics'
        self.diagnostics.mkdir(parents=True)
        self.path = self.model / 'regional.xlsx'
        self.path.write_bytes(b'regional workbook bytes')
        (self.model / 'results/regional_snapshot.xlsx').write_bytes(self.path.read_bytes())
        (self.model / 'sppr_source.xlsx').write_bytes(b'coefficient workbook bytes')
        self.book = {'Selected model groups': {'Group SPPR': (
            ['model_id', 'group', 'scope', 'method', 'sppr'], [['M', 'Fish', 'all', 'new_GE', 2.5]])}}
        self.context = {'model_sha256': 'original model identity'}
        self.expected = ['new_GE']
        self.original = self.reference('execution.json', b'original execution evidence')
        self.named = self.reference('constructor.json', b'new named evidence')
        self.saved = {'context': self.context, 'expected_methods': self.expected,
            'arithmetic_code_identity': coverage._arithmetic_identity(),
            'methods': {'new_GE': {'status': 'ok', 'evidence': self.reference('method.json', b'method evidence'),
                'group_rows_sha256': coverage._method_rows(self.book)[1]['new_GE']}}}

    def reference(self, name, data):
        path = self.diagnostics / name
        path.write_bytes(data)
        return {'path': name, 'sha256': sha(path)}

    def check(self, execution, valid):
        saved = {**self.saved, 'execution_evidence': copy.deepcopy(execution)}
        before = copy.deepcopy(saved)
        manifest = {'method_coverage': saved, 'snapshot_sha256': sha(self.path),
                    'coefficient_source_sha256': sha(self.model / 'sppr_source.xlsx')}
        self.assertEqual(coverage._cached_methods(self.model, saved, self.context, self.book, self.expected),
                         [] if valid else self.expected)
        self.assertEqual(coverage._package_cache_valid(self.model, self.path, manifest, self.context, self.expected), valid)
        self.assertEqual(saved, before, 'Reading references must not rewrite provenance')

    def test_legacy_single_reference_is_authenticated_without_rewriting(self):
        self.check(self.original, True)

    def test_named_references_remain_authenticated(self):
        self.check({'constructor': self.named}, True)

    def test_later_batch_authenticates_legacy_pair_and_new_named_references(self):
        mixed = {**self.original, 'constructor': self.named}
        self.check(mixed, True)
        (self.diagnostics / self.named['path']).write_bytes(b'changed constructor')
        self.check(mixed, False)
        self.assertEqual({key: mixed[key] for key in self.original}, self.original)

    def test_wrong_hash_missing_file_outside_path_and_missing_keys_fail_closed(self):
        outside = self.model.parent / 'outside.json'
        outside.write_bytes(b'outside evidence')
        for reference in [
            {**self.original, 'sha256': '0' * 64},
            {**self.original, 'path': 'missing.json'},
            {'path': '../../../outside.json', 'sha256': sha(outside)},
            {'path': self.original['path']}, {'sha256': self.original['sha256']},
            {'path': None, 'sha256': self.original['sha256']},
            {'path': [self.original['path']], 'sha256': self.original['sha256']},
            {'path': self.original['path'], 'sha256': [self.original['sha256']]},
        ]:
            with self.subTest(reference=reference):
                self.check(reference, False)

    def test_malformed_container_and_named_values_fail_closed(self):
        for value in ['not a reference', None, [], {'constructor': 'not a reference'},
                      {**self.original, 'constructor': None}]:
            with self.subTest(value=value):
                self.check(value, False)


if __name__ == '__main__':
    unittest.main()
