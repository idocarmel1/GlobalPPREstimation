"""Post-run verification wrapper for the unchanged retained-output importer.

This source did not produce the staged coefficients. certify() adds the exact
executed importer bytes and this verification wrapper to provenance, without
changing any workbook or coefficient bytes.
"""
from __future__ import annotations
import argparse, copy, importlib.util, json, shutil, os
from pathlib import Path
SCRIPT=Path(__file__).resolve()
spec=importlib.util.spec_from_file_location('_lme049_executed_importer',SCRIPT.with_name('stage_lme049_adoption.py'))
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
DEFAULT_PACKAGE=base.DEFAULT_PACKAGE
meta=base._load_module("_lme049_metadata_reconciliation",SCRIPT.with_name("metadata_reconciliation.py"))

def _assert_runtime_marker(package,plan):
 from tools.project_core.calculations import coverage
 from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
 model=package/'model'/base.MID
 manifest=base.read(model/'results/result_manifest.json')
 settings=base.read(model/base.RETAINED/'outputs/settings.json')
 summary=base.read(model/base.RETAINED/'inventory/summary.json')
 paths={'settings':base.RETAINED/'outputs/settings.json','recipe':base.RETAINED/'code/run_scenario.py',
        'initial_runtime':base.RETAINED/'outputs/initial_runtime.json.gz','inventory_recipe':base.RETAINED/'code/run_inventory.py',
        'inventory_summary':base.RETAINED/'inventory/summary.json'}
 expected={'kind':'retained_scenario','reexecution_supported':False,
           **{k:{'path':p.as_posix(),'sha256':base.sha(model/p)} for k,p in paths.items()},
           'required_preprocessing':[{'group_seq':3,'group_name':'Seabirds (all)','field':'det_fate','operation':'set entire outgoing detritus fate row to 0',
           'destination':'external export through existing det_export sink'}],
           'reconstruction_limitation':'Shared adapter cannot replay the recorded source preprocessing; fail closed on any cache miss. Retained initial runtime and full original returns are authoritative.'}
 book=coverage._settings_book(package/'regional'/(base.UNIT+'.xlsx'))
 flags=resolve_audited_configuration(model,book,manifest)
 for recorded in (flags,manifest['effective_flags'],manifest['method_coverage']['context']['flags'],plan['context']['flags']):
  if recorded.get('runtime_initialization')!=expected:raise ValueError('Resolved retained-scenario marker differs or is missing')
  if recorded.get('constructor')!=settings['constructor']:raise ValueError('Constructor differs from actual executed settings')
  if recorded.get('mc')!={'n_samples':100,'TE_error_percent':10,'TE_error_cut_percent':20,'seed':20261114}:raise ValueError('Retained MC settings differ')
  for p in paths.values():
   wanted={'relative_path':p.as_posix(),'sha256':base.sha(model/p),'original_source_hash':base.sha(model/'model.json')}
   if wanted not in recorded.get('configuration_evidence',[]):raise ValueError('Missing authenticated runtime/recipe evidence')
 if summary['state_sha256']!=expected['initial_runtime']['sha256']:raise ValueError('Retained inventory runtime is different')
 if settings['canonical_sha256']!=base.sha(model/'model.json'):raise ValueError('Retained scenario source changed')
 return {'runtime_marker_exact':True,'runtime_recipe_settings_bound_to_configuration_evidence':True,
         'constructor_matches_actual_execution':True,'mc_settings_match_actual_execution':True}

