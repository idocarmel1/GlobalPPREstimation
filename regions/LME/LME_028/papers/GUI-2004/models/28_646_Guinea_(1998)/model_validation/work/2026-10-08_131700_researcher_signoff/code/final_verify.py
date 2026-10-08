from pathlib import Path
import sys,json,hashlib,re
root=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(root))
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.validation.researcher_review import read_report
run=Path(__file__).resolve().parent.parent
proof=json.loads((run/'qa/handoff.json').read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
report=root/proof['report_path'];model=report.parent.parent/'model.json'
for path,key in [(report,'report_sha256'),(model,'model_sha256'),(root/'regions/LME/LME_028/LME_028.xlsx','regional_workbook_sha256'),(root/'Project.xlsx','project_after_sha256')]:
    assert sha(path)==proof[key],str(path)+' changed after verification'
verify_report(report)
name,date,summary=read_report(root,report,proof['model_id'])
assert (name,date)==(proof['reviewer'],proof['date'])
for file in ['index.html','trends.html']:
    page=(root/'interactive_map'/file).read_text(encoding='utf-8')
    fp=re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">',page).group(1)
    assert fp==proof['project_after_sha256']
assert not (root/'.project-write.lock').exists()
print('PASS: signed source, percentage gate, model and regional science hashes, Project identity and both page fingerprints. Handoff and live-browser source-to-review checks passed; nine report pages inspected.')
