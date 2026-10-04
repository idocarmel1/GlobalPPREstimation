"""Candidate catch attribution only; blocked model coefficients stay unavailable."""
from pathlib import Path
import json,math,csv,collections
C=Path(__file__).resolve().parents[1]
ctx=json.loads((C/'work/regional_context.json').read_text(encoding='utf-8'))
mapping=json.loads((C/'mapping/taxon_mapping_audit.json').read_text(encoding='utf-8'))
by_taxon={r['taxon']:r for r in mapping}
groups=json.loads((C/'extracted_tables/thesis/literal_source_extraction.json').read_text(encoding='utf-8'))['groups']
years=sorted(k for k in ctx['catch'][0] if k.isdigit())
rows=[];summary=[]
for basis in sorted(set(r['catch_basis'] for r in ctx['catch'])):
 for y in years:
  selected=[r for r in ctx['catch'] if r['catch_basis']==basis]
  buckets=collections.defaultdict(list);confcatch=collections.defaultdict(list)
  missing=[]
  for r in selected:
   catch=r.get(y)
   if not isinstance(catch,(int,float)) or not math.isfinite(catch):missing.append(r['taxon']);continue
   decision=by_taxon[r['taxon']]
   confcatch[decision['overall_confidence']].append(catch)
   for a in decision['assignments']:
    if a['weight'] is not None:buckets[a['group_id']].append(catch*a['weight'])
  total=math.fsum(r[y] for r in selected if isinstance(r.get(y),(int,float)))
  allocated=math.fsum(math.fsum(v) for v in buckets.values())
  assert abs(allocated-total)<=1e-8*max(1,total)
  for g in groups:
   rows.append({'year':int(y),'basis':basis,'group_id':g['group_id'],'group_name':g['group_name'],'candidate_allocated_catch_t':math.fsum(buckets[g['group_id']]),'model_id':mapping[0]['model_id'],'variant_id':mapping[0]['variant_id'],'unadopted':True,'GE_ppr_tC':None,'TE_ppr_tC':None,'With_Egestion_ppr_tC':None})
  summary.append({'year':int(y),'basis':basis,'catch_t':total,'allocated_catch_t':allocated,'difference_t':allocated-total,'missing_catch_taxa':missing,'confidence_catch_percentage':{conf:100*math.fsum(confcatch[conf])/total if total>0 else None for conf in ['High','Medium','Low','Very low','Unresolved']},'transfer_assumption':'Fixed thesis1991–1992 estuary mapping/proxy weights across whole-LME1950–2019 regional catch; these are allocations for review, not annual ecosystem reconstruction.','model_ppr_available':False,'model_ppr_reason':'Source group20 identity conflict prevents defensible computational loading or finite group SPPR.'})
(C/'calculations/annual_candidate_allocated_catch.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
(C/'calculations/annual_candidate_allocation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
with (C/'calculations/annual_candidate_allocated_catch.csv').open('w',encoding='utf-8-sig',newline='') as f:
 fields=['year','basis','group_id','group_name','candidate_allocated_catch_t','unadopted']
 w=csv.DictWriter(f,fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in rows)
print(json.dumps({'group_annual_rows':len(rows),'basis_year_rows':len(summary),'max_abs_attribution_difference_t':max(abs(r['difference_t']) for r in summary),'model_ppr_available':False},indent=2))
