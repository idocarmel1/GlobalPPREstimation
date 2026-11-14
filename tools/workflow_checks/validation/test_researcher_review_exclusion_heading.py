"""Signed removal wording must not produce a false no-exclusion display note."""
import unittest
from tools.project_core.validation.researcher_review import exclusion_note, removed_group_names


class ExclusionHeadingTests(unittest.TestCase):
    def test_numbered_single_line_diagnostic_list_names_each_exact_group(self):
        text = ('Groups removed from calculation:\nNear-zero TE: BaleenWhales (1), '
                'ToothedWhales (2), Seals (3), SurfaceFeedingSeabirds (4) and DivingSeabirds (65).')
        self.assertEqual(removed_group_names(text), ['baleenwhales', 'toothedwhales', 'seals',
                         'surfacefeedingseabirds', 'divingseabirds'])
        self.assertNotIn('Near-zero', exclusion_note(text))

    def test_signed_singular_and_plural_calculation_headings_name_removed_group(self):
        for heading in ['Removed groups from calculation:', 'Removed groups from calculations:']:
            with self.subTest(heading=heading):
                note = exclusion_note(heading + '\nM. mammals (GE=0.1%, SPPR_GE=110K)\n')
                self.assertIn('m. mammals are excluded from displayed PPR', note)
                self.assertNotIn('no model groups are excluded', note)

    def test_no_removals_does_not_parse_unrelated_parenthetical_notes(self):
        note = exclusion_note('No groups were removed from the calculation.\nDetritus (29) retained.')
        self.assertIn('no model groups are excluded', note)

    def test_signed_bare_group_name_is_not_reported_as_no_exclusion(self):
        for heading in ['Removed groups from calculation:', 'Removed groups from calculations:']:
            with self.subTest(heading=heading):
                note = exclusion_note(heading + '\nMarine mammals\n')
                self.assertIn('marine mammals are excluded from displayed PPR', note)
                self.assertNotIn('no model groups are excluded', note)

    def test_groups_removed_heading_preserves_signed_taxonomic_parenthetical(self):
        for heading in ['Groups removed from calculation:', 'Groups removed from calculations:']:
            with self.subTest(heading=heading):
                text = heading + '\n- Toothed whales (all) – GE < 0.01.'
                self.assertEqual(removed_group_names(text), ['toothed whales (all)'])
                note = exclusion_note(text)
                self.assertIn('toothed whales (all) are excluded from displayed PPR', note)
                self.assertNotIn('no model groups are excluded', note)
                self.assertNotIn('GE <', note)

    def test_groups_removed_heading_strips_only_diagnostic_details(self):
        text = ('Groups removed from calculation:\n'
                '• M. mammals (GE=0.1%, SPPR_GE=110K)\n'
                '- Toothed whales (all) (GE=0.1%, SPPR_TE=110K)\n')
        self.assertEqual(removed_group_names(text), ['m. mammals', 'toothed whales (all)'])

    def test_legacy_heading_keeps_existing_registered_note_wording(self):
        note = exclusion_note('Removed groups from calculation:\n- Toothed whales (all) (GE=0.1%)')
        self.assertEqual(note, 'Following researcher review, toothed whales are excluded from displayed PPR. '
                         'Model loading, diagnostics and saved workbook calculations retain all groups.')


if __name__ == '__main__':
    unittest.main()
