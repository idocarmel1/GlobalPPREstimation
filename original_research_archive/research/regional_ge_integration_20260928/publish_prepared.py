"""Apply a verified prepared workbook only if the saved user file is unchanged."""
from pathlib import Path
import sys,json,os,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import sha
report=json.loads((HERE/'STAGED_INTEGRATION_VERIFICATION.json').read_text(encoding='utf-8'))
assert sha(ROOT/'Project.xlsx')==sha(HERE/'baseline/Project.xlsx'),'Saved user edits require a new merge'
assert sha(ROOT/'Project.pending.xlsx')==report['project_sha256']
for r in report['selected_regions']:
    assert sha(ROOT/r['workbook'])==r['workbook_sha256'],r['unit_id']
shutil.copyfile(ROOT/'Project.pending.xlsx',HERE/'prepared/Project.xlsx')
os.replace(ROOT/'Project.pending.xlsx',ROOT/'Project.xlsx')
report.update(staged=False,workbook='Project.xlsx',publication_note='User closed Excel; saved central bytes unchanged from baseline. Verified prepared workbook applied atomically.')
report['diagnostic_schema_normalization']=json.loads((HERE/'health_schema_verification.json').read_text(encoding='utf-8'))
(HERE/'FINAL_INTEGRATION_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Verified combined workbook saved as Project.xlsx.',flush=True)
