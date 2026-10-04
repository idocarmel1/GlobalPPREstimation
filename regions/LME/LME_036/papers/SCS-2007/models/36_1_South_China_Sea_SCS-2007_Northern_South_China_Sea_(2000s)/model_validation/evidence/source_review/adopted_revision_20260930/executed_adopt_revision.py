from pathlib import Path
import json,sys,copy,math,hashlib
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path.cwd();OUT=ROOT/'outputs/validation_revision_20260930';sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import recalculate,inputs,set_setting,set_result_hash
MODEL='36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)'
EVID=ROOT/'regions/LME_036/validation_reports'/MODEL/'adopted_revision_20260930'
path=ROOT/'regions/LME_036/LME_036.xlsx';identity=json.loads((EVID/'input_identity.json').read_text())
assert sha(path) in [identity['baseline_region_sha256'],identity.get('last_adopted_sha256')],'Unexpected regional workbook modification'
before=json.loads((OUT/'baseline_book.json').read_text(encoding='utf-8'));b=copy.deepcopy(before)
a=json.loads((EVID/'taxon_audit_adopted.json').read_text(encoding='utf-8'));summary=json.loads((EVID/'summary.json').read_text())
evidence=str(EVID.relative_to(ROOT)).replace('\\','/')+'/taxon_audit_adopted.json'
match=[];review=[];ledger=records(b,'PPR','Allocation assumptions')
for r in a:
 t=r['taxon']
 for x in r['adopted_groups'] or [dict(name=None,weight=None)]:
  match.append(dict(model_id=MODEL,taxon=t,group=x['name'],weight=x['weight'],confidence=r['overall_confidence'].lower(),evidence=evidence,explanation=r['reason']))
 review.append(dict(model_id=MODEL,taxon=t,membership_rule=r['membership_rule_plain'],membership_confidence=r['membership_confidence'],allocation_rule=r['weight_rule_plain'],allocation_confidence=r['weight_confidence'],overall_confidence=r['overall_confidence'],membership_evidence=r['membership_source'],allocation_evidence=r['weight_source'],candidate_selection=clean(r['candidate_selection']),allocation_calculation=clean(r['allocation_calculation']),reason=r['reason'],adoption_date='2026-09-30'))
 if r['allocation_calculation']:
  calc=r['allocation_calculation']
  for c,w in zip(r['candidate_selection'],calc['weights']):
   ledger.append(dict(unit_id='LME_036',model_id=MODEL,taxon=t,rule='model_'+calc['field']+'_proxy',confidence='assumed',review_confidence='Medium',weight_evidence=r['weight_source'],definition=c['eligibility'],evidence=evidence,limitations=r['reason'],source_period='2000s',previous_mapping=clean(r['stored_mapping']),years_applied='1950-2019',catch_bases_applied='landings;catch;discards',rule_details='approved catch-first then biomass fallback',source_catch_basis='selected source model group.export',temporal_and_basis_assumption=r['transfer_assumption'],group=c['group'],seq=c['group_id'],source_catch=c['catch'],source_biomass=c['biomass'],weight=w,candidate_definition=c['definition'],assumption_dependent=True))
# Original assumption flags and rows are preserved; only descriptive review confidence is added.
bytax={r['taxon']:r for r in a}
for r in ledger:r['review_confidence']=bytax[r['taxon']]['overall_confidence']
b['PPR']['Matching']=table_dict(match);b['PPR']['Mapping review']=table_dict(review);b['PPR']['Allocation assumptions']=table_dict(ledger)
print('Recalculating dependent taxon coefficients and regional results from preserved group coefficients',flush=True)
recalculate(b,path)
# Model-mapping revision cannot alter independent catch, classic PPR or NPP outputs.
for s in ['Catch','Classic PPR','NPP']:b[s]=copy.deepcopy(before[s])
h,rs=b['PPR–NPP']['Ratios'];b['PPR–NPP']['Ratios']=(h,[r for r in before['PPR–NPP']['Ratios'][1] if not r[0]]+[r for r in rs if r[0]])
key=lambda r:(r['scope'],r['method'],r['catch_basis'],r['unidentified'],r['metric'])
old={key(r):r for r in records(before,'PPR','Annual')};new={key(r):r for r in records(b,'PPR','Annual')}
coef={(r['taxon'],r['scope'],r['method']):r['sppr'] for r in records(b,'PPR','Taxon SPPR')}
assumed={r['taxon'] for r in ledger if r['confidence']=='assumed'}
_,catch,_,_=inputs(b);impacts=[]
for k,r in new.items():
 scope,method,basis,treatment,metric=k
 if metric!='ppr' or treatment!='method':continue
 for i,year in enumerate(YEARS):
  cov=new[scope,method,basis,treatment,'covered_catch'][year];total=new[scope,method,basis,treatment,'catch'][year]
  amount=math.fsum(catch[t,basis][i] for t in assumed if finite(catch[t,basis][i]) and finite(coef.get((t,scope,method)))) if finite(cov) else None
  impacts.append(dict(unit_id='LME_036',model_id=MODEL,scope=scope,method=method,catch_basis=basis,year=year,status=r['status'],total_catch=total,baseline_covered_catch=old[scope,method,basis,treatment,'covered_catch'][year],covered_catch=cov,assumed_covered_catch=amount,covered_without_size_assumptions=cov-amount if finite(cov) else None,baseline_ppr_wet=old[k][year],ppr_wet=r[year]))
