"""Summarize retained comparison returns without executing a scientific method."""
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
WORK = Path(__file__).resolve().parents[1]
METHODS = ['new_GE', 'new_TE_EEfix', 'SPPR_1995_TE0.1']


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def finite(value):
    return isinstance(value, (int, float)) and math.isfinite(value)


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


inventory = read(WORK/'inputs/validated_inventory.json')
summary = {'method_scope': METHODS, 'comparison_scope_note': 'Three methods tested on identical completed state; no claim about other deterministic formulations or current loader reconstruction',
           'material_difference_rule': 'More than 10% annual PPR on common catch support, a zero-to-nonzero or sign change, or numerical availability/support change', 'models': []}
for item in inventory['pairs']:
    directory = ROOT/item['model_dir']/'results/diagnostics/engine_comparison_20261114'
    path = directory/'comparison.json'
    if not path.exists():
        summary['models'].append(read(directory/'error.json') if (directory/'error.json').exists() else {'unit_id': item['unit_id'], 'model_id': item['model_id'], 'error': 'Comparison absent'})
        continue
    report = read(path)
    if set(report['methods']) != set(METHODS):
        summary['models'].append({'unit_id': item['unit_id'], 'model_id': item['model_id'], 'error': 'Comparison incomplete'})
        continue
    if hashlib.sha256((ROOT/item['model_dir']/'model.json').read_bytes()).hexdigest() != report['model_sha256']:
        raise ValueError('Canonical model changed during comparison: '+item['unit_id'])
    for method, outcome in report['methods'].items():
        old = read(directory/(method+'_old.json.gz'))
        current = read(directory/(method+'_current.json.gz'))
        for scope, data in outcome['scopes'].items():
            before, after = old.get('scopes', {}).get(scope, {}), current.get('scopes', {}).get(scope, {})
            paired = [(group, a, after.get(group)) for group, a in before.items() if finite(a) and finite(after.get(group))]
            absolute = [(abs(b-a), group) for group, a, b in paired]
            relative = [(abs(b-a)/abs(a) if a else 0., group) for group, a, b in paired if a or b == 0]
            max_abs = max(absolute, default=(None, None))
            max_rel = max(relative, default=(None, None))
            data['max_absolute_coefficient_change'], data['max_absolute_coefficient_change_group'] = max_abs
            data['max_relative_coefficient_change'], data['max_relative_coefficient_change_group'] = max_rel
            data['zero_to_nonzero_coefficient_groups'] = [group for group, a, b in paired if a == 0 and b != 0]
            for row in data['annual']:
                row['zero_to_nonzero'] = bool(row['common_old_ppr_wet_tonnes'] == 0 and finite(row['common_current_ppr_wet_tonnes']) and row['common_current_ppr_wet_tonnes'] != 0)
            data['years_over_10_percent'] = [row['year'] for row in data['annual'] if row['zero_to_nonzero'] or (finite(row['relative_absolute_change_common']) and row['relative_absolute_change_common'] > .1)]
            data['year_2019'] = data['annual'][-1]
        outcome['materially_different'] = outcome['old_execution_status'] != outcome['current_execution_status'] or any(
            value['years_over_10_percent'] or value['years_with_sign_change'] or value['years_with_availability_change'] for value in outcome['scopes'].values())
    report['materially_different'] = any(value['materially_different'] for value in report['methods'].values())
    report['canonical_model_unchanged_after_comparison'] = True
    save(path, report)
    summary['current_engine_hashes'] = report['current_engine_hashes']
    summary['models'].append({'unit_id': item['unit_id'], 'model_id': item['model_id'], 'materially_different': report['materially_different'],
                             'report_path': path.relative_to(ROOT).as_posix(),
                             'methods': {key: {'materially_different': value['materially_different'],
                                               'old_status': value['old_execution_status'], 'current_status': value['current_execution_status'],
                                               'old_matches_saved_coefficients': value['old_matches_saved_coefficients'],
                                               'all_sources_2019': value['scopes']['all']['year_2019'],
                                               'max_relative_annual_all_sources': value['scopes']['all']['max_relative_annual_change_common'],
                                               'max_relative_coefficient_all_sources': value['scopes']['all']['max_relative_coefficient_change'],
                                               'max_absolute_coefficient_all_sources': value['scopes']['all']['max_absolute_coefficient_change']}
                                         for key, value in report['methods'].items()}})
summary['completed_pairs'] = sum('error' not in row for row in summary['models'])
summary['expected_pairs'] = len(inventory['pairs'])
summary['materially_different_pairs'] = [row['unit_id'] for row in summary['models'] if row.get('materially_different')]
save(WORK/'outputs/engine_comparison_summary.json', summary)
print(json.dumps({'completed': summary['completed_pairs'], 'expected': summary['expected_pairs'], 'materially_different_pairs': summary['materially_different_pairs'],
                  'errors': [{'unit_id': row['unit_id'], 'error': row['error']} for row in summary['models'] if row.get('error')]}))
