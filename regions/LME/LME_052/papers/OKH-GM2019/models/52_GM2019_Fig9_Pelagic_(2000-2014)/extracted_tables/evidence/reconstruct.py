"""Reproduce the conservative extraction and a separately labelled figure hypothesis.

The user's zero convention applies to absent feeding arrows only. Readable
numbers with tentative endpoint assignments stay explicitly tentative. Two
overprinted labels remain unknown in the conservative extraction; their
illustrative readings appear only in the hypothesis variant.
"""
from pathlib import Path
from decimal import Decimal, localcontext
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv, hashlib, json, sys
import numpy as np
from figure9_data import GROUPS, TABLE3, FLOWS

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
TABLES=HERE/'extracted_tables'
AUDIT=HERE/'audit'
CONSUMERS=list(range(2,22))
AREA=Decimal('1544000')
SOURCE=ROOT/'regions/LME_052/papers/OKH-GM2019/gorbatenko_melnikov_2019.pdf'
SOURCE_HASH=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
D=lambda x: Decimal(str(x))

def literal(x):
 if x is None:return None
 return format(x,'f') if isinstance(x,Decimal) else str(x)

def save_json(path,obj):
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

def save_csv(path,header,rows):
 with path.open('w',encoding='utf-8',newline='') as f:
  w=csv.writer(f,lineterminator='\r\n');w.writerow(header);w.writerows(rows)

groups=[dict(n=n,name=name,source_name=ru,figure_production_carbon_million_t_per_year=P,figure_box_pixels=list(box),source_trophic_tier=tier,group_type='producer' if n==1 else 'detritus' if n==22 else 'consumer') for n,name,ru,P,box,tier in GROUPS]
names={g['n']:g['name'] for g in groups}
table={row[-1]:row for row in TABLE3 if row[-1] is not None}
factors={n:D(row[3]) for n,row in table.items()}
table_rows=[]
for seq,row in enumerate(TABLE3,1):
 tier,name,*rest=row
 table_rows.append(dict(source_row=seq,trophic_tier=tier,source_name=name,biomass_wet_million_t=rest[0],wet_per_carbon=rest[1],biomass_carbon_million_t=rest[2],pb_per_year=rest[3],production_wet_million_t_per_year=rest[4],production_carbon_million_t_per_year=rest[5],production_gC_per_m2_per_year=rest[6],tier_share_percent=rest[7],figure_group_id=rest[8],source='Table 3; printed p.154; PDF p.12'))
save_json(AUDIT/'table3_source_readings.json',table_rows)
save_csv(TABLES/'Table3_source_parameters.csv',list(table_rows[0]),[[r[k] for k in table_rows[0]] for r in table_rows])

flows=[]
for fid,prey,consumer,value,hyp,x,y,status,note in FLOWS:
 flows.append(dict(flow_id=fid,prey_id=prey,prey=names[prey],consumer_id=consumer,consumer=names[consumer],source_literal=value.replace('.',',') if value is not None else ('0,02[overprinted]' if fid=='F62' else '0,05[overprinted]'),readable_carbon_flow=value,hypothesis_reading=hyp,label_centre_pixels=[x,y],routing_status=status,note=note,source_pdf='../../papers/OKH-GM2019/gorbatenko_melnikov_2019.pdf',source_sha256=SOURCE_HASH,pdf_page=15,printed_page=157,figure=9))
save_json(AUDIT/'flow_readings.json',flows)
save_csv(TABLES/'Figure9_flow_ledger.csv',list(flows[0]),[[json.dumps(r[k],ensure_ascii=False) if isinstance(r[k],list) else r[k] for k in flows[0]] for r in flows])
index=defaultdict(list)
for f in flows:index[f['prey_id'],f['consumer_id']].append(f)
duplicate_pairs=[dict(prey_id=i,consumer_id=j,prey=names[i],consumer=names[j],flow_ids=[f['flow_id'] for f in fs],status='unresolved endpoint interpretations may have created duplicate pairs; do not accept summed values as author-confirmed') for (i,j),fs in index.items() if len(fs)>1]

