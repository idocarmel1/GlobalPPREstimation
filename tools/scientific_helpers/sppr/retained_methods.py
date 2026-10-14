"""Certify compatible saved direct returns without running or repairing a model."""
from __future__ import annotations

import json
import math
import os
import copy
from pathlib import Path

import numpy as np
import pandas as pd

from .method_coverage import (_constructor, _defaults, _engine, _hash_bytes, _save,
                              encode_lossless, method_settings, method_inventory, NEGATIVE_TOLERANCE, DET_KEYS)
from .ppr_scopes import read_scopes


METHOD_OPTIONS = {'new_GE':'GE','new_TE_EEfix':'TE','new_WithEgestion':'With Egestion'}


def decode_typed(value):
    """Read the retained JSON type vocabulary; never unpickle or evaluate code."""
    if not isinstance(value,dict) or 'type' not in value:
        raise ValueError('Expected a lossless typed JSON value')
    kind=value['type']
    if kind=='null':return None
    if kind in ('str','bool','int','float'):
        raw=value['value']
        if kind=='float':return float(raw)
        if kind=='int':return int(raw)
        if kind=='bool' and not isinstance(raw,bool):raise ValueError('Invalid Boolean')
        return raw
    if kind in ('nan','NaN'):return float('nan')
    if kind in ('positive_infinity','posinf'):return float('inf')
    if kind in ('negative_infinity','neginf'):return -float('inf')
    if kind in ('list','tuple'):
        values=[decode_typed(item) for item in value['items']]
        return tuple(values) if kind=='tuple' else values
    if kind=='dict':
        pairs=[(decode_typed(k),decode_typed(v)) for k,v in value['items']]
        result=dict(pairs)
        if len(result)!=len(pairs):raise ValueError('Duplicate typed dictionary keys')
        return result
    if kind=='DataFrame':
        index,columns=decode_typed(value['index']),decode_typed(value['columns'])
        frame=pd.DataFrame([[decode_typed(cell) for cell in row] for row in value['data']],
                           index=index,columns=columns)
        if not frame.index.is_unique or not frame.columns.is_unique:raise ValueError('Duplicate matrix axes')
        return frame
    raise ValueError(f'Unsupported retained evidence type: {kind}')


def _read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def _sha(path):return _hash_bytes(path.read_bytes())


def _active_run(model, manifest):
    """Resolve an explicit adopted run pointer, including old region-relative paths."""
    relative = manifest.get('evidence')
    if not isinstance(relative, str) or Path(relative).is_absolute():return None
    candidates = {(base/relative).resolve() for base in (model,*model.parents)}
    candidates = {path for path in candidates if path.is_relative_to(model)
                  and path.name=='run_manifest.json' and path.is_file()}
    return next(iter(candidates)) if len(candidates)==1 else None


def _rows(book, sheet, table):
    header,rows=book.get(sheet,{}).get(table,([],[]))
    return [dict(zip(header,row)) for row in rows]


def _equal(a,b):
    if a is None or b is None:return a is None and b is None
    return math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-12)


def _scientific_options(flags):
    """Compare recorded options only, without loading an engine or its defaults."""
    if isinstance(flags, str):
        try: flags = json.loads(flags)
        except ValueError: return {}
    if not isinstance(flags, dict): return {}
    result = {}
    def flatten(prefix, value):
        if isinstance(value, dict):
            for key, item in value.items(): flatten(prefix + (str(key),), item)
        else: result[prefix] = value
    if isinstance(flags.get('constructor'), dict):
        flatten(('constructor',), flags['constructor'])
    for key in ('calculation_engine_upgrade', 'calculation_engine_sha256'):
        if key in flags:
            result[(key,)] = flags[key]
    common = flags.get('diagnostics') or {}
    methods = flags.get('methods') or {}
    if not isinstance(common, dict) or not isinstance(methods, dict):
        raise ValueError('Invalid recorded scientific configuration')
    for option in ('GE', 'TE', 'With Egestion'):
        selected = methods.get(option) or methods.get(option.replace(' ', '_')) or {}
        if not isinstance(selected, dict): raise ValueError('Invalid recorded method configuration')
        options = {key: value for key, value in common.items() if key in (*DET_KEYS, 'thresholds')}
        options.update({key: value for key, value in selected.items() if key in (*DET_KEYS, 'thresholds')})
        flatten(('methods', option), options)
    if isinstance(flags.get('mc'), dict): flatten(('mc',), flags['mc'])
    return result


