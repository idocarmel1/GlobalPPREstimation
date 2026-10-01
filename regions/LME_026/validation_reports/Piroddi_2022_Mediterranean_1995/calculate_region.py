from pathlib import Path
import sys,json
OUT=Path(__file__).parent;ROOT=OUT.parents[3];REGION=OUT.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import run_region
from workbooks import sha
EXPECTED=json.loads((OUT/'qa/adoption_freshness.json').read_text(encoding='utf-8'))['adopted_workbook_sha256']
path=REGION/'LME_026.xlsx'
assert sha(path)==EXPECTED,'Workbook changed before regional calculation'
original_writer=run_region.write_book
def guarded_writer(dest,book):
    assert sha(dest)==EXPECTED,'Workbook changed immediately before calculation save'
    original_writer(dest,book)
run_region.write_book=guarded_writer
sys.argv=['tools/run_region.py','--region',str(REGION),'--stage','calculate']
run_region.main()
(OUT/'qa/calculation_execution.json').write_text(json.dumps({'command':['tools/run_region.py','--region','regions/LME_026','--stage','calculate'],'expected_input_workbook_sha256':EXPECTED,'final_workbook_sha256':sha(path),'freshness_checked_before_read_and_save':True,'scientific_sppr_stage_run':False},indent=2),encoding='utf-8')
