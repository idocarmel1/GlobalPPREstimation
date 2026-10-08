from pathlib import Path
import hashlib,json,re,zipfile
from datetime import date
from docx import Document
from tools.project_core.validation.researcher_review import read_report,table_rows
from tools.project_core.registry.discovery import resolve_model,region_directory

root=Path.cwd().resolve();unit='LME_027';model_id='27_Villanueva2004_SineSaloum'
model=resolve_model(region_directory(root,unit),model_id)
report=model.parent/'model_validation/validation.docx'
run=Path(__file__).resolve().parents[1];qa=run/'qa';qa.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fields={row.cells[0].text:row.cells[1].text for row in Document(report).tables[0].rows if len(row.cells)==2}
identity=fields['Candidate model'];assert identity.splitlines()[0]==model_id
manual=fields['Review and reproducibility']
match=re.search(r'Researcher name:\s*([^|\n]+)\s*\|\s*review date:\s*(\d{2})/(\d{2})/(\d{4})',manual)
assert match and manual.count('MODEL DISQUALIFIED')==1 and 'MODEL VALIDATED' not in manual
name,day,month,year=match.groups();signed_date=date(int(year),int(month),int(day)).isoformat()
reason=manual.partition('MODEL DISQUALIFIED')[2].strip();assert reason.startswith('Reason – ')
regional=region_directory(root,unit)/(unit+'.xlsx')
with zipfile.ZipFile(regional) as z:settings={r['field']:r['value'] for _,r in table_rows(z,'Overview','Settings')[3]}
with zipfile.ZipFile(root/'Project.xlsx') as z:
 row=next(r for _,r in table_rows(z,'Models & coverage','Models')[3] if r['unit_id']==unit and r['model_id']==model_id)
try:
 parsed=read_report(root,report,model_id);parser_error=None
except ValueError as error:parsed=None;parser_error=str(error)
fingerprint=sha(root/'Project.xlsx')
result={'status':'BLOCKED_UNSELECTED_CANDIDATE_HANDOFF','unit_id':unit,'model_id':model_id,
 'verified_actual_source':{'path':report.relative_to(root).as_posix(),'sha256':sha(report),'identity_field':'Candidate model','researcher_name':name.strip(),'review_date':signed_date,'verdict':'MODEL DISQUALIFIED','reason':reason},
 'canonical_model_sha256':sha(model),'selected_model_id':settings['selected_model_id'],
 'current_central_candidate_review_status':row.get('researcher_review_status'),
 'supported_read_report_error':parser_error,
 'handoff_limits':['read_report requires the Selected model field','register_review requires this exact model to be selected','refresh_reviews addresses the selected model and requires it already exists in embedded payload'],
 'map_candidate_present':False,'proposed_bounded_extension':{'register_exact_candidate_decision':True,'display_candidate_verdict_and_reason':True,'change_selection':False,'recalculate':False,'edit_signed_Word':False,'transfer_exclusions':False},
 'Project_sha256_before':fingerprint,'regional_workbook_sha256':sha(regional),'map_fingerprints_match_current_Project':{},
 'central_or_generated_files_written':False}
for page in ['index.html','trends.html']:
 text=(root/'interactive_map'/page).read_text(encoding='utf8')
 result['map_fingerprints_match_current_Project'][page]=fingerprint in text.split('</head>',1)[0]
 if page=='index.html':
  payload=json.JSONDecoder().raw_decode(text,text.index('const DB=')+len('const DB='))[0]
  result['map_candidate_present']=any(m['id']==model_id for m in payload['network']['units'][unit]['models'])
assert sha(root/'Project.xlsx')==fingerprint and sha(report)==result['verified_actual_source']['sha256']
(qa/'registration_preflight.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
