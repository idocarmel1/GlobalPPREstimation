"""Authenticate explicit replay of retained calculations without new loading.

This opt-in records an archived algorithm identity; it does not certify equality
with the current engine. Completed state restoration never calls a constructor,
from_dict, normalization, balancing, or an EE-floor transformation.
"""
from __future__ import annotations

from copy import deepcopy
import gzip
import hashlib
import inspect
import json
from pathlib import Path, PureWindowsPath
import re

import numpy as np
import pandas as pd


ENGINE_FILES = ('ModelData.py', 'PPRCalculator.py', 'utils.py')
VECTORS = ('p', 'q', 'catch', 'predation', 'growth', 'immigration', 'emigration',
           'net_migration', 'respiration', 'egestion', 'M0', 'det_export',
           'EE', 'GE', 'GS', 'TL')
REQUIRED = ('_groups_df', '_DC', '_det_fate', 'seq2name', 'name2seq', *VECTORS)
FLOOR_FIELDS = ('ee_floor', 'EE_before_floor', 'M0_before_floor', 'source_EE',
                'source_M0', 'external_mortality_export', 'ee_floor_ledger',
                'ee_floor_info', '_ee_floor_base', '_initialization_settings')


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _local_bytes(root, reference, label):
    if not isinstance(reference, dict):
        raise ValueError(f'Audited replay {label} reference is required')
    relative, expected = reference.get('relative_path'), reference.get('sha256')
    if (not isinstance(relative, str) or not relative
            or Path(relative).is_absolute() or PureWindowsPath(relative).anchor):
        raise ValueError(f'Audited replay {label} path must be model-relative')
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f'Audited replay {label} path is outside the model')
    if not isinstance(expected, str) or re.fullmatch(r'[0-9a-f]{64}', expected) is None:
        raise ValueError(f'Audited replay {label} SHA-256 hash is required')
    if not path.is_file():
        raise ValueError(f'Audited replay {label} source is missing')
    raw = path.read_bytes()
    if _sha(raw) != expected:
        raise ValueError(f'Audited replay {label} hash mismatch')
    return path, raw


def validate_replay(flags, model_path):
    """Return the authenticated opt-in descriptor, or None when absent."""
    if not flags or 'audited_replay' not in flags:
        return None
    descriptor = flags['audited_replay']
    if (not isinstance(descriptor, dict)
            or type(descriptor.get('schema_version')) is not int
            or descriptor['schema_version'] != 1
            or descriptor.get('mode') not in ('completed_runtime', 'recorded_constructor')):
        raise ValueError('Unsupported audited replay descriptor')
    model_path = Path(model_path).resolve()
    if not model_path.is_file() or _sha(model_path.read_bytes()) != descriptor.get('model_sha256'):
        raise ValueError('Audited replay canonical model hash mismatch')
    root = model_path.parent
    sources, hashes = flags.get('engine_sources'), flags.get('engine_source_hashes')
    if (not isinstance(sources, dict) or not isinstance(hashes, dict)
            or set(sources) != set(ENGINE_FILES)
            or not set(ENGINE_FILES).issubset(hashes)):
        raise ValueError('Audited replay requires all exact engine sources and hashes')
    for name in ENGINE_FILES:
        _local_bytes(root, {'relative_path': sources[name], 'sha256': hashes[name]}, name)
    if flags.get('calculation_engine_source') is not None:
        _local_bytes(root, {'relative_path': flags['calculation_engine_source'],
                           'sha256': flags.get('calculation_engine_sha256')}, 'calculation engine')
    _local_bytes(root, descriptor.get('provenance'), 'provenance')
    if not isinstance(flags.get('constructor'), dict):
        raise ValueError('Audited replay requires recorded constructor settings')
    if descriptor['mode'] == 'completed_runtime':
        reference = descriptor.get('runtime')
        _local_bytes(root, reference, 'runtime')
        if (not isinstance(reference.get('keys', []), list)
                or any(not isinstance(key, str) for key in reference.get('keys', []))):
            raise ValueError('Audited replay runtime keys must be a list of names')
    elif 'runtime' in descriptor:
        raise ValueError('Recorded-constructor replay must not declare a completed runtime')
    return deepcopy(descriptor)


def _axis(values, names):
    if not isinstance(values, list) or not isinstance(names, list) or not names:
        raise ValueError('Malformed runtime dataframe axes')
    if len(names) > 1:
        return pd.MultiIndex.from_tuples([tuple(value) for value in values], names=names)
    return pd.Index(values, name=names[0], tupleize_cols=False)


