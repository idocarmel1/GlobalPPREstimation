"""Export annual atlas inputs without changing estimation code or source workbooks.

Run with ``python -X utf8 tools/build_time_series.py``. Every build verifies source
hashes, recomputes simple PPR from catch/taxon TL, and checks all persisted annual
totals. The output retains missing identities and failed methods explicitly.
"""
from __future__ import annotations

import argparse
from atomic_output import write_text_atomic
import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

import openpyxl

from build_ecosystem_data import load_catch, load_trophic_levels
from unidentified_catch import metadata as unidentified_metadata, coefficients as treatment_coefficients, VERSION, RULE
from npp_data import (load_npp, annual_arrays, annual_metadata, source_paths,
                      METHODS, ANNUAL_PATH)
from discard_data import (read_catch_components,annual_values,annual_totals,
                          catch_basis_metadata,BASES,POLICY)

ROOT = Path(__file__).resolve().parents[1]
SIMPLE = 'simple trophic chain'
NPP_METHODS = [dict(method) for method in METHODS]
for _method in NPP_METHODS:
    _method['note'] = ('Annual regional ensemble median; aggregation sums regional medians.'
                       if _method['id'] == 'ens_median_tC_yr'
                       else 'Year-specific NPP, tonnes carbon per year.')


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def verified_hash(root, relative_path, expected=None):
    path = root / relative_path
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected is not None and digest != expected:
        raise ValueError(f'SHA-256 mismatch: {relative_path}')
    return {'path': relative_path, 'sha256': digest}


def annual_method(years, source_years, catch, coefficients, status):
    """Sum taxon products, retaining numeric zero and excluding unavailable pairs."""
    result = {'status': status, 'ppr': [None] * len(years),
              'covered_catch': [None] * len(years)}
    if status != 'ok':
        return result
    if len(catch) != len(coefficients) or any(len(row) != len(source_years) for row in catch):
        raise ValueError('Catch/coefficient array dimensions do not agree')
    if len(source_years) != len(set(source_years)):
        raise ValueError('Duplicate source year')
    indexes = {year: index for index, year in enumerate(source_years)}
    for output_index, year in enumerate(years):
        if year not in indexes:
            continue
        index = indexes[year]
        pairs = [(row[index], coefficient) for row, coefficient in zip(catch, coefficients)
                 if finite(coefficient) and finite(row[index])]
        if pairs:
            # Model workbooks accumulate in taxon order with +=. Python's newer
            # compensated sum() can cross the final three-decimal rounding boundary.
            total = 0.0
            for c, v in pairs:
                total += c * v
            # openpyxl persists numeric cells with %.16g; keep the published decimal.
            result['ppr'][output_index] = float(format(round(total, 3), '.16g'))
            result['covered_catch'][output_index] = round(sum(c for c, _ in pairs), 3)
    return result


def simple_annual(rows, years, trophic_levels):
    coefficients = [(10 ** (trophic_levels[row['taxon']] - 1))
                    if finite(trophic_levels.get(row['taxon'])) else None for row in rows]
    catch = [[row['by_year'].get(year, 0.0) for year in years] for row in rows]
    matched = [(row, coefficient) for row, coefficient in zip(catch, coefficients) if coefficient is not None]
    # The base Summary uses sum() on unrounded catch/taxon coefficients, unlike
    # the model workbook's ordered accumulation of rounded model inputs.
    return {'ppr': [round(sum(row[index] * v for row, v in matched), 3) if matched else None
                    for index in range(len(years))],
            'catch': [round(sum(row[index] for row in catch), 3) if catch else None
                      for index in range(len(years))],
            'covered_catch': [round(sum(row[index] for row, _ in matched), 3) if matched else None
                              for index in range(len(years))]}


