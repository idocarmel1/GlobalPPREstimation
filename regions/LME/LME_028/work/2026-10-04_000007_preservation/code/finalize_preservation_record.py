import hashlib,json,re
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());QA=Path(__file__).parent.parent/'qa';BQ=ROOT/'regions/LME_028/work/2026-10-04_000002_reorganization/qa'
inventory=json.loads((BQ/'canonical_models.json').read_text('utf8'));review=json.loads((ROOT/'regions/LME_028/work/2026-10-04_000001_reorganization_review/qa/review_lineage_dispositions.json').read_text('utf8'));registered={(r['unit_id'],r['model_id']):r for r in review['registered_model_mapping']}
for item in inventory['destinations']:
 p=ROOT/item['directory']/'model_notes.md';mid=item['model_id'];unit=item['unit_id'];text=p.read_text('utf8')
 text=re.sub(r'^# [^\n]+','# '+mid,text,count=1)
 source_id=registered.get((unit,mid),{}).get('paper_ids')or next((r.get('paper_id')or r.get('proposed_paper_id') for k in ['unregistered_existing_model_mapping','distinct_source_computational_variants']for r in review[k]if r.get('model_id',r.get('proposed_distinct_model_id'))==mid and r['unit_id']==unit),None)
 if source_id:text=re.sub(r'(## Source identity\n\n)[^\n]+',lambda m:m.group(1)+source_id,text,count=1)
 # Scientific cell/arrow/table identifiers such as J14/F62/S8 remain exact.
 text=re.sub(r'\b([A-Z]) ([0-9]+)\b',r'\1\2',text)
 p.write_text(text,encoding='utf8')
record=json.loads((QA/'model_notes_and_sources.json').read_text('utf8'))
for r in record['notes']:
 p=next(ROOT/i['directory']/'model_notes.md'for i in inventory['destinations']if i['unit_id']==r['unit_id']and i['model_id']==r['model_id']);r['notes_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
(QA/'model_notes_and_sources.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report=json.loads((QA/'preservation_report.json').read_text('utf8'));late=json.loads((QA/'late_move_reconciliation.json').read_text('utf8'))
unresolved=[r for r in late if r['status']!='resolved_later_responsibility_move'];report['retained_files']['missing']=unresolved;report['retained_files']['late_move_reconciliation']={'resolved':len(late)-len(unresolved),'unresolved':unresolved,'evidence':'late_move_reconciliation.json'}
report['regional_workbooks']=json.loads((QA/'regional_table_comparison.json').read_text('utf8'))
report['preserved_previous_workbook_snapshots']=json.loads((QA/'preserved_previous_snapshots.json').read_text('utf8'))
report['obsolete_previous_result_disposition']=json.loads((QA/'obsolete_previous_result_disposition.json').read_text('utf8'))
report['model_notes_and_paper_sources']={'model_notes':len(record['notes']),'paper_manifests':len(record['paper_manifests']),'source_byte_verification':record['paper_source_byte_verification'],'evidence':'model_notes_and_sources.json'}
report['verification_scope']='The complete original-file hash pass and366-region baseline table comparison were performed before final cleanup. Subsequently documented harmless navigation/list changes, required authored-mapping restoration and exact outgoing snapshot copies are separate bounded checks. This record does not substitute for final layout/publisher/graph/release checks.'
report['pass']=report['canonical_models']['all_exact']and not report['retained_files']['unexpected_data_changes']and not unresolved and not report['regional_workbooks']['unexpected_table_changes']and report['regional_workbooks']['selected_unchanged']and not report['central_model_metadata']['unexpected_changes']and report['central_model_metadata']['review_decisions_unchanged']
(QA/'preservation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Preservation evidence consolidated. Pass:',report['pass'],'canonical:',report['canonical_models']['count'],'regional:',report['regional_workbooks']['count'],'resolved late moves:',len(late)-len(unresolved))
