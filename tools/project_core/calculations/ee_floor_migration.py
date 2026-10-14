"""Explicit EE-floor upgrade with immutable baseline evidence and limited reruns.

Historical omission of the floor remains omission in the compressed baseline.
Compatibility certificates describe reused numerical dependencies, never a new
execution, RNG draw, or researcher approval.
"""
from __future__ import annotations

import base64
import ast
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path

NUMERICAL_FIELDS = ('_DC', '_det_fate', 'p', 'q', 'catch', 'predation', 'growth',
                    'immigration', 'emigration', 'net_migration', 'respiration',
                    'egestion', 'M0', 'det_export', 'EE', 'GE', 'GS', 'TL',
                    'seq2name', 'name2seq')
REGISTRY_PREDECESSOR_SHA256 = '86fafff4d66fa81d960c69a4971d9de6cb5a5125f50631530c277213c6771032'
REGISTRY_PROTECTED_AST_SHA256 = '917d919df0b0a67b0357387921dbbfda64745ea0b4a2cea050740f9277e877b6'
REGISTRY_METADATA_FUNCTIONS = {'load_model','write_model_excel','run_directory','main',
    '_file_sha256','_export_constructor','_export_identity','_record_execution','_resume_matches'}


def registry_compatibility(recorded_sha256):
    """Admit only the verified predecessor and unchanged numerical registry AST."""
    from tools.scientific_helpers.sppr.method_coverage import ENGINE
    source=(ENGINE/'create_PPRS_excel.py').read_bytes(); live=hashlib.sha256(source).hexdigest()
    if live==recorded_sha256:return {'historical_sha256':recorded_sha256,'current_sha256':live,'exact_bytes':True}
    if recorded_sha256!=REGISTRY_PREDECESSOR_SHA256:return None
    tree=ast.parse(source.decode('utf-8-sig'))
    tree.body=[node for node in tree.body if not (
        isinstance(node,ast.FunctionDef) and node.name in REGISTRY_METADATA_FUNCTIONS) and not (
        isinstance(node,ast.If) and ast.unparse(node.test)=="__name__ == '__main__'")]
    for node in tree.body:
        if isinstance(node,ast.Import):
            node.names=[alias for alias in node.names if alias.name not in {'argparse','hashlib','inspect','json','zipfile'}]
    tree.body=[node for node in tree.body if not(isinstance(node,ast.Import) and not node.names)]
    digest=hashlib.sha256(ast.dump(tree,include_attributes=False).encode('utf-8')).hexdigest()
    if digest!=REGISTRY_PROTECTED_AST_SHA256:return None
    return {'historical_sha256':recorded_sha256,'current_sha256':live,'protected_ast_sha256':digest,
            'excluded_functions':sorted(REGISTRY_METADATA_FUNCTIONS),
            'excluded_imports':['argparse','hashlib','inspect','json','zipfile'],
            'excluded_module_if':"__name__ == '__main__'",'numerical_registry_unchanged':True}


def _authenticated_context(saved,actual):
    from tools.project_core.calculations.coverage import _same_context
    from tools.scientific_helpers.sppr.retained_methods import _scientific_options
    if not isinstance(saved,dict):return 'legacy',None
    normalized=copy.deepcopy(actual); proof=None
    previous=saved.get('code_identity') or {}; current=normalized.get('code_identity') or {}
    old_registry=previous.get('create_PPRS_excel.py'); new_registry=current.get('create_PPRS_excel.py')
    if old_registry and new_registry and old_registry!=new_registry:
        proof=registry_compatibility(old_registry)
        if not proof or proof['current_sha256']!=new_registry:return 'changed',None
        normalized['code_identity']['create_PPRS_excel.py']=old_registry
    if _same_context(saved,normalized):return 'exact',proof
    for key in ('model_sha256','dependencies','code_identity'):
        old=saved.get(key); new=normalized.get(key)
        if old is None:continue
        if isinstance(old,dict) and isinstance(new,dict):
            if any(old[name]!=new[name] for name in old.keys() & new.keys()):return 'changed',proof
        elif old!=new:return 'changed',proof
    old_options=_scientific_options(saved.get('flags')); new_options=_scientific_options(normalized.get('flags'))
    if any(old_options[key]!=new_options[key] for key in old_options.keys() & new_options.keys()):return 'changed',proof
    return 'legacy',proof


def authenticate_package(model_dir,manifest,*,reviewed_model_sha256=None):
    from tools.project_core.workbooks.workbooks import sha
    model=Path(model_dir).resolve(); actual=sha(model/'model.json')
    recorded=manifest.get('canonical_model_sha256') or manifest.get('input_sha256') or reviewed_model_sha256
    if recorded!=actual:raise ValueError('Original EE-floor package model identity is unknown or changed')
    for relative,key in [('sppr_source.xlsx','coefficient_source_sha256'),
                         ('results/regional_snapshot.xlsx','snapshot_sha256')]:
        expected=manifest.get(key); path=model/relative
        if expected and (not path.is_file() or sha(path)!=expected):
            raise ValueError('Original EE-floor package source/snapshot changed: '+relative)