def _saved_cell_equal(a, b):
    """Allow only Excel's last-digit serialization noise; never alter either cell."""
    from tools.project_core.workbooks.workbooks import digest_tables
    if a is None or b is None: return a is None and b is None
    if (isinstance(a, bool) or isinstance(b, bool) or
        not isinstance(a, (int, float)) or not isinstance(b, (int, float)) or
        not math.isfinite(a) or not math.isfinite(b)): return False
    return digest_tables([a]) == digest_tables([b]) or math.isclose(a, b, rel_tol=1e-15, abs_tol=0.)


def _saved_source_tables(path):
    """Read actual saved cells, without the source reader's nonfinite coercion."""
    import openpyxl
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=False)
    try:
        return {scope: [list(row) for row in workbook['sppr_'+scope].values]
                if 'sppr_'+scope in workbook.sheetnames else [] for scope in ('all', 'inner', 'PP')}
    finally: workbook.close()


def _prior_method_trace(model, manifest, key):
    """Keep earlier execution evidence without claiming it was re-executed."""
    coverage = manifest.get('method_coverage')
    prior = coverage.get('methods', {}).get(key) if isinstance(coverage, dict) and isinstance(coverage.get('methods'), dict) else None
    if not isinstance(prior, dict): return None
    trace = {'recorded_outcome': copy.deepcopy(prior)}
    reference = prior.get('evidence')
    if not isinstance(reference, dict) or not isinstance(reference.get('path'), str): return trace
    path = (model/'results/diagnostics'/reference['path']).resolve()
    if not path.is_relative_to(model):
        trace['evidence_check'] = {'status': 'not_checked', 'reason': 'Recorded path is outside the model'}
    elif not path.is_file():
        trace['evidence_check'] = {'status': 'missing', 'recorded_sha256': reference.get('sha256')}
    else:
        actual = _sha(path)
        trace['evidence_check'] = {'status': 'matching' if actual == reference.get('sha256') else 'hash_mismatch',
            'path': path.relative_to(model).as_posix(), 'recorded_sha256': reference.get('sha256'), 'actual_sha256': actual}
    return trace


