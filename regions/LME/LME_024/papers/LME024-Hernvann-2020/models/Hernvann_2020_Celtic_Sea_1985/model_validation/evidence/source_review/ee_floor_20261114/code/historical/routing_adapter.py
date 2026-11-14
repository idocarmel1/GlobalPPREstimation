"""Isolated return-accounting adapter; no changes to the shared scientific engine.

GE and With Egestion follow the explicit-return adapter in the frozen discard
study. TE is refused: its native direct-PP detritus scale has no donor-return
equation. This class does not balance the model or supply an absent inflow.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from PPRCalculator import PPRCalculator

class RoutingExperimentCalculator(PPRCalculator):
 def get_DC(self,DET_as_PP=True,normalize=False):
  dc=super().get_DC(DET_as_PP=DET_as_PP,normalize=normalize)
  # Four nonfeeding source groups (PP51/52, DET53/54) carry missing
  # diet-import cells. NumPy sum(NaN) otherwise prevents the native basal
  # identity test. Structural zeros exist only in this returned runtime copy;
  # stored/source cells and every consumer diet are untouched.
  if DET_as_PP:
   for i in self.get_PP_seq()+self.get_DET_seq():
    if dc.loc[i].sum()==0:dc.loc[i]=dc.loc[i].fillna(0.)
  return dc

 def _build_det_BC(self,sppr_basis,non_DET_sppr,DET_seq,DC,TE_option):
  B,c=super()._build_det_BC(sppr_basis,non_DET_sppr,DET_seq,DC,TE_option)
  for i,det in enumerate(DET_seq):
   if self.q[det]<=0:raise ValueError('Nonpositive detritus inflow in return experiment')
   donor=self.discard_return[det]/self.q[det]
   c[i]+=float(donor@non_DET_sppr.reindex(donor.index).fillna(0))
   for j,other in enumerate(DET_seq):
    B[i,j]+=float(donor@sppr_basis[other].reindex(donor.index).fillna(0))
  self.last_recycling_system={'B':B.copy(),'c':c.copy(),'det_seq':list(DET_seq)}
  return B,c

 def get_Z(self,DET_as_PP=False):
  z=super().get_Z(DET_as_PP=DET_as_PP)
  if not DET_as_PP:
   for det in self.get_DET_seq():
    z.loc[det,:]+=self.discard_return[det].reindex(z.columns).fillna(0)
  return z

 def is_sppr_balanced(self,sppr,diet_import_equations=None):
  if diet_import_equations is not None:
   raise ValueError('Experimental adapter only supports direct diagnose_sppr numeric accounting')
  s=PPRCalculator.rename_results(sppr,self.name2seq)
  if isinstance(s,pd.DataFrame):s=s.sum(axis=1)
  # Harvest retains L+D as a living mortality term; only L exits the system.
  # The same D enters its detritus destination through the recycling equation.
  external=self.catch+self.growth+self.net_migration-self.discard_return.sum(axis=1)
  inflow=float(self.p[self.get_PP_seq()+self.get_Import_seq()].sum())
  outflow=float(external.mul(s,fill_value=1).sum())
  return bool(np.isclose(inflow,outflow)),inflow,outflow

 def SPPR_new(self,*args,**kwargs):
  te=kwargs.get('TE_option','GE')
  if te=='TE' and float(self.discard_return.to_numpy().sum())>0:
   raise ValueError('TE_RETURN_UNSUPPORTED: native TE direct-PP detritus scaling has no donor-return term; a faithful positive-discard-return coefficient calculation is unavailable')
  if kwargs.get('det_collapse_mode','never')!='never':
   raise ValueError('Pooling is not authorized in this two-pool experiment')
  ans=super().SPPR_new(*args,**kwargs)
  self.last_solve=tuple(x.copy() for x in ans)
  return ans