def certify(package_path=None):
 package=base.package_dir(package_path);plan=base.read(package/'preparation.json')
 if plan.get('postrun_verifier'):return verify_package(package)
 base._check_inputs(plan['consumed_inputs'])
 for item in plan['promotions']:
  if base.sha(package/item['source'])!=item['sha256']:raise ValueError('Staged promotion changed')
 _assert_runtime_marker(package,plan)
 model=package/'model'/base.MID;manifest_path=model/'results/result_manifest.json';manifest=base.read(manifest_path)
 old_plan=base.sha(package/'preparation.json');old_manifest=base.sha(manifest_path)
 ledger_path,ledger=meta.reconcile(base,package,plan,manifest)
 evidence_dir=model/'results/diagnostics'/base.PREFIX
 added=[ledger_path]
 for source,name,role in ((base.SCRIPT,'executed_importer.py','executed_retained_output_importer'),
   (SCRIPT,'postrun_verifier.py','postrun_verification_only'),
   (SCRIPT.with_name('metadata_reconciliation.py'),'metadata_reconciliation.py','authorized_metadata_postprocessing_only')):
  destination=evidence_dir/name;shutil.copyfile(source,destination);added.append(destination)
  plan['consumed_inputs'][base.relative(source)]=base.sha(source)
  manifest['method_coverage']['execution_evidence'][role]={'path':base.PREFIX+'/'+name,'sha256':base.sha(destination)}
 manifest['method_coverage']['execution_evidence']['metadata_reconciliation']={'path':base.PREFIX+'/metadata_reconciliation.json','sha256':base.sha(ledger_path)}
 manifest['postrun_verification']={'executed_importer_sha256':base.sha(base.SCRIPT),'postrun_verifier_sha256':base.sha(SCRIPT),
 'original_preparation_sha256':old_plan,'original_manifest_sha256':old_manifest,'numeric_cells_or_coefficient_source_changed':False,
 'role':'Authorized textual metadata reconciliation and additional invariant assertions after coefficient staging.'}
 base.write(manifest_path,manifest)
 for source in added:
  item={'source':base.relative(source,package),'target':base.relative(base.MODEL/source.relative_to(model)),'sha256':base.sha(source)}
  plan['promotions'].append(item);plan['consumed_inputs'][item['target']]=base.fingerprint(base.ROOT/item['target'])
 for item in plan['promotions']:item['sha256']=base.sha(package/item['source'])
 plan['postrun_verifier']={'path':base.relative(SCRIPT),'sha256':base.sha(SCRIPT),'original_preparation_sha256':old_plan,
 'executed_importer_sha256':base.sha(base.SCRIPT),'metadata_reconciliation_sha256':base.sha(ledger_path),
 'metadata_script_sha256':base.sha(SCRIPT.with_name('metadata_reconciliation.py')),
 'numeric_xml_sha256_unchanged':ledger['preserved']['numeric_xml_sha256_before'],
 'source_workbook_sha256_unchanged':ledger['preserved']['source_workbook_sha256']}
 base.write(package/'preparation.json',plan)
 return verify_package(package)

def verify_package(package_path=None,check_inputs=True):
 from tools.project_core.calculations import coverage
 from tools.project_core.calculations.regional import result_hash
 from tools.project_core.workbooks.workbooks import read_book,overview,input_hash,records,rows,digest_tables
 from tools.scientific_helpers.sppr import method_coverage as adapter
 from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
 package=base.package_dir(package_path);plan=base.read(package/'preparation.json')
 model=package/'model'/base.MID;regional=package/'regional'/(base.UNIT+'.xlsx')
 if check_inputs:base._check_inputs(plan['consumed_inputs'])
 for item in plan['promotions']:
  path=(package/item['source']).resolve()
  if not path.is_relative_to(package) or base.sha(path)!=item['sha256']:raise ValueError('Staged promotion changed')
 if base._func_hash(Path(adapter.__file__),'_extract_result')!=plan['adapter_extraction_ast_sha256']:raise ValueError('Original extraction helper changed')
 checks=_assert_runtime_marker(package,plan);post=plan.get('postrun_verifier')
 if not post or post['sha256']!=base.sha(SCRIPT) or post['executed_importer_sha256']!=base.sha(base.SCRIPT) or post['metadata_script_sha256']!=base.sha(SCRIPT.with_name('metadata_reconciliation.py')):raise ValueError('Post-run verifier/original importer provenance changed')
 if meta.numeric_xml(regional)!=post['numeric_xml_sha256_unchanged'] or base.sha(model/'sppr_source.xlsx')!=post['source_workbook_sha256_unchanged']:raise ValueError('Numeric cells or source changed')
 ledger_path=model/'results/diagnostics'/base.PREFIX/'metadata_reconciliation.json'
 if base.sha(ledger_path)!=post['metadata_reconciliation_sha256']:raise ValueError('Reconciliation ledger changed')
 ledger=base.read(ledger_path);book=read_book(regional);manifest=base.read(model/'results/result_manifest.json')
 if base._protected(book)!=plan['protected_inputs']:raise ValueError('Protected workbook inputs changed')
 if overview(book)['calculation_input_sha256']!=input_hash(book) or overview(book)['calculation_result_sha256']!=result_hash(book):raise ValueError('Stale staged hashes')
 flags=resolve_audited_configuration(model,book,manifest);context=coverage._context(base.ROOT,model/'model.json',flags)
 if not coverage._same_context(context,plan['context']):raise ValueError('Scientific context changed')
 if not coverage._package_cache_valid(model,regional,manifest,context,plan['expected_methods']):raise ValueError('Canonical cache failed')
 if not coverage._source_matches(model,book,plan['expected_methods']):raise ValueError('Source workbook mismatch')
 coeff=records(book,'Selected model groups','Group SPPR')
 if len(coeff)!=2640:raise ValueError('Incomplete all22 inventory')
 mismatches=[]
 for row in coeff:
  wanted=manifest['method_coverage']['methods'][row['method']]['scopes'][row['scope']].get(row['group'])
  if digest_tables(row['sppr'])!=digest_tables(wanted):raise ValueError('Coefficient or missingness differs')
  if row['sppr']!=wanted:mismatches.append({'method':row['method'],'scope':row['scope'],'group':row['group'],'stored':row['sppr'],'retained_output':wanted})
 original=read_book(base.REGION)
 if base._protected(original)!=plan['protected_inputs']:raise ValueError('Current independent inputs changed')
 bykey={tuple(row[:6]):row for row in rows(book,'PPR','Annual')}
 authorized={tuple(row['key']):row for row in ledger['annual_status_changes']}
 for row in rows(original,'PPR','Annual'):
  current=bykey.get(tuple(row[:6]))
  if current is None:continue
  change=authorized.get(tuple(row[:6]))
  if change:
   if row[6]!=change['before'] or current[6]!=change['after']:raise ValueError('Unauthorized historical restriction replacement')
  elif row[6] and row[6]!='ok' and not str(current[6]).startswith(str(row[6])):raise ValueError('Applicable historical restriction lost')
 for entry in ledger['overview_changes']:
  if overview(book).get(entry['field'])!=entry['after']:raise ValueError('Reconciled Overview differs')
 if overview(book)['selection_rationale']!=overview(original)['selection_rationale']:raise ValueError('Researcher selection changed')
 if len(authorized)!=189:raise ValueError('Wrong status reconciliation scope')
 try:guard=base._guard_installed()
 except (ValueError,AssertionError):guard=False
 qa={'passed':True,'coefficient_rows':len(coeff),'finite_coefficients':sum(r['sppr'] is not None for r in coeff),
 'missing_coefficients':sum(r['sppr'] is None for r in coeff),'protected_inputs_exact':True,'numeric_xml_exact':True,
 'canonical_cache_valid':True,'raw_mc_draws_unchanged':True,'scientific_solve_performed':False,'adoption_performed':False,
 'runtime_reexecution_supported':False,'fail_closed_guard_installed':guard,'ready_for_apply':guard,
 'reconciled_status_rows':189,'unsupported_rows_per_original_method_preserved':18,
 'production_eligible':overview(book).get('production_eligible'),'production_eligibility_note':overview(book)['production_eligibility_note'],
 'coefficient_float_roundtrip_equivalences':mismatches,'staged_regional_sha256':base.sha(regional),**checks}
 base.write(base.RUN/'qa/package_verification.json',qa)
 return plan

