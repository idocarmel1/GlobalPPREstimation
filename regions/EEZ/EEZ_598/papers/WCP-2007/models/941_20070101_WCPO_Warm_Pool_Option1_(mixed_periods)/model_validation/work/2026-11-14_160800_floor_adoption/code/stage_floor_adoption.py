"""Stage exact retained WCPO floor-0.1 returns; no scientific solves or adoption.

apply() is deliberately callable only inside the coordinator's publication
transaction and writer lock. Original source evidence and input bytes remain
separate from this explicit cross-region adoption.
"""
from __future__ import annotations
import argparse, copy, gzip, hashlib, importlib.util, json, math, os, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve()
RUN = SCRIPT.parents[1]
ROOT = next(p for p in RUN.parents if (p / 'Project.xlsx').is_file())
MID = '941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
UNITS = ('HS_071', 'EEZ_598', 'EEZ_941')
METHODS = {'new_GE':'GE', 'new_TE_EEfix':'TE', 'new_WithEgestion':'With Egestion'}
DONOR = ROOT / 'regions/EEZ/EEZ_941/papers/WCP-2007/models' / MID
DIRECT = DONOR / 'model_validation/evidence/ee_floor_on'
RETAINED = Path('results/diagnostics/ee_floor/retained_direct_20261114')
PREFIX = 'method_coverage/retained_floor_20261114'
sys.path.insert(0, str(ROOT))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fingerprint(p):
    return sha(p) if Path(p).is_file() else None

def read(p):
    p = Path(p)
    return json.loads(gzip.decompress(p.read_bytes())) if p.suffix == '.gz' else json.loads(p.read_text(encoding='utf-8-sig'))

def write(p, v):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')

def relative(p, base=ROOT):
    return Path(p).resolve().relative_to(Path(base).resolve()).as_posix()

def model_dir(unit):
    if unit not in UNITS: raise ValueError('Unexpected region')
    return ROOT / 'regions' / unit.split('_')[0] / unit / 'papers/WCP-2007/models' / MID

def region_path(unit):
    return ROOT / 'regions' / unit.split('_')[0] / unit / (unit+'.xlsx')

def package_dir(unit):
    return RUN / 'outputs' / unit

def check_inputs(inputs):
    for name, digest in inputs.items():
        p = (ROOT/name).resolve()
        if not p.is_relative_to(ROOT) or fingerprint(p) != digest:
            raise ValueError('Consumed input changed: '+name)

def near(a,b):
    return math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-12)

