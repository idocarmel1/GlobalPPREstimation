import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from original_atlas_data import fill_annual,detail_from_book
from workbooks import YEARS

class HtmlAdapterTests(unittest.TestCase):
    def test_current_values_replace_old_series(self):
        row={'unidentified':'method','catch_basis':'landings','metric':'ppr','status':'ok',**{y:float(y) for y in YEARS}}
        r=fill_annual([row],{'ppr':[999]*70,'status':'ok','sensitivity':[{'min_tC':123}]*70})
        self.assertEqual(r['ppr'][0],1950);self.assertNotIn('sensitivity',r)
        self.assertEqual(r['catch_bases']['catch']['status'],'unavailable')
        self.assertIsNone(r['catch_bases']['catch']['ppr'][0])
    def test_scope_sensitivity_is_preserved_only_with_current_bounds(self):
        base={'sensitivity':[{'route_evidence':'documented','min_tC':1,'max_tC':2} for _ in YEARS]}
        row={'unidentified':'method','catch_basis':'landings','metric':'min_tC','status':'assessed',**{y:10 for y in YEARS}}
        r=fill_annual([row],base)
        self.assertEqual(r['sensitivity'][0]['min_tC'],10)
        self.assertEqual(r['sensitivity'][0]['route_evidence'],'documented')

if __name__=='__main__':unittest.main()
