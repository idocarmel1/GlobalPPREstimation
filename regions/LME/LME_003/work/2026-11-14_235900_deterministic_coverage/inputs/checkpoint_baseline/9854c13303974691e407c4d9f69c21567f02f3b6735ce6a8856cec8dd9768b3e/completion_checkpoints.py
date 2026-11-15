"""Sealed, identity-bound complete model packages; no scientific execution."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import tempfile


def digest(path):
    path = Path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')


def safe(root, value):
    root = Path(root).resolve()
    path = root / value
    if Path(value).is_absolute() or not path.resolve().is_relative_to(root):
        raise ValueError('Checkpoint path escaped root: ' + str(value))
    current = path
    while current != root:
        if current.is_symlink() or (current.exists() and getattr(current.stat(follow_symlinks=False), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Checkpoint path contains a reparse point: ' + str(current))
        current = current.parent
    return path.resolve()


def base_destinations(plan):
    return {Path(plan[k]).resolve() for k in ('source', 'manifest', 'regional')} | {
        (Path(plan['model']).parent/'results/regional_snapshot.xlsx').resolve()}


def permitted(plan, path):
    model = Path(plan['model']).parent.resolve()
    return path in base_destinations(plan) or any(path.is_relative_to(model/'results/diagnostics'/name)
                                               for name in ('method_coverage', 'ee_floor'))


def location(cache_root, plan, bindings):
    key = hashlib.sha256(encoded(bindings)).hexdigest()
    return safe(cache_root, '/'.join((*plan['pair'], key)))


def check_inputs(root, bindings):
    for name, expected in bindings['inputs'].items():
        if digest(safe(root, name)) != expected:
            raise ValueError('Checkpoint input changed: ' + name)


def make_bindings(root, plan, consumed, immutable, producer):
    model = plan['model'].parent
    relevant = {p: h for p, h in {**consumed, **immutable}.items()
                if p.is_relative_to(model) or p == plan['regional']}
    for batch in plan['batches']:
        relevant.update(batch.consumed)
    # Protect shared registration and actual producer/dependency identities.
    relevant[root/'Project.xlsx'] = consumed[root/'Project.xlsx']
    relevant.update(producer)
    destinations = {p.relative_to(root).as_posix(): digest(p) for p in base_destinations(plan)}
    return {'identity': list(plan['pair']), 'metadata': plan['metadata'], 'wanted': plan['wanted'],
            'inputs': {p.relative_to(root).as_posix(): h for p, h in relevant.items()},
            'destinations': destinations,
            'producer': {p.relative_to(root).as_posix(): h for p, h in producer.items()}}


def check_immutable_inputs(root, bindings):
    # Original output hashes are binding preconditions, not immutable after execution.
    for name, expected in bindings['inputs'].items():
        if name not in bindings['destinations'] and digest(safe(root, name)) != expected:
            raise ValueError('Checkpoint immutable input changed: ' + name)


def verify_references(root, plan, paths):
    """Bind every direct method/constructor/index reference in the final manifest.

    Older incomplete retained records remain historical: only references to new
    package files are required here; existing immutable evidence is in bindings.
    The unchanged adopter's full retained-record assertions remain authoritative.
    """
    model = Path(plan['model']).parent
    manifest = json.loads(Path(plan['manifest']).read_bytes())
    references = []
    for outcome in manifest.get('method_coverage', {}).get('methods', {}).values():
        for key in ('evidence', 'constructor_evidence', 'runtime_verification_evidence', 'cached_execution_source'):
            ref = outcome.get(key)
            if isinstance(ref, dict): references.append(ref)
    evidence = manifest.get('method_coverage', {}).get('execution_evidence', {})
    if isinstance(evidence, dict):
        if 'path' in evidence: references.append(evidence)
        references.extend(v for v in evidence.values() if isinstance(v, dict))
    checked = {}
    for ref in references:
        name, expected = ref.get('path'), ref.get('sha256')
        if not isinstance(name, str) or not isinstance(expected, str): continue
        candidates = []
        for base in (model/'results/diagnostics', model, model/'results'):
            try: candidates.append(safe(root, (base/name).relative_to(root).as_posix()))
            except ValueError: continue
        matches = [p for p in candidates if digest(p) == expected]
        if matches:
            path = matches[0]
            checked[path.relative_to(root).as_posix()] = expected
        elif any(p in paths for p in candidates):
            raise ValueError('New checkpoint evidence reference mismatch: ' + name)
        elif ref.get('availability') == 'present':
            raise ValueError('Present checkpoint evidence reference is unavailable: ' + name)
    return checked


def capture_model_checkpoint(root, plan, cache_root, bindings, batch_reports, written_paths):
    root = Path(root).resolve()
    folder = location(cache_root, plan, bindings)
    check_immutable_inputs(root, bindings)
    expected_outputs = {Path(p).resolve(): h for p, h in written_paths.items()}
    paths = set(expected_outputs) | base_destinations(plan)
    for path in paths:
        if path not in expected_outputs or digest(path) != expected_outputs[path]:
            raise ValueError('Checkpoint output changed after its verified write: ' + str(path))
    references = verify_references(root, plan, paths)
    for name, expected in references.items():
        if name not in bindings['inputs']:
            path = safe(root, name)
            if path not in expected_outputs or expected_outputs[path] != expected:
                raise ValueError('Referenced evidence lacks exact guarded ownership: ' + name)
            paths.add(path)
    objects = folder/'objects'; objects.mkdir(parents=True, exist_ok=True)
    files = []
    for path in sorted(paths):
        name = path.relative_to(root).as_posix(); safe(root, name)
        if not permitted(plan, path): raise ValueError('Checkpoint destination is outside the model allowlist: ' + name)
        before = bindings['destinations'].get(name, bindings['inputs'].get(name))
        data = path.read_bytes(); after = hashlib.sha256(data).hexdigest()
        if after != expected_outputs[path]: raise ValueError('Checkpoint output changed during capture: ' + name)
        if name in bindings['inputs'] and name not in bindings['destinations']:
            if after != before: raise ValueError('Checkpoint attempted to overwrite immutable evidence: ' + name)
            continue
        obj = objects/after
        if not obj.exists():
            with obj.open('xb') as stream:
                stream.write(data); stream.flush(); os.fsync(stream.fileno())
        if digest(obj) != after: raise ValueError('Checkpoint object corrupt: ' + str(obj))
        files.append({'path': name, 'before_sha256': before, 'after_sha256': after})
    manifest = {'schema_version': 1, 'state': 'COMPLETE', 'identity': list(plan['pair']),
                'bindings': bindings, 'files': files, 'batch_reports': batch_reports,
                'references': references,
                'provenance': 'Final stamped bytes. Restore must not stamp or execute again.'}
    check_immutable_inputs(root, bindings)
    if any(digest(p) != h for p, h in expected_outputs.items()):
        raise ValueError('Checkpoint output changed before sealing')
    # Seal last. Partial objects alone can never be loaded as a package.
    seal = folder/'COMPLETE.json'
    seal_bytes = encoded(manifest)
    with (folder/'manifest.sha256').open('w', encoding='ascii') as stream:
        stream.write(hashlib.sha256(seal_bytes).hexdigest()); stream.flush(); os.fsync(stream.fileno())
    fd, temporary = tempfile.mkstemp(dir=folder, suffix='.tmp'); os.close(fd)
    try:
        with open(temporary, 'wb') as stream:
            stream.write(seal_bytes); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, seal)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return seal


def load_model_checkpoint(root, plan, cache_root, bindings):
    folder = location(cache_root, plan, bindings); seal = folder/'COMPLETE.json'
    if not seal.is_file():
        # A publication-only repair must not silently rebuild completed models.
        # Stop for a narrow, explicit producer-compatibility decision instead.
        if folder.parent.is_dir():
            for candidate in folder.parent.iterdir():
                old_seal = candidate/'COMPLETE.json'
                if not old_seal.is_file(): continue
                try:
                    old = json.loads(old_seal.read_bytes())['bindings']
                    old_inputs = {k:v for k,v in old['inputs'].items() if k not in old.get('producer', {})}
                    new_inputs = {k:v for k,v in bindings['inputs'].items() if k not in bindings.get('producer', {})}
                    if old_inputs == new_inputs and old.get('producer') != bindings.get('producer'):
                        raise RuntimeError('Completed package has changed producer code; record explicit narrow compatibility before reuse: '+str(old_seal))
                except (OSError, ValueError, KeyError, TypeError): continue
        return None
    try:
        if digest(seal) != (folder/'manifest.sha256').read_text(encoding='ascii'):
            raise ValueError('Checkpoint seal corrupt')
        check_inputs(root, bindings)
        manifest = json.loads(seal.read_bytes())
        if not isinstance(manifest, dict): raise ValueError('Checkpoint seal must be an object')
        if (manifest.get('schema_version') != 1 or manifest.get('state') != 'COMPLETE'
                or manifest.get('identity') != list(plan['pair']) or manifest.get('bindings') != bindings):
            raise ValueError('Checkpoint identity/bindings mismatch')
        seen = set()
        for entry in manifest['files']:
            path = safe(root, entry['path'])
            if path in seen or not permitted(plan, path): raise ValueError('Checkpoint destination allowlist mismatch')
            seen.add(path)
            expected = bindings['destinations'].get(entry['path'], bindings['inputs'].get(entry['path']))
            if entry['before_sha256'] != expected or digest(path) != expected:
                raise ValueError('Checkpoint destination precondition changed')
            fingerprint = entry['after_sha256']
            if not isinstance(fingerprint, str) or len(fingerprint) != 64 or any(c not in '0123456789abcdef' for c in fingerprint):
                raise ValueError('Invalid checkpoint object identity')
            if digest(safe(folder, 'objects/'+fingerprint)) != fingerprint: raise ValueError('Checkpoint object corrupt')
        if not base_destinations(plan).issubset(seen): raise ValueError('Checkpoint package incomplete')
        packaged = {e['path']: e['after_sha256'] for e in manifest['files']}
        for name, expected in manifest.get('references', {}).items():
            if packaged.get(name, bindings['inputs'].get(name)) != expected:
                raise ValueError('Checkpoint referenced evidence was omitted')
        return {'folder': folder, 'manifest': manifest, 'seal_sha256': digest(seal)}
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print('Rejected checkpoint '+str(plan['pair'])+': '+str(error), flush=True)
        return None


def restore_model_checkpoint(root, plan, checkpoint, publication):
    from tools.project_core.registry.publication import guarded_replace
    root = Path(root).resolve(); folder = checkpoint['folder']; manifest = checkpoint['manifest']
    if digest(folder/'COMPLETE.json') != checkpoint['seal_sha256']: raise ValueError('Checkpoint seal changed')
    check_inputs(root, manifest['bindings'])
    # Verify the entire allowlist before making the first change.
    for entry in manifest['files']:
        path = safe(root, entry['path'])
        if not permitted(plan, path) or digest(path) != entry['before_sha256']:
            raise ValueError('Checkpoint destination changed: ' + str(path))
        if digest(folder/'objects'/entry['after_sha256']) != entry['after_sha256']:
            raise ValueError('Checkpoint object changed')
    for entry in manifest['files']:
        path = safe(root, entry['path']); path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=path.parent, suffix=path.suffix); os.close(fd)
        try:
            Path(temporary).write_bytes((folder/'objects'/entry['after_sha256']).read_bytes())
            guarded_replace(temporary, path, expected_sha256=entry['before_sha256'])
        finally:
            Path(temporary).unlink(missing_ok=True)
    check_immutable_inputs(root, manifest['bindings'])
    for name, expected in manifest.get('references', {}).items():
        if digest(safe(root, name)) != expected: raise ValueError('Restored evidence hash mismatch')
    return {'batch_reports': manifest['batch_reports'],
            'cache_restoration': {'identity': list(plan['pair']), 'seal_sha256': checkpoint['seal_sha256'],
                                  'files': len(manifest['files']), 'no_execution': True, 'no_restamping': True}}


def reconcile_ownership(root, journal, baseline, allowlist):
    """Read-only interrupted-write ownership report against exact baseline paths."""
    root = Path(root).resolve()
    expected = dict(baseline)
    states = {name: {value} for name, value in baseline.items()}
    for line in Path(journal).read_text(encoding='utf-8').splitlines():
        event = json.loads(line)
        name = event['path']
        if event.get('event') != 'intent' or name not in allowlist:
            raise ValueError('Unexpected ownership journal destination')
        safe(root, name)
        if event['before_sha256'] != expected.get(name):
            raise ValueError('Ownership journal chain mismatch: ' + name)
        expected[name] = event['after_sha256']
        states.setdefault(name, {baseline.get(name)}).update((event['before_sha256'], event['after_sha256']))
    result = []
    for name in allowlist:
        actual = digest(safe(root, name))
        state = 'baseline' if actual == baseline.get(name) else 'task_owned' if actual in states.get(name, set()) else 'external_conflict'
        result.append({'path': name, 'actual_sha256': actual, 'baseline_sha256': baseline.get(name), 'state': state})
    return result