def matrix(hypothesis=False,wet=False):
 m={};cellmeta={}
 for j in CONSUMERS:
  for i in range(1,23):
   fs=index.get((i,j),[])
   vals=[f['readable_carbon_flow'] if f['readable_carbon_flow'] is not None else f['hypothesis_reading'] if hypothesis else None for f in fs]
   val=sum((D(v) for v in vals),D(0)) if all(v is not None for v in vals) else None
   if wet and fs:
    val=val*factors[i] if val is not None and i in factors else None
   m[i,j]=val
   cellmeta[i,j]=dict(flow_ids=[f['flow_id'] for f in fs],basis='no displayed arrow: researcher instructed zero' if not fs else 'sum of displayed labels with adopted tentative endpoints' if len(fs)>1 else fs[0]['routing_status'])
 return m,cellmeta

def diets(m):
 totals={j:sum((m[i,j] for i in range(1,23)),D(0)) if all(m[i,j] is not None for i in range(1,23)) else None for j in CONSUMERS}
 diet={}
 for j in CONSUMERS:
  positive=[i for i in range(1,23) if m[i,j]!=0]
  for i in range(1,23):
   v=m[i,j]
   # A one-prey diet is identifiable without its unknown mass conversion.
   diet[i,j]=D(0) if v==0 else D(1) if len(positive)==1 else v/totals[j] if v is not None and totals[j] is not None and totals[j]>0 else None
 return diet,totals

def wide(path,m,extra=None):
 hdr=['Prey ID','Prey']+[f'{j} {names[j]}' for j in CONSUMERS]
 rows=[[i,names[i]]+[literal(m[i,j]) for j in CONSUMERS] for i in range(1,23)]
 if extra:
  rows+=extra
 save_csv(path,hdr,rows)

