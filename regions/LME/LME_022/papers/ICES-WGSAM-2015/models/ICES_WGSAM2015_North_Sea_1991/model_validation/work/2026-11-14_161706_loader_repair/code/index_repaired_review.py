"""Refresh model-local evidence references without overwriting historical assessments."""
from pathlib import Path
import hashlib,json,os,sys
from datetime import datetime,timezone
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
RUN=Path(__file__).resolve().parents[1];BASE=RUN.parents[1];MODEL=BASE.parent
EVIDENCE=BASE/'evidence';RESULTS=MODEL/'results/diagnostics/2026-11-14_loader_repair'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
save=lambda p,d:p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
relative=lambda p,base:os.path.relpath(p,base).replace('\\','/')
content=read(RUN/'inputs/report_update.json');manifest=read(RESULTS/'run_manifest.json')
summary=read(RESULTS/'report_ready.json')
scotland_run=ROOT/'regions/LME/LME_022/papers/NS-2025/models/22_20251990_East_Coast_of_Scotland_(1991-1995)/results/diagnostics/2026-11-14_163501_seabird_self_loop'
comparison_path=EVIDENCE/'source_review/candidate_review_loader_repair.json'
comparison={
 'schema_version':1,'created_at':datetime.now(timezone.utc).isoformat(),
 'scope':'Authorized ICES shared-loader/accounting repair and three direct reruns; Scotland retains historical evidence. No researcher decision, model selection or publication changes.',
 'unit_id':'LME_022','primary_pair':['ICES_WGSAM2015_North_Sea_1991','22_20251990_East_Coast_of_Scotland_(1991-1995)'],
 'historical_comparison':{'path':'candidate_review.json','sha256':sha(EVIDENCE/'source_review/candidate_review.json')},
 'current_ices_results':{'path':relative(RESULTS/'report_ready.json',comparison_path.parent),'sha256':sha(RESULTS/'report_ready.json')},
 'code_commit':manifest['code_commit'],'recommendation':content['recommendation'],
 'separate_scotland_investigation':[{'path':relative(scotland_run/'outputs'/name,comparison_path.parent),'sha256':sha(scotland_run/'outputs'/name)} for name in ['baseline_TE_summary.json','remove_redistribute_TE_summary.json']],
 'comparison_rows':[dict(zip(['assessment','ICES','Scotland'],row)) for row in content['comparison_rows']],
 'comparison_note':content['comparison_note'],'ices_summary':summary['summary'],
 'source_parameters_changed':False,'researcher_decision_registered':False,
 'runtime_limitations':['EE floor 0.1 and effective DET-stock closure are explicit calculation assumptions, not recovered source observations.',
 'High Discards SPPR; GE/With Egestion recycling sensitivity and five near-zero TE groups remain.',
 'No exact-model taxon assignment/allocation is adopted.',
 'Rpath port differs from the unavailable accepted native EwE Key Run; Scotland evidence is not a common-settings reproduction.']}
if comparison_path.exists():comparison['created_at']=read(comparison_path).get('created_at',comparison['created_at'])
save(comparison_path,comparison)
if '--comparison-only' in sys.argv:
 print('Comparison evidence written.');sys.exit(0)
index_path=EVIDENCE/'evidence_index.json'
index=read(index_path)
backup=RUN/'inputs/previous_evidence_index.json'
if not backup.exists():backup.write_bytes(index_path.read_bytes())
index['run_id']='2026-11-14_161706_loader_repair'
index['variant_id']='canonical_Rpath_port_global_source_preserving_repair_ee_floor_0.1'
index['computational_input_identity']={
 'current_run_manifest':relative(RESULTS/'run_manifest.json',EVIDENCE),
 'code_commit':manifest['code_commit'],
 'engine_role':'Clean committed shared repair; exact file hashes retained in diagnostic artifacts. Original working project separately retains a pre-existing inactive BA option.',
 'previous_diagnostics':'../../results/diagnostics/2026-11-14_validation'}
artifacts=index['artifacts']
for a in artifacts:
 if a['role']=='comparison' and a.get('path')=='source_review/candidate_review.json':a['role']='historical_comparison'
 if a['role'] in ['GE_outcome','TE_outcome','With_Egestion_outcome'] and '/2026-11-14_validation/' in a.get('path',''):a['role']='historical_'+a['role']
 if a.get('availability')=='present' and a['role'] in ['report','taxon_appendix']:
  a['sha256']=sha((EVIDENCE/a['path']).resolve())
def add(role,p):
 assert p.is_file(),p
 record={'role':role,'path':relative(p,EVIDENCE),'sha256':sha(p),'availability':'present'}
 for i,a in enumerate(artifacts):
  if a.get('path')==record['path'] and a['role']==role:artifacts[i]=record;break
 else:artifacts.append(record)
add('comparison',comparison_path)
for name in ['baseline_TE_summary.json','remove_redistribute_TE_summary.json']:add('separate_scotland_sensitivity',scotland_run/'outputs'/name)
for method,key in [('GE','new_GE'),('TE','new_TE_EEfix'),('With_Egestion','new_WithEgestion')]:add(method+'_outcome',RESULTS/(key+'.json.gz'))
for p in sorted(RESULTS.iterdir()):
 if p.is_file():add('repaired_diagnostic_evidence',p)
for name in ['report_patch_verification.json','final_review_verification.json','integration_manifest.json','engine_tests.xml','final_regressions.xml','test_summary.json','diagnostic_sheet_verification.json','visual_review.json']:
 p=RUN/'qa'/name
 if p.is_file():add('repair_verification',p)
index['reconciliation']={'appendix_universe_and_arithmetic':True,'canonical_scientific_inputs_unchanged':True,
 'researcher_cells_preserved':True,'all_three_source_matrices_reconciled':True}
index['review_boundary']='Editable review files only. No researcher decision registered and no selection, Project.xlsx, regional workbook, map or trends writes by this task.'
index['scientific_validation_complete']=False
index['remaining_limitations']=comparison['runtime_limitations']
save(index_path,index)
sys.path.insert(0,str(ROOT))
import importlib.util
spec=importlib.util.spec_from_file_location('check_evidence',ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
for p in [RESULTS/'evidence_index.json',index_path]:
 result=checker.check(p);save(p.parent/'completeness.json',result)
 print(json.dumps({'index':relative(p,BASE),'complete':result['complete'],'missing_roles':result['missing_roles'],'errors':result['errors']}))
 assert not result['errors']
