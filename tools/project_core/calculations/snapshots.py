"""Exact workbook snapshots with conservative, role-specific numerical reuse."""
import copy, json, os, shutil, tempfile,math
from datetime import datetime, timezone
from pathlib import Path
from tools.project_core.workbooks.workbooks import read_book, overview, rows, records, sha, digest_tables,finite

MODEL_TABLES={'Selected model groups':{'Groups','Group SPPR'},'PPR':{'Matching','Annual','Taxon SPPR','Taxon PPR inspected year'}}
DIAGNOSTIC_TABLES={'model_health','mc_diagnostics','run_notes'}

def dependencies(book):
    o=overview(book)
    settings={k:v for k,v in o.items() if k in {'catch_basis','taxon_detail_year','unidentified_treatment','scope','method','normalize_DC','balance_BA_after_DC_normalization'}}
    return {'catch':digest_tables(book.get('Catch',{})), 'classic':digest_tables(book.get('Classic PPR',{}).get('Taxa',([],[]))),
            'npp':digest_tables(book.get('NPP',{})), 'matching':digest_tables(book.get('PPR',{}).get('Matching',([],[]))),
            'groups':digest_tables(book.get('Selected model groups',{})), 'settings':digest_tables(sorted(settings.items()))}

def save_snapshot(workbook_path, model_dir, *, result_identity):
    path=Path(workbook_path);model=Path(model_dir);book=read_book(path);o=overview(book)
    identity=o.get('results_model_id')
    if identity!=model.name or identity!=result_identity.get('model_id'):
        raise ValueError(f'Snapshot destination {model.name} disagrees with results_model_id {identity}')
    numerical=bool(rows(book,'Selected model groups','Group SPPR') or rows(book,'PPR','Annual'))
    useful=numerical or bool(rows(book,'Selected model groups','Groups') or rows(book,'PPR','Matching'))
    if not useful:return None
    canonical=model/'model.json'
    directory=model/'results';directory.mkdir(parents=True,exist_ok=True)
    destination=directory/'regional_snapshot.xlsx';manifest_path=directory/'result_manifest.json'
    if not numerical and destination.is_file():
        prior=read_book(destination)
        if rows(prior,'Selected model groups','Group SPPR') or rows(prior,'PPR','Annual'):return None
    recorded=result_identity.get('canonical_model_sha256') or o.get('results_model_sha256')
    manifest={'schema_version':1,'unit_id':o['unit_id'],'model_id':identity,
              'snapshot_selected_model_id':o.get('selected_model_id'),'timestamp':datetime.now(timezone.utc).isoformat(),
              'snapshot_sha256':sha(path),'canonical_model_sha256':recorded,
              'present_canonical_model_sha256':sha(canonical),'coefficient_source_sha256':sha(model/'sppr_source.xlsx') if (model/'sppr_source.xlsx').is_file() else None,
              'effective_flags':result_identity.get('effective_flags'),'code_identity':result_identity.get('code_identity'),
              'provenance_status':result_identity.get('provenance_status','unknown historical execution'),
              'dependencies':dependencies(book),'artifacts':{'snapshot':'regional_snapshot.xlsx','model':'../model.json','coefficients':'../sppr_source.xlsx' if (model/'sppr_source.xlsx').is_file() else None}}
    before=sha(path)
    with tempfile.TemporaryDirectory(dir=directory,prefix='.snapshot-') as tmp:
        staged=Path(tmp)/destination.name;shutil.copyfile(path,staged)
        if sha(staged)!=before or sha(path)!=before:raise ValueError('Regional workbook changed while snapshotting')
        staged_manifest=Path(tmp)/manifest_path.name;staged_manifest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        # Roll back both package members if replacement fails.
        backups={p:p.read_bytes() if p.exists() else None for p in [destination,manifest_path]}
        try:os.replace(staged,destination);os.replace(staged_manifest,manifest_path)
        except Exception:
            for p,data in backups.items():
                if data is None:p.unlink(missing_ok=True)
                else:p.write_bytes(data)
            raise
    return destination