with localcontext() as ctx:
 ctx.prec=40
 carbon,cellmeta=matrix();hyp,unused=matrix(True);wet,unused=matrix(wet=True);wet_hyp,unused=matrix(True,True)
 dc_c,qc=diets(carbon);dc_h,qh=diets(hyp);dc_w,qw=diets(wet);dc_wh,qwh=diets(wet_hyp)
 wide(TABLES/'Food_flows_carbon.csv',carbon)
 wide(TABLES/'Diet_composition_carbon.csv',dc_c)
 wide(TABLES/'Diet_composition_carbon_label_hypothesis.csv',dc_h)
 wide(TABLES/'Food_flows_wet.csv',wet)
 wide(TABLES/'Diet_composition_wet_review.csv',dc_w)
 wide(TABLES/'Diet_composition_wet_label_hypothesis.csv',dc_wh)

 ledger=[]
 for j in CONSUMERS:
  for i in range(1,23):
   ledger.append(dict(prey_id=i,prey=names[i],consumer_id=j,consumer=names[j],**cellmeta[i,j],carbon_flow=literal(carbon[i,j]),wet_flow=literal(wet[i,j]),carbon_dc=literal(dc_c[i,j]),wet_dc=literal(dc_w[i,j]),carbon_dc_label_hypothesis=literal(dc_h[i,j]),figure_source_hash=SOURCE_HASH))
 save_json(AUDIT/'diet_cell_ledger.json',ledger)

 diagnostic=[]
 for n in range(1,22):
  P=D(groups[n-1]['figure_production_carbon_million_t_per_year'])
  incoming=qc.get(n)
  outgoing=[hyp[n,j] for j in CONSUMERS]
  out_h=sum(outgoing,D(0))
  clear_in=sum((D(f['readable_carbon_flow']) for f in flows if f['consumer_id']==n and f['routing_status']=='clear'),D(0))
  clear_out=sum((D(f['readable_carbon_flow']) for f in flows if f['prey_id']==n and f['routing_status']=='clear'),D(0))
  row=table.get(n)
  b_c=D(row[4]) if row else None
  b_w=D(row[2]) if row else None
  q_w=qw.get(n)
  pq=P/incoming if incoming is not None and incoming>0 else None
  ee=out_h/P
  diagnostic.append(dict(group_id=n,group=names[n],figure_P_carbon=literal(P),conservative_Q_carbon=literal(incoming),hypothesis_Q_carbon=literal(qh.get(n)),known_clear_inflows=literal(clear_in),known_clear_outflows=literal(clear_out),hypothesis_predation_carbon=literal(out_h),P_over_Q_carbon=literal(pq),hypothesis_predation_over_P=literal(ee),energy_failure=pq is not None and pq>1,predation_failure_hypothesis=ee>1,conservative_Q_wet=literal(q_w),derived_QB_wet=literal(q_w/b_w) if q_w is not None and b_w is not None else None,derived_QB_carbon=literal(incoming/b_c) if incoming is not None and b_c is not None else None))
 save_json(AUDIT/'flow_budget_checks.json',diagnostic)
 save_csv(TABLES/'Flow_budget_checks.csv',list(diagnostic[0]),[[r[k] for k in diagnostic[0]] for r in diagnostic])

 # Independent annual consumption reported in prose. Never used as a diet denominator.
 independent=[(4,'2945','153',11),(5,'1445.6','153',11),(6,'152.5','153',11),(7,'320','153',11),(10,'36.9','155',13),(11,'10.29','155',13),(13,'14.74','156',14),(12,'16.5','156',14),(15,'80.8','156',14)]
 comparisons=[]
 for j,q,printed,pdf in independent:
  qcalc=qw[j]
  comparisons.append(dict(group_id=j,group=names[j],reported_Q_wet_million_t_per_year=q,figure_derived_Q_wet_million_t_per_year=literal(qcalc),fraction_of_reported_Q=literal(qcalc/D(q)) if qcalc is not None else None,printed_page=printed,pdf_page=pdf,assessment='figure and prose do not reconcile' if qcalc is not None and abs(qcalc/D(q)-1)>D('.05') else 'incomplete wet conversion' if qcalc is None else 'within 5 percent; not proof of completeness'))
 save_json(AUDIT/'independent_consumption_comparison.json',comparisons)
 save_csv(TABLES/'Independent_consumption_comparison.csv',list(comparisons[0]),[[r[k] for k in comparisons[0]] for r in comparisons])

 # Source-stock parameters stay separate from diagram-derived consumption.
 # Unknown PB/B for separated bacteria/protozoa are not borrowed from the pooled row.
 basic=[]
 for g in groups:
  n=g['n'];row=table.get(n)
  basic.append(dict(n=n,name=g['name'],hab_area='1',biomass=literal(D(row[2])*D(1000000)/AREA) if row else None,pb=row[5] if row else None,qb=next((r['derived_QB_wet'] for r in diagnostic if r['group_id']==n),None),ee=None,other_mort=None,pq=None,unassim=None,detritus_import=None,tl=None,ba=None,ba_rate=None))
 extraction=dict(metadata=dict(LME='52 Sea of Okhotsk',model_number='GM2019-Fig9',model_name='Sea of Okhotsk pelagic figure reconstruction',model_year='2000-2014'),groups=basic,consumers=CONSUMERS,fleets=[],landings={},discards={},detritus_groups=['Detritus'],detritus_fate={},diet={str(j):{**{str(i):literal(dc_w[i,j]) for i in range(1,23)},'import':'0'} for j in CONSUMERS},diet_rows=22,landings_rows=22,discards_rows=22,reconstruction_status='INCOMPLETE_RESEARCH_CANDIDATE',currency='wet weight in eight import tables; carbon diet retained separately',source_group_order='local top-to-bottom figure IDs; not an author/EcoBase numbering',zero_rule='User instruction 2026-10-02: missing displayed feeding arrows are zeros; this does not imply zero catch, mortality, migration, BA, egestion or detritus fate',tentative_endpoints=True,overprinted_label_values_not_adopted=True)
 save_json(TABLES/'extraction.json',extraction)

 # Carbon dataset is the direct target of this reconstruction, distinct from the wet import.
 reconstructed=dict(schema_version=1,model_id=HERE.name,currency='million tC/year flows; dimensionless carbon diets',status='PROVISIONAL_WITH_UNRESOLVED_SOURCE_READINGS',model_period='2000-2014',source_pdf_sha256=SOURCE_HASH,groups=groups,consumers=CONSUMERS,flows=flows,diet={str(j):{str(i):literal(dc_c[i,j]) for i in range(1,23)} for j in CONSUMERS},assumptions=dict(missing_arrows_zero=True,displayed_arrows_exhaustive_for_reconstruction=True,imports_zero=True,endpoint_hypotheses_not_author_confirmed=True),duplicate_pair_flags=duplicate_pairs)
 save_json(HERE/'carbon_reconstruction.json',reconstructed)
 hypothesis=dict(reconstructed,variant='illustrative_overprinted_label_readings',status='ILLUSTRATIVE_ONLY_NOT_VERIFIED',assumed_label_readings={'F62':'0.023','F67':'0.05'},diet={str(j):{str(i):literal(dc_h[i,j]) for i in range(1,23)} for j in CONSUMERS})
 save_json(HERE/'carbon_label_hypothesis.json',hypothesis)

 # TL is derived only for the complete illustrative variant, never written as published TL.
 A=np.eye(22);rhs=np.ones(22)
 for j in CONSUMERS:
  for i in range(1,23):A[j-1,i-1]-=float(dc_h[i,j])
 tl=np.linalg.solve(A,rhs)
 residual=float(np.max(np.abs(A@tl-rhs)))
 save_csv(TABLES/'Derived_TL_label_hypothesis.csv',['Group ID','Group','Derived TL','Variant'],[[g['n'],g['name'],float(tl[g['n']-1]),'illustrative carbon label hypothesis'] for g in groups])

 summary=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),groups=22,consumers=20,label_count=len(flows),route_status_counts=dict(Counter(f['routing_status'] for f in flows)),missing_arrow_zero_cells=sum(not index.get((i,j)) for j in CONSUMERS for i in range(1,23)),conservative_carbon_complete_columns=sum(all(dc_c[i,j] is not None for i in range(1,23)) for j in CONSUMERS),conservative_wet_complete_columns=sum(all(dc_w[i,j] is not None for i in range(1,23)) for j in CONSUMERS),illustrative_carbon_complete_columns=20,unknown_label_consumers=sorted({f['consumer_id'] for f in flows if f['readable_carbon_flow'] is None}),wet_conversion_missing_prey_factors=[2,3,22],duplicate_pair_flags=duplicate_pairs,energy_failure_groups=[r['group'] for r in diagnostic if r['energy_failure']],hypothesis_predation_failure_groups=[r['group'] for r in diagnostic if r['predation_failure_hypothesis']],TL_hypothesis_linear_system_residual=residual,selection_changed=False,map_changed=False,regional_workbook_changed=False,validation_docx_changed=False,fully_balanced_model=False)
 save_json(AUDIT/'reconstruction_summary.json',summary)
 save_json(AUDIT/'workbook_data.json',dict(groups=groups,flows=flows,table3=table_rows,summary=summary,diagnostics=diagnostic,comparisons=comparisons,carbon_dc=[[literal(dc_c[i,j]) for j in CONSUMERS] for i in range(1,23)],carbon_hypothesis_dc=[[literal(dc_h[i,j]) for j in CONSUMERS] for i in range(1,23)],wet_dc=[[literal(dc_w[i,j]) for j in CONSUMERS] for i in range(1,23)],carbon_flow=[[literal(carbon[i,j]) for j in CONSUMERS] for i in range(1,23)],hypothesis_flow=[[literal(hyp[i,j]) for j in CONSUMERS] for i in range(1,23)]))
 print(json.dumps(summary,ensure_ascii=False,indent=2))
