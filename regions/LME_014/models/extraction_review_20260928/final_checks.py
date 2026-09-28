from pathlib import Path
import json,csv,math,hashlib
from openpyxl import load_workbook
R=Path(__file__).resolve().parent;ROOT=R.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
ids=read(R/'model_ids.json');checks=[]
for mid in ids:
 f=R.parent/mid;c=read(f/'model.json');x=read(f/'extraction_input.json');w=load_workbook(f/'model_reconstructed.xlsx',read_only=True,data_only=True)
 compared=0;errors=[];unknown_diet_zeroed=0
 for row,g in zip(list(w['Basic input'].values)[1:],c['group']):
  assert row[:2]==(int(g['group_seq']),g['group_name'])
  for j,key in enumerate(['habitat_area','biomass_habitat_area','pb','qb','ee','other_mort','gs','detritus_import'],2):
   expected=None if g[key]=='-9999' else float(g[key]);actual=row[j]
   if expected is None:
    if actual is not None:errors.append([g['group_seq'],key,expected,actual])
   elif actual is None or not math.isclose(expected,actual,rel_tol=1e-12,abs_tol=1e-12):errors.append([g['group_seq'],key,expected,actual])
   compared+=1
 dr=list(w['Diet composition'].values);headers=dr[0];matrix={str(r[0]):r for r in dr[1:] if r[0]}
 for g in c['group']:
  col=headers.index(g['group_seq']);diet=(g.get('diet_descr') or {}).get('diet',[])
  for entry in diet:
   v=entry['proportion'];actual=matrix[entry['prey_seq']][col]
   if v=='-9999':unknown_diet_zeroed+=int(actual==0)
   elif not math.isclose(float(v),actual or 0,rel_tol=1e-12,abs_tol=1e-12):errors.append([g['group_seq'],'diet:'+entry['prey_seq'],v,actual])
   compared+=1
 assert not errors,errors
 result={'model_id':mid,'compared_basic_and_diet_cells':compared,'numeric_mismatches':errors,'excel_relative_absolute_tolerance':1e-12,'unknown_diet_cells_reconstructed_as_zero':unknown_diet_zeroed,'nonlossless_fields':['Source fleet landings/discards are collapsed to combined catch by stock JSON/reconstruction','P/Q retained in canonical ge and source Basic_input but omitted by stock reconstructed Basic input','Canonical model filename loses source metadata in reconstructed Metadata; original Metadata.xlsx authoritative','Unknown diet cells are displayed as zero by stock reconstruction; source CSV and canonical -9999 remain authoritative','Native fleet discard-fate and explicit migration have no full eight-table roundtrip'],'canonical_source_sha256':hashlib.sha256((f/'model.json').read_bytes()).hexdigest()}
 dump(f/'extracted_tables/roundtrip_cell_validation.json',result);checks.append(result)
 for report in [f/'source_report.md',f/'extracted_tables/REPORT.md']:
  with report.open('a',encoding='utf-8') as h:h.write(f'\n## Final round-trip cell audit\n\nCompared {compared} numeric/basic/diet cells between canonical JSON and the reconstructed workbook at1e-12 relative/absolute tolerance: no numeric mismatches. The stock reconstruction displays {unknown_diet_zeroed} canonical unknown diet cells as zero; this is a documented presentation loss, never written back into source outputs. It also collapses fleet catches, omits printed P/Q from Basic input, and loses metadata when the filename is model.json. These limitations are recorded in `roundtrip_cell_validation.json`; original eight tables and Metadata.xlsx remain authoritative.\n')
# Explicit native-versus-published comparison; no reconciliation by replacement.
n=read(R.parent/ids[0]/'extraction_input.json');p=read(R.parent/ids[1]/'extraction_input.json');cmp=[]
for a,b in zip(n['groups'],p['groups']):
 for key in ['name','hab_area','biomass','pb','qb','ee','unassim','ba','tl']:
  if a.get(key)!=b.get(key):cmp.append({'group':a['n'],'field':key,'native':a.get(key),'published':b.get(key),'note':'Native habitat B derived from exact binary B/Area; Table4 B rounded' if key=='biomass' else ''})
for s,diet in n['diet'].items():
 for prey,v in diet.items():
  other=p['diet'].get(s,{}).get(prey)
  if other is not None and abs(float(v)-float(other))>0.00001:cmp.append({'group':int(s),'field':'diet:'+prey,'native':v,'published':other,'note':'Difference exceeds 0.001 percentage point (CSV printed precision)'})
dump(R/'evidence/native_vs_published_differences.json',cmp)
dump(R/'final_verification.json',{'models':checks,'source_hash_verification':read(R/'evidence/source_hash_verification.json'),'no_workbooks_written':True})
print('Cell verification complete',sum(x['compared_basic_and_diet_cells'] for x in checks),'cells;',len(cmp),'source differences retained')
