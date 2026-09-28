"""Read-only completion checks plus a compact verification record."""
from extract_candidates import *
import math
names=['22_20251890_East_Coast_of_Scotland_(1890-1895)','22_20251990_East_Coast_of_Scotland_(1991-1995)','22_20071991_North_Sea_report_Table_3.3_(1991)','457_457_North_Sea_(1991)']
result=[]
for name in names:
 d=REG/'models'/name;src=json.loads((d/'model.json').read_text(encoding='utf8'));summary=json.loads((d/'SPPR_DIAGNOSTICS.json').read_text())
 h=hashlib.sha256((d/'model.json').read_bytes()).hexdigest();assert h==summary['model_json_sha256']
 wb=openpyxl.load_workbook(d/'candidate_diagnostics.xlsx',read_only=True,data_only=True);ov=dict((r[0],r[1]) for r in list(wb['Overview'].values)[2:] if len(r)>1 and r[0]);assert ov['results_model_sha256']==h and ov['production_eligible'] is False;wb.close()
 et=d/'extracted_tables';rr=et if et.exists() else d/'repository_roundtrip'
 if et.exists():
  for file in ['Metadata.xlsx','Basic_input.csv','Diet_composition.csv','Detritus_fate.csv','Landings.csv','Discards.csv','Biomass_accumulation.csv','TL.xlsx']:assert (et/file).is_file()
 wb=openpyxl.load_workbook(next(rr.glob('*reconstructed.xlsx')),read_only=True,data_only=True)
 basic={str(r[0]):r for r in list(wb['Basic input'].values)[1:]};diet=list(wb['Diet composition'].values);dh=diet[0];dr={str(r[0]):r for r in diet[1:]};cells=0
 for g in src['group']:
  seq=g['group_seq'];r=basic[seq];assert r[1]==g['group_name']
  for col,key in [(2,'habitat_area'),(3,'biomass_habitat_area'),(4,'pb'),(5,'qb'),(6,'ee'),(8,'gs')]:
   if float(g[key])==-9999:assert r[col] is None
   else:assert math.isclose(float(r[col]),float(g[key]),rel_tol=1e-12,abs_tol=1e-12)
   cells+=1
  entries=(g.get('diet_descr') or {}).get('diet',[])
  if isinstance(entries,dict):entries=[entries]
  de={str(x['prey_seq']):float(x['proportion']) for x in entries}
  for prey in basic:assert math.isclose(float(dr[prey][dh.index(seq)] or 0),de.get(prey,0),rel_tol=1e-12,abs_tol=1e-12);cells+=1
 wb.close()
 snapshots={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [d/'model.json',*(d/'diagnostic_code').rglob('*.py')]}
 if not (d/'diagnostic_code_hashes.json').exists():dump(d/'diagnostic_code_hashes.json',snapshots)
 else:assert json.loads((d/'diagnostic_code_hashes.json').read_text())==snapshots
 result.append({'candidate':name,'groups':len(src['group']),'roundtrip_numeric_cells':cells,'canonical_and_run_hash_match':True,'isolated_not_production':True,'source_roundtrip_exists':True})
wb=openpyxl.load_workbook(REG/'LME_022.xlsx',read_only=True,data_only=True);ov={r[0]:r[1] for r in list(wb['Overview'].values)[2:] if len(r)>1 and r[0]};wb.close();assert not ov.get('selected_model_id')
dump(OUT/'COMPLETION_VERIFICATION.json',{'candidates':result,'live_region_selected_model_id':ov.get('selected_model_id'),'live_region_sha256':hashlib.sha256((REG/'LME_022.xlsx').read_bytes()).hexdigest(),'central_registration':'coordinated by parent; not written by extraction agent'})
print(json.dumps(result))