def _verify_masks(value, data):
    raw = np.asarray(data, dtype=object)
    if list(raw.shape) != value['shape']:
        raise ValueError('Runtime data shape disagrees with masks')
    kinds = ('null', 'nan', 'positive_infinity', 'negative_infinity')
    masks = value.get('masks')
    if not isinstance(masks, dict) or set(masks) != set(kinds):
        raise ValueError('Completed runtime requires all missingness masks')
    classified = []
    for item in raw.ravel():
        kind = 'null' if item is None else None
        if isinstance(item, (float, np.floating)):
            kind = ('nan' if np.isnan(item) else 'positive_infinity' if np.isposinf(item)
                    else 'negative_infinity' if np.isneginf(item) else None)
        classified.append(kind)
    for kind in kinds:
        expected = np.array([item == kind for item in classified], dtype=bool).reshape(raw.shape)
        actual = np.asarray(masks[kind])
        if actual.dtype.kind != 'b' or actual.shape != raw.shape or not np.array_equal(actual, expected):
            raise ValueError(f'Runtime {kind} mask disagrees with saved values')


def decode_lossless(value):
    """Decode the adapter's inert JSON vocabulary, with no code evaluation."""
    if isinstance(value, list):
        return [decode_lossless(item) for item in value]
    if not isinstance(value, dict):
        return value
    kind = value.get('type')
    if kind == 'float' and set(value) == {'type', 'value'}:
        values = {'nan': np.nan, 'positive_infinity': np.inf, 'negative_infinity': -np.inf,
                  'inf': np.inf, '-inf': -np.inf}
        if value['value'] not in values:
            raise ValueError('Unknown runtime nonfinite marker')
        return values[value['value']]
    if kind in ('mapping', 'tuple', 'dict') and set(value) == {'type', 'items'}:
        items = decode_lossless(value['items'])
        if kind == 'tuple':
            return tuple(items)
        result = dict(items)
        if len(result) != len(items):
            raise ValueError('Duplicate runtime mapping keys')
        return result
    if kind == 'tuple' and set(value) == {'type', 'values'}:
        return tuple(decode_lossless(value['values']))
    # The older full-runtime codec retained values and dtype strings, but no
    # index names or null masks. Preserve exactly that evidence availability.
    if kind == 'DataFrame':
        index, columns = decode_lossless(value['index']), decode_lossless(value['columns'])
        frame = pd.DataFrame(decode_lossless(value['values']), index=index, columns=columns, dtype=object)
        if len(value.get('dtypes', [])) != len(columns):
            raise ValueError('Legacy runtime dataframe dtypes are missing')
        for i, dtype in enumerate(value['dtypes']):
            frame.isetitem(i, frame.iloc[:, i].astype(dtype))
        return frame
    if kind == 'Series':
        return pd.Series(decode_lossless(value['values']), index=decode_lossless(value['index']),
                         name=decode_lossless(value['name']))
    if kind == 'dataframe':
        index = _axis(decode_lossless(value['index']), decode_lossless(value['index_names']))
        columns = _axis(decode_lossless(value['columns']), decode_lossless(value['column_names']))
        data = decode_lossless(value['data'])
        if value.get('shape') != [len(index), len(columns)] or len(value['dtypes']) != len(columns):
            raise ValueError('Runtime dataframe shape mismatch')
        _verify_masks(value, data)
        frame = pd.DataFrame(data, index=index, columns=columns, dtype=object)
        for i, dtype in enumerate(value['dtypes']):
            frame.isetitem(i, frame.iloc[:, i].astype(dtype))
        return frame
    if kind == 'series':
        frame = decode_lossless(value['frame'])
        if not isinstance(frame, pd.DataFrame) or frame.shape[1] != 1:
            raise ValueError('Malformed runtime series')
        series = frame.iloc[:, 0].copy()
        series.name = decode_lossless(value['name'])
        return series
    if kind == 'ndarray':
        if set(value) == {'type', 'values'}:
            return np.asarray(decode_lossless(value['values']))
        data = decode_lossless(value['data'])
        _verify_masks(value, data)
        array = np.asarray(data, dtype=value['dtype'])
        if list(array.shape) != value.get('shape'):
            raise ValueError('Runtime array shape mismatch')
        return array
    if kind in ('sympy', 'sympy_matrix', 'ModelData', 'PPRCalculator'):
        raise ValueError('Executable objects or symbolic expressions are not inert runtime attributes')
    return {key: decode_lossless(item) for key, item in value.items()}


