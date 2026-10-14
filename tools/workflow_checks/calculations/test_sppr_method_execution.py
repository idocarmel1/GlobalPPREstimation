"""Lossless evidence and scope/configuration guards for the SPPR adapter."""
import gzip
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import copy
import sys

import numpy as np
import pandas as pd

from tools.scientific_helpers.sppr import method_coverage as coverage


ROOT = Path(__file__).resolve().parents[3]
TOY = ROOT / 'research/human/discard_sensitivity_expanded_2026_09_10/inputs/corpus/ToyModels/900_900_Multi_DET_Toy_(2026).json'
FLAGS = {'constructor': {'underdetermined': True, 'zero_catch': True,
    'zero_biomass_accum': False, 'default_gs': True, 'weight_flow': 1.,
    'weight_guess': 1., 'normalize_DC': True, 'DC_tol': .001,
    'balance_BA_after_DC_normalization': False},
    'diagnostics': {'DET_TE_vals': 1, 'det_collapse_mode': 'never',
    'det_open_mode': 'none', 'det_theta': 1., 'det_external_sppr': 0.,
    'fix_EE_0_cases': True}}


class EvidenceTests(unittest.TestCase):
    def test_explicit_floor_upgrade_preserves_archived_loader_and_records_both_engines(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / 'model.json'
            shutil.copy2(TOY, model)
            original = self._archived_flags(directory)
            before, _, _ = coverage._load(model, coverage._constructor(original, model), original)
            flags = copy.deepcopy(original)
            flags['constructor'].update(use_ee_floor=True, ee_floor=.1)
            flags['calculation_engine_upgrade'] = 'ee_floor_v1'
            flags['calculation_engine_sha256'] = coverage._hash_bytes((coverage.ENGINE/'PPRCalculator.py').read_bytes())
            identity = coverage.engine_identity(flags, model)
            self.assertEqual(identity['PPRCalculator.py'], original['engine_source_hashes']['PPRCalculator.py'])
            self.assertEqual(identity['calculation/PPRCalculator.py'], flags['calculation_engine_sha256'])
            constructor = coverage._constructor(flags, model)
            self.assertNotIn('balance_BA_after_DC_normalization', constructor)
            after, _, _ = coverage._load(model, constructor, flags)
            self.assertIs(type(after), coverage._engine(flags, model)[2])
            self.assertTrue(after.use_ee_floor)
            for field in ('catch', 'predation', 'egestion', 'respiration', 'net_migration'):
                pd.testing.assert_series_equal(getattr(before, field), getattr(after, field))
            self.assertIn('external_mortality_export', coverage._runtime(after))

    def test_floor_upgrade_rejects_changed_calculation_engine(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / 'model.json'
            shutil.copy2(TOY, model)
            flags = self._archived_flags(directory)
            flags['constructor'].update(use_ee_floor=True, ee_floor=.1)
            flags['calculation_engine_upgrade'] = 'ee_floor_v1'
            flags['calculation_engine_sha256'] = '0'*64
            with self.assertRaisesRegex(ValueError, 'calculation engine'):
                coverage._constructor(flags, model)

    def test_diagnostic_table_restores_mapping_keys_and_blanks_nonfinite(self):
        report={'status':'FAIL','divergence':{'b':np.inf,'sppr_det':{7:2.,9:np.nan}},
                'warnings':('one','two')}
        evidence=coverage.encode_lossless(report)
        original=json.dumps(evidence,sort_keys=True)
        table=coverage.diagnostics_for_table(evidence)
        self.assertIsNone(table['divergence']['b'])
        self.assertEqual(table['divergence']['sppr_det'],{7:2.,9:None})
        flat=coverage._engine()[2]._flatten_diagnostics(table)
        self.assertEqual(flat['divergence_sppr_det_7'],2.)
        self.assertIsNone(flat['divergence_sppr_det_9'])
        self.assertEqual(flat['n_warnings'],2)
        self.assertEqual(json.dumps(evidence,sort_keys=True),original)

    def _archived_flags(self, directory):
        archived = ROOT / 'regions/LME/LME_028/papers/GUI-2004/models/28_646_Guinea_(1998)/model_validation/evidence/source_review/direct_diagnostics/engine/PPRCalculator.py'
        engine = Path(directory) / 'engine'
        engine.mkdir()
        shutil.copy2(archived, engine / 'PPRCalculator.py')
        flags = copy.deepcopy(FLAGS)
        flags['constructor'].pop('balance_BA_after_DC_normalization')
        flags['engine_sources'] = {'PPRCalculator.py': 'engine/PPRCalculator.py'}
        flags['engine_source_hashes'] = {name: coverage._hash_bytes(
            ((engine if name == 'PPRCalculator.py' else coverage.ENGINE) / name).read_bytes())
            for name in ('PPRCalculator.py', 'ModelData.py', 'utils.py')}
        return flags

    def test_archived_engine_keeps_original_defaults_and_isolates_current_module(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / 'model.json'
            shutil.copy2(TOY, model)
            flags = self._archived_flags(directory)
            current = coverage._engine()[2]
            archived = coverage._engine(flags, model)[2]
            self.assertIsNot(current, archived)
            self.assertNotIn('balance_BA_after_DC_normalization', coverage._constructor(flags, model))
            self.assertIn('balance_BA_after_DC_normalization', coverage._constructor(FLAGS))
            self.assertIs(coverage._engine()[2], current)
            self.assertIs(sys.modules['PPRCalculator'].PPRCalculator, current)
            identity = coverage.engine_identity(flags, model)
            self.assertEqual(identity['PPRCalculator.py'], flags['engine_source_hashes']['PPRCalculator.py'])
            for timeout in (0, 60):
                result = coverage.compute_methods(model, flags, ['new_GE'],
                    Path(directory) / f'evidence_{timeout}', progress=None, method_timeout=timeout)
                self.assertEqual(result['methods']['new_GE']['status'], 'ok', result['methods']['new_GE']['reason'])
                self.assertEqual(result['engine_hashes'], identity)
                self.assertNotIn('balance_BA_after_DC_normalization', result['constructor'])
            self.assertIs(coverage._engine()[2], current)

    def test_archived_dependency_mismatch_is_explicit_not_run(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / 'model.json'
            shutil.copy2(TOY, model)
            flags = self._archived_flags(directory)
            flags['engine_source_hashes']['utils.py'] = '0' * 64
            result = coverage.compute_methods(model, flags, ['SPPR_1986', 'new_GE'],
                Path(directory) / 'evidence', progress=None, method_timeout=0)
            for entry in result['methods'].values():
                self.assertEqual(entry['status'], 'NOT_RUN')
                self.assertIn('hash', entry['reason'].lower())
                self.assertIn('utils.py', entry['reason'])

    def test_masks_distinguish_missing_nonfinite_and_zero_with_axes(self):
        frame = pd.DataFrame([[None, np.nan, np.inf, -np.inf, 0.]],
                             index=pd.Index([7], name='recipient'),
                             columns=[11, 12, 13, 14, 15], dtype=object)
        saved = coverage.encode_lossless(frame)
        self.assertEqual(saved['index'], [7])
        self.assertEqual(saved['columns'], [11, 12, 13, 14, 15])
        self.assertEqual(saved['masks'], {'null': [[True,False,False,False,False]],
            'nan': [[False,True,False,False,False]],
            'positive_infinity': [[False,False,True,False,False]],
            'negative_infinity': [[False,False,False,True,False]]})
        self.assertEqual(json.loads(json.dumps(saved, allow_nan=False))['data'][0][4], 0.)

    def test_audited_auto_collapse_reaches_new_symbolic_and_mc(self):
        flags = {**FLAGS, 'diagnostics': {**FLAGS['diagnostics'], 'det_collapse_mode':'auto'}}
        for key in ('new_GE', 'new_TE_noEEfix', 'sym_GE_asDC', 'MC_new_TE_EEfix'):
            settings = coverage.method_settings(key, flags)
            self.assertEqual(settings['kwargs']['det_collapse_mode'], 'auto')
        self.assertFalse(coverage.method_settings('new_TE_noEEfix', flags)['kwargs']['fix_EE_0_cases'])
        self.assertTrue(coverage.method_settings('MC_new_TE_EEfix', flags)['kwargs']['exclude_diverged'])

    def test_scalar_scope_remains_unavailable_and_full_new_return_is_saved(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / TOY.name
            shutil.copy2(TOY, model)
            before = model.read_bytes()
            output = Path(directory) / 'evidence'
            result = coverage.compute_methods(model, FLAGS, ['SPPR_1995_TE0.1','new_GE'], output,
                                              progress=lambda _: None, method_timeout=0)
            scalar = result['methods']['SPPR_1995_TE0.1']
            self.assertEqual(scalar['status'], 'ok')
            self.assertTrue(all(v is None for v in scalar['scopes']['PP'].values()))
            self.assertEqual(scalar['annual_status']['PP'], 'unavailable: source scope unsupported')
            fresh = result['methods']['new_GE']
            self.assertEqual(fresh['status'], 'ok', fresh.get('reason'))
            doc = json.loads(gzip.decompress((output/fresh['evidence']['path']).read_bytes()))
            self.assertEqual(doc['return']['type'], 'tuple')
            self.assertEqual(len(doc['return']['items']), 4)
            self.assertEqual(doc['return']['items'][1]['type'], 'dataframe')
            self.assertTrue(doc['reconciliation']['scope_sums_verified'])
            self.assertEqual(before, model.read_bytes())

    def test_constructor_error_is_not_a_scientific_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory)/'model.json'
            model.write_text('{}', encoding='utf-8')
            result = coverage.compute_methods(model, FLAGS, ['new_GE','MC_new_GE'],
                Path(directory)/'evidence', progress=lambda _:None, method_timeout=0)
            for entry in result['methods'].values():
                self.assertEqual(entry['status'], 'NOT_RUN')
                self.assertIn('constructor', entry['reason'].lower())
                self.assertTrue(entry['evidence']['sha256'])

    def test_spawned_worker_preserves_mc_samples_and_symbolic_return(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'evidence'
            flags = {**FLAGS, 'mc': {'n_samples': 3, 'seed': 42}}
            result = coverage.compute_methods(TOY, flags, ['sym_GE_asDC','MC_new_GE'],
                output, progress=lambda _:None, method_timeout=60)
            for key in ('sym_GE_asDC','MC_new_GE'):
                entry = result['methods'][key]
                self.assertEqual(entry['status'], 'ok', entry.get('reason'))
                saved = json.loads(gzip.decompress((output/entry['evidence']['path']).read_bytes()))
                self.assertEqual(saved['runtime_before_sha256'],saved['runtime_after_sha256'])
                self.assertEqual(saved['return']['type'], 'tuple')
            symbolic = result['methods']['sym_GE_asDC']
            self.assertEqual(symbolic['annual_status']['all'], 'ok')
            self.assertIsNone(symbolic['scopes']['all']['diet_import'])
            mc = result['methods']['MC_new_GE']
            self.assertEqual(mc['mc_diagnostics']['n_samples'], 3)
            self.assertEqual(len(mc['mc_diagnostics']['per_sample_reason']), 3)
            saved = json.loads(gzip.decompress((output/mc['evidence']['path']).read_bytes()))
            self.assertEqual(saved['return']['items'][1]['type'], 'ndarray')
            self.assertEqual(saved['return']['items'][1]['shape'][0], mc['mc_diagnostics']['n_accepted'])
            self.assertIsNotNone(saved['rng_before'])

    def test_timeout_override_does_not_erase_later_method(self):
        with tempfile.TemporaryDirectory() as directory:
            flags = {**FLAGS, 'method_timeout_overrides_seconds': {'new_GE': .000001}}
            result = coverage.compute_methods(TOY, flags, ['new_GE','SPPR_1995_TE0.1'],
                Path(directory), progress=lambda _:None, method_timeout=60)
            self.assertEqual(result['methods']['new_GE']['status'], 'timeout')
            self.assertEqual(result['methods']['SPPR_1995_TE0.1']['status'], 'ok')
            self.assertEqual(result['methods']['new_GE']['scopes']['all'], {})

    def test_missing_configuration_records_not_run_without_stock_loading(self):
        with tempfile.TemporaryDirectory() as directory:
            result = coverage.compute_methods(TOY, None, ['SPPR_1986','new_GE'],
                Path(directory), progress=lambda _:None, method_timeout=0)
            for entry in result['methods'].values():
                self.assertEqual(entry['status'], 'NOT_RUN')
                self.assertIn('configuration', entry['reason'].lower())
                self.assertTrue(entry['evidence']['sha256'])

    def test_mc_below_eighty_percent_retains_coefficients_but_blocks_publication(self):
        model, _, _ = coverage._load(TOY, FLAGS['constructor'])
        settings = coverage.method_settings('MC_new_GE', {**FLAGS,'mc':{'n_samples':10}})
        frame = model.SPPR_new(TE_option='GE')[0]
        result = (frame, np.zeros((7,*frame.shape)), .3, None, None,
                  {'n_accepted':7,'n_rejected_negative':0,'n_rejected_diverged':3,
                   'reject_frac_negative':0.,'reject_frac_diverged':.3,
                   'per_sample_reason':['accepted']*7+['diverged']*3})
        outcome = coverage._extract_result(model, settings, result)
        self.assertTrue(any(v is not None for v in outcome['scopes']['all'].values()))
        self.assertIn('below 80%', outcome['annual_status']['all'])


if __name__ == '__main__':
    unittest.main()