def export_models(network_unit, years):
    models = []
    for source_model in network_unit.get('models', []):
        model = {key: source_model.get(key) for key in
                 ('id', 'label', 'verified', 'source', 'workbook', 'source_sha256', 'workbook_sha256')}
        model['scopes'] = {}
        if source_model.get('verified'):
            for scope, source_scope in source_model['scopes'].items():
                methods = {}
                for index, method in enumerate(source_scope['methods']):
                    if method == SIMPLE:
                        continue
                    coefficients = [row[index] for row in source_scope['values']]
                    status=source_scope['status'].get(method, 'unavailable: no verified method status')
                    methods[method] = model_basis_values(network_unit,years,coefficients,status)
                    attach_sensitivity(methods[method],source_model,scope,method,'method',network_unit.get('years',[]),years)
                    for treatment in ('zero', 'simple'):
                        status = source_scope['status'].get(method, 'unavailable: no verified method status')
                        if status == 'ok' and treatment == 'simple' and scope != 'all':
                            status = 'unavailable: reference trophic-chain SPPR has no source decomposition'
                        if status == 'ok' and 'unidentified' not in network_unit:
                            status = 'unavailable: unidentified-catch classification metadata is missing; rebuild the network export'
                        revised = treatment_coefficients(network_unit['taxa'], coefficients,
                            network_unit.get('unidentified', {}).get('taxa', []), treatment)
                        revised_record=model_basis_values(network_unit,years,revised,status)
                        attach_sensitivity(revised_record,source_model,scope,method,treatment,network_unit.get('years',[]),years)
                        methods[method]['unidentified_' + treatment] = revised_record
                model['scopes'][scope] = {'methods': methods}
        models.append(model)
    default_index = network_unit.get('default_model')
    default = (models[default_index]['id'] if isinstance(default_index, int)
               and 0 <= default_index < len(models) else None)
    return models, default


def model_basis_values(unit,years,coefficients,status):
    """New exports use classified landings; old fixtures retain their audit API."""
    if unit.get('catch_basis_policy')!=POLICY:
        return annual_method(years,unit['years'],unit['catch'],coefficients,status)
    result={}
    for basis,field in BASES.items():
        matrix=unit.get(field,[[None]*len(unit['years']) for _ in coefficients])
        item=annual_values(years,unit['years'],matrix,coefficients,status)
        totals=annual_totals(matrix,unit['years'])
        lookup=dict(zip(unit['years'],totals))
        item['catch']=[lookup.get(y) for y in years]
        result[basis]=item
    return {**result['landings'],'catch_basis':'landings',
            'catch_bases':{basis:result[basis] for basis in ('catch','discards')}}


def attach_sensitivity(record,model,scope,method,treatment,source_years,years):
    annual=model.get('discard_sensitivity',{}).get(scope,{}).get(method,{}).get(treatment)
    if annual is not None:
        lookup=dict(zip(source_years,annual))
        record['sensitivity']=[lookup.get(year) for year in years]
    else:
        record['sensitivity_unavailable']=model.get('discard_sensitivity_unavailable',{}).get(scope,{}).get(method,
            'No compatible tested discard-routing response is available.')


def simple_basis_values(components,years,trophic_levels,metadata,treatment='method'):
    taxa=components['taxa']
    original=[10**(trophic_levels[t]-1) if finite(trophic_levels.get(t)) else None for t in taxa]
    coeff=(original if treatment=='method' else treatment_coefficients(taxa,original,metadata.get('taxa',[]),treatment))
    unit={**components,'catch_basis_policy':POLICY}
    result=model_basis_values(unit,years,coeff,'ok')
    result['sensitivity_unavailable']='External fixed taxon-TL benchmark; discard-routing ecological uncertainty is not assessed.'
    return result


def simple_zero_annual(rows, years, trophic_levels, metadata):
    affected = {r['name'] for r in metadata['taxa']}
    normal = [r for r in rows if r['taxon'] not in affected]
    zero = simple_annual(normal, years, trophic_levels)
    for i, year in enumerate(years):
        if affected:
            zero['ppr'][i] = zero['ppr'][i] if zero['ppr'][i] is not None else 0
            zero['covered_catch'][i] = round(sum(row['by_year'].get(year, 0) for row in rows
                if row['taxon'] in affected or finite(trophic_levels.get(row['taxon']))), 3)
    zero['catch'] = [round(sum(row['by_year'].get(y, 0) for row in rows), 3) if rows else None for y in years]
    return zero


