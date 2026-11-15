"""Regression checks for symbolic labels, identity substitutions and omitted axes."""
import importlib.util
import ast
import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
import sympy as sm

ENGINE = Path(__file__).resolve().parents[2] / 'scientific_code' / 'PPREstimation'
sys.path.insert(0, str(ENGINE))
from PPRCalculator import PPRCalculator


class SymbolicRepairTests(unittest.TestCase):
    def test_canonical_identity_filter_avoids_general_simplification(self):
        x, y = sm.symbols('x y')
        with patch.object(sm, 'simplify', side_effect=AssertionError('General simplify must not run')):
            result = PPRCalculator._eval_symbolic_substitutions(x+y, {x: sm.Float(1.)*x, y: 2.})
        self.assertEqual(sm.expand(result - (x+2)), 0)

    def test_group_name_punctuation_is_one_symbol(self):
        model = object.__new__(PPRCalculator)
        model.seq2name = {22: 'Crab, lobster', 23: 'Fish: adult'}
        method = getattr(model, '_group_sppr_symbols', None)
        self.assertTrue(callable(method), 'Literal group names need explicit single symbols')
        symbols = method([22, 23], 'SPPR')
        self.assertEqual(symbols, [sm.Symbol('SPPR_Crab,_lobster'), sm.Symbol('SPPR_Fish:_adult')])
        result = pd.DataFrame([[.25, .75]]) @ pd.DataFrame(symbols)
        self.assertEqual(result.iloc[0, 0], .25 * symbols[0] + .75 * symbols[1])

    def test_label_normalization_collision_is_rejected(self):
        model = object.__new__(PPRCalculator)
        model.seq2name = {1: 'A B', 2: 'A_B'}
        method = getattr(model, '_group_sppr_symbols', None)
        self.assertTrue(callable(method))
        with self.assertRaisesRegex(ValueError, 'distinct'):
            method([1, 2], 'SPPR')

    def test_identity_substitution_keeps_the_free_variable(self):
        x, y = sm.symbols('x y')
        method = getattr(PPRCalculator, '_eval_symbolic_substitutions', None)
        self.assertTrue(callable(method), 'Identity substitutions must not recurse')
        result = method(x + y, {x: sm.Float(1.) * x, y: 2.})
        self.assertEqual(sm.simplify(result - (x + 2)), 0)
        self.assertEqual(result.free_symbols, {x})

    @staticmethod
    def collapse(omitted_weight):
        axes = [1, 2, 3]
        sppr = pd.DataFrame({2: [.5, 1.]}, index=[1, 2])
        non_det = pd.Series([1., 0.], index=[1, 2])
        mortality = pd.Series([.1, 0., omitted_weight], index=axes)
        zero = pd.Series(0., index=axes)
        q = pd.Series([1., 1., 0.], index=axes)
        diet = pd.DataFrame(0., index=axes, columns=axes)
        return PPRCalculator._collapse_det_scaling(
            sppr, [2], non_det, mortality, zero, q, mortality, diet, 'GE')

    def test_zero_weight_omitted_axis_is_safe(self):
        try:
            _, scalar, a, b = self.collapse(0.)
        except ValueError as error:
            self.fail('A provably zero omitted coordinate must align: ' + str(error))
        self.assertAlmostEqual(a, .1)
        self.assertAlmostEqual(b, .05)
        self.assertAlmostEqual(scalar, .1 / .95)

    def test_nonzero_omitted_axis_stays_unavailable(self):
        with self.assertRaisesRegex(ValueError, 'unrepresented nonzero'):
            self.collapse(.01)

    def test_archived_derivative_changes_only_symbolic_helpers_and_alignment(self):
        repair_file = ENGINE.parents[1] / 'scientific_helpers' / 'sppr' / 'symbolic_repairs.py'
        self.assertTrue(repair_file.is_file(), 'Archived engines need a checked derivative recipe')
        from tools.scientific_helpers.sppr.symbolic_repairs import repair_symbolic_source
        original = (ENGINE.parents[2] / 'regions/LME/LME_035/papers/Christensen-1998/models/'
                    '35_412_Gulf_of_Thailande_(1963)/model_validation/evidence/source_review/'
                    'direct_diagnostics/engine/PPRCalculator.py').read_text(encoding='utf-8')
        derived, manifest = repair_symbolic_source(original)
        self.assertEqual(manifest['original_sha256'], hashlib.sha256(original.encode()).hexdigest())
        self.assertEqual(manifest['derived_sha256'], hashlib.sha256(derived.encode()).hexdigest())
        def methods(text):
            cls = next(n for n in ast.parse(text).body if isinstance(n, ast.ClassDef) and n.name == 'PPRCalculator')
            return {n.name: ast.dump(n, include_attributes=False) for n in cls.body if isinstance(n, ast.FunctionDef)}
        old, new = methods(original), methods(derived)
        changed = {name for name in old if old[name] != new[name]}
        self.assertEqual(changed, {'_collapse_det_scaling', '_SPPR_symbolic_helper_diet_import_as_PP',
                                   '_SPPR_symbolic_helper_diet_import_as_DC'})
        self.assertEqual(set(new) - set(old), {'_group_sppr_symbols', '_eval_symbolic_substitutions'})
        self.assertEqual(repair_symbolic_source(derived)[0], derived)
        with self.assertRaisesRegex(ValueError, 'pattern'):
            repair_symbolic_source(original.replace('A @ sppr_vec - sppr_vec', 'A.dot(sppr_vec) - sppr_vec'))

    def test_repaired_raw_windows_source_is_idempotent_with_raw_hash(self):
        from tools.scientific_helpers.sppr.symbolic_repairs import repair_symbolic_source
        raw = (ENGINE / 'PPRCalculator.py').read_bytes().decode('utf-8')
        derived, manifest = repair_symbolic_source(raw, repair='symbolic_repairs_v2')
        self.assertEqual(derived, raw)
        self.assertEqual(manifest['original_sha256'], hashlib.sha256(raw.encode()).hexdigest())

    def test_archived_crlf_source_keeps_newlines_and_raw_hash(self):
        from tools.scientific_helpers.sppr.symbolic_repairs import repair_symbolic_source
        original = (ENGINE.parents[2] / 'regions/LME/LME_035/papers/Christensen-1998/models/'
                    '35_412_Gulf_of_Thailande_(1963)/model_validation/evidence/source_review/'
                    'direct_diagnostics/engine/PPRCalculator.py').read_text(encoding='utf-8')
        raw = original.replace('\n', '\r\n')
        derived, manifest = repair_symbolic_source(raw)
        self.assertEqual(manifest['original_sha256'], hashlib.sha256(raw.encode()).hexdigest())
        self.assertNotIn('\n', derived.replace('\r\n', ''))
        self.assertEqual(repair_symbolic_source(derived)[0], derived)


if __name__ == '__main__':
    unittest.main()
