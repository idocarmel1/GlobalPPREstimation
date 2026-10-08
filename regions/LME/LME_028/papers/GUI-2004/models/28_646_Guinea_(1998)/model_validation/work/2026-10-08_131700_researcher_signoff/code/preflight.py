from pathlib import Path
import sys,json,zipfile,re,hashlib,subprocess,collections
root=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(root))
from tools.project_core.registry.discovery import region_directory,resolve_model
from tools.project_core.validation.researcher_review import read_report,table_rows
from tools.project_core.validation.validation_percentage_format import verify_report
from docx import Document
unit='LME_028';mid='28_646_Guinea_(1998)';region=region_directory(root,unit);model=resolve_model(region,mid);report=model.parent/'model_validation/validation.docx'
run=Path(__file__).resolve().parent.parent
for x in ['inputs','outputs','qa']:(run/x).mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
name,date,summary=read_report(root,report,mid)
try:verify_report(report);percentage='PASS'
except ValueError as exc:percentage=str(exc)
with zipfile.ZipFile(region/(unit+'.xlsx')) as z:
    settings={r['field']:r['value'] for _,r in table_rows(z,'Overview','Settings')[3]}
    groups=[r for _,r in table_rows(z,'Selected model groups','Groups')[3]]
with zipfile.ZipFile(root/'Project.xlsx') as z:
    central=[r for _,r in table_rows(z,'Models & coverage','Models')[3] if r['unit_id']==unit]
page_info={}
for file,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
    page=(root/'interactive_map'/file).read_text(encoding='utf-8')
    f=re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">',page)
    start=page.index('const '+var+'=')+len('const '+var+'=');payload,_=json.JSONDecoder().raw_decode(page,start)
    units=payload['network']['units'] if var=='DB' else payload['units']
    focal=next(m for m in units[unit]['models'] if m['id']==mid)
    page_info[file]={'fingerprint':f.group(1) if f else None,'model_keys':list(focal),'model_workbook_sha256':focal.get('workbook_sha256'),'researcher_review':focal.get('researcher_review'),'pending':focal.get('recorded_review_pending')}
doc=Document(report)
manual={row.cells[0].text:row.cells[1].text for table in doc.tables for row in table.rows if len(row.cells)==2 and row.cells[0].text in ['SPPR calculation','Review and reproducibility','Open issues and next action']}
print('SIGNOFF',name,date);print('PERCENTAGES',percentage);print('MANUAL',json.dumps(manual,ensure_ascii=False,indent=2));print('GROUPS',json.dumps([{k:r.get(k) for k in ['seq','group_name']} for r in groups],ensure_ascii=False));print('MODEL_HASH',sha(model));print('WORKBOOK_HASH',sha(region/(unit+'.xlsx')));print('SETTINGS',json.dumps(settings,ensure_ascii=False));print('CENTRAL',json.dumps([{k:v for k,v in r.items() if k in ['unit_id','model_id','selected','model_path','researcher_review_status','researcher_name','researcher_review_date','validation_report_path']} for r in central],ensure_ascii=False));print('PAGE_INFO',json.dumps(page_info,ensure_ascii=False,indent=2));print('PROJECT_HASH',sha(root/'Project.xlsx'));print('SUMMARY',json.dumps(summary,ensure_ascii=False,indent=2))
git='C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
status=subprocess.run([git,'status','--porcelain','--untracked-files=normal'],cwd=root,capture_output=True,text=True,encoding='utf-8',check=True).stdout.splitlines()
status_counts=collections.Counter(x[:2] for x in status)
changes=subprocess.run([git,'diff','--no-renames','--name-only','ec297723','--'],cwd=root,capture_output=True,text=True,encoding='utf-8',check=True).stdout.splitlines()
areas=collections.Counter(x.strip('"').split('/')[0] for x in changes)
print('CHANGE_SUMMARY',json.dumps({'baseline':'ec297723 (1 October selected-region validation)','working_status_counts':dict(status_counts),'changed_path_counts':dict(areas)},ensure_ascii=False))
data={'unit_id':unit,'model_id':mid,'report_path':report.relative_to(root).as_posix(),'report_sha256':sha(report),'model_sha256':sha(model),'regional_workbook_sha256':sha(region/(unit+'.xlsx')),'reviewer':name,'review_date':date,'summary':summary,'percentage_check':percentage,'settings':settings,'groups':groups,'manual':manual,'central':central,'page_info':page_info,'project_sha256':sha(root/'Project.xlsx'),'change_summary':dict(areas),'working_status_counts':dict(status_counts)}
(run/'qa/preflight.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
