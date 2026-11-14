from pathlib import Path
import json, hashlib, sys, math, re, collections
import openpyxl
ROOT=Path.cwd(); MID='CAL-2016_California_Current_2000-2014'
M=ROOT/'regions/LME/LME_003/papers/CAL-2016/models'/MID; V=M/'model_validation'; E=V/'evidence/source_review'; W=V/'work/2026-11-14_210000_validation'; O=V/'evidence/mapping'
O.mkdir(exist_ok=True); (W/'qa').mkdir(exist_ok=True); (W/'outputs').mkdir(exist_ok=True)
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records, overview
regional=ROOT/'regions/LME/LME_003/LME_003.xlsx'; book=read_book(regional,sheets=['Overview','Catch','Classic PPR','Selected model groups','PPR'])
settings=overview(book); year=int(settings['taxon_detail_year']); basis=settings['catch_basis']
assert settings['selected_model_id']==MID and year==2019 and basis=='landings'
catch=records(book,'Catch','Catch'); catch=[r for r in catch if r['catch_basis']==basis]; assert len({r['taxon'] for r in catch})==len(catch)==349
catch={r['taxon']:r for r in catch}; classic={r['taxon']:r for r in records(book,'Classic PPR','Taxa')}
groups={r['group_name']:r for r in records(book,'Selected model groups','Groups')}; byid={int(r['group_seq']):r for r in groups.values()}
matching=collections.defaultdict(list)
for r in records(book,'PPR','Matching'):
 if r['model_id']==MID: matching[r['taxon']].append(r)
audit=read(E/'taxon_audit.json'); prior=read(E/'coverage_summary.json'); sourcecatch=read(E/'source_catch_provenance.json')
wb=openpyxl.load_workbook(V/'taxon_mapping.xlsx',data_only=False); ws=wb['Taxon mapping']; appendix={ws.cell(n,1).value:[ws.cell(n,c).value for c in range(1,8)] for n in range(8,ws.max_row+1)}
assert set(appendix)==set(catch)==set(matching)=={r['taxon'] for r in audit['rows']}
levels=['High','Medium','Low','Very low','Unresolved']; errors=[]; detail=[]; confidence_discrepancies=[]
for a in audit['rows']:
 t=a['taxon']; cr=classic.get(t,{}); c=catch[t][year]; sp=cr.get('sppr'); p=0.0 if c==0 else c*sp/9 if c is not None and sp is not None else None
 ms=matching[t]; expected={x['group']:float(x['weight']) for x in a['assignments']}; actual={x['group']:float(x['weight']) for x in ms}
 assert len(actual)==len(ms) and expected.keys()==actual.keys(),(t,'group mismatch')
 assert all(math.isclose(expected[g],actual[g],abs_tol=1e-12,rel_tol=1e-12) for g in actual),(t,'weights')
 assert math.isclose(sum(actual.values()),1,abs_tol=1e-10),(t,'weight sum')
 assert all(g in groups for g in actual)
 assert all(i in byid for i in a['candidate_ids'])
 assert a['membership_reason'] and a['allocation_reason'] and a['source_locators']
 conf=max([a['membership_confidence'],a['allocation_confidence']],key=levels.index); assert conf==a['overall_confidence']
 stored=sorted({str(r['confidence']) for r in ms})
 if any(s.lower().replace(' ','')!=conf.lower().replace(' ','') for s in stored): confidence_discrepancies.append({'taxon':t,'stored':stored,'review':conf})
 for k,val in [('catch_tonnes',c),('tl',cr.get('tl')),('classic_sppr',sp),('simple_chain_ppr_tC',p)]:
  old=a.get(k)
  assert (old is None and val is None) or (isinstance(old,(int,float)) and isinstance(val,(int,float)) and math.isclose(old,val,rel_tol=1e-12,abs_tol=1e-9)),(t,k,old,val)
 ar=appendix[t]
 assert ar[1]==(cr.get('tl') if cr.get('tl') is not None else '?') and ar[4]==a['mapping_display'] and ar[5]==conf,(t,'appendix label')
 assert math.isclose(ar[2],c,rel_tol=1e-12,abs_tol=1e-9) and math.isclose(ar[3],p,rel_tol=1e-12,abs_tol=1e-9),(t,'appendix arithmetic')
 detail.append({'taxon':t,'reference_year':year,'catch_basis':basis,'catch_tonnes':c,'tl':cr.get('tl'),'classic_sppr':sp,'simple_chain_ppr_tC':p,'tl_source':cr.get('tl_source'),'adopted_assignments':a['assignments'],'candidate_ids':a['candidate_ids'],'zero_weight_candidates':a['zero_weight_candidates'],'membership_rule':a['membership_rule'],'membership_confidence':a['membership_confidence'],'membership_reason':a['membership_reason'],'allocation_rule':a['allocation_rule'],'allocation_confidence':a['allocation_confidence'],'allocation_reason':a['allocation_reason'],'overall_confidence':conf,'stored_confidence':stored,'source_locators':a['source_locators'],'review_outcome':'retained: existing evidence matches current groups, weights, catch and classic coefficients','reason':ar[6]})
