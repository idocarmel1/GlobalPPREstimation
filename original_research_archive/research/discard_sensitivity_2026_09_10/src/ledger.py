"""Physical accounting ledger; no legacy field aliases enter this layer."""
import numpy as np
import pandas as pd


def from_calculator(calc):
    names={'production':'p','consumption':'q','predation':'predation','mortality':'M0',
           'egestion':'egestion','respiration':'respiration','harvest':'catch',
           'accumulation':'growth','migration':'net_migration'}
    ledger=pd.DataFrame({key:getattr(calc,value).copy() for key,value in names.items()})
    ledger.index.name='group_id'
    ledger['group_name']=[calc.seq2name[i] for i in ledger.index]
    ledger['external_loss']=0.
    return ledger


def route_ledger(baseline, fraction, route):
    if not np.isfinite(fraction) or not 0<=fraction<=1:
        raise ValueError('fraction must be finite and within [0,1]')
    if route not in ('S0','SC','SM','SE','SR'):
        raise ValueError('unknown route')
    required=['production','consumption','predation','mortality','egestion','respiration',
              'harvest','accumulation','migration','external_loss']
    if baseline[required].isna().any().any():
        raise ValueError('missing physical ledger input')
    out=baseline.copy(deep=True)
    out['designated_discard']=fraction*out.harvest
    out['retained']=(1-fraction)*out.harvest
    out['fishery_catch']=out.harvest if route in ('S0','SC','SR') else out.retained
    out['explicit_discard_return']=out.designated_discard if route=='SR' else 0.
    if route=='SM': out['mortality']+=out.designated_discard
    if route=='SE': out['external_loss']+=out.designated_discard
    out['ee']=1-out.mortality/out.production.replace(0,np.nan)
    out['production_residual']=out.production-(out.predation+out.mortality+out.fishery_catch+
        out.external_loss+out.accumulation+out.migration)
    out['consumption_residual']=out.consumption-out.production-out.egestion-out.respiration
    return out
