"""Compare preserved actual failures with repaired execution evidence, no solves."""
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
WORK = Path(__file__).resolve().parents[1]


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')


inventory = read(WORK/'inputs/validated_inventory.json')
summary = {'comparison_type': 'Observed historical exception versus repaired archived-engine execution, using preserved runtime and method settings',
           'interpretation': 'Availability changes are separate from large numeric shifts: failed old executions have no finite result to compare. Finite outputs keep all annual diagnostic restrictions. Runtime/environment and engine identities are recorded explicitly.',
           'models': []}
for unit in ['LME_035', 'LME_013']:
    item = next(row for row in inventory['pairs'] if row['unit_id'] == unit)
    model = ROOT/item['model_dir']
    output = model/'results/diagnostics/engine_comparison_20261114/symbolic_availability'
    keys = [key for key in inventory['canonical_non_mc_methods'] if key.startswith('sym_')] if unit == 'LME_035' else ['sym_GE_asDC', 'sym_TE_asDC', 'sym_WithEgestion_asDC']
    weights = read(output.parent/'group_catch_weights.json')
    report = {'unit_id': unit, 'model_id': item['model_id'], 'methods': {}}
    for key in keys:
        old_path = output/'original'/(key+'.json.gz')
        old = read(old_path)
        calculation = model/'results/diagnostics/method_coverage/deterministic_completion_20261114/calculated'
        candidates = [calculation/'symbolic_v2'/(key+'.json.gz'), calculation/'symbolic'/(key+'.json.gz')]
        current_path = next((path for path in candidates if path.exists()), None)
        if current_path is None:
            report['methods'][key] = {'old_status': old['status'], 'new_status': 'not available'}
            continue
        current = read(current_path)
        saved = output/'repaired'/(key+'.json.gz')
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(current_path.read_bytes())
        same_runtime = old.get('runtime_before') is not None and old.get('runtime_before') == current.get('runtime_before')
        same_settings = old['settings']['target'] == current['settings']['target'] and old['settings']['kwargs'] == current['settings']['kwargs']
        entry = {'old_status': old['status'], 'new_status': current['status'],
                 'old_reason': old.get('reason'), 'new_reason': current.get('reason'),
                 'new_annual_status': current.get('annual_status'),
                 'negative_entries': current.get('negative_entries'),
                 'old_evidence': old_path.relative_to(ROOT).as_posix(), 'old_sha256': sha(old_path),
                 'repaired_execution_source': current_path.relative_to(ROOT).as_posix(),
                 'repaired_evidence': saved.relative_to(ROOT).as_posix(), 'repaired_sha256': sha(saved),
                 'old_identity': old.get('identity'), 'repaired_identity': current.get('identity'),
                 'exact_encoded_runtime_before_equal': same_runtime,
                 'exact_method_target_and_kwargs_equal': same_settings,
                 'same_canonical_model': old.get('identity', {}).get('model_sha256') == current.get('identity', {}).get('model_sha256'),
                 'numerical_output_became_available': old['status'] != 'ok' and current['status'] == 'ok',
                 'numerical_percentage_difference': None,
                 'numerical_percentage_unavailable_reason': 'The original execution failed and supplied no finite coefficient comparison',
                 'current_annual_by_basis': {}}
        for basis, value in weights['bases'].items():
            scopes = {}
            for scope, coefficients in current.get('scopes', {}).items():
                totals = [0.]*70; supports = [0.]*70
                for group, catches in value['weights'].items():
                    coefficient = coefficients.get(group)
                    if not isinstance(coefficient, (int, float)) or not math.isfinite(coefficient): continue
                    for index, catch in enumerate(catches):
                        totals[index] += coefficient*catch
                        supports[index] += catch
                scopes[scope] = {'annual_ppr_wet_tonnes': [total if support > 0 else None for total, support in zip(totals, supports)],
                                 'annual_covered_catch_tonnes': supports,
                                 'diagnostic_status': current.get('annual_status', {}).get(scope)}
            entry['current_annual_by_basis'][basis] = scopes
        report['methods'][key] = entry
    report['availability_repaired_methods'] = [key for key, row in report['methods'].items() if row.get('numerical_output_became_available')]
    save(output/'comparison.json', report)
    summary['models'].append(report)
save(WORK/'outputs/engine_comparison_symbolic_availability.json', summary)
print(json.dumps([{'unit_id': row['unit_id'], 'availability_repaired_methods': row['availability_repaired_methods']} for row in summary['models']]))
