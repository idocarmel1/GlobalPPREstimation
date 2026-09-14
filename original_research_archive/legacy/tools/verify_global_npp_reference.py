"""Audit compact global NPP reference outputs without repeating raster extraction."""
from __future__ import annotations

import argparse
import calendar
import csv
import json
import math
import statistics
from pathlib import Path

from global_npp_reference import ROOT, OUTPUT, build_global_npp_reference, sha256, write_json


def close(actual, expected, context):
    if not math.isclose(float(actual), float(expected), rel_tol=2e-12, abs_tol=1e-6):
        raise ValueError(f'{context}: {actual} != {expected}')


def rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def verify(root=ROOT, require_all=True):
    root = Path(root)
    payload = build_global_npp_reference(root)
    directory = root / OUTPUT
    if len(payload['unit_ids']) != 84 or not {'LME_064', 'HS_018'} <= set(payload['unit_ids']):
        raise ValueError('Fixed reference must include all84 LME/high-seas identities, including no-catch identities')
    completed = []
    ledgers = []
    for year in range(1998, 2020):
        record_path = directory / 'years' / str(year) / 'record.json'
        if not record_path.exists():
            continue
        record = json.loads(record_path.read_text(encoding='utf-8'))
        provenance_path = root / record['provenance']
        provenance = json.loads(provenance_path.read_text(encoding='utf-8'))
        for artifact in provenance['outputs']:
            if sha256(root / artifact['path']) != artifact['sha256']:
                raise ValueError(f'Published ledger checksum mismatch: {artifact["path"]}')
        source = provenance['source_configuration']
        if sha256(root / source['path']) != source['sha256']:
            raise ValueError(f'Canonical source provenance checksum mismatch: {year}')
        helper_hash = provenance['code_sha256']['tools/global_npp_reference.py']
        helper_snapshot = directory / 'execution_sources' / f'global_npp_reference_{helper_hash}.py'
        if not helper_snapshot.exists() or sha256(helper_snapshot) != helper_hash:
            raise ValueError(f'Exact executed helper snapshot missing: {year}')
        for path, expected in provenance['code_sha256'].items():
            if path.startswith('NPPExtraction/npp/') and sha256(root / path) != expected:
                raise ValueError(f'NPP scientific implementation changed: {path}')
        output = directory / 'years' / str(year)
        base = rows(output / f'npp_{year}_baseline_by_region.csv')
        ens = rows(output / f'npp_{year}_ensemble_by_region.csv')
        monthly = rows(output / f'npp_{year}_baseline_monthly.csv')
        if len(base) != 1 or len(ens) != 1 or len(monthly) != 12:
            raise ValueError(f'Incomplete union CSV ledger: {year}')
        base, ens = base[0], ens[0]
        expected_models = ['antoinemorel'] if year < 2003 else ['antoinemorel', 'vgpm', 'eppley', 'cbpm', 'cafe']
        if record['expected_models'] != expected_models:
            raise ValueError(f'Unexpected annual model pool: {year}')
        for model in expected_models:
            total = record['model_totals_tC_yr'][model]
            close(total, ens[f'scaled_{model}_tC_yr'], f'{year}/{model}/scaled ledger')
            pool = 'common' if record['ensemble_basis'] == 'common mask' else 'own'
            expected = float(base['npp_central_tC_yr']) * float(ens[f'{pool}_{model}_tC_yr']) / float(ens[f'{pool}_antoinemorel_tC_yr'])
            close(total, expected, f'{year}/{model}/baseline and model ratio')
        median = statistics.median(record['model_totals_tC_yr'][model] for model in expected_models)
        close(median, record['ensemble_median_tC_yr'], f'{year}/median')
        index = payload['years'].index(year)
        close(median, payload['values'][index], f'{year}/graph value')
        coverage = record['coverage']
        water, polygon = float(base['water_area_km2']), float(base['polygon_area_km2'])
        close(coverage['water_area_pct_of_polygon'], 100 * water / polygon, f'{year}/water support')
        days = [calendar.monthrange(year, int(row['month']))[1] for row in monthly]
        central_categories = ['obs', 'dark', 'clim', 'nn_near']
        if coverage['baseline_far_fill_in_central']:
            central_categories.append('nn_far')
        central = sum(day * sum(float(row[f'area_{cat}_pct']) for cat in central_categories)
                      for day, row in zip(days, monthly)) / sum(days)
        close(coverage['central_support_pct_of_water_pixel_days'], central, f'{year}/central water support')
        close(coverage['central_support_pct_of_polygon_pixel_days'], central * water / polygon, f'{year}/central polygon support')
        meta = payload['metadata'][str(year)]
        if not meta['calculation_complete'] or not meta['coverage_limited'] or meta['coverage_complete']:
            raise ValueError(f'Calculation completion confused with spatial coverage: {year}')
        completed.append(year)
        ledgers.append({'year': year, 'denominator_tC_yr': median, 'model_count': len(expected_models),
                        'water_area_pct_of_polygon': coverage['water_area_pct_of_polygon'],
                        'central_support_pct_of_polygon_pixel_days': coverage['central_support_pct_of_polygon_pixel_days'],
                        'record_sha256': sha256(record_path), 'provenance_sha256': sha256(provenance_path)})
    for index, year in enumerate(payload['years']):
        if year not in completed and payload['values'][index] is not None:
            raise ValueError(f'Uncomputed reference year has a numeric denominator: {year}')
    missing = sorted(set(range(1998, 2020)) - set(completed))
    if require_all and missing:
        raise ValueError(f'Global atlas reference extraction remains incomplete: {missing}')
    result = {'status': 'passed' if not missing else 'partial_passed',
              'reference_id': payload['id'], 'reference_regions': len(payload['unit_ids']),
              'geometry_sha256': payload['reference_geography']['sha256'],
              'completed_years': completed, 'missing_years': missing,
              'ensemble_convention': payload['ensemble_details'],
              'checks': ['published ledger hashes', 'canonical source hashes', 'exact helper snapshots',
                         'unchanged scientific NPP code', 'baseline and model-ratio identity',
                         'median of union model totals', 'annual graph values', 'coverage arithmetic',
                         'coverage-limited labels', 'missing-year blanks'], 'annual': ledgers}
    write_json(directory / 'verification.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-partial', action='store_true')
    args = parser.parse_args()
    result = verify(require_all=not args.allow_partial)
    print(json.dumps({'status': result['status'], 'completed_years': result['completed_years'],
                      'missing_years': result['missing_years']}, indent=2))
