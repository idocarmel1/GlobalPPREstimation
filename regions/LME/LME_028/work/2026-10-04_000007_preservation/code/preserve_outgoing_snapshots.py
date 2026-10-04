import csv,json,sys
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book,overview,sha
from tools.project_core.calculations.snapshots import save_snapshot
from tools.project_core.calculations.selection import execution_identity
QA=Path(__file__).parent.parent/'qa';BQ=ROOT/'regions/LME_028/work/2026-10-04_000002_reorganization/qa'
inventory=json.loads((BQ/'canonical_models.json').read_text('utf8'));lookup={(r['unit_id'],r['model_id']):ROOT/r['directory']for r in inventory['destinations']}
allowed={('LME_013','13_2_Northern_Humboldt_Current_(1995-1998)'),('LME_013','13_1_Chilean_Patagonia_(1980)'),('LME_052','52_1_Sea_of_Okhotsk_NE_(1980)')}
out=[]
for entry in json.loads((QA/'previous_results_fast_review.json').read_text('utf8')):
 key=(entry['unit_id'],entry['results_model_id'])
 if key not in allowed:continue
 source=ROOT/entry['path'];home=lookup[key]
 if(home/'results/regional_snapshot.xlsx').exists():raise ValueError('Refuse to overwrite an existing useful snapshot: '+str(home))
 book=read_book(source);identity=execution_identity(ROOT,home,book)
 snapshot=save_snapshot(source,home,result_identity=identity)
 if snapshot is None or sha(source)!=sha(snapshot):raise ValueError('Full outgoing workbook byte equality failed')
 manifest=json.loads((home/'results/result_manifest.json').read_text('utf8'))
 out.append({'source':entry['path'],'snapshot':snapshot.relative_to(ROOT).as_posix(),'sha256':sha(snapshot),'full_byte_copy_verified':True,'actual_results_model_id':overview(book)['results_model_id'],'historical_results_model_sha256':overview(book).get('results_model_sha256'),'present_canonical_sha256':sha(home/'model.json'),'effective_flags':manifest['effective_flags'],'code_identity':manifest['code_identity'],'numerical_restoration_limitation':'Unknown flags/code or mismatched model hash prevents numerical reuse; preserved full workbook remains honest historical evidence.'})
 (QA/'preserved_previous_snapshots.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Preserved byte-identical full outgoing workbook:',key,flush=True)
