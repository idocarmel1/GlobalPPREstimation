"""Authenticated completed runtimes must replay without constructor arithmetic."""
from copy import deepcopy
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from tools.scientific_helpers.sppr.method_coverage import encode_lossless


class AuditedRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.model = self.root / 'model.json'
        self.model.write_text('{"model": "test"}', encoding='utf-8')
        self.provenance = self.root / 'execution.json'
        self.provenance.write_text('{"scope": "retained execution"}', encoding='utf-8')
        self.runtime = self.root / 'runtime.json.gz'
        index = pd.Index([3, 2, 1], name='group_seq')
        groups = pd.DataFrame({'group_name': ['import', 'detritus', 'producer'],
                               'trophic_info': ['Import', 'DET', 'PP']}, index=index)
        self.state = {'_groups_df': groups,
                      '_DC': pd.DataFrame(np.eye(3), index=index, columns=index),
                      '_det_fate': pd.DataFrame([0., 0., 1.], index=index, columns=[2]),
                      'seq2name': {3: 'import', 2: 'detritus', 1: 'producer'},
                      'name2seq': {'import': 3, 'detritus': 2, 'producer': 1}}
        for key in ('p', 'q', 'catch', 'predation', 'growth', 'immigration',
                    'emigration', 'net_migration', 'respiration', 'egestion',
                    'M0', 'det_export', 'EE', 'GE', 'GS', 'TL'):
            self.state[key] = pd.Series([0., 2., 3.], index=index, name=key)
        self.flags = {'constructor': {'underdetermined': False},
                      'engine_sources': {}, 'engine_source_hashes': {}}
        for name in ('ModelData.py', 'PPRCalculator.py', 'utils.py'):
            path = self.root / name
            path.write_text('# pinned test source\n', encoding='utf-8')
            self.flags['engine_sources'][name] = name
            self.flags['engine_source_hashes'][name] = self.sha(path)
        self.write_runtime()
        self.flags['audited_replay'] = {
            'schema_version': 1, 'mode': 'completed_runtime',
            'model_sha256': self.sha(self.model),
            'provenance': {'relative_path': self.provenance.name,
                           'sha256': self.sha(self.provenance)},
            'runtime': {'relative_path': self.runtime.name,
                        'sha256': self.sha(self.runtime),
                        'keys': ['constructor_outcome', 'runtime']}}

    @staticmethod
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def module(self):
        spec = importlib.util.find_spec('tools.scientific_helpers.sppr.audited_runtime')
        self.assertIsNotNone(spec, 'Authenticated runtime replay implementation is missing')
        return importlib.import_module(spec.name)

    def write_runtime(self):
        payload = {'constructor_outcome': {'runtime': encode_lossless(self.state)}}
        self.runtime.write_bytes(gzip.compress(json.dumps(payload).encode('utf-8'), mtime=0))
        if 'audited_replay' in self.flags:
            self.flags['audited_replay']['runtime']['sha256'] = self.sha(self.runtime)

    def test_restore_preserves_flows_and_never_calls_constructors(self):
        class Calculator:
            def __init__(self, *args, **kwargs):
                raise AssertionError('Constructor must not run')

            @classmethod
            def from_dict(cls, *args, **kwargs):
                raise AssertionError('from_dict must not run')

        model, source, notices = self.module().restore_runtime(Calculator, self.flags, self.model)
        for key in ('_groups_df', '_DC', '_det_fate'):
            pd.testing.assert_frame_equal(getattr(model, key), self.state[key])
        for key in ('p', 'q', 'M0', 'EE', 'catch'):
            pd.testing.assert_series_equal(getattr(model, key), self.state[key])
        self.assertEqual(model.seq2name, self.state['seq2name'])
        self.assertEqual(model.n_groups, 3)
        self.assertFalse(model.is_underdetermined)
        self.assertNotIn('ee_threshold', vars(model))
        self.assertIn('runtime_replay_reference', source)
        self.assertTrue(notices)

    def test_decode_preserves_nonfinite_values_dtype_and_named_axes(self):
        value = {'frame': pd.DataFrame({'x': pd.Series([None, np.nan, np.inf, -np.inf], dtype=object)}),
                 'array': np.array([[1., np.nan], [np.inf, -np.inf]]),
                 'mapping': {1: ('value', np.nan)}}
        decoded = self.module().decode_lossless(encode_lossless(value))
        pd.testing.assert_frame_equal(decoded['frame'], value['frame'])
        np.testing.assert_equal(decoded['array'], value['array'])
        self.assertEqual(decoded['mapping'][1][0], 'value')
        self.assertTrue(np.isnan(decoded['mapping'][1][1]))

    def test_validation_refuses_changed_model_runtime_provenance_and_engine(self):
        replay = self.module()
        self.assertIsNotNone(replay.validate_replay(self.flags, self.model))
        for path in (self.model, self.runtime, self.provenance, self.root / 'PPRCalculator.py'):
            with self.subTest(path=path.name):
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                try:
                    with self.assertRaisesRegex(ValueError, 'hash'):
                        replay.validate_replay(self.flags, self.model)
                finally:
                    path.write_bytes(original)

    def test_validation_refuses_path_escape(self):
        for key in ('runtime', 'provenance'):
            with self.subTest(key=key):
                flags = deepcopy(self.flags)
                flags['audited_replay'][key]['relative_path'] = '../outside.json'
                with self.assertRaisesRegex(ValueError, 'outside|relative'):
                    self.module().validate_replay(flags, self.model)

    def test_restore_refuses_missing_flow_and_mismatched_axes(self):
        class Calculator:
            pass
        del self.state['M0']
        self.write_runtime()
        with self.assertRaisesRegex(ValueError, 'M0'):
            self.module().restore_runtime(Calculator, self.flags, self.model)
        self.state['M0'] = self.state['p'].copy()
        self.state['_DC'].columns = [9, 2, 1]
        self.write_runtime()
        with self.assertRaisesRegex(ValueError, 'axes|groups'):
            self.module().restore_runtime(Calculator, self.flags, self.model)

    def test_recorded_constructor_requires_no_runtime_and_absence_is_opt_out(self):
        replay = self.module()
        self.assertIsNone(replay.validate_replay({}, self.model))
        flags = deepcopy(self.flags)
        flags['audited_replay'].update(mode='recorded_constructor')
        del flags['audited_replay']['runtime']
        self.assertEqual(replay.validate_replay(flags, self.model)['mode'], 'recorded_constructor')

    def test_restore_refuses_configuration_changes_and_derives_recorded_threshold(self):
        class Calculator:
            pass
        self.state['_initialization_settings'] = {'underdetermined': False, 'ee_threshold': .1}
        self.write_runtime()
        model, _, _ = self.module().restore_runtime(Calculator, self.flags, self.model)
        self.assertEqual(model.ee_threshold, .1)
        self.flags['constructor']['ee_threshold'] = .2
        with self.assertRaisesRegex(ValueError, 'configuration|settings'):
            self.module().restore_runtime(Calculator, self.flags, self.model)

    def test_decode_refuses_masks_that_conflict_with_saved_values(self):
        encoded = encode_lossless(pd.DataFrame({'x': [np.nan, 1.]}))
        encoded['masks']['nan'][0][0] = False
        with self.assertRaisesRegex(ValueError, 'mask'):
            self.module().decode_lossless(encoded)

    def test_restore_accepts_inert_legacy_codec_and_records_omitted_caches(self):
        def encode(value):
            if isinstance(value, pd.DataFrame):
                return {'type': 'DataFrame', 'index': list(value.index),
                        'columns': list(value.columns), 'values': value.values.tolist(),
                        'dtypes': [str(dtype) for dtype in value.dtypes]}
            if isinstance(value, pd.Series):
                return {'type': 'Series', 'index': list(value.index),
                        'values': value.tolist(), 'name': value.name}
            if isinstance(value, dict):
                return {'type': 'dict', 'items': [[key, encode(item)] for key, item in value.items()]}
            return value
        class Calculator:
            pass
        raw = encode(self.state)
        raw['items'].append(['_model', {'type': 'ModelData', 'attributes': {'type': 'dict', 'items': []}}])
        raw['items'].append(['balanced_model', {'type': 'PPRCalculator', 'attributes': {'type': 'dict', 'items': []}}])
        self.runtime.write_bytes(gzip.compress(json.dumps(raw).encode()))
        self.flags['audited_replay']['runtime'].update(sha256=self.sha(self.runtime), keys=[])
        model, source, _ = self.module().restore_runtime(Calculator, self.flags, self.model)
        np.testing.assert_equal(model._DC.values, np.eye(3))
        self.assertEqual(model.n_groups, 3)
        self.assertIn('_model', source['omitted_noncomputational_attributes'])
        self.assertIn('balanced_model', source['omitted_noncomputational_attributes'])
        self.assertFalse(hasattr(model, 'balanced_model'))


if __name__ == '__main__':
    unittest.main()