def load_identities(root):
    identities = {}
    memberships = {}
    for set_id, directory in [('global', 'global_output'), ('eez', 'eez_output')]:
        records = json.loads((root / f'SeaAroundUsExtraction/{directory}/tables/units.json').read_text(encoding='utf-8'))
        memberships[set_id] = [record['unit_id'] for record in records]
        for record in records:
            unit = record['unit_id']
            if unit in identities:
                raise ValueError(f'Duplicate ecosystem identity: {unit}')
            identities[unit] = {'name': record['name'], 'type': record['region_type']}
    selection = json.loads((root / 'data/atlas_selection.json').read_text(encoding='utf-8'))['units']
    with (root / 'PPRAtlas/data/regions.csv').open(encoding='utf-8-sig', newline='') as stream:
        memberships['atlas'] = [record['unit_id'] for record in csv.DictReader(stream)]
    memberships.update(pilot=list(selection),
                       lme=[unit for unit in identities if unit.startswith('LME_')],
                       high_seas=[unit for unit in identities if unit.startswith('HS_')],
                       all=sorted(identities))
    labels = {'global': 'Global LME + High Seas', 'pilot': 'Selected pilot',
              'lme': 'Large Marine Ecosystems', 'high_seas': 'High Seas',
              'eez': 'Exclusive Economic Zones', 'atlas': 'Atlas catalog', 'all': 'All ecosystems'}
    sets = []
    for set_id in ('global', 'pilot', 'lme', 'high_seas', 'eez', 'atlas', 'all'):
        members = memberships[set_id]
        if len(members) != len(set(members)) or set(members) - identities.keys():
            raise ValueError(f'Invalid ecosystem membership in {set_id}')
        note = 'Selected-region sum; regions may overlap and do not establish unique global coverage.'
        if set_id == 'global':
            note += ' Includes all 84 input identities, including two without catch.'
        if set_id == 'pilot':
            note += ' Selection alone does not make a model or method available.'
        sets.append({'id': set_id, 'label': labels[set_id], 'units': members, 'note': note})
    for unit, record in identities.items():
        record['pilot'] = unit in selection
        record['note'] = selection.get(unit, {}).get('note', '')
    return dict(sorted(identities.items())), sets


def read_base_summary(path):
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        records = list(workbook['Summary'].values)
        header = next(row for row in records if row[0] == 'year')
        return {int(row[0]): {'catch': row[header.index('catch_tonnes')],
                              'ppr': row[header.index('ppr_tonnes')]}
                for row in records if isinstance(row[0], int)}
    finally:
        workbook.close()


def assert_annual_equal(actual, expected, description):
    if (actual is None) != (expected is None):
        raise ValueError(f'{description}: missingness differs ({actual} vs {expected})')
    # Compare exactly after the source writer's numeric serialization, without a
    # relative tolerance that could hide a changed coefficient in a large total.
    if actual is not None and float(format(actual, '.16g')) != expected:
        raise ValueError(f'{description}: annual total differs ({actual} vs {expected})')


def audit_models(root, network, years, audit):
    """Independently compare every method/year with the stored annual workbook rows."""
    for unit, source_unit in network['units'].items():
        for model in source_unit['models']:
            for key in ('source', 'workbook'):
                if model.get(key):
                    audit['sources'].append(verified_hash(root, model[key], model[key + '_sha256']))
                    audit['model_hashes_verified'] += 1
            if not model['verified']:
                continue
            workbook = openpyxl.load_workbook(root / model['workbook'], read_only=True, data_only=True)
            try:
                for scope, data in model['scopes'].items():
                    sheet = 'PPR by method' if scope == 'all' else 'PPR ' + scope
                    records = list(workbook[sheet].values)
                    header = next(row for row in records if row[0] == 'method')
                    rows = {row[0]: row for row in records if row[0] in data['methods']}
                    for index, method in enumerate(data['methods']):
                        if method == SIMPLE:
                            continue
                        row = rows[method]
                        if row[1] != data['status'][method]:
                            raise ValueError(f'{model["id"]}/{scope}/{method}: status differs')
                        if data['status'][method] != 'ok':
                            # These are deliberately not estimates. Retain their
                            # verified status, never compare or publish their curve.
                            audit['flagged_annual_values_excluded'] += len(source_unit['years'])
                            continue
                        computed = annual_method(years, source_unit['years'], source_unit['catch'],
                                                 [values[index] for values in data['values']], 'ok')
                        for year in source_unit['years']:
                            actual = computed['ppr'][years.index(year)]
                            expected = row[header.index(year)]
                            assert_annual_equal(actual, expected, f'{model["id"]}/{scope}/{method}/{year}')
                            audit['model_annual_values_checked'] += 1
            finally:
                workbook.close()


def graph_years(catch_years, npp):
    """NPP-only dates must not disappear because there was no catch that year."""
    return sorted(set(catch_years) | {int(year) for record in npp.values()
                                    for year in record.get('annual', {})})


