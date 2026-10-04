"""Independent file-based annual/2019/carbon/NPP reconciliation; no solver."""
from pathlib import Path
import csv,gzip,hashlib,json,math
HERE=Path(__file__).resolve().parent
def read_csv(p):
    with p.open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))
def number(v):
    try: return float(v)
    except (TypeError,ValueError): return None
def key(r): return tuple(r[x] for x in ('year','method','scope','catch_basis','unidentified_treatment'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((HERE/'candidate_calculation_manifest.json').read_text(encoding='utf-8'))
mapping_path=(HERE/manifest['mapping_path']).resolve()
mapping_hash_matches=sha(mapping_path)==manifest['mapping_sha256']
if not mapping_hash_matches: raise ValueError('Candidate mapping changed after arithmetic')
annual=read_csv(HERE/'candidate_annual_totals.csv')
ref=read_csv(HERE/'candidate_reference_2019_taxa.csv')
ratios=read_csv(HERE/'candidate_annual_npp_ratios.csv')
assert len(annual)==5670 and len(ref)==17658 and len(ratios)==34020
assert len(set(key(r) for r in annual))==len(annual)
by_annual={key(r):r for r in annual}
ref_groups={}
for r in ref: ref_groups.setdefault(key(r),[]).append(r)
errors=[];zero_unknown=0
for r in ref:
    c,s,pw,pc=[number(r[f]) for f in ('catch_t_wet','coefficient_wet','ppr_t_wet_equivalent','ppr_tC')]
    if pw is not None and not math.isclose(pc,pw/9,rel_tol=1e-12,abs_tol=1e-8): errors.append(('carbon',r['taxon'],key(r)))
    if r['contribution_available']=='True' and c and s is not None:
        if not math.isclose(pw,c*s,rel_tol=1e-12,abs_tol=1e-8): errors.append(('product',r['taxon'],key(r)))
    if c==0 and s is None and r['contribution_available']=='True':
        assert pc==0 and r['coefficient_available']=='False';zero_unknown+=1
    assert r['production_eligible']=='False'
for k,rs in ref_groups.items():
    actual=number(by_annual[k]['ppr_tC'])
    contributions=[number(r['ppr_tC']) for r in rs]
    if actual is not None:
        assert all(v is not None for v in contributions)
        if not math.isclose(math.fsum(contributions),actual,rel_tol=1e-12,abs_tol=1e-7): errors.append(('reference_sum',k))
for r in annual:
    assert r['production_eligible']=='False'
    if r['scope']!='all' and r['unidentified_treatment']=='simple': assert number(r['ppr_tC']) is None
for r in ratios:
    n,p,v=[number(r[f]) for f in ('npp_tC_year','ppr_tC_year','ppr_npp_ratio')]
    if n is None or p is None:
        assert v is None
    elif not math.isclose(v,p/n,rel_tol=1e-12,abs_tol=1e-12): errors.append(('ratio',key(r),r['npp_method']))
    assert r['production_eligible']=='False'
count=0;negative_rows=0;available_rows=0
with gzip.open(HERE/'candidate_taxon_annual.csv.gz','rt',encoding='utf-8',newline='') as f:
    for r in csv.DictReader(f):
        count+=1
        assert r['production_eligible']=='False'
        pc=number(r['ppr_tC'])
        if pc is not None:
            available_rows+=1
            if pc<0: negative_rows+=1
assert count==manifest['taxon_annual_rows']
result={'schema_version':1,'status':'PASS' if not errors else 'FAIL','errors':errors,
        'mapping_hash_matches':mapping_hash_matches,'annual_rows':len(annual),'reference_taxon_rows':len(ref),
        'ratio_rows':len(ratios),'taxon_annual_rows_reopened':count,
        'available_taxon_annual_contributions':available_rows,'negative_taxon_annual_rows_retained':negative_rows,
        'zero_unknown_coefficient_reference_contributions':zero_unknown,
        'all_rows_production_ineligible':True,'all_reference_taxon_sums_reconcile':not errors,
        'division_by_nine_exactly_once':True,'missing_annual_npp_remains_unknown':True,
        'no_new_scientific_execution':True}
(HERE/'candidate_arithmetic_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
assert not errors,errors
print(json.dumps(result))