def verify_direct():
    """Reconcile retained matrices independently of their historical QA flags."""
    provenance = read(DIRECT/'run_provenance.json')
    source_hash = sha(DONOR/'model.json')
    if provenance['canonical_model_sha256'] != source_hash: raise ValueError('Donor canonical input changed')
    inputs = {SCRIPT, DONOR/'model.json', DIRECT/'artifact_manifest.json'}
    for item in read(DIRECT/'artifact_manifest.json')['files']:
        p = (DIRECT/item['path']).resolve()
        if not p.is_relative_to(DIRECT) or sha(p) != item['sha256'] or p.stat().st_size != item['bytes']:
            raise ValueError('Retained direct evidence changed: '+item['path'])
        inputs.add(p)
    flags = provenance['flags']
    if flags['constructor']['use_ee_floor'] is not True or flags['constructor']['ee_floor'] != .1:
        raise ValueError('Donor is not floor .1')
    for name,path in flags['engine_sources'].items():
        p = DONOR/path
        if sha(p) != flags['engine_source_hashes'][name]: raise ValueError('Base-loader bytes changed')
        inputs.add(p)
    if sha(DONOR/flags['calculation_engine_source']) != flags['calculation_engine_sha256']:
        raise ValueError('Floor engine changed')
    checks = read(DIRECT/'verification.json')
    if checks['canonical_model_sha256'] != source_hash or checks['protected_files_unchanged_at_verification'] is not True:
        raise ValueError('Retained direct verification identity failed')
    axes = read(DIRECT/'group_axes.json')
    names = {r['id']:r['name'] for r in axes}
    if len(names)!=32 or len(set(names.values()))!=32: raise ValueError('Group identities ambiguous')
    runtime = read(DIRECT/'runtime_initialized.json.gz')
    catches = runtime['catch']['frame']
    catches = {gid:row[0] for gid,row in zip(catches['index'],catches['data'])}
    expected_columns = [r['id'] for r in axes if r['type'] in {'Import','DET','PP'}]
    outcomes = {}
    for key,option in METHODS.items():
        result = read(DIRECT/(key+'_full_return.json.gz'))
        matrix = read(DIRECT/(key+'_SPPR_matrix.json'))
        if matrix != result['source_matrix'] or result['status']!='ok' or result['negative_entries']:
            raise ValueError('Direct output mismatch: '+key)
        if matrix['index'] != list(names) or matrix['columns'] != expected_columns:
            raise ValueError('Direct matrix axes differ')
        if any(any(row) for values in matrix['masks'].values() for row in values):
            raise ValueError('Nonfinite direct matrix')
        if len(result['return']['items'])!=4 or result['runtime_before']!=result['runtime_after']:
            raise ValueError('Incomplete return or changed direct runtime')
        if result['runtime_before']!=runtime: raise ValueError('Direct initialized runtime differs')
        for scope in ('all','inner','PP'):
            ids = expected_columns if scope=='all' else [r['id'] for r in axes if r['type'] in ({'DET','PP'} if scope=='inner' else {'PP'})]
            values = result['scopes'][scope]
            if set(values)!=set(names.values()): raise ValueError('Missing direct scope group')
            for gid,row in zip(matrix['index'],matrix['data']):
                if any(not isinstance(x,(int,float)) or not math.isfinite(x) or x<0 for x in row):
                    raise ValueError('Invalid direct coefficient')
                if not near(math.fsum(row[matrix['columns'].index(i)] for i in ids),values[names[gid]]):
                    raise ValueError('Scope sum mismatch')
            footprint = {'all':'ppr_all','inner':'ppr_inner','PP':'ppr_pp_only'}[scope]
            if not near(math.fsum(catches[gid]*values[name] for gid,name in names.items()),result['diagnostics']['footprint'][footprint]):
                raise ValueError('Direct footprint mismatch')
        if result['diagnostics']['config']['use_ee_floor'] is not True or result['diagnostics']['config']['ee_floor']!=.1:
            raise ValueError('Direct diagnostics floor identity differs')
        outcomes[key]=result
    return provenance, names, runtime, outcomes, inputs

def exact_source_numbers(path,book):
    source = ROOT/'regions/LME/LME_038/papers/INDO-1999/models/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/model_validation/work/2026-11-14_152558_signoff/code/adopt_current_diagnostics.py'
    spec=importlib.util.spec_from_file_location('_exact_adoption_numbers',source)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module._exact_source_numbers(path,book)

