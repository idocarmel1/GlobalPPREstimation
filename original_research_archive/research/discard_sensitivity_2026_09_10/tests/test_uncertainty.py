import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from uncertainty import valid_intervals, scenario_envelope


def test_invalid_midpoint_cannot_be_interpolated_across():
    rows=[dict(fraction=x,valid=good,diagnostics={}) for x,good in [(0,True),(.1,False),(.2,True),(.3,True)]]
    assert valid_intervals(rows,'new_GE')==[[.2,.3]]


def test_biomass_fallback_is_not_a_smooth_endpoint():
    rows=[dict(fraction=.75,valid=True,diagnostics={'catch_weight_mode':'catch_weighted'}),
          dict(fraction=1.,valid=True,diagnostics={'catch_weight_mode':'biomass_fallback'})]
    assert valid_intervals(rows,'SPPR_1995_TEmean')==[]


def test_envelope_excludes_failed_but_reports_failure_count():
    rows=[dict(route='SC',valid=True,ppr_fixed_H_tC=10.,ppr_retained_L_tC=8.),
          dict(route='SM',valid=True,ppr_fixed_H_tC=9.,ppr_retained_L_tC=7.2),
          dict(route='SR',valid=False,ppr_fixed_H_tC=None,ppr_retained_L_tC=None)]
    x=scenario_envelope(rows)
    assert x['min_fixed_H_tC']==9 and x['max_fixed_H_tC']==10
    assert x['n_invalid_or_unavailable']==1
    assert x['valid_routes']==['SC','SM']
