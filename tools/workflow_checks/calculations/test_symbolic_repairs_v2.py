"""Versioned identity filtering avoids repeated general algebraic simplification."""
import ast
import hashlib
import textwrap
import unittest
from unittest.mock import patch

import sympy as sm

from tools.scientific_helpers.sppr.method_coverage import ENGINE
from tools.scientific_helpers.sppr.symbolic_repairs import repair_symbolic_source
from tools.workflow_checks.calculations.sppr_repair_fixtures import v1_source_bytes


class SymbolicRepairsV2Tests(unittest.TestCase):
    @staticmethod
    def source():
        return v1_source_bytes().decode('utf-8')

    @staticmethod
    def helper(source):
        cls = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef)
                   and node.name == 'PPRCalculator')
        node = next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                    and node.name == '_eval_symbolic_substitutions')
        namespace = {'sm': sm}
        exec(compile(textwrap.dedent(ast.get_source_segment(source, node)),
                     '<checked symbolic helper>', 'exec'), namespace)
        return namespace['_eval_symbolic_substitutions']

    def repaired(self):
        return repair_symbolic_source(self.source(), repair='symbolic_repairs_v2')

    def test_v1_remains_unchanged_and_v2_changes_only_identity_helper(self):
        original = self.source()
        self.assertEqual(repair_symbolic_source(original)[0], original)
        derived, manifest = self.repaired()
        self.assertEqual(manifest['repair'], 'symbolic_repairs_v2')
        self.assertEqual(manifest['original_sha256'], hashlib.sha256(original.encode()).hexdigest())
        self.assertEqual(manifest['derived_sha256'], hashlib.sha256(derived.encode()).hexdigest())
        self.assertEqual(manifest['changed_methods'], ['_eval_symbolic_substitutions'])
        def bodies(source):
            cls = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef)
                       and node.name == 'PPRCalculator')
            return {node.name: ast.dump(node, include_attributes=False) for node in cls.body
                    if isinstance(node, ast.FunctionDef)}
        before, after = bodies(original), bodies(derived)
        self.assertEqual(before.keys(), after.keys())
        self.assertEqual({key for key in before if before[key] != after[key]},
                         {'_eval_symbolic_substitutions'})
        self.assertEqual(repair_symbolic_source(derived, repair='symbolic_repairs_v2')[0], derived)
        with self.assertRaisesRegex(ValueError, 'pattern|version'):
            repair_symbolic_source(derived)
        self.assertEqual(self.source(), original)

    def test_float_identity_is_removed_but_zero_and_other_values_are_applied(self):
        helper = self.helper(self.repaired()[0])
        x, y = sm.symbols('x y')
        self.assertEqual(sm.expand(helper(x+y, {x: sm.Float(1.)*x, y: 2.}) - (x+2)), 0)
        self.assertEqual(helper(x+y, {x: 0., y: 2.}), sm.Float(2.))
        self.assertEqual(helper(x, {x: y}), x.evalf(subs={x: y}))

    def test_large_substitution_does_not_call_general_simplification(self):
        helper = self.helper(self.repaired()[0])
        x, y, z = sm.symbols('x y z')
        value = sum((x+y+i)**2 for i in range(60))/(z+1)
        with patch.object(sm, 'simplify', side_effect=AssertionError('General simplify must not run')):
            self.assertEqual(helper(sm.Integer(3), {x: value}), sm.Float(3.))

    def test_unknown_nonidentity_cycle_remains_unresolved(self):
        helper = self.helper(self.repaired()[0])
        x, y = sm.symbols('x y')
        # x -> y -> x is not a proven identity substitution for either key.
        # Retain it and let SymPy report the unresolved cycle.
        with self.assertRaises(RecursionError):
            helper(x, {x: y, y: x})

    def test_raw_windows_newlines_survive_v1_to_v2_upgrade(self):
        original = self.source().replace('\r\n', '\n').replace('\n', '\r\n')
        derived, manifest = repair_symbolic_source(original, repair='symbolic_repairs_v2')
        self.assertNotIn('\n', derived.replace('\r\n', ''))
        self.assertEqual(manifest['original_sha256'], hashlib.sha256(original.encode()).hexdigest())

    def test_original_archive_reaches_same_v2_directly_or_through_v1(self):
        archive = (ENGINE.parents[2]/'regions/LME/LME_035/papers/Christensen-1998/models/'
                   '35_412_Gulf_of_Thailande_(1963)/model_validation/evidence/source_review/'
                   'direct_diagnostics/engine/PPRCalculator.py')
        original = archive.read_bytes().decode('utf-8')
        first, _ = repair_symbolic_source(original)
        direct, _ = repair_symbolic_source(original, repair='symbolic_repairs_v2')
        upgraded, _ = repair_symbolic_source(first, repair='symbolic_repairs_v2')
        self.assertEqual(direct, upgraded)

    def test_canonical_source_is_exact_v2_derivative_of_pinned_v1(self):
        derived, _ = self.repaired()
        self.assertEqual((ENGINE/'PPRCalculator.py').read_bytes(), derived.encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
