"""Verify/adopt staged floor packages while preserving unchanged saved floats.

The preparation's strict donor-float assertion did not account for the shared
coverage writer intentionally preserving compatible .16g-identical original
cells. This verifier admits only those exact original values, documents every
such difference, and changes no staged numerical artifacts.
"""
from __future__ import annotations
import argparse, importlib.util, json, os
from pathlib import Path

SCRIPT=Path(__file__).resolve()
spec=importlib.util.spec_from_file_location('_wcpo_preparation',SCRIPT.with_name('stage_floor_adoption.py'))
prepared=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepared)
ROOT,RUN,METHODS,DIRECT=prepared.ROOT,prepared.RUN,prepared.METHODS,prepared.DIRECT

def verify_package(unit, *, check_current_inputs=True):
    from tools.project_core.calculations import coverage
    from tools.project_core.calculations.regional import result_hash
    from tools.project_core.workbooks.workbooks import read_book,overview,input_hash,records,rows,digest_tables
    from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
    package=prepared.package_dir(unit);plan=prepared.read(package/'preparation.json')
    stage_model=package/'model';regional=package/'regional'/(unit+'.xlsx')
    if check_current_inputs:prepared.check_inputs(plan['consumed_inputs'])
    for item in plan['promotions']:
        p=(package/item['source']).resolve()
        if not p.is_relative_to(package) or prepared.sha(p)!=item['sha256']:
            raise ValueError('Staged promotion changed: '+item['source'])
    book=read_book(regional);manifest=prepared.read(stage_model/'results/result_manifest.json')
    if coverage._preserved_inputs(book)!=plan['protected_inputs_sha256']:raise ValueError('Protected inputs changed')
    if overview(book)['calculation_input_sha256']!=input_hash(book) or overview(book)['calculation_result_sha256']!=result_hash(book):
        raise ValueError('Staged arithmetic hashes stale')
    flags=resolve_audited_configuration(stage_model,book,manifest)
    context=coverage._context(ROOT,stage_model/'model.json',flags)
    if context!=plan['context']:raise ValueError('Staged configuration no longer resolves exactly')
    if not coverage._package_cache_valid(stage_model,regional,manifest,context,plan['expected_methods']):raise ValueError('Coverage cache failed')
    if not coverage._source_matches(stage_model,book,plan['expected_methods']):raise ValueError('Coefficient source differs')
    old_path=stage_model/'results/diagnostics/ee_floor/pre_adoption'/(unit+'.xlsx')
    if prepared.sha(old_path)!=plan['consumed_inputs'][prepared.relative(prepared.region_path(unit))]:raise ValueError('Historical workbook differs')
    old=read_book(old_path,sheets=['PPR','Selected model groups','Overview'])
    original={(r['method'],r['scope'],r['group']):r['sppr'] for r in records(old,'Selected model groups','Group SPPR')}
    direct={key:prepared.read(DIRECT/(key+'_full_return.json.gz')) for key in METHODS}
    coeff=records(book,'Selected model groups','Group SPPR')
    if len(coeff)!=32*3*22:raise ValueError('Full coefficient inventory incomplete')
    preserved=[]
    for r in coeff:
        key=(r['method'],r['scope'],r['group'])
        wanted=direct[r['method']]['scopes'][r['scope']][r['group']] if r['method'] in METHODS else None
        if r['sppr']==wanted:continue
        if (r['method'] not in METHODS or r['sppr']!=original.get(key)
                or digest_tables(r['sppr'])!=digest_tables(wanted)):
            raise ValueError('Changed direct coefficient or unsupported missing value: '+str(key))
        preserved.append({'method':r['method'],'scope':r['scope'],'group':r['group'],
                          'original_saved':original[key],'adopted_saved':r['sppr'],'donor_raw':wanted,
                          'delta':r['sppr']-wanted,'reason':'Exact compatible original saved value preserved by canonical .16g equality'})
    if any(r[2] in METHODS and r[5] in {'min_tC','max_tC'} for r in rows(book,'PPR','Annual')):
        raise ValueError('Affected historical sensitivity bounds survived')
    previous={tuple(r[:6]):r[6] for r in rows(old,'PPR','Annual')}
    for row in rows(book,'PPR','Annual'):
        prior=previous.get(tuple(row[:6]))
        if prior and prior!='ok' and row[2] in METHODS and not str(row[6]).startswith(str(prior)):
            raise ValueError('Existing diagnostic/provisional restriction lost')
    for k in ('selected_model_id','selection_rationale','model_path'):
        if overview(book).get(k)!=overview(old).get(k):raise ValueError('Selection changed: '+k)
    prepared.write(RUN/'qa'/(unit+'_verification.json'),{'unit_id':unit,'passed':True,
        'verifier_source_sha256':prepared.sha(SCRIPT),'preparation_source_sha256':prepared.sha(prepared.SCRIPT),
        'coefficient_rows':len(coeff),'finite_coefficients':sum(r['sppr'] is not None for r in coeff),
        'missing_coefficients':sum(r['sppr'] is None for r in coeff),'canonical_coverage_cache':True,
        'source_matches_saved_coefficients':True,'protected_inputs_equal':True,'selection_preserved':True,
        'effective_floor':.1,'scientific_solve_performed':False,'adoption_performed':False,
        'compatible_original_cells_preserved':preserved,'staged_regional_sha256':prepared.sha(regional),
        'prepared_utc':plan['prepared_utc']})
    return plan

def apply(publication,unit):
    from tools.project_core.registry.publication import _ACTIVE,publication_write
    from tools.project_core.calculations.coverage import _write_bytes,_package_cache_valid
    if publication not in _ACTIVE.get() or publication.root!=ROOT:raise ValueError('Active publication transaction required')
    lock=ROOT/'.project-write.lock'
    if not lock.is_file() or lock.read_text().strip()!=str(os.getpid()):raise ValueError('Project writer lock required')
    plan=verify_package(unit,check_current_inputs=False);package=prepared.package_dir(unit)
    targets={p['target'] for p in plan['promotions']}
    prepared.check_inputs({k:v for k,v in plan['consumed_inputs'].items() if k not in targets})
    if all(prepared.fingerprint(ROOT/p['target'])==p['sha256'] for p in plan['promotions']):
        return {'status':'already_applied','changed_units':[unit],'written_paths':[]}
    prepared.check_inputs(plan['consumed_inputs'])
    for item in plan['promotions']:
        source,target=package/item['source'],ROOT/item['target']
        with publication_write(target,fingerprint=item['sha256']):
            _write_bytes(target,source.read_bytes(),expected_sha256=plan['consumed_inputs'][item['target']])
    manifest=prepared.read(prepared.model_dir(unit)/'results/result_manifest.json')
    if not _package_cache_valid(prepared.model_dir(unit),prepared.region_path(unit),manifest,plan['context'],plan['expected_methods']):
        raise ValueError('Installed coverage cache check failed')
    return {'status':'applied','changed_units':[unit],'written_paths':[str(ROOT/p['target']) for p in plan['promotions']],
            'written_hashes':{str(ROOT/p['target']):p['sha256'] for p in plan['promotions']}}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--unit',choices=prepared.UNITS,required=True)
    args=parser.parse_args();p=verify_package(args.unit)
    print(json.dumps({'unit':args.unit,'verified':True,'package':p['package'],'promotions':len(p['promotions'])}),flush=True)
