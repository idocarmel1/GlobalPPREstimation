"""Candidate-only arithmetic from the authoritative regional reader snapshot.
No selected Ecopath mapping/coefficient is read or substituted.
"""
from pathlib import Path
import json, math, csv, collections, hashlib
C=Path(__file__).resolve().parents[1]
CTX=C/'work/regional_context.json'
ctx=json.loads(CTX.read_text(encoding='utf-8'))
out=C/'calculations'
def dump(name,x): (out/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def finite(v): return isinstance(v,(int,float)) and math.isfinite(v)
classic={r['taxon']:r for r in ctx['classic']}
assert len(classic)==len(ctx['classic'])
keys=[(r['taxon'],r['catch_basis']) for r in ctx['catch']]
assert len(set(keys))==len(keys)
years=sorted(k for k in ctx['catch'][0] if k.isdigit())
reference_year=str(ctx['overview']['taxon_detail_year'])
reference_basis=ctx['overview']['catch_basis']
ref=[]
for r in ctx['catch']:
 if r['catch_basis']!=reference_basis: continue
 coeff=classic.get(r['taxon'],{}); catch=r.get(reference_year); sppr=coeff.get('sppr')
 ppr=0.0 if catch==0 else catch*sppr/9 if finite(catch) and finite(sppr) else None
 ref.append({'taxon':r['taxon'],'common_name':r['common_name'],'functional_group':r['functional_group'],'commercial_group':r['commercial_group'],'unidentified':r['unidentified'],'year':int(reference_year),'basis':reference_basis,'catch_t':catch,'tl':coeff.get('tl'),'classic_sppr_wet_weight':sppr,'simple_ppr_tC':ppr,'tl_source':coeff.get('tl_source'),'classic_match_method':coeff.get('match_method'),'missing_classic_coefficient':not finite(sppr),'missing_catch':not finite(catch),'missing_annual_ppr':ppr is None})
dump('reference_inputs.json',ref)
annual=[]
for basis in sorted(set(r['catch_basis'] for r in ctx['catch'])):
 rows=[r for r in ctx['catch'] if r['catch_basis']==basis]
 for y in years:
  missing_catch=[]; missing_positive_coeff=[]; missing_zero_coeff=[]; contributions=[]
  for r in rows:
   v=r.get(y); co=classic.get(r['taxon'],{}).get('sppr')
   if not finite(v): missing_catch.append(r['taxon']); continue
   assert v>=0
   if v==0:
    contributions.append(0.0)
    if not finite(co): missing_zero_coeff.append(r['taxon'])
   elif not finite(co): missing_positive_coeff.append(r['taxon'])
   else: contributions.append(v*co/9)
  ppr=math.fsum(contributions); catch_sum=math.fsum(r[y] for r in rows if finite(r.get(y)))
  complete=not missing_catch and not missing_positive_coeff
  a={'year':int(y),'basis':basis,'catch_t':catch_sum,'taxa':len(rows),'simple_ppr_known_tC':ppr,'simple_ppr_total_tC':ppr if complete else None,'status':'complete' if complete else 'known subtotal; unknown contributions remain','missing_catch_taxa':missing_catch,'positive_catch_missing_coefficient_taxa':missing_positive_coeff,'zero_catch_missing_coefficient_taxa':missing_zero_coeff,'model_GE_ppr_tC':None,'model_TE_ppr_tC':None,'model_With_Egestion_ppr_tC':None,'model_reason':'BLOCKED before loading: preferred thesis supplies quantitative diet, but Table6.5 group20 Epinephelus aeneus and AnnexII.A group20 Hemichromis fasciatus identify different fish families; no source-supported identity reconciliation or model SPPR coefficient exists.'}
  saved=[r for r in ctx['classic_annual'] if r.get('scope')=='all' and r.get('method')=='simple trophic chain' and r.get('catch_basis')==basis and r.get('unidentified')=='method' and r.get('metric')=='ppr']
  if len(saved)==1 and finite(saved[0].get(y)):
   a['saved_classic_annual_wet_weight']=saved[0][y]
   a['difference_known_tC_minus_saved_divided_by_9']=ppr-saved[0][y]/9
  a['npp_ratios']={}
  for n in ctx['npp']:
   nv=n.get(y)
   a['npp_ratios'][n['method']]={'npp_tC':nv,'known_ppr_percent_npp':100*ppr/nv if finite(nv) and nv>0 else None,'total_ppr_percent_npp':100*ppr/nv if complete and finite(nv) and nv>0 else None}
  annual.append(a)
dump('annual_independent.json',annual)
with (out/'annual_independent.csv').open('w',encoding='utf-8-sig',newline='') as f:
 fields=['year','basis','taxa','catch_t','simple_ppr_known_tC','simple_ppr_total_tC','status']
 w=csv.DictWriter(f,fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in annual)
reference=[a for a in annual if a['basis']==reference_basis and a['year']==int(reference_year)][0]
verification={'context_sha256':hashlib.sha256(CTX.read_bytes()).hexdigest(),'reference':reference,'years':len(years),'bases':sorted(set(r['catch_basis'] for r in ctx['catch'])),'annual_rows':len(annual),'reference_taxa':len(ref),'saved_coefficient_taxa':len(classic),'reference_zero_catch_missing_coefficient_taxa':[r['taxon'] for r in ref if r['catch_t']==0 and r['missing_classic_coefficient']],'reference_positive_catch_missing_coefficient_taxa':[r['taxon'] for r in ref if finite(r['catch_t']) and r['catch_t']>0 and r['missing_classic_coefficient']],'carbon_conversion':'The saved Classic PPR / Taxa sppr is wet-weight equivalent. Each annual contribution is catch_t * sppr / 9, once; no group TL or model SPPR is used.','formula_crosscheck_max_coefficient_difference':max(abs(r['sppr']-0.1**(1-r['tl'])) for r in ctx['classic'] if finite(r.get('sppr')) and finite(r.get('tl'))),'max_abs_saved_annual_difference_tC':max(abs(a.get('difference_known_tC_minus_saved_divided_by_9',0)) for a in annual),'active_workbook_written':False,'provenance':'Authoritative tools/workbooks.py read_book / records snapshot in work/regional_context.json; Overview reference year/basis and saved classic evidence are preserved.'}
dump('independent_arithmetic_verification.json',verification)
print(json.dumps({k:verification[k] for k in ['reference_taxa','saved_coefficient_taxa','annual_rows','max_abs_saved_annual_difference_tC','formula_crosscheck_max_coefficient_difference']},indent=2))
print(json.dumps(reference,ensure_ascii=False,indent=2))
