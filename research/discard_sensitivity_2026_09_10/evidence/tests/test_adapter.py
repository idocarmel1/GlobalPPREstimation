import sys
from pathlib import Path
from copy import deepcopy
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from baseline import load_baseline,model_paths,calculate
from ledger import from_calculator
from scenarios import make_scenario, physical_diagnostics


@pytest.fixture(scope='module')
def base(): return load_baseline(next(p for p in model_paths() if p.stem.startswith('28_')))[0]


def test_adapter_updates_engine_fields_without_reinitialization(base):
    c,l=make_scenario(base,.2,'SM')
    np.testing.assert_allclose(c.M0,base.M0+.2*base.catch)
    np.testing.assert_allclose(c._groups_df.M0,c.M0)
    idx=base.get_Regular_seq()
    np.testing.assert_allclose(c.get_TE('TE',as_matrix=False).loc[idx],
                               (base.p.loc[idx]-c.M0.loc[idx])/base.q.loc[idx])
    assert c.growth.loc[c.get_DET_seq()].sum()-base.growth.loc[c.get_DET_seq()].sum()==pytest.approx(.2*base.catch.sum())
    original=make_scenario(base,0,'SC')
    assert physical_diagnostics(c,l)['max_living_production_residual']==pytest.approx(
        physical_diagnostics(*original)['max_living_production_residual'],abs=1e-10)
    assert physical_diagnostics(c,l)['ledger_closes']


def test_external_loss_has_distinct_weights_and_equivalent_flow_result(base):
    a,_=make_scenario(base,.4,'SC');b,ledger=make_scenario(base,.4,'SE')
    np.testing.assert_allclose(b.catch,.6*base.catch)
    np.testing.assert_allclose(b.external_loss,.4*base.catch)
    np.testing.assert_allclose(a.get_TE('global',as_matrix=False),b.get_TE('global',as_matrix=False))
    np.testing.assert_allclose(calculate(a,'new_GE'),calculate(b,'new_GE'),rtol=1e-8)
    assert physical_diagnostics(b,ledger)['max_living_production_residual']==pytest.approx(
        physical_diagnostics(*make_scenario(base,0,'SC'))['max_living_production_residual'],abs=1e-10)
    np.testing.assert_allclose(b.net_migration,base.net_migration)


def test_explicit_return_uses_one_source_flow(base):
    det=base.get_DET_seq()[0]
    destinations=pd.DataFrame(0.,index=base.p.index,columns=[det]);destinations[det]=1.
    c,ledger=make_scenario(base,.2,'SR',return_fate=destinations)
    np.testing.assert_allclose(c.M0,base.M0)
    np.testing.assert_allclose(c.catch,base.catch)
    assert c.q.loc[det]-base.q.loc[det]==pytest.approx(.2*base.catch.sum())
    assert c.discard_return.sum().sum()==pytest.approx(.2*base.catch.sum())
    assert physical_diagnostics(c,ledger)['max_detritus_residual']<1e-8


def test_sr_requires_documented_destination(base):
    with pytest.raises(ValueError,match='destination'):
        make_scenario(base,.2,'SR')


def test_source_alias_is_only_one_sink(base):
    assert 'catch' in base._model.groups_data
    assert 'export' not in base._model.groups_data


def test_fraction_one_mean_switch_is_exposed(base):
    c,_=make_scenario(base,1,'SE')
    assert c.catch.sum()==0
    assert c.weight_mode=='biomass_fallback'
