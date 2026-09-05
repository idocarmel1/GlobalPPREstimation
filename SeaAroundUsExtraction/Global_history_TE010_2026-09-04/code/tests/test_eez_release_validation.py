"""Mutation tests for the independent release audit; no spreadsheet authoring dependency."""
import importlib.util
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SPEC = importlib.util.spec_from_file_location('eez_audit', Path(__file__).parents[1]/'tools/validate_eez_release.py')
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def call(name, *args):
    assert hasattr(audit, name), f'Missing independent validator: {name}'
    return getattr(audit, name)(*args)


GROUP_COLUMNS = ['commercial_group','taxon_count_total','taxon_count_matched',
    'catch_tonnes_total','catch_tonnes_matched','catch_tonnes_missing_tl',
    'catch_coverage_fraction','sppr_correct','ppr_correct','tl_weighted_jensen',
    'sppr_jensen','ppr_jensen','jensen_difference','jensen_ratio_correct_to_error','jensen_percent_difference']


def group_fixture(matched=False):
    source = pd.DataFrame({'commercial_group':['Unknown'], 'functional_group':['Unknown'],
        'catch_tonnes':[0. if matched else 5.], 'tl':[3. if matched else np.nan],
        'ppr':[0. if matched else np.nan]})
    values = ['Unknown',1,int(matched),0. if matched else 5.,0.,0. if matched else 5.,
              np.nan if matched else 0.,np.nan,0. if matched else np.nan,*([np.nan]*6)]
    return source, pd.DataFrame([values],columns=GROUP_COLUMNS)


@pytest.mark.parametrize('matched',[False,True])
def test_group_unknown_and_zero_catch_semantics(matched):
    source, groups = group_fixture(matched)
    call('check_groups', source, groups, 'commercial')


@pytest.mark.parametrize('column,value', [('ppr_correct',0.),('catch_tonnes_missing_tl',0.),
    ('taxon_count_matched',1),('sppr_correct',0.),('ppr_jensen',0.),('jensen_difference',0.)])
def test_unmatched_group_rejects_invented_numeric_results_and_hidden_missing_tl(column,value):
    source, groups = group_fixture()
    groups.loc[0,column] = value
    assert hasattr(audit,'check_groups')
    with pytest.raises(AssertionError):
        audit.check_groups(source,groups,'commercial')


def literal_comparison():
    return pd.DataFrame([
        ['EEZ_001','First','EEZ',2019,1.,100.,.25,1.,2],
        ['EEZ_002','Second','EEZ',2019,3.,300.,.75,.75,1],
        ['LME_001','LME','LME',2019,2.,200.,1.,1.,1],
    ],columns=['unit_id','region_name','region_type','year','total_catch_tonnes','ppr_species',
               'fraction_type_ppr','accumulated_fraction_type','rank_type_ppr']).iloc[[1,0,2]].reset_index(drop=True)


