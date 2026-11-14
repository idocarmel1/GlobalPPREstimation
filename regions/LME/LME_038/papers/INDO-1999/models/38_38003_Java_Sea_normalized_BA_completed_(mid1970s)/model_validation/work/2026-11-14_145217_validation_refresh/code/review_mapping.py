from pathlib import Path
import hashlib, json, math, shutil, sys
from collections import defaultdict, Counter
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records, overview
from openpyxl import load_workbook

MID = '38_38003_Java_Sea_normalized_BA_completed_(mid1970s)'
BASE = ROOT / 'regions/LME/LME_038/papers/INDO-1999/models' / MID / 'model_validation'
RUN = BASE / 'work/2026-11-14_145217_validation_refresh'
EV = BASE / 'evidence/source_review'
for d in ['inputs','outputs','qa']: (RUN/d).mkdir(parents=True,exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(v): return hashlib.sha256(json.dumps(json.loads(json.dumps(v,default=str)),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(name,d): (RUN/'outputs'/name).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
bookpath=ROOT/'regions/LME/LME_038/LME_038.xlsx'
inputs=[bookpath,BASE.parent/'model.json',EV/'taxon_audit.json',EV/'candidate_and_allocation_evidence.json',EV/'coverage_summary.json',EV/'identified_catch_proxy_review.json',EV/'taxon_source_links.json',EV/'appendix_sources.json']
hashes={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in inputs}
b=read_book(bookpath,sheets=['Overview','Catch','Classic PPR','Selected model groups','PPR'])
ov=overview(b); assert ov['selected_model_id']==MID
year=int(ov['taxon_detail_year']);basis=ov['catch_basis']; assert (year,basis)==(2019,'landings')
catches=[r for r in records(b,'Catch','Catch') if r['catch_basis']==basis]
classic=records(b,'Classic PPR','Taxa'); matching=[r for r in records(b,'PPR','Matching') if r['model_id']==MID]
reviews=records(b,'PPR','Mapping review'); allocations=records(b,'PPR','Allocation assumptions')
groups=records(b,'Selected model groups','Groups'); model=read(BASE.parent/'model.json')
audit=read(EV/'taxon_audit.json'); candidate=read(EV/'candidate_and_allocation_evidence.json')
for name,arr in [('catch',catches),('classic',classic),('review',reviews),('audit',audit),('candidate',candidate)]:
 assert len({r['taxon'] for r in arr})==len(arr),(name,'duplicate')
assert len({(r['taxon'],r['group']) for r in matching})==len(matching)
cm={r['taxon']:r for r in classic}; rv={r['taxon']:r for r in reviews}; au={r['taxon']:r for r in audit}; ca={r['taxon']:r for r in candidate}
assert set(rv)==set(au)==set(ca)=={r['taxon'] for r in catches}
gm={r['group_name']:r for r in groups}; mg={r['group_name']:r for r in model['group']}
assert len(mg)==28
group_changes=[]
for name,g in mg.items():
 assert int(g['group_seq'])==gm[name]['seq'],name
 for field,stored in [('taxon_descr','taxon_descr'),('export','catch'),('biomass','biomass')]:
  v=g.get(field);w=gm[name].get(stored)
  equal=(v==w) if field=='taxon_descr' else math.isclose(float(v),float(w),rel_tol=1e-12,abs_tol=1e-12)
  if not equal:group_changes.append({'group':name,'field':field,'canonical':v,'stored':w})
bytax=defaultdict(list)
for r in matching: bytax[r['taxon']].append(r)
levels=['High','Medium','Low','Very low','Unresolved']
discrepancies=[];rows=[]
for c in catches:
 t=c['taxon']; old=au[t]; rev=rv[t]; cl=cm.get(t,{})
 m=bytax[t]; assert all(r['group'] in mg for r in m)
 assert math.isclose(sum(r['weight'] for r in m),1,rel_tol=0,abs_tol=1e-10),t
 oldmap=dict(zip(old['group_names'],old['weights'])); curmap={r['group']:r['weight'] for r in m}
 # Saved audit includes meaningful zero-weight candidates not persisted in Matching.
 positiveold={k:v for k,v in oldmap.items() if v!=0}
 positivecur={k:v for k,v in curmap.items() if v!=0}
 assert positiveold.keys()==positivecur.keys() and all(math.isclose(v,positivecur[k],rel_tol=0,abs_tol=1e-14) for k,v in positiveold.items()),(t,'mapping differs',positiveold,positivecur)
 for f in ['membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence','reason']:
  if rev[f]!=old[f]:discrepancies.append({'taxon':t,'field':f,'stored':rev[f],'saved_audit':old[f]})
 weakest=max([rev['membership_confidence'],rev['allocation_confidence']],key=levels.index)
 assert weakest==rev['overall_confidence'],t
 assert all(r['confidence'].lower().replace('_',' ')==weakest.lower() for r in m),(t,'confidence',[r['confidence'] for r in m],weakest)
 catch=c.get(year);sppr=cl.get('sppr');tl=cl.get('tl')
 ppr=0.0 if catch==0 else (catch*sppr/9 if catch is not None and sppr is not None else None)
 for f,v in [('catch_tonnes',catch),('classic_sppr',sppr),('tl',tl),('simple_chain_ppr_tC',ppr)]:
  o=old.get(f)
  if o!=v and not (isinstance(o,(float,int)) and isinstance(v,(float,int)) and math.isclose(o,v,rel_tol=1e-13,abs_tol=1e-8)):
   discrepancies.append({'taxon':t,'field':f,'current':v,'saved_audit':o})
 r={**old,**{f:rev[f] for f in ['membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence','reason']},'reference_year':year,'catch_basis':basis,'catch_tonnes':catch,'classic_sppr':sppr,'tl':tl,'simple_chain_ppr_tC':ppr,'stored_confidence':weakest,'review_confidence':weakest,'adopted_matching':m,'source_locations':{'catch':'Catch / Catch / 2019','classic':'Classic PPR / Taxa','membership_and_allocation':'PPR / Mapping review; PPR / Allocation assumptions'},'zero_weight_candidates':[{'group':k,'weight':v} for k,v in oldmap.items() if v==0]}
 r.pop('prior_mapping',None);rows.append(r)
rows.sort(key=lambda r:(r['simple_chain_ppr_tC'] is None,-(r['simple_chain_ppr_tC'] or 0),r['taxon']))
catchtotal=math.fsum(r['catch_tonnes'] for r in rows if r['catch_tonnes'] is not None)
pprtotal=math.fsum(r['simple_chain_ppr_tC'] for r in rows if r['simple_chain_ppr_tC'] is not None)
def part(items):
 c=math.fsum(r['catch_tonnes'] for r in items if r['catch_tonnes'] is not None);p=math.fsum(r['simple_chain_ppr_tC'] for r in items if r['simple_chain_ppr_tC'] is not None)
 return {'taxa':len(items),'catch_tonnes':c,'ppr_tC':p,'catch_percentage':100*c/catchtotal,'ppr_percentage':100*p/pprtotal}
confidence=[{'label':q,**part([r for r in rows if r['overall_confidence']==q])} for q in levels]
rules={'M2':'A verified historical taxonomic name links the catch taxon to the documented source group.','M3':'Taxonomy and the operative source definition establish an unambiguous group or stage-pair fit.','M5':'Source membership and ecological evidence support a group, with an explicit extension or boundary interpretation.','M6':'The ecological fit is partial or conflicts with another plausible source group.','M9':'Source definitions and regional evidence support an inferred eligible group set.','M10':'A broad reported category is approximated by a plausible set of source groups with uncertain composition.','M11':'A weak but meaningful taxonomic or ecological analogue represents a taxon not adequately resolved by the source model.','W1':'One group receives the full taxon catch; no allocation split is required.','W4':'Printed model-group catch proportions provide a fixed historical composition proxy, including documented source assumptions.','W5':'Identified-catch donor proportions provide an indirect composition proxy with substantial reporting and catch-basis differences.'}
def rule_summary(component):
 keys={(r[component+'_rule'],r[component+'_confidence']) for r in rows}
 out=[{'rule':rule,'plain_language_rule':rules[rule],'confidence':conf,**part([r for r in rows if (r[component+'_rule'],r[component+'_confidence'])==(rule,conf)])} for rule,conf in keys]
 return sorted(out,key=lambda x:(-x['ppr_percentage'],x['rule'],x['confidence']))
copy=RUN/'inputs/taxon_mapping_before.xlsx'
if not copy.exists():shutil.copy2(BASE/'taxon_mapping.xlsx',copy)
w=load_workbook(copy,data_only=False); ws=w['Taxon mapping']; existing={r[0].value:[c.value for c in r] for r in ws.iter_rows(min_row=8)}
assert set(existing)=={r['taxon'] for r in rows};manual=[]
links=read(EV/'taxon_source_links.json')
for r in rows:
 expected=f"Membership {r['membership_confidence']}; allocation {r['allocation_confidence']}. {r['reason']} Sources: {'; '.join([*r['sources'],*links.get(r['taxon'],[])])}."
 r['appendix_reason']=existing[r['taxon']][6]
 if existing[r['taxon']][6]!=expected:manual.append({'taxon':r['taxon'],'field':'Reason','preserved':existing[r['taxon']][6]})
 # Preserve manual mapping and confidence text if it differs; conflicts block publication.
 for i,key in [(4,'mapping_display'),(5,'overall_confidence')]:
  assert existing[r['taxon']][i]==r[key],(r['taxon'],key,'manual conflict')
sources=[]
for rr in w['Sources'].iter_rows(min_row=5):
 sources.append({'source':rr[0].value,'supports':rr[1].value,'label':rr[2].value,'date':rr[3].value,'target':rr[2].hyperlink.target if rr[2].hyperlink else None})
for p in inputs: assert hashes[str(p.relative_to(ROOT)).replace('\\','/')]==sha(p),'input changed during read'
result={'scope':'Report arithmetic and verification of reused adopted mappings; no scientific changes or SPPR execution','unit_id':'LME_038','model_id':MID,'year':year,'basis':basis,'source_groups':len(mg),'synthetic_groups':[g['group_name'] for g in groups if g['group_name'] not in mg],'taxa':len(rows),'total_catch_tonnes':catchtotal,'total_simple_chain_ppr_tC':pprtotal,'missing_coefficient_taxa':[r['taxon'] for r in rows if r['classic_sppr'] is None],'missing_tl_taxa':[r['taxon'] for r in rows if r['tl'] is None],'unknown_ppr_taxa':[r['taxon'] for r in rows if r['simple_chain_ppr_tC'] is None],'confidence_summary':confidence,'membership_summary':rule_summary('membership'),'allocation_summary':rule_summary('allocation'),'very_low_decisions':[{'taxon':r['taxon'],'reason':r['reason'],'appendix_reason':r['appendix_reason'],'ppr_percentage':100*r['simple_chain_ppr_tC']/pprtotal} for r in rows if r['overall_confidence']=='Very low'],'discrepancy_ledger':discrepancies,'group_dependency_changes':group_changes,'manual_content_preserved':manual,'input_hashes':hashes,'dependency_hashes':{name:canon(v) for name,v in [('catch',catches),('classic',classic),('matching',matching),('mapping_review',reviews),('allocation_assumptions',allocations),('canonical_group_membership',[{k:g.get(k) for k in ['group_seq','group_name','taxon_descr','export','biomass']} for g in model['group']])]},'compatibility':{'all_181_saved_decisions_checked':len(rows)==181,'exact_positive_group_weights_match_saved_audit':True,'stored_component_confidence_matches_saved_audit':not discrepancies,'weakest_component_all_rows':True,'canonical_groups_checked_against_regional_groups':not group_changes,'historical_numerical_readiness':ov.get('calculation_status'),'mapping_evidence_reused_without_repeat_resolution':True,'template_xlsx_present':(ROOT/'tools/templates/taxon_mapping.xlsx').exists()},'rows':rows,'sources':sources}
write('mapping_review.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ['rows','sources','very_low_decisions','input_hashes','dependency_hashes']},ensure_ascii=False,indent=2))
print('VERY_LOW',json.dumps([{'taxon':r['taxon'],'reason':r['reason']} for r in rows if r['overall_confidence']=='Very low'],ensure_ascii=False))
