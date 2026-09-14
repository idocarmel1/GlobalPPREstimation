import json
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def study(): return json.loads((ROOT/'results/study.json').read_text(encoding='utf-8'))


def test_saved_deterministic_baselines_are_reproduced(study):
    assert len(study['baseline_checks'])>=55
    assert all(x['passed'] for x in study['baseline_checks'])


def test_every_requested_fraction_method_scope_route_is_preserved(study):
    assert study['fraction_grid']==[0,.01,.05,.1,.2,.3,.4,.5,.75,1]
    identities={(r['model_id'],r['method'],r['scope'],r['route'],r['fraction']) for r in study['records']}
    assert len(identities)==len(study['records'])
    for model in study['models']:
        for method in study['methods']:
            for scope in study['scopes']:
                for f in study['fraction_grid']:
                    for route in study['routes']:
                        assert (model['model_id'],method,scope,route,f) in identities


def test_fixed_support_totals_and_retained_boundary(study):
    for r in study['records']:
        if not r['valid']: continue
        groups=study['groups'][r['scenario_id']]
        assert r['ppr_fixed_H_tC']==pytest.approx(sum(g['sppr']*g['H']/9 for g in groups),rel=1e-9,abs=1e-8)
        assert r['ppr_retained_L_tC']==pytest.approx((1-r['fraction'])*r['ppr_fixed_H_tC'],rel=1e-9,abs=1e-8)
        assert r['coverage_fraction']==1.


def test_sc_coefficient_invariance_and_zero_fraction_identity(study):
    baseline={(r['model_id'],r['method'],r['scope']):r for r in study['records'] if r['route']=='S0'}
    for r in study['records']:
        if r['route']!='SC' and not (r['fraction']==0 and r['route'] in ('SM','SE','SR')): continue
        sid=r['scenario_id'];b=baseline[r['model_id'],r['method'],r['scope']]
        if sid not in study['groups']: continue
        a=study['groups'][sid];expected=study['groups'][b['scenario_id']]
        np.testing.assert_allclose([g['sppr'] for g in a],[g['sppr'] for g in expected],rtol=2e-7,atol=1e-7)


def test_sc_se_equivalence_below_mean_weight_endpoint(study):
    rows={(r['model_id'],r['method'],r['scope'],r['fraction'],r['route']):r for r in study['records']}
    for r in study['records']:
        if r['route']!='SE' or r['fraction']==1: continue
        sc=rows[r['model_id'],r['method'],r['scope'],r['fraction'],'SC']
        if r['scenario_id'] not in study['groups']: continue
        np.testing.assert_allclose([g['sppr'] for g in study['groups'][r['scenario_id']]],
            [g['sppr'] for g in study['groups'][sc['scenario_id']]],rtol=2e-7,atol=1e-7)


def test_invalids_are_not_zero_and_standard_scopes_are_compatible(study):
    for r in study['records']:
        if not r['valid']:
            assert r['ppr_fixed_H_tC'] is None and r['ppr_retained_L_tC'] is None
            assert r['reasons']
        if r['scope']!='all':
            assert r['fixed_standard_ppr_tC'] is None
            assert r['standard_relative_excess_pct'] is None
        if r['valid']:
            d=r['decomposition']
            if d['residual'] is not None: assert abs(d['residual'])<1e-8


def test_no_harvest_never_becomes_assessed_map_response():
    r=json.loads((ROOT/'results/discard_responses.v1.json').read_text(encoding='utf-8'))
    model=next(m for m in r['response_models'] if m['model_id'].startswith('52_'))
    assert model['status']=='not_assessed_zero_source_harvest'
    for scopes in model['methods'].values():
        for s in scopes.values():
            for route in s['routes'].values():
                assert not route['valid_intervals']
                assert not any(p['valid'] for p in route['points'])


def test_convergence_is_separate_from_conservation(study):
    r=next(r for r in study['records'] if r['model_id'].startswith('13_') and r['method']=='new_TE_EEfix' and r['scope']=='all' and r['route']=='S0')
    assert r['numerical_valid']
    assert r['physical_valid']
    assert r['method_conservation_valid'] is False
    assert not r['valid']
    assert r['raw_numeric_ppr_fixed_H_tC']>0


def test_imported_numerator_has_no_internal_pp_ratio(study):
    bay=next(m for m in study['models'] if m['model_id'].startswith('34_'))
    assert bay['native_import_production_tC']>0
    for r in study['records']:
        if r['model_id']==bay['model_id'] and r['scope']=='all':
            assert r['native_denominator_compatible'] is False
            assert r['ppr_to_native_pp_pct'] is None
            assert r['ppr_retained_to_native_pp_pct'] is None
            assert r['native_ratio_reason']


def test_response_group_identity_uses_frozen_workbook_seq_and_unicode_names():
    import openpyxl
    package=json.loads((ROOT/'results/discard_responses.v1.json').read_text(encoding='utf-8'))
    for model in package['response_models']:
        path=ROOT/'inputs/PPREstimation/output/top10'/f'{model["model_id"]}.xlsx'
        wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
        rows=list(wb['sppr_all'].values);wb.close()
        names={row[0]:row[1] for row in rows[1:]}
        for scopes in model['methods'].values():
            for scope in scopes.values():
                assert scope['group_names']==[names[seq] for seq in scope['group_ids']]
