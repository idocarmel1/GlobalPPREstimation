import unittest
from atlas.core import rank_regions, select_regions

class CoreTests(unittest.TestCase):
    def test_selected_set_excludes_unselected_high_seas(self):
        result = select_regions([{'unit_id':'LME_001'}, {'unit_id':'EEZ_016'}], [{'unit_id':'HS_001'}, {'unit_id':'EEZ_016'}, {'unit_id':'LME_001'}])
        self.assertEqual({r['unit_id'] for r in result}, {'LME_001','EEZ_016'})

    def test_selection_rejects_missing_geometry_record(self):
        with self.assertRaises(ValueError):
            select_regions([{'unit_id':'EEZ_016'}], [])

    def test_ties_and_missing_ppr(self):
        rows = rank_regions([{'unit_id':i,'ppr':v} for i,v in [('a',60),('b',20),('c',20),('d',0),('e',None)]])
        self.assertEqual([r['ppr_rank'] for r in rows], [1,2,2,4,None])
        self.assertAlmostEqual(rows[0]['global_ppr_share'],.6)
        self.assertAlmostEqual(rows[2]['cumulative_ppr_share'],1)
        self.assertIsNone(rows[-1]['global_ppr_share'])

if __name__ == '__main__':
    unittest.main()
