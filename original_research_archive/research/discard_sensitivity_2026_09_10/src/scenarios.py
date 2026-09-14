"""Private adapter for explicit fishery, external-loss and detritus-return routes.

The frozen engine remains unchanged. Already initialized living-group physiology and
diet stay fixed. Detritus accumulation is the explicit dependent closure variable.
"""
from copy import deepcopy
import numpy as np
import pandas as pd
from baseline import PPRCalculator
from ledger import from_calculator,route_ledger


class LedgerCalculator(PPRCalculator):
    def _build_det_BC(self,sppr_basis,non_DET_sppr,DET_seq,DC,TE_option):
        B,c=super()._build_det_BC(sppr_basis,non_DET_sppr,DET_seq,DC,TE_option)
        # Whole dead fish carry their donor group's production requirement into the
        # explicitly documented destination. This is separate from natural M0.
        for i,det in enumerate(DET_seq):
            if self.q[det]<=0: continue
            donor=self.discard_return[det]/self.q[det]
            c[i]+=float(donor@non_DET_sppr.reindex(donor.index).fillna(0))
            for j,other in enumerate(DET_seq):
                B[i,j]+=float(donor@sppr_basis[other].reindex(donor.index).fillna(0))
        return B,c

    def get_Z(self,DET_as_PP=False):
        z=super().get_Z(DET_as_PP=DET_as_PP)
        if not DET_as_PP and hasattr(self,'discard_return'):
            for det in self.get_DET_seq(): z.loc[det,:]+=self.discard_return[det].reindex(z.columns)
        return z


def make_scenario(base,fraction,route,return_fate=None):
    ledger=route_ledger(from_calculator(base),fraction,route)
    c=LedgerCalculator.__new__(LedgerCalculator)
    c.__dict__=deepcopy(base.__dict__)
    # Never use balanced_model or call an initializer after changing the ledger.
    # The initializer derives dependent fields and cannot represent external_loss.
    c.balanced_model=None
    c.external_loss=ledger.external_loss.copy()
    c.catch=ledger.fishery_catch.copy()
    c.M0=ledger.mortality.copy()
    living=base.get_Regular_seq()+base.get_PP_seq()
    c.EE.loc[living]=ledger.ee.loc[living]
    c.discard_return=pd.DataFrame(0.,index=c.p.index,columns=c.get_DET_seq())
    if route=='SR':
        if return_fate is None: raise ValueError('SR requires an explicit source-supported destination')
        fate=return_fate.reindex(index=c.p.index,columns=c.get_DET_seq())
        if fate.isna().any().any() or (fate<0).any().any() or (fate.sum(axis=1)>1+1e-10).any():
            raise ValueError('invalid or missing discard return fate; no normalization allowed')
        c.discard_return=fate.mul(ledger.designated_discard,axis=0)
    ledger['explicit_discard_return']=c.discard_return.sum(axis=1)
    ledger['discard_return_external']=ledger.designated_discard-ledger.explicit_discard_return if route=='SR' else 0.
    flow=c.M0+c.egestion
    fate=c._det_fate.reindex(index=c.p.index,columns=c.get_DET_seq())
    if fate.isna().any().any() or (fate<0).any().any() or (fate.sum(axis=1)>1+1e-8).any():
        raise ValueError('invalid natural detritus fate; no normalization allowed')
    inflows=fate.mul(flow,axis=0).sum(axis=0)+c.discard_return.sum(axis=0)
    for det in c.get_DET_seq():
        c.q.loc[det]=inflows[det]
        c.p.loc[det]=inflows[det]
        c.growth.loc[det]=inflows[det]-c.predation[det]-c.net_migration[det]-c.catch[det]-c.external_loss[det]
    c.det_export=(1-fate.sum(axis=1))*flow
    c.weight_mode='catch_weighted' if c.catch.sum()>0 else 'biomass_fallback'
    for column,attr in {'p':'p','q':'q','M0':'M0','ee':'EE','catch':'catch',
                        'biomass_accum':'growth','det_export':'det_export'}.items():
        c._groups_df[column]=getattr(c,attr)
    c._groups_df['flow_to_det']=flow
    c._groups_df['pb']=c.p/c._groups_df.biomass
    c._groups_df['qb']=c.q/c._groups_df.biomass
    ledger.loc[c.get_DET_seq(),'production']=c.p.loc[c.get_DET_seq()]
    ledger.loc[c.get_DET_seq(),'consumption']=c.q.loc[c.get_DET_seq()]
    ledger.loc[c.get_DET_seq(),'accumulation']=c.growth.loc[c.get_DET_seq()]
    ledger['production_residual']=ledger.production-(ledger.predation+ledger.mortality+
        ledger.fishery_catch+ledger.external_loss+ledger.accumulation+ledger.migration)
    ledger['consumption_residual']=ledger.consumption-ledger.production-ledger.egestion-ledger.respiration
    return c,ledger


def physical_diagnostics(c,ledger):
    living=c.get_Regular_seq()+c.get_PP_seq()
    regular=c.get_Regular_seq()
    det=c.get_DET_seq()
    prod=ledger.production_residual.loc[living]
    cons=ledger.consumption_residual.loc[regular]
    fate=c._det_fate.reindex(index=c.p.index,columns=det)
    expected=fate.mul(c.M0+c.egestion,axis=0).sum(axis=0)+c.discard_return.sum(axis=0)
    detres=expected-(c.predation.loc[det]+c.growth.loc[det]+c.net_migration.loc[det]+c.catch.loc[det]+c.external_loss.loc[det])
    inflow=c.p.loc[c.get_PP_seq()+c.get_Import_seq()].sum()
    external=(c.catch+c.external_loss+c.growth+c.net_migration+c.det_export+c.respiration).sum()-c.discard_return.sum().sum()
    whole=float(inflow-external)
    prodrel=float((prod.abs()/ledger.production.loc[living].abs().clip(lower=1e-12)).max())
    consrel=float((cons.abs()/ledger.consumption.loc[regular].abs().clip(lower=1e-12)).max())
    knownneg={field:[int(i) for i in getattr(c,field).index[getattr(c,field)<-1e-8]]
              for field in ['p','q','M0','egestion','respiration','catch','external_loss']}
    return dict(max_living_production_residual=float(prod.abs().max()),
        max_living_production_relative_residual=prodrel,max_consumption_relative_residual=consrel,
        max_consumption_residual=float(cons.abs().max()),max_detritus_residual=float(detres.abs().max()),
        whole_system_residual=whole,whole_system_relative_residual=abs(whole)/max(abs(float(inflow)),1.),
        detritus_inflow=float(expected.sum()),detritus_accumulation=float(c.growth.loc[det].sum()),
        returned_discard=float(c.discard_return.sum().sum()),external_discard=float(c.external_loss.sum()),
        max_ee=float(c.EE.loc[living].max()),min_ee=float(c.EE.loc[living].min()),
        negative_physical_flows={k:v for k,v in knownneg.items() if v},
        negative_living_accumulation=[int(i) for i in living if c.growth[i]<-1e-8],
        ledger_closes=bool(prodrel<1e-4 and consrel<1e-4 and detres.abs().max()<1e-7 and abs(whole)/max(abs(float(inflow)),1.)<1e-4),
        balance_tolerance='1e-4 group-relative living/consumption and whole; 1e-7 absolute detritus; original rounding residuals preserved',
        catch_weight_mode=c.weight_mode)
