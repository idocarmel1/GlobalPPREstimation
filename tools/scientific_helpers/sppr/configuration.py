"""Resolve recorded model-specific SPPR call settings without inferring provenance.

This reads evidence only. It does not authenticate old numerical outputs or
substitute current API defaults for kwargs omitted by the recorded call.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path


_EVIDENCE_NAMES = {
    'run_provenance.json', 'adopted_provenance.json', 'execution_evidence.json',
    'refresh_configuration.json', 'runtime_identity.json', 'input_identity.json',
    'complete_input_identity.json', 'initial_export_configuration.json',
    'dependency_identity.json',
}
_SOURCE_KEYS = ('canonical_sha256', 'canonical_model_sha256', 'model_sha256', 'source_sha256', 'input_sha256')
_ENGINE_FILES = ('PPRCalculator.py', 'ModelData.py', 'utils.py')
_ENGINE_MAPS = ('engine_source_hashes', 'code_identity', 'engine_hashes', 'engine_sha256',
                'runtime_code_hashes', 'runtime_hashes', 'engines', 'engine_files', 'engine')
_ENGINE = Path(__file__).resolve().parents[2] / 'scientific_code' / 'PPREstimation'
_OPTIONS = ('GE', 'TE', 'With Egestion')
_MC_KEYS = {'MC_new_GE', 'MC_new_TE_EEfix'}
_DIAGNOSTIC_KEYS = {
    'DET_TE_vals', 'det_collapse_mode', 'det_open_mode', 'det_theta',
    'det_external_sppr', 'fix_EE_0_cases', 'thresholds',
}


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _records(book, sheet, table):
    header, values = book.get(sheet, {}).get(table, ([], []))
    return [dict(zip(header, row)) for row in values]


def _settings(book):
    return {row.get('field'): row.get('value') for row in _records(book, 'Overview', 'Settings')}


def _as_dict(value):
    if isinstance(value, dict):
        return copy.deepcopy(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except ValueError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _merge(target, incoming, label):
    for key, value in incoming.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _merge(target[key], value, f'{label}.{key}')
        elif key in target and target[key] != value:
            raise ValueError(f'Conflicting audited configuration for {label}.{key}')
        else:
            target[key] = copy.deepcopy(value)


def _validate_evidence(model, flags, source_hash):
    evidence = flags.get('configuration_evidence', [])
    if not isinstance(evidence, list):
        raise ValueError('Invalid audited configuration evidence')
    for item in evidence:
        if not isinstance(item, dict) or not item.get('relative_path'):
            raise ValueError('Invalid audited configuration evidence')
        path = (model / item['relative_path']).resolve()
        if not path.is_relative_to(model) or not path.is_file():
            raise ValueError('Audited configuration evidence missing or outside model')
        if _sha(path) != item.get('sha256'):
            raise ValueError('Audited configuration evidence changed')
        if item.get('original_source_hash') != source_hash:
            raise ValueError('Audited configuration evidence belongs to a different model input')
    if not isinstance(flags.get('constructor'), dict) or not flags['constructor']:
        raise ValueError('No recorded audited configuration constructor kwargs')


def _positive_integer(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0 or int(value) != value:
        raise ValueError(f'Invalid recorded {label}: {value!r}')
    return int(value)


def _record_engine_hashes(record):
    hashes = {}
    for key in _ENGINE_MAPS:
        value = record.get(key)
        if not isinstance(value, dict):
            continue
        for name in _ENGINE_FILES:
            digest = value.get(name)
            if digest is None:
                continue
            if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
                raise ValueError(f'Invalid recorded audited engine hash: {name}')
            _merge(hashes, {name: digest}, 'engine_source_hashes')
    return hashes


def _pin_engine(model, flags, source_hash, record=None):
    """Locate exact audited bytes; neither copy files nor infer missing hashes."""
    hashes = flags.setdefault('engine_source_hashes', {})
    if hashes:
        # Preferred flags already bind these hashes to validated evidence and
        # exact source bytes. Legacy aliases retained in a rewritten manifest
        # describe superseded executions and must not replace that identity.
        _record_engine_hashes({'engine_source_hashes': hashes})
    else:
        origin = record or {}
        if isinstance(origin.get('code_identity'), dict) and origin['code_identity']:
            origin = {'code_identity': origin['code_identity']}
        _merge(hashes, _record_engine_hashes(origin), 'engine_source_hashes')
    for name in _ENGINE_FILES:
        if not hashes.get(name):
            raise ValueError(f'No recorded audited engine hash is available: {name}')
    sources = flags.setdefault('engine_sources', {})
    if not isinstance(sources, dict) or set(sources) - set(_ENGINE_FILES):
        raise ValueError('Invalid audited engine source names')
    evidence = flags.setdefault('configuration_evidence', [])
    for name in _ENGINE_FILES:
        if name in sources:
            path = (model / sources[name]).resolve()
            if not path.is_relative_to(model) or not path.is_file() or _sha(path) != hashes[name]:
                raise ValueError(f'Audited engine hash mismatch or source missing: {name}')
        else:
            candidates = sorted(p for p in model.rglob(name)
                                if p.is_file() and p.resolve().is_relative_to(model) and _sha(p) == hashes[name])
            path = candidates[0] if candidates else None
            if path is None:
                # Dependencies may remain in the current engine directory only
                # when their bytes equal the recorded audited dependency hashes.
                current = _ENGINE / name
                if name != 'PPRCalculator.py' and current.is_file() and _sha(current) == hashes[name]:
                    continue
                raise ValueError(f'No exact model-local audited engine source is available: {name}')
            sources[name] = path.relative_to(model).as_posix()
        item = {'relative_path': path.relative_to(model).as_posix(),
                'sha256': hashes[name], 'original_source_hash': source_hash}
        if item not in evidence:
            evidence.append(item)
        provenance = path.parent / 'engine_copy_provenance.json'
        if provenance.is_file():
            copied = json.loads(provenance.read_text(encoding='utf-8-sig'))
            if copied.get('canonical_model_sha256') != source_hash or copied.get('files', {}).get(name, {}).get('sha256') != hashes[name]:
                raise ValueError(f'Copied engine provenance does not match audited source: {name}')
            item = {'relative_path': provenance.relative_to(model).as_posix(),
                    'sha256': _sha(provenance), 'original_source_hash': source_hash}
            if item not in evidence:
                evidence.append(item)
    return flags


def _active_manifest_origin(model, manifest, flags, source_hash):
    """Follow a legacy publication's explicit accepted run, never pick a newer run."""
    reference = manifest.get('evidence')
    if not isinstance(reference, str) or not reference.endswith('run_manifest.json'):
        return manifest
    candidates = {(base / reference).resolve() for base in (model, *model.parents)}
    paths = [path for path in candidates if path.is_relative_to(model) and path.is_file()]
    if len(paths) != 1:
        raise ValueError('Accepted configuration run evidence missing or ambiguous')
    path = paths[0]
    origin = json.loads(path.read_text(encoding='utf-8-sig'))
    recorded_source = next((origin[key] for key in _SOURCE_KEYS if origin.get(key)), None)
    if recorded_source != source_hash:
        raise ValueError('Accepted configuration run belongs to different model input')
    if origin.get('constructor') != flags['constructor'] or origin.get('method_call') != flags['diagnostics']:
        raise ValueError('Accepted configuration run conflicts with publication settings')
    snapshot = model / 'results/regional_snapshot.xlsx'
    if not manifest.get('snapshot_sha256') or not snapshot.is_file() or _sha(snapshot) != manifest['snapshot_sha256']:
        raise ValueError('Accepted configuration publication snapshot identity does not match')
    flags['configuration_evidence'] = [{'relative_path': path.relative_to(model).as_posix(),
        'sha256': _sha(path), 'original_source_hash': source_hash}]
    flags['engine_sources'] = {name: (path.parent / 'executed_code' / name).relative_to(model).as_posix()
                               for name in _ENGINE_FILES}
    if isinstance(origin.get('thresholds'), dict):
        flags['diagnostics']['thresholds'] = copy.deepcopy(origin['thresholds'])
    return origin


