"""Compare three scalar SPPR_1995 choices on the exact seven reviewed pairs.

Writes only this researcher-owned study. Audited model initialization is retained;
the new calculation code is explicitly identified as a study-only upgrade.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import inspect
import json
import math
import re
import sys
import warnings
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

STUDY = Path(__file__).resolve().parents[1]
OUT = STUDY / 'results/validated7'
INPUTS = STUDY / 'inputs/validated7'
EVIDENCE = STUDY / 'evidence/validated7'
ROOT = next(p for p in STUDY.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
COHORT_STUDY = ROOT / 'research/human/sppr_trophic_level_20261018_validated7'
sys.path.insert(0, str(COHORT_STUDY / 'code'))
from cohort import assert_cohort_current, validate_pairs
from tools.project_core.calculations.coverage import _metadata, validated_identities
from tools.project_core.registry.discovery import discover_models, discover_regions
from tools.project_core.validation.researcher_review import approved_review, table_rows
from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
from tools.scientific_helpers.sppr.method_coverage import (
    ENGINE, _engine_paths, _isolated_module, encode_lossless, _runtime,
)

LABELS = {
    'HS_077': 'Eastern tropical Pacific', 'LME_013': 'Northern Humboldt',
    'LME_032': 'Arabian Sea', 'LME_034': 'Bay of Bengal',
    'LME_035': 'Gulf of Thailand', 'LME_036': 'South China Sea',
    'LME_047': 'East China Sea',
}
VARIANTS = ('fixed_0.1', 'consumer_mean_Q', 'aggregated_II_IV')
SOURCES = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def consume(path):
    path = Path(path).resolve()
    key = path.relative_to(ROOT).as_posix()
    digest = sha(path)
    if key in SOURCES and SOURCES[key] != digest:
        raise ValueError('Input changed while reading: ' + key)
    SOURCES[key] = digest
    return path


def read_json(path):
    return json.loads(consume(path).read_text(encoding='utf-8-sig'))


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                               allow_nan=False) + '\n', encoding='utf-8')


def number(value):
    if value in (None, ''):
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def plain(value):
    """JSON-safe numeric evidence, preserving nonfinite values explicitly."""
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if isinstance(value, np.generic):
        return plain(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return {'nonfinite': str(value)}
    return value


def saved_book(path):
    book = {}
    with zipfile.ZipFile(consume(path)) as archive:
        for sheet, table in [('Overview', 'Settings'),
                             ('Selected model groups', 'Groups'),
                             ('Catch', 'Catch'), ('PPR', 'Matching')]:
            _, headers, _, values = table_rows(archive, sheet, table)
            headers = list(values[0][1]) if values else (headers or [])
            book.setdefault(sheet, {})[table] = (
                headers, [[r.get(h) for h in headers] for _, r in values])
    return book


def rows(book, sheet, table):
    headers, values = book[sheet][table]
    return [dict(zip(headers, row)) for row in values]


def settings(book):
    return {r['field']: r['value'] for r in rows(book, 'Overview', 'Settings')}


def audited_load(model_path, flags):
    """Use exact archived loading and explicitly rebind only the study calculator.

    The publication adapter intentionally rejects unregistered scientific changes.
    This study calls its source/hash validation and isolated-module primitives,
    without changing that gate or claiming the new method is an old audited run.
    """
    paths = _engine_paths(flags, model_path)
    for path in paths.values():
        consume(path)
    prefix = '_aggregated_study_' + sha(model_path)[:16]
    data_module = _isolated_module(paths['ModelData.py'], prefix + '_data', {})
    utils_module = _isolated_module(paths['utils.py'], prefix + '_utils', {})
    loader_module = _isolated_module(paths['PPRCalculator.py'], prefix + '_loader',
                                    {'ModelData': data_module, 'utils': utils_module})
    calculation_path = consume(ENGINE / 'PPRCalculator.py')
    current = _isolated_module(calculation_path, prefix + '_current',
                               {'ModelData': data_module, 'utils': utils_module})
    loader = loader_module.PPRCalculator
    defaults = {key: p.default for key, p in inspect.signature(loader.from_modeldata).parameters.items()
                if key not in ('cls', 'self') and p.default is not inspect.Parameter.empty}
    recorded = copy.deepcopy(flags['constructor'])
    floor = {key: recorded.pop(key) for key in ('use_ee_floor', 'ee_floor')}
    unknown = set(recorded) - set(defaults)
    if unknown:
        raise ValueError(f'Unknown recorded loader options: {sorted(unknown)}')
    options = {**defaults, **recorded}
    if 'use_ee_floor' in options:
        options.update(use_ee_floor=False, ee_floor=floor['ee_floor'])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        source = data_module.ModelData(str(model_path))
        model = loader.from_modeldata(source, **options)
        model.__class__ = current.PPRCalculator
        model._initialization_settings = {**copy.deepcopy(options), **floor}
        model.apply_ee_floor(floor['use_ee_floor'], floor['ee_floor'])
    return model, {
        'audited_base_loader_options': options,
        'runtime_floor_options': floor,
        'audited_source_hashes': {name: sha(path) for name, path in paths.items()},
        'study_calculator_path': calculation_path.relative_to(ROOT).as_posix(),
        'study_calculator_sha256': sha(calculation_path),
        'loading_warnings': [f'{w.category.__name__}: {w.message}' for w in caught],
        'role': 'Audited initialization plus explicitly identified study-only current calculator',
    }


def regional_allocations(book, model_id, group_names, excluded):
    catch_rows = [r for r in rows(book, 'Catch', 'Catch') if r['catch_basis'] == 'catch']
    catch = {}
    missing = []
    for row in catch_rows:
        if row['taxon'] in catch:
            raise ValueError('Duplicate catch taxon: ' + row['taxon'])
        catch[row['taxon']] = number(row.get('2019'))
        if catch[row['taxon']] is None:
            missing.append(row['taxon'])
    mapping = {}
    keys = set()
    for row in rows(book, 'PPR', 'Matching'):
        if row['model_id'] != model_id:
            continue
        key = (row['taxon'], row['group'])
        if key in keys:
            raise ValueError(f'Duplicate mapping: {key}')
        keys.add(key)
        weight = number(row['weight'])
        if row['group'] in (None, '') or weight is None:
            continue
        if row['group'] not in group_names or weight < 0:
            raise ValueError(f'Invalid mapping: {key}')
        mapping.setdefault(row['taxon'], []).append((row['group'], weight))
    totals = dict.fromkeys(group_names, 0.)
    allocations = []
    unmapped = []
    for taxon, amount in catch.items():
        if amount is None or amount == 0:
            continue
        if amount < 0:
            raise ValueError('Negative annual catch: ' + taxon)
        pairs = mapping.get(taxon, [])
        if not pairs:
            unmapped.append({'taxon': taxon, 'catch_tonnes': amount})
        if pairs and not math.isclose(sum(w for _, w in pairs), 1., abs_tol=1e-9):
            raise ValueError('Unnormalized original mapping: ' + taxon)
        for group, weight in pairs:
            part = amount * weight
            included = group not in excluded
            allocations.append({'taxon': taxon, 'group': group, 'original_weight': weight,
                                'catch_tonnes': part, 'review_included': included})
            if included:
                totals[group] += part
    return totals, allocations, {'missing_catch_taxa': missing, 'unmapped_positive_catch': unmapped,
                                'all_catch_tonnes': sum(v for v in catch.values() if v is not None)}


def weighted(coefficients, weights):
    missing = [name for name, weight in weights.items() if weight > 0 and coefficients.get(name) is None]
    total_weight = sum(weights.values())
    if missing or total_weight <= 0:
        return {'catch': total_weight, 'ppr': None, 'mean_sppr': None,
                'missing_positive_catch_groups': missing}
    result = sum(weight * coefficients[name] for name, weight in weights.items() if weight > 0)
    return {'catch': total_weight, 'ppr': result, 'mean_sppr': result / total_weight,
            'missing_positive_catch_groups': []}


def write_csv(path, values):
    if not values:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(values[0]))
        writer.writeheader()
        writer.writerows(values)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare-only', action='store_true', help='Validate inputs without model construction or outputs')
    args = parser.parse_args()
    consume(Path(__file__))
    consume(COHORT_STUDY / 'code/cohort.py')
    cohort_path = consume(COHORT_STUDY / 'inputs/cohort.json')
    cohort = assert_cohort_current(ROOT, cohort_path)
    consume(ROOT / 'Project.xlsx')
    metadata = _metadata(ROOT)
    identities = validate_pairs(validated_identities(metadata))
    regions = discover_regions(ROOT)
    html = consume(ROOT / 'interactive_map/trends.html').read_text(encoding='utf-8')
    db = json.loads(re.search(r'const SERIES_DB=(.*?);</script>', html, re.S).group(1))
    old_aggregation_path = ROOT / 'regions/LME/LME_028/work/2026-10-18_121535_trophic_aggregation_validated7/outputs/decomposition.json'
    prior = read_json(old_aggregation_path)
    prior_groups = {(g['unit_id'], g['group']): g['catch_tonnes'] for g in prior['groups']}
    contexts = []
    for unit_id, model_id in identities:
        metadata_row = next(r for r in metadata if (r['unit_id'], r['model_id']) == (unit_id, model_id))
        model_path = consume(discover_models(regions[unit_id].parent)[model_id])
        manifest = read_json(model_path.parent / 'results/result_manifest.json')
        book = saved_book(regions[unit_id])
        if settings(book).get('results_model_id') != model_id:
            raise ValueError('Regional results identify another model')
        review = approved_review(ROOT, metadata_row, book)
        consume(ROOT / metadata_row['validation_report_path'])
        if review['status'] != 'Validated by researcher' or sha(model_path) != review['model_sha256']:
            raise ValueError('Review is not current for canonical model')
        flags = resolve_audited_configuration(model_path.parent, book, manifest)
        for evidence in flags.get('configuration_evidence', []):
            consume(model_path.parent / evidence['relative_path'])
        payload = next(m for m in db['units'][unit_id]['models'] if m['id'] == model_id)
        if payload['workbook_sha256'] != sha(regions[unit_id]):
            raise ValueError('Published workbook identity differs')
        for source in payload.get('model_catch_unit_basis', {}).get('sources', []):
            if sha(consume(ROOT / source['path'])) != source['sha256']:
                raise ValueError('Model catch unit evidence changed')
        contexts.append((unit_id, model_id, model_path, manifest, book, review, flags, payload))
    if args.prepare_only:
        print(json.dumps({'pairs': identities, 'validated_input_files': len(SOURCES),
                          'prepared_without_model_construction': True}))
        return
    summaries, groups, levels, model_evidence, allocations = [], [], [], {}, []
    for unit_id, model_id, model_path, manifest, book, review, flags, payload in contexts:
        print(f'Calculating {unit_id}: {model_id}', flush=True)
        model, load_evidence = audited_load(model_path, flags)
        state_before = json.dumps(_runtime(model), sort_keys=True, allow_nan=False)
        frame = model.get_groups_df()
        names = {seq: str(model.seq2name[seq]) for seq in frame.index}
        if len(set(names.values())) != len(names):
            raise ValueError('Duplicate runtime names')
        excluded = set(review['excluded_group_ids'])
        catches, parts, allocation_checks = regional_allocations(book, model_id, set(names.values()), excluded)
        for part in parts:
            allocations.append({'unit_id': unit_id, 'model_id': model_id, **part})
        for name, amount in catches.items():
            if not math.isclose(amount, prior_groups.get((unit_id, name), 0.), rel_tol=1e-12, abs_tol=1e-8):
                raise ValueError(f'2019 support differs from retained seven-model comparison: {unit_id}/{name}')
        native_catch = {name: number(model.catch.loc[seq]) for seq, name in names.items()}
        if any(v is None or v < 0 for v in native_catch.values()):
            raise ValueError('Native catch has missing or negative weights')
        native_weights = {name: (0. if name in excluded else amount) for name, amount in native_catch.items()}
        scalar_mean = float(model.get_TE('global', global_TE='mean', weights='consumption', as_matrix=False)
                            .loc[frame.index[frame['trophic_info'] == 'Regular'][0]])
        level_frame = model.get_aggregated_TE(levels=(2, 3, 4))
        level_values = [number(level_frame.loc[level, 'TE']) for level in (2, 3, 4)]
        if any(v is None or v <= 0 for v in level_values):
            aggregate_te = None
        else:
            aggregate_te = float(np.exp(np.mean(np.log(level_values))))
        for level, values in level_frame.iterrows():
            levels.append({'unit_id': unit_id, 'trophic_level': int(level), **{str(k): plain(v) for k, v in values.items()}})
        coefficients = {}
        errors = {}
        calls = {
            'fixed_0.1': {'global_TE': .1, 'weights': 'consumption'},
            'consumer_mean_Q': {'global_TE': 'mean', 'weights': 'consumption'},
            'aggregated_II_IV': {'TE_option': 'aggregated', 'weights': 'consumption'},
        }
        for variant, kwargs in calls.items():
            try:
                result = model.SPPR_1995(**kwargs)['sppr']
                coefficients[variant] = {name: number(result.loc[seq]) for seq, name in names.items()}
            except Exception as error:
                errors[variant] = {'type': type(error).__name__, 'message': str(error)}
                coefficients[variant] = {name: None for name in names.values()}
        fixed_saved = manifest['method_coverage']['methods']['SPPR_1995_TE0.1']['scopes']['all']
        max_fixed_error = 0.
        for name, value in coefficients['fixed_0.1'].items():
            expected = number(fixed_saved.get(name))
            if expected is None or value is None or not math.isclose(value, expected, rel_tol=1e-10, abs_tol=1e-10):
                raise ValueError(f'Fixed-TE baseline no longer reproduces saved coefficients: {unit_id}/{name}')
            max_fixed_error = max(max_fixed_error, abs(value - expected) / max(abs(expected), 1.))
        tl = model.get_TL(break_cycles=True, DET_as_PP=True)
        restrictions = {key: {
            'status': result.get('status'), 'reason': result.get('reason'),
            'annual_status': result.get('annual_status'),
            'diagnostics': result.get('diagnostics'),
            'retained_diagnostics_flat': result.get('retained_diagnostics_flat'),
        } for key, result in manifest.get('method_coverage', {}).get('methods', {}).items()
          if key in ('SPPR_1995_TE0.1', 'SPPR_1995_TEmean', 'new_GE', 'new_TE_EEfix')}
        regional_status = manifest['method_coverage']['methods']['SPPR_1995_TE0.1'].get('annual_status', {}).get('all')
        for variant in VARIANTS:
            native = weighted(coefficients[variant], native_weights)
            regional = weighted(coefficients[variant], catches)
            scalar = {'fixed_0.1': .1, 'consumer_mean_Q': scalar_mean, 'aggregated_II_IV': aggregate_te}[variant]
            summaries.append({'unit_id': unit_id, 'model_id': model_id, 'label': LABELS[unit_id],
                'variant': variant, 'TE': scalar,
                'native_included_catch': native['catch'], 'native_catch_weighted_sppr': native['mean_sppr'],
                'native_catch_times_sppr': native['ppr'],
                'native_catch_units': payload.get('model_catch_units') or 'undocumented model-native flow units',
                'regional_2019_included_catch_tonnes': regional['catch'],
                'regional_2019_catch_weighted_sppr': regional['mean_sppr'],
                'regional_2019_ppr_tonnes_wet_equivalent': regional['ppr'],
                'regional_2019_ppr_tC': regional['ppr'] / 9 if regional['ppr'] is not None else None,
                'retained_annual_restriction': regional_status,
                'study_status': ('unavailable: ' + errors[variant]['message']) if variant in errors else 'exploratory study result'})
        for seq, name in names.items():
            groups.append({'unit_id': unit_id, 'model_id': model_id, 'group_seq': int(seq), 'group': name,
                'group_type': str(frame.loc[seq, 'trophic_info']), 'TL_cycle_broken_detritus_basal': number(tl.loc[seq]),
                'review_included': name not in excluded, 'native_catch': native_catch[name],
                'regional_2019_included_catch_tonnes': catches[name],
                'biomass_accumulation': number(model.growth.loc[seq]),
                'net_migration': number(model.net_migration.loc[seq]),
                'external_mortality_export': number(model.external_mortality_export.loc[seq]),
                **{variant + '_sppr': coefficients[variant][name] for variant in VARIANTS},
                'retained_annual_restriction': regional_status})
        if state_before != json.dumps(_runtime(model), sort_keys=True, allow_nan=False):
            raise ValueError('Comparison mutated runtime model state')
        model_evidence[unit_id] = {
            'model_id': model_id, 'recorded_flags': flags, 'execution': load_evidence,
            'review': review, 'retained_method_restrictions': restrictions,
            'model_catch_unit_basis': payload.get('model_catch_unit_basis'),
            'calls': calls, 'errors': errors, 'allocation_checks': allocation_checks,
            'fixed_baseline_max_relative_error': max_fixed_error,
            'level_table': encode_lossless(level_frame), 'level_metadata': plain(level_frame.attrs),
            'runtime_unchanged': True,
            'nonzero_biomass_accumulation_groups': {names[k]: float(v) for k, v in model.growth.items() if v != 0},
            'nonzero_net_migration_groups': {names[k]: float(v) for k, v in model.net_migration.items() if v != 0},
            'nonzero_external_mortality_export_groups': {names[k]: float(v) for k, v in model.external_mortality_export.items() if v != 0},
        }
    for row in summaries:
        baseline = next(r for r in summaries if r['unit_id'] == row['unit_id'] and r['variant'] == 'fixed_0.1')
        for field, output in [('native_catch_times_sppr', 'native_ppr_ratio_to_fixed_0.1'),
                              ('regional_2019_ppr_tC', 'regional_ppr_ratio_to_fixed_0.1')]:
            row[output] = row[field] / baseline[field] if row[field] is not None and baseline[field] else None
    total = {}
    for variant in VARIANTS:
        selected = [row for row in summaries if row['variant'] == variant]
        complete = all(row['regional_2019_ppr_tC'] is not None for row in selected)
        total[variant] = {'n_models': len(selected), 'complete': complete,
                          'included_catch_tonnes': sum(row['regional_2019_included_catch_tonnes'] for row in selected),
                          'regional_2019_ppr_tC': sum(row['regional_2019_ppr_tC'] for row in selected) if complete else None}
    baseline = total['fixed_0.1']['regional_2019_ppr_tC']
    for data in total.values():
        data['ratio_to_fixed_0.1'] = data['regional_2019_ppr_tC'] / baseline if data['complete'] and baseline else None
    for path, digest in SOURCES.items():
        if sha(ROOT / path) != digest:
            raise ValueError('Input changed before saving: ' + path)
    result = {
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Three scalar TE choices, same cycle-broken detritus-basal SPPR_1995 TL, reviewed identical catch shares',
        'pairs': identities, 'cohort': cohort,
        'regional_definition': {'year': 2019, 'catch_basis': 'catch (landings plus discards)',
            'unidentified': 'method', 'group_selection': 'signed-review default exclusions',
            'allocation': 'original weights, omitted shares not reassigned',
            'carbon_conversion': 'regional wet-weight PPR divided by 9',
            'support_matches_retained_seven_model_study': True},
        'TE_definition': {'fixed_0.1': '0.1', 'consumer_mean_Q': 'arithmetic mean of all consumer TE weighted by Q',
            'aggregated_II_IV': 'geometric mean of aggregated level II, III, IV flow efficiencies; published export-inclusive definition'},
        'summary': summaries, 'regional_total': total, 'model_evidence': model_evidence,
        'all_consumed_inputs_unchanged': True,
    }
    save_json(INPUTS / 'source_hashes.json', SOURCES)
    save_json(INPUTS / 'cohort.json', {**cohort, 'scientific_scope': result['scope']})
    save_json(OUT / 'comparison.json', plain(result))
    save_json(OUT / 'group_records.json', groups)
    save_json(OUT / 'level_records.json', levels)
    save_json(EVIDENCE / 'allocations_2019.json', allocations)
    write_csv(OUT / 'summary.csv', summaries)
    write_csv(OUT / 'group_records.csv', groups)
    write_csv(OUT / 'level_records.csv', levels)
    print(json.dumps({'regional_total': total, 'source_files': len(SOURCES),
                      'group_rows': len(groups), 'level_rows': len(levels)}, indent=2))


if __name__ == '__main__':
    main()