def apply(publication,package_path=None):
 from tools.project_core.registry.publication import _ACTIVE,publication_write
 from tools.project_core.calculations import coverage
 if publication not in _ACTIVE.get() or publication.root!=base.ROOT:raise ValueError('Active publication transaction required')
 lock=base.ROOT/'.project-write.lock'
 if not lock.is_file() or lock.read_text().strip()!=str(os.getpid()):raise ValueError('Project writer lock required')
 base._guard_installed()
 package=base.package_dir(package_path);plan=verify_package(package,check_inputs=False)
 targets={p['target'] for p in plan['promotions']}
 base._check_inputs({k:v for k,v in plan['consumed_inputs'].items() if k not in targets})
 if all(base.fingerprint(base.ROOT/p['target'])==p['sha256'] for p in plan['promotions']):
  return {'status':'already_applied','changed_units':[base.UNIT],'written_paths':[],'written_hashes':{}}
 base._check_inputs(plan['consumed_inputs'])
 for item in plan['promotions']:
  source,target=package/item['source'],base.ROOT/item['target']
  with publication_write(target,fingerprint=item['sha256']):
   coverage._write_bytes(target,source.read_bytes(),expected_sha256=plan['consumed_inputs'][item['target']])
 manifest=base.read(base.MODEL/'results/result_manifest.json')
 if not coverage._package_cache_valid(base.MODEL,base.REGION,manifest,plan['context'],plan['expected_methods']):raise ValueError('Installed cache failed')
 return {'status':'applied','changed_units':[base.UNIT],'written_paths':[str(base.ROOT/p['target']) for p in plan['promotions']],
 'written_hashes':{str(base.ROOT/p['target']):p['sha256'] for p in plan['promotions']}}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['certify','verify']);parser.add_argument('--package',type=Path)
 args=parser.parse_args();plan=certify(args.package) if args.command=='certify' else verify_package(args.package)
 print(json.dumps({'package':plan['package'],'promotions':len(plan['promotions']),'methods':len(plan['expected_methods']),'scientific_solve_performed':False}),flush=True)

