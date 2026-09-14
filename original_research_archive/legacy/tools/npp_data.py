"""Shared year-specific NPP inputs for workbooks and browser exports.

Canonical annual rows always take precedence, including explicitly missing rows.
The older CSV is a 2019 reference only; it is never repeated across catch years.
Its scaled_* columns hold the regional estimates documented in METHODS section 6.2;
the older npp_*/ens_* columns are common-mask comparisons, not those regional totals.
"""
from __future__ import annotations

import csv
import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNUAL_PATH = os.environ.get('PPR_ANNUAL_NPP_PATH', 'NPPExtraction/output/annual_npp.csv')
LEGACY_PATH = 'NPPExtraction/NPP_2019_filled_SAU_regions.csv'
METHODS = [
    {'id': 'npp_antoinemorel_tC_yr', 'label': 'Antoine–Morel'},
    {'id': 'npp_vgpm_tC_yr', 'label': 'VGPM'},
    {'id': 'npp_eppley_tC_yr', 'label': 'Eppley'},
    {'id': 'npp_cbpm_tC_yr', 'label': 'CbPM'},
    {'id': 'npp_cafe_tC_yr', 'label': 'CAFE'},
    {'id': 'ens_median_tC_yr', 'label': 'Regional ensemble median'},
]
VALUE_KEYS = [m['id'] for m in METHODS] + ['ens_min_tC_yr', 'ens_max_tC_yr', 'water_area_km2']
LEGACY_SCALED_FIELDS = {
    **{m['id']: m['id'].replace('npp_', 'scaled_', 1) for m in METHODS if m['id'].startswith('npp_')},
    **{f'ens_{label}_tC_yr': f'scaled_{label}_tC_yr' for label in ('median', 'min', 'max')},
}


def _number(value, context):
    if value is None or str(value).strip() == '':
        return None
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f'Invalid NPP number in {context}: {value!r}') from error
    if not math.isfinite(result) or result < 0:
        raise ValueError(f'Invalid NPP number in {context}: {value!r}')
    return result


def _record(row, context):
    result = dict(row)
    for key in VALUE_KEYS:
        result[key] = _number(row.get(key), f'{context}/{key}')
    return result


def load_npp(root=ROOT):
    root = Path(root)
    values = {}
    legacy = root / LEGACY_PATH
    if legacy.exists():
        prefix = {'lme': 'LME', 'highseas': 'HS', 'eez': 'EEZ'}
        with legacy.open(encoding='utf-8-sig', newline='') as stream:
            for row in csv.DictReader(stream):
                if row.get('layer') not in prefix:
                    continue
                unit = f"{prefix[row['layer']]}_{int(row['region_id']):03d}"
                if unit in values:
                    raise ValueError(f'Duplicate legacy NPP identity: {unit}')
                # Select already-scaled columns; never apply the baseline ratio again.
                # Column presence identifies the schema, including rows whose scaled
                # values are blank. Falling back per cell would mix two denominators.
                scaled_schema = any(field in row for field in LEGACY_SCALED_FIELDS.values())
                selected = dict(row)
                if scaled_schema:
                    selected.update({target: row.get(source)
                                     for target, source in LEGACY_SCALED_FIELDS.items()})
                record = _record(selected, f'{unit}/2019')
                record.update(year=2019, status='legacy_reference',
                              provenance=LEGACY_PATH,
                              reason='Legacy 2019 reference; not an annual extraction or historical estimate.')
                if scaled_schema:
                    record['method'] = 'Legacy scaled_* regional totals; gap-filled baseline and coverage-matched model ratios (METHODS section 6.2)'
                    record['reason'] = 'Legacy 2019 regional reference from scaled_* columns; missing scaled estimates remain unavailable.'
                values[unit] = {**record, 'annual': {'2019': record}}
    annual = root / ANNUAL_PATH
    if annual.exists():
        seen = set()
        with annual.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            if not {'unit_id', 'year'} <= set(reader.fieldnames or []):
                raise ValueError('Annual NPP requires unit_id and year columns')
            for row in reader:
                unit = row['unit_id']
                if not re.fullmatch(r'(LME|HS|EEZ)_\d{3}', unit):
                    raise ValueError(f'Invalid annual NPP unit: {unit!r}')
                year = int(row['year'])
                if (unit, year) in seen:
                    raise ValueError(f'Duplicate annual NPP identity: {unit}/{year}')
                seen.add((unit, year))
                record = _record(row, f'{unit}/{year}')
                record['year'] = year
                item = values.setdefault(unit, {'annual': {}})
                item['annual'][str(year)] = record
                if year == 2019:
                    item.update(record)
    return values


def npp_for_year(record, year):
    """Return observed/published inputs for that year, never an implicit proxy."""
    if not record:
        return {}
    if 'annual' in record:
        return record['annual'].get(str(int(year)), {})
    # Compatibility for legacy dictionaries passed by existing builder callers.
    return record if int(year) == int(record.get('year', 2019)) else {}


def npp_median_by_year(record, years):
    return {int(year): npp_for_year(record, year).get('ens_median_tC_yr') for year in years}


def annual_arrays(record, years):
    return {method['id']: [npp_for_year(record, year).get(method['id']) for year in years]
            for method in METHODS}


def annual_metadata(record):
    keys = ('status', 'reason', 'provenance', 'n_models', 'ensemble_basis', 'method',
            'source_start_year', 'available_models', 'window_years', 'config_key', 'model_status')
    return {str(year): {key: row[key] for key in keys if row.get(key) not in (None, '')}
            for year, row in (record or {}).get('annual', {}).items()}


def source_paths(root=ROOT):
    return [path for path in (LEGACY_PATH, ANNUAL_PATH) if (Path(root) / path).exists()]