def _validate_state(state):
    if not isinstance(state, dict):
        raise ValueError('Completed runtime must be an attribute mapping')
    missing = set(REQUIRED) - set(state)
    if missing:
        raise ValueError('Completed runtime missing required attributes: '+', '.join(sorted(missing)))
    groups, diet, fate = (state[name] for name in ('_groups_df', '_DC', '_det_fate'))
    if not all(isinstance(frame, pd.DataFrame) for frame in (groups, diet, fate)):
        raise ValueError('Completed runtime group/diet/fate frames are required')
    ids = groups.index
    if not ids.is_unique or not groups.columns.is_unique or 'group_name' not in groups:
        raise ValueError('Completed runtime group axes or names are invalid')
    expected = set(ids)
    for label, frame in (('diet', diet), ('detritus fate', fate)):
        if not frame.index.is_unique or not frame.columns.is_unique or set(frame.index) != expected:
            raise ValueError(f'Completed runtime {label} axes disagree with groups')
    if set(diet.columns) != expected or not set(fate.columns).issubset(expected):
        raise ValueError('Completed runtime diet/fate axes disagree with groups')
    for name in VECTORS:
        vector = state[name]
        if not isinstance(vector, pd.Series) or not vector.index.is_unique or set(vector.index) != expected:
            raise ValueError(f'Completed runtime {name} axes disagree with groups')
    names = groups['group_name'].to_dict()
    if (state['seq2name'] != names or len(set(names.values())) != len(names)
            or state['name2seq'] != {name: seq for seq, name in names.items()}):
        raise ValueError('Completed runtime group name mappings disagree')
    if state.get('use_ee_floor'):
        missing_floor = set(FLOOR_FIELDS) - set(state)
        if missing_floor:
            raise ValueError('Completed floor runtime missing attributes: '+', '.join(sorted(missing_floor)))
    return state


def restore_runtime(calculator, flags, model_path):
    """Rehydrate only authenticated completed attributes and derived dimensions."""
    descriptor = validate_replay(flags, model_path)
    if descriptor is None or descriptor['mode'] != 'completed_runtime':
        raise ValueError('Completed-runtime replay must be explicitly requested')
    path, raw = _local_bytes(Path(model_path).resolve().parent, descriptor['runtime'], 'runtime')
    payload = json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)
    for key in descriptor['runtime'].get('keys', []):
        if not isinstance(payload, dict) or key not in payload:
            raise ValueError(f'Completed runtime key is missing: {key}')
        payload = payload[key]
    omitted = []
    if isinstance(payload, dict) and payload.get('type') == 'dict':
        items = payload.get('items', [])
        ancillary = {'_model', 'balanced_model', 'n_balance_runs', 'is_balanced', 'detritus_resolution_info'}
        omitted = [key for key, _ in items if key in ancillary]
        payload = {**payload, 'items': [[key, value] for key, value in items if key not in ancillary]}
    state = _validate_state(decode_lossless(payload))
    # Do not accept state that could overwrite behavior on the pinned class.
    if any(name.startswith('__') or callable(getattr(calculator, name, None)) for name in state):
        raise ValueError('Completed runtime contains a callable or special attribute')
    model = calculator.__new__(calculator)
    model.__dict__.update(state)
    count = len(state['_groups_df'])
    if 'n_groups' in state and state['n_groups'] != count:
        raise ValueError('Completed runtime n_groups disagrees with group axes')
    if 'n_groups' not in state:
        model.n_groups = count
    constructor = flags['constructor']
    initialization = state.get('_initialization_settings', {})
    if not isinstance(initialization, dict):
        raise ValueError('Completed runtime initialization settings are malformed')
    for key, value in constructor.items():
        recorded = initialization.get(key, state.get(key))
        if (key in initialization or key in state) and recorded != value:
            raise ValueError(f'Completed runtime configuration conflicts with recorded settings: {key}')
    if ('is_underdetermined' in state and 'underdetermined' in constructor
            and state['is_underdetermined'] != constructor['underdetermined']):
        raise ValueError('Completed runtime underdetermined configuration conflicts with recorded settings')
    if 'underdetermined' in constructor and 'is_underdetermined' not in state:
        model.is_underdetermined = constructor['underdetermined']
    floor_info = state.get('ee_floor_info', {})
    threshold = state.get('ee_threshold', initialization.get('ee_threshold',
                          floor_info.get('ee_threshold', constructor.get('ee_threshold'))))
    if threshold is not None:
        if 'ee_threshold' not in state:
            model.ee_threshold = threshold
    elif (state.get('use_ee_floor') and hasattr(calculator, 'apply_ee_floor')
          and 'ee_threshold' in inspect.signature(calculator.apply_ee_floor).parameters):
        raise ValueError('Completed floor runtime has no recorded ee_threshold')
    # Adding dimension/config metadata must leave every restored attribute intact.
    if any(getattr(model, key) is not value for key, value in state.items()):
        raise ValueError('Completed runtime changed during restoration')
    source = {'runtime_replay_reference': deepcopy(descriptor['runtime']),
              'provenance_reference': deepcopy(descriptor['provenance']),
              'canonical_model_sha256': descriptor['model_sha256'],
              'omitted_noncomputational_attributes': omitted,
              'source_state_availability': 'Not reconstructed; authenticated completed state replayed'}
    return model, source, ['Authenticated completed runtime restored without initialization arithmetic; '
                          'the pinned historical engine is not claimed equivalent to the current engine.']
