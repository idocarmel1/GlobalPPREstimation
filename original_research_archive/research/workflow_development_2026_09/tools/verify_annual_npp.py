"""Verify annual NPP agreement across inputs, workbooks and portable atlas exports.

Run after the four integration builders, while extraction is paused between years.
"""
from __future__ import annotations

import hashlib
import argparse
import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path

import openpyxl

from npp_data import load_npp, npp_for_year, annual_arrays, source_paths, METHODS, ANNUAL_PATH

ROOT = Path(__file__).resolve().parents[1]


def same_number(actual, expected, context, tolerance=0):
    if (actual is None) != (expected is None):
        raise ValueError(f'{context}: missingness differs ({actual} vs {expected})')
    if actual is not None:
        expected = float(format(expected, '.16g'))
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=tolerance):
            raise ValueError(f'{context}: {actual} != {expected}')


def verify(root=ROOT, units=None):
    sources = [{'path': p, 'sha256': hashlib.sha256((root / p).read_bytes()).hexdigest()}
               for p in source_paths(root)]
    npp = load_npp(root)
    report = {'status': 'ok', 'sources': sources, 'annual_values_checked': 0,
              'workbook_npp_values_checked': 0, 'summary_ratios_checked': 0,
              'central_workbooks': 0, 'model_workbooks': 0}
    report['workbook_units'] = sorted(units) if units else 'all'
    annual = root / ANNUAL_PATH
    if annual.exists():
        with annual.open(encoding='utf-8-sig', newline='') as stream:
            source_rows = list(csv.DictReader(stream))
        report['canonical_rows'] = len(source_rows)
        report['canonical_statuses'] = dict(Counter(row.get('status', 'unspecified') for row in source_rows))
        for source in source_rows:
            row = npp_for_year(npp[source['unit_id']], int(source['year']))
            values = [row[m['id']] for m in METHODS[:-1] if row[m['id']] is not None]
            if 'n_models' in source and int(source['n_models']) != len(values):
                raise ValueError(f"{source['unit_id']}/{source['year']}: incorrect ensemble count")
            for key, function in [('ens_median_tC_yr', statistics.median), ('ens_min_tC_yr', min),
                                  ('ens_max_tC_yr', max)]:
                if key in source:
                    expected = function(values) if values else None
                    same_number(row[key], expected, f"{source['unit_id']}/{source['year']}/{key}",
                                tolerance=abs(expected or 0) * 1e-14)
    network = json.loads((root / 'PPRAtlas/data/network_ppr.json').read_text(encoding='utf-8'))
    trends = json.loads((root / 'PPRAtlas/data/time_series.json').read_text(encoding='utf-8'))
    if network.get('npp_sources') != sources:
        raise ValueError('Map NPP source hashes differ from current input files')
    if any(source not in trends['sources'] for source in sources):
        raise ValueError('Graph NPP source hashes differ from current input files')
    if set(network['npp']) != set(npp):
        raise ValueError('Map NPP ecosystem identities differ from source inputs')
    for name, years, export_units in [('map', network['npp_years'], network['npp']),
                               ('graph', trends['years'], {u: r['npp'] for u, r in trends['units'].items()})]:
        for unit, actual in export_units.items():
            expected = annual_arrays(npp.get(unit), years)
            if actual != expected:
                raise ValueError(f'{name}/{unit}: annual NPP arrays differ from inputs')
            report['annual_values_checked'] += len(years) * len(METHODS)
    for unit, item in trends['units'].items():
        if units and unit not in units:
            continue
        paths = [(item.get('sources', {}).get('workbook'), 'central_workbooks')]
        paths += [(m.get('workbook'), 'model_workbooks') for m in item['models']]
        for relative, kind in paths:
            if not relative:
                continue
            with_workbook = openpyxl.load_workbook(root / relative, read_only=True, data_only=True)
            try:
                rows = list(with_workbook['NPP'].values)
                header = next(r for r in rows if r[0] == 'year')
                sheet_years = set()
                for row in rows:
                    if not isinstance(row[0], int):
                        continue
                    if row[0] in sheet_years:
                        raise ValueError(f'{relative}: duplicate NPP year {row[0]}')
                    sheet_years.add(row[0])
                    expected = npp_for_year(npp.get(unit), row[0])
                    for method in METHODS:
                        key = method['id']
                        same_number(row[header.index(key)], expected.get(key), f'{relative}/{row[0]}/{key}')
                        report['workbook_npp_values_checked'] += 1
                summary = list(with_workbook['Summary'].values)
                required = {row[0] for row in summary if isinstance(row[0], int)}
                required |= {int(year) for year in (npp.get(unit) or {}).get('annual', {})}
                if sheet_years != required:
                    raise ValueError(f'{relative}: NPP sheet year coverage differs from inputs')
                for row in summary:
                    if not isinstance(row[0], int):
                        continue
                    denominator = npp_for_year(npp.get(unit), row[0]).get('ens_median_tC_yr')
                    pairs = [(2, 3)] if kind == 'central_workbooks' else [(2, 4), (3, 5)]
                    for numerator, ratio in pairs:
                        expected = (round(100 * row[numerator] / 9 / denominator, 4)
                                    if denominator and row[numerator] is not None else None)
                        same_number(row[ratio], expected, f'{relative}/{row[0]}/ratio', tolerance=.00010001)
                        report['summary_ratios_checked'] += 1
                if 'Final mappings' not in with_workbook.sheetnames:
                    raise ValueError(f'{relative}: Final mappings sheet missing')
                report[kind] += 1
            finally:
                with_workbook.close()
    # Detect an extraction update during verification instead of certifying mixed inputs.
    for source in sources:
        if hashlib.sha256((root / source['path']).read_bytes()).hexdigest() != source['sha256']:
            raise ValueError('NPP changed during verification; rerun between extraction jobs')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--units', nargs='+', help='Limit workbook checks; atlas arrays and source hashes are always checked in full')
    report = verify(units=parser.parse_args().units)
    (ROOT / 'data/annual_npp_validation.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
