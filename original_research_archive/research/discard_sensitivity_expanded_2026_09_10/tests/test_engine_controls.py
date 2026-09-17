"""Independent whole-food-web fixtures exercise the actual private engine adapter."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from baseline import PPRCalculator,calculate
from scenarios import make_scenario,physical_diagnostics


def toy(det_diet=.2):
    idx=[3,2,1]
    c=PPRCalculator.__new__(PPRCalculator)
    c.n_groups=3;c.seq2name={1:'plants',2:'fish',3:'detritus'};c.name2seq={v:k for k,v in c.seq2name.items()}
    c._groups_df=pd.DataFrame(dict(group_name=['detritus','fish','plants'],trophic_info=['DET','Regular','PP'],biomass=[1.,1.,1.]),index=idx)
    c._DC=pd.DataFrame(0.,index=idx,columns=idx);c._DC.loc[2,1]=1-det_diet;c._DC.loc[2,3]=det_diet
    c._det_fate=pd.DataFrame(1.,index=idx,columns=[3])
    p_mort=100-50*(1-det_diet)
    det_q=p_mort+5+10
    for attr,vals in dict(p=[det_q,10,100],q=[det_q,50,100],M0=[0,5,p_mort],egestion=[0,10,0],
        respiration=[0,30,0],catch=[0,5,0],predation=[50*det_diet,0,50*(1-det_diet)],
        growth=[det_q-50*det_diet,0,0],net_migration=[0,0,0],EE=[1,.5,1-p_mort/100],
        GE=[1,.2,1],det_export=[0,0,0]).items():
        setattr(c,attr,pd.Series(vals,index=idx,dtype=float))
    c._groups_df['q']=c.q
    return c


@pytest.mark.parametrize('route,f',[('SC',0),('SM',.2),('SM',.75),('SE',.5),('SR',.5)])
def test_convergent_engine_loop_against_independent_equations(route,f):
    base=toy();fate=pd.DataFrame(1.,index=base.p.index,columns=[3])
    c,l=make_scenario(base,f,route,return_fate=fate if route=='SR' else None)
    frame=calculate(c,'new_GE');coefficient=frame.sum(axis=1)
    extra=5*f if route in ('SM','SR') else 0
    denominator=75+extra
    # x=4+d, d=(60+(5+extra)*x)/(75+extra), independently
    # solved without using any engine matrix or engine detritus coefficients.
    independent=np.linalg.solve([[1.,-1.],[-(5+extra)/denominator,1.]],[4.,60/denominator])
    np.testing.assert_allclose([coefficient[2],coefficient[3]],independent,rtol=1e-7,atol=1e-8)
    assert physical_diagnostics(c,l)['ledger_closes']


def test_no_recycling_path_leaves_caught_fish_invariant():
    base=toy(det_diet=0)
    values=[calculate(make_scenario(base,f,route)[0],'new_GE').sum(axis=1)[2]
        for f in (0,.5,1) for route in ('SC','SM','SE')]
    np.testing.assert_allclose(values,5.)
