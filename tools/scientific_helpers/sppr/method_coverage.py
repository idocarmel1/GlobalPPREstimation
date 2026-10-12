"""Run the canonical SPPR inventory without changing audited model inputs.

The exporter registry defines the method names. This adapter retains full engine
returns and model-specific loading/detritus settings rather than adopting the
exporter's stock loader or discarding source matrices. It never writes workbooks.
"""
from __future__ import annotations

import copy
import ast
import builtins
from datetime import datetime, timezone
import gzip
import hashlib
import inspect
import importlib.util
import json
import math
import multiprocessing as mp
from pathlib import Path
import platform
import sys
import time
import traceback
import warnings

import numpy as np
import pandas as pd


ENGINE = Path(__file__).resolve().parents[2] / 'scientific_code' / 'PPREstimation'
SCOPES = ('all', 'inner', 'PP')
DET_KEYS = ('DET_TE_vals', 'det_collapse_mode', 'det_open_mode', 'det_theta',
            'det_external_sppr', 'fix_EE_0_cases')
NEGATIVE_TOLERANCE = 1e-10
ENGINE_FILES = ('ModelData.py', 'PPRCalculator.py', 'utils.py')
_PINNED_ENGINES = {}


def _engine_paths(flags=None, model_path=None):
    paths = {name: ENGINE / name for name in (*ENGINE_FILES, 'create_PPRS_excel.py')}
    flags = flags or {}
    supplied = flags.get('engine_sources')
    if not supplied:
        return paths
    if not isinstance(supplied, dict) or set(supplied) - set(ENGINE_FILES):
        raise ValueError('Unsupported audited engine source names')
    if model_path is None:
        raise ValueError('Audited engine sources require the canonical model path')
    root = Path(model_path).resolve().parent
    hashes = flags.get('engine_source_hashes')
    if not isinstance(hashes, dict) or any(not hashes.get(name) for name in ENGINE_FILES):
        raise ValueError('Audited hashes for PPRCalculator.py, ModelData.py and utils.py are required')
    for name, relative in supplied.items():
        if not isinstance(relative, str) or Path(relative).is_absolute():
            raise ValueError(f'Audited engine source must be model-relative: {name}')
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f'Audited engine source missing or outside model: {name}')
        paths[name] = path
    for name in ENGINE_FILES:
        if _hash_bytes(paths[name].read_bytes()) != hashes[name]:
            raise ValueError(f'Audited engine hash mismatch: {name}')
    return paths


def engine_identity(flags=None, model_path=None):
    """Hashes of the actual audited engine and the current canonical registry."""
    return {name: _hash_bytes(path.read_bytes())
            for name, path in _engine_paths(flags, model_path).items()}


