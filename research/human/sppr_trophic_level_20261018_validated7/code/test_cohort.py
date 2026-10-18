"""Bounded checks for the exact cohort guard; no project files are changed."""
import unittest
from cohort import EXCLUDED_PAIR, REQUIRED_PAIRS, validate_pairs


class CohortGuardTests(unittest.TestCase):
    def test_exact_seven_pairs_pass(self):
        self.assertEqual(validate_pairs(list(reversed(REQUIRED_PAIRS))), sorted(REQUIRED_PAIRS))

    def test_old_eight_pair_cohort_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_pairs([*REQUIRED_PAIRS, EXCLUDED_PAIR])

    def test_duplicate_pair_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_pairs([*REQUIRED_PAIRS, REQUIRED_PAIRS[0]])

    def test_wrong_model_in_the_same_region_is_rejected(self):
        altered = list(REQUIRED_PAIRS)
        altered[0] = (altered[0][0], 'another_model')
        with self.assertRaises(ValueError):
            validate_pairs(altered)

    def test_missing_pair_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_pairs(REQUIRED_PAIRS[:-1])


if __name__ == '__main__':
    unittest.main()