@pytest.mark.parametrize('kind',['unequal','tie','zero'])
@pytest.mark.parametrize('comparison_directory',['other_year','global_output'])
def test_reconstruction_uses_regional_species_and_configured_comparison_directory(tmp_path,kind,comparison_directory):
    catches={'unequal':(1,3),'tie':(1,1),'zero':(0,0)}[kind]
    for directory, units in [('eez_output',[('EEZ_001','First','EEZ',catches[0]),('EEZ_002','Second','EEZ',catches[1])]),
                             (comparison_directory,[('LME_001','LME','LME',2)])]:
        tables = tmp_path/directory/'tables'
        tables.mkdir(parents=True)
        (tables/'units.json').write_text(json.dumps([dict(unit_id=u,name=n,region_type=t) for u,n,t,c in units]))
        (tables/'run_metadata.json').write_text(json.dumps(dict(year=2019,transfer_efficiency=.1)))
        for unit,name,region_type,catch in units:
            folder=tables/'regions'/unit
            folder.mkdir(parents=True)
            pd.DataFrame(dict(catch_tonnes=[catch],tl=[3.],ppr=[100.*catch])).to_csv(folder/'species.csv',index=False)
    metadata={'year':2019}
    if comparison_directory!='global_output': metadata['comparison_output_directory']=comparison_directory
    actual = call('reconstruct_comparison',tmp_path,metadata)
    expected=literal_comparison()
    if kind!='unequal':
        expected=expected.iloc[[1,0,2]].reset_index(drop=True)
        expected.loc[:1,'total_catch_tonnes']=1. if kind=='tie' else 0.
        expected.loc[:1,'ppr_species']=100. if kind=='tie' else 0.
        expected.loc[:1,'fraction_type_ppr']=.5 if kind=='tie' else np.nan
        expected.loc[:1,'rank_type_ppr']=[1,2]
        expected.loc[:1,'accumulated_fraction_type']=[.5,1.] if kind=='tie' else [np.nan,np.nan]
    pd.testing.assert_frame_equal(actual[expected.columns],expected,check_dtype=False)


@pytest.mark.parametrize('mutation',['equal_shares','duplicate','replaced','rank','cumulative','catch','ppr','type','year'])
def test_comparison_rejects_core_mutations(mutation):
    expected=literal_comparison()
    actual=expected.copy()
    if mutation=='equal_shares': actual.loc[:1,'fraction_type_ppr']=.5
    elif mutation=='duplicate': actual.loc[1,'unit_id']='EEZ_002'
    elif mutation=='replaced': actual.loc[1,'unit_id']='EEZ_999'
    else:
        column={'rank':'rank_type_ppr','cumulative':'accumulated_fraction_type',
                'catch':'total_catch_tonnes','ppr':'ppr_species','type':'region_type','year':'year'}[mutation]
        actual.loc[0,column]='LME' if mutation=='type' else 42
    assert hasattr(audit,'check_comparison')
    with pytest.raises(AssertionError): audit.check_comparison(actual,expected)


def cells(frame):
    def col(n):
        text=''
        while n:
            n,r=divmod(n-1,26); text=chr(65+r)+text
        return text
    result={f'{col(i)}1':h for i,h in enumerate(frame.columns,1)}
    for r,values in enumerate(frame.itertuples(index=False,name=None),2):
        result.update({f'{col(c)}{r}':None if pd.isna(v) else v for c,v in enumerate(values,1)})
    return result


@pytest.mark.parametrize('column',list('ABCDEFGH'))
def test_compact_export_rejects_every_core_column_and_intermediate_cumulative(column):
    expected=literal_comparison()
    frame=expected[['unit_id','region_name','region_type','total_catch_tonnes','ppr_species',
                    'fraction_type_ppr','rank_type_ppr','accumulated_fraction_type']].rename(columns={'accumulated_fraction_type':'accumulated fraction'})
    exported=cells(frame)
    assert hasattr(audit,'check_compact_cells')
    audit.check_compact_cells(exported,expected,True)
    exported[f'{column}2']='wrong' if column in 'ABC' else 42
    with pytest.raises(AssertionError): audit.check_compact_cells(exported,expected,True)


@pytest.mark.parametrize('matched',[False,True])
def test_group_export_rejects_invented_blank_result(matched):
    source,groups=group_fixture(matched)
    exported=cells(groups)
    call('check_table_cells',exported,groups)
    exported['M2']=0.
    with pytest.raises(AssertionError): audit.check_table_cells(exported,groups)


@pytest.mark.parametrize('column',['lme_mostly_contained','flag_prefer_eez_candidate','flag_review_110_120'])
def test_pair_export_rejects_wrong_boolean_result(column):
    pairs=pd.DataFrame({'eez_unit_id':['EEZ_001'],'lme_unit_id':['LME_001'],
        'lme_mostly_contained':[True],'flag_prefer_eez_candidate':[True],'flag_review_110_120':[False]})
    exported=cells(pairs)
    call('check_table_cells',exported,pairs)
    key=next(k[:-1]+'2' for k,v in exported.items() if k.endswith('1') and v==column)
    exported[key]=not pairs.loc[0,column]
    with pytest.raises(AssertionError): audit.check_table_cells(exported,pairs)