detail.sort(key=lambda x:(x['simple_chain_ppr_tC'] is None,-(x['simple_chain_ppr_tC'] or 0),x['taxon']))
assert [r['taxon'] for r in detail]==list(appendix),'full precision order'
ct=math.fsum(r['catch_tonnes'] for r in detail); pt=math.fsum(r['simple_chain_ppr_tC'] for r in detail if r['simple_chain_ppr_tC'] is not None)
summary={'unit_id':'LME_003','model_id':MID,'reference_year':year,'catch_basis':basis,'catch_basis_description':'landings only; excludes discards','method':'Independent simple trophic chain','transfer_efficiency':settings['transfer_efficiency'],'carbon_divisor':9,'source_group_count':len([g for g in groups.values() if g['group_name']!='diet_import']),'computational_import_count':len([g for g in groups.values() if g['group_name']=='diet_import']),'total_taxa':len(detail),'total_catch_tonnes':ct,'simple_chain_ppr_tC':pt,'missing_tl_taxa':[r['taxon'] for r in detail if r['tl'] is None],'missing_coefficient_taxa':[r['taxon'] for r in detail if r['classic_sppr'] is None],'unknown_annual_ppr_taxa':[r['taxon'] for r in detail if r['simple_chain_ppr_tC'] is None],'zero_catch_taxa_count':sum(r['catch_tonnes']==0 for r in detail),'categories':{},'membership_rules':[],'allocation_rules':[],'confidence_discrepancies':confidence_discrepancies}
for q in levels:
 rr=[r for r in detail if r['overall_confidence']==q]; qc=math.fsum(r['catch_tonnes'] for r in rr); qp=math.fsum(r['simple_chain_ppr_tC'] for r in rr if r['simple_chain_ppr_tC'] is not None)
 summary['categories'][q]={'taxa_count':len(rr),'catch_tonnes':qc,'catch_percent':100*qc/ct,'simple_chain_ppr_tC':qp,'ppr_percent':100*qp/pt}
descriptions={'M1':'Explicit assignment in the source group definition','M2':'Verified synonym of a documented source member','M3':'Unambiguous fit to the documented group definition','M4':'Extension from source-listed representatives','M5':'Supported ecological assignment requiring interpretation','M6':'Partial or conflicting ecological fit','M9':'Assumed eligible group set from regional taxonomy and source definitions','M10':'Broad reporting-category composition approximated by compatible model groups','M11':'Closest represented ecological or taxonomic analogue with material mismatch','W1':'No split required: the full taxon catch is assigned to one group','W4':'Source-model total Yield proportions used as fixed composition proxies across years and catch bases; source zero catches retained','W5':'Identified regional catches pooled across 1950–2019 supply a transferred composition proxy; donor and target reporting populations are not established as equivalent'}
for component in ['membership','allocation']:
 for rule,conf in sorted({(r[component+'_rule'],r[component+'_confidence']) for r in detail}):
  rr=[r for r in detail if r[component+'_rule']==rule and r[component+'_confidence']==conf]; pp=math.fsum(r['simple_chain_ppr_tC'] for r in rr if r['simple_chain_ppr_tC'] is not None)
  summary[component+'_rules'].append({'rule':rule,'plain_language_rule':descriptions[rule],'confidence':conf,'taxa_count':len(rr),'simple_chain_ppr_tC':pp,'ppr_percent':100*pp/pt})
 summary[component+'_rules'].sort(key=lambda x:-x['ppr_percent'])
 assert math.isclose(math.fsum(x['ppr_percent'] for x in summary[component+'_rules']),100,abs_tol=1e-8)