def _retained_mc(model, book, manifest, source_hash):
    """Read actual sample counts only for retained canonical MC coefficient rows."""
    settings = _settings(book)
    if settings.get('results_model_id', settings.get('selected_model_id')) != model.name:
        return {}
    if settings.get('results_model_sha256') != source_hash:
        return {}
    present = {row.get('method') for row in _records(book, 'Selected model groups', 'Group SPPR')} & _MC_KEYS
    if not present:
        return {}
    rows = _records(book, 'Diagnostics', 'mc_diagnostics')
    if not rows:
        source = model / 'sppr_source.xlsx'
        expected = manifest.get('coefficient_source_sha256')
        if not expected or not source.is_file() or _sha(source) != expected:
            return {}
        import openpyxl
        workbook = openpyxl.load_workbook(source, read_only=True, data_only=True)
        try:
            values = list(workbook['mc_diagnostics'].values) if 'mc_diagnostics' in workbook.sheetnames else []
            rows = [dict(zip(values[0], row)) for row in values[1:]] if values else []
        finally:
            workbook.close()
    counts = {}
    for row in rows:
        method = row.get('method')
        if method not in present or row.get('n_samples') is None:
            continue
        count = _positive_integer(row['n_samples'], 'MC n_samples')
        if method in counts and counts[method] != count:
            raise ValueError(f'Conflicting retained MC sample counts for {method}')
        counts[method] = count
    if len(set(counts.values())) > 1:
        raise ValueError('Conflicting retained MC sample counts across canonical methods')
    return {'n_samples': next(iter(counts.values()))} if counts else {}


