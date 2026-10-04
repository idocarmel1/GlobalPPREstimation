import copy,json,sys
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book,overview,sha,input_hash,update_book
from tools.project_core.calculations.regional import result_hash,set_result_hash
QA=Path(__file__).parent.parent/'qa'
path=ROOT/'regions/LME/LME_038/LME_038.xlsx';home=path.parent/'papers/INDO-1999/models/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)'
snapshot=home/'results/regional_snapshot.xlsx'
before=read_book(path);original_sha=sha(path);old=read_book(snapshot);saved_sha=sha(snapshot);canonical_sha=sha(home/'model.json')
target=copy.deepcopy(before);tables=['Allocation assumptions','Mapping review']
for name in tables:
 if name not in old.get('PPR',{}):raise ValueError('Authored evidence missing from historical snapshot: '+name)
 if before['PPR'].get(name,[[],[]])[1]:raise ValueError('Refuse to replace existing authored table: '+name)
 target['PPR'][name]=copy.deepcopy(old['PPR'][name])
if input_hash(target)!=input_hash(before)or result_hash(target)!=result_hash(before):raise ValueError('Authored-table restoration changed numerical dependencies unexpectedly')
set_result_hash(target)
if sha(path)!=original_sha:raise ValueError('Active workbook changed while reading; safe retry needed')
update_book(path,target);after=read_book(path)
for sheet in set(before)|set(after):
 for table in set(before.get(sheet,{}))|set(after.get(sheet,{})):
  if sheet=='PPR'and table in tables:
   if after[sheet][table]!=old[sheet][table]:raise ValueError('Authored table failed exact typed-value restoration')
  elif sheet=='Overview'and table=='Settings':
   b=overview(before);a=overview(after)
   if any(b.get(k)!=a.get(k)for k in set(b)|set(a)if k!='calculation_result_sha256'):raise ValueError('Pending identities or independent settings changed')
  elif before.get(sheet,{}).get(table)!=after.get(sheet,{}).get(table):raise ValueError('Unrelated authoritative table changed: '+sheet+'/'+table)
if sha(snapshot)!=saved_sha or sha(home/'model.json')!=canonical_sha:raise ValueError('Historical snapshot or scientific model bytes changed')
o=overview(after)
if o.get('results_model_id')is not None or o.get('results_model_sha256')is not None or not str(o.get('calculation_status')).startswith('pending:'):raise ValueError('Restoration changed pending model identity')
record={'reason':'Administrative invalidation had incorrectly cleared authored auxiliary mapping evidence. Restore exact snapshot rows without adopting old numerical results.','tables':{n:{'rows':len(after['PPR'][n][1]),'exact_snapshot_values':True}for n in tables},'snapshot_sha256':saved_sha,'canonical_sha256':canonical_sha,'active_before_sha256':original_sha,'active_after_sha256':sha(path),'independent_tables_unchanged':True,'numerical_dependencies_unchanged':True,'generated_result_hash_before':overview(before).get('calculation_result_sha256'),'generated_result_hash_after':o.get('calculation_result_sha256'),'pending_state_preserved':True}
(QA/'authored_mapping_evidence_restoration.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report_path=QA/'regional_table_comparison.json';report=json.loads(report_path.read_text('utf8'))
report['explicit_administrative_or_invalidation_changes']=[r for r in report['explicit_administrative_or_invalidation_changes']if not(r.get('unit_id')=='LME_038'and r.get('sheet')=='PPR'and r.get('table')in tables)]
report['corrected_preservation_issue']=record;report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Restored exact authored mapping evidence:',record['tables'],'pending identities and all numerical tables unchanged.',flush=True)