@pytest.mark.parametrize('mutation',['none','species','commercial','functional','catch','ppr'])
def test_empty_regional_workbook_requires_no_data_and_zero_totals(mutation):
    source=pd.DataFrame(columns=['catch_tonnes','tl','ppr','commercial_group','functional_group'])
    groups=pd.DataFrame(columns=GROUP_COLUMNS)
    sheets={'Species':cells(source),'Commercial':cells(groups),'Functional':cells(groups.rename(columns={'commercial_group':'functional_group'}))}
    row=pd.Series(dict(total_catch_tonnes=0.,ppr_species=0.))
    if mutation in ('species','commercial','functional'): sheets[mutation.title()]['A2']='unexpected'
    if mutation=='catch': row['total_catch_tonnes']=1.
    if mutation=='ppr': row['ppr_species']=1.
    assert hasattr(audit,'check_empty_region')
    if mutation=='none': audit.check_empty_region(sheets,row)
    else:
        with pytest.raises(AssertionError): audit.check_empty_region(sheets,row)


def test_jensen_difference_allows_machine_cancellation_but_not_wrong_result():
    # Same mathematically zero difference after independent summation orders.
    audit.check_value(4.092726157978177e-12,-4.092726157978177e-12,'group/jensen_difference')
    with pytest.raises(AssertionError):
        audit.check_value(1.,0.,'group/jensen_difference')


@pytest.mark.parametrize('column',GROUP_COLUMNS[7:])
def test_known_group_export_rejects_each_numeric_result_column(column):
    # A single TL=3 member, catch=2: SPPR=100 and both PPR methods=200.
    groups=pd.DataFrame([['Known',1,1,2.,2.,0.,1.,100.,200.,3.,100.,200.,0.,1.,0.]],columns=GROUP_COLUMNS)
    exported=cells(groups)
    audit.check_table_cells(exported,groups)
    address=next(k[:-1]+'2' for k,v in exported.items() if k.endswith('1') and v==column)
    exported[address]=999.
    with pytest.raises(AssertionError): audit.check_table_cells(exported,groups)


@pytest.mark.parametrize('within_type',[False,True])
def test_compact_rejects_extra_data_rows(within_type):
    expected=literal_comparison()
    frame=expected[['unit_id','region_name','region_type','total_catch_tonnes','ppr_species',
        'fraction_type_ppr','rank_type_ppr','accumulated_fraction_type']].rename(columns={'accumulated_fraction_type':'accumulated fraction'})
    if not within_type: frame=frame.rename(columns={'fraction_type_ppr':'fraction_eez_ppr','rank_type_ppr':'rank_eez_ppr'})
    exported=cells(frame)
    audit.check_compact_cells(exported,expected,within_type)
    exported['A5']='unexpected'
    with pytest.raises(AssertionError): audit.check_compact_cells(exported,expected,within_type)


