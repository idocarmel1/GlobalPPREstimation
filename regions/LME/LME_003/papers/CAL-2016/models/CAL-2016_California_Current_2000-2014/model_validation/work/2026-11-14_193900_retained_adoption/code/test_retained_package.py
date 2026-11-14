"""Focused publication safety checks using only temporary model-local fixtures."""
import hashlib, importlib.util, os, tempfile, unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).with_name('retained_package.py')
spec = importlib.util.spec_from_file_location('lme003_retained_test', SCRIPT)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


class PublicationSafety(unittest.TestCase):
    def setUp(self):
        qa = mod.RUN / 'qa'; qa.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=qa, prefix='publication_fixture_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve(); self.model = self.root / 'model'; self.model.mkdir()
        self.region = self.root / 'regional.xlsx'; self.region.write_bytes(b'prior regional bytes')
        self.package = self.root / 'package'; self.package.mkdir(); self.source = self.package / 'regional.xlsx'; self.source.write_bytes(b'prepared regional bytes')
        self.input = self.root / 'raw.json'; self.input.write_bytes(b'authenticated input')
        (self.root / 'Project.xlsx').write_bytes(b'fixture project, never parsed')
        (self.root / '.project-write.lock').write_text(str(os.getpid()))
        self.stack = ExitStack(); self.addCleanup(self.stack.close)
        for owner, key, value in [(mod, 'ROOT', self.root), (mod, 'MODEL', self.model), (mod, 'REGION', self.region), (mod.stage, 'ROOT', self.root)]:
            self.stack.enter_context(patch.object(owner, key, value))
        self.plan = {'promotions': [{'source': 'regional.xlsx', 'target': 'regional.xlsx', 'sha256': mod.stage.sha(self.source)}],
            'consumed_inputs': {'regional.xlsx': mod.stage.sha(self.region), 'raw.json': mod.stage.sha(self.input)}}

    def test_cached_buffer_cannot_change_with_source(self):
        buffers = mod._verified_buffers(self.package, self.plan)
        self.source.write_bytes(b'changed after verification')
        self.assertEqual(buffers[0][2], b'prepared regional bytes')
        with self.assertRaisesRegex(ValueError, 'source buffer changed'):
            mod._verified_buffers(self.package, self.plan)

    def test_canonical_target_is_rejected(self):
        self.plan['promotions'][0]['target'] = 'model/model.json'
        with self.assertRaisesRegex(ValueError, 'outside approved'):
            mod._verified_buffers(self.package, self.plan)

    def test_duplicate_target_is_rejected(self):
        self.plan['promotions'].append(dict(self.plan['promotions'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            mod._verified_buffers(self.package, self.plan)

    def test_active_transaction_required(self):
        with self.assertRaisesRegex(ValueError, 'Active publication transaction'):
            mod.apply(None, self.package)

    def test_late_input_change_rolls_back_owned_write(self):
        from tools.project_core.registry.publication import publication_transaction
        from tools.project_core.calculations import coverage
        actual_write = coverage._write_bytes
        def late_change(path, data, **kwargs):
            actual_write(path, data, **kwargs)
            self.input.write_bytes(b'concurrent independent edit')
        with patch.object(mod, '_guard', return_value={'guard': 'fixture'}), patch.object(mod, 'verify_package', return_value=self.plan), patch.object(coverage, '_write_bytes', side_effect=late_change):
            with self.assertRaisesRegex(ValueError, 'Consumed input changed: raw.json'):
                with publication_transaction(self.root, [self.region], [self.model]) as publication:
                    mod.apply(publication, self.package)
        self.assertEqual(self.region.read_bytes(), b'prior regional bytes')
        self.assertEqual(self.input.read_bytes(), b'concurrent independent edit')


if __name__ == '__main__': unittest.main(verbosity=2)
