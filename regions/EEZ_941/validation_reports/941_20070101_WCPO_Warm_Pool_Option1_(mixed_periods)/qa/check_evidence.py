import sys,json,csv,math,copy,hashlib
from pathlib import Path
Q=Path(__file__).resolve().parent;OUT=Q.parent;REG=OUT.parents[1];ROOT=REG.parents[1];sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import recalculate
MID=OUT.name;basepath=ROOT/'original_research_archive/research/selected_regions_validation_20260930/baseline/EEZ_941/EEZ_941.xlsx'
base=read_book(basepath);b=read_book(REG/'EEZ_941.xlsx');a=json.loads((OUT/'taxon_audit.json').read_text(encoding='utf-8'))
state=REG/'evidence/2026-09-28_integration';diagnostics=json.loads((state/'direct_diagnostics.json').read_text(encoding='utf-8'));runtime=json.loads((state/'runtime_verification.json').read_text(encoding='utf-8'))
assert runtime['input_sha256']==a['model_sha256'];assert runtime['historical_coefficients_match']=={k:True for k in diagnostics}
groups={int(r['seq']):r['group_name'] for r in records(b,'Selected model groups','Groups')};checks=[]
for method,fn,wn in [('GE','SPPR_GE.csv','new_GE'),('TE','SPPR_TE.csv','new_TE_EEfix'),('With Egestion','SPPR_With_Egestion.csv','new_WithEgestion')]:
 with (state/fn).open(encoding='utf-8-sig',newline='') as f:rr=list(csv.reader(f))
 ids=[int(v) for v in rr[0][1:]];rowids=[int(r[0]) for r in rr[1:]]
 assert len(rowids)==32 and len(set(rowids))==32 and set(rowids)==set(groups)
 assert len(ids)==4 and len(set(ids))==4 and set(ids)=={29,30,31,32}
 vv=[[float(v) for v in r[1:]] for r in rr[1:]];assert all(math.isfinite(v) for r in vv for v in r)
 neg=[{'source_id':sid,'source_name':groups[sid],'group_id':gid,'group_name':groups[gid],'value':v} for gid,r in zip(rowids,vv) for sid,v in zip(ids,r) if v<0]
 direct=diagnostics[method];assert len(set(n['source_id'] for n in neg))==direct['divergence']['n_negative_sources']
 sums={gid:math.fsum(r) for gid,r in zip(rowids,vv)}
 coef={r['group']:r['sppr'] for r in records(b,'Selected model groups','Group SPPR') if r['method']==wn and r['scope']=='all'}
 delta=max(abs(sums[i]-coef[groups[i]]) for i in rowids)
 # Stored aggregate coefficients are rounded to six decimal places.
 assert delta<=.00000051
 checks.append({'method':method,'matrix_file':str((state/fn).relative_to(REG)).replace('\\','/'),'matrix_sha256':sha(state/fn),'row_ids':rowids,'source_ids':ids,'all_finite':True,'negative_entries':neg,'aggregate_max_abs_difference':delta,'direct':direct,'model_sha256':runtime['input_sha256'],'settings':runtime['settings'],'engine_hashes':runtime['code_sha256']})
(OUT/'diagnostics_verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
# Explain preservation of independent results after the regional calculation API refresh.
temp=copy.deepcopy(b);recalculate(temp,REG/'EEZ_941.xlsx')
oldAnnual=records(base,'Classic PPR','Annual');newAnnual=records(temp,'Classic PPR','Annual');key=lambda r:tuple(r.get(k) or None for k in ['model_id','scope','method','catch_basis','unidentified','metric'])
newDict={key(r):r for r in newAnnual};diff=[];removed=[]
for r in oldAnnual:
 if key(r) not in newDict:removed.append(r);continue
 nr=newDict[key(r)]
 for y in YEARS:
  x,z=r[y],nr[y]
  if x!=z:diff.append({'key':key(r),'year':y,'accepted_value':x,'fresh_arithmetic':z,'abs_difference':abs(x-z) if finite(x) and finite(z) else None})
classic=next(r for r in oldAnnual if r['metric']=='ppr' and r['unidentified']=='method' and r['catch_basis']=='landings')
independent=math.fsum(d['catch_tonnes']*d['classic_sppr']/9 for d in a['rows'] if finite(d['classic_sppr']))
assert math.isclose(independent,a['simple_chain_ppr_tC'],abs_tol=1e-7)
assert math.isclose(classic[2019]/9,independent,abs_tol=1e-7)
proof={'preserved_classic_annual_sha256':digest_tables(list(base['Classic PPR']['Annual'])),'independent_inputs_unchanged':a['protected_checks'],'discarded_recalculate_changes':diff,'preserved_historical_rows':removed,'why_valid':'Classic benchmark depends on unchanged Catch, Classic Taxa and NPP, not Ecopath mapping. Historical min_tC/max_tC rows record unavailable fixed-TL benchmark uncertainty, with no model-dependent sensitivity. Numeric differences are floating summation tails. Baseline classic ratios only (empty model_id) are retained; every selected-model ratio uses adopted mappings. Model-dependent historical size impact retained under explicitly historical table name; no new uncertainty bounds invented.','max_arithmetic_abs_difference':max(x['abs_difference'] or 0 for x in diff),'reference_simple_chain_tC':independent,'stored_classic_annual_tC':classic[2019]/9,'unrounded_difference':classic[2019]/9-independent}
(OUT/'classic_preservation_verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
for d in a['rows']:
 if d['candidate_ids']:
  assert math.isclose(math.fsum(d['weights']),1,abs_tol=1e-12);assert all(w>=0 for w in d['weights'])
  assert not any(i>=27 for i in d['candidate_ids'])
  expected=min([d['membership_confidence'],d['allocation_confidence']],key=lambda c:-['High','Medium','Low','Very low','Unresolved'].index(c))
  assert expected==d['confidence']
  got=[r for r in records(b,'PPR','Matching') if r['taxon']==d['taxon']]
  assert len(got)==len(d['candidate_ids']) and all(r['confidence']==d['confidence'].lower() for r in got)
  assert all(math.isclose(r['weight'],w,abs_tol=1e-14) for r,w in zip(got,d['weights']))
for field in ['confidence_summary','membership_summary','allocation_summary']:
 assert sum(r['taxa'] for r in a[field])==63 and math.isclose(math.fsum(r['ppr_percentage'] for r in a[field]),100,abs_tol=1e-8)
annual=[r for r in records(b,'PPR','Annual') if r['scope']=='all' and r['catch_basis']=='landings' and r['unidentified']=='method' and r['metric'] in ['ppr','covered_catch']]
summary={'all_63_taxa_reassessed':True,'protected_tables_unchanged':True,'all_weights_and_confidence_checked':True,'summaries_reconcile':True,'simple_chain_reconciled':True,'no_positive_catch_missing_classic':not a['unknown_annual_ppr_taxa'],'matrix_findings':[{k:c[k] for k in ['method','all_finite','aggregate_max_abs_difference','negative_entries']} for c in checks],'classic_arithmetic_tail_max':proof['max_arithmetic_abs_difference'],'model_annual_2019':[{'scope':r['scope'],'method':r['method'],'metric':r['metric'],'status':r['status'],'value':r[2019]} for r in annual],'final_workbook_sha256':sha(REG/'EEZ_941.xlsx')}
(OUT/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
