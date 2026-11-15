"""Real transaction checks for the one authorized review amendment.

Only disposable files are changed. Registration and the publication gate are
substituted at their boundary; the actual journal, replacement and guards run.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from promote_humboldt_review import publish_review
from tools.project_core.registry.publication import publication_transaction
from tools.project_core.validation.researcher_review import STATUS


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class ReviewPromotionTransactionTests(unittest.TestCase):
    def setUp(self):
        # Keep all temporary writes in this authorized model-local work folder.
        self.temp = tempfile.TemporaryDirectory(prefix='review-test-', dir=Path(__file__).resolve().parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.work = self.root / 'work'
        (self.work / 'inputs').mkdir(parents=True)
        self.project = self.root / 'Project.xlsx'
        self.project.write_bytes(b'original Project bytes with original signoff and exclusions')
        self.canonical = self.root / 'model/model_validation/validation.docx'
        self.canonical.parent.mkdir(parents=True)
        self.canonical.write_bytes(b'original signed report')
        self.staged = self.root / 'staged.docx'
        self.staged.write_bytes(b'approved diagnostic amendment')
        self.handoff = self.root / 'handoff.json'
        self.handoff.write_text('{}', encoding='utf-8')
        self.exclusions = ['Fishery offal', 'Pinnipeds', 'Seabirds', 'Chrysaora plocamia']
        self.before = ('Ido Carmel', '2026-10-08', {'status': STATUS, 'sections': ['original diagnostics']})
        self.after = ('Ido Carmel', '2026-10-08', {'status': STATUS, 'sections': ['amended diagnostics']})
        self.prepared = {
            'handoff': {
                'unit_id': 'LME_013', 'model_id': 'Chiaverano2018_detailed_Northern_Humboldt_1995_1998',
                'original_sha256': digest(self.canonical), 'staged_sha256': digest(self.staged),
            },
            'handoff_path': self.handoff, 'handoff_sha256': digest(self.handoff),
            'canonical': self.canonical, 'staged': self.staged,
            'before': copy.deepcopy(self.before), 'after': copy.deepcopy(self.after),
            'excluded_seq': [39, 32, 31, 7], 'excluded_group_ids': self.exclusions[:],
        }
        self.registration = {
            'researcher_review_status': STATUS,
            'researcher_review_summary': json.dumps({'excluded_group_ids': self.exclusions}),
            'researcher_name': 'Ido Carmel', 'researcher_review_date': '2026-10-08',
        }
        self.project_before = self.project.read_bytes()
        self.canonical_before = self.canonical.read_bytes()
        self.staged_before = self.staged.read_bytes()

    @property
    def original(self):
        return self.canonical.parent / 'evidence/ee_floor_amendment_20261115/original_signed_validation.docx'

    @property
    def previous(self):
        return self.work / 'inputs/Project_before_humboldt_review.xlsx'

    def register(self, project, report, unit, model, excluded_seq):
        # The real registration atomically writes Project and returns metadata.
        self.assertEqual((Path(project), Path(report)), (self.project, self.canonical))
        self.assertEqual((unit, model), ('LME_013', 'Chiaverano2018_detailed_Northern_Humboldt_1995_1998'))
        self.assertEqual(excluded_seq, [39, 32, 31, 7])
        self.assertEqual(self.canonical.read_bytes(), self.staged_before)
        self.project.write_bytes(json.dumps(self.registration, sort_keys=True).encode())
        return copy.deepcopy(self.registration)

    def invoke(self, gate):
        with patch('tools.project_core.validation.researcher_review.read_report', return_value=copy.deepcopy(self.after)), \
             patch('tools.project_core.validation.researcher_review._register_review', side_effect=self.register), \
             patch('tools.project_core.maps.build_html._refresh_reviews', side_effect=gate):
            # No model scope: these dummy bytes are never parsed as a workbook.
            with publication_transaction(self.root):
                return publish_review(self.root, self.work, self.prepared)

    def assert_rolled_back(self):
        self.assertEqual(self.project.read_bytes(), self.project_before)
        self.assertEqual(self.canonical.read_bytes(), self.canonical_before)
        self.assertEqual(self.staged.read_bytes(), self.staged_before)
        self.assertFalse(self.previous.exists())
        self.assertFalse(self.original.exists())
        self.assertEqual(list(self.canonical.parent.glob('.review-promote-*')), [])

    def test_review_gate_failure_restores_project_and_signed_docx_exactly(self):
        def reject(project, previous, units, **kwargs):
            self.assertEqual(Path(previous).read_bytes(), self.project_before)
            self.assertNotEqual(Path(project).read_bytes(), self.project_before)
            self.assertEqual(units, [])
            self.assertEqual(kwargs, {'model_pairs': {('LME_013', 'Chiaverano2018_detailed_Northern_Humboldt_1995_1998')}, 'publish': True})
            raise ValueError('review page gate rejected candidate')
        with self.assertRaisesRegex(ValueError, 'review page gate rejected candidate'):
            self.invoke(reject)
        self.assert_rolled_back()

    def test_success_retains_exact_signoff_and_exclusions(self):
        result = self.invoke(lambda *args, **kwargs: None)
        actual = json.loads(self.project.read_bytes())
        self.assertEqual(actual['researcher_name'], 'Ido Carmel')
        self.assertEqual(actual['researcher_review_date'], '2026-10-08')
        self.assertEqual(json.loads(actual['researcher_review_summary'])['excluded_group_ids'], self.exclusions)
        self.assertEqual(actual['researcher_review_status'], STATUS)
        self.assertEqual(result['excluded_group_ids'], self.exclusions)
        self.assertEqual(self.previous.read_bytes(), self.project_before)
        self.assertEqual(self.original.read_bytes(), self.canonical_before)
        self.assertEqual(self.canonical.read_bytes(), self.staged_before)
        self.assertEqual(self.staged.read_bytes(), self.staged_before)

    def test_changed_reviewer_or_date_is_rejected_and_rolled_back(self):
        for field, replacement in [('researcher_name', 'Another reviewer'), ('researcher_review_date', '2026-11-15')]:
            with self.subTest(field=field):
                saved = self.registration[field]
                self.registration[field] = replacement
                with self.assertRaisesRegex(ValueError, 'Original signoff changed'):
                    self.invoke(lambda *args, **kwargs: self.fail('Gate reached with altered signoff'))
                self.assert_rolled_back()
                self.registration[field] = saved

    def test_changed_exclusion_membership_or_order_is_rejected_and_rolled_back(self):
        for changed in [self.exclusions[:-1], list(reversed(self.exclusions))]:
            with self.subTest(exclusions=changed):
                self.registration['researcher_review_summary'] = json.dumps({'excluded_group_ids': changed})
                with self.assertRaisesRegex(ValueError, 'Researcher group exclusions changed'):
                    self.invoke(lambda *args, **kwargs: self.fail('Gate reached with altered exclusions'))
                self.assert_rolled_back()

    def test_changed_validation_verdict_is_rejected_and_rolled_back(self):
        self.registration['researcher_review_status'] = 'MODEL DISQUALIFIED'
        with self.assertRaisesRegex(ValueError, 'lost its validated decision'):
            self.invoke(lambda *args, **kwargs: self.fail('Gate reached with altered decision'))
        self.assert_rolled_back()

    def test_changed_staged_bytes_are_rejected_before_any_write(self):
        self.staged.write_bytes(b'changed after QA')
        with self.assertRaisesRegex(ValueError, 'handoff changed before promotion'):
            self.invoke(lambda *args, **kwargs: self.fail('Gate reached with altered handoff'))
        self.assertEqual(self.project.read_bytes(), self.project_before)
        self.assertEqual(self.canonical.read_bytes(), self.canonical_before)
        self.assertFalse(self.previous.exists())
        self.assertFalse(self.original.exists())

    def test_different_historical_signed_report_is_not_overwritten(self):
        self.original.parent.mkdir(parents=True)
        self.original.write_bytes(b'previous historical evidence')
        with self.assertRaisesRegex(ValueError, 'Historical signed report already exists'):
            self.invoke(lambda *args, **kwargs: self.fail('Gate reached with historical collision'))
        self.assertEqual(self.original.read_bytes(), b'previous historical evidence')
        self.assertEqual(self.project.read_bytes(), self.project_before)
        self.assertEqual(self.canonical.read_bytes(), self.canonical_before)
        self.assertFalse(self.previous.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
