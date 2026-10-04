"""One-action, serialized model selection; no scientific engine runs or mapping guesses."""
import copy,json,os,shutil,tempfile,subprocess
from contextlib import contextmanager
from pathlib import Path
from tools.project_core.registry.discovery import resolve_model,discover_models,project_root
from tools.project_core.registry.writes import central_lock
from tools.project_core.workbooks.workbooks import *
from tools.project_core.calculations.regional import recalculate,set_setting,set_result_hash,result_hash
from tools.project_core.calculations.snapshots import save_snapshot,inspect_snapshot,restore_model_tables,dependencies

def execution_identity(root, model_dir, book=None, *, flags=None):
    explicit_flags=flags is not None
    o=overview(book or {})
    if flags is None:
        for key in ['effective_loader_flags','sppr_configuration']:
            value=o.get(key)
            if isinstance(value,str):
                try:value=json.loads(value)
                except ValueError:continue
            if isinstance(value,dict):flags=value;break
    code={name:sha(Path(root)/'tools/scientific_code/PPREstimation'/name) for name in ['ModelData.py','PPRCalculator.py','utils.py']}
    recorded=o.get('sppr_engine_hashes')
    if isinstance(recorded,str):
        try:recorded=json.loads(recorded)
        except ValueError:recorded=None
    return {'model_id':Path(model_dir).name,'canonical_model_sha256':o.get('results_model_sha256') or sha(Path(model_dir)/'model.json'),
            'effective_flags':flags,'code_identity':recorded or (code if explicit_flags else None),
            'provenance_status':'recorded execution' if flags is not None and recorded else 'unknown historical execution' if flags is None else 'explicit fixture/current loading configuration'}

def _clear_model(book):
    for sheet in ['Selected model groups','PPR']:
        book[sheet]={name:(header,[]) for name,(header,data) in book.get(sheet,{}).items()}
    for table in ['model_health','mc_diagnostics','run_notes']:
        if table in book.get('Diagnostics',{}):book['Diagnostics'][table]=(book['Diagnostics'][table][0],[])
    if 'Ratios' in book.get('PPR–NPP',{}):
        h,r=book['PPR–NPP']['Ratios'];book['PPR–NPP']['Ratios']=(h,[row for row in r if not row[0]])
    for key in ['results_model_id','results_model_sha256','effective_loader_flags','sppr_configuration','sppr_engine_hashes']:set_setting(book,key,None)
    set_setting(book,'production_eligible',False)

def available_models(region, central):
    """Generated navigation from canonical files and existing scientific registration."""
    unit=Path(region).name
    registered=[r['model_id'] for r in records(central,'Models & coverage','Models') if r.get('unit_id')==unit]
    if len(registered)!=len(set(registered)):raise ValueError('Duplicate regional registration: '+unit)
    models=discover_models(region)
    if set(models)!=set(registered):raise ValueError('Canonical files and registered models disagree: '+unit)
    return (['model_id','model_path'],[[mid,path.relative_to(region).as_posix()] for mid,path in models.items()])

def _shortcut(region,model):
    if os.name!='nt':return 'unavailable on this platform'
    # Paths are literal PowerShell string arguments, never interpolated shell expressions.
    def literal(value):return "'"+str(value).replace("'","''")+"'"
    command="$s=(New-Object -ComObject WScript.Shell).CreateShortcut("+literal(region/'selected_model.lnk')+");$s.TargetPath="+literal(model)+";$s.Save()"
    result=subprocess.run(['powershell','-NoProfile','-NonInteractive','-Command',command],capture_output=True,text=True)
    if result.returncode:raise RuntimeError('Could not regenerate selected_model.lnk: '+result.stderr.strip())
    return 'generated'

def _publish(root,units):
    from tools.project_core.maps.build_html import build
    build(root/'Project.xlsx',only_units=set(units))