def target_flags(original, use_ee_floor, ee_floor, calculation_hash):
    if not isinstance(use_ee_floor, bool):
        raise ValueError('use_ee_floor must be Boolean')
    if isinstance(ee_floor, bool) or not isinstance(ee_floor, (int, float)) or not math.isfinite(ee_floor) or not 0 <= ee_floor <= 1:
        raise ValueError('ee_floor must be finite and in [0, 1]')
    if not isinstance(original, dict) or not isinstance(original.get('constructor'), dict):
        raise ValueError('Recorded audited constructor settings are required for migration')
    result = copy.deepcopy(original)
    result['constructor'].update(use_ee_floor=use_ee_floor, ee_floor=float(ee_floor))
    result['calculation_engine_upgrade'] = 'ee_floor_v1'
    result['calculation_engine_sha256'] = calculation_hash
    if original.get('calculation_engine_sha256') != calculation_hash:
        result.pop('calculation_engine_source',None)
    return result


def _identity(model, fields):
    from tools.scientific_helpers.sppr.method_coverage import encode_lossless, _json_bytes
    value = {key:getattr(model, key) for key in fields if hasattr(model, key)}
    value['PP'] = model.get_PP_seq(); value['DET'] = model.get_DET_seq(); value['Import'] = model.get_Import_seq()
    return hashlib.sha256(_json_bytes(encode_lossless(value))).hexdigest()


def compatible_methods(before, after, expected):
    numerical = (_identity(before, NUMERICAL_FIELDS), _identity(after, NUMERICAL_FIELDS))
    if numerical[0] == numerical[1]:
        return {key:{'reason':'All numerical runtime dependencies unchanged', 'before_sha256':numerical[0],
                     'after_sha256':numerical[1]} for key in expected}
    fixed = ('_DC', 'catch', 'TL', 'GE', 'seq2name', 'name2seq')
    trophic = (_identity(before, fixed), _identity(after, fixed))
    if trophic[0] != trophic[1]:
        return {}
    from tools.scientific_helpers.sppr.method_coverage import encode_lossless, _json_bytes
    computed=[hashlib.sha256(_json_bytes(encode_lossless(model.get_TL(break_cycles=True,DET_as_PP=True)))).hexdigest()
              for model in (before,after)]
    if computed[0] != computed[1]:return {}
    consumption=[]
    for model in (before,after):
        regular=model.get_Regular_seq() if hasattr(model,'get_Regular_seq') else sorted(set(model.q.index)-set(model.get_PP_seq()+model.get_DET_seq()+model.get_Import_seq()))
        consumption.append(hashlib.sha256(_json_bytes(encode_lossless(model.q.loc[regular]))).hexdigest())
    if consumption[0]!=consumption[1]:return {}
    return {key:{'reason':'Fixed transfer efficiency and trophic-level/catch/source identities unchanged',
                 'before_sha256':trophic[0], 'after_sha256':trophic[1], 'calculated_TL_sha256':computed[0],
                 'regular_consumption_sha256':consumption[0]}
            for key in expected if key in {'SPPR_1986','SPPR_1995_TE0.1'}}


