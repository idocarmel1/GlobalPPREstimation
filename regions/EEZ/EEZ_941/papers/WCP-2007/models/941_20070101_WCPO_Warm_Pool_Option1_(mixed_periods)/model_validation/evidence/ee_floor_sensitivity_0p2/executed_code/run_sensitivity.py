"""Matched EE-floor sensitivity using the exact delivered-report engine bytes."""
from pathlib import Path
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import json
import sys
import tempfile
import warnings

HERE = Path(__file__).resolve()
MODEL = next(p for p in HERE.parents if (p / 'model.json').is_file())
ROOT = next(p for p in HERE.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
from tools.scientific_helpers.sppr import method_coverage as mc
import numpy as np
import pandas as pd

REFERENCE = MODEL / 'model_validation/evidence/ee_floor_on'
OUT = MODEL / 'model_validation/evidence/ee_floor_sensitivity_0p2'
PRIOR = MODEL / 'model_validation/evidence/source_review/evidence/2026-09-28_integration'


def read(path):
    if path.suffix == '.gz':
        with gzip.open(path, 'rt', encoding='utf-8') as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)
    if path.suffix == '.gz':
        with gzip.open(path, 'wt', encoding='utf-8') as handle:
            handle.write(text)
    else:
        path.write_text(text, encoding='utf-8')


