"""Operate on a single regional workbook. Research matching is performed by the regional skill."""
import argparse,sys,tempfile,shutil,csv,copy,json,os,hashlib
from datetime import datetime, timezone
from pathlib import Path
from tools.project_core.workbooks.workbooks import *
from tools.project_core.calculations.regional import recalculate,taxon_detail,set_setting,set_result_hash

def export_taxon(book,output):
    from tools.project_core.calculations.regional import inputs
    taxa,catch,_,_=inputs(book);o=overview(book);basis=o.get('catch_basis','landings')
    status={(r[1],r[2]):r[6] for r in rows(book,'PPR','Annual') if r[3]==basis and r[4]=='method' and r[5]=='ppr'}
    with output.open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['model_id','taxon','scope','method','catch_basis','status',*YEARS])
        for r in records(book,'PPR','Taxon SPPR'):
            st=status.get((r['scope'],r['method']),'unavailable');v=r['sppr']
            writer.writerow([r['model_id'],r['taxon'],r['scope'],r['method'],basis,st,*[c*v if numeric_status(st) and finite(c) and finite(v) else None for c in catch.get((r['taxon'],basis),[None]*70)]])

def sppr(book,path,timeout,*,use_ee_floor=None,ee_floor=None):
    """Run the canonical inventory using recorded audited settings, with guarded adoption."""
    from tools.project_core.registry.discovery import project_root,resolve_model
    from tools.project_core.registry.writes import central_lock
    from tools.project_core.registry.publication import publication_transaction, publication_write
    from tools.project_core.calculations import coverage
    from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
    from tools.scientific_helpers.sppr import method_coverage as adapter
    from tools.project_core.calculations import ee_floor_migration as floor
    from tools.project_core.calculations.snapshots import dependencies
    path=Path(path).resolve();o=overview(book);selected=o.get('selected_model_id')
    if not selected:raise ValueError('Select a model in Overview first')
    model=(path.parent/o['model_path']).resolve();model_dir=model.parent;root=project_root(path)
    if model.name!='model.json' or model_dir.name!=selected:
        raise ValueError('Selected canonical model identity does not match Overview')
    if resolve_model(path.parent,selected)!=model:
        raise ValueError('Overview model path does not match canonical discovery')
    keys=list(adapter._engine()[0].ALL_METHOD_KEYS)
    if use_ee_floor is not None or ee_floor is not None:
        adapter._engine()[2].validate_ee_floor(use_ee_floor if use_ee_floor is not None else True,
                                             ee_floor if ee_floor is not None else .1)
    original=copy.deepcopy(book);protected=coverage._preserved_inputs(book)
    manifest_path=model_dir/'results/result_manifest.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.is_file() else {}
    consumed={model:sha(model),path:sha(path)}
    manifest_fingerprint=sha(manifest_path) if manifest_path.is_file() else None
    def check_inputs(journal):
        for source,fingerprint in consumed.items():
            expected=journal.owned.get(source,fingerprint)
            if sha(source)!=expected:raise ValueError('Inputs changed during SPPR execution: '+str(source))
    def save_book(journal):
        check_inputs(journal)
        with publication_write(path):
            update_book(path,book)
            coverage._restore_retained_numbers(path,book,original)
        saved=read_book(path)
        if coverage._preserved_inputs(saved)!=protected:
            raise ValueError('SPPR publication changed a protected scientific input')
        book.clear();book.update(saved)
    with central_lock(root),publication_transaction(root,[path],[model_dir]) as journal:
        if journal.owned[path]!=consumed[path] or journal.owned[manifest_path]!=manifest_fingerprint:
            raise ValueError('Inputs changed before regional SPPR transaction')
        try:
            if o.get('results_model_id',selected)!=selected:
                raise ValueError('Saved group/calculation inputs belong to another model; refresh selection first')
            flags=resolve_audited_configuration(model_dir,book,manifest)
            original_flags=copy.deepcopy(flags)
            original_context=coverage._context(root,model,flags)
            migration=None
            if use_ee_floor is not None or ee_floor is not None:
                actual=adapter._constructor(flags,model)
                request={'use_ee_floor':actual.get('use_ee_floor',False) if use_ee_floor is None else use_ee_floor,
                         'ee_floor':actual.get('ee_floor',.1) if ee_floor is None else ee_floor}
                migration=floor.prepare(model,flags,keys,request)
                if migration:flags=migration['flags']
            context=coverage._context(root,model,flags)
            # Recheck exact consumed code bytes, including a pinned historical loader.
            for code in adapter._engine_paths(flags,model).values():consumed[code]=sha(code)
            calculation=adapter._calculation_engine_path(flags,model)
            if calculation is not None:consumed[calculation]=sha(calculation)
            if context.get('adapter_sha256'):consumed[Path(adapter.__file__)]=context['adapter_sha256']
            if context['code_identity'].get('create_PPRS_excel.py'):
                consumed[adapter.ENGINE/'create_PPRS_excel.py']=context['code_identity']['create_PPRS_excel.py']
        except (ValueError,TypeError,OSError,ImportError) as error:
            reason='Audited configuration unavailable: '+str(error)
            book.setdefault('Diagnostics',{})['SPPR execution']=(['method','status','reason'],
                [[key,'NOT_RUN',reason] for key in keys])
            save_book(journal)
            print('NOT_RUN: '+reason)
            return {'status':'NOT_RUN','reason':reason}
        diagnostics=model_dir/'results/diagnostics';diagnostics.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=diagnostics,prefix='.sppr-') as temporary:
            staged=Path(temporary);method_dir=staged/'method_coverage';method_dir.mkdir()
            baseline=None;retained={};floor_evidence={}
            if migration:
                floor_dir=staged/'ee_floor';floor_dir.mkdir()
                outbound={target:journal.before.get(target) for target in
                    (path,model_dir/'sppr_source.xlsx',manifest_path,model_dir/'results/regional_snapshot.xlsx')}
                baseline=floor.save_baseline(model_dir,outbound,manifest,floor_dir)
                baseline['path']='ee_floor/'+baseline['path']
                saved_methods={row[3] for row in rows(book,'Selected model groups','Group SPPR')}
                saved_methods.update(manifest.get('method_coverage',{}).get('methods',{}))
                compatible={key:proof for key,proof in migration['compatible'].items() if key in saved_methods}
                if compatible:
                    retained=floor.retained_outcomes(manifest,compatible,book,method_dir,context,baseline,
                        original_context=original_context,model_dir=model_dir,reviewed_model_sha256=consumed[model])
                runtime={key:migration[key] for key in ('before_runtime','after_runtime','old_warnings','new_warnings')}
                runtime.update(info=adapter.encode_lossless(migration['info']),ledger=adapter.encode_lossless(migration['ledger']),
                               original_flags=original_flags,requested_flags=flags,baseline=baseline)
                evidence=floor._write_gzip(floor_dir/'runtime.json.gz',runtime);evidence['path']='ee_floor/'+evidence['path']
                floor_evidence={'baseline':baseline,'runtime':evidence}
                code_hash=hashlib.sha256(migration['calculation_code']).hexdigest()
                code=floor_dir/'executed_code'/code_hash/'PPRCalculator.py';code.parent.mkdir(parents=True)
                code.write_bytes(migration['calculation_code'])
            execute=[key for key in keys if key not in retained]
            calculated=(adapter.compute_methods(model,flags,execute,method_dir,method_timeout=timeout)
                        if execute else {'methods':{}})
            outcomes={**retained,**calculated['methods']}
            if set(outcomes)!=set(keys):raise ValueError('SPPR executor omitted requested method outcomes')
            coverage._apply_outcomes(book,selected,outcomes,keys,migration=bool(migration))
            changed={key for key in keys if not outcomes[key].get('preserve_saved')}
            # Preserve each old catch/scope restriction as a pending arithmetic row.
            present={tuple(row[:6]) for row in rows(book,'PPR','Annual')}
            for row in rows(original,'PPR','Annual'):
                if row[2] in changed and row[5]=='ppr' and tuple(row[:6]) not in present:
                    status=outcomes[row[2]].get('annual_status',{}).get(row[1],'unavailable')
                    book['PPR']['Annual'][1].append([*row[:6],status,*[None]*len(YEARS)])
            floor.preserve_restrictions(book,original)
            if migration:floor.add_diagnostics(book,migration)
            book.setdefault('Diagnostics',{})['SPPR execution']=(['method','status','reason'],
                [[key,outcomes[key]['status'],outcomes[key].get('reason')] for key in keys])
            note_header,note_rows=book['Diagnostics'].get('run_notes',(['topic','note','status'],[]))
            if note_header==['topic','note','status']:
                note_rows=[row for row in note_rows if row[0]!='SPPR execution identity (current)']
                note_rows.append(['SPPR execution identity (current)',json.dumps(context,ensure_ascii=False),'recorded'])
                book['Diagnostics']['run_notes']=(note_header,note_rows)
            set_setting(book,'effective_loader_flags',json.dumps(flags,ensure_ascii=False))
            set_setting(book,'sppr_engine_hashes',json.dumps(context['code_identity'],ensure_ascii=False))
            set_setting(book,'results_model_id',selected);set_setting(book,'results_model_sha256',consumed[model])
            if changed:
                set_setting(book,'calculation_status','SPPR inventory recorded; matching/PPR refresh required')
                set_setting(book,'calculation_input_sha256',None)
            elif o.get('calculation_input_sha256')==input_hash(original):
                set_setting(book,'calculation_input_sha256',input_hash(book))
            set_result_hash(book)
            check_inputs(journal)
            for produced in staged.rglob('*'):
                if not produced.is_file():continue
                target=diagnostics/produced.relative_to(staged);target.parent.mkdir(parents=True,exist_ok=True)
                with publication_write(target,fingerprint=sha(produced)):
                    os.replace(produced,target)
            for outcome in outcomes.values():
                evidence=outcome.get('evidence')
                if evidence:evidence['path']='method_coverage/'+evidence['path']
            for key,evidence in calculated.items():
                if key in ('constructor_evidence','evidence_index'):
                    evidence['path']='method_coverage/'+evidence['path']
            coefficient_source=model_dir/'sppr_source.xlsx'
            check_inputs(journal)
            with publication_write(coefficient_source):
                coverage._update_source(coefficient_source,book,outcomes,replace_methods=changed,
                    effective_groups=migration['effective_groups'] if migration else None,
                    expected_sha256=journal.owned[coefficient_source])
            set_setting(book,'results_source_sha256',sha(coefficient_source))
            if not changed and o.get('calculation_input_sha256')==input_hash(original):
                set_setting(book,'calculation_input_sha256',input_hash(book))
            save_book(journal)
            snapshot=model_dir/'results/regional_snapshot.xlsx';snapshot.parent.mkdir(parents=True,exist_ok=True)
            with publication_write(snapshot,fingerprint=sha(path)):
                coverage._write_bytes(snapshot,path.read_bytes(),expected_sha256=journal.owned[snapshot])
            row_hashes=coverage._method_rows(book)[1]
            for key in keys:outcomes[key]['group_rows_sha256']=row_hashes[key]
            manifest.update(schema_version=1,unit_id=o['unit_id'],model_id=selected,
                canonical_model_sha256=consumed[model],snapshot_sha256=sha(snapshot),
                coefficient_source_sha256=sha(coefficient_source),effective_flags=flags,
                code_identity={key:value for key,value in context['code_identity'].items() if key!='create_PPRS_excel.py'},timestamp=datetime.now(timezone.utc).isoformat(),
                snapshot_selected_model_id=overview(book).get('selected_model_id'),
                present_canonical_model_sha256=consumed[model],
                artifacts={'snapshot':'regional_snapshot.xlsx','model':'../model.json','coefficients':'../sppr_source.xlsx'},
                dependencies=dependencies(book),
                provenance_status='Recorded audited regional SPPR execution',
                method_coverage={'schema_version':1,'context':context,'expected_methods':keys,'methods':outcomes,
                    'protected_inputs_sha256':protected,
                    'execution_evidence':{key:calculated[key] for key in ('constructor_evidence','evidence_index') if key in calculated},
                    'arithmetic_status':'pending matching/PPR refresh'})
            if migration:manifest['ee_floor_migration']={**floor_evidence,'original_flags':original_flags,'requested_flags':flags}
            with publication_write(manifest_path):
                coverage._write_json(manifest_path,manifest,expected_sha256=journal.owned[manifest_path])
    return {'status':'complete','methods':outcomes}