verylow=collections.OrderedDict()
for r in detail:
 if r['overall_confidence']!='Very low':continue
 reason=r['membership_reason']
 if reason.startswith('Source Benthic fish is a documented benthic catch-all.'):
  reason='Absent demersal, reef or benthopelagic taxa use the residual Benthic fish pool as the closest represented analogue. Source examples do not establish their membership; provider categories and common names supply only a coarse ecological connection. Named stocks represent different species, and transfer of habitat and feeding composition remains weak.'
 elif reason.startswith('Previously adopted identified-regional-catch taxonomic composition is retained.'):
  reason=reason.split('Constant weights')[0].replace('Previously adopted identified-regional-catch taxonomic composition is retained. Candidate set: ','Unknown composition within ')+ 'Source representative lists do not establish all members of the reporting label.'
 key=(reason,r['allocation_rule'],r['allocation_confidence'])
 if key not in verylow:verylow[key]={'taxa':[],'why_very_low':reason,'allocation_rule':r['allocation_rule'],'allocation_confidence':r['allocation_confidence'],'allocation_assumption':r['allocation_reason'],'ppr_tC':0.0}
 verylow[key]['taxa'].append(r['taxon']); verylow[key]['ppr_tC']+=r['simple_chain_ppr_tC'] or 0
vr=list(verylow.values())
for r in vr:
 r['taxa'].sort();r['ppr_percent']=100*r.pop('ppr_tC')/pt
 if r['allocation_rule']=='W4':r['why_very_low']+=' Source-model Yield proportions assume a fixed composition across 1950–2019 and catch bases; model zero catches do not establish regional absence.'
 elif r['allocation_rule']=='W5':r['why_very_low']+=' Identified-catch proportions are transferred across 1950–2019 without an established match between donor and residual reporting populations.'
assert sum(len(r['taxa']) for r in vr)==190
summary['very_low_decisions']=vr
links=[];cells=[]
for s in wb:
 for row in s:
  for c in row:
   if c.value is not None or c.hyperlink or c.comment:
    cells.append({'sheet':s.title,'cell':c.coordinate,'value':c.value,'hyperlink_target':c.hyperlink.target if c.hyperlink else None,'hyperlink_location':c.hyperlink.location if c.hyperlink else None,'comment':c.comment.text if c.comment else None})
   if c.hyperlink:
    target=c.hyperlink.target; location=c.hyperlink.location
    local=bool(target and not re.match(r'^[a-z]+://',target,re.I)); found=(V/target.split('#')[0]).resolve().exists() if local else True
    links.append({'sheet':s.title,'cell':c.coordinate,'label':c.value,'target':target,'location':location,'local':local,'exists':found,'font_color':c.font.color.rgb if c.font.color and c.font.color.type=='rgb' else None,'underline':c.font.u})
print('SUMMARY',json.dumps({k:v for k,v in summary.items() if k not in ['very_low_decisions','missing_tl_taxa','missing_coefficient_taxa']},ensure_ascii=True))
print('PPR_TABLES',list(book['PPR']))
print('LINKS',json.dumps(links,ensure_ascii=True))
print('SOURCES',json.dumps([[c.value for c in row] for row in wb['Sources']],ensure_ascii=True))
print('VERY_LOW_GROUPS',len(vr));print('FIRST_REVIEW_CHECK',json.dumps(read(E/'coordination_handoff.json')['review_completeness'],ensure_ascii=True))
save(W/'qa/mapping_before_cells.json',cells);save(W/'qa/mapping_before_links.json',links)
save(O/'review_rows_20261114.json',{'scope':'Report-only read-only reuse of the complete current mapping decision set; no adoption, replacement assignments, fresh taxonomy search or scientific calculations','rows':detail})
save(O/'coverage_2019_landings_20261114.json',summary)
verification={'date':'2026-11-14','model_id':MID,'scope':'All 349 catch labels reviewed once against retained source definitions, component decisions, exact current group identities and weights, annual catch and independent classic coefficients. Existing adequately evidenced decisions retained; no groups, weights or classifications changed. This is not fresh taxonomic research or a scientific run.','source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [regional,M/'model.json',V/'taxon_mapping.xlsx',E/'taxon_audit.json',E/'allocation_evidence.json',E/'analogue_review.json',E/'broad_candidate_followup.json',E/'source_catch_provenance.json']},'complete_taxon_set':True,'group_weight_alignment':True,'separate_component_confidence':True,'weakest_component_valid':True,'numeric_sort_valid':True,'catch_and_ppr_denominator_reconciled':True,'both_rule_tables_partition_known_ppr':True,'missing_coefficients_all_zero_reference_catch':True,'confidence_discrepancies':confidence_discrepancies,'very_low_taxa':190,'very_low_reason_groups':len(vr),'appendix_comments':[r for r in cells if r['comment']],'existing_links':links,'scientific_run':False,'adoption':False}
save(O/'mapping_verification_20261114.json',verification)
