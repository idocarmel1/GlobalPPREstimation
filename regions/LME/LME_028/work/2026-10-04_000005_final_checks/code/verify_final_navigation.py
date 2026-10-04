"""Independent read-only final inventory, ModelData and full-snapshot audit."""
import collections, datetime, json, re, sys, warnings, zipfile
from pathlib import Path
import openpyxl

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
from tools.project_core.registry.discovery import discover_regions, discover_models
from tools.project_core.workbooks.workbooks import read_book, overview, records, sha
from tools.project_core.calculations.snapshots import dependencies, inspect_snapshot

QA = Path(__file__).resolve().parent.parent/'qa'
def rel(p): return Path(p).relative_to(ROOT).as_posix()
def overview_blocks(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
    try:
        blocks = {}; name = None; header = None; values = []
        for row in wb['Overview'].values:
            row = list(row)
            while row and row[-1] is None: row.pop()
            if not row: continue
            if row[0] == '@table':
                if name is not None: blocks[name] = (header or [], values)
                name, header, values = row[1], None, []
            elif name is not None:
                if header is None: header = row
                else: values.append((row+[None]*len(header))[:len(header)])
        if name is not None: blocks[name] = (header or [], values)
        return {'Overview': blocks}
    finally: wb.close()

regions = discover_regions(ROOT)
models = {(unit, mid): path for unit, workbook in regions.items()
          for mid, path in discover_models(workbook.parent).items()}
starting_hashes = {rel(p): sha(p) for p in [*regions.values(), *models.values()]}
errors = []; selected = []; region_identity_errors = []
for unit, workbook in regions.items():
    book = overview_blocks(workbook); o = overview(book)
    if o.get('unit_id') != unit: region_identity_errors.append({'unit_id':unit,'recorded':o.get('unit_id')})
    mid = o.get('selected_model_id')
    if mid:
        model = models.get((unit, mid))
        expected = model.relative_to(workbook.parent).as_posix() if model else None
        available = records(book, 'Overview', 'Available models')
        expected_available = {m: p.relative_to(workbook.parent).as_posix() for (u,m),p in models.items() if u == unit}
        actual_available = {r.get('model_id'): r.get('model_path') for r in available}
        item = {'unit_id':unit,'selected_model_id':mid,'model_path':o.get('model_path'),
                'expected_model_path':expected,'path_matches':expected is not None and o.get('model_path') == expected,
                'available_models_count':len(available),'available_models_exact':len(available)==len(actual_available) and actual_available==expected_available,
                'shortcut_exists':(workbook.parent/'selected_model.lnk').is_file(),
                'results_model_id':o.get('results_model_id'),'calculation_status':o.get('calculation_status'),
                'expected_shortcut_target':str(model.parent) if model else None}
        selected.append(item)
        if not item['path_matches'] or not item['available_models_exact']: errors.append({'navigation':item})
print(f'Overview navigation read: {len(regions)} regions, {len(selected)} selected', flush=True)

loaded = []
for (unit,mid), path in models.items():
    source = json.loads(path.read_text(encoding='utf-8-sig')); groups = source.get('group')
    seqs = [str(g.get('group_seq')) for g in groups] if isinstance(groups,list) else []
    item = {'unit_id':unit,'model_id':mid,'path':rel(path),'sha256':sha(path),
            'schema_group_list':bool(groups) and isinstance(groups,list),'unique_group_ids':len(seqs)==len(set(seqs)) and 'None' not in seqs,
            'notes_exist':(path.parent/'model_notes.md').is_file()}
    with warnings.catch_warnings(record=True) as observed:
        warnings.simplefilter('always')
        try:
            model = ModelData(str(path))
            item.update({'loadable':True,'source_group_count':len(groups),'loaded_group_count':len(model.groups_data),
                         'synthetic_import_only_extra_group':len(model.groups_data)==len(groups)+1,
                         'diet_shape':list(model.DC.shape),'diet_shape_matches_groups':model.DC.shape==(len(model.groups_data),len(model.groups_data)),
                         'resolved_name':str(model.model_name),'resolved_year':str(model.model_year),
                         'source_dict_preserved':model.data_json==source,
                         'missing_loaded_parameters':{c:int(model.groups_data[c].isna().sum()) for c in ['biomass','pb','qb','ee']}})
        except Exception as exc: item.update({'loadable':False,'error_type':type(exc).__name__,'error':str(exc)})
    item['warnings'] = sorted({str(w.message) for w in observed})
    notes = (path.parent/'model_notes.md').read_text(encoding='utf-8') if item['notes_exist'] else ''
    item['documented_restrictions'] = [line for line in notes.splitlines() if re.search(r'constructor|construction blocked|loading fails|NOT_RUN|strict admission|routing.{0,50}missing|source admission fails|direct.{0,80}(FAIL|WARN)|GE.{0,80}FAIL',line,re.I)]
    loaded.append(item)
    if not all(item.get(k) for k in ['schema_group_list','unique_group_ids','notes_exist','loadable','synthetic_import_only_extra_group','diet_shape_matches_groups']): errors.append({'model':item})
print(f'ModelData loaded: {sum(x["loadable"] for x in loaded)}/{len(loaded)}; no PPRCalculator/default-repair or numerical diagnostic call', flush=True)

baseline_path = ROOT/'regions/LME/LME_028/work/2026-10-04_000002_reorganization/qa/files.json'
baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
baseline_sha = collections.defaultdict(list)
for row in baseline:
    if row.get('sha256'): baseline_sha[row['sha256']].append(row['path'])
promoted_path = ROOT/'regions/LME/LME_028/work/2026-10-04_000007_preservation/qa/preserved_previous_snapshots.json'
promoted = {r['snapshot']:r for r in json.loads(promoted_path.read_text(encoding='utf-8'))}
current_code = {name:sha(ROOT/'tools/scientific_code/PPREstimation'/name) for name in ['ModelData.py','PPRCalculator.py','utils.py']}
snapshots = []
for (unit,mid), path in models.items():
    home = path.parent; mf = home/'results/result_manifest.json'; sf = home/'results/regional_snapshot.xlsx'
    if not mf.exists() and not sf.exists(): continue
    item = {'unit_id':unit,'model_id':mid,'snapshot':rel(sf),'manifest':rel(mf)}
    try:
        manifest = json.loads(mf.read_text(encoding='utf-8')); saved = read_book(sf); o = overview(saved); actual = sha(sf)
        current = sha(path)
        with zipfile.ZipFile(sf) as z: members=z.namelist()
        compatibility = inspect_snapshot(home,saved,expected_identity={'effective_flags':manifest.get('effective_flags'),'code_identity':current_code})
        item.update({'snapshot_sha256':actual,'manifest_snapshot_sha256':manifest['snapshot_sha256'],
                     'full_package_hash_exact':actual==manifest['snapshot_sha256'],
                     'identity_exact':manifest['model_id']==mid==o.get('results_model_id') and manifest['unit_id']==unit==o.get('unit_id'),
                     'selected_identity_recorded_exact':manifest.get('snapshot_selected_model_id')==o.get('selected_model_id'),
                     'dependencies_exact':manifest['dependencies']==dependencies(saved),
                     'sheet_names':list(saved),'worksheet_parts':sum(n.startswith('xl/worksheets/sheet') and n.endswith('.xml') for n in members),
                     'recorded_results_model_sha256':o.get('results_model_sha256'),'manifest_canonical_sha256':manifest['canonical_model_sha256'],
                     'current_canonical_sha256':current,'recorded_model_matches_current':manifest['canonical_model_sha256']==current,
                     'effective_flags':manifest.get('effective_flags'),'code_identity':manifest.get('code_identity'),
                     'provenance_status':manifest.get('provenance_status'),
                     'baseline_full_byte_source_candidates':baseline_sha.get(actual,[]),
                     'promoted_outgoing_full_copy_record':promoted.get(rel(sf)),
                     'reuse_against_own_saved_inputs':{k:compatibility.get(k) for k in ['groups','coefficients','matching','diagnostics','reasons']}})
        if not all(item[k] for k in ['full_package_hash_exact','identity_exact','selected_identity_recorded_exact','dependencies_exact']): errors.append({'snapshot':item})
    except Exception as exc:
        item.update({'error_type':type(exc).__name__,'error':str(exc)});errors.append({'snapshot':item})
    snapshots.append(item)
print(f'Full snapshot packages checked: {len(snapshots)}', flush=True)

central = ROOT/'Project.xlsx'; central_before = sha(central); lock_before = (ROOT/'.project-write.lock').exists()
book = read_book(central); registered = records(book,'Models & coverage','Models')
counts = collections.Counter((r.get('unit_id'),r.get('model_id')) for r in registered)
registration = {'rows':len(registered),'unique_identities':len(counts),'duplicates':[list(k) for k,v in counts.items() if v!=1],
                'unregistered_canonical':[list(k) for k in sorted(set(models)-set(counts))],
                'unavailable_registered':[list(k) for k in sorted(set(counts)-set(models))],
                'path_errors':[{'unit_id':r.get('unit_id'),'model_id':r.get('model_id'),'recorded_path':r.get('model_path'),'expected_path':rel(models[(r['unit_id'],r['model_id'])])} for r in registered if (r.get('unit_id'),r.get('model_id')) in models and r.get('model_path')!=rel(models[(r['unit_id'],r['model_id'])])],
                'central_sha256':central_before,'central_read_hash_stable':sha(central)==central_before,'writer_lock_present_during_read':lock_before or (ROOT/'.project-write.lock').exists()}
if any(registration[k] for k in ['duplicates','unregistered_canonical','unavailable_registered','path_errors']): errors.append({'registration':registration})
changed = [{'path':p,'before':old,'after':sha(ROOT/p)} for p,old in starting_hashes.items() if sha(ROOT/p)!=old]
record = {'schema_version':1,'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'runtime':sys.executable,'scope':'Independent current-file audit; source bytes hashed before and after; no scientific parameter or workbook edits',
          'counts':{'regions':len(regions),'regions_by_type':dict(collections.Counter(u.split('_')[0] for u in regions)),
                    'models':len(models),'selected_regions':len(selected),'snapshots':len(snapshots),'ModelData_loadable':sum(x['loadable'] for x in loaded)},
          'region_identity_errors':region_identity_errors,'registration':registration,'selected_navigation':selected,
          'model_compatibility':loaded,'snapshots':snapshots,'changed_during_verification':changed,'errors':errors,
          'limitations':['ModelData loadability is distinct from constructor readiness, diagnostic admission, researcher approval and source fidelity.',
                         'No PPRCalculator construction, numerical diagnostics, additional normalization/default-repair flags or scientific reruns were executed. Existing ModelData in-memory transformations remain unchanged; canonical file bytes are the preservation authority.',
                         'Documented constructor/diagnostic restrictions are quoted from adjacent notes, not newly computed.',
                         'Manifest hash verifies the complete current workbook package. Baseline hash candidates independently identify original byte copies where available; otherwise recorded copy evidence is distinguished from independently available source bytes.',
                         f'{sum(x.get("effective_flags") is None or x.get("code_identity") is None for x in snapshots)} snapshot manifests explicitly retain unknown historical flags/code identities; complete copies do not authorize numerical reuse.',
                         'The central registry must be rechecked after its writer exits if this audit overlaps an active writer.']}
(QA/'canonical_navigation_verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'counts':record['counts'],'errors':len(errors),'region_identity_errors':len(region_identity_errors),'changed_during_verification':len(changed),'registration_stable':registration['central_read_hash_stable'],'central_writer_present':registration['writer_lock_present_during_read']},indent=2),flush=True)
