import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_npp_sources import verify


class NppSourcesTests(unittest.TestCase):
    def fixture(self, root):
        raw = root / 'common_reference_data/npp/raw'
        raw.mkdir(parents=True)
        (raw / 'sample.nc').write_bytes(b'original')
        entry = {'path': 'sample.nc', 'bytes': 8,
                 'sha256': hashlib.sha256(b'original').hexdigest()}
        manifest = raw.parent / 'source_manifest.json'
        manifest.write_text(json.dumps({'raw_directory': 'common_reference_data/npp/raw',
                                       'files': [entry]}))
        return raw, manifest, entry

    def test_detects_same_size_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            raw, manifest, _ = self.fixture(root)
            self.assertEqual(verify(root, manifest)['verified_files'], 1)
            (raw / 'sample.nc').write_bytes(b'changed!')
            with self.assertRaisesRegex(ValueError, 'SHA-256'):
                verify(root, manifest)

    def test_rejects_escape_and_missing_sources(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            raw, manifest, entry = self.fixture(root)
            (raw / 'sample.nc').unlink()
            with self.assertRaisesRegex(ValueError, 'Missing'):
                verify(root, manifest)
            entry['path'] = '../outside.nc'
            manifest.write_text(json.dumps({'raw_directory': 'common_reference_data/npp/raw',
                                           'files': [entry]}))
            with self.assertRaisesRegex(ValueError, 'escapes'):
                verify(root, manifest)


if __name__ == '__main__':
    unittest.main()