def build():
    units, sets = load_identities(ROOT)
    npp = load_npp(ROOT)
    network = json.loads((ROOT / 'PPRAtlas/data/network_ppr.json').read_text(encoding='utf-8'))
    if network.get('catch_basis_policy')!=POLICY:
        raise ValueError('Rebuild the network export with full-precision landings/catch/discards before building time series.')
    audit = {'status': 'ok', 'sources': [], 'simple_annual_values_checked': 0,
             'model_annual_values_checked': 0, 'model_hashes_verified': 0,
             'flagged_annual_values_excluded': 0, 'missing_catch': [], 'samples': {}}
    for path in ('SeaAroundUsExtraction/global_output/tables/units.json',
                 'SeaAroundUsExtraction/eez_output/tables/units.json',
                 'data/atlas_selection.json', 'PPRAtlas/data/regions.csv',
                 'PPRAtlas/data/network_ppr.json', *source_paths(ROOT)):
        audit['sources'].append(verified_hash(ROOT, path))
    all_years = set()
    for count, (unit, record) in enumerate(units.items(), 1):
        rows, years = load_catch(unit)
        trophic_levels = load_trophic_levels(unit)
        record['_years'] = years
        record['_components']=read_catch_components(ROOT,unit,[r['taxon'] for r in rows],years)
        record['_trophic_levels']=trophic_levels
        record['catch_basis_policy']=POLICY
        all_years.update(years)
        record['simple'] = simple_annual(rows, years, trophic_levels)
        record['unidentified'] = unidentified_metadata(rows, years, trophic_levels)
        record['unidentified']['catch_bases']=catch_basis_metadata(record['unidentified'],
            [r['taxon'] for r in rows],years,record['_components'])
        # The zero sensitivity retains catch tonnage and treats its coefficient as
        # known zero, including explicitly unidentified labels with no reference TL.
        record['_simple_zero'] = simple_zero_annual(rows, years, trophic_levels, record['unidentified'])
        record['sources'] = {}
        if not rows:
            audit['missing_catch'].append(unit)
            record['note'] = (record['note'] + ' No catch series is available; annual estimates are unavailable.').strip()
        else:
            paths = {'catch': f'SeaAroundUsExtraction/data/catch_by_taxon_year/{unit}.csv.gz',
                     'workbook': f'data/{unit}/{unit}.xlsx'}
            for directory in ('global_output', 'eez_output'):
                relative = f'SeaAroundUsExtraction/{directory}/tables/regions/{unit}/species.csv'
                if (ROOT / relative).exists():
                    paths['trophic_levels'] = relative
                    break
            for key, path in paths.items():
                record['sources'][key] = path
                audit['sources'].append(verified_hash(ROOT, path))
            summary = read_base_summary(ROOT / paths['workbook'])
            if set(summary) != set(years):
                raise ValueError(f'{unit}: base workbook catch years differ')
            for index, year in enumerate(years):
                for key in ('catch', 'ppr'):
                    assert_annual_equal(record['simple'][key][index], summary[year][key], f'{unit}/{key}/{year}')
                    # Deliver the exact persisted decimal, after independent recomputation.
                    record['simple'][key][index] = summary[year][key]
                    audit['simple_annual_values_checked'] += 1
        if count % 75 == 0:
            print(f'Checked annual source totals for {count}/{len(units)} ecosystems', flush=True)
    years = graph_years(all_years, npp)
    for unit, record in units.items():
        record['npp'] = annual_arrays(npp.get(unit), years)
        record['npp_metadata'] = annual_metadata(npp.get(unit))
        if not any(finite(value) for values in record['npp'].values() for value in values):
            record['note'] = (record['note'] + ' No annual NPP estimate is available.').strip()
        source_years = record.pop('_years')
        lookup = {year: index for index, year in enumerate(source_years)}
        # Source workbook total-catch checks above remain independent. Published
        # series now use full-precision classified taxon vectors for each basis.
        components=record.pop('_components');tl=record.pop('_trophic_levels')
        record.pop('_simple_zero')
        record['simple']=simple_basis_values(components,years,tl,record['unidentified'])
        for treatment in ('simple','zero'):
            record['simple']['unidentified_'+treatment]=simple_basis_values(components,years,tl,record['unidentified'],treatment)
        record['catch_accounting']=components['catch_accounting']
        for basis,data in record['unidentified']['catch_bases'].items():
            record['unidentified']['catch_bases'][basis]={key:[values[lookup[y]] if y in lookup else None for y in years] for key,values in data.items()}
        record['catch_accounting']['classification_status']=[components['catch_accounting']['classification_status'][lookup[y]] if y in lookup else 'missing_catch' for y in years]
        for key in ('catch', 'missing_simple_catch'):
            values = record['unidentified'][key]
            record['unidentified'][key] = [values[lookup[y]] if y in lookup else None for y in years]
        record['models'], record['default_model'] = export_models(network['units'].get(unit, {}), years)
    audit_models(ROOT, network, years, audit)
    methods = [{'id': SIMPLE, 'label': 'Trophic chain · catch-taxon TL (TE 0.1)',
                'kind': 'taxon', 'scopes': ['all']}]
    scopes = {}
    for record in units.values():
        for model in record['models']:
            for scope, data in model['scopes'].items():
                for method in data['methods']:
                    if scope not in scopes.setdefault(method, []):
                        scopes[method].append(scope)
    methods.extend({'id': method,
                    'label': ('SPPR_1995_TE0.1 · model TL (TE 0.1)' if method == 'SPPR_1995_TE0.1' else method),
                    'kind': 'model', 'scopes': supported}
                   for method, supported in scopes.items())
    counts = {'units': len(units), 'years': len(years),
              'with_catch': sum(any(finite(v) for v in u['simple']['catch']) for u in units.values()),
              'with_simple_ppr': sum(any(finite(v) for v in u['simple']['ppr']) for u in units.values()),
              'with_npp': sum(any(finite(v) for values in u['npp'].values() for v in values) for u in units.values()),
              'models': sum(len(u['models']) for u in units.values()),
              'verified_models': sum(m['verified'] for u in units.values() for m in u['models'])}
    audit['counts'] = counts
    audit['model_statuses'] = dict(Counter(data['status'] for u in units.values() for m in u['models']
                                         for scope in m['scopes'].values() for data in scope['methods'].values()))
    for unit in ('LME_013', 'LME_035', 'LME_047', 'EEZ_711', 'HS_018'):
        record = units[unit]
        audit['samples'][unit] = {str(year): {key: values[years.index(year)]
                                             for key, values in record['simple'].items() if isinstance(values, list)}
                                  for year in (1950, 1980, 2019)}
    from global_npp_reference import build_global_npp_reference
    global_npp = build_global_npp_reference(ROOT, years)
    payload = {'schema_version': 4, 'years': years, 'npp_year': None, 'npp_source': ANNUAL_PATH,
               'global_npp': global_npp,
               'catch_basis_policy':POLICY,
               'npp_policy': 'Year-specific NPP; unavailable years remain blank. An explicit display option may use the earliest available year for earlier years only, labeled as a proxy.',
               'units_note': 'PPR is tonnes wet-weight-equivalent primary production; NPP is tonnes carbon. Convert PPR to carbon at 9:1 for ratios.',
               'model_note': 'Each model uses its fixed published coefficients across catch years. Distinct models are alternatives and are never averaged.',
               'scopes': network['scopes'], 'npp_methods': NPP_METHODS, 'ppr_methods': methods,
               'sets': sets, 'units': units, 'coverage': counts,
               'sources': audit['sources'][:5 + len(source_paths(ROOT))],
               'validation': {'report': '../../data/time_series_validation.json',
                              'simple_annual_values_checked': audit['simple_annual_values_checked'],
                              'model_annual_values_checked': audit['model_annual_values_checked'],
                              'model_hashes_verified': audit['model_hashes_verified']}}
    return payload, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify sources and compare with the existing export without writing files')
    args = parser.parse_args()
    payload, audit = build()
    text = json.dumps(payload, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    destination = ROOT / 'PPRAtlas/data/time_series.json'
    if args.check:
        if not destination.exists() or destination.read_text(encoding='utf-8') != text:
            raise ValueError('The annual export is missing or differs from its verified sources')
    else:
        write_text_atomic(destination, text)
        write_text_atomic(ROOT / 'data/time_series_validation.json',
            json.dumps(audit, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        inventory = {'classifier_version': VERSION, 'rule_description': RULE,
                     'units': {unit: record['unidentified']['taxa'] for unit, record in payload['units'].items()}}
        write_text_atomic(ROOT / 'data/unidentified_taxa.json',
            json.dumps(inventory, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        sys.path.insert(0, str(ROOT / 'PPRAtlas'))
        from atlas.render import render_time_series
        write_text_atomic(ROOT / 'PPRAtlas/trends.html', render_time_series(ROOT / 'PPRAtlas'))
    print(json.dumps({'status': 'ok', **audit['counts'],
                      'simple_annual_values_checked': audit['simple_annual_values_checked'],
                      'model_annual_values_checked': audit['model_annual_values_checked'],
                      'model_hashes_verified': audit['model_hashes_verified'],
                      'flagged_annual_values_excluded': audit['flagged_annual_values_excluded'],
                      'missing_catch': audit['missing_catch']}))


if __name__ == '__main__':
    main()