b['Diagnostics']['Size allocation impact']=table_dict(impacts)
b['Diagnostics']['Mapping adoption review']=table_dict([dict(unit_id='LME_036',model_id=MODEL,adoption_date='2026-09-30',fallback_taxa=42,newly_mapped_taxa=20,very_low_taxa=20,unresolved_taxa=0,assumption_dependent_taxa=len(assumed),authorization='User authorized coverage-first mapping including Very low broad categories and closest ecological analogues; no new group SPPR or extraction',evidence=evidence)])
# These existing fields are displayed as current; update them rather than leaving stale counts.
for table in ['Size allocation review','Size allocation scope review']:
 rr=records(b,'Diagnostics',table)
 for r in rr:
  if table=='Size allocation review':r['assumed_taxa']=len(assumed);r['reviewed_taxa']=374;r['plan_evidence']=evidence
  else:r['review_status']='Adopted coverage revision';r['reviewed_taxa']=374;r['adopted_taxa']=42;r['evidence_path']=evidence;r['review_date']='2026-09-30';r['workbook_sha256']=identity['baseline_region_sha256']
 b['Diagnostics'][table]=table_dict(rr)
b['Diagnostics']['Size allocation unresolved']=table_dict([dict(taxon=r['taxon'],reason=r['reason'],existing_matching=clean(r['stored_mapping'])) for r in a if r['overall_confidence']=='Unresolved'])
set_setting(b,'source_note','PROVISIONAL: 374 taxa mapped; 177 assumption-dependent taxa, including 20 Very low broad-category or closest-analogue assignments; 0 unresolved taxa. Very low mappings cover 12.5661% of 2019 landings. See PPR / Mapping review and Allocation assumptions. Regional scope and diagnostic limitations remain.')
set_setting(b,'calculation_status','provisional: approved mapping revision; saved group SPPR and original method diagnoses retained; dependent results recalculated')
set_setting(b,'calculation_input_sha256',input_hash(b));set_result_hash(b)
assert b['Selected model groups']==before['Selected model groups']
for s in ['Catch','Classic PPR','NPP']:assert b[s]==before[s]
for table in ['model_health','run_notes','mc_diagnostics']:assert b['Diagnostics'][table]==before['Diagnostics'][table]
assert overview(b)['results_model_sha256']==sha(ROOT/'regions/LME_036'/overview(b)['model_path'])
validate_region(b,path)
comp=[]
for k,r in new.items():
 if k[0]=='all' and k[1] in ['new_GE','new_TE_EEfix'] and k[3]=='method' and k[4] in ['ppr','covered_catch']:
  v=old[k][2019];n=r[2019];div=9 if k[4]=='ppr' else 1
  comp.append(dict(scope=k[0],method=k[1],basis=k[2],metric=k[4],year=2019,before=v/div if finite(v) else None,after=n/div if finite(n) else None,units='t C' if div==9 else 't catch',status=r['status']))
(EVID/'dependent_result_changes.json').write_text(json.dumps(comp,indent=2),encoding='utf-8')
(OUT/'adopted_book.json').write_text(json.dumps(b,ensure_ascii=False),encoding='utf-8')
write_book(path,b)
identity['last_adopted_sha256']=sha(path);(EVID/'input_identity.json').write_text(json.dumps(identity,indent=2),encoding='utf-8')
print('Saved canonical workbook; group SPPR, model health, catch, classic PPR and NPP preserved',flush=True)
print(json.dumps(comp,indent=2))
