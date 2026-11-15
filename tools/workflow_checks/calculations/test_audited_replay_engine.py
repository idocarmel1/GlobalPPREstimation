"""Explicit archived execution is independent of current algorithm equivalence."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.scientific_helpers.sppr import method_coverage as adapter
from tools.workflow_checks.calculations.sppr_repair_fixtures import v1_source_bytes


class AuditedReplayEngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.model = self.root / 'model.json'
        self.model.write_text('{}', encoding='utf-8')
        self.provenance = self.root / 'execution.json'
        self.provenance.write_text('{"role":"retained execution"}', encoding='utf-8')
        files = {
            'ModelData.py': 'class ModelData: pass\n',
            'utils.py': 'RETAINED = True\n',
            'PPRCalculator.py': 'DEFAULT_DIAGNOSTIC_THRESHOLDS = {}\nclass PPRCalculator:\n    def retained_value(self): return 7\n',
        }
        for name, value in files.items():
            (self.root / name).write_text(value, encoding='utf-8')
        sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        self.flags = {
            'constructor': {'zero_catch': False},
            'engine_sources': {name: name for name in files},
            'engine_source_hashes': {name: sha(self.root/name) for name in files},
            'audited_replay': {
                'schema_version': 1, 'model_sha256': sha(self.model),
                'mode': 'recorded_constructor',
                'provenance': {'relative_path': self.provenance.name, 'sha256': sha(self.provenance)},
            },
        }

    def test_authenticated_archived_engine_executes_its_own_methods(self):
        engine = adapter._audited_engine(self.flags, self.model)
        self.assertEqual(engine[2]().retained_value(), 7)
        self.assertEqual(engine[2].__module__.split('_')[1:3], ['sppr', 'audited'])

    def test_without_explicit_replay_algorithm_difference_stays_blocked(self):
        flags = {k:v for k,v in self.flags.items() if k != 'audited_replay'}
        with self.assertRaisesRegex(ValueError, 'scientific methods differ'):
            adapter._audited_engine(flags, self.model)

    def test_replay_rechecks_provenance_even_for_cached_engine(self):
        adapter._audited_engine(self.flags, self.model)
        self.provenance.write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'hash|changed'):
            adapter._audited_engine(self.flags, self.model)

    def test_symbolic_derivative_must_match_checked_transformation(self):
        original = v1_source_bytes()
        (self.root/'PPRCalculator.py').write_bytes(original)
        self.flags['engine_source_hashes']['PPRCalculator.py'] = hashlib.sha256(original).hexdigest()
        from tools.scientific_helpers.sppr.symbolic_repairs import repair_symbolic_source
        derived, _ = repair_symbolic_source(original.decode('utf-8'))
        destination=self.root/'repaired.py'
        destination.write_text(derived,encoding='utf-8',newline='')
        reference={'relative_path':destination.name,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
                   'base_sha256':hashlib.sha256(original).hexdigest(),'repair':'symbolic_repairs_v1'}
        self.flags['audited_replay']['symbolic_repair']=reference
        self.assertEqual(adapter._derivative_engine_path(self.flags,self.model),destination)
        destination.write_text(derived+'\n# unrecorded edit',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'hash|transformation'):
            adapter._derivative_engine_path(self.flags,self.model)

    def test_symbolic_derivative_cache_binds_each_recorded_dependency_bundle(self):
        derivative = self.root/'derivative.py'
        derivative.write_text(
            'from ModelData import ModelData\nfrom utils import TAG\n'
            'DEFAULT_DIAGNOSTIC_THRESHOLDS = {}\nclass PPRCalculator:\n'
            '    def dependency_identity(self): return ModelData, TAG\n', encoding='utf-8')
        engines = []
        for label in ('first', 'second'):
            bundle = self.root/label
            bundle.mkdir()
            data_path, utility_path = bundle/'ModelData.py', bundle/'utils.py'
            data_path.write_text('class ModelData: pass\n', encoding='utf-8')
            utility_path.write_text('TAG = '+repr(label)+'\n', encoding='utf-8')
            module_name = '_dependency_bundle_' + hashlib.sha256(str(bundle).encode()).hexdigest()
            data = adapter._isolated_module(data_path, module_name, {})
            engine = (None, data.ModelData, None, {})
            with patch.object(adapter, '_derivative_engine_path', return_value=derivative), \
                 patch.object(adapter, '_engine_paths', return_value={
                     'ModelData.py': data_path, 'utils.py': utility_path}):
                repaired = adapter._with_symbolic_repair(engine, {}, self.model)
            engines.append((data.ModelData, repaired[2]))
            self.assertEqual(repaired[2]().dependency_identity(), (data.ModelData, label))
        self.assertIsNot(engines[0][1], engines[1][1])

    def test_symbolic_v2_derivative_uses_its_own_exact_recipe(self):
        from tools.scientific_helpers.sppr.symbolic_repairs import repair_symbolic_source
        original = v1_source_bytes()
        (self.root/'PPRCalculator.py').write_bytes(original)
        self.flags['engine_source_hashes']['PPRCalculator.py'] = hashlib.sha256(original).hexdigest()
        derived, _ = repair_symbolic_source(original.decode('utf-8'), repair='symbolic_repairs_v2')
        destination = self.root/'repaired_v2.py'
        destination.write_bytes(derived.encode('utf-8'))
        reference = {'relative_path': destination.name,
                     'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                     'base_sha256': hashlib.sha256(original).hexdigest(), 'repair': 'symbolic_repairs_v2'}
        self.flags['audited_replay']['symbolic_repair'] = reference
        self.assertEqual(adapter._derivative_engine_path(self.flags, self.model), destination)
        reference['repair'] = 'symbolic_repairs_v1'
        with self.assertRaisesRegex(ValueError, 'transformation'):
            adapter._derivative_engine_path(self.flags, self.model)

    def test_distinct_derivative_descriptors_cannot_silently_override_each_other(self):
        self.flags['audited_replay']['symbolic_repair'] = {'repair': 'symbolic_repairs_v2'}
        self.flags['audited_replay']['ew_e_optimized'] = {'repair': 'ewe_slow_numeric_fast_v1'}
        with self.assertRaisesRegex(ValueError, 'one|exclusive|multiple'):
            adapter._derivative_engine_path(self.flags, self.model)

    def test_ewe_derivative_binds_actual_calculation_upgrade_source(self):
        from tools.scientific_helpers.sppr.ewe_path_optimization import repair_ewe_source
        source = (adapter.ENGINE.parents[2]/'regions/LME/LME_003/papers/CAL-2016/models/'
                  'CAL-2016_California_Current_2000-2014/results/diagnostics/'
                  'ee_floor_review_20261114/code/floor/PPRCalculator.py')
        original = source.read_bytes()
        base = self.root/'calculation.py'
        base.write_bytes(original)
        self.flags.update(calculation_engine_source=base.name,
                          calculation_engine_sha256=hashlib.sha256(original).hexdigest(),
                          calculation_engine_upgrade=adapter.EE_FLOOR_UPGRADE)
        derived, _ = repair_ewe_source(original.decode('utf-8'))
        destination = self.root/'optimized.py'
        destination.write_bytes(derived.encode('utf-8'))
        self.flags['audited_replay']['ew_e_optimized'] = {
            'relative_path': destination.name, 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
            'base_sha256': hashlib.sha256(original).hexdigest(), 'repair': 'ewe_slow_numeric_fast_v1'}
        self.assertEqual(adapter._derivative_engine_path(self.flags, self.model), destination)
        identity = adapter.engine_identity(self.flags, self.model)
        self.assertEqual(identity['ewe_path_optimization/PPRCalculator.py'],
                         hashlib.sha256(destination.read_bytes()).hexdigest())
        self.assertNotIn('symbolic_repair/PPRCalculator.py', identity)


if __name__ == '__main__':
    unittest.main()
