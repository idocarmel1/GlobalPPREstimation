import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from ledger import route_ledger


def fixture():
    return pd.DataFrame([dict(group_id=1, group_name='fish', production=100., consumption=200.,
        predation=20., mortality=30., egestion=40., respiration=60., harvest=50.,
        accumulation=0., migration=0., external_loss=0.)]).set_index('group_id')


@pytest.mark.parametrize('route,catch,mortality,external,ee', [
    ('SC',50,30,0,.7), ('SM',40,40,0,.6), ('SE',40,30,10,.7)])
def test_analytic_production_fixture(route,catch,mortality,external,ee):
    x=route_ledger(fixture(), .2, route)
    assert x.loc[1,'fishery_catch']==catch
    assert x.loc[1,'mortality']==mortality
    assert x.loc[1,'external_loss']==external
    assert x.loc[1,'ee']==ee
    assert x.loc[1,'production_residual']==0
    assert x.loc[1,'retained']+x.loc[1,'designated_discard']==50


@pytest.mark.parametrize('route',['SC','SM','SE'])
def test_zero_fraction_identity_and_endpoints(route):
    x=route_ledger(fixture(),0,route)
    assert x.loc[1,'mortality']==30
    assert x.loc[1,'fishery_catch']==50
    y=route_ledger(fixture(),1,route)
    assert y.loc[1,'retained']==0
    assert y.loc[1,'designated_discard']==50
    assert y.loc[1,'production_residual']==0


def test_missing_harvest_is_not_zero():
    f=fixture(); f.loc[1,'harvest']=np.nan
    with pytest.raises(ValueError,match='missing'):
        route_ledger(f,.5,'SM')


def test_return_is_counted_once():
    x=route_ledger(fixture(),.2,'SM')
    assert x.loc[1,'mortality']-30==10
    assert x.loc[1,'explicit_discard_return']==0

