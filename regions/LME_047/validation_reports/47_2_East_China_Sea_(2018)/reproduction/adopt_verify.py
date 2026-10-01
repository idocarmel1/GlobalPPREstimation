from pathlib import Path
import json,sys,math,copy,collections,zipfile,re
import numpy as np
from lxml import etree
ROOT=Path.cwd();Q=Path(__file__).parent;R=ROOT/'regions/LME_047';MID='47_2_East_China_Sea_(2018)';O=R/'validation_reports'/MID
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import recalculate,result_hash,set_setting,set_result_hash
def read(n):return json.loads((O/n).read_text(encoding='utf-8'))
def save(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
b=read_book(R/'LME_047.xlsx');base=copy.deepcopy(b);audit=read('taxon_audit.json');changes=read('mapping_changes.json')
solutions=read('direct_diagnostics/direct_solutions.json');reports=read('direct_diagnostics/direct_reports.json');groupco={(r['group'],r['scope'],r['method']):r['sppr']for r in records(b,'Selected model groups','Group SPPR')};gn={r['seq']:r['group_name']for r in records(b,'Selected model groups','Groups')}
mi=[]
for opt,m in [('GE','new_GE'),('TE','new_TE_EEfix'),('With Egestion','new_WithEgestion')]:
 ss=solutions[opt]['SPPR'];a=np.array(ss['data'],float);negative=[];missing=[];parity=[]
 for i,seq in enumerate(ss['index']):
  for j,src in enumerate(ss['columns']):
   if np.isfinite(a[i,j])and a[i,j]<0:negative.append({'recipient':seq,'source':src,'value':a[i,j]})
   if not np.isfinite(a[i,j]):missing.append({'recipient':seq,'source':src,'nan':ss['nan_mask'][i][j],'positive_infinity':ss['positive_infinity_mask'][i][j],'negative_infinity':ss['negative_infinity_mask'][i][j]})
  for scope in ['all','inner','PP']:
   jj=[j for j,src in enumerate(ss['columns'])if scope=='all'or (scope=='inner'and src!=25)or(scope=='PP'and src==1)]
   value=sum(a[i,j]for j in jj);saved=groupco.get((gn[seq],scope,m));parity.append({'group':gn[seq],'scope':scope,'direct':value,'saved':saved,'matches':saved is not None and math.isclose(value,saved,rel_tol=1e-10,abs_tol=1e-6)})
 mi.append({'method':opt,'recipient_count':len(ss['index']),'source_count':len(ss['columns']),'recipient_axis':ss['index'],'source_axis':ss['columns'],'source_names':[gn[x]for x in ss['columns']],'all_entries_examined':a.size,'negative_entries':negative,'unavailable_entries':missing,'diagnostic':reports[opt],'group_coefficient_parity':parity,'all_saved_scoped_coefficients_match':all(x['matches']for x in parity)})
save('matrix_inspection.json',{'methods':mi,'basis':'All75 entries per method, every source/recipient including unfished25groups; A and L retained with axes/masks in direct_solutions.json. Count alone not substituted for matrix inspection.'});assert all(not x['negative_entries']and x['all_saved_scoped_coefficients_match']for x in mi)
if '--adopt'in sys.argv:
 h=b['PPR']['Matching'][0];b['PPR']['Matching']=(h,[[r.get(k)for k in h]for ch in changes for r in ch['new']]);bounds=[r for r in base['Classic PPR']['Annual'][1]if r[5]in ['min_tC','max_tC']]
 recalculate(b,R/'LME_047.xlsx');b['Classic PPR']['Annual'][1].extend(copy.deepcopy(bounds));set_setting(b,'calculation_status','Reviewed mapping and dependent results refreshed; GE/TE/With Egestion WARN with strict balance true; accepted coefficients/defaults preserved; classic bounds retained.');set_result_hash(b)
 write_book(R/'LME_047.xlsx',b);b=read_book(R/'LME_047.xlsx');validate_region(b,R/'LME_047.xlsx',require_fresh=True);assert result_hash(b)==overview(b)['calculation_result_sha256']
 assert overview(b)['production_eligible']is True
 for s,t in [('Catch','Catch'),('Classic PPR','Taxa'),('Selected model groups','Groups'),('Selected model groups','Group SPPR'),('NPP','NPP'),('NPP','Provenance')]:assert b[s][t]==base[s][t],(s,t)
 assert [r for r in b['Classic PPR']['Annual'][1]if r[5]in ['min_tC','max_tC']]==bounds
 save('mapping_adoption_verification.json',{'workbook_sha256':sha(R/'LME_047.xlsx'),'canonical_sha256':sha(R/overview(b)['model_path']),'input_hash':input_hash(b),'result_hash':result_hash(b),'protected_tables_equal':True,'classic_bounds_equal':True,'production_eligible_preserved':True,'change_keys':len(changes),'matching_rows':len(b['PPR']['Matching'][1]),'shared_integration':'pending root','changes':'Only reviewed taxonomy/membership/allocation/confidence, Matching evidence, dependent TaxonSPPR/Annual/Ratios and freshness/status metadata.'})
# Independent expected arithmetic for every available/unavailable taxon/method/scope/basis/year/treatment.
taxa={r['taxon']for r in records(b,'Catch','Catch')};catch={(r['taxon'],r['catch_basis']):r for r in records(b,'Catch','Catch')};un={r['taxon']:r['unidentified']for r in records(b,'Catch','Catch')};simple={r['taxon']:r['sppr']for r in records(b,'Classic PPR','Taxa')};co={(r['taxon'],r['scope'],r['method']):r['sppr']for r in records(b,'PPR','Taxon SPPR')}
checks=0;maxgap=0;errors=[]
for sheet in ['Classic PPR','PPR']:
 for r in records(b,sheet,'Annual'):
  if r['metric']not in ['ppr','catch','covered_catch']:continue
  for y in YEARS:
   parts=[];ct=[]
   for t in taxa:
    c=catch[t,r['catch_basis']][y];v=simple.get(t)if sheet=='Classic PPR'else co.get((t,r['scope'],r['method']))
    if un[t]and r['unidentified']=='zero':v=0
    if un[t]and r['unidentified']=='simple':v=simple.get(t)
    ct.append(c)
    if finite(c)and finite(v):parts.append((c,v))
   expected=math.fsum(ct)if r['metric']=='catch'else (math.fsum(c*(v if r['metric']=='ppr'else 1)for c,v in parts)if parts and numeric_status(r['status'])else None)
   actual=r[y];checks+=1
   if expected is None:
    if actual is not None:errors.append([sheet,r['scope'],r['method'],r['metric'],y,actual,expected])
   elif actual is None or not math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-6):errors.append([sheet,r['scope'],r['method'],r['metric'],y,actual,expected])
   else:maxgap=max(maxgap,abs(actual-expected))
