"""Transient Windows page-replacement retries preserve target bytes and rollback."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
RUN=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('atomic_retry_proposal',RUN/'outputs/build_html.atomic_retry.proposed.py')
build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
from tools.project_core.registry.publication import publication_transaction,publication_write

def denied(code=5):
    error=PermissionError('transient Windows sharing/access failure');error.winerror=code;return error

class AtomicRetryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=RUN/'qa');self.root=Path(self.tmp.name);self.addCleanup(self.tmp.cleanup)
        self.pages=self.root/'interactive_map';self.pages.mkdir();self.path=self.pages/'trends.html';self.path.write_bytes(b'original')
        self.replace=os.replace

    def test_transient_permissions_retry_under_guard(self):
        attempts=[]
        def replace(source,target):
            attempts.append(1)
            if len(attempts)<3:raise denied(32 if len(attempts)==1 else 5)
            return self.replace(source,target)
        with patch.object(build.os,'replace',side_effect=replace),patch('time.sleep') as sleep,patch('tools.project_core.registry.publication.publication_write',wraps=publication_write) as guard:
            build.atomic_bytes(self.path,b'new')
        self.assertEqual(self.path.read_bytes(),b'new');self.assertEqual(len(attempts),3)
        self.assertEqual(guard.call_count,3);self.assertEqual([call.args[0] for call in sleep.call_args_list],[.2,.4])
        self.assertEqual(list(self.pages.iterdir()),[self.path])

    def test_exhaustion_preserves_target_and_cleans_temp(self):
        with patch.object(build.os,'replace',side_effect=denied(33)) as replace,patch('time.sleep') as sleep:
            with self.assertRaises(PermissionError):build.atomic_bytes(self.path,b'new')
        self.assertEqual(replace.call_count,6);self.assertEqual(sleep.call_count,5)
        self.assertAlmostEqual(sum(c.args[0] for c in sleep.call_args_list),6.2)
        self.assertEqual(self.path.read_bytes(),b'original');self.assertEqual(list(self.pages.iterdir()),[self.path])

    def test_concurrent_author_change_stops_before_second_replace(self):
        def replace(source,target):
            Path(target).write_bytes(b'author edit');raise denied()
        with patch.object(build.os,'replace',side_effect=replace) as attempt,patch('time.sleep'):
            with self.assertRaisesRegex(ValueError,'changed'):build.atomic_bytes(self.path,b'new')
        self.assertEqual(attempt.call_count,1);self.assertEqual(self.path.read_bytes(),b'author edit')
        self.assertEqual(list(self.pages.iterdir()),[self.path])

    def test_transaction_restores_first_page_after_second_exhausts(self):
        (self.root/'Project.xlsx').write_bytes(b'project')
        first=self.pages/'index.html';first.write_bytes(b'old index')
        def replace(source,target):
            if Path(target)==self.path:raise denied()
            return self.replace(source,target)
        with patch.object(build.os,'replace',side_effect=replace),patch('time.sleep'):
            with self.assertRaises(PermissionError):
                with publication_transaction(self.root):
                    build.atomic_bytes(first,b'new index');build.atomic_bytes(self.path,b'new trends')
        self.assertEqual(first.read_bytes(),b'old index');self.assertEqual(self.path.read_bytes(),b'original')
        self.assertEqual(set(self.pages.iterdir()),{first,self.path})

    def test_other_permission_error_is_not_retried(self):
        with patch.object(build.os,'replace',side_effect=PermissionError('not Windows transient')) as replace,patch('time.sleep') as sleep:
            with self.assertRaises(PermissionError):build.atomic_bytes(self.path,b'new')
        self.assertEqual(replace.call_count,1);sleep.assert_not_called()
        self.assertEqual(self.path.read_bytes(),b'original');self.assertEqual(list(self.pages.iterdir()),[self.path])

if __name__=='__main__':unittest.main()
