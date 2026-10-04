"""Native Windows access remains inherited after complete snapshot promotion."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest
import uuid

from tools.project_core.calculations.snapshots import save_snapshot
from tools.project_core.registry.discovery import project_root
from tools.project_core.workbooks.workbooks import sha, write_book
from tools.workflow_checks.selection.test_snapshots import fixture


def inherited_access(path):
    script = (
        '$a=Get-Acl -LiteralPath $env:SNAPSHOT_ACCESS_TEST_PATH; '
        '[pscustomobject]@{protected=$a.AreAccessRulesProtected; '
        'allowed=@($a.Access | Where-Object AccessControlType -eq Allow | '
        'ForEach-Object {$_.IdentityReference.Value})} | ConvertTo-Json'
    )
    result = subprocess.run(
        ['powershell.exe', '-NoProfile', '-Command', script],
        env={**os.environ, 'SNAPSHOT_ACCESS_TEST_PATH': str(path)},
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


@unittest.skipUnless(os.name == 'nt', 'Native Windows access check')
class SnapshotAccessTests(unittest.TestCase):
    def test_promotion_preserves_normal_parent_access_and_exact_workbook(self):
        # A normal project directory is essential: system temporary directories
        # already have private ACLs, masking the promotion regression.
        root = project_root(__file__)
        qa = root / 'regions/LME/LME_028/work/2026-10-04_000005_final_checks/qa'
        base = qa / ('.snapshot-access-test-' + uuid.uuid4().hex)
        base.mkdir()
        self.assertTrue(base.resolve().is_relative_to(qa.resolve()))
        try:
            model = base / 'papers/P/models/A'
            model.mkdir(parents=True)
            (model / 'model.json').write_text('{"group":[{"group_seq":"1","group_name":"Fish"}]}')
            workbook = base / 'LME_001.xlsx'
            write_book(workbook, fixture())
            original = workbook.read_bytes()
            identity = {'model_id': 'A', 'canonical_model_sha256': sha(model / 'model.json')}
            for _ in range(2):
                snapshot = save_snapshot(workbook, model, result_identity=identity)
                self.assertEqual(snapshot.read_bytes(), original)
                parent_access = inherited_access(model / 'results')
                for member in (snapshot, model / 'results/result_manifest.json'):
                    access = inherited_access(member)
                    self.assertFalse(access['protected'], str(member))
                    self.assertLessEqual(set(parent_access['allowed']), set(access['allowed']))
                self.assertEqual(json.loads((model / 'results/result_manifest.json').read_text())['snapshot_sha256'], sha(workbook))
                self.assertEqual(list((model / 'results').glob('.snapshot-*')), [])
        finally:
            shutil.rmtree(base)
