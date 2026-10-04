"""Run only after the stable HTML handoff and serialized root authorization."""
import copy, hashlib, json, re, shutil, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as E

QA=Path(__file__).resolve().parent
ROOT=next(p for p in QA.parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT/'tools'))
from researcher_review import register_review,table_rows,FIELDS,approved_review
from build_html import refresh_reviews
PROJECT=ROOT/'Project.xlsx';BASELINE=QA/'baseline_Project.xlsx'
REPORT=ROOT/'regions/LME_034/Model_validation_34_1_Bay_of_Bengal_(1978).docx'
MODEL='34_1_Bay_of_Bengal_(1978)'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXPECTED_PROJECT='05343788bdfd9ba31c63cd4affa366d8406f32741285846a816058aa60a0d3a7'
EXPECTED_REPORT='3e1f329da2cb8160f8f8cd56443fcb4f62b1377689dbc4206ab9846dd6196da2'
assert sha(PROJECT)==EXPECTED_PROJECT and sha(REPORT)==EXPECTED_REPORT
assert not BASELINE.exists(),'Do not accidentally replay registration'
region=ROOT/'regions/LME_034/LME_034.xlsx'
region_sha=sha(region)
with zipfile.ZipFile(region) as z:
 groups=[r for _,r in table_rows(z,'Selected model groups','Groups')[3]]
 assert len(groups)==50 and not any('bird' in r['group_name'].lower() or 'mammal' in r['group_name'].lower() for r in groups)
with zipfile.ZipFile(PROJECT) as z:
 old_models={(r['unit_id'],r['model_id']):r for _,r in table_rows(z,'Models & coverage','Models')[3]}
 model_path=ROOT/old_models[('LME_034',MODEL)]['model_path']
 model_sha=sha(model_path)
shutil.copyfile(PROJECT,BASELINE)
# The exact Word label is preserved; there is no matching selected-model group.
register_review(PROJECT,REPORT,'LME_034',MODEL,[])
with zipfile.ZipFile(BASELINE) as old,zipfile.ZipFile(PROJECT) as new:
 changed=[n for n in old.namelist() if old.read(n)!=new.read(n)]
 new_models={(r['unit_id'],r['model_id']):r for _,r in table_rows(new,'Models & coverage','Models')[3]}
 assert set(old_models)==set(new_models)
 changed_models=[k for k in old_models if old_models[k]!=new_models[k]]
 assert changed_models==[('LME_034',MODEL)]
 for key,row in old_models.items():
  for field,value in row.items():
   if key==('LME_034',MODEL) and field in FIELDS:continue
   assert new_models[key][field]==value,(key,field)
 assert set(changed)<=set(['xl/worksheets/sheet3.xml','xl/tables/table3.xml','xl/styles.xml'])
 sheet,headers,_,rows=table_rows(new,'Models & coverage','Models')
 row=next(r for r,d in rows if d['unit_id']=='LME_034' and d['model_id']==MODEL)
 S='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
 styles=E.fromstring(new.read('xl/styles.xml'));fonts=styles.find(S+'fonts');formats=styles.find(S+'cellXfs')
 def col(address):
  out=0
  for ch in re.match('[A-Z]+',address)[0]:out=out*26+ord(ch)-64
  return out
 green={}
 for field in ['model_id','researcher_review_status']:
  cell=next(c for c in row if col(c.get('r'))==headers.index(field)+1)
  color=fonts[int(formats[int(cell.get('s'))].get('fontId'))].find(S+'color').get('rgb')
  assert color=='FF187344';green[field]=color
data=new_models[('LME_034',MODEL)]
assert data['researcher_review_status']=='Validated by researcher'
assert data['validation_report_sha256']==EXPECTED_REPORT
assert data['reviewed_model_sha256']==model_sha
assert data['researcher_name']=='Ido Carmel' and data['researcher_review_date']=='2026-10-01'
summary=json.loads(data['researcher_review_summary']);assert summary['excluded_group_ids']==[]
assert 'seabirds' in summary['sections'][2]['rows'][0]['text']
assert sha(region)==region_sha and sha(model_path)==model_sha
(QA/'registered_review.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
proof={'baseline_project_sha256':EXPECTED_PROJECT,'project_sha256':sha(PROJECT),'changed_project_zip_parts':changed,
 'changed_model_rows':[list(k) for k in changed_models],'all_other_model_metadata_unchanged':True,
 'old_model_scientific_fields_unchanged':True,'green_fonts':green,'regional_workbook_sha256':region_sha,'model_sha256':model_sha,
 'source_review_label_without_applicable_group':{'Word_SPPR_exclusion':'seabirds','selected_model_matching_groups':[],
  'applicable_display_exclusions':[],'decision':'Preserve the user Word row verbatim and apply no exclusion because the selected model has no matching group; do not substitute another group.'}}
(QA/'project_preservation.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
refresh_reviews(PROJECT,BASELINE,['LME_034'])
assert sha(region)==region_sha and sha(model_path)==model_sha and sha(REPORT)==EXPECTED_REPORT
(QA/'metadata_refresh.json').write_text(json.dumps({'project_sha256':sha(PROJECT),'report_sha256':sha(REPORT),
 'refresh_reviews_exact_replay_preservation_gate_passed':True,'all_other_embedded_data_preserved':True,
 'model_group_exclusions':[],'source_SPPR_label':'seabirds','scientific_workbooks_and_model_unchanged':True},indent=2),encoding='utf-8')
print(json.dumps(proof,indent=2))