def adopt_saved_methods(model_dir, manifest, context, book, evidence_dir, expected,
                        *, reviewed_model_sha256=None):
    """Bind existing aggregate results without rerunning or upgrading provenance.

    Missing execution metadata is not a reason to replace saved coefficients.
    Changed known model/configuration/source identities require an explicit
    scientific refresh and raise. Incomplete method tables are omitted; callers
    must distinguish those from absent methods and must not silently rerun them.
    ``preserve_saved`` requires callers to retain the original coefficient,
    annual and diagnostic rows, including failed and unavailable outcomes.
    """
    from tools.project_core.workbooks.workbooks import digest_tables
    model = Path(model_dir).resolve(); evidence_dir = Path(evidence_dir).resolve()
    coefficients = _rows(book, 'Selected model groups', 'Group SPPR')
    expected = list(dict.fromkeys(expected))
    present = {row.get('method') for row in coefficients}
    wanted = [key for key in expected if key in present]
    if not wanted: return {}
    if any(not isinstance(key, str) or Path(key).name != key or '/' in key or '\\' in key for key in wanted):
        raise ValueError('Invalid saved method identity')
    model_hash = _sha(model/'model.json')
    recorded_hashes = [manifest.get('canonical_model_sha256') or manifest.get('input_sha256'),
                       reviewed_model_sha256]
    if not any(recorded_hashes) or context.get('model_sha256') != model_hash or any(
            value and value != model_hash for value in recorded_hashes):
        raise ValueError('Saved model identity differs or is unknown; explicit scientific refresh required')
    overview = {row.get('field'): row.get('value') for row in _rows(book, 'Overview', 'Settings')}
    for value in (manifest.get('model_id'), overview.get('results_model_id')):
        if value and value != model.name: raise ValueError('Saved results belong to a different model')
    if overview.get('results_model_sha256') and overview['results_model_sha256'] != model_hash:
        raise ValueError('Saved workbook model identity differs; explicit scientific refresh required')
    if any(row.get('model_id') != model.name for row in coefficients if row.get('method') in wanted):
        raise ValueError('Saved coefficient rows belong to a different model')
    requested_options = _scientific_options(context.get('flags'))
    historical_flags = manifest.get('effective_flags')
    floor_keys = {('constructor', 'use_ee_floor'), ('constructor', 'ee_floor'),
                  ('calculation_engine_upgrade',), ('calculation_engine_sha256',)}
    requested_floor = {key: value for key, value in requested_options.items() if key in floor_keys}
    if requested_floor and any(_scientific_options(historical_flags).get(key) != value
                               for key, value in requested_floor.items()):
        raise ValueError('Saved EE-floor calculation identity is different or unknown; explicit scientific refresh required')
    for recorded in (historical_flags, overview.get('effective_loader_flags'), overview.get('sppr_configuration')):
        original_options = _scientific_options(recorded)
        changed = [path for path in original_options.keys() & requested_options.keys()
                   if original_options[path] != requested_options[path]]
        if changed:
            raise ValueError('Saved scientific configuration differs at ' + ', '.join('.'.join(path) for path in sorted(changed)) +
                             '; explicit scientific refresh required')
    artifacts = []
    for path, declared in ((model/'model.json', model_hash),
                           (model/'sppr_source.xlsx', manifest.get('coefficient_source_sha256')),
                           (model/'results/regional_snapshot.xlsx', manifest.get('snapshot_sha256'))):
        if not path.is_file():
            if declared: raise ValueError('Recorded saved source artifact is missing: ' + path.name)
            continue
        actual = _sha(path)
        if declared and actual != declared: raise ValueError('Saved source artifact identity differs: ' + path.name)
        artifacts.append({'path': os.path.relpath(path, evidence_dir).replace('\\', '/'), 'sha256': actual,
                          'matches_recorded_hash': bool(declared)})
    source_path = model/'sppr_source.xlsx'
    source_tables = _saved_source_tables(source_path) if source_path.is_file() else None
    group_rows = _rows(book, 'Selected model groups', 'Groups')
    names = [row.get('group_name') for row in group_rows]
    if not names or any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ValueError('Saved group identities are missing or duplicated')
    group_names = set(names)
    annual_rows = _rows(book, 'PPR', 'Annual')
    diagnostic_tables = {name: [copy.deepcopy(header), copy.deepcopy(values)]
                         for name, (header, values) in book.get('Diagnostics', {}).items()}
    coefficient_header, coefficient_values = book['Selected model groups']['Group SPPR']
    annual_header, annual_values = book.get('PPR', {}).get('Annual', ([], []))
    candidates = {}
    for key in wanted:
        selected = [row for row in coefficients if row.get('method') == key]
        if len(selected) != 3*len(names) or any(row.get('scope') not in ('all', 'inner', 'PP') for row in selected): continue
        scopes = {}; annual = {}; source_cells = {}; complete = True
        for scope in ('all', 'inner', 'PP'):
            scoped_rows = [row for row in selected if row.get('scope') == scope]
            values = {row.get('group'): row.get('sppr') for row in scoped_rows}
            if len(scoped_rows) != len(names) or set(values) != group_names:
                complete = False; break
            if any(value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or
                   not math.isfinite(value)) for value in values.values()):
                raise ValueError('Saved coefficient cells contain unsupported or nonfinite values')
            primary = [row for row in annual_rows if row.get('method') == key and row.get('scope') == scope and
                       row.get('metric') == 'ppr' and row.get('catch_basis') == 'landings' and row.get('unidentified') == 'method']
            if len(primary) != 1 or not isinstance(primary[0].get('status'), str) or not primary[0]['status']:
                complete = False; break
            if primary[0].get('model_id') != model.name: raise ValueError('Saved annual rows belong to a different model')
            scopes[scope] = values; annual[scope] = primary[0]['status']
            if source_tables is not None:
                table = source_tables[scope]
                if not table or table[0].count(key) != 1 or table[0].count('group_name') != 1:
                    raise ValueError('Saved source method or scope is missing or duplicated: ' + key + '/' + scope)
                group_index, method_index = table[0].index('group_name'), table[0].index(key)
                entries = [[row[group_index], row[method_index]] for row in table[1:]
                           if len(row) > max(group_index, method_index) and row[group_index] is not None]
                source_values = dict(entries)
                if len(entries) != len(names) or set(source_values) != group_names or any(
                        not _saved_cell_equal(value, source_values[group]) for group, value in values.items()):
                    raise ValueError('Saved source coefficients disagree with retained Group SPPR: ' + key + '/' + scope)
                source_cells[scope] = entries
        if not complete: continue
        saved_coefficients = [copy.deepcopy(row) for row in coefficient_values
                              if dict(zip(coefficient_header, row)).get('method') == key]
        saved_annual = [copy.deepcopy(row) for row in annual_values if dict(zip(annual_header, row)).get('method') == key]
        if any(dict(zip(annual_header, row)).get('model_id') != model.name for row in saved_annual):
            raise ValueError('Saved annual rows belong to a different model')
        certificate = {
            'schema_version': 1, 'evidence_kind': 'retained_saved_method', 'status': 'reused', 'preserve_saved': True,
            'method': key, 'model_sha256': model_hash, 'adoption_context': copy.deepcopy(context),
            'historical_execution': {'effective_flags': copy.deepcopy(historical_flags),
                'code_identity': copy.deepcopy(manifest.get('code_identity')), 'verified_by_adoption': False,
                'note': 'Recorded historical fields only. Unknown settings, engine, RNG and execution provenance remain unknown; adoption performs no scientific execution.'},
            'scopes': scopes, 'annual_status': annual,
            'saved_group_sppr': [copy.deepcopy(coefficient_header), saved_coefficients],
            'saved_annual': [copy.deepcopy(annual_header), saved_annual],
            'saved_diagnostic_tables': diagnostic_tables, 'source_scoped_cells': source_cells,
            'prior_method_trace': _prior_method_trace(model, manifest, key),
            'table_hashes': {'group_sppr': digest_tables([coefficient_header, saved_coefficients]),
                'annual': digest_tables([annual_header, saved_annual]),
                'diagnostics': digest_tables([[name, *table] for name, table in diagnostic_tables.items()]),
                'source_scopes': digest_tables([[scope, rows] for scope, rows in source_cells.items()]) if source_tables is not None else None},
            'availability': {'aggregate_scopes': 'present', 'full_return': 'not_recovered_by_adoption',
                'per_basal_source_matrix': 'not_recovered_by_adoption', 'individual_mc_samples': 'not_recovered_by_adoption'},
            'reconciliation': {'canonical_model_identity': True, 'complete_saved_group_scopes': True,
                'saved_statuses_and_diagnostics_preserved': True, 'source_scopes_compared': source_tables is not None,
                'source_cell_comparison': '16 significant digit digest, otherwise rtol=1e-15, atol=0; original cells retained',
                'historical_execution_verified': False}, 'artifacts': artifacts}
        outcome = {'status': 'reused', 'reason': 'Saved aggregate result retained without numerical execution; historical execution provenance not verified by adoption',
            'preserve_saved': True, 'evidence_kind': 'retained_saved_method', 'scopes': scopes, 'annual_status': annual}
        health = [row for row in _rows(book, 'Diagnostics', 'model_health')
                  if (row.get('TE_option') or row.get('config_TE_option')) == METHOD_OPTIONS.get(key)] if key in METHOD_OPTIONS else []
        mc = [row for row in _rows(book, 'Diagnostics', 'mc_diagnostics') if row.get('method') == key] if key.startswith('MC_') else []
        if len(health) == 1: outcome['retained_diagnostics_flat'] = copy.deepcopy(health[0])
        if len(mc) == 1: outcome['mc_diagnostics'] = copy.deepcopy(mc[0])
        candidates[key] = (certificate, outcome)
    outcomes = {}
    if candidates: evidence_dir.mkdir(parents=True, exist_ok=True)
    for key, (certificate, outcome) in candidates.items():
        if certificate['prior_method_trace'] is not None:
            outcome['prior_method_trace'] = copy.deepcopy(certificate['prior_method_trace'])
        outcome['evidence'] = _save(evidence_dir/f'{key}.adopted.json.gz', encode_lossless(certificate))
        outcomes[key] = outcome
    return outcomes


