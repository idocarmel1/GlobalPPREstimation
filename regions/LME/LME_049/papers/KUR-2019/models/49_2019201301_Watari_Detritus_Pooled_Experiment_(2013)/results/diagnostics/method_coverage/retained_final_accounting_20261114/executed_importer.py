"""Stage retained LME049 all22 returns without constructing or solving a model.

prepare() writes only this run's package. apply() requires the existing project
writer lock and publication transaction. Unsupported runtime preprocessing is
recorded honestly and must be guarded before publication.
"""
from __future__ import annotations
import argparse, ast, copy, gzip, hashlib, importlib.util, json, math, os, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
sys.dont_write_bytecode=True
SCRIPT=Path(__file__).resolve()
RUN=SCRIPT.parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').is_file())
MID='49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'
UNIT='LME_049'
MODEL=ROOT/'regions/LME/LME_049/papers/KUR-2019/models'/MID
REGION=ROOT/'regions/LME/LME_049/LME_049.xlsx'
RETAINED=Path('results/diagnostics/ee_floor_seabird_accounting_20261114')
SCENARIO=MODEL/RETAINED
PREFIX='method_coverage/retained_final_accounting_20261114'
DEFAULT_PACKAGE=RUN/'outputs/current_adoption'
sys.path.insert(0,str(ROOT))

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fingerprint(p):return sha(p) if Path(p).is_file() else None
def read(p):
 p=Path(p); raw=p.read_bytes()
 return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw.decode('utf-8-sig'))
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def relative(p,base=ROOT):return Path(p).resolve().relative_to(Path(base).resolve()).as_posix()
def package_dir(path=None):return Path(path).resolve() if path else DEFAULT_PACKAGE
def _check_inputs(inputs):
 for name,digest in inputs.items():
  p=(ROOT/name).resolve()
  if not p.is_relative_to(ROOT) or fingerprint(p)!=digest:raise ValueError('Consumed input changed: '+name)
def _load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
 sys.modules[name]=module;spec.loader.exec_module(module);return module
def _exact_source_numbers(path,book):
 helper=ROOT/'regions/LME/LME_038/papers/INDO-1999/models/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/model_validation/work/2026-11-14_152558_signoff/code/adopt_current_diagnostics.py'
 _load_module('_lme049_exact_source',helper)._exact_source_numbers(path,book)
 return helper
def _ast_module(path,omit=()):
 tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'))
 tree.body=[node for node in tree.body if getattr(node,'name',None) not in omit]
 return ast.dump(tree,include_attributes=False)
def _func_hash(path,name):
 tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'))
 node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
 return hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()

