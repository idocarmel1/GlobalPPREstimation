"""Bounded reads must preserve table semantics and recheck actual input bytes."""
import os
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import openpyxl
from tools.project_core.workbooks.workbooks import read_book, write_book
from tools.project_core.workbooks.read_session import ReadSession


class ReadSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'LME_001.xlsx'
        self.book = {'Overview': {'Settings': (['field', 'value'], [['unit_id', 'LME_001']])},
                     'Catch': {'Catch': (['taxon', 2019], [['zero', 0], ['missing', None]])}}
        write_book(self.path, self.book)

    def test_selected_sheet_matches_complete_reader(self):
        selected = read_book(self.path, sheets=['Catch'])
        self.assertEqual(selected, {'Catch': read_book(self.path)['Catch']})
        self.assertEqual(selected['Catch']['Catch'][0], ['taxon', 2019])
        self.assertEqual(selected['Catch']['Catch'][1], [['zero', 0], ['missing', None]])

    def test_full_reader_still_rejects_formulas(self):
        workbook = openpyxl.load_workbook(self.path)
        workbook['Catch']['B3'] = '=1+1'
        workbook.save(self.path); workbook.close()
        with self.assertRaisesRegex(ValueError, 'formulas are not supported'):
            read_book(self.path)
        self.assertEqual(read_book(self.path, sheets=['Overview'])['Overview'], self.book['Overview'])
        with self.assertRaisesRegex(ValueError, 'formulas are not supported'):
            read_book(self.path, sheets=['Catch'])

    def test_missing_sheet_is_an_error(self):
        with self.assertRaisesRegex(ValueError, 'Missing requested worksheet'):
            read_book(self.path, sheets=['absent'])

    def test_failed_parser_invocation_is_counted(self):
        session = ReadSession()
        with self.assertRaisesRegex(ValueError, 'Missing requested worksheet'):
            session.read(self.path, sheets=['absent'])
        self.assertEqual((session.read_count, session.parse_count), (1, 1))

    def test_unchanged_repeated_reads_parse_once_and_returns_are_independent(self):
        session = ReadSession()
        first = session.read(self.path, sheets=['Overview'])
        first['Overview']['Settings'][1][0][1] = 'wrong'
        self.assertEqual(session.read(self.path, sheets=['Overview']), {'Overview': self.book['Overview']})
        self.assertEqual((session.read_count, session.parse_count), (2, 1))
        session.assert_unchanged()

    def test_changed_bytes_invalidate_even_with_preserved_mtime(self):
        session = ReadSession(); session.read(self.path)
        stat = self.path.stat()
        updated = {'Overview': {'Settings': (['field', 'value'], [['unit_id', 'LME_002']])}}
        write_book(self.path, updated)
        os.utime(self.path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(session.read(self.path), updated)
        self.assertEqual(session.parse_count, 2)
        # Earlier returned dictionaries still exist: a reread cannot certify a
        # mixed-version operation for publication. Start a new coherent session.
        with self.assertRaisesRegex(ValueError, 'Consumed workbook changed'):
            session.assert_unchanged()
        fresh = ReadSession(); self.assertEqual(fresh.read(self.path), updated)
        fresh.assert_unchanged()

    def test_publication_recheck_rejects_changed_bytes(self):
        session = ReadSession(); session.read(self.path, sheets=['Overview'])
        with self.path.open('ab') as target: target.write(b'changed')
        with self.assertRaisesRegex(ValueError, 'Consumed workbook changed'):
            session.assert_unchanged()

    def test_detected_parse_race_remains_invalid_after_reread(self):
        session = ReadSession()
        def changing_read(path, **kwargs):
            value = read_book(path, **kwargs)
            with self.path.open('ab') as target: target.write(b'changed')
            return value
        with patch('tools.project_core.workbooks.read_session.read_book', changing_read):
            with self.assertRaisesRegex(ValueError, 'Workbook changed while reading'):
                session.read(self.path)
        self.assertEqual(session.read(self.path), self.book)
        with self.assertRaisesRegex(ValueError, 'Consumed workbook changed'):
            session.assert_unchanged()

    def test_detected_publication_change_remains_invalid_after_restore(self):
        session = ReadSession(); session.read(self.path)
        original = self.path.read_bytes()
        with self.path.open('ab') as target: target.write(b'changed')
        with self.assertRaisesRegex(ValueError, 'Consumed workbook changed'):
            session.assert_unchanged()
        self.path.write_bytes(original)
        self.assertEqual(session.read(self.path), self.book)
        with self.assertRaisesRegex(ValueError, 'Consumed workbook changed'):
            session.assert_unchanged()

    def test_same_size_same_mtime_change_reparses(self):
        # ZIP permits trailing bytes; a byte-only change still changes input identity.
        with self.path.open('ab') as target: target.write(b'a')
        session = ReadSession(); session.read(self.path)
        before = self.path.read_bytes(); stat = self.path.stat()
        self.path.write_bytes(before[:-1] + b'b')
        os.utime(self.path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(self.path.stat().st_size, len(before))
        self.assertEqual(self.path.stat().st_mtime_ns, stat.st_mtime_ns)
        self.assertEqual(session.read(self.path), self.book)
        self.assertEqual(session.parse_count, 2)

    def test_inspect_cli_is_scoped_and_does_not_write(self):
        before = self.path.read_bytes()
        root = Path(__file__).resolve().parents[3]
        result = subprocess.run([sys.executable, '-B', str(root / 'tools/cli/region.py'),
                                 'inspect', '--region', str(self.path), '--sheet', 'Overview',
                                 '--table', 'Settings'], capture_output=True, text=True, check=True)
        value = json.loads(result.stdout)
        self.assertEqual(value['rows'], self.book['Overview']['Settings'][1])
        self.assertEqual(value['scope'], 'saved table only; readiness not assessed')
        self.assertEqual(self.path.read_bytes(), before)
        missing = subprocess.run([sys.executable, '-B', str(root / 'tools/cli/region.py'),
                                  'inspect', '--region', str(self.path), '--sheet', 'Overview',
                                  '--table', 'absent'], capture_output=True, text=True)
        self.assertNotEqual(missing.returncode, 0)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == '__main__': unittest.main()
