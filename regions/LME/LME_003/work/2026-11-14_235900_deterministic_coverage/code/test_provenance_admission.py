"""Initialization admission rejects overwritten or differently configured states."""
import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import provenance_admission as admission


class InitializationAdmissionTests(unittest.TestCase):
    def save(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(gzip.compress(json.dumps(value, sort_keys=True).encode(), mtime=0))
        return {'path': path.name, 'sha256': admission.sha(path)}

    def test_failed_constructor_cannot_authenticate_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = {'identity': {'a': 1}, 'status': 'ok', 'runtime_before': {'v': 2}}
            ref = self.save(root/'constructor.json.gz', {'identity': document['identity'],
                'constructor_outcome': {'status': 'constructor_failed'}})
            with self.assertRaisesRegex(ValueError, 'ready constructor'):
                admission.verify_initialization(root/'model.json', root, 'test',
                                                {'constructor_evidence': ref}, document)

    def test_ready_constructor_must_match_runtime_and_groups(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = {'identity': {'a': 1}, 'status': 'ok', 'runtime_before': {'v': 2}, 'groups': [1]}
            initial = {'status': 'ready', 'runtime': {'v': 2}, 'groups': [1]}
            for field, value in [('runtime', {'v': 3}), ('groups', [2])]:
                changed = {**initial, field: value}
                ref = self.save(root/'constructor.json.gz', {'identity': document['identity'], 'constructor_outcome': changed})
                with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'runtime|group'):
                    admission.verify_initialization(root/'model.json', root, 'test', {'constructor_evidence': ref}, document)
            ref = self.save(root/'constructor.json.gz', {'identity': document['identity'], 'constructor_outcome': initial})
            valid = admission.verify_initialization(root/'model.json', root, 'test', {'constructor_evidence': ref}, document)
            self.assertEqual(valid['evidence_kind'], 'original_constructor')

    def test_not_run_binds_the_actual_failed_constructor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            failed = {'status': 'constructor_failed', 'reason': 'unavailable'}
            document = {'identity': {'a': 1}, 'status': 'NOT_RUN', 'constructor_outcome': failed}
            ref = self.save(root/'constructor.json.gz', {'identity': document['identity'], 'constructor_outcome': failed})
            admission.verify_initialization(root/'model.json', root, 'test', {'constructor_evidence': ref}, document)
            document['constructor_outcome'] = {'status': 'constructor_timeout'}
            with self.assertRaisesRegex(ValueError, 'NOT_RUN'):
                admission.verify_initialization(root/'model.json', root, 'test', {'constructor_evidence': ref}, document)

    def test_retrospective_record_keeps_original_failure_and_does_not_run_methods(self):
        with tempfile.TemporaryDirectory() as temporary:
            model_dir = Path(temporary)/admission.CAL_MODEL
            model_dir.mkdir()
            model = model_dir/'model.json'
            model.write_text('{}')
            cache = model_dir/'results/diagnostics/method_coverage/deterministic_completion_20261114/calculated'
            state = {'v': 4}
            groups = [{'id': 1, 'name': 'Fish'}]
            identity = {'model_id': model_dir.name, 'model_sha256': admission.sha(model), 'flags': {}, 'engine_hashes': {}}
            documents, hashes = {}, {}
            for key in admission.CAL_METHOD_HASHES:
                document = {'identity': identity, 'status': 'ok', 'groups': groups, 'runtime_before': state,
                            'runtime_before_sha256': admission._state_digest(state)}
                documents[key] = document
                hashes[key] = self.save(cache/'symbolic'/(key+'.json.gz'), document)['sha256']
            failed = {'identity': identity, 'constructor_outcome': {'status': 'constructor_failed', 'reason': 'adapter mismatch'}}
            failed_ref = self.save(cache/'symbolic/constructor.json.gz', failed)
            before = (cache/'symbolic/constructor.json.gz').read_bytes()
            with patch.dict(admission.CAL_METHOD_HASHES, hashes, clear=True), \
                 patch.object(admission, 'CAL_CONSTRUCTOR_SHA256', failed_ref['sha256']), \
                 patch.object(admission, 'CAL_RUNTIME_SHA256', admission._state_digest(state)), \
                 patch.object(admission, '_pinned_runtime', return_value=(state, {})), \
                 patch.object(admission.adapter, '_load', return_value=(object(), {}, [])), \
                 patch.object(admission.adapter, '_constructor', return_value={}), \
                 patch.object(admission.adapter, '_runtime', return_value=state), \
                 patch.object(admission.adapter, '_group_metadata', return_value=groups), \
                 patch.object(admission.adapter, 'engine_identity', return_value={}), \
                 patch.object(admission.adapter, '_run', side_effect=AssertionError('No scientific rerun')):
                result = admission.recover_california_v1(model, cache/'retrospective')
                self.assertFalse(result['record']['original_constructor_available'])
                self.assertFalse(result['record']['scientific_execution_performed'])
                self.assertNotIn('constructor_outcome', result['record'])
                for key, document in documents.items():
                    outcome = {**result['method_outcome_patches'][key],
                        'evidence': {'path': 'symbolic/'+key+'.json.gz', 'sha256': hashes[key]}}
                    verified = admission.verify_initialization(model, cache, key, outcome, document)
                    self.assertEqual(verified['evidence_kind'], admission.KIND)
                forged = copy.deepcopy(result['record'])
                forged['scientific_execution_performed'] = True
                bad = self.save(cache/'forged.json.gz', forged)
                outcome['runtime_verification_evidence'] = bad
                with self.assertRaisesRegex(ValueError, 'Unsupported retrospective'):
                    admission.verify_initialization(model, cache, key, outcome, document)
            self.assertEqual((cache/'symbolic/constructor.json.gz').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
