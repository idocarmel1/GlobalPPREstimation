"""Exact numerical parity with the authenticated archived slow EwE branch."""
import ast
import json
from pathlib import Path
import unittest
import warnings

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

import ewe_fast_parity as parity


class Toy:
    def __init__(self, dc, te, ee):
        labels = [f'g{i}' for i in range(len(ee))]
        self.dc = pd.DataFrame(dc, index=labels, columns=labels)
        self.te = pd.DataFrame(te, index=labels, columns=labels)
        self.EE = pd.Series(ee, index=labels)

    def get_DC(self, **kwargs):
        return self.dc.copy()

    def get_TE(self, **kwargs):
        return self.te.copy()


class EwEParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.source_path = parity.archived_source('LME_003')
        cls.slow = staticmethod(parity.compile_method(cls.source))
        cls.derived, cls.certificate = parity.repair_fast_source(cls.source)
        cls.fast = staticmethod(parity.compile_method(cls.derived))

    def equal(self, model, max_paths=100000):
        for use_ee in (False, True):
            with self.subTest(use_ee=use_ee), warnings.catch_warnings(), np.errstate(all='ignore'):
                warnings.simplefilter('ignore', RuntimeWarning)
                slow = self.slow(model, 'TE', use_EE=use_ee, return_paths=True, max_paths=max_paths)
                fast = self.fast(model, 'TE', use_EE=use_ee, return_paths=False, max_paths=max_paths)
                self.assertEqual(len(fast), 3)
                self.assertEqual(fast[2], {})
                for left, right in zip(slow[:2], fast[:2]):
                    assert_frame_equal(left, right, check_exact=True)
                    np.testing.assert_array_equal(np.signbit(left.to_numpy()), np.signbit(right.to_numpy()))

    def test_all_terminal_self_values_and_empty_edge_indices(self):
        self.equal(Toy(np.zeros((4, 4)), np.ones((4, 4)), [0., .3, 1., .7]))

    def test_no_terminal_cycle_keeps_three_part_return(self):
        self.equal(Toy([[0., 1.], [1., 0.]], np.ones((2, 2)), [.4, .7]))

    def test_finite_and_zero_nan_infinite_efficiencies(self):
        dc = np.array([[0., .2, .3, .5], [0., 0., .8, .2], [0., 0., 0., 1.], [0., 0., 0., 0.]])
        for value in (0., np.nan, np.inf, -np.inf, .12345678912345678):
            te = np.full((4, 4), .13)
            te[0, 1] = value
            self.equal(Toy(dc, te, [.4, .7, .8, 1.]))

    def test_random_graphs_and_original_safety_valve(self):
        random = np.random.default_rng(20261115)
        for _ in range(20):
            dc = random.uniform(.01, .9, (7, 7))
            dc[random.uniform(size=(7, 7)) < .65] = 0
            np.fill_diagonal(dc, 0)
            dc[-2:] = 0
            te = np.exp(random.uniform(-5, 3, (7, 7)))
            self.equal(Toy(dc, te, random.uniform(.1, 1., 7)), max_paths=2)

    def test_unknown_scientific_body_is_rejected(self):
        changed = self.source.replace('prod = 1.0', 'prod = 2.0', 1)
        with self.assertRaisesRegex(ValueError, 'authenticated|body|hash'):
            parity.repair_fast_source(changed)

    def test_raw_crlf_source_keeps_original_newlines(self):
        raw_source = self.source.replace('\r\n', '\n').replace('\n', '\r\n')
        derived, _ = parity.repair_fast_source(raw_source, force_fast=True)
        self.assertNotIn('\n', derived.replace('\r\n', ''))
        self.assertEqual(parity.method_hash(derived), parity.method_hash(
            parity.repair_fast_source(self.source, force_fast=True)[0]))

    def test_bay_uses_same_authenticated_method_and_forced_route_is_exact(self):
        bay, _ = parity.archived_source('LME_034')
        self.assertEqual(parity.method_hash(bay), parity.method_hash(self.source))
        forced, _ = parity.repair_fast_source(self.source, force_fast=True)
        forced_method = parity.compile_method(forced)
        model = Toy([[0., 1.], [0., 0.]], np.full((2, 2), .2), [.5, 1.])
        expected = self.slow(model, 'TE', use_EE=True, return_paths=True)
        actual = forced_method(model, 'TE', use_EE=True, return_paths=True)
        assert_frame_equal(expected[0], actual[0], check_exact=True)
        assert_frame_equal(expected[1], actual[1], check_exact=True)
        self.assertEqual(actual[2], {})


if __name__ == '__main__':
    unittest.main()
