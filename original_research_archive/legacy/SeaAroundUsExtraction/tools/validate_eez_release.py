"""Independent numeric and exported-XLSX audit of the all-EEZ TE=0.1 release."""
from pathlib import Path
import argparse
import json
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NS = {'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'

# The boolean checks ppr_pipeline.validation.validate_region emits, named here in one
# place instead of as string literals inside validate(). Selecting checks by name and
# then calling .all() passes vacuously when the selection is empty, so a removed or
# renamed check would be reported as a pass; boolean_check() below requires the rows
# to exist first. group_ppr_within_convexity_bound is the one-sided invariant that
# group PPR never exceeds the taxon-summed PPR, since 10 ** (TL - 1) is convex.
BOOLEAN_CHECK_NAMES = ('catch_reconciled','group_ppr_within_convexity_bound','tl_coverage_complete')


def boolean_check(validation, name):
    """Return whether a named boolean check passed; fail loudly if it is absent."""
    values = validation.loc[validation['check']==name,'value'].astype(str).str.lower()
    assert not values.empty, f'validation.csv has no {name} check'
    return bool(values.eq('true').all())


def workbook_cells(path):
    """Read cached exported values independently of the workbook generator."""
    with zipfile.ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings = [''.join(e.itertext()) for e in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        relations = {r.get('Id'): r.get('Target') for r in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
        sheets = {}
        formulas = 0
        for sheet in ET.fromstring(archive.read('xl/workbook.xml')).find('m:sheets',NS):
            target = relations[sheet.get(RID)]
            name = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            cells = {}
            for cell in ET.fromstring(archive.read(name)).findall('.//m:sheetData/m:row/m:c',NS):
                assert cell.get('t') != 'e', f'Excel error {path.name}/{sheet.get("name")}/{cell.get("r")}'
                value = cell.find('m:v',NS)
                if cell.find('m:f',NS) is not None:
                    formulas += 1
                raw = value.text if value is not None else None
                if cell.get('t') == 's':
                    raw = strings[int(raw)]
                elif cell.get('t') == 'inlineStr':
                    raw = ''.join(cell.find('m:is',NS).itertext())
                elif raw is not None and cell.get('t') not in ('str', 's'):
                    raw = float(raw)
                cells[cell.get('r')] = raw
            sheets[sheet.get('name')] = cells
        return sheets, formulas


def check_value(actual, expected, label='value'):
    if pd.isna(expected):
        assert actual is None or actual == '' or pd.isna(actual), (label, actual, expected)
    elif isinstance(expected, (bool, np.bool_)):
        assert actual in (True, False, 0, 1) and actual == expected, (label, actual, expected)
    elif isinstance(expected, str):
        assert actual == expected, (label, actual, expected)
    else:
        dimensionless=any(word in label for word in ('fraction','coverage','ratio','percent'))
        assert isinstance(actual, (int, float, np.number)) and np.isclose(
            actual, expected, rtol=1e-11, atol=1e-12 if dimensionless else 1e-6), (label, actual, expected)


def check_table_cells(cells, expected):
    """Check all expected columns, cached values, and exact data-row extent."""
    headers = {v:k[:-1] for k,v in cells.items() if re.fullmatch(r'[A-Z]+1',k)}
    assert set(expected.columns) <= set(headers), ('missing headers',set(expected.columns)-set(headers))
    for row, values in enumerate(expected.itertuples(index=False,name=None),2):
        for field,value in zip(expected.columns,values):
            address=f'{headers[field]}{row}'
            check_value(cells.get(address),value,address+'/'+field)
    for address,value in cells.items():
        match=re.fullmatch(r'([A-Z]+)(\d+)',address)
        if match and int(match[2])>len(expected)+1:
            assert value is None or value == '', ('unexpected data row',address,value)


def check_groups(source, groups, classification):
    """Reconstruct all group results, retaining unknown versus known-zero PPR.

    This deliberately recomputes the catch-weighted-mean-TL (Jensen-affected)
    aggregation independently of ``ppr_pipeline.calculations.aggregate_groups``,
    rather than importing it, so the two implementations can be cross-checked.
    """
    key=f'{classification}_group'
    names=source[key].fillna('Unclassified').replace('','Unclassified')
    assert groups[key].is_unique and set(groups[key]) == set(names)
    indexed=groups.set_index(key)
    for name in sorted(set(names)):
        part=source.loc[names==name]
        matched=part.loc[part.tl.notna()]
        catch=float(matched.catch_tonnes.sum())
        mean=float((matched.catch_tonnes*matched.tl).sum()/catch) if catch>0 else np.nan
        sppr=10.**(mean-1) if catch>0 else np.nan
        ppr=catch*sppr if catch>0 else np.nan
        expected=dict(catch_tonnes_matched=catch,tl_weighted=mean,sppr=sppr,ppr=ppr)
        for field,value in expected.items():
            check_value(indexed.loc[name,field],value,f'{classification}/{name}/{field}')


def reconstruct_comparison(root, metadata):
    """Use unit manifests and species rows, never supplied summary numbers/shares."""
    rows=[]
    for directory in ('eez_output',metadata.get('comparison_output_directory','global_output')):
        tables=root/directory/'tables'
        run=json.loads((tables/'run_metadata.json').read_text(encoding='utf8'))
        assert run['year']==metadata['year'] and run['transfer_efficiency']==.1
        units=json.loads((tables/'units.json').read_text(encoding='utf8'))
        assert len({u['unit_id'] for u in units})==len(units)
        for unit in units:
            source=pd.read_csv(tables/'regions'/unit['unit_id']/'species.csv')
            for field in ('catch_tonnes','tl','ppr'):
                source[field]=pd.to_numeric(source[field])
            assert source.catch_tonnes.ge(0).all()
            for field,expected in [('unit_id',unit['unit_id']),('region_type',unit['region_type']),('year',run['year'])]:
                if field in source:
                    assert source[field].eq(expected).all(), (unit['unit_id'],field)
            powers=source.catch_tonnes*10.**(source.tl-1)
            assert np.allclose(source.ppr,powers,rtol=1e-12,atol=1e-6,equal_nan=True)
            rows.append(dict(unit_id=unit['unit_id'],region_name=unit['name'],region_type=unit['region_type'],
                year=run['year'],total_catch_tonnes=float(source.catch_tonnes.sum()),ppr_species=float(powers.sum())))
    result=pd.DataFrame(rows).sort_values(['region_type','ppr_species','unit_id'],ascending=[True,False,True]).reset_index(drop=True)
    assert result.unit_id.is_unique
    result['fraction_type_ppr']=np.nan
    result['rank_type_ppr']=0
    result['accumulated_fraction_type']=np.nan
    for kind,part in result.groupby('region_type',sort=False):
        denominator=float(part.ppr_species.sum())
        running=0.
        for rank,index in enumerate(part.index,1):
            fraction=float(result.loc[index,'ppr_species'])/denominator if denominator else np.nan
            running+=fraction
            result.loc[index,['fraction_type_ppr','rank_type_ppr','accumulated_fraction_type']]=[fraction,rank,running]
    return result


def check_comparison(actual, expected):
    assert actual.unit_id.is_unique and set(actual.unit_id)==set(expected.unit_id)
    assert actual.unit_id.tolist()==expected.unit_id.tolist(), 'not in deterministic type/PPR/ID order'
    for field in expected.columns:
        assert field in actual
        for unit,a,e in zip(expected.unit_id,actual[field],expected[field]):
            check_value(a,e,f'{unit}/{field}')


def check_compact_cells(cells, expected, within_type):
    frame=expected[['unit_id','region_name','region_type','total_catch_tonnes','ppr_species',
                    'fraction_type_ppr','rank_type_ppr','accumulated_fraction_type']].copy()
    rename={'accumulated_fraction_type':'accumulated fraction'}
    if not within_type:
        rename.update(fraction_type_ppr='fraction_eez_ppr',rank_type_ppr='rank_eez_ppr')
    check_table_cells(cells,frame.rename(columns=rename))


def check_empty_region(sheets, row):
    for field in ('total_catch_tonnes','ppr_species'):
        check_value(row[field],0.,'empty region/'+field)
    for name in ('Species','Commercial','Functional'):
        for address,value in sheets[name].items():
            if int(re.search(r'\d+$',address)[0])>1:
                assert value is None or value=='', ('empty region data',name,address,value)


def check_workbooks(output, summary, flags, pairs, expected_comparison=None):
    if expected_comparison is None:
        metadata=json.loads((output/'tables/run_metadata.json').read_text())
        expected_comparison=reconstruct_comparison(output.parent,metadata)
    files = list((output/'regional_calculations').glob('*.xlsx'))
    assert len(files) == len(summary)
    formula_count = 0
    by_id = summary.set_index('unit_id')
    workbook_ids=['_'.join(path.stem.split('_')[:2]) for path in files]
    assert len(set(workbook_ids))==len(files) and set(workbook_ids)==set(summary.unit_id)
    for path in files:
        unit_id = '_'.join(path.stem.split('_')[:2])
        sheets, count = workbook_cells(path)
        formula_count += count
        assert sheets['Metadata']['B5'] == .1
        species = pd.read_csv(output/'tables/regions'/unit_id/'species.csv')
        assert count > 0 or len(species) == 0, f'No formulas in populated workbook {path}'
        if species.empty:
            check_empty_region(sheets,by_id.loc[unit_id])
        for classification in ('commercial','functional'):
            groups=pd.read_csv(output/'tables/regions'/unit_id/f'{classification}.csv')
            check_groups(species,groups,classification)
            check_table_cells(sheets[classification.title()],groups)
        for i,row in enumerate(species.itertuples(index=False),2):
            actual = sheets['Species'].get(f'U{i}')
            if pd.isna(row.tl):
                assert actual in (None,'')
            else:
                assert np.isclose(actual,row.catch_tonnes*10**(row.tl-1),rtol=1e-11,atol=1e-6)
        total = sum(float(v or 0) for k,v in sheets['Species'].items() if re.fullmatch(r'U[2-9]\d*|U1\d+',k))
        assert np.isclose(total,by_id.loc[unit_id,'ppr_species'],rtol=1e-11,atol=1e-6)
    sheets, count = workbook_cells(output/'PPR_eez_summary.xlsx')
    assert count > 0
    formula_count += count
    assert sheets['Configuration']['B7'] == .1
    assert {'summarized summary','All Areas Summary','EEZ Selection Flags','EEZ LME Pairs','Selection Rules'} <= set(sheets)
    compact = sheets['summarized summary']
    check_compact_cells(sheets['All Areas Summary'],expected_comparison,True)
    expected_eez=expected_comparison.loc[expected_comparison.region_type=='EEZ'].reset_index(drop=True)
    check_compact_cells(compact,expected_eez,False)
    check_table_cells(sheets['EEZ LME Pairs'],pairs)
    check_table_cells(sheets['EEZ Selection Flags'],flags)
    keyed = flags.set_index('unit_id')
    flag_cols = ['flag_add_low_lme_overlap','flag_prefer_eez_candidate','flag_review_110_120']
    for i,row in enumerate(summary.itertuples(index=False),2):
        assert compact[f'A{i}'] == row.unit_id
        for col,flag in zip('IJK',flag_cols):
            assert bool(compact[f'{col}{i}']) == bool(keyed.loc[row.unit_id,flag]), (row.unit_id,flag)
    return {'workbook_count':len(files)+1,'formula_count':formula_count,'formula_errors':0}


def validate(root=ROOT, *, workbooks=True):
    output = root/'eez_output'
    tables = output/'tables'
    metadata = json.loads((tables/'run_metadata.json').read_text())
    spatial = json.loads((tables/'spatial_validation.json').read_text())
    catalog = json.loads((root/'raw_data/SAU_downloads/eez_regions.json').read_text(encoding='utf8'))['data']
    summary = pd.read_csv(tables/'eez_summary.csv')
    flags = pd.read_csv(tables/'eez_selection_flags.csv')
    pairs = pd.read_csv(tables/'eez_lme_intersections.csv')
    expected_ids = {f'EEZ_{int(r["id"]):03d}' for r in catalog}
    assert set(summary.unit_id) == set(flags.unit_id) == expected_ids
    assert summary.unit_id.is_unique and flags.unit_id.is_unique
    assert metadata['transfer_efficiency'] == .1
    assert metadata['unit_count'] == len(expected_ids) == spatial['eez_count']
    assert set(summary.region_type) == {'EEZ'}
    assert summary.year.nunique() == 1
    years = pd.read_csv(tables/'year_availability.csv')
    assert years.loc[years.constrains_common_year,'contains_selected_year'].all()
    archive_audit = pd.read_csv(tables/'archive_audit.csv')
    assert set(archive_audit.unit_id) == expected_ids
    assert (archive_audit.data_version == 50.1).all()
    validation = pd.read_csv(tables/'validation.csv')
    missing_checks = sorted(set(BOOLEAN_CHECK_NAMES) - set(validation['check']))
    assert not missing_checks, f'validation.csv is missing expected boolean checks: {missing_checks}'
    checks = validation.loc[validation.unit=='boolean','value'].astype(str).str.lower()
    assert not checks.empty
    assert checks.eq('true').all()
    for name in BOOLEAN_CHECK_NAMES:
        assert boolean_check(validation,name), name
    total_rows = 0
    for row in summary.itertuples(index=False):
        source = pd.read_csv(tables/'regions'/row.unit_id/'species.csv')
        for column in ('catch_tonnes','tl','ppr'):
            source[column] = pd.to_numeric(source[column])
        total_rows += len(source)
        expected = source.catch_tonnes * 10.**(source.tl-1)
        assert np.allclose(source.ppr,expected,rtol=1e-12,atol=1e-6,equal_nan=True)
        assert np.isclose(source.catch_tonnes.sum(),row.total_catch_tonnes,rtol=1e-12,atol=1e-6)
        assert np.isclose(source.ppr.sum(),row.ppr_species,rtol=1e-12,atol=1e-6)
        matched=source.loc[source.tl.notna()]
        check_value(row.matched_catch_tonnes,float(matched.catch_tonnes.sum()),row.unit_id+'/matched catch')
        check_value(row.missing_tl_catch_tonnes,float(source.loc[source.tl.isna(),'catch_tonnes'].sum()),row.unit_id+'/missing TL catch')
        for classification in ('commercial','functional'):
            groups = pd.read_csv(tables/'regions'/row.unit_id/f'{classification}.csv')
            check_groups(source,groups,classification)
    thresholds = spatial['thresholds']
    assert np.allclose(flags.lme_overlap_fraction_of_eez,flags.lme_union_intersection_km2/flags.area_km2)
    assert flags.flag_add_low_lme_overlap.equals(flags.lme_overlap_fraction_of_eez < thresholds['low_overlap_threshold'])
    assert np.allclose(pairs.intersection_fraction_of_lme,pairs.intersection_km2/pairs.lme_area_km2)
    assert np.allclose(pairs.eez_to_lme_area_ratio,pairs.eez_area_km2/pairs.lme_area_km2)
    contained = pairs.intersection_fraction_of_lme >= thresholds['containment_threshold']
    assert contained.equals(pairs.lme_mostly_contained)
    assert np.allclose(pairs.intersection_fraction_of_eez,pairs.intersection_km2/pairs.eez_area_km2)
    prefer = contained & (pairs.eez_to_lme_area_ratio >= thresholds['prefer_ratio'])
    review = contained & (pairs.eez_to_lme_area_ratio >= thresholds['review_ratio']) & (pairs.eez_to_lme_area_ratio < thresholds['prefer_ratio'])
    assert prefer.equals(pairs.flag_prefer_eez_candidate)
    assert review.equals(pairs.flag_review_110_120)
    for flag in ('flag_prefer_eez_candidate','flag_review_110_120'):
        selected = set(pairs.loc[pairs[flag],'eez_unit_id'])
        assert set(flags.loc[flags[flag],'unit_id']) == selected
    for fraction in ('lme_overlap_fraction_of_eez','hs_overlap_fraction_of_eez'):
        assert flags[fraction].between(-1e-8,1+1e-5).all()
    import geopandas as gpd
    for name,count in [('EEZs.geojson',len(expected_ids)),('LMEs.geojson',66),('HighSeas.geojson',18)]:
        layer = gpd.read_file(output/'spatial'/name)
        assert len(layer)==count and layer.crs.to_epsg()==4326 and layer.is_valid.all()
    comparison = pd.read_csv(tables/'all_areas_summary.csv')
    expected_comparison=reconstruct_comparison(root,metadata)
    assert set(expected_comparison.loc[expected_comparison.region_type=='EEZ','unit_id'])==expected_ids
    assert len(expected_comparison)==len(summary)+84
    check_comparison(comparison,expected_comparison)
    expected_eez=expected_comparison.loc[expected_comparison.region_type=='EEZ'].reset_index(drop=True)
    check_comparison(summary.rename(columns={'fraction_eez_ppr':'fraction_type_ppr',
        'rank_eez_ppr':'rank_type_ppr'}),expected_eez.drop(columns='accumulated_fraction_type'))
    catch = summary.total_catch_tonnes.sum()
    report = {'status':'passed','year':int(summary.year.iloc[0]),'transfer_efficiency':.1,
        'eez_count':len(summary),'species_rows':total_rows,'empty_catch_units':summary.loc[summary.total_catch_tonnes==0,'unit_id'].tolist(),
        'catch_tonnes_sum_across_eezs':float(catch),'ppr_sum_across_eezs':float(summary.ppr_species.sum()),
        'catch_tl_coverage_fraction':float(summary.matched_catch_tonnes.sum()/catch),
        'missing_tl_catch_tonnes':float(summary.missing_tl_catch_tonnes.sum()),
        'flag_counts':spatial['flag_counts'],'tl_coverage_complete':boolean_check(validation,'tl_coverage_complete'),
        'group_ppr_within_convexity_bound':boolean_check(validation,'group_ppr_within_convexity_bound'),
        'totals_by_spatial_type_not_additive':comparison.groupby('region_type').agg(units=('unit_id','size'),catch_tonnes=('total_catch_tonnes','sum'),ppr=('ppr_species','sum')).reset_index().to_dict('records')}
    if workbooks:
        report.update(check_workbooks(output,summary,flags,pairs,expected_comparison))
    (output/'release_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-workbooks',action='store_true')
    args = parser.parse_args()
    print(json.dumps(validate(workbooks=not args.skip_workbooks),indent=2))
