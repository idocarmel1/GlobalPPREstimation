"""Signed exclusions resolve canonical and legacy IDs without changing science."""
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools.project_core.maps import build_html
from tools.project_core.validation import researcher_review as review
from tools.project_core.workbooks.workbooks import read_book, records, write_book
from tools.workflow_checks.validation import test_researcher_review_model_boundary as report_fixture


class ReviewGroupSequenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.region = self.root / 'regions/LME/LME_001/LME_001.xlsx'
        self.model = self.region.parent / 'papers/P/models/m/model.json'
        self.model.parent.mkdir(parents=True)
        self.model.write_text('{}')
        self.project = self.root / 'Project.xlsx'
        write_book(self.project, {'Models & coverage': {'Models': (
            ['unit_id', 'model_id', 'model_path'],
            [['LME_001', 'm', self.model.relative_to(self.root).as_posix()]])}})
        self.prior = self.root / 'previous.xlsx'
        shutil.copyfile(self.project, self.prior)
        self.report = report_fixture.ModelBoundaryTests().report(self.root, 'm')
        with zipfile.ZipFile(self.report) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()}
        parts['word/document.xml'] = parts['word/document.xml'].replace(
            b'No groups were removed from the calculation.',
            b'Removed groups from calculation: Seabirds (GE&lt;0.01%)')
        with zipfile.ZipFile(self.report, 'w') as archive:
            for name, value in parts.items(): archive.writestr(name, value)
        self.payloads = {
            'DB': {'network': {'units': {'LME_001': {'models': [{'id': 'm', 'values': [0, None, -2.5]}]}}}},
            'SERIES_DB': {'units': {'LME_001': {'models': [{'id': 'm', 'values': [0, None, -2.5]}]}}}}
        for filename, variable in [('index.html', 'DB'), ('trends.html', 'SERIES_DB')]:
            (self.root / filename).write_text(
                '<html><head><meta name="ppr-project-sha256" content="' + review.sha(self.prior)
                + '"></head><script>const ' + variable + '=' + json.dumps(self.payloads[variable])
                + ';</script></html>', encoding='utf-8')

    def groups(self, header, rows):
        write_book(self.region, {
            'Overview': {'Settings': (['field', 'value'], [['selected_model_id', 'm']])},
            'Selected model groups': {'Groups': (header, rows)}})

    def register(self, excluded=(1,)):
        return review.register_review(self.project, self.report, 'LME_001', 'm', list(excluded))

    def replay(self):
        # Exercise the actual signed-source and ZIP-part replay gate; layout
        # transformations have their own tests and do not govern ID selection.
        with patch.object(build_html, 'linked_layout', side_effect=lambda template: template):
            build_html._refresh_reviews(self.project, self.prior, ['LME_001'], self.root)

    def assert_registered_and_replayed(self, header, rows):
        self.groups(header, rows)
        before = {path: path.read_bytes() for path in [self.region, self.model, self.report]}
        source = review.read_report(self.root, self.report, 'm')
        registered = self.register()
        metadata = records(read_book(self.project), 'Models & coverage', 'Models')[0]
        approved = review.approved_review(self.root, metadata, read_book(self.region))
        self.assertEqual((registered['researcher_name'], registered['researcher_review_date']), source[:2])
        self.assertEqual(approved['sections'], source[2]['sections'])
        self.assertEqual(approved['excluded_group_ids'], ['Seabirds'])
        central = self.project.read_bytes()
        self.replay()
        self.assertEqual(self.project.read_bytes(), central)
        self.assertEqual({path: path.read_bytes() for path in before}, before)
        for filename, variable in [('index.html', 'DB'), ('trends.html', 'SERIES_DB')]:
            text = (self.root / filename).read_text(encoding='utf-8')
            marker = 'const ' + variable + '='
            payload, _ = json.JSONDecoder().raw_decode(text, text.index(marker) + len(marker))
            units = payload['network']['units'] if variable == 'DB' else payload['units']
            model = units['LME_001']['models'][0]
            self.assertEqual(model.pop('researcher_review'), approved)
            self.assertEqual(model.pop('display_ppr_excluded_group_ids'), ['Seabirds'])
            self.assertEqual(payload, self.payloads[variable])

    def test_canonical_group_seq_registers_and_replays_exact_signed_exclusion(self):
        self.assert_registered_and_replayed(['group_seq', 'group_name'], [['1.0', 'Seabirds'], [2, 'Fish']])

    def test_legacy_seq_registers_and_replays_same_source_decision(self):
        self.assert_registered_and_replayed(['seq', 'group_name'], [[1, 'Seabirds'], ['2.0', 'Fish']])

    def test_matching_canonical_and_legacy_aliases_are_accepted(self):
        self.assert_registered_and_replayed(['group_seq', 'seq', 'group_name'], [[1, '1.0', 'Seabirds'], [2, 2, 'Fish']])

    def test_conflicting_aliases_fail_before_central_write(self):
        self.groups(['group_seq', 'seq', 'group_name'], [[9, 1, 'Seabirds'], [2, 2, 'Fish']])
        before = self.project.read_bytes()
        with self.assertRaises(ValueError): self.register()
        self.assertEqual(self.project.read_bytes(), before)

    def test_missing_malformed_and_nonintegral_ids_fail_before_central_write(self):
        for value in [None, '', 'unknown', '1.5', 'true', 'NaN', 'Infinity']:
            with self.subTest(value=value):
                self.groups(['group_seq', 'group_name'], [[value, 'Seabirds'], [2, 'Fish']])
                before = self.project.read_bytes()
                with self.assertRaises(ValueError): self.register()
                self.assertEqual(self.project.read_bytes(), before)

    def test_duplicate_ids_cannot_mask_a_missing_requested_id(self):
        self.groups(['seq', 'group_name'], [[1, 'Seabirds'], [1, 'Fish']])
        before = self.project.read_bytes()
        with self.assertRaises(ValueError): self.register((1, 3))
        self.assertEqual(self.project.read_bytes(), before)

    def test_ambiguous_replay_keeps_central_and_both_pages_unchanged(self):
        self.groups(['seq', 'group_name'], [[1, 'Seabirds'], [2, 'Fish']])
        self.register()
        self.groups(['group_seq', 'seq', 'group_name'], [[9, 1, 'Seabirds'], [2, 2, 'Fish']])
        paths = [self.project, self.root / 'index.html', self.root / 'trends.html']
        before = {path: path.read_bytes() for path in paths}
        with self.assertRaises(ValueError): self.replay()
        self.assertEqual({path: path.read_bytes() for path in paths}, before)


if __name__ == '__main__': unittest.main()
