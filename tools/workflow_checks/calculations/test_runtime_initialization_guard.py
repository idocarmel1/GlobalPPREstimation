"""Retained scenarios must not fall through to stock model reconstruction.

These tests keep the real adapter entry points and replace only scientific
engine access. Running a real model to test a refusal would risk the very
unauthorized reconstruction this guard must prevent.
"""
from __future__ import annotations

import copy
import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools.scientific_helpers.sppr import method_coverage as production_adapter

adapter = production_adapter
if os.environ.get('METHOD_COVERAGE_CANDIDATE'):
    candidate = Path(os.environ['METHOD_COVERAGE_CANDIDATE'])
    spec = importlib.util.spec_from_file_location('_runtime_guard_candidate', candidate)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)


class RuntimeInitializationGuardTests(unittest.TestCase):
    # These are inert fixture hashes; the guard refuses any declared custom
    # initialization and does not claim to authenticate this test scenario.
    marker = {
        'kind': 'retained_scenario',
        'reexecution_supported': False,
        'settings': {'path': 'retained/settings.json', 'sha256': 'a' * 64},
        'recipe': {'path': 'retained/recipe.json', 'sha256': 'b' * 64},
        'initial_runtime': {'path': 'retained/runtime.json.gz', 'sha256': 'c' * 64},
        'required_preprocessing': [{
            'group_seq': 3, 'group_name': 'Seabirds (all)', 'field': 'det_fate',
            'operation': 'set entire outgoing detritus fate row to 0',
            'destination': 'external export through existing det_export sink',
        }],
    }

    def reject_before_engine(self, entry, marker):
        flags = {'constructor': {'zero_catch': True},
                 'runtime_initialization': copy.deepcopy(marker)}
        before = copy.deepcopy(flags)
        # These tripwires fail if rejection occurs after either engine access
        # boundary, even when a scientific engine would itself reject later.
        with patch.object(adapter, '_audited_engine', side_effect=AssertionError('audited engine accessed')), \
             patch.object(adapter, '_engine', side_effect=AssertionError('calculation engine accessed')), \
             patch.object(adapter, '_calculation_engine_path', side_effect=AssertionError('engine path accessed')):
            with self.assertRaisesRegex(ValueError, '[Cc]onfiguration unavailable') as caught:
                if entry == 'constructor':
                    adapter._constructor(flags, Path('does-not-exist/model.json'))
                else:
                    adapter._load(Path('does-not-exist/model.json'), {'zero_catch': True}, flags)
        message = str(caught.exception).lower()
        self.assertIn('authenticated saved runtime', message)
        self.assertIn('stock', message)
        self.assertEqual(flags, before)

    def test_declared_scenario_constructor_rejects_before_engine_access(self):
        self.reject_before_engine('constructor', self.marker)

    def test_declared_scenario_load_rejects_before_modeldata_construction(self):
        self.reject_before_engine('load', self.marker)

    def test_malformed_marker_is_not_silently_treated_as_absent(self):
        for marker in (None, False, 0, '', [], (), 'retained_scenario', [{}]):
            for entry in ('constructor', 'load'):
                with self.subTest(marker=repr(marker), entry=entry):
                    self.reject_before_engine(entry, marker)

    def test_nonempty_unknown_or_reexecution_claim_cannot_enable_stock_loading(self):
        for marker in ({'kind': 'unknown'}, {'reexecution_supported': True}):
            for entry in ('constructor', 'load'):
                with self.subTest(marker=marker, entry=entry):
                    self.reject_before_engine(entry, marker)

    def test_absent_or_empty_marker_preserves_constructor_options_and_defaults(self):
        class Calculator:
            @staticmethod
            def from_modeldata(source, zero_catch=False, normalize_DC=True):
                raise AssertionError('constructor option resolution must not construct')

        for extra in ({}, {'runtime_initialization': {}}):
            with self.subTest(extra=extra), \
                 patch.object(adapter, '_audited_engine', return_value=(None, None, Calculator, {})), \
                 patch.object(adapter, '_calculation_engine_path', return_value=None):
                flags = {'constructor': {'zero_catch': True}, **extra}
                self.assertEqual(adapter._constructor(flags),
                                 {'zero_catch': True, 'normalize_DC': True})

    def test_unmarked_load_preserves_source_state_constructor_and_return_contract(self):
        class ModelData:
            def __init__(self, path):
                self.path = path
                self.groups_data = {'group': 3}
                self.DC = [[1.0]]
                self.det_fate = [[0.0]]

        class Calculator:
            @staticmethod
            def from_modeldata(source, zero_catch=False):
                return SimpleNamespace(source=source, zero_catch=zero_catch)

        for flags in (None, {}, {'runtime_initialization': {}}):
            with self.subTest(flags=flags), \
                 patch.object(adapter, '_engine', return_value=(None, ModelData, Calculator, {})), \
                 patch.object(adapter, '_calculation_engine_path', return_value=None):
                model, source_state, notices = adapter._load(Path('ordinary.json'), {'zero_catch': True}, flags)
                self.assertEqual(model.source.path, 'ordinary.json')
                self.assertIs(model.zero_catch, True)
                self.assertEqual(source_state, {'groups': {'group': 3}, 'diet': [[1.0]], 'detritus_fate': [[0.0]]})
                self.assertEqual(notices, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