def main():
    provenance = read(REFERENCE / 'run_provenance.json')
    assert sha(MODEL / 'model.json') == provenance['canonical_model_sha256']
    assert sha(Path(mc.__file__)) == provenance['engine_identity']['method_coverage.py']
    assert sha(REFERENCE / 'executed_code/PPRCalculator.py') == provenance['engine_identity']['calculation/PPRCalculator.py']
    for row in read(REFERENCE / 'artifact_manifest.json')['files']:
        assert sha(REFERENCE / row['path']) == row['sha256']
    protect = [MODEL / 'model.json', MODEL / 'model_notes.md', MODEL / 'results/result_manifest.json',
        MODEL / 'results/regional_snapshot.xlsx', MODEL / 'model_validation/validation.docx',
        MODEL / 'model_validation/taxon_mapping.xlsx', ROOT / 'regions/EEZ/EEZ_941/EEZ_941.xlsx',
        ROOT / 'Project.xlsx', ROOT / 'interactive_map/index.html', ROOT / 'interactive_map/trends.html']
    protect += [p for p in REFERENCE.rglob('*') if p.is_file()]
    protected = {p.relative_to(ROOT).as_posix(): sha(p) for p in protect}
    code = OUT / 'executed_code'
    code.mkdir(parents=True, exist_ok=True)
    for name in ('PPRCalculator.py', 'method_coverage.py'):
        (code / name).write_bytes((REFERENCE / 'executed_code' / name).read_bytes())
    (code / 'run_sensitivity.py').write_bytes(HERE.read_bytes())
    for name in mc.ENGINE_FILES:
        assert sha(PRIOR / 'engine_snapshot' / name) == provenance['engine_identity'][name]
    data = mc._isolated_module(PRIOR / 'engine_snapshot/ModelData.py', '_eez941_sensitivity_data', {})
    utils = mc._isolated_module(PRIOR / 'engine_snapshot/utils.py', '_eez941_sensitivity_utils', {})
    old = mc._isolated_module(PRIOR / 'engine_snapshot/PPRCalculator.py', '_eez941_sensitivity_base',
        {'ModelData': data, 'utils': utils})
    pinned = mc._isolated_module(code / 'PPRCalculator.py', '_eez941_sensitivity_pinned',
        {'ModelData': data, 'utils': utils})
    settings = read(PRIOR / 'runtime_verification.json')['settings']
    inputs = HERE.parent.parent / 'inputs'
    inputs.mkdir(exist_ok=True)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        with tempfile.TemporaryDirectory(prefix='loader_alias_', dir=inputs) as temporary:
            alias = Path(temporary) / (MODEL.name + '.json')
            alias.write_bytes((MODEL / 'model.json').read_bytes())
            source = data.ModelData(str(alias))
        base = old.PPRCalculator.from_modeldata(source, **settings)
    save(OUT / 'pre_floor_runtime.json.gz', mc._runtime(base))
    groups = mc._group_metadata(base)
    save(OUT / 'group_axes.json', groups)
    group_by_name = {g['name']: g for g in groups}
    comparison = {'model_id': MODEL.name, 'region_id': 'EEZ_941', 'configurations': {},
        'canonical_model_sha256': sha(MODEL / 'model.json'),
        'scope': 'Matched sensitivity, no adoption or reviewer decision',
        'model_flow_units': 'Retained source-model density flow units; no carbon conversion applied here'}
    for label, use_floor, floor, threshold in [('OFF', False, .1, .1), ('0.1', True, .1, .1), ('0.2', True, .2, .2)]:
        model = copy.deepcopy(base)
        model.__class__ = pinned.PPRCalculator
        constructor = {**provenance['resolved_constructor'], 'use_ee_floor': use_floor,
            'ee_floor': floor, 'ee_threshold': threshold}
        model._initialization_settings = constructor
        model.apply_ee_floor(use_floor, floor, threshold)
        initialized = mc._runtime(model)
        if label == '0.1':
            assert initialized == read(REFERENCE / 'runtime_initialized.json.gz'), 'Reference runtime drift'
        dest = OUT / ('floor_' + label.replace('.', 'p').lower())
        save(dest / 'runtime_initialized.json.gz', initialized)
        save(dest / 'ee_floor_ledger.json', mc.encode_lossless(model.ee_floor_ledger))
        model.ee_floor_ledger.to_csv(dest / 'ee_floor_ledger.csv', index_label='group_seq')
        living = model._groups_df.index[model._groups_df.trophic_info.isin(['Regular', 'PP'])]
        for key in ('p', 'q', 'catch', 'predation', 'growth', 'net_migration', 'respiration', 'egestion'):
            np.testing.assert_equal(getattr(model, key).loc[living].values, getattr(base, key).loc[living].values)
        np.testing.assert_equal(model._DC.values, base._DC.values)
        item = {'constructor': constructor, 'floor_info': mc.encode_lossless(model.ee_floor_info),
            'affected_groups': [group_by_name[name] for name in model.ee_floor_ledger.loc[model.ee_floor_ledger.applied, 'group_name']],
            'living_flows_catch_diet_preserved': True, 'methods': {}}
        for option, key in [('GE', 'new_GE'), ('TE', 'new_TE_EEfix')]:
            reference = read(REFERENCE / (key + '_full_return.json.gz'))
            method_settings = reference['settings']
            if label == '0.1':
                result = {k:v for k,v in reference.items() if k != 'settings'}
                origin = 'Reused exact same model/runtime/engine/settings from delivered report'
            else:
                result = mc._run(model, method_settings)
                save(dest / (key + '_full_return.json.gz'), {'settings': method_settings, **result})
                save(dest / (key + '_SPPR_matrix.json'), result.get('source_matrix'))
                origin = 'Fresh direct diagnosis using pinned report engine'
            assert result['status'] == 'ok', result.get('exception')
            item['methods'][option] = {'origin': origin, 'execution_status': result['status'],
                'diagnostics': result['diagnostics'], 'scopes': result['scopes'],
                'annual_status': result['annual_status'], 'negative_entries': result['negative_entries'],
                'matrix_shape': result['source_matrix']['shape']}
            print(label, option, result['status'], result['diagnostics']['status'], flush=True)
        comparison['configurations'][label] = item
    coefficient_rows = []
    for option in ('GE', 'TE'):
        for scope in ('all', 'inner', 'PP'):
            for name, group in group_by_name.items():
                row = {'method': option, 'scope': scope, 'group_id': group['id'], 'group_name': name}
                for label in ('OFF', '0.1', '0.2'):
                    row[label] = comparison['configurations'][label]['methods'][option]['scopes'][scope][name]
                coefficient_rows.append(row)
    save(OUT / 'group_coefficients_comparison.json', coefficient_rows)
    save(OUT / 'comparison.json', comparison)
    after = {path: sha(ROOT / path) for path in protected}
    assert after == protected, 'Protected file changed'
    save(OUT / 'protected_files.json', {'before': protected, 'after': after, 'unchanged': True})
    save(OUT / 'run_provenance.json', {'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'pinned_engine_sha256': sha(code / 'PPRCalculator.py'),
        'current_engine_sha256_at_execution': sha(mc.ENGINE / 'PPRCalculator.py'),
        'pin_reason': 'Isolate floor sensitivity relative to delivered0.1 report; newer concurrent BA/balance changes are excluded',
        'audited_base_engine_identity': provenance['engine_identity'],
        'base_constructor': settings, 'scoped_compatibility': provenance['scoped_compatibility'],
        'reference_runtime_equal': True, 'requested_methods': ['GE', 'TE'],
        'configurations': ['OFF', '0.1', '0.2'], 'floor_semantics': 'ON uses threshold equal to floor',
        'warnings': [f'{w.category.__name__}: {w.message}' for w in caught],
        'canonical_model_sha256': comparison['canonical_model_sha256'], 'script_sha256': sha(HERE)})
    print(json.dumps({label: {option: item['methods'][option]['diagnostics']['footprint']
        for option in ('GE','TE')} for label,item in comparison['configurations'].items()}, indent=2))


if __name__ == '__main__':
    main()
