from pathlib import Path
import json,csv
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'extracted_tables/thesis'
IMP=OUT/'partial_import_evidence'
src=ROOT.parents[1]/'papers/LME027-Villanueva-2004-Thesis/Villanueva2004_thesis_29305.pdf'
for path in [IMP/'model.json', IMP/'27_Canary_Current_Villanueva2004Thesis_Sine_Saloum_(1991-1992).json']:
 j=json.loads(path.read_text(encoding='utf-8'))
 j['metadata']['source']='../../../../../papers/LME027-Villanueva-2004-Thesis/Villanueva2004_thesis_29305.pdf'
 assert (path.parent/j['metadata']['source']).resolve()==src.resolve()
 assert src.exists()
 path.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
literal=json.loads((OUT/'literal_source_extraction.json').read_text(encoding='utf-8'))
canonical=json.loads((OUT/'partial_import_source.json').read_text(encoding='utf-8'))
source_masks=json.loads((OUT/'canonical_diet_missingness.json').read_text(encoding='utf-8'))
errors=[]
for a,b in zip(literal['groups'],canonical['groups']):
 for orig,mapped in [('B','biomass'),('PB','pb'),('QB','qb'),('EE','ee'),('PQ','pq'),('TL','tl')]:
  if a[orig]!=b[mapped]:errors.append([a['group_id'],orig,a[orig],b[mapped]])
for c in literal['diet_cells']:
 value=canonical['diet'][str(c['consumer_id_source_number'])].get(str(c['prey_id']))
 expected=None if c['consumer_id_source_number']==20 or c['prey_id']==20 else c['value']
 if value!=expected:errors.append(['diet',c['cell_id'],value,expected])
sourcepq=[]
for g in literal['groups'][:34]:
 ratio=Decimal(g['PB'])/Decimal(g['QB']);delta=Decimal(g['PQ'])-ratio
 sourcepq.append({'group_id':g['group_id'],'name':g['group_name_source'],'source_PQ':g['PQ'],'PB_div_QB':str(ratio),'source_minus_ratio':str(delta),'within_001':abs(delta)<=Decimal('.001')})
with (OUT/'table_6_5_PQ_arithmetic.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(sourcepq[0]));w.writeheader();w.writerows(sourcepq)
db=json.loads((IMP/'27_Canary_Current_Villanueva2004Thesis_Sine_Saloum_(1991-1992).json').read_text(encoding='utf-8'))
assert len(db['group'])==37
assert all(g['habitat_area']=='-9999' and g['gs']=='-9999' and g['biomass_accum']=='-9999' for g in db['group'])
qa={'source_groups':37,'source_diet_cells':1258,'canonical_parameter_values_checked':222,'canonical_diet_values_and_missing_masks_checked':1258,'unresolved_identity_masked_cells':70,'unresolved_identity_masked_nonblank':13,'source_canonical_value_mask_match':not errors,'errors':errors,'P_Q_arithmetic_all34_within_001':all(r['within_001'] for r in sourcepq),'fish_biomass_source_sum_t_km2':str(sum(Decimal(g['B']) for g in literal['groups'][:29])),'known_published_catch_subtotal_t_km2_year':str(sum(Decimal(g['Y']) for g in literal['groups'] if g['Y'] is not None)),'source_links_resolve':True,'final_database_GS_BA_habitat_missingness_preserved':True,'calculator_loaded':False,'runtime_normalization':False,'diagnostics_status':'NOT_RUN','roundtrip_fidelity':json.loads((IMP/'SOURCE_FIDELITY_CHECK.json').read_text(encoding='utf-8'))}
(OUT/'EXTRACTION_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(qa,ensure_ascii=True))
