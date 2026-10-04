"""Refresh three direct configurations for the observed non-exempt rate change."""
from pathlib import Path
import hashlib
import json
import math
import shutil
import sys
import time
import traceback
import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
MODEL = ROOT / 'regions/LME_050/models/50_502013_Coastal_Kyoto_Inoue_(2013)'
OUT = Path(__file__).parent / 'current_runtime_refresh'
OUT.mkdir(exist_ok=True)
CODE = OUT / 'executed_code'
CODE.mkdir(exist_ok=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value): return {'nonfinite': str(value)}
    if hasattr(value, 'tolist'): return clean(value.tolist())
    if hasattr(value, 'item'): return clean(value.item())
    return value

def dump(path, value):
    path.write_text(json.dumps(clean(value), indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')

source = MODEL / 'model.json'
source_hash = sha(source)
names = ('ModelData.py', 'PPRCalculator.py', 'utils.py')
active = ROOT / 'tools/scientific_code/PPREstimation'
active_hashes = {name: sha(active / name) for name in names}
for name in names:
    shutil.copyfile(active / name, CODE / name)
assert active_hashes == {name: sha(CODE / name) for name in names}
assert active_hashes == {name: sha(active / name) for name in names}, 'Concurrent code change'
shutil.copyfile(source, OUT / source.name)
assert sha(OUT / source.name) == source_hash
sys.path.insert(0, str(CODE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
settings = dict(underdetermined=True, zero_catch=True, zero_biomass_accum=False,
                default_gs=True, weight_flow=1.0, weight_guess=1.0,
                DC_tol=0.001, normalize_DC=True)
outcomes = []
for option in ('GE', 'TE', 'With Egestion'):
    label = option.replace(' ', '_')
    m = PPRCalculator.from_modeldata(ModelData(str(OUT / source.name)), **settings)
    if option == 'GE':
        for name, frame in [('loaded_groups', m._groups_df), ('normalized_DC', m._DC), ('detritus_fate', m._det_fate)]:
            frame.to_csv(OUT / (name + '.csv'))
    config = dict(TE_option=option, short=False, flat=False, return_sppr=True, thresholds=None,
                  det_collapse_mode='never', det_open_mode='none', det_theta=1., det_external_sppr=0.)
    start = time.monotonic()
    try:
        report, coefficients, A, L = m.diagnose_sppr(**config)
        dump(OUT / ('diagnose_sppr_' + label + '.json'), {'configuration': config, 'direct_diagnose_sppr_return': report})
        comparisons = {}
        for name, frame in [('SPPR', coefficients), ('A', A), ('L', L)]:
            frame.to_csv(OUT / (name + '_' + label + '.csv'))
            retained = pd.read_csv(MODEL / 'selected_pipeline' / (name + '_' + label + '.csv'), index_col=0)
            current = pd.read_csv(OUT / (name + '_' + label + '.csv'), index_col=0)
            assert retained.index.equals(current.index) and retained.columns.equals(current.columns)
            delta = np.abs(retained.to_numpy(dtype=float) - current.to_numpy(dtype=float))
            comparisons[name] = {'maximum_absolute_difference': float(np.nanmax(delta)),
                                 'equivalent_at_absolute_1e_12': bool(np.allclose(retained, current, atol=1e-12, rtol=0, equal_nan=True))}
        outcomes.append({'option': option, 'status': report['status'], 'matrix_comparison': comparisons,
                         'elapsed_seconds': time.monotonic() - start})
        print(option, report['status'], json.dumps(comparisons), flush=True)
    except Exception as exc:
        error = {'option': option, 'error': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
        dump(OUT / ('error_' + label + '.json'), error)
        outcomes.append(error)
        print(json.dumps(error), flush=True)
assert sha(source) == source_hash, 'Concurrent selected source change'
dump(OUT / 'refresh_receipt.json', {'canonical_sha256': source_hash, 'settings': settings,
      'executed_code_hashes': active_hashes, 'atol': 1e-12, 'rtol': 0,
      'ignored_runtime_fields': ['biomass_accum', 'biomass_accum_rate', 'growth', 'predation'],
      'trigger': 'Synthetic import pb/qb changed beyond tolerance under current engine',
      'outcomes': outcomes, 'historical_evidence_unchanged': True})
