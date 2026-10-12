"""Researcher validation covers the extraction and the signed diagnostic findings."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.project_core.validation import researcher_review as review
from tools.project_core.workbooks.workbooks import read_book, records, write_book
from tools.workflow_checks.validation.test_researcher_disqualification import report_fixture


class ReviewScopeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.model = self.root / 'regions/LME/LME_001/papers/P/models/m/model.json'
        self.model.parent.mkdir(parents=True)
        self.model.write_text('{}')
        self.regional = self.root / 'regions/LME/LME_001/LME_001.xlsx'
        self.book = {
            'Overview': {'Settings': (['field', 'value'], [
                ['selected_model_id', 'm'], ['results_model_id', 'm'],
                ['calculation_input_sha256', 'original-calculation']])},
            'Selected model groups': {
                'Groups': (['seq', 'group_name'], [[1, 'Fish']]),
                'Group SPPR': (['method', 'sppr'], [['MC_new_GE', 2.]])},
            'Diagnostics': {'model_health': (['TE_option', 'status'], [['GE', 'WARN'], ['TE', 'FAIL']])}}
        write_book(self.regional, self.book)
        self.report = report_fixture(self.root, decision='MODEL VALIDATED', reason='')
        self.project = self.root / 'Project.xlsx'
        write_book(self.project, {'Models & coverage': {'Models': (
            ['unit_id', 'model_id', 'model_path'],
            [['LME_001', 'm', self.model.relative_to(self.root).as_posix()]])}})
        review.register_review(self.project, self.report, 'LME_001', 'm', [1])
        self.metadata = records(read_book(self.project), 'Models & coverage', 'Models')[0]

    def test_mc_additional_methods_and_downstream_inputs_do_not_revoke_signed_review(self):
        before = copy.deepcopy(self.metadata)
        approved = review.approved_review(self.root, self.metadata, self.book)
        changed = copy.deepcopy(self.book)
        changed['Overview']['Settings'][1][-1][1] = 'recalculated-inputs'
        changed['Selected model groups']['Group SPPR'][1][:] = [['MC_new_GE', 4.], ['added-method', None]]
        changed['Catch'] = {'Catch': (['taxon', 2000], [['Fish', 99.]])}
        changed['PPR'] = {'Annual': (['method', 'status', 2000], [['added-method', 'unavailable: FAIL', None]])}
        self.assertEqual(review.approved_review(self.root, self.metadata, changed), approved)
        self.assertEqual(approved['review_scope'], 'model_extraction_and_signed_sppr_diagnostics')
        self.assertIn('signed report', approved['diagnostic_scope_note'])
        self.assertEqual(self.metadata, before)

    def test_current_diagnostics_remain_separate_from_unchanged_signed_findings(self):
        approved = review.approved_review(self.root, self.metadata, self.book)
        changed = copy.deepcopy(self.book)
        changed['Diagnostics']['model_health'][1][0][1] = 'FAIL'
        self.assertEqual(review.approved_review(self.root, self.metadata, changed), approved)
        self.assertEqual(changed['Diagnostics']['model_health'][1][0][1], 'FAIL')
        tampered = copy.deepcopy(self.metadata)
        summary = json.loads(tampered['researcher_review_summary'])
        summary['sections'][1]['rows'][0]['text'] = 'GE OK; changed diagnostic finding'
        tampered['researcher_review_summary'] = json.dumps(summary)
        with self.assertRaisesRegex(ValueError, 'reviewed Word source'):
            review.approved_review(self.root, tampered, changed)

    def test_calculation_fingerprint_is_not_required_for_validation(self):
        self.book['Overview']['Settings'][1].pop()
        self.metadata['reviewed_calculation_input_sha256'] = ''
        self.assertEqual(review.approved_review(self.root, self.metadata, self.book)['status'], review.STATUS)

    def test_payload_calculation_bytes_do_not_revoke_model_validation(self):
        approved = review.approved_review(self.root, self.metadata, self.book)
        payload = {'id': 'm', 'verified': False, 'scopes': {'all': {'status': 'unavailable: FAIL'}},
                   'workbook_sha256': 'different-calculation-package'}
        review.attach_payload_review(self.root, self.metadata, self.book, payload, approved)
        self.assertEqual(payload['researcher_review'], approved)
        self.assertFalse(payload['verified'])
        self.assertEqual(payload['scopes']['all']['status'], 'unavailable: FAIL')

    def test_changed_model_or_signed_report_is_still_rejected(self):
        for path in (self.model, self.report):
            with self.subTest(path=path.name):
                original = path.read_bytes()
                path.write_bytes(original + b'changed')
                with self.assertRaisesRegex(ValueError, 'review source changed'):
                    review.approved_review(self.root, self.metadata, self.book)
                path.write_bytes(original)


if __name__ == '__main__':
    unittest.main()
