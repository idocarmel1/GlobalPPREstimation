import unittest
import json
from assumed_allocation import allocate


class AllocationTests(unittest.TestCase):
    def candidates(self, catches, biomass):
        return [dict(group_id=i + 1, group=f'Group {i+1}',
                     eligibility='Documented taxonomic and ecological fit',
                     catch=c, biomass=b) for i, (c, b) in enumerate(zip(catches, biomass))]

    def test_catch_precedes_biomass_and_preserves_zero(self):
        r = allocate(self.candidates([3, 1, 0], [1, 8, 9]))
        self.assertEqual(r['field'], 'catch')
        self.assertEqual(r['weights'], [0.75, 0.25, 0])
        self.assertEqual(r['confidence'], 'Medium')

    def test_incomplete_catch_uses_complete_biomass(self):
        r = allocate(self.candidates([3, None], [2, 6]))
        self.assertEqual(r['field'], 'biomass')
        self.assertEqual(r['weights'], [0.25, 0.75])
        self.assertEqual(r['confidence'], 'Medium')

    def test_all_zero_catch_uses_biomass(self):
        self.assertEqual(allocate(self.candidates([0, 0], [2, 2]))['weights'], [0.5, 0.5])

    def test_invalid_complete_proportions_stay_unresolved(self):
        for catches, biomass in [([None, 1], [1, None]), ([0, 0], [0, 0]), ([-9999, 1], [-9999, 2])]:
            self.assertEqual(allocate(self.candidates(catches, biomass))['confidence'], 'Unresolved')

    def test_candidates_cannot_be_selected_by_the_math(self):
        self.assertEqual(allocate([])['confidence'], 'Unresolved')
        c = self.candidates([1, 2], [3, 4]); c[0]['eligibility'] = ''
        self.assertEqual(allocate(c)['confidence'], 'Unresolved')
        c[0]['eligibility'] = 'fit'; c[1]['group_id'] = 1
        with self.assertRaises(ValueError): allocate(c)

    def geographic(self):
        return dict(values_by_group={1: 80, 2: 20}, source='Source table 2',
                    area_boundaries='Two reported strata',
                    group_correspondence='Each stratum corresponds to its named group',
                    period='2019', catch_basis='landings', units='t',
                    applicability='Same taxon, region, year and catch basis',
                    directly_measured=True)

    def test_direct_geography_precedes_model_proxy(self):
        r = allocate(self.candidates([1, 9], [9, 1]), geographic=self.geographic())
        self.assertEqual(r['weights'], [0.8, 0.2])
        self.assertEqual(r['confidence'], 'High')
        self.assertEqual(r['field'], 'source_geographic_catch')
        self.assertEqual(r['evidence']['source'], 'Source table 2')

    def test_geographic_ids_survive_json_roundtrip(self):
        g = json.loads(json.dumps(self.geographic()))
        r = allocate(self.candidates([1, 9], [9, 1]), geographic=g)
        self.assertEqual(r['weights'], [0.8, 0.2])
        self.assertEqual(r['confidence'], 'High')

    def test_geographic_id_alias_collision_is_rejected(self):
        g = self.geographic(); g['values_by_group']['1'] = 999
        with self.assertRaises(ValueError):
            allocate(self.candidates([1, 9], [9, 1]), geographic=g)

    def test_geographic_overlap_cannot_acquire_high_confidence(self):
        g = self.geographic(); g['directly_measured'] = False
        r = allocate(self.candidates([1, 9], [9, 1]), geographic=g)
        self.assertEqual(r['weights'], [0.1, 0.9])
        self.assertEqual(r['confidence'], 'Medium')
        self.assertFalse(r['attempts'][0]['usable'])

    def test_missing_geographic_candidate_or_provenance_falls_back(self):
        for field in ['source', 'area_boundaries', 'group_correspondence', 'period',
                      'catch_basis', 'units', 'applicability']:
            g = self.geographic(); del g[field]
            self.assertEqual(allocate(self.candidates([1, 9], [9, 1]), geographic=g)['field'], 'catch')
        for values in [{1: 80}, {1: 80, 2: 20, 3: 10}, {1: 80, 2: None}, {1: 0, 2: 0}]:
            g = self.geographic(); g['values_by_group'] = values
            self.assertEqual(allocate(self.candidates([1, 9], [9, 1]), geographic=g)['field'], 'catch')


if __name__ == '__main__':
    unittest.main()