def inspect_snapshot(model_dir, current_book, *, expected_identity=None):
    model=Path(model_dir);result={'coefficients':False,'matching':False,'diagnostics':False,'reasons':[],'book':None}
    expected_identity=expected_identity or {}
    try:
        manifest=json.loads((model/'results/result_manifest.json').read_text(encoding='utf-8'))
        snapshot=model/'results/regional_snapshot.xlsx'
        if manifest['schema_version']!=1 or manifest['model_id']!=model.name or manifest['unit_id']!=overview(current_book)['unit_id']:raise ValueError('snapshot identity mismatch')
        if sha(snapshot)!=manifest['snapshot_sha256']:raise ValueError('snapshot corrupt: SHA-256 mismatch')
        saved=read_book(snapshot);result['book']=saved
        model_ok=sha(model/'model.json')==manifest['canonical_model_sha256']
        if not model_ok:result['reasons'].append('canonical model hash changed')
        flags_ok=manifest.get('effective_flags') is not None and manifest.get('effective_flags')==expected_identity.get('effective_flags')
        code_ok=manifest.get('code_identity') is not None and manifest.get('code_identity')==expected_identity.get('code_identity')
        if not flags_ok:result['reasons'].append('loading flags unknown or incompatible')
        if not code_ok:result['reasons'].append('executed calculator code identity unknown or incompatible')
        source=manifest.get('coefficient_source_sha256')
        source_ok=not source or ((model/'sppr_source.xlsx').is_file() and sha(model/'sppr_source.xlsx')==source)
        if not source_ok:result['reasons'].append('coefficient source hash changed')
        settings_ok=manifest['dependencies']['settings']==dependencies(current_book)['settings']
        if not settings_ok:result['reasons'].append('model-dependent settings changed')
        compatible=model_ok and flags_ok and code_ok and source_ok and settings_ok
        available=any(finite(r.get('sppr')) for r in records(saved,'Selected model groups','Group SPPR'))
        result['coefficients']=compatible and available
        result['groups']=model_ok and settings_ok
        if not available:result['reasons'].append('no usable saved group coefficients; scientific calculation remains pending')
        # Retained matching is evidence even when coefficients require fresh execution.
        taxa={r['taxon'] for r in records(current_book,'Catch','Catch')}
        matching=records(saved,'PPR','Matching')
        result['matching']=model_ok and settings_ok and all(r.get('model_id')==model.name for r in matching)
        known={r.get('group_name') for r in records(saved,'Selected model groups','Groups')}|{r.get('group') for r in records(saved,'Selected model groups','Group SPPR')}
        known.discard(None)
        allocations={};pairs=set()
        for row in matching:
            group=row.get('group');taxon=row.get('taxon')
            if not group:continue
            weight=row.get('weight');pair=(taxon,group)
            if group not in known or pair in pairs or not finite(weight) or weight<0:
                result['matching']=False;result['reasons'].append('saved matching has unknown/duplicate groups or invalid weights');break
            pairs.add(pair);allocations.setdefault(taxon,[]).append(weight)
        if any(not math.isclose(math.fsum(weights),1,abs_tol=1e-9,rel_tol=0) for weights in allocations.values()):
            result['matching']=False;result['reasons'].append('saved matching weights do not sum to one')
        if manifest['dependencies']['catch']!=dependencies(current_book)['catch'] and any(r.get('weight') not in (None,0,1) for r in matching):
            result['matching']=False;result['reasons'].append('changed catch: split allocation assumptions require review')
        result['diagnostics']=compatible
        result['manifest']=manifest
    except (OSError,ValueError,KeyError,TypeError) as e:result['reasons'].append(str(e))
    return result

def restore_model_tables(current_book, snapshot_book, compatibility):
    result=copy.deepcopy(current_book)
    for sheet,names in MODEL_TABLES.items():
        for name in names:
            allowed=compatibility.get('matching') if name=='Matching' else compatibility.get('coefficients')
            if name=='Groups':allowed=compatibility.get('groups',compatibility.get('coefficients'))
            if sheet=='PPR' and name!='Matching':allowed=allowed and compatibility.get('matching')
            if allowed and name in snapshot_book.get(sheet,{}):
                header,data=copy.deepcopy(snapshot_book[sheet][name])
                if name=='Matching':
                    taxa={r['taxon'] for r in records(current_book,'Catch','Catch')};i=header.index('taxon');data=[r for r in data if r[i] in taxa]
                result.setdefault(sheet,{})[name]=(header,data)
    # Authored allocation/review records travel with compatible matching even
    # when unknown execution provenance prevents numerical coefficient reuse.
    if compatibility.get('matching'):
        for name in ['Allocation assumptions','Mapping review']:
            if name in snapshot_book.get('PPR',{}):result.setdefault('PPR',{})[name]=copy.deepcopy(snapshot_book['PPR'][name])
    if compatibility.get('diagnostics'):
        for name in DIAGNOSTIC_TABLES:
            if name in snapshot_book.get('Diagnostics',{}):result.setdefault('Diagnostics',{})[name]=copy.deepcopy(snapshot_book['Diagnostics'][name])
    if compatibility.get('coefficients') and compatibility.get('matching') and dependencies(result)==dependencies(snapshot_book):
        if 'Ratios' in snapshot_book.get('PPR–NPP',{}):
            h,r=copy.deepcopy(snapshot_book['PPR–NPP']['Ratios']);current=result.get('PPR–NPP',{}).get('Ratios',(h,[]))[1]
            result.setdefault('PPR–NPP',{})['Ratios']=(h,[row for row in current if not row[0]]+[row for row in r if row[0]])
    return result