def _from_evidence(record):
    constructor = record.get('constructor', record.get('constructor_settings'))
    hashes = _record_engine_hashes(record)
    if not isinstance(constructor, dict):
        constructor = {}
    if not constructor and not hashes:
        return None
    flags = {'constructor': copy.deepcopy(constructor), 'diagnostics': {}, 'methods': {}, 'mc': {}}
    diagnostic = record.get('diagnose_kwargs', record.get('direct_settings',
                 record.get('diagnostic_settings', record.get('method', {}))))
    if isinstance(diagnostic, dict):
        settings = {key: value for key, value in diagnostic.items() if key in _DIAGNOSTIC_KEYS}
        option = diagnostic.get('TE_option')
        if isinstance(option, str) and option in _OPTIONS:
            flags['methods'][option] = settings
        else:
            flags['diagnostics'] = settings
    thresholds = record.get('effective_diagnostic_thresholds', record.get('thresholds'))
    if isinstance(thresholds, dict):
        flags['diagnostics']['thresholds'] = copy.deepcopy(thresholds)
    if isinstance(record.get('mc'), dict):
        flags['mc'] = {key: value for key, value in record['mc'].items()
                       if key in {'n_samples', 'TE_error_percent', 'TE_error_cut_percent', 'seed'}}
    if record.get('mc_samples') is not None:
        _merge(flags['mc'], {'n_samples': _positive_integer(record['mc_samples'], 'mc_samples')}, 'mc')
    for key in ('method_timeout_seconds', 'method_timeout_overrides_seconds'):
        if key in record:
            flags[key] = copy.deepcopy(record[key])
    for key in ('calculation_engine_upgrade', 'calculation_engine_sha256',
                'calculation_engine_source', 'ee_floor_authorization'):
        if key in record:
            flags[key] = copy.deepcopy(record[key])
    if hashes:
        flags['engine_source_hashes'] = hashes
    return flags


