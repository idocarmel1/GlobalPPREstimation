"""Focused two-pool controls, independent of the Celtic Sea source numbers."""
from pathlib import Path
import sys,unittest
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from PPRCalculator import PPRCalculator
try:
 from routing_adapter import RoutingExperimentCalculator
except ImportError:
 # Red-phase control: the unchanged engine is the behavior being corrected.
 RoutingExperimentCalculator=PPRCalculator

def fixture():
 c=RoutingExperimentCalculator.__new__(RoutingExperimentCalculator)
 idx=[4,3,2,1]
 c.p=pd.Series([6.,2.,4.,10.],index=idx);c.q=pd.Series([6.,2.,10.,10.],index=idx)
 c.M0=pd.Series([0.,0.,2.,2.],index=idx);c.egestion=pd.Series([0.,0.,2.,0.],index=idx)
 c.catch=pd.Series([0.,0.,2.,0.],index=idx)
 c.growth=pd.Series([1.,.25,0.,0.],index=idx);c.net_migration=pd.Series(0.,index=idx)
 c._groups_df=pd.DataFrame({'q':c.q,'trophic_info':['DET','DET','Regular','PP']},index=idx)
 c._DC=pd.DataFrame(0.,index=idx,columns=idx);c._DC.loc[2,1]=.5;c._DC.loc[2,3]=.2;c._DC.loc[2,4]=.3
 c._det_fate=pd.DataFrame(0.,index=idx,columns=[3,4]);c._det_fate.loc[[1,2],4]=1.
 c.discard_return=pd.DataFrame(0.,index=idx,columns=[3,4]);c.discard_return.loc[2,3]=2.
 c.name2seq={};c.seq2name={i:str(i) for i in idx}
 return c

class ReturnTests(unittest.TestCase):
 def test_nonfeeding_basal_missing_import_does_not_destroy_identity_basis(self):
  c=fixture();c._DC.loc[[1,3,4],2]=np.nan;c._DC.loc[2,2]=np.nan
  dc=c.get_DC(DET_as_PP=True)
  self.assertEqual(int(dc.loc[[1,3,4]].isna().sum().sum()),0)
  self.assertTrue(np.isnan(dc.loc[2,2]))
  self.assertTrue(np.isnan(c._DC.loc[1,2]))

 def test_return_ancestry_enters_each_recycling_equation_once(self):
  c=fixture();idx=c.p.index
  basis=pd.DataFrame({3:[0.,1.,2.,0.],4:[1.,0.,3.,0.]},index=idx)
  non=pd.Series([0.,0.,5.,1.],index=idx)
  B,v=c._build_det_BC(basis,non,[3,4],c._DC,'GE')
  np.testing.assert_allclose(B,[[2,3],[2/3,1]])
  np.testing.assert_allclose(v,[5,2])

 def test_whole_fish_return_keeps_catch_and_natural_mortality_separate(self):
  c=fixture();z=c.get_Z(DET_as_PP=False)
  self.assertEqual(z.loc[3,2],2.)
  self.assertEqual(z.loc[4,2],4.)
  self.assertEqual(c.catch[2],2.)
  self.assertEqual(c.M0[2],2.)
  self.assertEqual(c.growth[3],.25)
  self.assertEqual(c.get_Z(DET_as_PP=True).loc[3].sum(),0.)

 def test_internal_return_subtracted_from_external_export_once(self):
  c=fixture();sppr=pd.Series([4.,3.,5.,1.],index=c.p.index)
  _,inflow,outflow=c.is_sppr_balanced(sppr)
  self.assertEqual(inflow,10.)
  self.assertEqual(outflow,4*1+3*.25)

 def test_te_return_cannot_silently_drop_donor_ancestry(self):
  c=fixture()
  with self.assertRaisesRegex(ValueError,'TE_RETURN_UNSUPPORTED'):
   c.SPPR_new(TE_option='TE')

if __name__=='__main__':unittest.main()
