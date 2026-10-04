"""Bounded refresh of the previously adopted methods for this model only."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import shutil
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
MODEL = ROOT / 'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json'
BASELINE = OUT / 'baseline'
ENGINE = ROOT / 'tools/scientific_code/PPREstimation'
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(ROOT / 'tools'))
sys.dont_write_bytecode = True


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')


def export():
    import numpy as np
    import openpyxl
    import create_PPRS_excel as cpe
    from ModelData import ModelData

    w = openpyxl.load_workbook(BASELINE / 'sppr_source.xlsx', read_only=True, data_only=True)
    header = list(next(w['sppr_all'].values))
    methods = header[header.index('group_name') + 1:]
    mc_rows = list(w['mc_diagnostics'].values)
    mc_count = int(mc_rows[1][1])
    assert mc_count == 75 and all(int(r[1]) == mc_count for r in mc_rows[1:])
    w.close()
    config = {'run_id': 'LME034_detritus_completion_20261001', 'started_utc': datetime.now(timezone.utc).isoformat(),
              'canonical_model_sha256': sha(MODEL), 'methods': methods, 'mc_samples': mc_count,
              'parent_numpy_python_seed': 20261001, 'method_timeout_seconds': 180,
              'monte_carlo_worker_seed': 'Unspecified native spawned-worker RNG; retained results are run-specific75-draw stochastic estimates',
              'constructor': {'underdetermined': True, 'zero_catch': True, 'zero_biomass_accum': False,
                              'default_gs': True, 'normalize_DC': True, 'DC_tol': 0.001},
              'engine_hashes': {n: sha(ENGINE / n) for n in ['ModelData.py', 'PPRCalculator.py', 'utils.py', 'create_PPRS_excel.py']}}
    dump('refresh_configuration.json', config)
    np.random.seed(config['parent_numpy_python_seed'])
    random.seed(config['parent_numpy_python_seed'])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        md = ModelData(str(MODEL))
        raw_dc = md.DC.copy(deep=True)
        calculator, label = cpe.load_model(str(MODEL))
    normalization_warnings = [{'category': w.category.__name__, 'message': str(w.message)} for w in caught]
    dump('constructor_warnings.json', normalization_warnings)
    assert any('does not sum to 1' in w['message'] for w in normalization_warnings)
    assert md.DC.equals(raw_dc), 'Runtime normalization changed the original ModelData'
    print('CONSTRUCTOR_WARNING', normalization_warnings, flush=True)
    old_md = ModelData(str(BASELINE / 'canonical_raw_model.json'))
    delta = float((calculator._DC - old_md.DC).abs().to_numpy().max())
    dump('source_runtime_separation.json', {
        'raw_modeldata_sum': {str(k): float(v) for k, v in md.DC.sum(axis=1).items()},
        'runtime_sum': {str(k): float(v) for k, v in calculator._DC.sum(axis=1).items()},
        'max_abs_runtime_vs_prior_raw_diet_delta': delta,
        'researcher_final_detritus_cells': {str(s):float(md.DC.loc[s,49]) for s in [30,32,33,36,38,39,40,41]},
        'canonical_json_not_normalized_by_constructor': sha(MODEL) == config['canonical_model_sha256'],
        'runtime_normalization_only_on_calculator_copy': True})
    t = time.perf_counter()
    tables = cpe.build_model_tables(calculator, method_keys=methods, mc_samples=mc_count,
                                   model_label=label, source_file=str(MODEL.relative_to(ROOT)), method_timeout=180)
    destination = cpe.write_tables_excel(tables, str(MODEL), str(OUT / 'export'))
    shutil.copy2(destination, MODEL.parent / 'sppr_source.xlsx')
    config.update({'finished_utc': datetime.now(timezone.utc).isoformat(), 'seconds': time.perf_counter() - t,
                   'method_status': tables.method_status, 'issues': tables.issues,
                   'fresh_sppr_sha256': sha(MODEL.parent / 'sppr_source.xlsx')})
    dump('refresh_configuration.json', config)
    print('EXPORTED', json.dumps({'seconds': config['seconds'], 'method_status': tables.method_status,
                                 'issues': len(tables.issues)}, default=str), flush=True)


def direct():
    source = ROOT / 'regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/source_diagnostics/direct_diagnostics.py'
    spec = importlib.util.spec_from_file_location('lme034_direct_audit', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT / 'direct_diagnostics'
    module.OUT.mkdir(exist_ok=True)
    module.OLD = MODEL.parent / 'sppr_source.xlsx'
    for option in ['GE', 'TE', 'With Egestion']:
        module.run_worker(option)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    {'export': export, 'direct': direct}[sys.argv[1]]()
