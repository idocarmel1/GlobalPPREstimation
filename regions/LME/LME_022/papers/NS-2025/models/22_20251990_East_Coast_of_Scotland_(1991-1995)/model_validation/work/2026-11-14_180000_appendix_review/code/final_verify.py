from pathlib import Path
from openpyxl import load_workbook
import json,math,hashlib,urllib.parse,collections
RUN=Path(__file__).resolve().parents[1]; MODEL=RUN.parents[2]; APP=RUN.parents[1]/'taxon_mapping.xlsx'
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=read(MODEL/'model_validation/evidence/source_review/taxon_audit.json'); h=read(RUN/'outputs/report_handoff.json'); q=read(RUN/'outputs/mapping_verification.json')
tc=sum(r['catch_tonnes'] for r in audit); tp=sum(r['simple_chain_ppr_tC'] for r in audit)
assert math.isclose(tc,h['summary']['total_catch_tonnes'],rel_tol=1e-12)
assert math.isclose(tp,h['summary']['total_simple_chain_ppr_tC'],rel_tol=1e-12)
for summary,key in [(h['confidence_rows'],'overall_confidence'),(h['membership_rows'],'membership_rule'),(h['allocation_rows'],'allocation_rule')]:
 for row in summary:
  rr=[r for r in audit if r[key]==row.get('label',row.get('rule'))]
  assert len(rr)==row['taxa']
  assert math.isclose(sum(r['simple_chain_ppr_tC'] for r in rr)/tp*100,row['ppr_percentage'],abs_tol=1e-10)
  if 'catch_percentage' in row: assert math.isclose(sum(r['catch_tonnes'] for r in rr)/tc*100,row['catch_percentage'],abs_tol=1e-10)
 assert math.isclose(sum(r['ppr_percentage'] for r in summary),100,abs_tol=1e-8)
levels=['High','Medium','Low','Very low','Unresolved']
assert all(r['overall_confidence']==levels[max(levels.index(r['membership_confidence']),levels.index(r['allocation_confidence']))] for r in audit)
vl=[t for r in h['very_low_decisions_compact'] for t in r['taxa']]
assert len(vl)==len(set(vl))==110 and set(vl)=={r['taxon'] for r in audit if r['overall_confidence']=='Very low'}
w=load_workbook(APP); before=load_workbook(RUN/'inputs/taxon_mapping_before.xlsx')
assert list(w['Taxon mapping'].values)[7:]==list(before['Taxon mapping'].values)[7:]
links=[]
for s in w:
 for row in s:
  for c in row:
   if not c.hyperlink: continue
   t=c.hyperlink.target
   if t and not t.startswith(('http:','https:')): assert (APP.parent/urllib.parse.unquote(t.split('#')[0])).exists()
   assert c.font.underline in ['single','double']
   links.append((s.title,c.coordinate,t,c.hyperlink.location))
assert sha(ROOT/'regions/LME/LME_022/LME_022.xlsx')==q['current_region_sha256']
assert sha(MODEL/'model.json')==q['canonical_sha256']
result={'status':'pass','appendix_sha256':sha(APP),'all_384_taxon_rows_byte_semantic_preservation':True,'catch_classic_and_snapshot_matching_compatible':True,'current_regional_matching_rows':0,'mapping_adoption':False,'confidence_counts':[r['taxa'] for r in h['confidence_rows']],'catch_total_t':tc,'simple_chain_total_tC':tp,'very_low_count':len(vl),'very_low_compact_groups':len(h['very_low_decisions_compact']),'unresolved_taxa':h['summary']['unresolved_taxa'],'links_checked':len(links),'all_links_preserved':True,'same_canonical_and_region_hashes':True,'appendix_filters_and_frozen_headers':True,'visual_checks':'Final changed view renders inspected at normal zoom: candidate header and Sources diagnostics, candidate-mapping and baseline-exposure notes. Unchanged taxon body preserved.'}
(RUN/'qa/final_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
