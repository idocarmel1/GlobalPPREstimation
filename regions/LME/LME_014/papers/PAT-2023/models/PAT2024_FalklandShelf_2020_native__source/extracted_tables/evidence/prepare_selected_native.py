from pathlib import Path
import sys,json,shutil,hashlib
MODEL=Path(__file__).resolve().parent;REGION=MODEL.parents[1];ROOT=REGION.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,write_book,sha,overview
from regional import set_setting
from run_region import prepare_selection
MID='PAT2024_FalklandShelf_2020_native'
E=MODEL/'selection_20260928';E.mkdir(exist_ok=True)
src=MODEL/'loader_input'/f'14_140001_{MID}_(2020).json'
dest=MODEL/'computational_input'/f'14_140001_{MID}_(2020).json';dest.parent.mkdir(exist_ok=True)
shutil.copy2(src,dest)
record=json.loads((MODEL/'diagnostic_run_record.json').read_text(encoding='utf-8'))
assert 'derived_native_completion' in record
assert all(v['return']['status']=='WARN' for v in record['diagnostics'].values())
assert all(v['return']['model_input']['is_model_balanced'] for v in record['diagnostics'].values())
bookpath=REGION/'LME_014.xlsx';b=read_book(bookpath)
before=E/f'LME_014_before_selection_{sha(bookpath)[:12]}.xlsx'
if not before.exists():shutil.copy2(bookpath,before)
rationale='User selected PAT2024_FalklandShelf_2020_native because the native-source reconstruction did not FAIL. GE, TE and With Egestion all return WARN, not OK. Computational input uses the audited coupled Ecopath solution only for source-missing living/producer B and EE; source model.json and the native database remain unchanged. Native discard routing and loader-derived detritus accumulation limitations remain explicit; Falkland shelf is a subregion of the LME.'
set_setting(b,'selected_model_id',MID);set_setting(b,'model_path',dest.relative_to(REGION).as_posix());set_setting(b,'selection_rationale',rationale)
set_setting(b,'selected_paper_ids','PAT-2023');set_setting(b,'production_eligible',False)
set_setting(b,'source_model_path',(MODEL/'model.json').relative_to(REGION).as_posix())
set_setting(b,'computational_input_note','Audited coupled native Ecopath B/EE completion; see model selection report. No consumer diet normalization or routing changes.')
prepare_selection(b,bookpath);write_book(bookpath,b)
provenance={'selected_model_id':MID,'source_model_sha256':sha(MODEL/'model.json'),'computational_input_sha256':sha(dest),'diagnostic_input_sha256':sha(src),'computational_input_path':dest.relative_to(REGION).as_posix(),'source_model_path':(MODEL/'model.json').relative_to(REGION).as_posix(),'user_rationale':rationale,'derived_native_completion':record['derived_native_completion'],'status':'selection recorded; bounded same-configuration pipeline pending','prior_workbook_sha256':sha(before)}
(E/'selection_provenance.json').write_text(json.dumps(provenance,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(overview(read_book(bookpath)),ensure_ascii=False,indent=2))
