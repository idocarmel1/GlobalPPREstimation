"""Checks the review utility on changed-length blocks and protected raw XML."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'tools'))
import workbooks as W
from bounded_workbook_update import update_blocks


class BlockUpdateTests(unittest.TestCase):
    def test_growth_shrink_preserves_other_parts_and_precision(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'region.xlsx'
            before = {'PPR': {'First': (['taxon', 'value'], [['a', 1.0]]),
                              'Last': (['taxon', 'value'], [['z', 9.0], ['q', 8.0]])},
                      'Accepted': {'Parameters': (['B', 'PB'], [[3.14, 2.5]])}}
            W.write_book(p, before)
            before = W.read_book(p)
            with ZipFile(p) as z:
                parts = {n: z.read(n) for n in z.namelist()}
            after = copy.deepcopy(before)
            precise = 1.2345678901234567
            after['PPR']['First'][1].extend([['b', precise], ['c', 0.0]])
            after['PPR']['Last'][1].pop()
            update_blocks(p, before, after, expected_sha256=W.sha(p))
            self.assertEqual(W.read_book(p), after)
            with ZipFile(p) as z:
                changed = [n for n, value in parts.items() if z.read(n) != value]
            self.assertEqual(changed, ['xl/worksheets/sheet1.xml'])

    def test_stale_input_rejected_without_write(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'region.xlsx'
            b = {'PPR': {'Matching': (['taxon'], [['a']])}}
            W.write_book(p, b)
            original = p.read_bytes()
            with self.assertRaises(AssertionError):
                update_blocks(p, b, b, expected_sha256='stale')
            self.assertEqual(p.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
