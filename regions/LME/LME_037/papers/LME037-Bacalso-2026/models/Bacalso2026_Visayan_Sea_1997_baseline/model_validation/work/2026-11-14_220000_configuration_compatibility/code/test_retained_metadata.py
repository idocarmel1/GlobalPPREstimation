"""Bounded tests: metadata identity, stock-runtime refusal and write rollback."""
from pathlib import Path
import copy
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))


class RetainedMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = HERE / 'retained_metadata.py'
        cls.package = None
        if path.is_file():
            spec = importlib.util.spec_from_file_location('lme037_metadata_test', path)
            cls.package = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.package)

    def required_package(self):
        self.assertIsNotNone(self.package, 'LME037 retained metadata compatibility wrapper is missing')
        return self.package

    def test_saved_package_configuration_and_original_science(self):
        p = self.required_package()
        plan = p.verify_package()
        original = p.read(p.ARCHIVE)
        staged = p.read(p.OUTPUT / 'result_manifest.json')
        self.assertNotEqual(staged['effective_flags'], original['effective_flags'])
        self.assertEqual(staged['method_coverage'], original['method_coverage'])
        self.assertFalse(staged['effective_flags']['stock_adapter_reconstructible'])
        self.assertEqual(staged['effective_flags']['constructor']['ee_floor'], 1.0)
        self.assertEqual(staged['effective_flags']['constructor']['ee_threshold'], 0.1)
        self.assertEqual(len(plan['promotions']), 3)
        self.assertTrue(all(not x['target'].endswith('.xlsx') for x in plan['promotions']))

    def test_guarded_writes_restore_new_and_existing_targets(self):
        p = self.required_package()
        from tools.project_core.registry.publication import publication_transaction
        fixture_root = (HERE.parent / 'qa/test_fixtures').resolve()
        fixture_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=fixture_root) as folder:
            root = Path(folder).resolve()
            self.assertTrue(root.is_relative_to(fixture_root))
            (root / '.project-write.lock').write_text(str(os.getpid()))
            source = root / 'source.json'; source.write_bytes(b'new metadata')
            target = root / 'manifest.json'; target.write_bytes(b'old manifest')
            fresh = root / 'archive.json'
            plan = {'promotions': [
                {'source': 'source.json', 'target': 'archive.json', 'sha256': p.sha(source)},
                {'source': 'source.json', 'target': 'manifest.json', 'sha256': p.sha(source)}],
                'consumed_inputs': {'manifest.json': p.sha(target), 'archive.json': None,
                                    'source.json': p.sha(source)}}
            with patch.object(p, 'ROOT', root):
                with self.assertRaisesRegex(RuntimeError, 'rollback probe'):
                    with publication_transaction(root) as transaction:
                        p._apply_plan(plan, transaction)
                        self.assertEqual(target.read_bytes(), b'new metadata')
                        self.assertTrue(fresh.is_file())
                        raise RuntimeError('rollback probe')
            self.assertEqual(target.read_bytes(), b'old manifest')
            self.assertFalse(fresh.exists())

    def test_consumed_change_stops_before_first_write(self):
        p = self.required_package()
        from tools.project_core.registry.publication import publication_transaction
        fixture_root = (HERE.parent / 'qa/test_fixtures').resolve()
        fixture_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=fixture_root) as folder:
            root = Path(folder).resolve()
            self.assertTrue(root.is_relative_to(fixture_root))
            (root / '.project-write.lock').write_text(str(os.getpid()))
            source = root / 'source.json'; source.write_bytes(b'new')
            consumed = root / 'input.json'; consumed.write_bytes(b'original')
            plan = {'promotions': [{'source': 'source.json', 'target': 'manifest.json',
                                     'sha256': p.sha(source)}],
                    'consumed_inputs': {'source.json': p.sha(source), 'manifest.json': None,
                                        'input.json': p.sha(consumed)}}
            consumed.write_bytes(b'author edit')
            with patch.object(p, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'Consumed input changed'):
                    with publication_transaction(root) as transaction:
                        p._apply_plan(plan, transaction)
            self.assertFalse((root / 'manifest.json').exists())
            self.assertEqual(consumed.read_bytes(), b'author edit')

    def test_overlap_and_external_target_rejected(self):
        p = self.required_package()
        base = {'promotions': [{'source': 'source.json', 'target': 'same.json', 'sha256': 'x'}],
                'consumed_inputs': {'same.json': None}}
        duplicate = copy.deepcopy(base); duplicate['promotions'] *= 2
        with self.assertRaisesRegex(ValueError, 'Duplicate promotion target'):
            p._validate_plan_paths(duplicate)
        external = copy.deepcopy(base); external['promotions'][0]['target'] = '../external.json'
        with self.assertRaisesRegex(ValueError, 'outside'):
            p._validate_plan_paths(external)


if __name__ == '__main__':
    unittest.main(verbosity=2)