def resolve_audited_configuration(model_dir, book, manifest):
    """Return exact recorded kwargs; raise ValueError when evidence is unavailable.

    Explicit current Overview settings and matching manifest flags are preferred.
    Legacy model-local evidence is admitted only when its source hash matches
    current canonical bytes. File paths are relative to the model directory.
    """
    model = Path(model_dir).resolve()
    source_hash = _sha(model / 'model.json')
    settings = _settings(book)
    identity = settings.get('results_model_id') or settings.get('selected_model_id')
    if identity == model.name:
        for key in ('effective_loader_flags', 'sppr_configuration'):
            flags = _as_dict(settings.get(key))
            if flags and isinstance(flags.get('constructor'), dict) and flags['constructor']:
                _validate_evidence(model, flags, source_hash)
                retained_mc = _retained_mc(model, book, manifest, source_hash)
                if retained_mc:
                    _merge(flags.setdefault('mc', {}), retained_mc, 'mc')
                origin = manifest if (manifest.get('canonical_model_sha256') or manifest.get('input_sha256')) == source_hash else {}
                return _pin_engine(model, flags, source_hash, origin)
    manifest_source = manifest.get('canonical_model_sha256') or manifest.get('input_sha256')
    if manifest_source == source_hash:
        flags = _as_dict(manifest.get('effective_flags')) or _as_dict(manifest.get('audited_configuration'))
        origin = manifest
        if not flags and manifest.get('constructor') and manifest.get('diagnostics'):
            flags = {key: copy.deepcopy(manifest[key]) for key in ('constructor', 'diagnostics')}
            origin = _active_manifest_origin(model, manifest, flags, source_hash)
        if flags:
            _validate_evidence(model, flags, source_hash)
            retained_mc = _retained_mc(model, book, manifest, source_hash)
            if retained_mc:
                _merge(flags.setdefault('mc', {}), retained_mc, 'mc')
            # No self-referential hash of result_manifest.json: its signed-off
            # canonical identity and retained flags are the configuration source.
            return _pin_engine(model, flags, source_hash, origin)

    flags = {'constructor': {}, 'diagnostics': {}, 'methods': {}, 'mc': {}}
    evidence = []
    roots = (model / 'model_validation/evidence/source_review', model / 'results/diagnostics/audited_engine')
    paths = sorted(path for root in roots if root.is_dir()
                   for path in root.rglob('*.json') if path.name in _EVIDENCE_NAMES)
    for path in paths:
        if not path.resolve().is_relative_to(model):
            raise ValueError('Audited configuration evidence outside model')
        try:
            record = json.loads(path.read_text(encoding='utf-8-sig'))
        except (OSError, ValueError) as error:
            raise ValueError(f'Unreadable audited configuration evidence: {path.name}') from error
        if not isinstance(record, dict):
            continue
        recorded_source = next((record[key] for key in _SOURCE_KEYS if record.get(key)), None)
        if recorded_source != source_hash:
            continue
        candidate = _from_evidence(record)
        if candidate is None:
            continue
        _merge(flags, candidate, 'configuration')
        evidence.append({'relative_path': path.relative_to(model).as_posix(),
                         'sha256': _sha(path), 'original_source_hash': source_hash})
    if not evidence:
        raise ValueError('No model-matching audited configuration evidence is available')
    # Method-specific records and common direct kwargs may complement one
    # another, but a disagreement cannot be silently resolved by precedence.
    for option, method in flags['methods'].items():
        common = copy.deepcopy(flags['diagnostics'])
        _merge(common, method, f'diagnostics/{option}')
    _merge(flags['mc'], _retained_mc(model, book, manifest, source_hash), 'mc')
    flags['configuration_evidence'] = evidence
    _validate_evidence(model, flags, source_hash)
    return _pin_engine(model, flags, source_hash)