def parse_arguments(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--region',type=Path,required=True);ap.add_argument('--stage',choices=['validate','calculate','inspect-year','export-taxon-ppr','sppr'],required=True);ap.add_argument('--year',type=int);ap.add_argument('--basis',choices=['landings','catch','discards']);ap.add_argument('--output',type=Path);ap.add_argument('--timeout',type=float,default=180)
    floor=ap.add_mutually_exclusive_group();floor.add_argument('--use-ee-floor',dest='use_ee_floor',action='store_true');floor.add_argument('--no-ee-floor',dest='use_ee_floor',action='store_false');ap.set_defaults(use_ee_floor=None)
    ap.add_argument('--ee-floor',type=float);a=ap.parse_args(argv)
    if a.use_ee_floor is not None or a.ee_floor is not None:
        if a.stage!='sppr':ap.error('EE-floor settings apply to --stage sppr only')
        from tools.scientific_helpers.sppr.method_coverage import _engine
        try:_engine()[2].validate_ee_floor(a.use_ee_floor if a.use_ee_floor is not None else True,a.ee_floor if a.ee_floor is not None else .1)
        except ValueError as error:ap.error(str(error))
    return a

def main():
    a=parse_arguments()
    path=a.region.resolve()
    if path.is_dir():path=path/(path.name+'.xlsx')
    b=read_book(path)
    if a.stage=='validate':validate_region(b,path);print('Region is ready for consolidation');return
    if a.year:
        if a.year not in YEARS:raise ValueError('Year must be 1950–2019')
        set_setting(b,'taxon_detail_year',a.year)
    if a.basis:set_setting(b,'catch_basis',a.basis)
    if a.stage=='export-taxon-ppr':
        validate_region(b,path)
        output=a.output or path.parent/'taxon_ppr_export.csv';export_taxon(b,output);print(f'Exported {output}');return
    if a.stage=='calculate':recalculate(b,path)
    elif a.stage=='sppr':
        result=sppr(b,path,a.timeout,use_ee_floor=a.use_ee_floor,ee_floor=a.ee_floor)
        print(f"Updated {path.name}: sppr ({result['status']})");return
    else:taxon_detail(b)
    update_book(path,b);print(f'Updated {path.name}: {a.stage}')
if __name__=='__main__':main()