def test_parser_permits_genuine_formula_free_header_only_workbook(tmp_path):
    path=tmp_path/'empty.xlsx'
    main='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    rel='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    with zipfile.ZipFile(path,'w') as package:
        package.writestr('xl/workbook.xml',f'<workbook xmlns="{main}" xmlns:r="{rel}"><sheets><sheet name="Species" sheetId="1" r:id="rId1"/></sheets></workbook>')
        package.writestr('xl/_rels/workbook.xml.rels','<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
        package.writestr('xl/worksheets/sheet1.xml',f'<worksheet xmlns="{main}"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>taxon</t></is></c></row></sheetData></worksheet>')
    sheets,count=audit.workbook_cells(path)
    assert sheets=={'Species':{'A1':'taxon'}}
    assert count==0


@pytest.mark.parametrize('mutation',['none','commercial','functional','pair','all_area','compact_cumulative'])
def test_check_workbooks_checks_real_export_boundaries(tmp_path,monkeypatch,mutation):
    expected=literal_comparison()
    summary=expected.iloc[:2].drop(columns='accumulated_fraction_type').rename(columns={
        'fraction_type_ppr':'fraction_eez_ppr','rank_type_ppr':'rank_eez_ppr'})
    flags=pd.DataFrame({'unit_id':['EEZ_002','EEZ_001'],'flag_add_low_lme_overlap':[False,True],
        'flag_prefer_eez_candidate':[True,False],'flag_review_110_120':[False,False]})
    pairs=pd.DataFrame({'eez_unit_id':['EEZ_002'],'lme_unit_id':['LME_001'],
        'lme_mostly_contained':[True],'flag_prefer_eez_candidate':[True],'flag_review_110_120':[False]})
    output=tmp_path/'eez_output'
    (output/'regional_calculations').mkdir(parents=True)
    exports={}
    for row in summary.itertuples(index=False):
        folder=output/'tables/regions'/row.unit_id
        folder.mkdir(parents=True)
        source=pd.DataFrame({'commercial_group':['Known'],'functional_group':['Known'],
            'catch_tonnes':[row.total_catch_tonnes],'tl':[3.],'ppr':[row.ppr_species]})
        source.to_csv(folder/'species.csv',index=False)
        groups=pd.DataFrame([['Known',1,1,row.total_catch_tonnes,row.total_catch_tonnes,0.,1.,100.,
            row.ppr_species,3.,100.,row.ppr_species,0.,1.,0.]],columns=GROUP_COLUMNS)
        groups.to_csv(folder/'commercial.csv',index=False)
        functional=groups.rename(columns={'commercial_group':'functional_group'})
        functional.to_csv(folder/'functional.csv',index=False)
        path=output/'regional_calculations'/f'{row.unit_id}_name.xlsx'
        path.touch()
        exports[path.name]={'Metadata':{'B5':.1},'Species':{'U2':row.ppr_species},
            'Commercial':cells(groups),'Functional':cells(functional)}
    compact_columns=['unit_id','region_name','region_type','total_catch_tonnes','ppr_species',
                     'fraction_type_ppr','rank_type_ppr','accumulated_fraction_type']
    all_compact=expected[compact_columns].rename(columns={'accumulated_fraction_type':'accumulated fraction'})
    compact=all_compact.iloc[:2].rename(columns={'fraction_type_ppr':'fraction_eez_ppr','rank_type_ppr':'rank_eez_ppr'}).copy()
    for field in flags.columns[1:]: compact[field]=flags[field].to_numpy()
    exports['PPR_eez_summary.xlsx']={'Configuration':{'B7':.1},'All Areas Summary':cells(all_compact),
        'summarized summary':cells(compact),'EEZ Selection Flags':cells(flags),'EEZ LME Pairs':cells(pairs),'Selection Rules':{}}
    if mutation in ('commercial','functional'): exports['EEZ_002_name.xlsx'][mutation.title()]['I2']=999.
    elif mutation=='pair': exports['PPR_eez_summary.xlsx']['EEZ LME Pairs']['D2']=False
    elif mutation=='all_area': exports['PPR_eez_summary.xlsx']['All Areas Summary']['D2']=999.
    elif mutation=='compact_cumulative': exports['PPR_eez_summary.xlsx']['summarized summary']['H2']=.5
    monkeypatch.setattr(audit,'workbook_cells',lambda path:(exports[path.name],1))
    if mutation=='none':
        result=audit.check_workbooks(output,summary,flags,pairs,expected)
        assert result['workbook_count']==3
    else:
        with pytest.raises(AssertionError): audit.check_workbooks(output,summary,flags,pairs,expected)
