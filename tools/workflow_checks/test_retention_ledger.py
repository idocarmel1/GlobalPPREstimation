import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_migration import verify_retention


class RetentionLedgerTests(unittest.TestCase):
    def test_deleted_interface_is_explicit_but_missing_research_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            archive = root / 'original_research_archive'
            archive.mkdir()
            (root / 'study.txt').write_bytes(b'research')
            rows = [dict(original_path='old/study.txt', retained_path='study.txt',
                         sha256=hashlib.sha256(b'research').hexdigest(), disposition='moved',
                         disposition_reason='Relocated research'),
                    dict(original_path='old/index.html', retained_path='', sha256='old-hash',
                         disposition='intentionally_removed_interface',
                         disposition_reason='User discarded historical page')]
            def save():
                with (archive / 'migration.csv').open('w', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=list(rows[0]))
                    w.writeheader(); w.writerows(rows)
            save()
            self.assertEqual(verify_retention(root), (1, 1))
            (root / 'study.txt').unlink()
            with self.assertRaisesRegex(AssertionError, 'Retention mismatch'):
                verify_retention(root)
            rows[0]['retained_path'] = ''
            save()
            with self.assertRaisesRegex(AssertionError, 'Retention mismatch'):
                verify_retention(root)
