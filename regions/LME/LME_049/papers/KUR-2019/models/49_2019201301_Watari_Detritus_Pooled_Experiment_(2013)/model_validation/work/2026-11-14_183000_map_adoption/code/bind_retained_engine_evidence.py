"""Bind historical import guards to authenticated retained bytes; no numerical work."""
from pathlib import Path
import importlib.util,json,shutil
SCRIPT=Path(__file__).resolve()
spec=importlib.util.spec_from_file_location('_lme049_retained_final_verifier',SCRIPT.with_name('verified_lme049_package.py'))
wrapper=importlib.util.module_from_spec(spec);spec.loader.exec_module(wrapper)
base=wrapper.base;package=base.DEFAULT_PACKAGE;model=package/'model'/base.MID
plan=base.read(package/'preparation.json');manifest_path=model/'results/result_manifest.json';manifest=base.read(manifest_path)
evidence=model/'results/diagnostics'/base.PREFIX
if plan.get('retained_engine_guard_binding'):raise ValueError('Already bound; use final verifier')
changes=[]
for name in ('ModelData.py','PPRCalculator.py'):
 live='tools/scientific_code/PPREstimation/'+name;old=plan['consumed_inputs'][live]
 retained=model/base.RETAINED/'code/engine'/name;actual=base.MODEL/base.RETAINED/'code/engine'/name
 if base.sha(retained)!=old or base.sha(actual)!=old:raise ValueError('Original import-time engine bytes not authenticated')
 if manifest['effective_flags']['engine_source_hashes'][name]!=old:raise ValueError('Actual execution identity differs')
 if plan['consumed_inputs'].get(base.relative(actual))!=old:raise ValueError('Retained exact source guard missing')
 changes.append({'historical_live_path':live,'historical_role':'Additional import-time current-engine byte equality check; not adopted execution source',
 'original_import_time_sha256':old,'current_shared_engine_sha256_at_binding':base.sha(base.ROOT/live),
 'retained_original_path':base.relative(actual),'retained_original_sha256':old,
 'disposition':'Historical live-file guard superseded by existing exact model-local retained-source guard. No flags/context/science changed.'})
 del plan['consumed_inputs'][live]
ledger={'schema_version':1,'operation':'Authorized retained-only historical engine binding',
 'authorization':'Root approved replacing only obsolete import-time live engine guards with authenticated original copies after unrelated concurrent engine changes.',
 'changes':changes,'actual_import_time_engine_sources':{
 name:{'path':(base.RETAINED/'code/engine'/name).as_posix(),'sha256':base.sha(model/base.RETAINED/'code/engine'/name)}
 for name in ('ModelData.py','PPRCalculator.py','utils.py')},
 'current_engine_scientifically_different':True,'new_engine_executed_or_used_for_coefficients':False,
 'numerical_equivalence_to_new_engine_claimed':False,'scientific_solve_performed':False,
 'retained_only_reexecution_supported':False,'runtime_initialization_guard_required':True,
 'unchanged':['canonical model','original engine sources','initialized runtime','source preprocessing recipe','all22 complete raw returns','MC draws','configuration evidence','coefficient cells','regional numeric cells'],
 'material_shared_changes_observed':['discard-return and external catch accounting','source detritus routing and known DET BA preservation','loader metadata and diagnostic flattening'],
 'original_importer_sha256':base.sha(base.SCRIPT),'binding_script_sha256':base.sha(SCRIPT)}
destination=evidence/'shared_engine_drift.json';base.write(destination,ledger)
base.write(base.RUN/'qa/retained_engine_binding.json',ledger)
copied=evidence/'bind_retained_engine_evidence.py';shutil.copyfile(SCRIPT,copied)
for source,role in [(destination,'shared_engine_drift'),(copied,'retained_engine_binding_script')]:
 manifest['method_coverage']['execution_evidence'][role]={'path':base.PREFIX+'/'+source.name,'sha256':base.sha(source)}
 item={'source':base.relative(source,package),'target':base.relative(base.MODEL/source.relative_to(model)),'sha256':base.sha(source)}
 plan['promotions'].append(item);plan['consumed_inputs'][item['target']]=base.fingerprint(base.ROOT/item['target'])
manifest['retained_engine_binding']={'ledger':base.PREFIX+'/shared_engine_drift.json','sha256':base.sha(destination),
 'numerical_equivalence_to_current_shared_engine':False,'reexecution_supported':False}
base.write(manifest_path,manifest)
for item in plan['promotions']:
 if item['source']==base.relative(manifest_path,package):item['sha256']=base.sha(manifest_path)
plan['retained_engine_guard_binding']={'ledger_sha256':base.sha(destination),'historical_live_guards':changes}
plan['consumed_inputs'][base.relative(SCRIPT)]=base.sha(SCRIPT)
base.write(package/'preparation.json',plan)
wrapper.verify_package(package)
print(json.dumps({'package':base.relative(package),'promotions':len(plan['promotions']),'verified':True,'scientific_solve_performed':False}),flush=True)

