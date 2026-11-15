"""Admit actual initialization evidence; narrowly verify two preserved CAL states.

The retrospective record is a new verification, never a recovered constructor.
No method calculation is called and no original execution record is rewritten.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path, PureWindowsPath
import platform
import sys

ROOT = next(path for path in Path(__file__).resolve().parents if (path/'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
from tools.scientific_helpers.sppr import method_coverage as adapter
from tools.scientific_helpers.sppr.audited_runtime import validate_replay

HELPER_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
KIND = 'retrospective_runtime_authentication'
CAL_MODEL = 'CAL-2016_California_Current_2000-2014'
CAL_METHOD_HASHES = {
    'sym_TE_asPP': '05ba51766f57868bb910c7ae3f47158b137e5a2f46f602190c165959df10d8e0',
    'sym_GE_asPP': '534eb56d361fec1cdd777fef710f599a49277f6daedfba7740516bcd970124ea',
}
CAL_CONSTRUCTOR_SHA256 = '4f568ed4c734d18f3c716dea89d149fd467b4984d6c141e8ecd13370c399b2db'
CAL_RUNTIME_SHA256 = 'ad51b718cb1547d9e29307a37f1a22acad75ec1c399e38c23d1a23d001eb7c7c'
LIMITATION = (
    'The original ready constructor record was overwritten by a later failed worker restart. '
    'The surviving constructor record reports an adapter revision mismatch and does not '
    'evidence either successful method initialization. This later verification authenticates '
    'the exact saved pre-method runtime against the pinned completed-runtime replay. It does '
    'not reconstruct the original constructor event or rerun the successful methods. '
    'The original recorded adapter digest remains unchanged; its import-time identity is not attested.'
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def reference(root, ref):
    root = Path(root).resolve()
    name = ref.get('path', ref.get('relative_path'))
    if not isinstance(name, str) or not name or Path(name).is_absolute() or PureWindowsPath(name).anchor:
        raise ValueError('Initialization evidence must use a relative path')
    path = (root/name).resolve()
    if not path.is_relative_to(root) or not path.is_file() or sha(path) != ref.get('sha256'):
        raise ValueError('Initialization evidence is missing, changed, or outside its directory')
    return path


def _state_digest(state):
    return adapter._hash_bytes(adapter._json_bytes(state))


def _method_state(document):
    if 'runtime_before' not in document:
        raise ValueError('Method has no actual pre-method runtime')
    state = document['runtime_before']
    if document.get('runtime_before_sha256', _state_digest(state)) != _state_digest(state):
        raise ValueError('Method runtime hash disagrees with its saved state')
    return state


def _pinned_runtime(model, identity):
    """Authenticate sources and read inert completed state without calculations."""
    model = Path(model).resolve()
    if identity.get('model_id') != model.parent.name or identity.get('model_sha256') != sha(model):
        raise ValueError('Initialization model identity differs')
    flags = identity['flags']
    replay = validate_replay(flags, model)
    if not replay or replay['mode'] != 'completed_runtime' or replay['runtime'].get('keys', []):
        raise ValueError('Retrospective verification requires the exact flat completed-runtime replay')
    if adapter.engine_identity(flags, model) != identity.get('engine_hashes'):
        raise ValueError('Initialization engine identity differs')
    path = reference(model.parent, replay['runtime'])
    return read(path), {path: sha(path)}


def verify_initialization(model, cache_dir, key, outcome, document):
    """Return the authenticated initialization record and consumed immutable paths.

    Caller still validates complete method summaries/settings and execution identity.
    This validator never treats a later verification as an original constructor.
    """
    model, cache_dir = Path(model).resolve(), Path(cache_dir).resolve()
    alternate = outcome.get('runtime_verification_evidence')
    ref = alternate if alternate is not None else outcome.get('constructor_evidence', {})
    path = reference(cache_dir, ref)
    saved = read(path)
    identity = document['identity']
    consumed = {path: sha(path)}
    if alternate is None:
        if saved.get('identity') != identity:
            raise ValueError('Constructor execution identity differs from the method')
        embedded = document.get('constructor_evidence')
        if embedded and embedded.get('sha256') != ref.get('sha256'):
            raise ValueError('Method points to a different original constructor')
        initial = saved.get('constructor_outcome', {})
        if document.get('status') == 'NOT_RUN':
            if initial.get('status') == 'ready' or initial != document.get('constructor_outcome'):
                raise ValueError('NOT_RUN method does not match its unavailable constructor')
        else:
            if initial.get('status') != 'ready':
                raise ValueError('Executed method requires its ready constructor record')
            if 'runtime_before' in document and initial.get('runtime') != _method_state(document):
                raise ValueError('Constructor runtime differs from the actual pre-method runtime')
            if 'groups' in document and initial.get('groups') != document['groups']:
                raise ValueError('Constructor group identities differ from the method')
        return {'evidence_kind': 'original_constructor', 'path': path,
                'reference': copy.deepcopy(ref), 'consumed': consumed}

    if (model.parent.name != CAL_MODEL or key not in CAL_METHOD_HASHES
            or saved.get('schema_version') != 1 or saved.get('evidence_kind') != KIND
            or saved.get('scientific_execution_performed') is not False
            or saved.get('original_constructor_available') is not False
            or saved.get('limitation') != LIMITATION
            or saved.get('original_execution_identity') != identity):
        raise ValueError('Unsupported retrospective initialization verification')
    method_path = reference(cache_dir, outcome['evidence'])
    if sha(method_path) != CAL_METHOD_HASHES[key] or read(method_path) != document:
        raise ValueError('Retrospective verification does not identify the original CAL method')
    original = reference(model.parent, saved.get('original_method_evidence', {}).get(key, {}))
    if sha(original) != sha(method_path) or document.get('status') != 'ok':
        raise ValueError('Retrospective verification does not cover this successful method')
    overwritten = reference(model.parent, saved.get('surviving_failed_constructor_evidence', {}))
    failed = read(overwritten)
    if (sha(overwritten) != CAL_CONSTRUCTOR_SHA256 or failed.get('identity') != identity
            or failed.get('constructor_outcome', {}).get('status') != 'constructor_failed'):
        raise ValueError('Original overwritten constructor limitation is not evidenced')
    state, sources = _pinned_runtime(model, identity)
    digest = _state_digest(state)
    verification = saved.get('verification_identity', {})
    if (state != _method_state(document) or digest != CAL_RUNTIME_SHA256
            or saved.get('runtime_sha256') != digest
            or saved.get('exact_runtime_and_groups_verified') is not True
            or verification.get('model_sha256') != identity['model_sha256']
            or verification.get('engine_hashes') != identity['engine_hashes']
            or not isinstance(verification.get('adapter_sha256'), str)
            or len(verification['adapter_sha256']) != 64):
        raise ValueError('Retrospective verification state or verification identity differs')
    consumed.update(sources)
    consumed.update({method_path: sha(method_path), original: sha(original), overwritten: sha(overwritten)})
    return {'evidence_kind': KIND, 'path': path, 'reference': copy.deepcopy(ref),
            'consumed': consumed, 'limitation': LIMITATION}


def recover_california_v1(model, output_dir):
    """Create a separately typed state verification for exactly two frozen returns."""
    model, output_dir = Path(model).resolve(), Path(output_dir).resolve()
    if model.parent.name != CAL_MODEL or not output_dir.is_relative_to(model.parent):
        raise ValueError('CAL recovery requires its exact model and model-local output')
    cache = model.parent/'results/diagnostics/method_coverage/deterministic_completion_20261114/calculated'
    if not output_dir.is_relative_to(cache):
        raise ValueError('CAL verification output must remain within its staged calculation directory')
    methods = {key: reference(cache/'symbolic', {'path': key+'.json.gz', 'sha256': digest})
               for key, digest in CAL_METHOD_HASHES.items()}
    constructor = reference(cache/'symbolic', {'path': 'constructor.json.gz', 'sha256': CAL_CONSTRUCTOR_SHA256})
    documents = {key: read(path) for key, path in methods.items()}
    identity = next(iter(documents.values()))['identity']
    if any(doc['identity'] != identity or doc.get('status') != 'ok' for doc in documents.values()):
        raise ValueError('CAL original successful method identities differ')
    failed = read(constructor)
    if failed.get('identity') != identity or failed.get('constructor_outcome', {}).get('status') != 'constructor_failed':
        raise ValueError('CAL surviving constructor is not the recorded failed restart')
    state, sources = _pinned_runtime(model, identity)
    if _state_digest(state) != CAL_RUNTIME_SHA256:
        raise ValueError('CAL completed state differs from its original method state')
    flags = identity['flags']
    # Completed-runtime _load restores inert attributes; no constructor or solver.
    loaded, _, _ = adapter._load(model, adapter._constructor(flags, model), flags)
    actual, groups = adapter._runtime(loaded), adapter._group_metadata(loaded)
    if actual != state or any(_method_state(doc) != actual or doc.get('groups') != groups
                              for doc in documents.values()):
        raise ValueError('Pinned replay does not reproduce the exact saved runtime and groups')
    record = {
        'schema_version': 1, 'evidence_kind': KIND,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'scientific_execution_performed': False, 'original_constructor_available': False,
        'original_execution_identity': identity,
        'original_method_evidence': {key: {'relative_path': path.relative_to(model.parent).as_posix(),
                                          'sha256': sha(path)} for key, path in methods.items()},
        'surviving_failed_constructor_evidence': {'relative_path': constructor.relative_to(model.parent).as_posix(),
                                                'sha256': sha(constructor)},
        'runtime_sha256': _state_digest(actual), 'exact_runtime_and_groups_verified': True,
        'verification_identity': {'adapter_sha256': adapter.ADAPTER_SOURCE_SHA256,
            'verification_helper_sha256': HELPER_SHA256, 'model_sha256': sha(model),
            'engine_hashes': adapter.engine_identity(flags, model),
            'environment': {'python': sys.version, 'platform': platform.platform(),
                            'numpy': adapter.np.__version__, 'pandas': adapter.pd.__version__}},
        'limitation': LIMITATION,
    }
    for path, digest in {**sources, **{p: CAL_METHOD_HASHES[k] for k, p in methods.items()},
                         constructor: CAL_CONSTRUCTOR_SHA256}.items():
        if sha(path) != digest:
            raise ValueError('CAL evidence changed during retrospective verification')
    payload = gzip.compress(adapter._json_bytes(record), mtime=0)
    digest = hashlib.sha256(payload).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir/('runtime-verification-'+digest+'.json.gz')
    if target.exists():
        if target.read_bytes() != payload:
            raise ValueError('Immutable verification output changed')
    else:
        with target.open('xb') as stream:
            stream.write(payload)
    ref = {'path': target.relative_to(cache).as_posix(), 'sha256': digest, 'availability': 'present'}
    patches = {key: {'runtime_verification_evidence': copy.deepcopy(ref),
                     'initialization_provenance_caveat': LIMITATION} for key in methods}
    return {'evidence': ref, 'method_outcome_patches': patches, 'record': record}
