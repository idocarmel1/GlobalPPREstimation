"""Check published EE-floor settings, coefficient sources, annual series and review scope."""
from pathlib import Path
import gzip, json, math, sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
from tools.project_core.maps.original_atlas_data import embedded, calculation_provenance
from tools.project_core.maps.build_html import _stale_reviewed_payload_units
from tools.project_core.calculations.coverage import _metadata, validated_identities
from tools.project_core.registry.discovery import region_directory, resolve_model
from tools.project_core.workbooks.workbooks import read_book, records, sha
from tools.scientific_helpers.sppr.method_coverage import method_inventory

WORK = Path(__file__).resolve().parents[1]

def equal(a, b):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, (int,float)) and isinstance(b, (int,float)):
        return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)
    return a == b

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(value,ensure_ascii=False,allow_nan=False).encode(),mtime=0))

def verify():
    directory=ROOT/'interactive_map'
    catalog, map_layout=embedded(directory/'index.html','DB')
    series, trend_layout=embedded(directory/'trends.html','SERIES_DB')
    project_hash=sha(ROOT/'Project.xlsx')
    for page in (map_layout,trend_layout):
        assert f'<meta name="ppr-project-sha256" content="{project_hash}">' in page
        assert 'PPREeFloor?.append' in page
    metadata=_metadata(ROOT)
    identities=validated_identities(metadata)
    wanted=set(identities)
    assert not _stale_reviewed_payload_units(ROOT,directory,[row for row in metadata
               if (row['unit_id'],row['model_id']) in wanted])
    methods=set(method_inventory()); results=[]
    years=[str(y) for y in series['years']]
    source_page=(directory/'sources.html').read_text(encoding='utf-8')
    for unit,mid in identities:
        model_dir=resolve_model(region_directory(ROOT,unit),mid).parent
        book=read_book(region_directory(ROOT,unit)/(unit+'.xlsx'))
        manifest=json.loads((model_dir/'results/result_manifest.json').read_text(encoding='utf-8'))
        flags=manifest['effective_flags']; provenance=calculation_provenance(book)
        assert provenance['use_ee_floor'] is True and provenance['ee_floor']==.1
        assert provenance['effective_loader_flags']==flags
        ledger={row['group_name']:row for row in records(book,'Diagnostics','EE floor groups')}
        coefficients={(row['scope'],row['group'],row['method']):row['sppr']
                      for row in records(book,'Selected model groups','Group SPPR')}
        annual={(row['scope'],row['method'],row['catch_basis'],row['unidentified'],row['metric']):row
                for row in records(book,'PPR','Annual')}
        checked_groups=checked_annual=0
        mapped=[]
        for collection in (catalog['network']['units'],series['units']):
            payload=next(m for m in collection[unit]['models'] if m['id']==mid)
            mapped.append(payload)
            assert payload['calculation_provenance']==provenance
            assert payload['workbook_sha256']==sha(ROOT/payload['workbook'])
            assert (ROOT/payload['source']).resolve()==model_dir/'sppr_source.xlsx'
            group_data=payload['group_data']; assert set(group_data['methods'])==methods
            for scope,matrix in group_data['scopes'].items():
                for group,values in zip(group_data['groups'],matrix,strict=True):
                    for method,value in zip(group_data['methods'],values,strict=True):
                        assert equal(value,coefficients[(scope,group['id'],method)]), (unit,scope,group['id'],method)
                        checked_groups+=1
            for group in group_data['groups']:
                row=ledger[group['id']]
                for field,column in [('source_ee','source_EE'),('source_m0','source_M0'),
                                     ('ee_before_floor','EE_before_floor'),('m0_before_floor','M0_before_floor'),
                                     ('ee','EE_effective'),('m0_effective','M0_effective'),
                                     ('external_mortality_export','external_mortality_export')]:
                    assert equal(group[field],row[column]), (unit,group['id'],field)
        assert mapped[0].get('researcher_review')==mapped[1].get('researcher_review')
        assert mapped[0].get('display_ppr_excluded_group_ids')==mapped[1].get('display_ppr_excluded_group_ids')
        assert mid in source_page and unit in source_page
        for scope,saved in mapped[1]['scopes'].items():
            assert set(saved['methods'])==methods
            for method,value in saved['methods'].items():
                for policy,policy_value in [('method',value),('zero',value.get('unidentified_zero')),
                                           ('simple',value.get('unidentified_simple'))]:
                    if policy_value is None:continue
                    for basis,basis_value in [('landings',policy_value),*policy_value.get('catch_bases',{}).items()]:
                        for metric in ('ppr','catch','covered_catch'):
                            if metric not in basis_value:continue
                            row=annual[(scope,method,basis,policy,metric)]
                            for year,number in zip(years,basis_value[metric],strict=True):
                                column=year if year in row else int(year)
                                assert equal(number,row[column]), (unit,scope,method,basis,policy,metric,year)
                                checked_annual+=1
        entry={'unit_id':unit,'model_id':mid,'setting':'EE floor ON (0.1)',
               'project_sha256':project_hash,'published_pages':{name:sha(directory/name) for name in
                  ('index.html','trends.html','sources.html')},
               'method_count':len(methods),'checked_group_coefficients':checked_groups,
               'checked_annual_values':checked_annual,'settings_and_review_scope_match':True}
        save(model_dir/'results/diagnostics/ee_floor/view_verification.json.gz',entry)
        results.append(entry)
    save(WORK/'qa/view_verification.json.gz',results)
    print(json.dumps([{k:r[k] for k in ('unit_id','method_count','checked_group_coefficients','checked_annual_values')} for r in results],indent=2))

if __name__=='__main__':verify()