def _verify_matrix(directory,name,frame,typed):
    paths=[directory/f'{name}.npy',directory/f'{name}_axes.json',directory/f'{name}_masks.npz']
    matrix=np.load(paths[0],allow_pickle=False)
    np.testing.assert_equal(matrix,frame.to_numpy(dtype=float))
    axes=_read(paths[1])
    if ([r['id'] for r in axes['rows']]!=frame.index.tolist() or
        [r['id'] for r in axes['columns']]!=frame.columns.tolist() or
        axes['shape']!=list(frame.shape)):
        raise ValueError('Retained axes do not match the full return')
    null=np.array([[cell.get('type')=='null' for cell in row] for row in typed['data']])
    expected={'null':null,'nan':np.isnan(matrix)&~null,
              'positive_infinity':np.isposinf(matrix),'negative_infinity':np.isneginf(matrix)}
    with np.load(paths[2],allow_pickle=False) as masks:
        for kind,mask in expected.items():np.testing.assert_equal(masks[kind],mask)
    return axes,paths


def _reuse_audited_export(model,manifest,context,book,evidence_dir,expected):
    """Certify saved aggregate exports; never imply discarded matrices survived."""
    import openpyxl
    outcomes={}
    try:
        flags=context.get('flags')
        if not flags:return outcomes
        source=model/'sppr_source.xlsx';snapshot=model/'results/regional_snapshot.xlsx'
        source_hash=_sha(source);model_hash=_sha(model/'model.json')
        if (model_hash!=context.get('model_sha256') or
            model_hash!=(manifest.get('canonical_model_sha256') or manifest.get('input_sha256')) or
            source_hash!=manifest.get('coefficient_source_sha256') or
            _sha(snapshot)!=manifest.get('snapshot_sha256')):return outcomes
        exporter,_,calculator,thresholds=_engine(flags,model/'model.json')
        all_keys=method_inventory()
        constructor=_constructor(flags,model/'model.json')
        defaults=_defaults(calculator.SPPR_new)
        # The recorded exporter hash establishes its fixed variant/error policy.
        # Admit only audited flags equal to that exact exported policy.
        for key in all_keys:
            settings=method_settings(key,flags,model/'model.json');kwargs=settings['kwargs']
            if key.startswith(('new_','sym_','MC_')):
                for name in DET_KEYS:
                    if name=='fix_EE_0_cases':continue
                    if kwargs.get(name)!=defaults[name]:return outcomes
            expected_fix=False if key=='new_TE_noEEfix' else defaults['fix_EE_0_cases']
            if key.startswith(('new_','sym_')) and kwargs.get('fix_EE_0_cases')!=expected_fix:return outcomes
            if key.startswith('MC_') and kwargs['method_kwargs'].get('fix_EE_0_cases')!=defaults['fix_EE_0_cases']:return outcomes
            if key.startswith('new_') and kwargs['thresholds']!=thresholds:return outcomes
            if key.startswith('MC_') and (settings['seed'] is not None or
                kwargs['TE_error_percent']!=10 or kwargs['TE_error_cut_percent']!=20):return outcomes
        records=[]
        for base in ('model_validation/evidence','model_validation/work','results/diagnostics'):
            directory=model/base
            if directory.is_dir():
                for name in ('refresh_configuration.json','export_manifest.json','run_manifest.json'):
                    records.extend(directory.rglob(name))
        matched=None
        for path in sorted(records):
            if not path.resolve().is_relative_to(model):continue
            record=_read(path)
            if not isinstance(record,dict):continue
            if record.get('fresh_sppr_sha256')!=source_hash or record.get('canonical_model_sha256')!=model_hash:continue
            if set(record.get('methods',[]))!=set(all_keys) or set(record.get('method_status',{}))!=set(all_keys):continue
            engines=record.get('engine_hashes')
            if not isinstance(engines,dict) or any(engines.get(name)!=context['code_identity'].get(name)
                for name in ('ModelData.py','PPRCalculator.py','utils.py','create_PPRS_excel.py')):continue
            recorded_constructor=record.get('constructor')
            if not isinstance(recorded_constructor,dict):continue
            # A historical omission is not evidence that a new default floor
            # was enabled in the recorded execution.
            if constructor.get('use_ee_floor') is True and (
                    recorded_constructor.get('use_ee_floor') is not True or
                    recorded_constructor.get('ee_floor') != constructor.get('ee_floor')):continue
            if {**_defaults(calculator.from_modeldata),**recorded_constructor}!=constructor:continue
            if record.get('mc_samples')!=flags.get('mc',{}).get('n_samples',exporter.DEFAULT_MC_SAMPLES):continue
            if not record.get('monte_carlo_worker_seed'):continue
            matched=(path,record);break
        if matched is None:return outcomes
        path,record=matched
        workbook=openpyxl.load_workbook(source,read_only=True,data_only=True)
        try:
            tables={name:list(workbook[name].values) for name in ('model_health','mc_diagnostics')}
        finally:workbook.close()
        source_health=[dict(zip(tables['model_health'][0],row)) for row in tables['model_health'][1:]]
        source_mc=[dict(zip(tables['mc_diagnostics'][0],row)) for row in tables['mc_diagnostics'][1:]]
        health={row.get('TE_option') or row.get('config_TE_option'):row for row in source_health}
        mc={row.get('method'):row for row in source_mc}
        final_mc={row['method']:row for row in record.get('final_mc_diagnostics',[])}
        for key in all_keys:
            if not key.startswith('MC_'):continue
            if key not in mc or key not in final_mc:return outcomes
            if any(mc[key].get(name)!=value for name,value in final_mc[key].items()):return outcomes
            n,accepted=mc[key].get('n_samples'),mc[key].get('n_accepted')
            if not isinstance(n,(int,float)) or n<=0 or n!=record['mc_samples'] or not isinstance(accepted,(int,float)) or not 0<=accepted<=n:return outcomes
        if any(option not in health for option in METHOD_OPTIONS.values()):return outcomes
        source_scopes=read_scopes(source)
        group_names={row['group_name'] for row in _rows(book,'Selected model groups','Groups')}
        coefficients=_rows(book,'Selected model groups','Group SPPR')
        annual_rows=_rows(book,'PPR','Annual')
        saved_status={(row['scope'],row['method']):row.get('status') for row in annual_rows
            if row.get('metric')=='ppr' and row.get('catch_basis')=='landings' and row.get('unidentified')=='method'}
        scoped={}
        for scope in ('all','inner','PP'):
            methods,groups=source_scopes[scope]
            if not set(all_keys).issubset(methods) or set(groups)!=group_names:return outcomes
            for key in all_keys:
                rows=[row for row in coefficients if row['scope']==scope and row['method']==key and row['model_id']==model.name]
                values={row['group']:row['sppr'] for row in rows}
                if len(rows)!=len(group_names) or set(values)!=group_names:return outcomes
                if any(not _equal(value,groups[group][methods.index(key)]) for group,value in values.items()):return outcomes
                scoped[scope,key]=values
        for key in expected:
            if key not in all_keys:continue
            engine_status=record['method_status'][key]
            if engine_status not in {'ok','timeout','error','failed'}:continue
            settings=method_settings(key,flags,model/'model.json')
            scopes={scope:scoped[scope,key] for scope in ('all','inner','PP')}
            annual={}
            for scope in scopes:
                status=saved_status.get((scope,key))
                if not isinstance(status,str) or not status:raise ValueError('Missing retained annual restriction')
                if scope=='PP' and not settings['source_resolved']:status='unavailable: source scope unsupported'
                elif engine_status!='ok':status='unavailable: retained exporter '+engine_status
                elif not any(v is not None for v in scopes[scope].values()):status='unavailable: no finite coefficients'
                elif key.startswith('MC_') and mc[key]['n_accepted']/mc[key]['n_samples']<.8:
                    status=f"unavailable: MC acceptance {mc[key]['n_accepted']}/{mc[key]['n_samples']} below 80%"
                elif any(v is not None and v<0 for v in scopes[scope].values()) and not status.startswith('provisional:'):
                    status='FAIL: negative SPPR in a source-model group'
                elif key in METHOD_OPTIONS and health[METHOD_OPTIONS[key]].get('status')=='FAIL' and not status.startswith('provisional:'):
                    status='FAIL: configuration diagnostic'
                annual[scope]=status
            certificate={'schema_version':1,'status':'reused','evidence_kind':'retained_aggregate_export',
                'context':context,'settings':settings,'original_export_record':record,
                'original_engine_status':engine_status,'scopes':scopes,'annual_status':annual,
                'source_diagnostic_tables':tables,'original_rng_statement':record['monte_carlo_worker_seed'],
                'availability':{'aggregate_scopes':'present','full_return':'not_retained',
                    'per_basal_source_matrix':'not_retained','individual_mc_samples':'not_retained'},
                'reconciliation':{'source_and_snapshot_hashes':True,'all_canonical_source_scopes':True,
                    'full_return_or_matrix_reconciliation':False,'rtol':1e-10,'atol':1e-12},
                'artifacts':[{'path':os.path.relpath(p,evidence_dir).replace('\\','/'),'sha256':_sha(p)}
                    for p in (path,source,snapshot,model/'model.json')]}
            evidence_dir.mkdir(parents=True,exist_ok=True)
            evidence=_save(evidence_dir/f'{key}.json.gz',encode_lossless(certificate))
            outcomes[key]={'status':'reused' if engine_status=='ok' else 'failed' if engine_status=='error' else engine_status,
                'reason':'; '.join(sorted({v for v in annual.values() if v!='ok'})),
                'evidence_kind':'retained_aggregate_export','original_engine_status':engine_status,
                'scopes':scopes,'annual_status':annual,'settings':settings,'evidence':evidence}
            if key in METHOD_OPTIONS:outcomes[key]['retained_diagnostics_flat']=health[METHOD_OPTIONS[key]]
            if key.startswith('MC_'):outcomes[key]['mc_diagnostics']=mc[key]
    except (OSError,ValueError,TypeError,KeyError,AssertionError):
        return {}
    return outcomes


