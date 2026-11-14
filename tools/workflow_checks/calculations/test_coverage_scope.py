"""Scientific inventory and rollback discovery stay inside explicit targets."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.project_core.calculations import coverage
from tools.project_core.registry import publication, update_project
from tools.project_core.workbooks.workbooks import sha, write_book


class CoverageScopeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.pairs = [('LME_001', 'a'), ('LME_001', 'candidate'), ('LME_002', 'b')]
        self.metadata = [dict(unit_id=u, model_id=m, researcher_review_status='Validated by researcher')
                         for u, m in self.pairs]
        regions = []
        for unit in sorted({u for u, _ in self.pairs}):
            region = self.root / 'regions/LME' / unit
            region.mkdir(parents=True)
            path = region / (unit + '.xlsx')
            path.write_bytes(b'retained workbook')
            regions.append([unit, sha(path)])
        for unit, model in self.pairs:
            path = self.root / 'regions/LME' / unit / 'papers/p/models' / model
            path.mkdir(parents=True)
            (path / 'model.json').write_text('{}')
        write_book(self.root / 'Project.xlsx', {
            'Models & coverage': {'Models': (list(self.metadata[0]), [list(r.values()) for r in self.metadata])},
            'Regions & status': {'Regions': (['unit_id', 'sha256'], regions)}})

    def complete(self, **scope):
        visited = []
        def complete(root, metadata, expected, **kwargs):
            visited.append((metadata['unit_id'], metadata['model_id']))
            return False, {'unit_id': metadata['unit_id'], 'model_id': metadata['model_id']}
        with patch.object(coverage, '_complete_model', side_effect=complete), \
             patch('tools.scientific_helpers.sppr.method_coverage.method_inventory', return_value=('GE',)):
            coverage.ensure_validated_coverage(self.root, lock_held=True, **scope)
        return visited

    def test_unit_scope_keeps_candidates_but_never_discovers_other_regions(self):
        from tools.project_core.registry import discovery
        original = discovery.resolve_model
        def resolve(region, model):
            self.assertEqual(region.name, 'LME_001')
            return original(region, model)
        with patch.object(discovery, 'resolve_model', side_effect=resolve):
            self.assertEqual(self.complete(units={'LME_001'}), self.pairs[:2])

    def test_exact_pair_scope_does_not_traverse_other_candidates(self):
        self.assertEqual(self.complete(model_pairs={('LME_001', 'candidate')}), [self.pairs[1]])

    def test_empty_and_omitted_scope_do_not_read_metadata_or_load_adapter(self):
        for scope in ({}, {'units': []}, {'model_pairs': []}):
            with self.subTest(scope=scope), \
                 patch.object(coverage, '_metadata', side_effect=AssertionError('unrequested metadata')), \
                 patch('tools.scientific_helpers.sppr.method_coverage.method_inventory', side_effect=AssertionError('unrequested adapter')):
                result = coverage.ensure_validated_coverage(self.root, **scope)
                self.assertEqual(result['models'], [])

    def test_explicit_all_preserves_full_inventory(self):
        self.assertEqual(self.complete(all_validated=True), self.pairs)

    def test_migration_units_also_bound_identity_traversal(self):
        self.assertEqual(self.complete(migration_units={'LME_002'}, ee_floor={'use_ee_floor': True, 'ee_floor': .1}), [self.pairs[2]])

    def test_global_and_narrow_scope_cannot_be_combined(self):
        with self.assertRaisesRegex(ValueError, 'scope'):
            self.complete(all_validated=True, units={'LME_001'})

    def test_render_transaction_does_not_discover_scientific_packages(self):
        with patch.object(publication, 'resolve_model', side_effect=AssertionError('unrequested package')):
            with publication.publication_transaction(self.root) as backup:
                self.assertEqual(backup.models, [])

    def test_scoped_transaction_backs_up_only_requested_model(self):
        with publication.publication_transaction(self.root, model_pairs={self.pairs[1]}) as backup:
            self.assertEqual([(r['unit_id'], r['model_id']) for r in backup.models], [self.pairs[1]])
            self.assertFalse(any('LME_002' in str(path) for path in backup.before))

    def test_full_audit_is_an_explicit_cli_operation(self):
        self.assertTrue(update_project.parse_arguments(['--audit-validated-methods']).audit_validated_methods)


if __name__ == '__main__':
    unittest.main()