def prepare(unit):
    from tools.project_core.calculations import coverage
    from tools.project_core.calculations.regional import set_setting
    from tools.project_core.calculations.snapshots import dependencies
    from tools.project_core.calculations.ee_floor_migration import add_diagnostics
    from tools.project_core.workbooks.workbooks import read_book, overview, records
    from tools.scientific_helpers.sppr import method_coverage as adapter
    from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
    package=package_dir(unit); model=model_dir(unit); region=region_path(unit)
    if (package/'preparation.json').is_file(): return verify_package(unit)
    if package.exists() and any(package.iterdir()): raise ValueError('Partial staged package needs inspection: '+str(package))
    provenance,names,runtime,direct,inputs=verify_direct()
    original=read_book(region); settings=overview(original)
    if settings['selected_model_id']!=MID or settings['results_model_id']!=MID or sha(model/'model.json')!=provenance['canonical_model_sha256']:
        raise ValueError('Target selection/input differs: '+unit)
    if {int(r['seq']):r['group_name'] for r in records(original,'Selected model groups','Groups')}!=names:
        raise ValueError('Target group identity differs: '+unit)
    if set(r['method'] for r in records(original,'Selected model groups','Group SPPR'))!=set(METHODS):
        raise ValueError('Unexpected existing method inventory; do not overwrite')
    protected=coverage._preserved_inputs(original)
    stage_model=package/'model';stage_region=package/'regional'/(unit+'.xlsx')
    stage_model.mkdir(parents=True);stage_region.parent.mkdir(parents=True)
    shutil.copyfile(region,stage_region);shutil.copyfile(model/'model.json',stage_model/'model.json')
    retained=stage_model/RETAINED
    shutil.copytree(DIRECT,retained)
    base=retained/'base_engine';base.mkdir()
    flags=copy.deepcopy(provenance['flags'])
    for name,old in flags['engine_sources'].items():
        shutil.copyfile(DONOR/old,base/name)
    flags['engine_sources']={name:(RETAINED/'base_engine'/name).as_posix() for name in flags['engine_sources']}
    flags['calculation_engine_source']=(RETAINED/'executed_code/PPRCalculator.py').as_posix()
    kwargs=copy.deepcopy(direct['new_GE']['settings']['kwargs']);kwargs.pop('TE_option')
    flags['diagnostics']=kwargs;flags['methods']={};flags['mc']={}
    flags['configuration_evidence']=[{'relative_path':(RETAINED/'run_provenance.json').as_posix(),
                                    'sha256':sha(retained/'run_provenance.json'),'original_source_hash':sha(model/'model.json')}]
    bridge={'schema_version':1,'unit_id':unit,'model_id':MID,'canonical_model_sha256':sha(model/'model.json'),
            'source_region':'EEZ_941','source_evidence':relative(DIRECT),'source_manifest_sha256':sha(DIRECT/'artifact_manifest.json'),
            'authorization':'User requested floor 0.1 for this identical shared model and publication of HS_071, EEZ_598, EEZ_941.',
            'operation':'Adopt verified existing direct outputs; no new scientific solve, no copied regional mappings or catch.',
            'floor':{'use_ee_floor':True,'ee_floor':.1},'original_execution_utc':provenance['timestamp_utc'],
            'adoption_prepared_utc':datetime.now(timezone.utc).isoformat(),'canonical_inputs_changed':False,
            'diagnostic_restrictions':'All three transformed direct diagnostics remain WARN and existing annual provisional restrictions remain.',
            'unsupported_inventory':'Other methods retain real adapter NOT_RUN outcomes; this does not establish scientific eligibility.'}
    write(retained/'adoption_provenance.json',bridge)
    flags['configuration_evidence'].append({'relative_path':(RETAINED/'adoption_provenance.json').as_posix(),
                                           'sha256':sha(retained/'adoption_provenance.json'),'original_source_hash':sha(model/'model.json')})
    flags=resolve_audited_configuration(stage_model,original,{'canonical_model_sha256':sha(model/'model.json'),'effective_flags':flags})
    keys=list(adapter.method_inventory());missing=[k for k in keys if k not in METHODS]
    context=coverage._context(ROOT,stage_model/'model.json',flags)
    evidence_dir=stage_model/'results/diagnostics'/PREFIX
    print(unit+': collecting canonical unavailable outcomes',flush=True)
    calculated=adapter.compute_methods(stage_model/'model.json',flags,missing,evidence_dir,progress=None)
    if any(v['status']!='NOT_RUN' or 'configuration_unavailable' not in v.get('reason','') for v in calculated['methods'].values()):
        raise ValueError('This importer is limited to genuine configuration-unavailable remaining methods')
    outcomes=calculated['methods']
    for key,option in METHODS.items():
        result=direct[key]
        certificate={'schema_version':1,'evidence_kind':'verified_retained_ee_floor_direct_adoption','method':key,
                     'context':context,'original_execution_utc':provenance['timestamp_utc'],
                     'source_evidence':RETAINED.as_posix(),'source_sha256':sha(DIRECT/(key+'_full_return.json.gz')),
                     'scientific_execution_performed_by_adoption':False,'target_unit_id':unit,
                     'scopes':result['scopes'],'direct_diagnostics':result['diagnostics'],
                     'reconciliation':{'matrix_axes_masks_scopes_and_footprint_checked':True,'identical_canonical_bytes':True,
                                       'identical_group_identity':True,'independent_regional_inputs_preserved':True}}
        evidence=adapter._save(evidence_dir/(key+'.adopted.json.gz'),certificate)
        outcomes[key]={'status':'reused','reason':'Verified identical-model floor-0.1 direct return adopted without solving; original diagnostic WARN',
                       'scopes':copy.deepcopy(result['scopes']),'annual_status':copy.deepcopy(result['annual_status']),
                       'diagnostics':copy.deepcopy(result['diagnostics']),'evidence':evidence}
    outcomes={k:outcomes[k] for k in keys}
    for v in outcomes.values():v['evidence']['path']=PREFIX+'/'+v['evidence']['path']
    execution={k:{**calculated[k],'path':PREFIX+'/'+calculated[k]['path']} for k in ('constructor_evidence','evidence_index') if k in calculated}
    inputs.update([region,model/'model.json',model/'sppr_source.xlsx',model/'results/regional_snapshot.xlsx',model/'results/result_manifest.json',
                   Path(adapter.__file__),adapter.ENGINE/'PPRCalculator.py',adapter.ENGINE/'create_PPRS_excel.py'])
    inputs.update(ROOT/'tools/project_core'/n for n in coverage._arithmetic_identity())
    inputs.add(ROOT/'regions/LME/LME_038/papers/INDO-1999/models/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/model_validation/work/2026-11-14_152558_signoff/code/adopt_current_diagnostics.py')
    input_hashes={relative(p):fingerprint(p) for p in inputs}
    backup_index={}
    for source in (region,model/'sppr_source.xlsx',model/'results/regional_snapshot.xlsx',model/'results/result_manifest.json'):
        if source.is_file():
            destination=stage_model/'results/diagnostics/ee_floor/pre_adoption'/source.name
            destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
            backup_index[relative(source)]={'path':relative(destination,stage_model),'sha256':sha(source)}
    book=copy.deepcopy(original)
    # The reviewed historical diagnostics remain available in this immutable
    # pre-adoption workbook; their signed report is not modified by this run.
    coverage._apply_outcomes(book,MID,outcomes,keys,migration=True)
    ledger=read(DIRECT/'ee_floor_ledger.json')
    ledger_rows=[dict(zip(ledger['columns'],r),group_seq=i) for i,r in zip(ledger['index'],ledger['data'])]
    add_diagnostics(book,{'info':read(DIRECT/'ee_floor_info.json'),'ledger':ledger_rows})
    set_setting(book,'sppr_engine_hashes',json.dumps({k:v for k,v in context['code_identity'].items() if k!='create_PPRS_excel.py'}))
    print(unit+': recalculating retained regional arithmetic',flush=True)
    coverage._arithmetic(book,region,model/'model.json',flags,original,migration=True,invalidated_methods=tuple(METHODS))
    print(unit+': saving staged regional workbook',flush=True)
    saved=coverage._save_calculation(stage_region,book,model/'model.json',flags,copy.deepcopy(book),migration=True,invalidated_methods=tuple(METHODS))
    if coverage._preserved_inputs(saved)!=protected: raise ValueError('Protected scientific input changed')
    coverage._update_source(stage_model/'sppr_source.xlsx',saved,outcomes,replace_methods=keys)
    exact_source_numbers(stage_model/'sppr_source.xlsx',saved)
    set_setting(saved,'results_source_sha256',sha(stage_model/'sppr_source.xlsx'))
    saved=coverage._save_calculation(stage_region,saved,model/'model.json',flags,copy.deepcopy(saved),migration=True,invalidated_methods=tuple(METHODS))
    snapshot=stage_model/'results/regional_snapshot.xlsx';shutil.copyfile(stage_region,snapshot)
    hashes=coverage._method_rows(saved)[1]
    for k in keys:outcomes[k]['group_rows_sha256']=hashes[k]
    manifest={'schema_version':1,'unit_id':unit,'model_id':MID,'snapshot_selected_model_id':MID,
              'timestamp':datetime.now(timezone.utc).isoformat(),'canonical_model_sha256':sha(model/'model.json'),
              'present_canonical_model_sha256':sha(model/'model.json'),'snapshot_sha256':sha(snapshot),
              'coefficient_source_sha256':sha(stage_model/'sppr_source.xlsx'),'effective_flags':flags,
              'code_identity':{k:v for k,v in context['code_identity'].items() if k!='create_PPRS_excel.py'},
              'provenance_status':'Three verified identical-model floor-0.1 direct returns adopted; remaining canonical methods have explicit unavailable adapter outcomes.',
              'dependencies':dependencies(saved),'artifacts':{'snapshot':'regional_snapshot.xlsx','model':'../model.json','coefficients':'../sppr_source.xlsx'},
              'historical_package_backup':backup_index,'method_coverage':{'schema_version':1,'expected_methods':keys,'context':context,'methods':outcomes,
                'execution_evidence':execution,'arithmetic_code_identity':coverage._arithmetic_identity(),'protected_inputs_sha256':protected}}
    write(stage_model/'results/result_manifest.json',manifest)
    promotions=[{'source':relative(stage_region,package),'target':relative(region),'sha256':sha(stage_region)}]
    for source in sorted(p for p in stage_model.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
        if source==stage_model/'model.json':continue
        target=model/source.relative_to(stage_model)
        promotions.append({'source':relative(source,package),'target':relative(target),'sha256':sha(source)})
        input_hashes.setdefault(relative(target),fingerprint(target))
    check_inputs(input_hashes)
    plan={'schema_version':1,'unit_id':unit,'model_id':MID,'package':relative(package),'prepared_utc':datetime.now(timezone.utc).isoformat(),
          'consumed_inputs':input_hashes,'context':context,'expected_methods':keys,'protected_inputs_sha256':protected,'promotions':promotions,
          'method_outcomes':{k:{'status':v['status'],'reason':v.get('reason'),'evidence':v['evidence']} for k,v in outcomes.items()},
          'numerical_adoption_performed':False,'scientific_solve_performed':False}
    write(package/'preparation.json',plan)
    print(unit+': verifying staged package',flush=True)
    return verify_package(unit)

def verify_package(unit, *, check_current_inputs=True):
    from tools.project_core.calculations import coverage
    from tools.project_core.calculations.regional import result_hash
    from tools.project_core.workbooks.workbooks import read_book,overview,input_hash,records,rows
    from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
    package=package_dir(unit);plan=read(package/'preparation.json');stage_model=package/'model';regional=package/'regional'/(unit+'.xlsx')
    if check_current_inputs:check_inputs(plan['consumed_inputs'])
    for item in plan['promotions']:
        p=(package/item['source']).resolve()
        if not p.is_relative_to(package) or sha(p)!=item['sha256']:raise ValueError('Staged promotion changed')
    book=read_book(regional);manifest=read(stage_model/'results/result_manifest.json')
    if coverage._preserved_inputs(book)!=plan['protected_inputs_sha256']:raise ValueError('Protected inputs changed in staged workbook')
    if overview(book)['calculation_input_sha256']!=input_hash(book) or overview(book)['calculation_result_sha256']!=result_hash(book):raise ValueError('Stale staged hashes')
    flags=resolve_audited_configuration(stage_model,book,manifest)
    context=coverage._context(ROOT,stage_model/'model.json',flags)
    if context!=plan['context']:raise ValueError('Staged audited configuration does not resolve exactly')
    if not coverage._package_cache_valid(stage_model,regional,manifest,context,plan['expected_methods']):raise ValueError('Coverage cache failed')
    if not coverage._source_matches(stage_model,book,plan['expected_methods']):raise ValueError('Source coefficients differ')
    direct={key:read(DIRECT/(key+'_full_return.json.gz')) for key in METHODS}
    coeff=records(book,'Selected model groups','Group SPPR')
    if len(coeff)!=32*3*22:raise ValueError('Incorrect full coefficient inventory')
    for r in coeff:
        wanted=direct[r['method']]['scopes'][r['scope']][r['group']] if r['method'] in METHODS else None
        if r['sppr']!=wanted:raise ValueError('Exact coefficients or missingness differ')
    if any(r[2] in METHODS and r[5] in {'min_tC','max_tC'} for r in rows(book,'PPR','Annual')):
        raise ValueError('Affected historical sensitivity bounds survived')
    original=read_book(region_path(unit),sheets=['PPR'])
    previous={tuple(r[:6]):r[6] for r in rows(original,'PPR','Annual')}
    for row in rows(book,'PPR','Annual'):
        prior=previous.get(tuple(row[:6]))
        if prior and prior!='ok' and row[2] in METHODS and not str(row[6]).startswith(str(prior)):
            raise ValueError('Existing diagnostic/provisional restriction lost')
    write(RUN/'qa'/(unit+'_verification.json'),{'unit_id':unit,'passed':True,'coefficient_rows':len(coeff),
        'finite_coefficients':sum(r['sppr'] is not None for r in coeff),'missing_coefficients':sum(r['sppr'] is None for r in coeff),
        'canonical_coverage_cache':True,'source_coefficients_exact':True,'protected_inputs_equal':True,
        'effective_floor':.1,'scientific_solve_performed':False,'adoption_performed':False,
        'staged_regional_sha256':sha(regional),'prepared_utc':plan['prepared_utc']})
    return plan

def apply(publication, unit):
    from tools.project_core.registry.publication import _ACTIVE,publication_write
    from tools.project_core.calculations.coverage import _write_bytes,_package_cache_valid
    if publication not in _ACTIVE.get() or publication.root!=ROOT:raise ValueError('Active publication transaction required')
    lock=ROOT/'.project-write.lock'
    if not lock.is_file() or lock.read_text().strip()!=str(os.getpid()):raise ValueError('Project writer lock required')
    plan=verify_package(unit,check_current_inputs=False);package=package_dir(unit)
    targets={p['target'] for p in plan['promotions']}
    check_inputs({k:v for k,v in plan['consumed_inputs'].items() if k not in targets})
    if all(fingerprint(ROOT/p['target'])==p['sha256'] for p in plan['promotions']):
        return {'status':'already_applied','changed_units':[unit],'written_paths':[]}
    check_inputs(plan['consumed_inputs'])
    for item in plan['promotions']:
        source,target=package/item['source'],ROOT/item['target']
        with publication_write(target,fingerprint=item['sha256']):
            _write_bytes(target,source.read_bytes(),expected_sha256=plan['consumed_inputs'][item['target']])
    manifest=read(model_dir(unit)/'results/result_manifest.json')
    if not _package_cache_valid(model_dir(unit),region_path(unit),manifest,plan['context'],plan['expected_methods']):raise ValueError('Installed cache check failed')
    return {'status':'applied','changed_units':[unit],'written_paths':[str(ROOT/p['target']) for p in plan['promotions']],
            'written_hashes':{str(ROOT/p['target']):p['sha256'] for p in plan['promotions']}}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','verify']);parser.add_argument('--unit',choices=UNITS,required=True)
    a=parser.parse_args();p=prepare(a.unit) if a.command=='prepare' else verify_package(a.unit)
    print(json.dumps({'unit':a.unit,'package':p['package'],'promotions':len(p['promotions']),'methods':{k:v['status'] for k,v in p['method_outcomes'].items()}}),flush=True)