assert not errors,errors[:5]
ratio_checks=0;den={r['method']:r for r in records(b,'NPP','NPP')};annual={tuple(r[k]or''for k in ['model_id','scope','method','catch_basis','unidentified']):r for s in ['Classic PPR','PPR']for r in records(b,s,'Annual')if r['metric']=='ppr'}
for r in records(b,'PPR–NPP','Ratios'):
 pp=annual[tuple(r[k]or''for k in ['model_id','scope','method','catch_basis','unidentified'])]
 for y in YEARS:
  p=pp[y];n=den[r['npp_method']][y];e=100*p/9/n if finite(p)and finite(n)and n>0 else None;a=r[y];ratio_checks+=1;assert a is None if e is None else math.isclose(a,e,rel_tol=1e-12,abs_tol=1e-8)
ex=[]
for scope in ['all','inner','PP']:
 for method in ['new_GE','new_TE_EEfix','new_WithEgestion']:
  rows=[]
  for rr in audit:
   c=rr['catch_tonnes'];v=co.get((rr['taxon'],scope,method));p=c*v/9 if finite(v)else (0 if c==0 else None);rows.append({'taxon':rr['taxon'],'catch_t':c,'sppr':v,'ppr_tC':p,'confidence':rr['overall_confidence']})
  total=math.fsum(r['ppr_tC']or 0 for r in rows);top=sorted(rows,key=lambda r:-(r['ppr_tC']or 0))[:12];cc=[]
  for conf in ['High','Medium','Low','Very low','Unresolved']:cc.append({'label':conf,'ppr_tC':math.fsum(r['ppr_tC']or 0 for r in rows if r['confidence']==conf),'ppr_percentage':100*math.fsum(r['ppr_tC']or 0 for r in rows if r['confidence']==conf)/total})
  ex.append({'method':method,'scope':scope,'total_tC':total,'top_contributors':top,'confidence_contribution':cc})
save('method_contribution_exposure.json',{'reference_year':2019,'basis':'landings','unidentified':'method','methods':ex,'limit':'Method-specific shares are separate from classic-PPR confidence tables. Diagnostic model footprint0 uses missing/default group catch; SAU catch produces these positive regional sums. TE EEfix Sharks22/Marine mammals23 remain0, not missing.'})
save('arithmetic_verification.json',{'annual_value_checks':checks,'ratio_checks':ratio_checks,'maximum_absolute_gap':maxgap,'errors':errors,'scope_status_count':dict(collections.Counter(r['status']for r in records(b,'PPR','Annual')if r['metric']=='ppr')),'zero_positive_unknown_conventions':True})
print('ARITHMETIC',checks,ratio_checks,overview(b)['calculation_result_sha256'])