def reuse_methods(model_dir,manifest,context,book,evidence_dir,expected):
    """Return only certified saved direct methods, otherwise an empty/partial dict.

    A certificate compares source/snapshot hashes, engine and dependency versions,
    effective call options, independent matrix files/axes/masks and all three
    scoped coefficient tables. Rejection merely leaves that method for execution.
    All source evidence is read-only; certificates keep its hashes and full JSON.
    """
    model=Path(model_dir).resolve(); evidence_dir=Path(evidence_dir).resolve()
    outcomes=_reuse_audited_export(model,manifest,context,book,evidence_dir,expected)
    if set(expected).issubset(outcomes):return outcomes
    try:
        flags=context.get('flags')
        if not flags:return outcomes
        source_hash=_sha(model/'model.json')
        manifest_source=manifest.get('canonical_model_sha256') or manifest.get('input_sha256')
        if source_hash!=context['model_sha256'] or source_hash!=manifest_source:return outcomes
        source_workbook_hash=_sha(model/'sppr_source.xlsx')
        declared_source_hash=manifest.get('coefficient_source_sha256')
        if declared_source_hash and source_workbook_hash!=declared_source_hash:return outcomes
        if _sha(model/'results/regional_snapshot.xlsx')!=manifest.get('snapshot_sha256'):return outcomes
        engines=context['code_identity']
        recorded_engines=manifest.get('code_identity')
        if not isinstance(engines,dict):return outcomes
        active_run=_active_run(model,manifest)
        # Older publication manifests retain obsolete descriptive engine_hashes.
        # Their explicit active-run link can authenticate a direct method only
        # after current source/snapshot coefficients and full evidence agree.
        if not isinstance(recorded_engines,dict) or not declared_source_hash:
            if active_run is None:return outcomes
            active=_read(active_run)
            if not isinstance(active,dict):return outcomes
            recorded_engines=active.get('engine')
        if not isinstance(recorded_engines,dict):return outcomes
        if any(recorded_engines.get(name)!=engines.get(name)
               for name in ('ModelData.py','PPRCalculator.py','utils.py')):return outcomes
        constructor=_constructor(flags,model/'model.json')
        source_scopes=read_scopes(model/'sppr_source.xlsx')
        coefficients=_rows(book,'Selected model groups','Group SPPR')
        group_rows=_rows(book,'Selected model groups','Groups')
        group_names={r['group_name'] for r in group_rows}
        manifests=[active_run] if active_run else []
        if active_run is None:
            for base in ('model_validation/work','model_validation/evidence','results/diagnostics'):
                directory=model/base
                if directory.is_dir():manifests.extend(directory.rglob('run_manifest.json'))
        for path in sorted(manifests):
            if not path.resolve().is_relative_to(model):continue
            run=_read(path)
            if not isinstance(run,dict):continue
            if run.get('input_sha256')!=source_hash or run.get('model_id')!=model.name:continue
            if run.get('constructor')!=constructor:continue
            run_engines,packages=run.get('engine'),run.get('packages')
            if not isinstance(run_engines,dict) or not isinstance(packages,dict):continue
            if any(run_engines.get(name)!=engines.get(name) for name in
                   ('ModelData.py','PPRCalculator.py','utils.py')):continue
            if any(value is not None and packages.get(name)!=value
                   for name,value in context.get('dependencies',{}).items()):continue
            if (run.get('constructor_status')!='CONSTRUCTED' or run.get('source_input_unchanged') is not True
                    or run.get('persisted_runtime_reload_exact') is not True):continue
            if not run.get('reconciliation') or not all(value is True for value in run['reconciliation'].values()):continue
            call=run.get('method_call',{})
            if any(call.get(k)!=v for k,v in {'short':False,'flat':False,'return_sppr':True}.items()):continue
            for key in expected:
                if key in outcomes or key not in METHOD_OPTIONS:continue
                option=METHOD_OPTIONS[key]; directory=path.parent/option.replace(' ','_')
                try:
                    full_path=directory/'full_return_lossless.json'
                    typed=_read(full_path); result=decode_typed(typed)
                    if not isinstance(result,tuple) or len(result)!=4:continue
                    report,sppr,a,l=result
                    if not isinstance(report,dict) or not all(isinstance(frame,pd.DataFrame) for frame in (sppr,a,l)):continue
                    settings=method_settings(key,flags,model/'model.json');kwargs=settings['kwargs']
                    if run.get('thresholds')!=kwargs['thresholds']:continue
                    config=report.get('config',{})
                    if config.get('TE_option')!=option or config.get('explicit_TE') is not False:continue
                    if any(config.get(name)!=kwargs[name] for name in
                           ('det_collapse_mode','det_open_mode','det_theta','det_external_sppr')):continue
                    defaults=_defaults(_engine(flags,model/'model.json')[2].SPPR_new)
                    if any(call.get(name,defaults[name])!=kwargs[name] for name in ('DET_TE_vals','fix_EE_0_cases')):continue
                    evidence=[path,full_path,model/'sppr_source.xlsx',model/'results/regional_snapshot.xlsx']
                    if (model/'results/result_manifest.json').is_file():evidence.append(model/'results/result_manifest.json')
                    axes=None
                    for i,(name,frame) in enumerate((('SPPR',sppr),('A',a),('L',l)),start=1):
                        verified,files=_verify_matrix(directory,name,frame,typed['items'][i]);evidence.extend(files)
                        if name=='SPPR':axes=verified
                    row_names={r['id']:r['name'] for r in axes['rows']}
                    if set(row_names.values())!=group_names:continue
                    source_types={r['id']:r['trophic_type'] for r in axes['columns']}
                    scopes={};annual={}
                    for scope in ('all','inner','PP'):
                        columns=[c for c in sppr.columns if scope=='all' or
                                 (source_types[c]!='Import' and (scope!='PP' or source_types[c]!='DET'))]
                        sums=sppr[columns].sum(axis=1,min_count=1)
                        recorded={r['group']:r['sppr'] for r in coefficients
                                  if r['method']==key and r['scope']==scope and r['model_id']==model.name}
                        if set(recorded)!=group_names:raise ValueError('Incomplete retained coefficient rows')
                        source_keys,source_groups=source_scopes[scope]
                        if key not in source_keys:raise ValueError('Source coefficient method absent')
                        j=source_keys.index(key)
                        for seq,value in sums.items():
                            number=float(value) if np.isfinite(value) else None;name=row_names[seq]
                            if not _equal(number,recorded[name]) or not _equal(recorded[name],source_groups[name][j]):
                                raise ValueError('Retained source scopes disagree')
                        scopes[scope]=recorded
                        if not any(v is not None for v in recorded.values()):status='unavailable: no finite coefficients'
                        elif np.isinf(sppr.to_numpy()).any():status='unavailable: nonfinite source contributions'
                        elif (sppr.to_numpy() < -NEGATIVE_TOLERANCE).any():status='FAIL: negative SPPR in a source-model group'
                        elif report.get('status')=='FAIL':status='FAIL: configuration diagnostic'
                        else:status='ok'
                        annual[scope]=status
                    evidence_dir.mkdir(parents=True,exist_ok=True)
                    certificate={'schema_version':1,'status':'reused','model_sha256':source_hash,
                        'context':context,'settings':settings,'scopes':scopes,'annual_status':annual,
                        'coefficient_source_sha256':source_workbook_hash,
                        'coefficient_source_identity_basis':('manifest hash and full-return reconciliation' if declared_source_hash
                            else 'explicit active run and complete source/snapshot coefficient reconciliation'),
                        'active_run':str(active_run.relative_to(model)) if active_run else None,
                        'full_return_lossless':typed,'source_axes':axes,
                        'reconciliation':{'source_and_snapshot_hashes':True,'all_source_scopes':True,
                            'full_return_vs_matrices_axes_and_masks':True,'rtol':1e-10,'atol':1e-12},
                        'artifacts':[{'path':os.path.relpath(p,evidence_dir).replace('\\','/'),
                                      'sha256':_sha(p)} for p in evidence]}
                    saved=_save(evidence_dir/f'{key}.json.gz',certificate)
                    restrictions=sorted({status for status in annual.values() if status!='ok'})
                    outcomes[key]={'status':'reused','reason':'; '.join(restrictions),
                        'scopes':scopes,'annual_status':annual,'diagnostics':encode_lossless(report),
                        'settings':settings,'evidence':saved}
                except (OSError,ValueError,TypeError,KeyError,AssertionError):
                    continue
    except (OSError,ValueError,TypeError,KeyError,AssertionError):
        return outcomes
    return outcomes
