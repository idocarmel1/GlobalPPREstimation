from pathlib import Path
import sys,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from baseline import FRACTIONS
from screen import ecological_hash
from summarize import finalize_model,distribution

def test_dense_grid_exact_and_not_interpolated():
    assert FRACTIONS==[i/100 for i in range(21)]+[.25,.3,.4,.5,.75,1.]
    assert len(FRACTIONS)==27

def test_canonical_duplicates_ignore_taxonomy_pedigree_numeric_format_and_group_order():
    a={'group':[{'group_seq':'1','group_name':'Producer','biomass':'2.0','pp':'1','taxon_descr':{'x':1}},
                {'group_seq':'2','group_name':'Fish','biomass':'3','pp':'0','diet_descr':{'diet':[{'prey_seq':'1','proportion':'1.0','detritus_fate':'0'}]}}]}
    b=copy.deepcopy(a);b['group'].reverse();b['group'][1]['biomass']=2;b['group'][1]['taxon_descr']={'x':999}
    assert ecological_hash(a)==ecological_hash(b)
    b['group'][1]['biomass']=2.5
    assert ecological_hash(a)!=ecological_hash(b)

def study(baseline_gap=.01,imports=0):
    def r(route,f,gap,value):return dict(method='new_GE',scope='all',route=route,fraction=f,valid=True,status='valid',diagnostics={'ledger_sppr_relative_gap':gap},
        reasons=[],ppr_fixed_H_tC=value,ppr_retained_L_tC=(1-f)*value,standard_relative_excess_pct=0,standard_absolute_difference_tC=0)
    return dict(models=[dict(denominator_value=100,native_import_production_tC=imports,cohort='additional')],records=[r('S0',0,baseline_gap,20),r('SM',.2,.01,30)])

def test_invalid_baseline_cannot_sneak_into_paired_decomposition():
    s=finalize_model(study(.2))
    assert not s['records'][0]['valid']
    x=s['records'][1]
    assert x['valid'] and x['ppr_fixed_H_tC']==30
    assert x['baseline_ppr_fixed_H_tC'] is None and x['coefficient_change_pct'] is None
    assert all(v is None for v in x['decomposition'].values())

def test_import_boundary_guard_preserves_ppr_but_suppresses_ratio():
    s=finalize_model(study(imports=1))
    assert s['records'][1]['ppr_fixed_H_tC']==30
    assert s['records'][1]['ppr_to_native_pp_pct'] is None
    assert s['records'][1]['ppr_retained_to_native_pp_pct'] is None

def test_coefficient_numerator_interaction_and_units():
    x=finalize_model(study())['records'][1]
    assert x['coefficient_change_pct']==50
    assert x['decomposition']==dict(coefficient_effect=10,catch_effect=-4,interaction=-2,total_change=4,residual=0)

def test_no_valid_values_are_unavailable_not_zero_distribution():
    assert all(v is None for v in distribution([]).values())

def test_source_fate_audit_distinguishes_zero_bookkeeping_from_erased_transfer(monkeypatch):
    import pandas as pd
    from types import SimpleNamespace
    from screen import detritus_source_checks,ModelData
    idx=[10,11];raw=pd.DataFrame(0.,index=idx,columns=idx)
    data=SimpleNamespace(groups_data=pd.DataFrame({'trophic_info':['DET','DET'],'biomass_accum':[float('nan')]*2},index=idx),
        data_json={},det_fate=pd.DataFrame([[1.,0.],[0.,1.]],index=idx,columns=idx))
    monkeypatch.setattr(ModelData,'get_DC',staticmethod(lambda _: (None,raw)))
    zero=pd.Series([0.,0.],index=idx);positive=pd.Series([1.,1.],index=idx)
    reasons,a=detritus_source_checks(data,zero,positive,positive,zero)
    assert not reasons and a['fate_class']=='zero_row_identity_bookkeeping'
    raw.loc[10,11]=1.
    reasons,a=detritus_source_checks(data,zero,positive,positive,zero)
    assert reasons and a['nonzero_fate_overwritten']

def test_missing_detritus_inflow_cannot_be_financed_by_invented_stock_draw(monkeypatch):
    import pandas as pd
    from types import SimpleNamespace
    from screen import detritus_source_checks,ModelData
    idx=[10];fate=pd.DataFrame([[1.]],index=idx,columns=idx)
    data=SimpleNamespace(groups_data=pd.DataFrame({'trophic_info':['DET'],'biomass_accum':[float('nan')]},index=idx),data_json={},det_fate=fate)
    monkeypatch.setattr(ModelData,'get_DC',staticmethod(lambda _: (None,fate)))
    zero=pd.Series([0.],index=idx);one=pd.Series([1.],index=idx);draw=pd.Series([-.1],index=idx)
    reasons,a=detritus_source_checks(data,draw,one,zero,zero)
    assert reasons and a['negative_inferred_detritus_accumulation_groups']==[10]
    data.groups_data.loc[10,'biomass_accum']=-.1
    reasons,a=detritus_source_checks(data,draw,one,zero,zero)
    assert not reasons and not a['negative_inferred_detritus_accumulation_groups']