def _write_gzip(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8')
    path.write_bytes(gzip.compress(payload, mtime=0))
    return {'path':path.name, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def save_baseline(model_dir, outbound, manifest, directory):
    """Preserve raw workbook and evidence bytes before replacing their live paths."""
    model = Path(model_dir).resolve(); files = {}
    candidates = dict(outbound)
    coverage = manifest.get('method_coverage', {})
    references = [value.get('evidence') for value in coverage.get('methods', {}).values()]
    references.extend(coverage.get('execution_evidence', {}).values())
    for reference in references:
        if not reference:
            continue
        path = (model/'results/diagnostics'/str(reference.get('path',''))).resolve()
        if not path.is_relative_to(model) or not path.is_file():
            raise ValueError('Missing recorded migration baseline evidence')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != reference.get('sha256'):
            raise ValueError('Changed migration baseline evidence: ' + str(path))
        candidates[path] = data
    for path, data in candidates.items():
        if data is None:
            continue
        path = Path(path).resolve()
        # The current regional workbook is external to the model. Its origin is
        # recorded explicitly; it does not become another active source workbook.
        relative = path.relative_to(model).as_posix() if path.is_relative_to(model) else 'outgoing_regional_workbook_bytes'
        import os
        files[relative] = {'origin_model_relative_path':os.path.relpath(path,model).replace('\\','/'),
                           'sha256':hashlib.sha256(data).hexdigest(), 'base64':base64.b64encode(data).decode('ascii')}
    value = {'schema_version':1, 'kind':'immutable_before_ee_floor', 'historical_manifest':copy.deepcopy(manifest), 'files':files}
    fingerprint = hashlib.sha256(json.dumps(value, sort_keys=True).encode('utf-8')).hexdigest()
    return _write_gzip(Path(directory)/(fingerprint+'.baseline.json.gz'), value)


def prepare(model_path, original_flags, expected, request):
    """Load the audited baseline and requested runtime without executing methods."""
    from tools.scientific_helpers.sppr.method_coverage import ENGINE, _constructor, _load, _runtime
    calculation = ENGINE/'PPRCalculator.py'
    flags = target_flags(original_flags, request['use_ee_floor'], request['ee_floor'],
                         hashlib.sha256(calculation.read_bytes()).hexdigest())
    if flags == original_flags:
        return None
    old, old_source, old_warnings = _load(model_path, _constructor(original_flags,model_path), original_flags)
    new, new_source, new_warnings = _load(model_path, _constructor(flags,model_path), flags)
    if old_source != new_source:
        raise ValueError('EE-floor migration altered canonical source loading')
    protected = ('_DC','_det_fate','catch','predation','immigration','emigration','net_migration','egestion','respiration')
    if _identity(old, protected) != _identity(new, protected):
        raise ValueError('EE-floor migration changed protected runtime inputs')
    from tools.scientific_helpers.sppr.method_coverage import encode_lossless, _json_bytes
    living=sorted(set(old.p.index)-set(old.get_DET_seq()+old.get_Import_seq()))
    living_state=[]
    for calculator in (old,new):
        state={name:getattr(calculator,name).loc[living] for name in ('p','q','growth')}
        frame=calculator.get_groups_df()
        state['biomass']=frame.loc[living,'biomass']
        living_state.append(_json_bytes(encode_lossless(state)))
    if living_state[0]!=living_state[1]:
        raise ValueError('EE-floor migration changed living production, consumption, accumulation, or biomass')
    groups=new.get_groups_df().copy()
    for name in ('source_EE','source_M0','EE_before_floor','M0_before_floor','external_mortality_export'):
        groups[name]=getattr(new,name).reindex(groups.index)
    return {'flags':flags, 'compatible':compatible_methods(old,new,expected), 'effective_groups':groups,
            'before_runtime':_runtime(old), 'after_runtime':_runtime(new), 'old_warnings':old_warnings,
            'new_warnings':new_warnings, 'info':copy.deepcopy(new.ee_floor_info),
            'ledger':new.ee_floor_ledger.copy(), 'calculation_code':calculation.read_bytes()}


def retained_outcomes(manifest, compatible, book, directory, context, baseline, *,
                      original_context=None, model_dir=None, reviewed_model_sha256=None, dry_run=False):
    """Certify saved outcomes against unchanged dependencies, retaining provenance."""
    from tools.project_core.workbooks.workbooks import records, digest_tables
    old = manifest.get('method_coverage', {}).get('methods', {})
    if not compatible:return {}
    if model_dir is None:raise ValueError('Model directory is required to authenticate retained EE-floor results')
    model=Path(model_dir).resolve(); authenticate_package(model,manifest,reviewed_model_sha256=reviewed_model_sha256)
    actual_original=original_context or context
    authentication, registry_proof=_authenticated_context(manifest.get('method_coverage',{}).get('context'),actual_original)
    if authentication=='changed':return {}
    legacy={}
    if authentication=='legacy' or any(not old.get(key,{}).get('group_rows_sha256') or not old.get(key,{}).get('evidence') for key in compatible):
        if dry_run:return {}
        from tools.scientific_helpers.sppr.retained_methods import adopt_saved_methods
        legacy=adopt_saved_methods(model,manifest,actual_original,book,directory,list(compatible),
                                  reviewed_model_sha256=reviewed_model_sha256)
    result = {}
    for key, proof in compatible.items():
        if key not in old and key not in legacy:
            continue
        previous = copy.deepcopy(legacy.get(key) or old[key]); scopes = {scope:{} for scope in ('all','inner','PP')}
        selected = [r for r in records(book,'Selected model groups','Group SPPR') if r['method']==key]
        saved_rows=[r for r in book['Selected model groups']['Group SPPR'][1] if r[3]==key]
        if previous.get('group_rows_sha256') and previous['group_rows_sha256']!=digest_tables(saved_rows):
            continue
        names={r['group_name'] for r in records(book,'Selected model groups','Groups')}
        if len(selected)!=3*len(names) or any(r.get('model_id')!=model.name for r in selected):continue
        if any({r['group'] for r in selected if r['scope']==scope}!=names for scope in scopes):continue
        reference=previous.get('evidence') or {}; path=(model/'results/diagnostics'/str(reference.get('path',''))).resolve()
        if key in legacy:path=Path(directory)/reference['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=reference.get('sha256'):continue
        if key not in legacy and not path.is_relative_to(model):continue
        try:
            if path.suffix=='.gz':
                with gzip.open(path,'rt',encoding='utf-8') as stream:document=json.load(stream)
            else:document=json.loads(path.read_text(encoding='utf-8-sig'))
        except (OSError,ValueError):continue
        evidence_method=document.get('method') or document.get('settings',{}).get('method')
        identity=document.get('identity',{})
        evidence_model=document.get('model_sha256') or identity.get('model_sha256')
        if evidence_method and evidence_method!=key:continue
        if evidence_model and evidence_model!=actual_original.get('model_sha256'):continue
        if identity.get('model_id') and identity['model_id']!=model.name:continue
        if previous.get('settings'):
            from tools.scientific_helpers.sppr.method_coverage import method_settings
            if previous['settings']!=method_settings(key,actual_original['flags'],model/'model.json'):continue
        for row in selected:
            scopes[row['scope']][row['group']] = row['sppr']
        status = {r['scope']:r['status'] for r in records(book,'PPR','Annual')
                  if r['method']==key and r['catch_basis']=='landings' and r['unidentified']=='method' and r['metric']=='ppr'}
        if set(status) != {'all','inner','PP'}:
            raise ValueError('Cannot certify incomplete retained method statuses: ' + key)
        certificate = {'schema_version':1, 'kind':'ee_floor_dependency_compatibility', 'method':key,
                       'numerical_execution':False, 'dependency_proof':proof, 'baseline':baseline,
                       'historical_method_outcome':copy.deepcopy(old.get(key)),
                       'historical_context':copy.deepcopy(manifest.get('method_coverage', {}).get('context')),
                       'historical_effective_flags':copy.deepcopy(manifest.get('effective_flags')),
                       'current_context':context, 'scopes':scopes, 'annual_status':status,
                       'original_context_authentication':authentication,'registry_compatibility':registry_proof,
                       'legacy_adoption_evidence':document if key in legacy else None}
        evidence = previous.get('evidence') if dry_run else _write_gzip(Path(directory)/(key+'.ee_floor_reused.json.gz'), certificate)
        previous.update(status='reused', reason='Saved method retained after exact numerical dependency comparison; no new execution',
                        preserve_saved=True, evidence_kind='ee_floor_dependency_compatibility', evidence=evidence,
                        scopes=scopes, annual_status=status, historical_method_outcome=copy.deepcopy(old.get(key)))
        if dry_run:previous['compatibility_certificate']=certificate
        result[key] = previous
    return result


def add_diagnostics(book, migration):
    from tools.project_core.workbooks.workbooks import table_dict, clean
    info=migration['info']
    fields={'use_ee_floor':info.get('use_ee_floor'),'ee_floor':info.get('ee_floor'),
            'assumption':info.get('assumption'),'affected_group_count':len(info.get('affected_groups',[])),
            'external_mortality_export_total':info.get('external_mortality_export_total'),
            'provenance':'Explicit EE-floor calculation migration; original signed review retained separately'}
    book.setdefault('Diagnostics', {})['EE floor'] = (['field','value'],
        [[key,clean(value)] for key,value in fields.items()])
    ledger = migration['ledger']
    values = ledger.reset_index().to_dict(orient='records') if hasattr(ledger, 'reset_index') else ledger
    book['Diagnostics']['EE floor groups'] = table_dict(values) if values else (['group'],[])


def preserve_restrictions(book, original):
    """Retain each scope/catch restriction, while adding fresh restrictions."""
    from tools.project_core.workbooks.workbooks import rows, numeric_status
    previous={tuple(row[:6]):str(row[6]) for row in rows(original,'PPR','Annual')}
    blocked=set()
    for row in rows(book,'PPR','Annual'):
        prior=previous.get(tuple(row[:6])); current=str(row[6])
        if prior and prior!='ok':
            if prior.startswith('provisional:'):
                row[6]=current if current.startswith('provisional:') else prior if current=='ok' else prior+'; refreshed diagnosis: '+current
            elif current=='ok' or current not in prior:
                row[6]=prior if current=='ok' else prior+'; refreshed diagnosis: '+current
        if not numeric_status(row[6]) and row[5] in {'ppr','covered_catch','min_tC','max_tC'}:
            row[7:]=[None]*len(row[7:]);blocked.add(tuple(row[:5]))
    for row in rows(book,'PPR–NPP','Ratios'):
        if tuple(row[:5]) in blocked:row[6:]=[None]*len(row[6:])
