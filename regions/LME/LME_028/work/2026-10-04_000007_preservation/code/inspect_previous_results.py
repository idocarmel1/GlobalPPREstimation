import csv,hashlib,json,math,sys
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book,overview,rows
QA=Path(__file__).parent.parent/'qa';BQ=ROOT/'regions/LME_028/work/2026-10-04_000002_reorganization/qa'
inventory=json.loads((BQ/'canonical_models.json').read_text('utf8'));lookup={(r['unit_id'],r['model_id']):ROOT/r['directory']for r in inventory['destinations']}
moves=list(csv.DictReader((BQ/'file_moves.csv').open(encoding='utf8',newline='')))
out=[]
for r in moves:
 if '/previous_results/'not in r['original_path']or not r['original_path'].endswith('.xlsx'):continue
 p=ROOT/r['original_path'];b=read_book(p);o=overview(b);key=(o.get('unit_id'),o.get('results_model_id'));home=lookup.get(key)
 item={'path':r['original_path'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'unit_id':key[0],'selected_model_id':o.get('selected_model_id'),'results_model_id':key[1],'results_model_sha256':o.get('results_model_sha256'),'input_hash':o.get('calculation_input_sha256'),'canonical_model':home.relative_to(ROOT).as_posix()if home else None,'group_sppr_rows':len(rows(b,'Selected model groups','Group SPPR')),'matching_rows':len(rows(b,'PPR','Matching')),'annual_rows':len(rows(b,'PPR','Annual')),'groups_rows':len(rows(b,'Selected model groups','Groups')),'snapshot_exists':bool(home and(home/'results/regional_snapshot.xlsx').is_file()),'sheet_names':list(b)}
 if home:item['current_model_sha256']=hashlib.sha256((home/'model.json').read_bytes()).hexdigest();item['model_hash_compatible']=item['results_model_sha256']==item['current_model_sha256']
 out.append(item);(QA/'previous_results_fast_review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(key,item['group_sppr_rows'],item['matching_rows'],'snapshot',item['snapshot_exists'],flush=True)
