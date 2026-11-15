"""Each method keeps its own immutable, actually used initialization evidence."""
import copy
import gzip
import json
from contextlib import ExitStack
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from tools.scientific_helpers.sppr import method_coverage as adapter


class ConstructorEvidenceTests(unittest.TestCase):
    def read(self, directory, reference):
        path = directory/reference['path']
        self.assertEqual(adapter._hash_bytes(path.read_bytes()), reference['sha256'])
        return json.loads(gzip.decompress(path.read_bytes()))

    def stubs(self, keys, *, workers=(), runtimes=()):
        stack = ExitStack()
        registry = SimpleNamespace(SPEC_BY_KEY={key: SimpleNamespace(source_resolved=False) for key in keys})
        stack.enter_context(patch.object(adapter, '_engine', return_value=(registry,)))
        stack.enter_context(patch.object(adapter, '_constructor', return_value={}))
        stack.enter_context(patch.object(adapter, 'engine_identity', return_value={}))
        stack.enter_context(patch.object(adapter, 'method_settings',
            side_effect=lambda key, *_: {'method': key, 'source_resolved': False}))
        stack.enter_context(patch.object(adapter, '_load', return_value=(object(), {}, [])))
        stack.enter_context(patch.object(adapter, '_runtime', side_effect=list(runtimes)))
        stack.enter_context(patch.object(adapter, '_group_metadata', return_value=[{'name': 'local'}]))
        stack.enter_context(patch.object(adapter, '_run',
            side_effect=lambda model, settings: {'status': 'ok', 'reason': ''}))
        context = Mock()
        context.Pipe.side_effect = [(worker, Mock()) for worker in workers]
        process = Mock()
        process.is_alive.return_value = False
        context.Process.return_value = process
        stack.enter_context(patch.object(adapter.mp, 'get_context', return_value=context))
        return stack

    def test_ready_constructor_survives_timeout_then_failed_restart(self):
        first = Mock()
        first.recv.side_effect = [
            {'status': 'ready', 'runtime': {'value': 1}, 'groups': [{'name': 'first'}]},
            {'status': 'ok', 'reason': '', 'runtime_before': {'value': 1}}]
        first.poll.side_effect = [True, True, False]
        second = Mock()
        second.recv.return_value = {'status': 'constructor_failed', 'reason': 'replacement failed'}
        second.poll.return_value = True
        keys = ['first', 'timeout', 'replacement']
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model = root/'model.json'
            model.write_text('{}', encoding='utf-8')
            evidence = root/'evidence'
            with self.stubs(keys, workers=[first, second]):
                result = adapter.compute_methods(model, {}, keys, evidence, progress=None, method_timeout=1)
            outcomes = result['methods']
            self.assertEqual([outcomes[key]['status'] for key in keys], ['ok', 'timeout', 'NOT_RUN'])
            first_ref = outcomes['first']['constructor_evidence']
            self.assertEqual(first_ref, outcomes['timeout']['constructor_evidence'])
            last_ref = outcomes['replacement']['constructor_evidence']
            self.assertNotEqual(first_ref['path'], last_ref['path'])
            self.assertEqual(self.read(evidence, first_ref)['constructor_outcome']['status'], 'ready')
            self.assertEqual(self.read(evidence, last_ref)['constructor_outcome']['status'], 'constructor_failed')
            for key in keys:
                method = self.read(evidence, outcomes[key]['evidence'])
                self.assertEqual(method['constructor_evidence'], outcomes[key]['constructor_evidence'])

    def test_failed_worker_does_not_taint_existing_in_process_model(self):
        worker = Mock()
        worker.recv.return_value = {'status': 'constructor_failed', 'reason': 'worker unavailable'}
        worker.poll.return_value = True
        keys = ['local_first', 'worker', 'local_again']
        flags = {'method_timeout_overrides_seconds': {'worker': 1}}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model = root/'model.json'
            model.write_text('{}', encoding='utf-8')
            evidence = root/'evidence'
            with self.stubs(keys, workers=[worker], runtimes=[{'value': 4}]):
                result = adapter.compute_methods(model, flags, keys, evidence, progress=None, method_timeout=0)
            outcomes = result['methods']
            self.assertEqual([outcomes[key]['status'] for key in keys], ['ok', 'NOT_RUN', 'ok'])
            self.assertEqual(outcomes['local_first']['constructor_evidence'],
                             outcomes['local_again']['constructor_evidence'])
            last = self.read(evidence, outcomes['local_again']['evidence'])
            self.assertEqual(last['groups'], [{'name': 'local'}])

    def test_later_invocation_cannot_overwrite_prior_constructor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model = root/'model.json'
            model.write_text('{}', encoding='utf-8')
            evidence = root/'evidence'
            with self.stubs(['one', 'two'], runtimes=[{'value': 1}, {'value': 2}]):
                first = adapter.compute_methods(model, {}, ['one'], evidence, progress=None, method_timeout=0)
                old_ref = copy.deepcopy(first['methods']['one']['constructor_evidence'])
                old_contents = (evidence/old_ref['path']).read_bytes()
                second = adapter.compute_methods(model, {}, ['two'], evidence, progress=None, method_timeout=0)
            self.assertNotEqual(old_ref['path'], second['methods']['two']['constructor_evidence']['path'])
            self.assertEqual((evidence/old_ref['path']).read_bytes(), old_contents)
            self.assertEqual(self.read(evidence, old_ref)['constructor_outcome']['runtime'], {'value': 1})


if __name__ == '__main__':
    unittest.main()
