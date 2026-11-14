"""Stage authenticated LME014 GE/TE evidence; never solve or publish from CLI.

The current WithEgestion slots are unavailable for this custom runtime. Their
exact original values and unknown historical execution identity remain archived.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

SCRIPT = Path(__file__).resolve()
RUN = SCRIPT.parents[1]
MODEL = RUN.parents[2]
ROOT = next(p for p in MODEL.parents if (p/'tools/project_core').is_dir())
REGION = ROOT/'regions/LME/LME_014/LME_014.xlsx'
HANDOFF = MODEL/'model_validation/evidence/researcher_review_20261114/adoption_handoff.json'
PACKAGE = RUN/'outputs/retained_package_v2'
PREFIX = 'retained_adoption_20261114'
KEYS = ['new_GE', 'new_TE_EEfix', 'new_WithEgestion']
OPTIONS = dict(zip(KEYS, ['GE', 'TE', 'With Egestion']))
HANDOFF_SHA = 'ac7dbd7962a319e3b1209e45d1ba9e8efae33e7660b758483fa9322735001464'
DOCX_SHA = '2854655b494fc8d9220c86962da02f043d9f1180a86dc9bb77d310787af072be'
CANONICAL_SHA = '9880e521a406974367530ffb06f13392714dba57b9645c38a1b1448926d83d17'
REASON = ('NOT_RUN for approved source_exact_returns_to_36 runtime; original 111 WithEgestion '
          'coefficients and diagnostics are historical, not approved for this runtime, and retained '
          'exactly in the linked pre-adoption archive. No new solve or Monte Carlo was performed.')
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def rel(path, base=ROOT): return Path(path).resolve().relative_to(Path(base).resolve()).as_posix()
def fingerprint(path): return sha(path) if Path(path).is_file() else None
def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
def require(condition, message):
    if not condition: raise ValueError(message)
def near(a, b): return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-12)
def check_inputs(values):
    for name, expected in values.items():
        path = (ROOT/name).resolve()
        require(path.is_relative_to(ROOT) and fingerprint(path) == expected, 'Consumed input changed: '+name)
def frame_records(frame):
    require(frame['type']=='dataframe' and frame['shape']==[len(frame['index']),len(frame['columns'])], 'Bad encoded frame')
    return {i:dict(zip(frame['columns'], row)) for i,row in zip(frame['index'],frame['data'])}
def scalar(value):
    if isinstance(value,dict) and value.get('type')=='float':
        require(value.get('value')=='nan','Unsupported nonfinite display scalar'); return None
    return value
def flatten(value):
    result={}
    def visit(path, item):
        if isinstance(item,dict):
            for k,v in item.items():visit((*path,str(k)),v)
        elif isinstance(item,(list,tuple)): result['_'.join((*path[:-1],'n_'+path[-1]))]=len(item)
        else:result['_'.join(path)]=item
    for k,v in value.items():visit((str(k),),v)
    return result


def authenticate(original, *, historical_region=None, check_original_bytes=True):
    """Authenticate saved bytes and independently reconcile matrices, scopes and catch."""
    from tools.project_core.workbooks.workbooks import records
    require(sha(HANDOFF)==HANDOFF_SHA,'Approved handoff changed')
    require(sha(MODEL/'model.json')==CANONICAL_SHA,'Canonical changed')
    require(sha(MODEL/'model_validation/validation.docx')==DOCX_SHA,'Signed report changed')
    handoff=read(HANDOFF); consumed={HANDOFF,MODEL/'model.json',MODEL/'model_validation/validation.docx',SCRIPT}
    refs={}
    def reference(item):
        path=(HANDOFF.parent/item['path']).resolve()
        require(path.is_relative_to(ROOT) and sha(path)==item['sha256'],'Handoff source mismatch: '+item['path'])
        consumed.add(path); refs[rel(path)]=item['sha256']; return path
    for item in [handoff['canonical_input'],handoff['native_source'],handoff['execution_provenance'],*handoff['executed_code'].values(),*handoff['input_state_references'].values()]:reference(item)
    if check_original_bytes:
        for name,digest in handoff['protected_artifact_hashes_at_preparation'].items():reference({'path':name,'sha256':digest})
    provenance=read(reference(handoff['execution_provenance']))
    runtime_document=read(reference(handoff['input_state_references']['effective_runtime']))
    runtime=runtime_document['runtime']; config=handoff['actual_configuration']
    require(config['detritus_ids']==[35,36] and config['det_collapse_mode']=='never' and config['det_open_mode']=='none','Unapproved pool configuration')
    require(config['use_ee_floor'] is True and config['ee_floor']==.1 and config['ee_threshold']==.1 and config['floor_applications']==1,'Unapproved floor configuration')
    require(runtime_document['floor_application_count']==1 and runtime['ee_floor_info']['use_ee_floor'] is True,'Floor execution mismatch')
    groups=frame_records(runtime['_groups_df']); names={i:r['group_name'] for i,r in groups.items()}
    source_groups=records(original,'Selected model groups','Groups')
    require(len(groups)==37 and names=={int(r['seq']):r['group_name'] for r in source_groups},'Group identity mismatch')
    require(names[35]=='Discards' and names[36]=='Detritus','Separate pools missing')
    require(groups[35]['detritus_stock_residual']==config['negative_discard_stock_residual']==-.20750363203745528,'Residual changed')
    returns=frame_records(runtime['_discard_returns'])
    require(set(runtime['_discard_returns']['columns'])=={35,36},'Return destinations changed')
    require(all(row[35]==0 for row in returns.values()),'Fishery return incorrectly assigned to Discards35')
    require(near(math.fsum(row[36] for row in returns.values()),config['fishery_return_total']) and config['fishery_return_destination']==36,'Fishery return total mismatch')
    source_returns=read(reference(handoff['input_state_references']['source_return_matrix']))['matrix']
    require(frame_records(source_returns)==returns,'Effective returns differ from authenticated native source matrix')
    ledger=frame_records(runtime['ee_floor_ledger'])
    require(set(ledger)==set(groups) and sum(row['applied'] for row in ledger.values())==8,'Floor ledger identity differs')
    require(near(math.fsum(row['external_mortality_export'] for row in ledger.values()),runtime['ee_floor_info']['external_mortality_export_total']),'Floor sink total differs')
    coefficients=handoff['coefficient_records']; require(len(coefficients)==222,'Expected 222 coefficients')
    actual={(r['method'],r['scope'],r['group']):r['sppr'] for r in records(original,'Selected model groups','Group SPPR')}
    expected={}; full={}; counts={}
    for key in KEYS[:2]:
        info=handoff['methods'][key]; document=read(reference(info['saved_full_return'])); full[key]=document
        require(document['scenario']=='source_exact_returns_to_36' and document['execution']=='returned','Incorrect full return')
        require(document['diagnostic']==info['diagnostic'] and document['diagnostic']['status']=='WARN','Diagnostic changed')
        require(document['diagnostic']['model_input']['is_model_balanced'] is True and document['diagnostic']['balance']['is_balanced'] is True,'Strict balances failed')
        require(document['call']==info['actual_call'],'Recorded call differs')
        matrix=document['SPPR']['dataframe']; matrix_rows=frame_records(matrix)
        require(set(matrix_rows)==set(groups) and set(matrix['columns'])=={37,36,35,22,12},'SPPR axes differ')
        require(all(isinstance(v,(int,float)) and math.isfinite(v) and v>=-1e-12 for r in matrix_rows.values() for v in r.values()),'SPPR finite/sign mask changed')
        for scope, ids in document['source_scopes'].items():
            values=frame_records(document['scope_coefficients'][scope]['frame'])
            require(set(values)==set(groups),'Scope rows differ')
            for group,row in values.items():
                value=next(iter(row.values()))
                require(near(value,math.fsum(matrix_rows[group][c] for c in ids)),'Scope differs from source matrix sum')
                expected[key,scope,names[group]]=value
            field={'all':'ppr_all','inner':'ppr_inner','PP':'ppr_pp_only'}[scope]
            total=math.fsum(next(iter(values[g].values()))*groups[g]['catch'] for g in groups)
            require(near(total,info['source_model_footprint'][field]),'Catch-weighted source footprint differs')
        counts[key]=111
    incoming={(r['method'],r['scope'],r['group_name']):r['sppr'] for r in coefficients}
    require(len(incoming)==222 and incoming==expected,'Handoff coefficients do not exactly match saved returns')
    historical=handoff['historical_WithEgestion_preservation']
    historical_values={(r['method'],r['scope'],r['group_name']):r['sppr'] for r in historical['coefficient_records']}
    require(len(historical_values)==111 and all(actual[k]==v for k,v in historical_values.items()),'Historical WithE coefficients changed')
    require(historical['execution_flags'] is None and historical['code_identity'] is None,'Unknown historical identity was invented')
    engines={name:rel(reference(item),MODEL) for name,item in handoff['executed_code'].items() if name!='executed_runner'}
    hashes={name:handoff['executed_code'][name]['sha256'] for name in engines}
    require(hashes==provenance['engine_hashes'],'Executed code identity differs')
    constructor={k:v for k,v in config['loader_settings'].items() if k!='initialization_mode'}
    evidence=[{'relative_path':rel(p,MODEL),'sha256':sha(p),'original_source_hash':CANONICAL_SHA} for p in sorted(consumed) if p.is_relative_to(MODEL) and p not in {SCRIPT,MODEL/'sppr_source.xlsx',MODEL/'results/result_manifest.json',MODEL/'results/regional_snapshot.xlsx'}]
    flags={'constructor':constructor,'diagnostics':{'det_collapse_mode':'never','det_open_mode':'none','det_theta':1.0,'det_external_sppr':0.0,'thresholds':provenance['effective_thresholds']},
           'methods':{OPTIONS[k]:{a:b for a,b in handoff['methods'][k]['actual_call'].items() if a not in {'TE_option','short','flat','return_sppr'}} for k in KEYS[:2]},
           'engine_sources':engines,'engine_source_hashes':hashes,'configuration_evidence':evidence,
           'runtime_initialization':{'kind':'retained_scenario','configuration_id':'source_exact_returns_to_36','reexecution_supported':False,
               'description':config['initialization'],'constructor_role':'Recorded completed initialization settings; this adoption does not invoke a loader',
               'executed_runner':{'relative_path':rel(reference(handoff['executed_code']['executed_runner']),MODEL),'sha256':handoff['executed_code']['executed_runner']['sha256']},
               'states':{k:{'relative_path':rel((HANDOFF.parent/v['path']).resolve(),MODEL),'sha256':v['sha256'],'json_pointer':v.get('json_pointer')} for k,v in handoff['input_state_references'].items()},
               'fishery_return_destination':36,'fishery_return_total':config['fishery_return_total'],'floor_applications':1,'detritus_ids':[35,36]}}
    # The native source ledger lies outside model; its already authenticated
    # origin belongs to the handoff, not the model-local resolver evidence list.
    from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
    flags=resolve_audited_configuration(MODEL,original,{'canonical_model_sha256':CANONICAL_SHA,'effective_flags':flags})
    from tools.scientific_helpers.sppr import method_coverage as adapter
    for action in (lambda:adapter._constructor(flags,MODEL/'model.json'),lambda:adapter._load(MODEL/'model.json',{},flags)):
        try:action()
        except ValueError as error:require('Unsupported retained runtime initialization' in str(error),'Unexpected stock guard failure')
        else:raise ValueError('Custom runtime reached a stock loader')
    return handoff,runtime,full,incoming,historical_values,flags,consumed,{'imported_GE_TE':222,'changed_GE_TE_exact':sum(actual[k]!=v for k,v in incoming.items()),'historical_WithE':111,'effective_groups':37,'floor_groups':len(runtime['ee_floor_info']['affected_groups']),'stock_constructor_and_loader_blocked':True}


def source_cells(path):
    import openpyxl
    workbook=openpyxl.load_workbook(path,read_only=True,data_only=False)
    try:return {sheet.title:[list(row) for row in sheet.values] for sheet in workbook}
    finally:workbook.close()


def exact_source(path, book, handoff):
    """Patch only authorized coefficient/footprint cells; preserve other XML bytes."""
    from tools.project_core.validation.researcher_review import sheet_xml,S
    from tools.project_core.workbooks.workbooks import records
    from openpyxl.utils import get_column_letter
    cells=source_cells(path); wanted={}
    coeff={(r['scope'],r['group'],r['method']):r['sppr'] for r in records(book,'Selected model groups','Group SPPR')}
    for scope in ('all','inner','PP'):
        table=cells['sppr_'+scope]; header=table[0]; group_col=header.index('group_name')
        wanted['sppr_'+scope]={get_column_letter(j+1)+str(i):coeff[scope,row[group_col],key] for i,row in enumerate(table[1:],2) for j,key in enumerate(header) if key in KEYS}
    table=cells['footprint']; header=table[0]
    wanted['footprint']={get_column_letter(j+1)+str(i):(handoff['methods'][row[0]]['source_model_footprint'].get(field) if row[0] in handoff['methods'] else None)
                         for i,row in enumerate(table[1:],2) for j,field in enumerate(header) if j>0 and row[0] in KEYS}
    # The project writer rounds new diagnostic floats to sixteen digits; use
    # the exact authenticated scalar values already in the regional table.
    header, health=book['Diagnostics']['model_health']
    wanted['model_health']={get_column_letter(j+1)+str(i):value
        for i,row in enumerate(health,2) for j,value in enumerate(row)
        if isinstance(value,(int,float)) and not isinstance(value,bool)}
    with zipfile.ZipFile(path) as archive:
        replacements={}
        for name,numbers in wanted.items():
            member,sheet=sheet_xml(archive,name); found=set()
            for cell in sheet.iter(f'{{{S}}}c'):
                address=cell.get('r')
                if address not in numbers:continue
                require(cell.find(f'{{{S}}}f') is None,'Cannot overwrite formula coefficient')
                value=numbers[address]; found.add(address)
                for child in list(cell):cell.remove(child)
                if value is None:cell.attrib.pop('t',None)
                else:cell.set('t','n'); ET.SubElement(cell,f'{{{S}}}v').text=repr(value)
            require({a for a,v in numbers.items() if v is not None}.issubset(found),'Missing source cells')
            replacements[member]=ET.tostring(sheet,encoding='utf-8')
        # Source group metadata and the empty historical MC diagnostic sheet
        # are immutable inputs, including their original blank-row structure.
        with zipfile.ZipFile(RUN/'inputs/pre_adoption/sppr_source.xlsx') as baseline:
            for name in ('groups_df','mc_diagnostics'):
                member,_=sheet_xml(archive,name);old_member,_=sheet_xml(baseline,name)
                replacements[member]=baseline.read(old_member)
        parts=[(item,replacements.get(item.filename,archive.read(item.filename))) for item in archive.infolist()]
    with zipfile.ZipFile(path,'w') as archive:
        for item,data in parts:archive.writestr(item,data)


def prepare(package_path=None, *, progress=print):
    from tools.project_core.calculations import coverage
    from tools.project_core.calculations.regional import set_setting
    from tools.project_core.calculations.snapshots import dependencies
    from tools.project_core.workbooks.workbooks import read_book,overview,records,table_dict,digest_tables
    package=Path(package_path or PACKAGE).resolve()
    require(package.is_relative_to(RUN/'outputs'),'Stage outside authorized work directory')
    if (package/'preparation.json').is_file():return verify_package(package)
    require(not package.exists() or not any(package.iterdir()),'Partial package exists; inspect then choose a new output directory')
    original=read_book(REGION)
    require(overview(original)['selected_model_id']==MODEL.name and overview(original)['results_model_id']==MODEL.name,'Actual selected/results model changed')
    h,runtime,full,incoming,historical,flags,consumed,counts=authenticate(original)
    consumed.update([REGION,MODEL/'sppr_source.xlsx',MODEL/'results/result_manifest.json',MODEL/'results/regional_snapshot.xlsx'])
    consumed.update(ROOT/'tools/project_core'/name for name in coverage._arithmetic_identity())
    consumed.update([ROOT/'tools/scientific_helpers/sppr/method_coverage.py',ROOT/'tools/scientific_helpers/sppr/configuration.py',ROOT/'tools/scientific_code/PPREstimation/create_PPRS_excel.py'])
    hashes={rel(p):sha(p) for p in sorted(consumed)}
    backup=RUN/'inputs/pre_adoption'; backup_index={}
    for path in [REGION,MODEL/'sppr_source.xlsx',MODEL/'results/regional_snapshot.xlsx',MODEL/'results/result_manifest.json']:
        target=backup/path.name; target.parent.mkdir(parents=True,exist_ok=True)
        require(not target.exists() or sha(target)==sha(path),'Historical archive already differs')
        if not target.exists():shutil.copyfile(path,target)
        backup_index[rel(path)]={'relative_path':rel(target,MODEL),'sha256':sha(target)}
    historical_path=backup/'historical_WithEgestion.json'; write(historical_path,h['historical_WithEgestion_preservation'])
    backup_index['historical_WithEgestion']={'relative_path':rel(historical_path,MODEL),'sha256':sha(historical_path)}
    write(backup/'backup_index.json',backup_index)
    hashes.update({rel(MODEL/v['relative_path']):v['sha256'] for v in backup_index.values()})
    hashes[rel(backup/'backup_index.json')]=sha(backup/'backup_index.json')
    stage_model=package/'model'; stage_region=package/'regional/LME_014.xlsx'; evidence=stage_model/'results/diagnostics'/PREFIX
    evidence.mkdir(parents=True);stage_region.parent.mkdir(parents=True)
    shutil.copyfile(REGION,stage_region);shutil.copyfile(MODEL/'sppr_source.xlsx',stage_model/'sppr_source.xlsx')
    context=coverage._context(ROOT,MODEL/'model.json',flags)
    outcomes={}; old_status={(r['method'],r['scope']):r['status'] for r in records(original,'PPR','Annual') if r['catch_basis']=='landings' and r['unidentified']=='method' and r['metric']=='ppr'}
    for key in KEYS:
        scopes={scope:{group:value for (method,s,group),value in incoming.items() if method==key and s==scope} for scope in ('all','inner','PP')}
        certificate={'schema_version':1,'kind':'authenticated_retained_runtime_adoption' if key in KEYS[:2] else 'historical_method_unavailable_in_current_runtime',
            'method':key,'canonical_model_sha256':CANONICAL_SHA,'configuration_id':'source_exact_returns_to_36','handoff':{'relative_path':rel(HANDOFF,MODEL),'sha256':HANDOFF_SHA},
            'scientific_execution_performed_by_adoption':False,'full_inventory_claim':False,'stock_engine_equivalence_claim':False,
            'effective_flags':flags,'scopes':scopes,'historical_package_backup':backup_index}
        if key in KEYS[:2]:
            certificate.update(saved_full_return=h['methods'][key]['saved_full_return'],saved_full_return_path_base=rel(HANDOFF.parent,MODEL),diagnostic=h['methods'][key]['diagnostic'],actual_call=h['methods'][key]['actual_call'],reconciliation=counts)
            statuses={scope:old_status[key,scope]+'; GE/TE WARN: separate Discards35 residual -0.20750363203745528; approved source returns once to Detritus36; EE floor ON 0.1' for scope in scopes}
            require(all(v.startswith('provisional:') for v in statuses.values()),'Original restrictions require explicit review')
            outcome={'status':'reused','reason':'Authenticated retained GE/TE full return; no fresh scientific execution; original diagnosis WARN','scopes':scopes,'annual_status':statuses,
                     'retained_diagnostics_flat':{'TE_option':OPTIONS[key],**flatten(h['methods'][key]['diagnostic'])}}
        else:
            certificate.update(reason=REASON,historical_execution_flags=None,historical_code_identity=None,historical_coefficient_count=111)
            outcome={'status':'NOT_RUN','reason':REASON,'scopes':scopes,'annual_status':{scope:'unavailable: '+REASON for scope in scopes}}
        target=evidence/(key+'.json');write(target,certificate)
        outcome['evidence']={'path':PREFIX+'/'+target.name,'sha256':sha(target),'availability':'present'};outcome['evidence_kind']=certificate['kind'];outcomes[key]=outcome
    book=copy.deepcopy(original);coverage._apply_outcomes(book,MODEL.name,outcomes,KEYS)
    for row in book['Selected model groups']['Group SPPR'][1]:row[4]=incoming.get((row[3],row[2],row[1]))
    info=runtime['ee_floor_info'];ledger=frame_records(runtime['ee_floor_ledger'])
    book['Diagnostics']['EE floor']=(['field','value'],[['use_ee_floor',True],['ee_floor',.1],['ee_threshold',.1],['affected_group_count',len(info['affected_groups'])],['external_mortality_export_total',info['external_mortality_export_total']],['assumption',info['assumption']],['provenance','Approved retained source_exact_returns_to_36 runtime; one floor application; Groups remains source metadata']])
    book['Diagnostics']['EE floor groups']=table_dict([{'group_seq':i,**{k:scalar(v) for k,v in row.items()}} for i,row in ledger.items()])
    book['Diagnostics']['Retained adoption']=table_dict([{'topic':'current runtime','detail':'GE/TE source_exact_returns_to_36; separate Discards35 and Detritus36; WARN retained; no new solve; no MC'},
        {'topic':'historical WithEgestion','detail':REASON},{'topic':'source versus effective groups','detail':'Selected model groups/Groups and sppr_source groups_df unchanged. Effective 37-group runtime and floor ledger authenticated by manifest.'},
        {'topic':'historical additional diagnostics','detail':'Unchanged Scientific review, size/allocation impact and other custom diagnostic tables retain their original historical configuration; they are not recalculated or relabeled as current runtime results.'},
        {'topic':'historical archive','detail':rel(backup,MODEL)}])
    coverage._arithmetic(book,REGION,MODEL/'model.json',flags,original,invalidated_methods=KEYS)
    set_setting(book,'production_eligible',False)
    set_setting(book,'calculation_status','provisional: original mapping/geography restrictions retained; GE/TE WARN in approved separate-pool runtime; WithEgestion unavailable for this runtime')
    set_setting(book,'sppr_engine_hashes',json.dumps(flags['engine_source_hashes'],sort_keys=True))
    progress('Saving staged regional arithmetic using 222 authenticated coefficients; WithE current slots unavailable')
    coverage._update_source(stage_model/'sppr_source.xlsx',book,outcomes,replace_methods=KEYS)
    exact_source(stage_model/'sppr_source.xlsx',book,h)
    set_setting(book,'results_source_sha256',sha(stage_model/'sppr_source.xlsx'))
    saved=coverage._save_calculation(stage_region,book,MODEL/'model.json',flags,copy.deepcopy(book),invalidated_methods=KEYS)
    snapshot=stage_model/'results/regional_snapshot.xlsx';shutil.copyfile(stage_region,snapshot)
    for key,digest in coverage._method_rows(saved)[1].items():outcomes[key]['group_rows_sha256']=digest
    manifest={'schema_version':1,'unit_id':'LME_014','model_id':MODEL.name,'snapshot_selected_model_id':MODEL.name,'timestamp':datetime.now(timezone.utc).isoformat(),
        'canonical_model_sha256':CANONICAL_SHA,'present_canonical_model_sha256':CANONICAL_SHA,'snapshot_sha256':sha(snapshot),'coefficient_source_sha256':sha(stage_model/'sppr_source.xlsx'),
        'effective_flags':flags,'code_identity':flags['engine_source_hashes'],'provenance_status':'Authenticated retained GE/TE source_exact_returns_to_36 runtime; WithEgestion NOT_RUN here, original 111 coefficients archived with unknown historical execution identity; no engine equivalence or full inventory claim',
        'dependencies':dependencies(saved),'artifacts':{'snapshot':'regional_snapshot.xlsx','model':'../model.json','coefficients':'../sppr_source.xlsx'},'historical_package_backup':backup_index,
        'retained_adoption':{'handoff':{'relative_path':rel(HANDOFF,MODEL),'sha256':HANDOFF_SHA},'approved_configuration':'source_exact_returns_to_36','executed_runtime_provenance':h['execution_provenance'],'provenance_path_base':rel(HANDOFF.parent,MODEL),
            'context_roles':{'method_coverage.context':'Current retained-evidence verification and arithmetic environment; not an SPPR execution claim','method_coverage.context.code_identity.create_PPRS_excel.py':'Current registry identity only; not the executed scientific runner','executed_numeric_engine':'code_identity plus handoff executed_runner and saved full-return provenance'},
            'source_group_metadata_preserved':True,'runtime_group_metadata':flags['runtime_initialization']['states']['effective_37_group_metadata'],'full_inventory_claim':False,'stock_engine_equivalence_claim':False,'scientific_execution_performed':False,'counts':counts},
        'method_coverage':{'schema_version':1,'scope':'Only retained approved GE/TE and explicit current WithE unavailability; no full inventory','expected_methods':KEYS,'context':context,'methods':outcomes,'execution_evidence':{},'arithmetic_code_identity':coverage._arithmetic_identity(),'protected_inputs_sha256':coverage._preserved_inputs(original)}}
    write(stage_model/'results/result_manifest.json',manifest)
    promotions=[{'source':rel(stage_region,package),'target':rel(REGION),'sha256':sha(stage_region)}]
    for source in sorted(p for p in stage_model.rglob('*') if p.is_file()):
        target=MODEL/source.relative_to(stage_model);promotions.append({'source':rel(source,package),'target':rel(target),'sha256':sha(source)});hashes.setdefault(rel(target),fingerprint(target))
    check_inputs(hashes)
    plan={'schema_version':1,'prepared_utc':datetime.now(timezone.utc).isoformat(),'package':rel(package),'unit_id':'LME_014','model_id':MODEL.name,'consumed_inputs':hashes,'context':context,'expected_methods':KEYS,
        'protected_inputs_sha256':coverage._preserved_inputs(original),'protected_groups_sha256':digest_tables(original['Selected model groups']['Groups']),'promotions':promotions,'counts':counts,'ready_for_apply':False,'numerical_adoption_performed':False,'historical_package_backup':backup_index}
    write(package/'preparation.json',plan)
    verify_package(package)
    plan['ready_for_apply']=True;write(package/'preparation.json',plan)
    return plan


def verify_package(package_path=None, *, check_consumed=True):
    from tools.project_core.calculations import coverage
    from tools.project_core.calculations.regional import result_hash
    from tools.project_core.workbooks.workbooks import read_book,records,overview,input_hash,YEARS,digest_tables
    from tools.scientific_helpers.sppr.ppr_scopes import read_scopes
    package=Path(package_path or PACKAGE).resolve();require(package.is_relative_to(RUN/'outputs'),'Package outside work directory')
    plan=read(package/'preparation.json')
    if check_consumed:check_inputs(plan['consumed_inputs'])
    for item in plan['promotions']:
        source=(package/item['source']).resolve();target=(ROOT/item['target']).resolve()
        require(source.is_relative_to(package) and target.is_relative_to(ROOT) and sha(source)==item['sha256'],'Promotion mismatch')
        require(target==REGION or target.is_relative_to(MODEL/'results') or target==MODEL/'sppr_source.xlsx','Promotion outside approved package')
    book=read_book(package/'regional/LME_014.xlsx');manifest=read(package/'model/results/result_manifest.json')
    backup=RUN/'inputs/pre_adoption';original=read_book(backup/'LME_014.xlsx')
    for item in plan['historical_package_backup'].values():require(sha(MODEL/item['relative_path'])==item['sha256'],'Historical archive mismatch')
    h,runtime,full,incoming,historical,flags,consumed,counts=authenticate(original,check_original_bytes=False)
    require(flags==manifest['effective_flags'] and counts==plan['counts'],'Runtime or reconciliation identity mismatch')
    require(coverage._preserved_inputs(book)==plan['protected_inputs_sha256'],'Protected inputs changed')
    require(book['Selected model groups']['Groups']==original['Selected model groups']['Groups'],'Source group metadata changed')
    require(book['Classic PPR']==original['Classic PPR'],'Independent Classic PPR changed')
    for name,data in original['Diagnostics'].items():
        if name not in {'model_health','Method coverage','EE floor','EE floor groups'}:require(book['Diagnostics'][name]==data,'Unrelated diagnostic table changed: '+name)
    for key in ('selected_model_id','selection_rationale','source_note','taxon_detail_year','catch_basis'):
        require(overview(book).get(key)==overview(original).get(key),'Preserved setting changed: '+key)
    require(overview(book).get('production_eligible') is False,'Provisional production restriction removed')
    require(overview(book)['calculation_input_sha256']==input_hash(book) and overview(book)['calculation_result_sha256']==result_hash(book),'Stale arithmetic fingerprints')
    actual={(r['method'],r['scope'],r['group']):r['sppr'] for r in records(book,'Selected model groups','Group SPPR')}
    require(len(actual)==333 and all(actual[k]==v for k,v in incoming.items()) and all(actual[k] is None for k in historical),'Exact current coefficients or WithE missingness differ')
    old_scopes=read_scopes(backup/'sppr_source.xlsx');new_scopes=read_scopes(package/'model/sppr_source.xlsx')
    for scope in ('all','inner','PP'):
        methods,groups=new_scopes[scope];oldmethods,oldgroups=old_scopes[scope]
        for group,values in groups.items():
            for key in KEYS:require(values[methods.index(key)]==actual[key,scope,group],'Source/regional exact coefficient differs')
            require(oldgroups[group][oldmethods.index(KEYS[2])]==historical[KEYS[2],scope,group],'Historical source recovery differs')
    old_cells=source_cells(backup/'sppr_source.xlsx');new_cells=source_cells(package/'model/sppr_source.xlsx')
    require(new_cells['groups_df']==old_cells['groups_df'],'Source groups_df changed')
    require(new_cells['mc_diagnostics']==old_cells['mc_diagnostics'],'Source MC evidence changed')
    require(new_cells['run_notes'][:len(old_cells['run_notes'])]==old_cells['run_notes'],'Source historical notes changed')
    for row in records(book,'PPR','Annual'):
        if row['method']==KEYS[2] and row['metric']!='catch':require(all(row.get(y) is None for y in YEARS),'Current WithE annual values remain usable')
        if row['method']==KEYS[2] and row['metric']=='ppr':require(not str(row['status']).startswith(('ok','provisional:')),'Current WithE is numerically eligible')
        if row['method'] in KEYS[:2] and row['metric']=='ppr' and not (row['unidentified']=='simple' and row['scope']!='all'):
            require(str(row['status']).startswith('provisional:') and 'WARN' in row['status'],'GE/TE restrictions missing')
    for row in records(book,'PPR','Taxon SPPR'):
        if row['method']==KEYS[2]:require(row.get('sppr') is None,'WithE taxon coefficient reusable')
    for row in records(book,'PPR','Taxon PPR inspected year'):
        if row['method']==KEYS[2]:require(row.get('sppr') is None and row.get('ppr') is None,'WithE taxon detail remains numeric')
    for row in records(book,'PPR–NPP','Ratios'):
        if row['method']==KEYS[2]:require(all(row.get(y) is None for y in YEARS),'WithE ratios remain numeric')
    require(manifest['snapshot_sha256']==sha(package/'regional/LME_014.xlsx')==sha(package/'model/results/regional_snapshot.xlsx'),'Snapshot not exact')
    require(manifest['method_coverage']['arithmetic_code_identity']==coverage._arithmetic_identity(),'Staging arithmetic code drift')
    require(coverage._source_matches(package/'model',book,KEYS),'Canonical source coherence check failed')
    require(coverage._package_cache_valid(package/'model',package/'regional/LME_014.xlsx',manifest,plan['context'],KEYS),'Scoped three-outcome package coherence failed')
    require(read(backup/'historical_WithEgestion.json')==h['historical_WithEgestion_preservation'],'Historical payload recovery differs')
    write(RUN/'qa/verification.json',{'passed':True,'package':rel(package),'preparation_sha256':sha(package/'preparation.json'),'counts':counts,
        'protected_inputs_sha256':plan['protected_inputs_sha256'],'protected_groups_exact':True,'source_groups_and_MC_exact':True,
        'current_WithE_coefficient_annual_taxon_ratio_unavailable':True,'historical_WithE_exact_recovery':True,
        'snapshot_exact_copy':True,'full_inventory_claim':False,'stock_engine_equivalence_claim':False,'scientific_solve_performed':False})
    return plan


def apply(publication, package_path=None):
    """Install verified staged bytes only inside the caller's guarded transaction."""
    from tools.project_core.registry.publication import _ACTIVE,publication_write
    from tools.project_core.calculations.coverage import _write_bytes
    package=Path(package_path or PACKAGE).resolve()
    require(publication in _ACTIVE.get() and publication.root==ROOT,'Active caller publication required')
    lock=ROOT/'.project-write.lock';require(lock.is_file() and lock.read_text().strip()==str(os.getpid()),'Caller must hold process project writer lock')
    plan=verify_package(package,check_consumed=False);targets={p['target'] for p in plan['promotions']}
    require(plan['ready_for_apply'] is True,'Package has not completed preparation verification')
    check_inputs({k:v for k,v in plan['consumed_inputs'].items() if k not in targets})
    if all(fingerprint(ROOT/p['target'])==p['sha256'] for p in plan['promotions']):return {'status':'already_applied','changed_units':['LME_014'],'written_paths':[]}
    check_inputs(plan['consumed_inputs']);written=[]
    for item in plan['promotions']:
        target=ROOT/item['target']
        data=(package/item['source']).read_bytes()
        require(hashlib.sha256(data).hexdigest()==item['sha256'],'Promotion bytes changed before write')
        with publication_write(target,fingerprint=item['sha256']):_write_bytes(target,data,expected_sha256=plan['consumed_inputs'][item['target']])
        written.append(str(target))
    check_inputs({k:v for k,v in plan['consumed_inputs'].items() if k not in targets})
    return {'status':'applied','changed_units':['LME_014'],'written_paths':written,'written_hashes':{str(ROOT/p['target']):p['sha256'] for p in plan['promotions']}}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','verify']);parser.add_argument('--package',type=Path);args=parser.parse_args()
    result=prepare(args.package) if args.command=='prepare' else verify_package(args.package)
    print(json.dumps({'package':result['package'],'promotions':len(result['promotions']),'counts':result['counts'],'ready_for_apply':result['ready_for_apply']},ensure_ascii=False))
