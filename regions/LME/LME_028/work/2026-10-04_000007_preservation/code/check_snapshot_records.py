import json
from pathlib import Path
QA=Path(__file__).parent.parent/'qa'
items=json.loads((QA/'full_snapshot_identities.json').read_text('utf8'))
bad=[r for r in items if r['actual_sha256']!=r['manifest_snapshot_sha256']or r['model_id']!=r['manifest_results_id']or r['model_id']!=r['overview_results_id']]
if bad:raise ValueError('Snapshot bytes/actual identity do not match the recorded package: '+str(bad))
historical=[{'unit_id':r['unit_id'],'model_id':r['model_id'],'historical_sha256':r['overview_results_hash'],'current_sha256':r['current_model_hash']}for r in items if r['overview_results_hash']!=r['current_model_hash']]
if len(historical)!=1 or historical[0]['unit_id']!='LME_038':raise ValueError('Unexpected numerical model hash mismatch in saved packages: '+str(historical))
report=json.loads((QA/'preservation_report.json').read_text('utf8'));report['snapshots']['all_manifest_byte_hashes_exact']=True;report['snapshots']['all_actual_results_identities_match']=True;report['snapshots']['historical_model_hash_mismatch']=historical
(QA/'preservation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Verified',len(items),'full-snapshot manifest/byte identities; only explicitly historical LME_038 differs from current canonical model hash.')
