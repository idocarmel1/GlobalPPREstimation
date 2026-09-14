"""Compact, model-independent simple PPR for every catch ecosystem identity.

Only annual aggregates are published. Catch boundaries and trophic-chain arithmetic
are shared with the graph, using unrounded source taxon values. Missing catch has
no invented years; missing trophic levels retain the graph's explicit support rules.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_model_workbook as bmw
from build_time_series import simple_basis_values
from discard_data import read_catch_components, catch_basis_metadata, POLICY, finite
from unidentified_catch import metadata as unidentified_metadata


def export_simple_units(root):
    root = Path(root)
    units = {}
    for directory in ('global_output', 'eez_output'):
        identity_path = root / f'SeaAroundUsExtraction/{directory}/tables/units.json'
        for identity in json.loads(identity_path.read_text(encoding='utf-8')):
            unit = identity['unit_id']
            if unit in units:
                raise ValueError(f'Duplicate ecosystem identity: {unit}')
            components = read_catch_components(root, unit)
            years, taxa = components['years'], components['taxa']
            trophic_levels = bmw.mio.read_trophic_levels(root, unit)
            rows = [{**components['_labels'][name],
                     'by_year': {year: value for year, value in zip(years, values) if finite(value)}}
                    for name, values in zip(taxa, components['full_precision_catch'])]
            unidentified = unidentified_metadata(rows, years, trophic_levels)
            unidentified['catch_bases'] = catch_basis_metadata(unidentified, taxa, years, components)
            # Basis metadata is full precision and preserves unknown catch cells.
            unidentified.update(unidentified['catch_bases']['catch'])
            simple = simple_basis_values(components, years, trophic_levels, unidentified)
            for treatment in ('zero', 'simple'):
                simple['unidentified_' + treatment] = simple_basis_values(
                    components, years, trophic_levels, unidentified, treatment)
            paths = {'catch': components['catch_accounting']['source'],
                     'workbook': f'data/{unit}/{unit}.xlsx'}
            for table in ('global_output', 'eez_output'):
                relative = f'SeaAroundUsExtraction/{table}/tables/regions/{unit}/species.csv'
                if (root / relative).exists():
                    paths['trophic_levels'] = relative
                    break
            sources = {key: relative for key, relative in paths.items() if (root / relative).exists()}
            hashes = {key: hashlib.sha256((root / relative).read_bytes()).hexdigest()
                      for key, relative in sources.items()}
            units[unit] = {'name': identity['name'], 'type': identity['region_type'],
                           'years': years, 'simple': simple, 'unidentified': unidentified,
                           'catch_basis_policy': POLICY, 'catch_accounting': components['catch_accounting'],
                           'sources': sources, 'source_sha256': hashes}
    return units
