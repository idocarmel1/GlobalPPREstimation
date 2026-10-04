"""Candidate-local independent classic PPR/NPP context; never writes regional state."""
from pathlib import Path
import sys, json, csv, hashlib, math

CANDIDATE = Path(__file__).resolve().parents[1]
ROOT = CANDIDATE.parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from workbooks import read_book, records, overview, YEARS

book_path = ROOT / 'regions/LME_027/LME_027.xlsx'
book = read_book(book_path)
out = CANDIDATE / 'calculations'
def save(name, obj):
    (out/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
def csvwrite(name, data):
    with (out/name).open('w', newline='', encoding='utf-8-sig') as f:
        w=csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)

catch = records(book, 'Catch','Catch')
taxa = records(book,'Classic PPR','Taxa')
lookup = {r['taxon']:r for r in taxa}
assert len(lookup)==len(taxa), 'Duplicate classic taxon keys'
assert len({(r['taxon'],r['catch_basis']) for r in catch})==len(catch), 'Duplicate catch keys'
npp = records(book,'NPP','NPP')
save('regional_input_snapshot.json', {
    'source':'../../../LME_027.xlsx',
    'source_sha256':hashlib.sha256(book_path.read_bytes()).hexdigest(),
    'scope':'Read-only source snapshot. Independent calculations do not use candidate GE/TE coefficients.',
    'overview':overview(book),'catch':catch,'classic_taxa':taxa,
    'npp':npp,'npp_provenance':records(book,'NPP','Provenance')})
annual=[]; max_diff=0.; comparisons=[]
saved = records(book,'Classic PPR','Annual')
for basis in sorted({r['catch_basis'] for r in catch}):
    subset=[r for r in catch if r['catch_basis']==basis]
    for treatment in ('method','zero','simple'):
        for year in YEARS:
            vals=[]; cs=[]; missing=[]
            for r in subset:
                c=r.get(year); sppr=lookup.get(r['taxon'],{}).get('sppr')
                if not finite(c): p=None
                elif c==0 or (treatment=='zero' and r.get('unidentified')): p=0.
                elif not finite(sppr): p=None
                else: p=c*sppr/9.
                if p is None: missing.append(r['taxon'])
                else: vals.append(p)
                if finite(c): cs.append(c)
            ppr=math.fsum(vals)
            row={'year':year,'catch_basis':basis,'unidentified':treatment,'method':'simple trophic chain',
                 'catch_t':math.fsum(cs),'known_ppr_tC':ppr,'unknown_contributions':len(missing),
                 'total_ppr_tC':None if missing else ppr,'status':'partial' if missing else 'complete'}
            annual.append(row)
            old=next((r.get(year) for r in saved if r['catch_basis']==basis and r['unidentified']==treatment and r['metric']=='ppr'),None)
            if finite(old):
                diff=abs(ppr-old/9.); max_diff=max(diff,max_diff)
                comparisons.append({'year':year,'basis':basis,'treatment':treatment,'difference_tC':diff,
                                    'within_tolerance':math.isclose(ppr,old/9.,rel_tol=1e-12,abs_tol=1e-6)})
csvwrite('independent_classic_annual.csv',annual)
ratios=[]
for r in annual:
    for source in npp:
        n=source.get(r['year'])
        ratios.append({**{k:r[k] for k in ('year','catch_basis','unidentified')},'npp_method':source['method'],
                       'npp_tC':n,'ppr_tC':r['total_ppr_tC'],
                       'ppr_npp_pct':100*r['total_ppr_tC']/n if finite(n) and n>0 and r['total_ppr_tC'] is not None else None,
                       'status':'available independent classic context' if finite(n) and n>0 and r['total_ppr_tC'] is not None else 'unavailable; no temporal NPP substitution'})
csvwrite('independent_classic_npp_ratios.csv',ratios)
save('independent_calculation_check.json',{'annual_rows':len(annual),'ratio_rows':len(ratios),
     'all_saved_annual_reconciled':all(r['within_tolerance'] for r in comparisons),
     'max_absolute_difference_tC':max_diff,'relative_tolerance':1e-12,'absolute_tolerance_tC':1e-6,
     'comparison_count':len(comparisons),'unknown_annual_count':sum(r['status']=='partial' for r in annual),
     'reference_2019_landings':next(r for r in annual if r['year']==2019 and r['catch_basis']=='landings' and r['unidentified']=='method'),
     'limitations':'Fixed saved taxon coefficients; independent of model mappings. Existing NPP reused read-only with missing years preserved. Candidate model PPR/NPP awaits admissible model coefficients.'})
print(json.dumps({'annual_rows':len(annual),'ratio_rows':len(ratios),'max_difference_tC':max_diff,
                  'all_reconciled':all(r['within_tolerance'] for r in comparisons)}))
