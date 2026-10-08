"""Signed removal wording must not produce a false no-exclusion display note."""
import unittest
from tools.project_core.validation.researcher_review import exclusion_note


class ExclusionHeadingTests(unittest.TestCase):
    def test_signed_singular_and_plural_calculation_headings_name_removed_group(self):
        for heading in ['Removed groups from calculation:', 'Removed groups from calculations:']:
            with self.subTest(heading=heading):
                note = exclusion_note(heading + '\nM. mammals (GE=0.1%, SPPR_GE=110K)\n')
                self.assertIn('m. mammals are excluded from displayed PPR', note)
                self.assertNotIn('no model groups are excluded', note)

    def test_no_removals_does_not_parse_unrelated_parenthetical_notes(self):
        note = exclusion_note('No groups were removed from the calculation.\nDetritus (29) retained.')
        self.assertIn('no model groups are excluded', note)


if __name__ == '__main__':
    unittest.main()
