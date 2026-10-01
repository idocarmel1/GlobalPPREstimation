"""End-to-end guards for reviewed missing paper records; only synthetic workbooks."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import apply_reviewed_metadata as subject


class SourceInsertTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.old_root, self.old_here = subject.ROOT, subject.HERE
        subject.ROOT = subject.HERE = self.root
        self.addCleanup(self.restore_paths)
        self.project = self.root / 'Project.xlsx'
        self.book = {
            'Papers': {'Papers': (['article_id', 'unit_id', 'title', 'selected', 'target_coverage_ratio'],
                                   [['old', 'LME_035', 'Unrelated source', False, None]])},
            'Models & coverage': {'Models': (['unit_id', 'model_id', 'paper_ids'],
                                              [['LME_035', 'accepted1963', None]])},
            'Protected': {'Inputs': (['group', 'B', 'PB'], [['accepted', 1.412971356337523, 0.0]])},
        }
        subject.write_book(self.project, self.book)
        self.before_sha = subject.sha(self.project)
        self.plan = {'regional_inputs': [], 'patches': [], 'record_inserts': [{
            'sheet': 'Papers', 'table': 'Papers', 'key': {'article_id': 'new', 'unit_id': 'LME_035'},
            'expected_old': 'record_absent',
            'proposed': {'article_id': 'new', 'unit_id': 'LME_035', 'title': 'Reviewed source',
                         'selected': True, 'target_coverage_ratio': 0.46879416652121647},
            'evidence': 'retained source identity',
        }]}

    def restore_paths(self):
        subject.ROOT, subject.HERE = self.old_root, self.old_here

    def run_plan(self, execute=True):
        path = self.root / 'plan.json'
        path.write_text(json.dumps(self.plan), encoding='utf-8')
        subject.apply(path, execute)

    def test_reviewed_new_paper_preserves_existing_rows_and_unrelated_values(self):
        self.run_plan()
        result = subject.read_book(self.project)
        self.assertEqual(result['Papers']['Papers'][1], [self.book['Papers']['Papers'][1][0],
                          ['new', 'LME_035', 'Reviewed source', True, 0.4687941665212165]])
        self.assertEqual(result['Protected'], self.book['Protected'])
        self.assertEqual(result['Models & coverage'], self.book['Models & coverage'])
        receipt = json.loads((self.root / 'plan_applied.json').read_text(encoding='utf-8'))
        self.assertTrue(receipt['preserved_unrelated_content'])
        self.assertEqual(len(receipt['record_inserts']), 1)

    def test_dry_run_has_no_workbook_mutation(self):
        self.run_plan(False)
        self.assertEqual(subject.sha(self.project), self.before_sha)
        receipt = json.loads((self.root / 'plan_dry_run.json').read_text(encoding='utf-8'))
        self.assertEqual(len(receipt['record_inserts']), 1)

    def test_existing_article_id_even_with_different_unit_is_rejected(self):
        self.plan['record_inserts'][0]['key'] = {'article_id': 'old', 'unit_id': 'LME_999'}
        self.plan['record_inserts'][0]['proposed'].update(article_id='old', unit_id='LME_999')
        with self.assertRaises(ValueError):
            self.run_plan()
        self.assertEqual(subject.sha(self.project), self.before_sha)

    def test_absence_precondition_is_required(self):
        del self.plan['record_inserts'][0]['expected_old']
        with self.assertRaises(ValueError):
            self.run_plan()
        self.assertEqual(subject.sha(self.project), self.before_sha)

    def test_unknown_field_and_key_disagreement_rejected(self):
        original = copy.deepcopy(self.plan)
        for field, value in [('unreviewed_field', 3), ('article_id', 'different')]:
            self.plan = copy.deepcopy(original)
            self.plan['record_inserts'][0]['proposed'][field] = value
            with self.assertRaises(ValueError):
                self.run_plan()
            self.assertEqual(subject.sha(self.project), self.before_sha)

    def test_unrelated_table_insert_rejected(self):
        self.plan['record_inserts'][0].update(sheet='Protected', table='Inputs')
        with self.assertRaises(ValueError):
            self.run_plan()
        self.assertEqual(subject.sha(self.project), self.before_sha)

    def test_regional_evidence_changed_during_backup_rejects_before_save(self):
        regional = self.root / 'handoff.json'
        regional.write_text('reviewed original evidence', encoding='utf-8')
        self.plan['regional_inputs'] = [{'path': 'handoff.json', 'sha256': subject.sha(regional)}]
        real_copy = subject.shutil.copy2

        def copy_and_change_evidence(source, target):
            result = real_copy(source, target)
            regional.write_text('changed during backup', encoding='utf-8')
            return result

        with mock.patch.object(subject.shutil, 'copy2', side_effect=copy_and_change_evidence):
            with self.assertRaises(ValueError):
                self.run_plan()
        self.assertEqual(subject.sha(self.project), self.before_sha)


if __name__ == '__main__':
    unittest.main()