def authenticate():
 from tools.scientific_helpers.sppr import method_coverage as adapter
 settings=read(SCENARIO/'outputs/settings.json');summary=read(SCENARIO/'inventory/summary.json')
 if settings['canonical_sha256']!=sha(MODEL/'model.json'):raise ValueError('Canonical source changed')
 if settings['constructor']['use_ee_floor'] is not True or settings['constructor']['ee_floor']!=.1:raise ValueError('Wrong EE floor')
 if settings['routing_override']!={'group':3,'name':'Seabirds (all)','detritus_fraction':0,'unrouted_fraction':1,'destination':'other external export (existing det_export sink, not catch or a trophic group)'}:raise ValueError('Wrong scenario routing')
 files={MODEL/'model.json',SCRIPT}
 for branch in ('outputs','inventory'):
  index=SCENARIO/branch/'evidence_index.json';files.add(index)
  for item in read(index)['artifacts']:
   p=(index.parent/item['path']).resolve()
   if not p.is_relative_to(ROOT) or sha(p)!=item['sha256']:raise ValueError('Retained evidence changed: '+str(p))
   files.add(p)
 for name,digest in settings['engine_hashes'].items():
  p=SCENARIO/'code/engine'/name
  if sha(p)!=digest or summary['engine_hashes'][name]!=digest:raise ValueError('Retained engine identity differs: '+name)
  files.add(p)
 if summary['state_sha256']!=sha(SCENARIO/'outputs/initial_runtime.json.gz'):raise ValueError('Inventory runtime differs')
 if summary['mc_samples']!=100 or summary['mc_seed']!=20261114 or summary['fresh_draws'] is not True:raise ValueError('Unexpected retained MC configuration')
 keys=list(adapter.method_inventory())
 if summary['all_method_keys']!=keys or set(summary['methods'])!=set(keys):raise ValueError('Canonical inventory differs')
 for key,item in summary['methods'].items():
  if item['execution']!='returned' or item['negative_entries'] or item['nan_entries'] or item['infinite_entries'] or item['protected_runtime_unchanged'] is not True:raise ValueError('Unusable retained outcome: '+key)
 # The only current exporter change concerns a post-run symbolic display
 # balance check. The inventory invokes SPEC_BY_KEY.run directly, never this
 # table builder. All registry entries, callables, kwargs, and scope helpers
 # are AST-identical to the actually executed retained exporter.
 old=SCENARIO/'code/engine/create_PPRS_excel.py';current=adapter.ENGINE/'create_PPRS_excel.py'
 if _ast_module(old,('build_model_tables',))!=_ast_module(current,('build_model_tables',)):raise ValueError('Retained canonical method semantics changed')
 for name in adapter.ENGINE_FILES:
  if sha(adapter.ENGINE/name)!=settings['engine_hashes'][name]:raise ValueError('Current scientific engine differs from retained source')
 if not all(read(SCENARIO/'outputs/verification.json').values()):raise ValueError('Source scenario verification failed')
 if read(SCENARIO/'inventory/handoff_check.json')['complete'] is not True:raise ValueError('Incomplete all22 evidence')
 files.update(p for p in SCENARIO.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 files.update(adapter.ENGINE/name for name in (*adapter.ENGINE_FILES,'create_PPRS_excel.py'))
 return settings,summary,keys,files

def retained_outcomes(stage_model,settings,summary,keys):
 from tools.scientific_helpers.sppr import method_coverage as adapter
 # decode creates objects with __new__ only; no constructor, scientific
 # method, diagnostic, random draw, or MC executor is called here.
 sys.path.insert(0,str(SCENARIO/'code/engine'))
 codec_path=ROOT/'research/agents/regional_ge_integration_20260928/evidence/runtime_codec.py'
 codec=_load_module('_lme049_retained_codec',codec_path)
 from PPRCalculator import PPRCalculator
 state=codec.decode(read(SCENARIO/'outputs/initial_runtime.json.gz'))
 runtime=PPRCalculator.__new__(PPRCalculator);runtime.__dict__.update(state)
 names={int(k):v for k,v in runtime.seq2name.items()}
 if len(names)!=40 or names[2]!='Toothed whales (all)' or names[3]!='Seabirds (all)':raise ValueError('Runtime group identities differ')
 if runtime._det_fate.loc[3].sum()!=0 or runtime.EE[3]!=.1:raise ValueError('Retained routing/floor missing')
 if not math.isclose(runtime.det_export[3],runtime.M0[3]+runtime.egestion[3],rel_tol=1e-12):raise ValueError('Retained seabird export differs')
 outcomes={};frames={}
 direct={'new_GE':'GE','new_TE_EEfix':'TE','new_WithEgestion':'With_Egestion'}
 for key in keys:
  original=read(SCENARIO/'inventory'/(key+'.json.gz'))
  if original['execution']!='returned':raise ValueError('Original method did not return')
  frame=codec.decode(original['full_return']['values'][0])
  frames[key]=frame
  # Preserve the exact original return including symbolic expressions and raw
  # MC samples in copied evidence; this extraction view needs only coefficients.
  result=(frame,{})
  call={'method':key,'target':'retained_exporter_result','source_resolved':original['source_resolved'],'kwargs':{}}
  if key in direct:
   result=codec.decode(read(SCENARIO/'outputs'/(direct[key]+'_full_return.json')))
   if not result[1].equals(frame):raise ValueError('Direct and inventory source matrix differ: '+key)
   call['target']='diagnose_sppr'
  elif key.startswith('MC_'):
   result=codec.decode(original['full_return'])
   call['target']='monte_carlo_SPPR';call['kwargs']={'n_samples':100}
   if result[5]['n_accepted']!=100 or result[5]['n_rejected_negative'] or result[5]['n_rejected_diverged']:raise ValueError('MC acceptance changed')
  extracted=adapter._extract_result(runtime,call,result)
  if extracted['negative_entries']:raise ValueError('Negative scoped matrix')
  outcomes[key]={'status':'reused','reason':'Exact retained final-accounting output; no scientific execution during adoption.',
                 **extracted,'retained_warning_messages':original.get('warnings',[])}
  if key in direct:
   outcomes[key]['reason']+=' Original direct diagnostic '+result[0]['status']+'.'
  # Independently verify scope sum membership by retained source IDs, keeping
  # all-missing synthetic recipient rows and unsupported PP scope missing.
  for scope in ('all','inner','PP'):
   omitted=set(runtime.get_Import_seq()) if scope!='all' else set()
   if scope=='PP':omitted.update(runtime.get_DET_seq())
   selected=[c for c in frame.columns if c not in omitted]
   for gid,name in names.items():
    value=extracted['scopes'][scope].get(name)
    wanted=None
    if gid in frame.index and not(scope=='PP' and not original['source_resolved']):
     cells=[float(frame.loc[gid,c]) for c in selected]
     if any(math.isfinite(v) for v in cells):wanted=math.fsum(v for v in cells if math.isfinite(v))
    if (value is None)!=(wanted is None) or (value is not None and not math.isclose(value,wanted,rel_tol=1e-12,abs_tol=1e-12)):raise ValueError('Independent source-sum reconciliation failed')
 return outcomes,names,codec

def _protected(book):
 from tools.project_core.calculations import coverage
 from tools.project_core.workbooks.workbooks import digest_tables,overview
 settings=overview(book)
 return {'canonical_tables':coverage._preserved_inputs(book),'classic_complete':digest_tables(book.get('Classic PPR',{})),
         'reference_settings':{key:settings.get(key) for key in ('catch_basis','taxon_detail_year','transfer_efficiency','selected_model_id','selection_rationale')}}

def prepare(package_path=None):
 from tools.project_core.calculations import coverage
 from tools.project_core.calculations.regional import set_setting
 from tools.project_core.calculations.snapshots import dependencies
 from tools.project_core.calculations.ee_floor_migration import add_diagnostics
 from tools.project_core.workbooks.workbooks import read_book,overview,records
 from tools.scientific_helpers.sppr import method_coverage as adapter
 from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
 package=package_dir(package_path)
 if (package/'preparation.json').is_file():return verify_package(package)
 if package.exists() and any(package.iterdir()):raise ValueError('Partial staged package requires inspection')
 settings,summary,keys,inputs=authenticate()
 original=read_book(REGION);original_settings=overview(original)
 if original_settings['selected_model_id']!=MID or original_settings['results_model_id']!=MID:raise ValueError('Regional selection differs')
 protected=_protected(original)
 stage_model=package/'model'/MID;stage_region=package/'regional'/(UNIT+'.xlsx')
 stage_model.mkdir(parents=True);stage_region.parent.mkdir(parents=True)
 shutil.copyfile(REGION,stage_region);shutil.copyfile(MODEL/'model.json',stage_model/'model.json')
 shutil.copytree(SCENARIO,stage_model/RETAINED,ignore=shutil.ignore_patterns('__pycache__'))
 paths={'settings':RETAINED/'outputs/settings.json','recipe':RETAINED/'code/run_scenario.py',
        'initial_runtime':RETAINED/'outputs/initial_runtime.json.gz','inventory_recipe':RETAINED/'code/run_inventory.py',
        'inventory_summary':RETAINED/'inventory/summary.json'}
 marker={'kind':'retained_scenario','reexecution_supported':False,
         **{k:{'path':p.as_posix(),'sha256':sha(stage_model/p)} for k,p in paths.items()},
         'required_preprocessing':[{'group_seq':3,'group_name':'Seabirds (all)','field':'det_fate','operation':'set entire outgoing detritus fate row to 0',
         'destination':'external export through existing det_export sink'}],
         'reconstruction_limitation':'Shared adapter cannot replay the recorded source preprocessing; fail closed on any cache miss. Retained initial runtime and full original returns are authoritative.'}
 flags={'constructor':copy.deepcopy(settings['constructor']),'diagnostics':{},'methods':{},
        'mc':{'n_samples':100,'TE_error_percent':10,'TE_error_cut_percent':20,'seed':20261114},
        'runtime_initialization':marker,
        'engine_sources':{name:(RETAINED/'code/engine'/name).as_posix() for name in adapter.ENGINE_FILES},
        'engine_source_hashes':{name:settings['engine_hashes'][name] for name in adapter.ENGINE_FILES},
        'configuration_evidence':[{'relative_path':p.as_posix(),'sha256':sha(stage_model/p),'original_source_hash':sha(MODEL/'model.json')} for p in paths.values()]}
 # This identifies actual recorded settings; it is not an executed wrapper.
 flags=resolve_audited_configuration(stage_model,original,{'canonical_model_sha256':sha(MODEL/'model.json'),'effective_flags':flags})
 context=coverage._context(ROOT,stage_model/'model.json',flags)
 outcomes,names,codec=retained_outcomes(stage_model,settings,summary,keys)
 if {int(r['seq']):r['group_name'] for r in records(original,'Selected model groups','Groups')}!=names:raise ValueError('Regional group identities differ')
 evidence_dir=stage_model/'results/diagnostics'/PREFIX;evidence_dir.mkdir(parents=True)
 copied_adapter=evidence_dir/'executed_importer_adapter.py';shutil.copyfile(Path(adapter.__file__),copied_adapter)
 recipe_evidence={'schema_version':1,'operation':'Import retained outputs without execution','canonical_model_sha256':sha(MODEL/'model.json'),
  'actual_execution':{'scenario_settings':relative(SCENARIO/'outputs/settings.json',MODEL),'constructor':settings['constructor'],
  'engine_hashes':settings['engine_hashes'],'runtime_sha256':summary['state_sha256'],'inventory_recipe':relative(SCENARIO/'code/run_inventory.py',MODEL),
  'mc_n_samples':100,'mc_seed':20261114,'mc_GE_method_kwargs':None,'mc_TE_method_kwargs':{'fix_EE_0_cases':True},
  'mc_exclude_diverged':True,'mc_return_diagnostics':True,'mc_kind':'new','mc_TE_error_percent':10,'mc_TE_error_cut_percent':20},
  'current_registry_identity':context['code_identity']['create_PPRS_excel.py'],
  'registry_compatibility':'Module AST identical excluding build_model_tables; actual run used SPEC_BY_KEY.run, never build_model_tables. This omitted function changed only symbolic display balance checking after calculation.',
  'scientific_execution_by_adoption':False,'raw_return_files_copied_byte_for_byte':True,'retained_runtime_reconstructed_with_new_only':True,
  'display_exclusion':{'group_seq':2,'group_name':'Toothed whales (all)','applies_to':'published displayed calculations through registered researcher review; does not delete model or diagnostic rows'},
  'source_inputs_unchanged':True,'current_cache_miss_behavior':'requires fail-closed runtime_initialization guard before apply'}
 write(evidence_dir/'adoption_provenance.json',recipe_evidence)
 for key,outcome in outcomes.items():
  cert={'schema_version':1,'evidence_kind':'retained_final_accounting_all22_adoption','method':key,'context':context,
        'original_full_return':{'path':(RETAINED/'inventory'/(key+'.json.gz')).as_posix(),'sha256':sha(SCENARIO/'inventory'/(key+'.json.gz'))},
        'recipe':recipe_evidence,'extraction':copy.deepcopy(outcome),'scientific_execution_performed_by_adoption':False}
  evidence=adapter._save(evidence_dir/(key+'.adopted.json.gz'),cert);evidence['path']=PREFIX+'/'+evidence['path'];outcome['evidence']=evidence
 inputs.update([REGION,MODEL/'sppr_source.xlsx',MODEL/'results/regional_snapshot.xlsx',MODEL/'results/result_manifest.json',
                ROOT/'research/agents/regional_ge_integration_20260928/evidence/runtime_codec.py',
                ROOT/'tools/scientific_helpers/sppr/configuration.py'])
 inputs.update(ROOT/'tools/project_core'/name for name in coverage._arithmetic_identity())
 backups={}
 for source in (REGION,MODEL/'sppr_source.xlsx',MODEL/'results/regional_snapshot.xlsx',MODEL/'results/result_manifest.json'):
  if source.is_file():
   dest=stage_model/'results/diagnostics/ee_floor/pre_adoption_20261114'/source.name
   dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
   backups[relative(source)]={'path':relative(dest,stage_model),'sha256':sha(source)}
 book=copy.deepcopy(original)
 coverage._apply_outcomes(book,MID,outcomes,keys,migration=True)
 ledger=codec.decode(read(SCENARIO/'outputs/ee_floor_ledger.json'))
 add_diagnostics(book,{'info':read(SCENARIO/'outputs/ee_floor_info.json'),'ledger':[dict(row,group_seq=int(i)) for i,row in ledger.to_dict('index').items()]})
 set_setting(book,'sppr_engine_hashes',json.dumps(settings['engine_hashes']))
 print('LME_049: recalculating retained regional arithmetic only',flush=True)
 coverage._arithmetic(book,REGION,MODEL/'model.json',flags,original,migration=True,invalidated_methods=tuple(keys))
 saved=coverage._save_calculation(stage_region,book,MODEL/'model.json',flags,copy.deepcopy(book),migration=True,invalidated_methods=tuple(keys))
 if _protected(saved)!=protected:raise ValueError('Protected regional input changed')
 coverage._update_source(stage_model/'sppr_source.xlsx',saved,outcomes,replace_methods=keys)
 inputs.add(_exact_source_numbers(stage_model/'sppr_source.xlsx',saved))
 set_setting(saved,'results_source_sha256',sha(stage_model/'sppr_source.xlsx'))
 saved=coverage._save_calculation(stage_region,saved,MODEL/'model.json',flags,copy.deepcopy(saved),migration=True,invalidated_methods=tuple(keys))
 snapshot=stage_model/'results/regional_snapshot.xlsx';shutil.copyfile(stage_region,snapshot)
 hashes=coverage._method_rows(saved)[1]
 for key in keys:outcomes[key]['group_rows_sha256']=hashes[key]
 execution={'adoption_provenance':{'path':PREFIX+'/adoption_provenance.json','sha256':sha(evidence_dir/'adoption_provenance.json')},
            'actual_importer_adapter':{'path':PREFIX+'/executed_importer_adapter.py','sha256':sha(copied_adapter)}}
 manifest={'schema_version':1,'unit_id':UNIT,'model_id':MID,'snapshot_selected_model_id':MID,'timestamp':datetime.now(timezone.utc).isoformat(),
 'canonical_model_sha256':sha(MODEL/'model.json'),'present_canonical_model_sha256':sha(MODEL/'model.json'),
 'snapshot_sha256':sha(snapshot),'coefficient_source_sha256':sha(stage_model/'sppr_source.xlsx'),'effective_flags':flags,
 'code_identity':{k:v for k,v in context['code_identity'].items() if k!='create_PPRS_excel.py'},
 'actual_execution_engine_identity':settings['engine_hashes'],'provenance_status':'Authenticated retained final-accounting all22 outputs and original MC draws imported without new scientific execution.',
 'dependencies':dependencies(saved),'artifacts':{'snapshot':'regional_snapshot.xlsx','model':'../model.json','coefficients':'../sppr_source.xlsx'},
 'historical_package_backup':backups,'method_coverage':{'schema_version':1,'expected_methods':keys,'context':context,'methods':outcomes,
 'execution_evidence':execution,'arithmetic_code_identity':coverage._arithmetic_identity(),'protected_inputs_sha256':coverage._preserved_inputs(saved)}}
 write(stage_model/'results/result_manifest.json',manifest)
 promotions=[{'source':relative(stage_region,package),'target':relative(REGION),'sha256':sha(stage_region)}]
 input_hashes={relative(p):fingerprint(p) for p in inputs}
 for source in sorted(p for p in stage_model.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
  if source==stage_model/'model.json':continue
  target=MODEL/source.relative_to(stage_model)
  # Existing immutable retained science is authenticated, not rewritten.
  if fingerprint(target)==sha(source):continue
  promotions.append({'source':relative(source,package),'target':relative(target),'sha256':sha(source)})
  input_hashes.setdefault(relative(target),fingerprint(target))
 _check_inputs(input_hashes)
 plan={'schema_version':1,'unit_id':UNIT,'model_id':MID,'package':relative(package),'prepared_utc':datetime.now(timezone.utc).isoformat(),
 'consumed_inputs':input_hashes,'context':context,'expected_methods':keys,'protected_inputs':protected,'promotions':promotions,
 'method_outcomes':{k:{'status':v['status'],'reason':v.get('reason'),'evidence':v['evidence']} for k,v in outcomes.items()},
 'adapter_extraction_ast_sha256':_func_hash(Path(adapter.__file__),'_extract_result'),
 'adapter_sha256_at_import':sha(copied_adapter),'scientific_solve_performed':False,'numerical_adoption_performed':False,
 'apply_requirement':'Installed shared adapter must reject runtime_initialization in _constructor and _load before any engine access.'}
 write(package/'preparation.json',plan)
 return verify_package(package)

def _guard_installed():
 from unittest.mock import patch
 from tools.scientific_helpers.sppr import method_coverage as adapter
 for fn,args in ((adapter._constructor,({'runtime_initialization':{'kind':'retained_scenario','reexecution_supported':False}},MODEL/'model.json')),
                 (adapter._load,(MODEL/'model.json',{}, {'runtime_initialization':{'kind':'retained_scenario','reexecution_supported':False}}))):
  with patch.object(adapter,'_engine',side_effect=AssertionError('Engine must not load')),patch.object(adapter,'_audited_engine',side_effect=AssertionError('Engine must not load')):
   try:fn(*args)
   except ValueError as exc:
    if 'runtime' not in str(exc).lower():raise ValueError('Runtime guard lacks explicit reason') from exc
   else:raise ValueError('Runtime initialization fail-closed guard is not installed')
 return True

def verify_package(package_path=None,check_inputs=True):
 from tools.project_core.calculations import coverage
 from tools.project_core.calculations.regional import result_hash
 from tools.project_core.workbooks.workbooks import read_book,overview,input_hash,records,rows
 from tools.scientific_helpers.sppr import method_coverage as adapter
 from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
 package=package_dir(package_path);plan=read(package/'preparation.json')
 stage_model=package/'model'/MID;regional=package/'regional'/(UNIT+'.xlsx')
 if check_inputs:_check_inputs(plan['consumed_inputs'])
 for item in plan['promotions']:
  p=(package/item['source']).resolve()
  if not p.is_relative_to(package) or sha(p)!=item['sha256']:raise ValueError('Staged promotion changed')
 if _func_hash(Path(adapter.__file__),'_extract_result')!=plan['adapter_extraction_ast_sha256']:raise ValueError('Actual extraction helper changed')
 book=read_book(regional);manifest=read(stage_model/'results/result_manifest.json')
 if _protected(book)!=plan['protected_inputs']:raise ValueError('Protected workbook inputs changed')
 if overview(book)['calculation_input_sha256']!=input_hash(book) or overview(book)['calculation_result_sha256']!=result_hash(book):raise ValueError('Stale staged hashes')
 flags=resolve_audited_configuration(stage_model,book,manifest);context=coverage._context(ROOT,stage_model/'model.json',flags)
 if not coverage._same_context(context,plan['context']):raise ValueError('Audited configuration differs')
 if not coverage._package_cache_valid(stage_model,regional,manifest,context,plan['expected_methods']):raise ValueError('Coverage cache failed')
 if not coverage._source_matches(stage_model,book,plan['expected_methods']):raise ValueError('Source workbook mismatch')
 coeff=records(book,'Selected model groups','Group SPPR')
 if len(coeff)!=40*3*22:raise ValueError('Incomplete all22 coefficient inventory')
 for row in coeff:
  wanted=manifest['method_coverage']['methods'][row['method']]['scopes'][row['scope']].get(row['group'])
  # openpyxl's prior exact numbers may be retained only at its canonical .16g
  # equality. Every changed value is serialized from the retained output.
  from tools.project_core.workbooks.workbooks import digest_tables
  if digest_tables(row['sppr'])!=digest_tables(wanted):raise ValueError('Coefficient missingness/value mismatch')
 original=read_book(REGION)
 if _protected(original)!=plan['protected_inputs']:raise ValueError('Current independent inputs changed')
 prior={tuple(r[:6]):r[6] for r in rows(original,'PPR','Annual')}
 for row in rows(book,'PPR','Annual'):
  previous=prior.get(tuple(row[:6]))
  if previous and previous!='ok' and not str(row[6]).startswith(str(previous)):raise ValueError('Existing diagnostic restriction lost')
 try:guard=_guard_installed()
 except (ValueError,AssertionError):guard=False
 qa={'passed':True,'coefficient_rows':len(coeff),'missing_coefficients':sum(r['sppr'] is None for r in coeff),
     'protected_inputs_exact':True,'canonical_cache_valid':True,'raw_mc_draws_unchanged':True,'scientific_solve_performed':False,
     'adoption_performed':False,'runtime_reexecution_supported':False,'fail_closed_guard_installed':guard,
     'ready_for_apply':guard,'actual_execution_exporter_sha256':manifest['actual_execution_engine_identity']['create_PPRS_excel.py'],
     'current_extraction_registry_sha256':context['code_identity']['create_PPRS_excel.py'],'staged_regional_sha256':sha(regional)}
 write(RUN/'qa/package_verification.json',qa)
 return plan

def apply(publication,package_path=None):
 from tools.project_core.registry.publication import _ACTIVE,publication_write
 from tools.project_core.calculations import coverage
 if publication not in _ACTIVE.get() or publication.root!=ROOT:raise ValueError('Active publication transaction required')
 lock=ROOT/'.project-write.lock'
 if not lock.is_file() or lock.read_text().strip()!=str(os.getpid()):raise ValueError('Project writer lock required')
 _guard_installed()
 package=package_dir(package_path);plan=verify_package(package,check_inputs=False)
 targets={p['target'] for p in plan['promotions']}
 _check_inputs({k:v for k,v in plan['consumed_inputs'].items() if k not in targets})
 if all(fingerprint(ROOT/p['target'])==p['sha256'] for p in plan['promotions']):
  return {'status':'already_applied','changed_units':[UNIT],'written_paths':[],'written_hashes':{}}
 _check_inputs(plan['consumed_inputs'])
 for item in plan['promotions']:
  source,target=package/item['source'],ROOT/item['target']
  with publication_write(target,fingerprint=item['sha256']):
   coverage._write_bytes(target,source.read_bytes(),expected_sha256=plan['consumed_inputs'][item['target']])
 manifest=read(MODEL/'results/result_manifest.json')
 if not coverage._package_cache_valid(MODEL,REGION,manifest,plan['context'],plan['expected_methods']):raise ValueError('Installed cache failed')
 return {'status':'applied','changed_units':[UNIT],'written_paths':[str(ROOT/p['target']) for p in plan['promotions']],
 'written_hashes':{str(ROOT/p['target']):p['sha256'] for p in plan['promotions']}}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','verify']);parser.add_argument('--package',type=Path)
 args=parser.parse_args();result=prepare(args.package) if args.command=='prepare' else verify_package(args.package)
 print(json.dumps({'package':result['package'],'promotions':len(result['promotions']),'methods':len(result['expected_methods']),'scientific_solve_performed':False}),flush=True)