def _scientific_ast(path):
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    calculator = next(node for node in tree.body
                      if isinstance(node, ast.ClassDef) and node.name == 'PPRCalculator')
    class StripDocstrings(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            return node
    loader_methods = {'__init__', 'from_dict', 'from_modeldata', '_fill_properties',
                      'apply_lim', '_reconcile_normalized_diet_biomass_accum'}
    return {node.name: ast.dump(StripDocstrings().visit(node), include_attributes=False)
            for node in calculator.body if isinstance(node, ast.FunctionDef)
            and node.name not in loader_methods}


def _isolated_module(path, name, dependencies):
    """Load unmodified audited source with local engine imports, never aliases.

    Keeping its qualified module in sys.modules supports dataclasses/deepcopy;
    standard ModelData/PPRCalculator/utils names and other models stay untouched.
    Workers receive paths and load their own modules; no calculator is pickled.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    original_import = builtins.__import__
    def local_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and name in dependencies:
            return dependencies[name]
        return original_import(name, globals, locals, fromlist, level)
    module.__dict__['__builtins__'] = {**vars(builtins), '__import__': local_import}
    sys.modules[name] = module
    try:
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def _engine(flags=None, model_path=None):
    if str(ENGINE) not in sys.path:
        sys.path.insert(0, str(ENGINE))
    import create_PPRS_excel as exporter
    from ModelData import ModelData
    from PPRCalculator import PPRCalculator, DEFAULT_DIAGNOSTIC_THRESHOLDS
    if flags and flags.get('engine_sources'):
        paths = _engine_paths(flags, model_path)
        identity = engine_identity(flags, model_path)
        # Loader differences are precisely why the archived engine is selected.
        # All calculation methods/helpers must remain the canonical algorithms.
        cache_key = tuple((name, str(paths[name]), identity[name]) for name in ENGINE_FILES)
        if cache_key not in _PINNED_ENGINES:
            if _scientific_ast(paths['PPRCalculator.py']) != _scientific_ast(ENGINE / 'PPRCalculator.py'):
                raise ValueError('Audited engine scientific methods differ from the canonical supported algorithms')
            prefix = '_sppr_audited_' + _hash_bytes(repr(cache_key).encode('utf-8'))
            data = _isolated_module(paths['ModelData.py'], prefix + '_ModelData', {})
            utility = _isolated_module(paths['utils.py'], prefix + '_utils', {})
            calculator = _isolated_module(paths['PPRCalculator.py'], prefix + '_PPRCalculator',
                                          {'ModelData': data, 'utils': utility})
            _PINNED_ENGINES[cache_key] = (exporter, data.ModelData, calculator.PPRCalculator,
                                         calculator.DEFAULT_DIAGNOSTIC_THRESHOLDS)
        return _PINNED_ENGINES[cache_key]
    return exporter, ModelData, PPRCalculator, DEFAULT_DIAGNOSTIC_THRESHOLDS


def method_inventory():
    """Return the live canonical exporter inventory, in its defined order."""
    return tuple(_engine()[0].ALL_METHOD_KEYS)


def _defaults(callable_):
    return {name: p.default for name, p in inspect.signature(callable_).parameters.items()
            if name != 'self' and p.default is not inspect.Parameter.empty}


def _constructor(flags, model_path=None):
    _, _, calculator, _ = _engine(flags, model_path)
    supplied = flags.get('constructor')
    if not isinstance(supplied, dict):
        raise ValueError('Audited constructor settings are required; stock loading is not permitted')
    defaults = _defaults(calculator.from_modeldata)
    unknown = set(supplied) - set(defaults)
    if unknown:
        raise ValueError(f'Unknown audited constructor settings: {sorted(unknown)}')
    return {**defaults, **supplied}


def method_settings(key, flags, model_path=None):
    """Resolve canonical variant settings while preserving audited detritus choices."""
    exporter, _, calculator, thresholds = _engine(flags, model_path)
    if key not in exporter.SPEC_BY_KEY:
        raise KeyError(f'Unknown canonical SPPR method: {key}')
    source_resolved = exporter.SPEC_BY_KEY[key].source_resolved
    option = ('With Egestion' if 'WithEgestion' in key else
              'GE' if '_GE' in key else 'TE' if '_TE' in key else None)
    recorded = flags.get('methods', {}).get(option, {})
    diagnostic_settings = flags.get('diagnostics', {})
    det = {k: v for k, v in _defaults(calculator.SPPR_new).items() if k in DET_KEYS}
    det.update({k: v for k, v in diagnostic_settings.items() if k in DET_KEYS})
    det.update({k: v for k, v in recorded.items() if k in DET_KEYS})
    kwargs = {}
    if key == 'SPPR_1986':
        target = 'SPPR_1986'
    elif key.startswith('SPPR_1995'):
        target = 'SPPR_1995'
        kwargs = {'global_TE': .1 if key.endswith('TE0.1') else 'mean',
                  'weights': 'catch' if key.endswith('_catch') else 'consumption'}
    elif key.startswith('Ulanowicz_'):
        target = 'SPPR_EwE_Ulanowicz'
        kwargs = {'TE_option': 'global' if 'global' in key else 'TE',
                  'global_TE': 'mean' if 'global' in key else None, 'use_EE': False,
                  'weights': 'catch' if key.endswith('_catch') else 'consumption'}
    elif key.startswith('EwE_'):
        target = 'SPPR_EwE'
        use_ee = key == 'EwE_TE_EE'
        kwargs = {'TE_option': 'TE', 'use_EE': use_ee, 'return_paths': use_ee,
                  'silent': True, 'max_paths': 100_000}
    elif key == 'SPPR_2015':
        target = 'SPPR_2015'
    elif key.startswith('new_'):
        target = 'diagnose_sppr'
        kwargs = {**det, 'TE_option': option, 'short': False, 'flat': False,
                  'return_sppr': True,
                  'thresholds': {**thresholds, **diagnostic_settings.get('thresholds', {})}}
        if key == 'new_TE_noEEfix':
            kwargs['fix_EE_0_cases'] = False
        elif key == 'new_TE_EEfix':
            kwargs['fix_EE_0_cases'] = True
    elif key.startswith('sym_'):
        target = 'SPPR_symbolic'
        kwargs = {**_defaults(calculator.SPPR_symbolic), **det, 'TE_option': option,
                  'diet_import_option': 'as_PP' if key.endswith('_asPP') else 'as_DC'}
    elif key.startswith('MC_'):
        target = 'monte_carlo_SPPR'
        mc = flags.get('mc', {})
        kwargs = {**_defaults(calculator.monte_carlo_SPPR),
                  **{k: v for k, v in det.items() if k != 'fix_EE_0_cases'},
                  'n_samples': mc.get('n_samples', exporter.DEFAULT_MC_SAMPLES),
                  'TE_error_percent': mc.get('TE_error_percent', 10),
                  'TE_error_cut_percent': mc.get('TE_error_cut_percent', 20),
                  'TE_option': option, 'kind': 'new', 'silent': True,
                  'exclude_diverged': True, 'return_diagnostics': True,
                  'method_kwargs': {'fix_EE_0_cases': True if option == 'TE' else det['fix_EE_0_cases']}}
    else:
        raise ValueError(f'Canonical method has no full-return adapter: {key}')
    return {'method': key, 'target': target, 'kwargs': kwargs,
            'source_resolved': source_resolved,
            'description': exporter.SPEC_BY_KEY[key].description,
            'seed': flags.get('mc', {}).get('seed') if key.startswith('MC_') else None,
            'mc_policy_origin': ({name: ('audited settings' if name in flags.get('mc', {}) else
                'canonical exporter execution policy; no historical value inferred')
                for name in ('n_samples','TE_error_percent','TE_error_cut_percent','seed')}
                if key.startswith('MC_') else None)}


def _mask_kind(value):
    if value is None or value is pd.NA or value is pd.NaT:
        return 'null'
    if isinstance(value, (float, np.floating)):
        if math.isnan(value):
            return 'nan'
        if math.isinf(value):
            return 'positive_infinity' if value > 0 else 'negative_infinity'
    return None


def encode_lossless(value):
    """JSON-safe typed representation, with distinct null and nonfinite masks."""
    if isinstance(value, pd.DataFrame):
        raw = value.to_numpy(dtype=object)
        return {'type': 'dataframe', 'index': encode_lossless(value.index.tolist()),
                'index_names': encode_lossless(list(value.index.names)),
                'columns': encode_lossless(value.columns.tolist()),
                'column_names': encode_lossless(list(value.columns.names)),
                'dtypes': [str(dtype) for dtype in value.dtypes],
                'shape': list(raw.shape), 'data': encode_lossless(raw.tolist()),
                'masks': {kind: [[_mask_kind(cell) == kind for cell in row] for row in raw]
                          for kind in ('null', 'nan', 'positive_infinity', 'negative_infinity')}}
    if isinstance(value, pd.Series):
        return {'type': 'series', 'name': encode_lossless(value.name),
                'frame': encode_lossless(value.to_frame())}
    if isinstance(value, np.ndarray):
        flat = value.ravel().tolist()
        return {'type': 'ndarray', 'dtype': str(value.dtype), 'shape': list(value.shape),
                'data': encode_lossless(value.tolist()),
                'masks': {kind: np.array([_mask_kind(cell) == kind for cell in flat],
                                        dtype=bool).reshape(value.shape).tolist()
                          for kind in ('null', 'nan', 'positive_infinity', 'negative_infinity')}}
    kind = _mask_kind(value)
    if kind:
        return None if kind == 'null' else {'type': 'float', 'value': kind}
    if isinstance(value, np.generic):
        return encode_lossless(value.item())
    if isinstance(value, dict):
        if all(isinstance(k, str) for k in value):
            return {k: encode_lossless(v) for k, v in value.items()}
        return {'type': 'mapping', 'items': [[encode_lossless(k), encode_lossless(v)]
                                            for k, v in value.items()]}
    if isinstance(value, tuple):
        return {'type': 'tuple', 'items': [encode_lossless(v) for v in value]}
    if isinstance(value, (list, set)):
        return [encode_lossless(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Path):
        return str(value)
    import sympy
    if isinstance(value, sympy.Basic):
        return {'type': 'sympy', 'srepr': sympy.srepr(value), 'text': str(value)}
    if isinstance(value, sympy.MatrixBase):
        return {'type': 'sympy_matrix', 'shape': list(value.shape),
                'data': encode_lossless(value.tolist())}
    raise TypeError(f'Unrecognized evidence type: {type(value).__module__}.{type(value).__name__}')


def _json_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('utf-8')


def diagnostics_for_table(value):
    """Restore diagnostic keys; blank nonfinite cells without altering evidence."""
    if isinstance(value, list):
        return [diagnostics_for_table(item) for item in value]
    if isinstance(value, dict):
        if set(value) == {'type', 'value'} and value['type'] == 'float' and value['value'] in {
                'nan', 'positive_infinity', 'negative_infinity'}:
            return None
        if set(value) == {'type', 'items'} and value['type'] == 'mapping':
            return {diagnostics_for_table(key): diagnostics_for_table(item)
                    for key, item in value['items']}
        if set(value) == {'type', 'items'} and value['type'] == 'tuple':
            return tuple(diagnostics_for_table(item) for item in value['items'])
        return {key: diagnostics_for_table(item) for key, item in value.items()}
    return value


def _hash_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _runtime(model):
    fields = ('_groups_df', '_DC', '_det_fate', 'p', 'q', 'catch', 'predation',
              'growth', 'immigration', 'emigration', 'net_migration', 'respiration',
              'egestion', 'M0', 'det_export', 'EE', 'GE', 'GS', 'TL', 'seq2name',
              'name2seq', 'diet_normalization_rows', 'diet_normalization_balance_ledger',
              'balance_BA_after_DC_normalization')
    return encode_lossless({k: getattr(model, k) for k in fields if hasattr(model, k)})


def _load(model_path, constructor, flags=None):
    _, modeldata, calculator, _ = _engine(flags, model_path)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        source = modeldata(str(model_path))
        model = calculator.from_modeldata(source, **constructor)
    source_state = encode_lossless({'groups': source.groups_data, 'diet': source.DC,
                                    'detritus_fate': source.det_fate})
    return model, source_state, [f'{w.category.__name__}: {w.message}' for w in caught]


def _error():
    kind, exc, _ = sys.exc_info()
    return {'type': kind.__name__, 'message': str(exc), 'traceback': traceback.format_exc()}


def _group_metadata(model):
    types = _engine()[0]._group_type_map(model)
    return [{'id': int(seq), 'name': str(model.seq2name[seq]), 'type': types.get(int(seq)),
             'synthetic': types.get(int(seq)) == 'Import'} for seq in model.get_groups_df().index]


def _numeric(value):
    return float(value) if isinstance(value, (int, float, np.number)) and np.isfinite(value) else None


def _extract_result(model, settings, result):
    exporter = _engine()[0]
    target = settings['target']
    diagnostic = result[0] if target == 'diagnose_sppr' else None
    raw = (result[1] if target in ('diagnose_sppr', 'SPPR_symbolic') else
           result[0] if isinstance(result, tuple) else result)
    if raw is None:
        return {'scopes': {scope: {} for scope in SCOPES},
                'annual_status': {scope: 'unavailable: returned no coefficients' for scope in SCOPES},
                'diagnostics': encode_lossless(diagnostic), 'source_matrix': None,
                'negative_entries': [], 'reconciliation': {'scope_sums_verified': True}}
    frame = exporter._to_seq_frame(model, raw)
    if not frame.index.is_unique or not frame.columns.is_unique:
        raise ValueError('Returned SPPR matrix has duplicate axes')
    values = frame.to_numpy(dtype=float)
    scope_sums = exporter._source_sums(model, frame, settings['source_resolved'])
    scopes = {scope: {str(model.seq2name[index]): _numeric(value)
                     for index, value in scope_sums[sum_key].items()}
              for scope, sum_key in [('all','SUM_ALL'),('inner','SUM_INNER'),('PP','SUM_PP')]}
    negatives = [{'method': settings['method'], 'matrix': 'SPPR', 'recipient_id': int(frame.index[i]),
                  'recipient_name': str(model.seq2name[frame.index[i]]),
                  'source_id': encode_lossless(frame.columns[j]),
                  'source_name': str(model.seq2name.get(frame.columns[j], frame.columns[j])),
                  'value': float(values[i,j]), 'tolerance': NEGATIVE_TOLERANCE}
                 for i,j in np.argwhere(values < -NEGATIVE_TOLERANCE)]
    mc = None
    if target == 'monte_carlo_SPPR':
        mc = {**result[5], 'n_samples': settings['kwargs']['n_samples'], 'reject_frac': result[2]}
    annual = {}
    for scope in SCOPES:
        if scope == 'PP' and not settings['source_resolved']:
            status = 'unavailable: source scope unsupported'
        elif not any(v is not None for v in scopes[scope].values()):
            status = 'unavailable: no finite coefficients'
        elif np.isinf(values).any():
            status = 'unavailable: nonfinite source contributions'
        elif negatives:
            status = 'FAIL: negative SPPR in a source-model group'
        elif diagnostic and diagnostic.get('status') == 'FAIL':
            status = 'FAIL: configuration diagnostic'
        elif mc and mc['n_accepted'] / mc['n_samples'] < .8:
            status = f"unavailable: MC acceptance {mc['n_accepted']}/{mc['n_samples']} below 80%"
        else:
            status = 'ok'
        annual[scope] = status
    # JSON preserves finite IEEE doubles. Reopen and independently sum the saved
    # matrix by explicit source membership before claiming coefficient equivalence.
    encoded = encode_lossless(frame)
    reopened = json.loads(_json_bytes(encoded))
    restored = np.array([[float(cell) if not isinstance(cell, dict) and cell is not None else
                         (np.nan if cell is None or cell['value'] == 'nan' else
                          np.inf if cell['value'] == 'positive_infinity' else -np.inf)
                         for cell in row] for row in reopened['data']])
    np.testing.assert_equal(restored, values)
    for scope, sum_key in [('all','SUM_ALL'),('inner','SUM_INNER'),('PP','SUM_PP')]:
        if scope == 'PP' and not settings['source_resolved']:
            continue
        omitted = set(model.get_Import_seq()) if scope != 'all' else set()
        if scope == 'PP':
            omitted.update(model.get_DET_seq())
        selected = [j for j,col in enumerate(frame.columns) if col not in omitted]
        for i,index in enumerate(frame.index):
            cells = restored[i, selected]
            expected = float(np.nansum(cells)) if np.any(~np.isnan(cells)) else np.nan
            np.testing.assert_allclose(expected, scope_sums[sum_key].loc[index], rtol=1e-12, atol=1e-12, equal_nan=True)
    return {'scopes': scopes, 'annual_status': annual, 'diagnostics': encode_lossless(diagnostic),
            'mc_diagnostics': encode_lossless(mc), 'source_matrix': encoded,
            'negative_entries': negatives, 'reconciliation': {'scope_sums_verified': True,
                'source_matrix_masks_verified': True, 'unique_axes': True,
                'rtol': 1e-12, 'atol': 1e-12}}


def _run(model, settings):
    model = copy.deepcopy(model)
    before = _runtime(model)
    started = time.monotonic()
    state = np.random.get_state()
    retained_return = None
    caught = []
    try:
        if settings['seed'] is not None:
            np.random.seed(settings['seed'])
        rng_before = encode_lossless(np.random.get_state()) if settings['method'].startswith('MC_') else None
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            result = getattr(model, settings['target'])(**settings['kwargs'])
        retained_return = encode_lossless(result)
        extracted = _extract_result(model, settings, result)
        after = _runtime(model)
        restrictions = sorted(set(status for status in extracted['annual_status'].values()
                                  if status != 'ok'))
        return {'status': 'ok', 'reason': '; '.join(restrictions), **extracted, 'return': retained_return,
                'runtime_before': before, 'runtime_after': after,
                'runtime_before_sha256': _hash_bytes(_json_bytes(before)),
                'runtime_after_sha256': _hash_bytes(_json_bytes(after)),
                'rng_before': rng_before,
                'warnings': [f'{w.category.__name__}: {w.message}' for w in caught],
                'elapsed_seconds': time.monotonic() - started}
    except Exception:
        return {'status': 'failed', 'reason': 'Method execution or evidence reconciliation failed',
                'exception': _error(), 'runtime_before': before, 'runtime_after': _runtime(model),
                'return': retained_return, 'warnings': [f'{w.category.__name__}: {w.message}' for w in caught],
                'elapsed_seconds': time.monotonic() - started}
    finally:
        if settings['seed'] is not None:
            np.random.set_state(state)


def _worker(connection, model_path, constructor, flags):
    try:
        model, source, notices = _load(model_path, constructor, flags)
        connection.send({'status': 'ready', 'source_state': source, 'runtime': _runtime(model),
                         'groups': _group_metadata(model), 'warnings': notices})
    except Exception:
        connection.send({'status': 'constructor_failed', 'exception': _error()})
        connection.close()
        return
    try:
        while True:
            settings = connection.recv()
            if settings is None:
                return
            connection.send(_run(model, settings))
    except (EOFError, BrokenPipeError):
        pass
    finally:
        connection.close()


def _save(path, document):
    raw = _json_bytes(document)
    compressed = gzip.compress(raw, mtime=0)
    path.write_bytes(compressed)
    if gzip.decompress(path.read_bytes()) != raw:
        raise IOError(f'Evidence round trip failed: {path}')
    return {'path': path.name, 'sha256': _hash_bytes(compressed), 'availability': 'present'}


def compute_methods(model_path, flags, method_keys, evidence_dir, progress=print, *, method_timeout=None):
    """Return coefficients/outcomes and save full returns beneath ``evidence_dir``.

    ``flags`` contains the audited ``constructor`` and either per-option
    ``methods`` configuration or common ``diagnostics`` settings. Optional ``mc``
    settings document samples/error/clip/seed; absent MC settings use the existing
    canonical exporter settings (100 draws, 10%/20%, unseeded). Failures never
    become numeric zeros or scientific diagnostic grades. This function does not
    authorize publication or researcher approval.
    """
    model_path, evidence_dir = Path(model_path).resolve(), Path(evidence_dir).resolve()
    keys = list(method_keys)
    if len(keys) != len(set(keys)):
        raise ValueError('Method keys must be unique')
    supplied_flags = flags
    flags = flags if isinstance(flags, dict) else {}
    registry = _engine()[0]
    for key in keys:
        if key not in registry.SPEC_BY_KEY:
            raise KeyError(f'Unknown canonical SPPR method: {key}')
    configuration_error = None
    try:
        constructor = _constructor(flags, model_path)
        settings = {key: method_settings(key, flags, model_path) for key in keys}
        executed_hashes = engine_identity(flags, model_path)
    except (TypeError, ValueError, OSError, ImportError, SyntaxError):
        constructor, configuration_error = None, _error()
        executed_hashes = None
        settings = {key: {'method': key, 'source_resolved': registry.SPEC_BY_KEY[key].source_resolved,
                         'target': None, 'kwargs': None, 'configuration_unavailable': True} for key in keys}
    default_timeout = (flags.get('method_timeout_seconds', 180.)
                       if method_timeout is None else method_timeout)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    model_bytes = model_path.read_bytes()
    identity = {'model_id': model_path.parent.name, 'model_sha256': _hash_bytes(model_bytes),
                'flags': encode_lossless(supplied_flags), 'constructor': constructor,
                'engine_hashes': executed_hashes,
                'adapter_sha256': _hash_bytes(Path(__file__).read_bytes()),
                'environment': {'python': sys.version, 'platform': platform.platform(),
                                'numpy': np.__version__, 'pandas': pd.__version__}}
    answer = {**identity, 'methods': {}, 'groups': [], 'diagnostic_rows': []}
    process = connection = model = initial = None
    if configuration_error:
        initial = {'status':'configuration_unavailable', 'exception':configuration_error}
        answer['constructor_evidence'] = _save(evidence_dir/'constructor.json.gz',
                    {'schema_version':1,'identity':identity,'constructor_outcome':initial})

    def close_worker():
        nonlocal process, connection
        if process is not None:
            if process.is_alive():
                process.terminate()
            process.join(timeout=5)
        if connection is not None:
            connection.close()
        process = connection = None

    try:
        for key in keys:
            timeout = flags.get('method_timeout_overrides_seconds', {}).get(key, default_timeout)
            if timeout is not None and timeout < 0:
                raise ValueError('Method timeout cannot be negative')
            if progress:
                progress(f'{model_path.parent.name}: {key}')
            if not configuration_error and (initial is None or (timeout and process is None) or (not timeout and model is None)):
                if timeout:
                    parent, child = mp.get_context('spawn').Pipe()
                    process = mp.get_context('spawn').Process(target=_worker,
                        args=(child,str(model_path),constructor,flags), daemon=True)
                    try:
                        process.start()
                        child.close()
                        connection = parent
                        initial = (connection.recv() if connection.poll(300) else
                                   {'status':'constructor_timeout', 'reason':'Constructor exceeded 300 seconds'})
                    except Exception:
                        initial = {'status':'constructor_failed', 'exception':_error()}
                else:
                    try:
                        model, source, notices = _load(model_path, constructor, flags)
                        initial = {'status':'ready','source_state':source,'runtime':_runtime(model),
                                   'groups':_group_metadata(model),'warnings':notices}
                    except Exception:
                        initial = {'status':'constructor_failed','exception':_error()}
                answer['groups'] = initial.get('groups', [])
                answer['constructor_evidence'] = _save(evidence_dir/'constructor.json.gz',
                    {'schema_version':1,'identity':identity,'constructor_outcome':initial})
            if initial['status'] != 'ready':
                outcome = {'status':'NOT_RUN','reason':f"Constructor unavailable: {initial['status']}",
                           'constructor_outcome':initial}
                if initial.get('exception'):
                    outcome['reason'] += ': ' + initial['exception']['message']
            elif timeout:
                try:
                    connection.send(settings[key])
                    if connection.poll(timeout):
                        outcome = connection.recv()
                    else:
                        outcome = {'status':'timeout', 'reason':f'Method exceeded {timeout:g} seconds',
                                   'timeout_seconds':timeout}
                        close_worker()
                except Exception:
                    outcome = {'status':'crashed', 'reason':'Method worker ended without a result',
                               'exception':_error()}
                    close_worker()
            else:
                outcome = _run(model, settings[key])
            outcome.setdefault('scopes', {scope:{} for scope in SCOPES})
            outcome.setdefault('annual_status', {scope:f"unavailable: {outcome['status']}" for scope in SCOPES})
            if outcome.get('exception'):
                outcome['reason'] += ': ' + outcome['exception']['type'] + ': ' + outcome['exception']['message']
            document = {'schema_version':1, 'identity':identity, 'settings':encode_lossless(settings[key]),
                        'method_timeout_seconds': timeout,
                        'timestamp':datetime.now(timezone.utc).isoformat(),
                        'groups':answer['groups'], 'matrix_orientation':'recipient groups by basal sources',
                        'sppr_units':'wet-weight primary production equivalent per wet-weight unit of group catch',
                        'scope_definitions':{'all':'all returned basal sources','inner':'all except Import',
                                             'PP':'all except Import and detritus; unavailable for scalar methods'},
                        'decomposition_available':settings[key]['source_resolved'], **outcome}
            evidence = _save(evidence_dir/f'{key}.json.gz', document)
            answer['methods'][key] = {k:v for k,v in outcome.items()
                if k not in ('return','source_matrix','runtime_before','runtime_after','rng_before','constructor_outcome')}
            answer['methods'][key]['settings'] = settings[key]
            answer['methods'][key]['evidence'] = evidence
            if outcome.get('diagnostics'):
                answer['diagnostic_rows'].append({'method':key, **outcome['diagnostics']})
            if model_path.read_bytes() != model_bytes:
                raise RuntimeError('Canonical model changed during execution; refuse mixed-version publication')
    finally:
        close_worker()
    answer['evidence_index'] = _save(evidence_dir/'method_coverage.json.gz',
                                    {'schema_version':1, **answer})
    return answer
