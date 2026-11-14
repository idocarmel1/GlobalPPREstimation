import sys,json,hashlib
from pathlib import Path
root=Path.cwd().resolve()
sys.path.insert(0,str(root))
from tools.project_core.validation.researcher_review import read_report
from tools.project_core.registry.discovery import region_directory,resolve_model
model_id='Hernvann_2020_Celtic_Sea_1985'
model=resolve_model(region_directory(root,'LME_024'),model_id)
report=model.parent/'model_validation'/'validation.docx'
name,date,summary=read_report(root,report,model_id)
packet={'unit_id':'LME_024','model_id':model_id,'report_path':report.relative_to(root).as_posix(),'report_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),'canonical_path':model.relative_to(root).as_posix(),'canonical_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'researcher_name':name,'review_date':date,'summary':summary,'excluded_seq':[],'authorization':'User explicitly requested registration of disqualification in Project.xlsx and coordinator-owned map/trends update','scope':'Review metadata only; no source edits, science, selection or arithmetic changes'}
assert summary.get('status')=='Disqualified by researcher'
output=Path(__file__).resolve().parents[1]/'outputs'/'signed_review_packet.json'
output.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(packet,ensure_ascii=False,indent=2))
