"""Preserve exact prior diagnostic numbers when new options add columns."""
import copy
from pathlib import Path
import tempfile
import unittest
import zipfile
from xml.etree import ElementTree as etree

from tools.project_core.calculations.coverage import _restore_retained_numbers
from tools.project_core.validation.researcher_review import S, sheet_xml
from tools.project_core.workbooks.workbooks import read_book, records, sha, update_book, write_book


class RetainedDiagnosticNumbersTests(unittest.TestCase):
    field = 'model_input_p_max_rel_residual'
    # Exact saved LME014 GE/TE value; openpyxl's .16g changes its final bit.
    precise = 1.6724311166010748e-14
    new_number = 0.12345678912345678

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / 'region.xlsx'
        book = {'Diagnostics': {'model_health': (
            ['TE_option', self.field, 'status', 'flag'],
            [['GE', self.precise, 'FAIL', False], ['TE', self.precise, 'WARN', False]])}}
        write_book(self.path, book)
        # Supply a real saved workbook containing the exact original 17-digit
        # XML, independently of the preservation helper being tested.
        with zipfile.ZipFile(self.path) as archive:
            member, sheet = sheet_xml(archive, 'Diagnostics')
            for cell in sheet.iter(f'{{{S}}}c'):
                if cell.get('r') in ('B3', 'B4'):
                    cell.find(f'{{{S}}}v').text = repr(self.precise)
            parts = [(info, etree.tostring(sheet) if info.filename == member else archive.read(info.filename))
                     for info in archive.infolist()]
        with zipfile.ZipFile(self.path, 'w') as archive:
            for info, content in parts:
                archive.writestr(info, content)
        self.original = read_book(self.path)
        self.assertEqual(self.original['Diagnostics']['model_health'][1][0][1], self.precise)

    def expanded(self, reorder=False):
        prior = records(self.original, 'Diagnostics', 'model_health')
        header = ['TE_option', self.field, 'status', 'flag', 'divergence_sppr_det_35', 'divergence_sppr_det_36']
        if reorder:
            header = ['divergence_sppr_det_35', 'status', 'TE_option', 'flag', self.field, 'divergence_sppr_det_36']
            prior = list(reversed(prior))
        rows = [{**row, 'divergence_sppr_det_35': self.new_number} for row in prior]
        rows.append({'TE_option': 'With Egestion', self.field: 2.5, 'status': 'OK', 'flag': False,
                     'divergence_sppr_det_35': 3.5, 'divergence_sppr_det_36': 4.5})
        return {'Diagnostics': {'model_health': (header, [[row.get(key) for key in header] for row in rows])}}

    def test_appended_or_reordered_headers_restore_only_exact_old_fields(self):
        for reorder in (False, True):
            with self.subTest(reorder=reorder):
                requested = self.expanded(reorder)
                update_book(self.path, requested)
                before = {row['TE_option']: row for row in records(read_book(self.path), 'Diagnostics', 'model_health')}
                self.assertNotEqual(before['GE'][self.field], self.precise)
                _restore_retained_numbers(self.path, requested, self.original)
                after = {row['TE_option']: row for row in records(read_book(self.path), 'Diagnostics', 'model_health')}
                for option in ('GE', 'TE'):
                    self.assertEqual(after[option][self.field], self.precise)
                    self.assertEqual(after[option]['divergence_sppr_det_35'], before[option]['divergence_sppr_det_35'])
                    self.assertNotEqual(after[option]['divergence_sppr_det_35'], self.new_number)
                self.assertEqual(after['With Egestion'], before['With Egestion'])

    def test_changed_prior_value_status_option_or_boolean_prevents_whole_row_restoration(self):
        for field, replacement in [(self.field, self.new_number), ('status', 'OK'),
                                   ('TE_option', 'Changed GE'), ('flag', 0)]:
            with self.subTest(field=field):
                requested = self.expanded()
                header, rows = requested['Diagnostics']['model_health']
                rows[0][header.index(field)] = replacement
                update_book(self.path, requested)
                before = records(read_book(self.path), 'Diagnostics', 'model_health')
                _restore_retained_numbers(self.path, requested, self.original)
                after = records(read_book(self.path), 'Diagnostics', 'model_health')
                self.assertEqual(after[0][self.field], before[0][self.field])
                self.assertEqual(after[0][field], before[0][field])
                self.assertEqual(after[1][self.field], self.precise)

    def test_missing_renamed_or_duplicate_headers_cannot_match_an_intersection(self):
        for kind in ('missing', 'renamed', 'duplicate', 'duplicate_original'):
            with self.subTest(kind=kind):
                requested, original = self.expanded(), copy.deepcopy(self.original)
                header, rows = requested['Diagnostics']['model_health']
                if kind == 'missing':
                    index = header.index('status')
                    header.pop(index)
                    for row in rows:
                        row.pop(index)
                elif kind == 'renamed':
                    header[header.index('status')] = 'different_status'
                elif kind == 'duplicate':
                    header[-1] = 'status'
                else:
                    original['Diagnostics']['model_health'][0][-1] = 'status'
                update_book(self.path, requested)
                before = sha(self.path)
                self.assertFalse(_restore_retained_numbers(self.path, requested, original))
                self.assertEqual(sha(self.path), before)

    def test_projected_restoration_is_limited_to_model_health(self):
        requested, original = self.expanded(), copy.deepcopy(self.original)
        requested['Diagnostics']['other_table'] = requested['Diagnostics'].pop('model_health')
        original['Diagnostics']['other_table'] = original['Diagnostics'].pop('model_health')
        write_book(self.path, requested)
        before = sha(self.path)
        self.assertFalse(_restore_retained_numbers(self.path, requested, original))
        self.assertEqual(sha(self.path), before)

    def test_malformed_rows_do_not_receive_projected_restoration(self):
        requested = self.expanded()
        # Remove the newly appended trailing field; do not manufacture None.
        requested['Diagnostics']['model_health'][1][:] = [requested['Diagnostics']['model_health'][1][0][:-1]]
        update_book(self.path, requested)
        before = sha(self.path)
        self.assertFalse(_restore_retained_numbers(self.path, requested, self.original))
        self.assertEqual(sha(self.path), before)


if __name__ == '__main__':
    unittest.main()
