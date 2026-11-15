"""Cached adoption authenticates immutable returns without scientific execution."""
import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import adopt_completion as adoption


class CachedAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.model = self.root/'model.json'
        self.model.write_text('{}')
        self.cache = self.root/'calculated'
        self.cache.mkdir()
        self.identity = {'model_id': self.root.name, 'model_sha256': adoption.sha(self.model),
                         'flags': {'constructor': {'normalize_DC': True}},
                         'engine_hashes': {'PPRCalculator.py': 'exact engine'},
                         'adapter_sha256': 'recorded adapter', 'environment': {'python': 'recorded'}}
        self.outcome = {'status': 'ok', 'reason': '', 'scopes': {'all': {'Fish': 7.}},
                        'annual_status': {'all': 'ok'}, 'settings': {'method': 'SPPR_1986'}}
        document = {**self.outcome, 'identity': self.identity}
        evidence = self.cache/'SPPR_1986.json.gz'
        evidence.write_bytes(gzip.compress(json.dumps(document).encode()))
        constructor = self.cache/'constructor.json.gz'
        constructor.write_bytes(gzip.compress(json.dumps({'identity': self.identity,
            'constructor_outcome': {'status': 'ready', 'runtime': {'retained': True}}}).encode()))
        self.outcome.update(execution_identity=copy.deepcopy(self.identity),
            evidence={'path': evidence.name, 'sha256': adoption.sha(evidence)},
            constructor_evidence={'path': constructor.name, 'sha256': adoption.sha(constructor)})
        self.cache_path = self.cache/'calculated.json'
        self.cache_path.write_text(json.dumps({'methods': {'SPPR_1986': self.outcome}}))
        self.patcher = patch.object(adoption, 'authenticate_identity', return_value={self.model: adoption.sha(self.model)})
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def record(self):
        return adoption.verify_method(self.model, self.cache, 'SPPR_1986', self.outcome)

    def test_callback_copies_exact_method_and_constructor_without_running_engine(self):
        callback = adoption.CachedBatch(self.model, self.cache_path, {'SPPR_1986': self.record()})
        output = self.root/'output'
        output.mkdir()
        with patch.object(adoption.adapter, 'compute_methods', side_effect=AssertionError('scientific rerun')):
            result = callback(self.model, self.identity['flags'], ['SPPR_1986'], output, progress=lambda _: None)
        outcome = result['methods']['SPPR_1986']
        self.assertEqual(outcome['execution_identity'], self.identity)
        self.assertEqual(adoption.sha(output/outcome['evidence']['path']), self.outcome['evidence']['sha256'])
        self.assertEqual(adoption.sha(output/result['constructor_evidence']['path']), self.outcome['constructor_evidence']['sha256'])

    def test_summary_mismatch_rejected(self):
        self.outcome['scopes']['all']['Fish'] = 99.
        with self.assertRaisesRegex(ValueError, 'summary|scopes'):
            self.record()

    def test_changed_evidence_after_preflight_rejected_before_output(self):
        callback = adoption.CachedBatch(self.model, self.cache_path, {'SPPR_1986': self.record()})
        (self.cache/'SPPR_1986.json.gz').write_bytes(b'changed')
        output = self.root/'output'
        output.mkdir()
        with self.assertRaisesRegex(ValueError, 'changed|hash'):
            callback(self.model, self.identity['flags'], ['SPPR_1986'], output, progress=lambda _: None)
        self.assertEqual(list(output.iterdir()), [])

    def test_mixed_execution_identities_cannot_share_one_callback(self):
        first = self.record()
        second = copy.deepcopy(first)
        second['identity']['engine_hashes']['PPRCalculator.py'] = 'different engine'
        with self.assertRaisesRegex(ValueError, 'identity|identities'):
            adoption.CachedBatch(self.model, self.cache_path, {'SPPR_1986': first, 'SPPR_1995_TE0.1': second})

    def test_mc_and_unrequested_method_are_rejected(self):
        callback = adoption.CachedBatch(self.model, self.cache_path, {'SPPR_1986': self.record()})
        output = self.root/'output'
        output.mkdir()
        with self.assertRaisesRegex(ValueError, 'requested|Monte Carlo'):
            callback(self.model, self.identity['flags'], ['MC_new_GE'], output, progress=lambda _: None)
        self.assertEqual(list(output.iterdir()), [])


class ControlProvenanceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.model = self.root / 'model.json'
        self.model.write_text('{}')
        self.original = self.save('results/result_manifest.json', b'reviewed manifest')
        self.relocated_manifest = self.save(
            'results/diagnostics/method_coverage/deterministic_completion_20261114/inputs/accepted_result_manifest.json',
            b'reviewed manifest')

    def save(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return {'relative_path': name, 'sha256': adoption.sha(path)}

    def flags(self):
        return {'constructor': {'normalize_DC': True},
                'audited_replay': {'mode': 'completed_runtime',
                    'provenance': copy.deepcopy(self.original),
                    'runtime': {'relative_path': 'retained/runtime.json', 'sha256': 'b' * 64}}}

    def relocated(self, flags):
        result = copy.deepcopy(flags)
        result['audited_replay']['provenance']['relative_path'] = (
            'results/diagnostics/method_coverage/deterministic_completion_20261114/'
            'inputs/accepted_result_manifest.json')
        return result

    def test_same_authenticated_provenance_hash_accepts_relocation(self):
        control = self.flags()
        executed = self.relocated(control)
        before = copy.deepcopy((control, executed))
        adoption.check_control_settings(control, executed, self.model)
        self.assertEqual((control, executed), before)

    def test_changed_or_missing_provenance_hash_rejects_relocation(self):
        for old_hash, new_hash in [('a' * 64, 'c' * 64), ('', ''), (None, None)]:
            with self.subTest(old_hash=old_hash, new_hash=new_hash):
                control = self.flags()
                control['audited_replay']['provenance']['sha256'] = old_hash
                executed = self.relocated(control)
                executed['audited_replay']['provenance']['sha256'] = new_hash
                with self.assertRaisesRegex(ValueError, 'flags|provenance|control'):
                    adoption.check_control_settings(control, executed, self.model)

    def dependency_flags(self, relocate=False):
        control = self.flags()
        control.update(engine_sources={}, engine_source_hashes={}, configuration_evidence=[])
        for name in ['PPRCalculator.py', 'ModelData.py', 'utils.py']:
            ref = self.save('original/' + name, ('# ' + name).encode())
            control['engine_sources'][name] = ref['relative_path']
            control['engine_source_hashes'][name] = ref['sha256']
        executed = copy.deepcopy(control)
        if relocate:
            old = control['engine_sources']['utils.py']
            ref = self.save('relocated/utils.py', (self.root / old).read_bytes())
            executed['engine_sources']['utils.py'] = ref['relative_path']
            for flags in (control, executed):
                flags['configuration_evidence'].append({
                    'relative_path': flags['engine_sources']['utils.py'],
                    'sha256': flags['engine_source_hashes']['utils.py'],
                    'original_source_hash': adoption.sha(self.model)})
        else:
            executed['configuration_evidence'] = [
                {'relative_path': path, 'sha256': executed['engine_source_hashes'][name],
                 'original_source_hash': adoption.sha(self.model)}
                for name, path in executed['engine_sources'].items()]
        return control, executed

    def test_identical_engine_dependency_relocation_is_accepted_without_mutation(self):
        control, executed = self.dependency_flags(relocate=True)
        before = copy.deepcopy((control, executed))
        try:
            verified = adoption.check_control_settings(control, executed, self.model)['immutable']
        except ValueError as error:
            self.fail('Identical dependency relocation rejected: ' + str(error))
        self.assertEqual((control, executed), before)
        for path in ['original/utils.py', 'relocated/utils.py']:
            self.assertEqual(verified[self.root / path], control['engine_source_hashes']['utils.py'])

    def test_redundant_evidence_for_identical_engine_dependencies_is_accepted_without_mutation(self):
        control, executed = self.dependency_flags()
        before = copy.deepcopy((control, executed))
        try:
            verified = adoption.check_control_settings(control, executed, self.model)['immutable']
        except ValueError as error:
            self.fail('Already authenticated dependency evidence rejected: ' + str(error))
        self.assertEqual((control, executed), before)
        for name, path in control['engine_sources'].items():
            self.assertEqual(verified[self.root / path], control['engine_source_hashes'][name])

    def test_provenance_relocation_requires_both_retained_files(self):
        control = self.flags()
        executed = self.relocated(control)
        (self.root / self.relocated_manifest['relative_path']).write_bytes(b'changed manifest')
        with self.assertRaises(ValueError):
            adoption.check_control_settings(control, executed, self.model)

    def test_live_manifest_is_checked_before_write_and_archive_remains_immutable(self):
        control = self.flags()
        executed = self.relocated(control)
        before = copy.deepcopy((control, executed))
        guards = adoption.check_control_settings(control, executed, self.model)
        consumed = guards['consumed']
        immutable = guards['immutable']
        adoption.check_hashes(consumed)
        (self.root / self.original['relative_path']).write_bytes(b'new adopted manifest')
        with self.assertRaises(ValueError):
            adoption.check_hashes(consumed)
        try:
            adoption.check_hashes(immutable)
        except ValueError as error:
            self.fail('Authorized live manifest write invalidated immutable evidence: ' + str(error))
        (self.root / self.relocated_manifest['relative_path']).write_bytes(b'changed archive')
        with self.assertRaises(ValueError):
            adoption.check_hashes(immutable)
        self.assertEqual((control, executed), before)

    def test_other_original_provenance_files_remain_immutable(self):
        control = self.flags()
        control['audited_replay']['provenance'] = self.save('historical/manifest.json', b'reviewed manifest')
        executed = self.relocated(control)
        guards = adoption.check_control_settings(control, executed, self.model)
        immutable = guards['immutable']
        (self.root / 'historical/manifest.json').write_bytes(b'changed original evidence')
        with self.assertRaises(ValueError):
            adoption.check_hashes(immutable)

    def test_live_manifest_reused_as_engine_dependency_is_still_immutable(self):
        control, executed = self.dependency_flags(relocate=True)
        for flags, path in [(control, self.original['relative_path']), (executed, 'relocated/utils.py')]:
            self.save(path, b'reviewed manifest')
            flags['engine_sources']['utils.py'] = path
            flags['engine_source_hashes']['utils.py'] = self.original['sha256']
            flags['configuration_evidence'][0].update(relative_path=path, sha256=self.original['sha256'])
        executed = self.relocated(executed)
        guards = adoption.check_control_settings(control, executed, self.model)
        immutable = guards['immutable']
        self.assertIn(self.root / self.original['relative_path'], immutable)
        (self.root / self.original['relative_path']).write_bytes(b'changed engine dependency')
        with self.assertRaises(ValueError):
            adoption.check_hashes(immutable)

    def test_existing_configuration_evidence_cannot_be_removed(self):
        _, control = self.dependency_flags()
        executed = copy.deepcopy(control)
        executed['configuration_evidence'].pop()
        with self.assertRaises(ValueError):
            adoption.check_control_settings(control, executed, self.model)

    def test_engine_relocation_rejects_changed_or_missing_dependency_bytes(self):
        for side in ['original', 'relocated']:
            for content in [None, b'changed engine']:
                with self.subTest(side=side, content=content):
                    control, executed = self.dependency_flags(relocate=True)
                    target = self.root / (side + '/utils.py')
                    if content is None:
                        target.unlink()
                    else:
                        target.write_bytes(content)
                    with self.assertRaises(ValueError):
                        adoption.check_control_settings(control, executed, self.model)

    def test_engine_relocation_rejects_changed_hashes_settings_and_extra_evidence_fields(self):
        for change in ['hash', 'constructor', 'original_source_hash', 'evidence_annotation']:
            with self.subTest(change=change):
                control, executed = self.dependency_flags(relocate=True)
                if change == 'hash':
                    executed['engine_source_hashes']['utils.py'] = 'c' * 64
                elif change == 'constructor':
                    executed['constructor']['normalize_DC'] = False
                elif change == 'original_source_hash':
                    executed['configuration_evidence'][0]['original_source_hash'] = 'c' * 64
                else:
                    executed['configuration_evidence'][0]['json_pointer'] = '/changed'
                with self.assertRaises(ValueError):
                    adoption.check_control_settings(control, executed, self.model)

    def test_added_evidence_requires_current_bytes_model_binding_and_shared_engine_identity(self):
        for change in ['bytes', 'model_hash', 'undeclared_dependency', 'engine_hash']:
            with self.subTest(change=change):
                control, executed = self.dependency_flags()
                ref = executed['configuration_evidence'][0]
                if change == 'bytes':
                    (self.root / ref['relative_path']).write_bytes(b'changed after execution')
                elif change == 'model_hash':
                    ref['original_source_hash'] = 'c' * 64
                elif change == 'undeclared_dependency':
                    ref['relative_path'] = self.save('other/PPRCalculator.py', b'other dependency')['relative_path']
                else:
                    executed['engine_source_hashes']['PPRCalculator.py'] = 'c' * 64
                with self.assertRaises(ValueError):
                    adoption.check_control_settings(control, executed, self.model)

    def test_dependency_relocation_cannot_escape_model_directory(self):
        control, executed = self.dependency_flags(relocate=True)
        executed['engine_sources']['utils.py'] = '../utils.py'
        executed['configuration_evidence'][0]['relative_path'] = '../utils.py'
        with self.assertRaises(ValueError):
            adoption.check_control_settings(control, executed, self.model)


if __name__ == '__main__':
    unittest.main()
