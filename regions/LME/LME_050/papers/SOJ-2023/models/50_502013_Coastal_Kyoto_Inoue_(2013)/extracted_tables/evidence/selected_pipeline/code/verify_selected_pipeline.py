from pathlib import Path
import sys,json,math,shutil
import numpy as np
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_050';MID='50_502013_Coastal_Kyoto_Inoue_(2013)';DEST=REG/'models'/MID;EV=DEST/'selected_pipeline'
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import result_hash
P=REG/'LME_050.xlsx';b=read_book(P);o=validate_region(b,P);assert o['calculation_result_sha256']==result_hash(b)
assert o['selected_model_id']==MID and o['production_eligible'] is False
old=read_book(REG/'models/previous_results/LME_050_before_user_2013_selection_b4fdf13039c1.xlsx')
for s in ['Catch','NPP']:assert b[s]==old[s]
assert b['Classic PPR']['Taxa']==old['Classic PPR']['Taxa']
catch=records(b,'Catch','Catch');maps=records(b,'PPR','Matching');groups=records(b,'Selected model groups','Groups');sp=records(b,'Selected model groups','Group SPPR');tx=records(b,'PPR','Taxon SPPR');annual=records(b,'PPR','Annual')
taxa={r['taxon'] for r in catch};assert {r['taxon'] for r in maps}==taxa and len(maps)==len(taxa)
group_types={r['group_name']:r['trophic_info'] for r in groups}
mapping={r['taxon']:r['group'] for r in maps if r['group']}
assert len(mapping)==19 and all(r['weight']==1 and group_types[r['group']]=='Regular' for r in maps if r['group'])
coeff={(r['group'],r['scope'],r['method']):r['sppr'] for r in sp}
taxcoeff={(r['taxon'],r['scope'],r['method']):r['sppr'] for r in tx}
assert len(sp)==41*3*3 and all(finite(r['sppr']) and r['sppr']>=0 for r in sp)
assert {r['method'] for r in sp}=={'new_GE','new_TE_EEfix','new_WithEgestion'}
for r in tx:
 expected=round(coeff[mapping[r['taxon']],r['scope'],r['method']],6) if r['taxon'] in mapping else None
 assert (r['sppr']==expected) or (finite(r['sppr']) and math.isclose(r['sppr'],expected,abs_tol=1e-12)),r
checks=0;maxerr=0.;max_source_rounding_delta=0.
for r in annual:
 if r['metric'] not in ['ppr','covered_catch'] or r['unidentified']!='method':continue
 rr=[x for x in catch if x['catch_basis']==r['catch_basis'] and x['taxon'] in mapping]
 for y in YEARS:
  values=[];unrounded=[]
  for cr in rr:
   if not finite(cr.get(y)):continue
   c=taxcoeff[cr['taxon'],r['scope'],r['method']]
   values.append(cr[y]*c if r['metric']=='ppr' else cr[y])
   unrounded.append(cr[y]*coeff[mapping[cr['taxon']],r['scope'],r['method']] if r['metric']=='ppr' else cr[y])
  expected=float(np.sum(np.asarray(values,dtype=float))) if values else None
  assert r['status']=='ok' and math.isclose(r[y],expected,rel_tol=1e-12,abs_tol=1e-7),(r['method'],y,r[y],expected)
  checks+=1;maxerr=max(maxerr,abs(r[y]-expected));max_source_rounding_delta=max(max_source_rounding_delta,abs(r[y]-float(np.sum(unrounded))))
npp={r['method']:r for r in records(b,'NPP','NPP')};ar={(r['model_id'],r['scope'],r['method'],r['catch_basis'],r['unidentified']):r for r in annual if r['metric']=='ppr'};ratio_checks=0;unavailable=0
for r in records(b,'PPR–NPP','Ratios'):
 if r['model_id']!=MID:continue
 src=ar[r['model_id'],r['scope'],r['method'],r['catch_basis'],r['unidentified']]
 for y in YEARS:
  num=src[y];den=npp[r['npp_method']][y]
  if finite(num) and finite(den) and den>0:assert math.isclose(r[y],100*num/9/den,rel_tol=1e-12,abs_tol=1e-12);ratio_checks+=1
  else:assert r[y] is None;unavailable+=1
for basis in ['landings','catch','discards']:
 assert len([r for r in catch if r['catch_basis']==basis])==253
cc={(r['taxon'],r['catch_basis']):r for r in catch};catch_error=0.
for t in taxa:
 for y in YEARS:
  vals=[cc[t,k][y] for k in ['catch','landings','discards']]
  if all(finite(x) for x in vals):catch_error=max(catch_error,abs(vals[0]-vals[1]-vals[2]));assert math.isclose(vals[0],vals[1]+vals[2],rel_tol=1e-9,abs_tol=1e-6)
for name in ['record_user_selection.py','run_selected_sppr.py','complete_supported_pipeline.py','verify_selected_pipeline.py']:shutil.copy2(Path(__file__).parent/name,EV/'code'/name)
for name in ['regional.py','workbooks.py','run_region.py']:shutil.copy2(ROOT/'tools'/name,EV/'code'/name)
out={'status':'PASS','selection':MID,'reason':'User chose2013because newer;1985good comparison; notnumericalsuperiority','source_sha256':sha(DEST/'model.json'),'regional_sha256':sha(P),'all_groups':len(groups),'SPPR_rows':len(sp),'taxa':len(taxa),'resolved':len(mapping),'unresolved':len(taxa)-len(mapping),'annual_mapped_subset_checks':checks,'max_independent_annual_absolute_error':maxerr,'maximum_annual_difference_due_to_current_regional_six_decimal_taxon_coefficient_rounding':max_source_rounding_delta,'ratio_checks_with_single_carbon_division':ratio_checks,'unsupported_ratio_cells_remain_blank':unavailable,'max_C_minus_L_minus_D_error':catch_error,'Catch_NPP_ClassicTaxa_unchanged':True,'source_admission':'Still unresolved; numerical checks do not validate year-specific source reconstruction','production_eligible':False,'central_updates':'Not performed by this run'}
(EV/'VALIDATION.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