def refresh_region(root,region_workbook,*,publisher=None):
    root=Path(root).resolve();path=Path(region_workbook).resolve()
    if path.is_dir():path=path/(path.name+'.xlsx')
    if not path.is_relative_to(root/'regions'):raise ValueError('Regional workbook must be inside project regions')
    source_hashes={path:sha(path),root/'Project.xlsx':sha(root/'Project.xlsx')}
    original=read_book(path);o=overview(original);selected=o.get('selected_model_id')
    if not o.get('selection_rationale'):raise ValueError('Enter selection_rationale in regional Overview')
    model=resolve_model(path.parent,selected);source_hashes[model]=sha(model);data=json.loads(model.read_text(encoding='utf-8-sig'))
    if not isinstance(data,dict) or not isinstance(data.get('group'),list) or not data['group']:raise ValueError('Canonical JSON is not a supported Ecopath group export')
    group_ids=[str(g.get('group_seq')) for g in data['group']]
    if len(set(group_ids))!=len(group_ids) or any(g=='None' for g in group_ids):raise ValueError('Canonical JSON has missing or duplicate group identity')
    central=read_book(root/'Project.xlsx')
    registered=[r for r in records(central,'Models & coverage','Models') if (r.get('unit_id'),r.get('model_id'))==(o.get('unit_id'),selected)]
    if len(registered)!=1:raise ValueError('Register this exact regional model once in Project.xlsx; missing or duplicate metadata')
    if any(sha(p)!=value for p,value in source_hashes.items()):raise ValueError('Inputs changed while reading refresh preflight; reread the current workbook')
    with central_lock(root),tempfile.TemporaryDirectory(dir=path.parent,prefix='.refresh-') as tmp:
        backup=Path(tmp);protected=[path,root/'Project.xlsx'];maps=root/'interactive_map'
        if maps.exists():protected+=list(p for p in maps.rglob('*') if p.is_file())
        before={p:p.read_bytes() for p in protected};prior_pages=set(protected);owned={path:source_hashes[path],root/'Project.xlsx':source_hashes[root/'Project.xlsx']};shortcut=path.parent/'selected_model.lnk';old_shortcut=shortcut.read_bytes() if shortcut.exists() else None
        packages={d.parent/'results'/name for d in discover_models(path.parent).values() for name in ['regional_snapshot.xlsx','result_manifest.json']}
        package_before={p:p.read_bytes() if p.exists() else None for p in packages}
        try:
            if any(sha(p)!=value for p,value in source_hashes.items()):raise ValueError('Inputs changed during refresh preflight')
            outgoing=o.get('results_model_id')
            if outgoing:
                outgoing_model=resolve_model(path.parent,outgoing)
                identity=execution_identity(root,outgoing_model.parent,original)
                existing=outgoing_model.parent/'results/result_manifest.json'
                # A verified snapshot's recorded flags remain pinned; do not replace them with unknown defaults.
                if existing.is_file():
                    saved=json.loads(existing.read_text(encoding='utf-8'))
                    source=outgoing_model.parent/'sppr_source.xlsx'
                    same_coefficients=saved.get('dependencies',{}).get('groups')==dependencies(original)['groups'] and saved.get('coefficient_source_sha256')==(sha(source) if source.is_file() else None)
                    if saved.get('canonical_model_sha256')==identity['canonical_model_sha256'] and same_coefficients:
                        for key in ['effective_flags','code_identity','provenance_status']:
                            identity[key]=saved.get(key)
                save_snapshot(path,outgoing_model.parent,result_identity=identity)
            book=copy.deepcopy(original);set_setting(book,'model_path',model.relative_to(path.parent).as_posix())
            book.setdefault('Overview',{})['Available models']=available_models(path.parent,central)
            unchanged=outgoing==selected and o.get('results_model_sha256')==sha(model) and o.get('calculation_input_sha256')==input_hash(book) and o.get('calculation_result_sha256')==result_hash(book)
            pinned_path=model.parent/'results/result_manifest.json'
            if unchanged and pinned_path.is_file():
                pinned=json.loads(pinned_path.read_text(encoding='utf-8'))
                requested=execution_identity(root,model.parent,original)
                current_code={name:sha(root/'tools/scientific_code/PPREstimation'/name) for name in ['ModelData.py','PPRCalculator.py','utils.py']}
                if pinned.get('effective_flags') is not None and requested.get('effective_flags') is not None and pinned['effective_flags']!=requested['effective_flags']:unchanged=False
                if pinned.get('code_identity') is not None and pinned['code_identity']!=current_code:unchanged=False
            missing=[]
            if not unchanged:
                _clear_model(book)
                manifest=model.parent/'results/result_manifest.json'
                expected=execution_identity(root,model.parent,original if outgoing==selected else None)
                expected['code_identity']={name:sha(root/'tools/scientific_code/PPREstimation'/name) for name in ['ModelData.py','PPRCalculator.py','utils.py']}
                if manifest.is_file() and expected.get('effective_flags') is None:
                    recorded=json.loads(manifest.read_text(encoding='utf-8'))
                    expected['effective_flags']=recorded.get('effective_flags')
                compatibility=inspect_snapshot(model.parent,book,expected_identity=expected)
                if compatibility.get('book'):book=restore_model_tables(book,compatibility['book'],compatibility)
                if compatibility.get('coefficients') and compatibility.get('matching'):
                    set_setting(book,'results_model_id',selected);set_setting(book,'results_model_sha256',sha(model))
                    set_setting(book,'effective_loader_flags',compatibility['manifest']['effective_flags'])
                    set_setting(book,'sppr_engine_hashes',compatibility['manifest']['code_identity'])
                    # Recalculate regional arithmetic only. The engine is never invoked.
                    oldclassic=copy.deepcopy(original.get('Classic PPR',{}))
                    saved_book=compatibility['book'];saved_settings=overview(saved_book)
                    cached_fresh=saved_settings.get('calculation_input_sha256')==input_hash(saved_book) and saved_settings.get('calculation_result_sha256')==result_hash(saved_book)
                    if dependencies(book)==dependencies(saved_book) and cached_fresh:
                        set_setting(book,'calculation_input_sha256',input_hash(book))
                        set_setting(book,'production_eligible',overview(compatibility['book']).get('production_eligible',False))
                    else:recalculate(book,path)
                    if dependencies(original)['catch']==dependencies(book)['catch'] and dependencies(original)['classic']==dependencies(book)['classic']:
                        book['Classic PPR']=oldclassic
                    set_setting(book,'calculation_status','ready; compatible saved model restored; retained diagnostic restrictions apply')
                    set_result_hash(book)
                else:
                    missing=compatibility['reasons'] or ['no saved coefficients/matching for selected model']
                    set_setting(book,'calculation_status','pending: '+'; '.join(missing));set_setting(book,'calculation_input_sha256',input_hash(book));set_result_hash(book)
            validate_region(book,path)
            if sha(path)!=source_hashes[path] or sha(root/'Project.xlsx')!=source_hashes[root/'Project.xlsx']:raise ValueError('Authoritative workbooks changed during refresh; current edits preserved')
            update_book(path,book)
            owned[path]=sha(path)
            # Derived registry fields preserve every centrally authored metadata cell.
            central=read_book(root/'Project.xlsx');h,r=central['Models & coverage']['Models']
            for row in r:
                record=dict(zip(h,row))
                if record.get('unit_id')==o['unit_id'] and record.get('model_id') in discover_models(path.parent):
                    if 'model_path' in h:row[h.index('model_path')]=resolve_model(path.parent,record['model_id']).relative_to(root).as_posix()
            update_book(root/'Project.xlsx',central)
            owned[root/'Project.xlsx']=sha(root/'Project.xlsx')
            from tools.project_core.registry.update_project import update
            update(root,[path],lock_held=True);owned[root/'Project.xlsx']=sha(root/'Project.xlsx');(publisher or _publish)(root,[o['unit_id']])
            shortcut_status=_shortcut(path.parent,model.parent)
            if not missing:
                final_identity=execution_identity(root,model.parent,book,flags=(expected.get('effective_flags') if not unchanged else None))
                pinned=model.parent/'results/result_manifest.json'
                if pinned.is_file():
                    saved=json.loads(pinned.read_text(encoding='utf-8'))
                    if saved.get('canonical_model_sha256')==final_identity['canonical_model_sha256']:
                        for key in ['effective_flags','code_identity','provenance_status']:
                            if final_identity.get(key) is None or final_identity.get('provenance_status')=='unknown historical execution':final_identity[key]=saved.get(key)
                save_snapshot(path,model.parent,result_identity=final_identity)
            return {'unit_id':o['unit_id'],'selected_model_id':selected,'calculation_status':'pending' if missing else 'ready','missing_stages':missing,'shortcut':shortcut_status,'changed_paths':[path.relative_to(root).as_posix(),'Project.xlsx','interactive_map/']}
        except Exception:
            for p,value in package_before.items():
                if value is None:p.unlink(missing_ok=True)
                else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(value)
            conflicts=[]
            for p,value in before.items():
                if p in owned and sha(p)!=owned[p]:conflicts.append(p.relative_to(root).as_posix());continue
                p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(value)
            if maps.exists():
                for p in maps.rglob('*'):
                    if p.is_file() and p not in prior_pages:p.unlink()
            if old_shortcut is None:shortcut.unlink(missing_ok=True)
            else:shortcut.write_bytes(old_shortcut)
            if conflicts:raise RuntimeError('Refresh failed; concurrent author edits were preserved and require reconciliation: '+', '.join(conflicts))
            raise
