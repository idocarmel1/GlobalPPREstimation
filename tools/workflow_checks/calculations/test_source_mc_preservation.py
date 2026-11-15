"""Untouched source MC diagnostics retain exact values and empty-row shape."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from xml.etree import ElementTree as etree

import openpyxl

from tools.project_core.calculations.coverage import _update_source
from tools.project_core.validation.researcher_review import S, sheet_xml
from tools.project_core.workbooks.workbooks import sha


class SourceMCPreservationTests(unittest.TestCase):
    precise = 0.12345678912345678

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / 'sppr_source.xlsx'

    def fixture(self, mc_rows, *, empty_row=False, existing_mc=False):
        workbook = openpyxl.Workbook()
        workbook.remove(workbook.active)
        for scope in ('all', 'inner', 'PP'):
            sheet = workbook.create_sheet('sppr_' + scope)
            sheet.append(['seq', 'group_name', 'new_GE', *(['MC_GE'] if existing_mc else [])])
            sheet.append([1, 'Fish', 5.0, *([6.0] if existing_mc else [])])
        sheet = workbook.create_sheet('mc_diagnostics')
        for row in mc_rows:
            sheet.append(row)
        workbook.save(self.path)
        workbook.close()
        with zipfile.ZipFile(self.path) as archive:
            member, sheet = sheet_xml(archive, 'mc_diagnostics')
            if empty_row:
                etree.SubElement(sheet.find(f'{{{S}}}sheetData'), f'{{{S}}}row', {'r': '2'})
                sheet.find(f'{{{S}}}dimension').set('ref', 'A1:D2')
            for cell in sheet.iter(f'{{{S}}}c'):
                if cell.get('r') == 'B2' and cell.get('t') == 'n':
                    cell.find(f'{{{S}}}v').text = repr(self.precise)
            parts = [(info, etree.tostring(sheet) if info.filename == member else archive.read(info.filename))
                     for info in archive.infolist()]
        with zipfile.ZipFile(self.path, 'w') as archive:
            for info, content in parts:
                archive.writestr(info, content)
        return {'Selected model groups': {
            'Groups': (['seq', 'group_name'], [[1, 'Fish']]),
            'Group SPPR': (['model_id', 'group', 'scope', 'method', 'sppr'],
                           [['M', 'Fish', scope, method, coefficient]
                            for scope in ('all', 'inner', 'PP')
                            for method, coefficient in [('new_GE', 5.0), *([('MC_GE', 6.0)] if existing_mc else [])]])},
            'Diagnostics': {'mc_diagnostics': (['method', 'reject_frac', 'status', 'flag'],
                                              [['MC_GE', 0.25, 'new result', True]])}}

    def state(self):
        workbook = openpyxl.load_workbook(self.path, read_only=True)
        try:
            values = tuple(tuple((type(value).__name__, repr(value)) for value in row)
                           for row in workbook['mc_diagnostics'].values)
        finally:
            workbook.close()
        with zipfile.ZipFile(self.path) as archive:
            _, sheet = sheet_xml(archive, 'mc_diagnostics')
        return values, sheet.find(f'{{{S}}}dimension').get('ref'), [
            row.get('r') for row in sheet.findall(f'{{{S}}}sheetData/{{{S}}}row') if not len(row)]

    def test_explicit_empty_mc_row_survives_no_mc_request(self):
        book = self.fixture([['method', 'reject_frac', 'status', 'flag']], empty_row=True)
        before = self.state()
        _update_source(self.path, book, {})
        self.assertEqual(self.state(), before)

    def test_completely_empty_mc_sheet_stays_empty(self):
        book = self.fixture([])
        before = self.state()
        _update_source(self.path, book, {})
        self.assertEqual(self.state(), before)

    def test_genuine_mc_values_stay_exact_without_mc_request(self):
        book = self.fixture([['method', 'reject_frac', 'status', 'flag'],
                             ['MC_GE', self.precise, 'retained failure', False]], existing_mc=True)
        before = self.state()
        _update_source(self.path, book, {'MC_GE': {'status': 'retained'}})
        self.assertEqual(self.state(), before)

    def test_unexpected_mc_value_change_rejects_before_replacement(self):
        for coordinate, value in [('C2', 'changed'), ('D2', 0), ('A9', 'hidden extra row')]:
            with self.subTest(coordinate=coordinate):
                book = self.fixture([['method', 'reject_frac', 'status', 'flag'],
                                     ['MC_GE', self.precise, 'retained failure', False]], existing_mc=True)
                before = sha(self.path)
                original_save = openpyxl.workbook.workbook.Workbook.save
                def mutate_then_save(workbook, filename):
                    workbook['mc_diagnostics'][coordinate] = value
                    return original_save(workbook, filename)
                with patch.object(openpyxl.workbook.workbook.Workbook, 'save', mutate_then_save):
                    with self.assertRaisesRegex(ValueError, 'Untouched MC diagnostics changed'):
                        _update_source(self.path, book, {})
                self.assertEqual(sha(self.path), before)

    def test_requested_mc_addition_and_replacement_are_allowed(self):
        for replacement in (False, True):
            with self.subTest(replacement=replacement):
                rows = [['method', 'reject_frac', 'status', 'flag']]
                if replacement:
                    rows.append(['MC_GE', self.precise, 'old', False])
                book = self.fixture(rows, existing_mc=replacement)
                if not replacement:
                    book['Selected model groups']['Group SPPR'][1].extend(
                        [['M', 'Fish', scope, 'MC_GE', 6.0] for scope in ('all', 'inner', 'PP')])
                _update_source(self.path, book, {'MC_GE': {'status': 'ok'}},
                               replace_methods={'MC_GE'} if replacement else ())
                workbook = openpyxl.load_workbook(self.path, read_only=True)
                try:
                    self.assertEqual(list(workbook['mc_diagnostics'].values)[1],
                                     ('MC_GE', 0.25, 'new result', True))
                finally:
                    workbook.close()


if __name__ == '__main__':
    unittest.main()
