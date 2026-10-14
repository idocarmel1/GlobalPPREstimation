"""Durable executed evidence for retries of an EE-floor publication.

These work packages are not adopted results or researcher approval. Exact
scientific context and evidence bytes must match before a retry can consume one.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


def _bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _inside(root, relative):
    relative = Path(str(relative))
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('Invalid execution evidence path')
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Execution evidence escaped its directory')
    return target


def _identity(model_dir, context, methods, settings):
    methods = list(methods)
    if not methods or len(methods) != len(set(methods)) or set(settings) != set(methods):
        raise ValueError('Execution cache requires an exact nonempty method inventory')
    actual = _sha((model_dir / 'model.json').read_bytes())
    if context.get('model_sha256') != actual:
        raise ValueError('Canonical source changed before execution caching')
    return {'context': context, 'methods': methods, 'settings': settings,
            'environment': {'python': sys.version, 'platform': platform.platform()}}


def _references(calculated, methods):
    outcomes = calculated.get('methods', {})
    if set(outcomes) != set(methods):
        raise ValueError('Executed evidence omitted or added requested methods')
    references = [outcomes[key].get('evidence') for key in methods]
    references.extend(calculated[key] for key in ('constructor_evidence', 'evidence_index')
                      if key in calculated)
    if any(not isinstance(ref, dict) or not ref.get('path') or not ref.get('sha256')
           for ref in references):
        raise ValueError('Executed evidence has a missing file identity')
    return references


def _executed_identity(calculated, context, settings):
    for key, expected in [('model_sha256', context['model_sha256']),
                          ('flags', context.get('flags')),
                          ('engine_hashes', context.get('code_identity')),
                          ('adapter_sha256', context.get('adapter_sha256'))]:
        if key in calculated and calculated[key] != expected:
            raise ValueError('Executed scientific identity differs from the retry context: ' + key)
    for key, outcome in calculated['methods'].items():
        if 'settings' in outcome and outcome['settings'] != settings[key]:
            raise ValueError('Executed method settings differ from the retry identity')


def _work(model_dir):
    return _inside(model_dir, 'model_validation/work')


def _atomic(path, data):
    temporary = path.with_name(path.name + '.writing')
    with temporary.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def save_execution(model_dir, context, methods, settings, calculated, staged_dir):
    """Save all actual returns before adopted-output writes or evidence promotion."""
    model_dir, staged_dir = Path(model_dir).resolve(), Path(staged_dir).resolve()
    identity = _identity(model_dir, context, methods, settings)
    files = {}
    for reference in _references(calculated, identity['methods']):
        path = _inside(staged_dir, reference['path'])
        data = path.read_bytes()
        if _sha(data) != reference['sha256']:
            raise ValueError('Executed evidence changed before caching')
        files[Path(reference['path']).as_posix()] = {
            'sha256': reference['sha256'], 'base64': base64.b64encode(data).decode('ascii')}
    _executed_identity(calculated, context, settings)
    package = {'schema_version': 1, 'role': 'unadopted executed evidence for publication retry',
               'timestamp': datetime.now(timezone.utc).isoformat(), **identity,
               'calculated': calculated, 'files': files}
    data = gzip.compress(_bytes(package), mtime=0)
    work = _work(model_dir)
    work.mkdir(parents=True, exist_ok=True)
    name = datetime.now().strftime('%Y-%m-%d_%H%M%S_ee_floor_execution')
    for suffix in range(10000):
        run = _inside(work, name + (f'_{suffix}' if suffix else ''))
        try:
            run.mkdir()
            break
        except FileExistsError:
            continue
    else:
        raise ValueError('Unable to allocate a distinct execution work run')
    outputs = run / 'outputs'
    outputs.mkdir()
    path = outputs / 'pending.json.gz'
    _atomic(path, data)
    reference = {'path': path.relative_to(model_dir).as_posix(), 'sha256': _sha(data)}
    # A separate receipt detects edits to compact outcomes as well as full returns.
    _atomic(outputs / 'receipt.json', _bytes(reference))
    if _identity(model_dir, context, methods, settings) != identity:
        raise ValueError('Canonical source changed while caching execution evidence')
    return reference


def load_execution(model_dir, context, methods, settings, staged_dir):
    """Restore authenticated exact-context returns without executing new draws."""
    model_dir, staged_dir = Path(model_dir).resolve(), Path(staged_dir).resolve()
    identity = _identity(model_dir, context, methods, settings)
    work = _work(model_dir)
    if not work.is_dir():
        return None
    for path in sorted(work.glob('*_ee_floor_execution*/outputs/pending.json.gz'), reverse=True):
        path = _inside(model_dir, path.relative_to(model_dir))
        receipt_path = _inside(model_dir, path.with_name('receipt.json').relative_to(model_dir))
        if not receipt_path.is_file():
            continue
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        data = path.read_bytes()
        package = json.loads(gzip.decompress(data))
        if any(package.get(key) != value for key, value in identity.items()):
            continue
        if package.get('schema_version') != 1:
            raise ValueError('Unsupported cached execution evidence schema')
        references = _references(package.get('calculated', {}), identity['methods'])
        _executed_identity(package['calculated'], context, settings)
        restored = {}
        for ref in references:
            name = Path(ref['path']).as_posix()
            record = package.get('files', {}).get(name, {})
            try:
                raw = base64.b64decode(record['base64'], validate=True)
            except (KeyError, ValueError, TypeError) as error:
                raise ValueError('Invalid cached execution evidence') from error
            if _sha(raw) != ref['sha256'] or record.get('sha256') != ref['sha256']:
                raise ValueError('Cached execution evidence changed')
            target = _inside(staged_dir, ref['path'])
            if target.exists() and (not target.is_file() or _sha(target.read_bytes()) != ref['sha256']):
                raise ValueError('Cached execution evidence conflicts with staged evidence')
            restored[target] = raw
        expected_reference = {'path': path.relative_to(model_dir).as_posix(), 'sha256': _sha(data)}
        if receipt != expected_reference:
            raise ValueError('Cached execution evidence package changed')
        for target, raw in restored.items():
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                _atomic(target, raw)
        return {'calculated': package['calculated'], 'reference': receipt}
    return None


def discard_execution(model_dir, reference):
    """Remove a duplicate only after the caller verified whole-batch publication."""
    model_dir = Path(model_dir).resolve()
    path = _inside(model_dir, reference['path'])
    work = _work(model_dir)
    if (not path.is_relative_to(work) or path.name != 'pending.json.gz'
            or path.parent.name != 'outputs' or '_ee_floor_execution' not in path.parent.parent.name):
        raise ValueError('Not a bounded EE-floor execution cache')
    receipt = path.with_name('receipt.json')
    if _sha(path.read_bytes()) != reference['sha256'] or json.loads(receipt.read_text(encoding='utf-8')) != reference:
        raise ValueError('Execution cache changed before cleanup')
    path.unlink()
    receipt.unlink()
    # Only remove empty directories; unrelated author work is preserved.
    if not any(path.parent.iterdir()):
        path.parent.rmdir()
    run = path.parent.parent
    if not any(run.iterdir()):
        run.rmdir()
