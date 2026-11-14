"""Independent retained-only arithmetic and source-display audit; no adoption."""
import hashlib
import json
import math
import sys
from pathlib import Path

RUN=Path(__file__).resolve().parents[1]
MODEL=RUN.parents[2]
ROOT=next(p for p in MODEL.parents if (p/'tools/project_core').is_dir())
sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book,records,YEARS
from tools.project_core.maps.original_atlas_data import _group_efficiencies
from tools.scientific_helpers.sppr.ppr_scopes import read_scopes
from tools.scientific_helpers.sppr import method_coverage
from unittest.mock import patch

package=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else RUN/'outputs/retained_package_v2'
book=read_book(package/'regional/LME_014.xlsx')
h=json.loads((MODEL/'model_validation/evidence/researcher_review_20261114/adoption_handoff.json').read_text(encoding='utf8'))
manifest=json.loads((package/'model/results/result_manifest.json').read_text(encoding='utf8'))
source=read_scopes(package/'model/sppr_source.xlsx')
approved={(r['method'],r['scope'],r['group_name']):r['sppr'] for r in h['coefficient_records']}
for (method,scope,group),value in approved.items():
    methods,groups=source[scope]
    assert groups[group][methods.index(method)]==value
for methods,groups in source.values():
    if 'new_WithEgestion' in methods:
        assert all(v[methods.index('new_WithEgestion')] is None for v in groups.values())
coeff={(r['taxon'],r['scope'],r['method']):r['sppr'] for r in records(book,'PPR','Taxon SPPR')}
catch={r['taxon']:r for r in records(book,'Catch','Catch') if r['catch_basis']=='landings'}
annual=[r for r in records(book,'PPR','Annual') if r['method'] in {'new_GE','new_TE_EEfix'} and r['catch_basis']=='landings' and r['unidentified']=='method' and r['metric']=='ppr']
checked=0; maximum=0.0
for row in annual:
    assert 'WARN' in row['status'] and row['status'].startswith('provisional:')
    for year in YEARS:
        terms=[r[year]*coeff[t,row['scope'],row['method']] for t,r in catch.items()
               if isinstance(r.get(year),(int,float)) and isinstance(coeff.get((t,row['scope'],row['method'])),(int,float))]
        expected=math.fsum(terms) if terms else None
        if expected is None:assert row[year] is None
        else:
            assert math.isclose(expected,row[year],rel_tol=1e-12,abs_tol=1e-8),(row['method'],row['scope'],year,expected,row[year])
            maximum=max(maximum,abs(expected-row[year]))
        checked+=1
assert checked==420
for row in records(book,'PPR','Annual'):
    if row['method']=='new_WithEgestion' and row['metric'] in {'ppr','covered_catch','min_tC','max_tC'}:
        assert all(row.get(year) is None for year in YEARS)
for row in records(book,'PPR','Taxon PPR inspected year'):
    if row['method']=='new_WithEgestion':assert row.get('sppr') is None and row.get('ppr') is None
ledger=records(book,'Diagnostics','EE floor groups')
display=_group_efficiencies(records(book,'Selected model groups','Groups'),ledger)
assert len(display)==37 and sum(row['applied'] for row in ledger)==8
for row in ledger:
    assert display[row['group_name']]['ee']==row['EE_effective']
    assert display[row['group_name']]['external_mortality_export']==row['external_mortality_export']
assert display['Discards']['external_mortality_export']==0
assert math.isclose(sum(row['external_mortality_export'] for row in ledger),65.52118784337331,rel_tol=1e-14)
flags=manifest['effective_flags']
with patch.object(method_coverage,'_audited_engine',side_effect=AssertionError('Stock engine touched')),patch.object(method_coverage,'_engine',side_effect=AssertionError('Engine touched')):
    for action in (lambda:method_coverage._constructor(flags,MODEL/'model.json'),lambda:method_coverage._load(MODEL/'model.json',{},flags)):
        try:action()
        except ValueError as error:assert 'Unsupported retained runtime initialization' in str(error)
        else:raise AssertionError('Runtime guard did not refuse')
proof={'passed':True,'approved_coefficients_exact':len(approved),'independent_landings_method_annual_checks':checked,'max_annual_absolute_difference':maximum,
       'current_WithE_unavailable':True,'effective_group_display_overlay_verified':37,'affected_floor_groups':8,
       'stock_guard_before_any_engine_access':True,'scientific_solve_performed':False,'new_MC_draws_performed':False,
       'snapshot_sha256':hashlib.sha256((package/'regional/LME_014.xlsx').read_bytes()).hexdigest(),
       'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(RUN/'qa/independent_arithmetic.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8')
print(json.dumps(proof))
