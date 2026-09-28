"""Export verified model-workbook values and render the existing atlas catalog.

The explicit selected-article pilot gate prevents archived candidate articles or
isolated validation models from silently becoming colored estimation coverage.
"""
import hashlib
from atomic_output import write_text_atomic
import html
import json
import sys
from pathlib import Path

import openpyxl

from ppr_scopes import SCOPES, read_health, read_scopes, read_mc_diagnostics, finite
from group_filter_data import build_group_data
import build_model_workbook as bmw
import verify_model_workbook as verify
from unidentified_catch import metadata as unidentified_metadata
from npp_data import load_npp, annual_arrays, annual_metadata, source_paths, METHODS, ANNUAL_PATH
from discard_data import (read_catch_components,catch_basis_metadata,load_response_package,
                          read_final_mappings,model_sensitivity,POLICY,RESPONSE_PATH)
from simple_atlas_data import export_simple_units

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'PPRAtlas'))
from atlas.render import render_map


def export_network(root=ROOT):
    selection = json.loads((root / 'data/atlas_selection.json').read_text(encoding='utf-8'))
    npp = load_npp(root)
    response_package=load_response_package(root)
    payload = {'schema_version': 3, 'scopes': SCOPES, 'units': {},
               'method_labels': {
                   'SPPR_1995_TEmean': 'SPPR_1995_TEmean · consumption weights',
                   'SPPR_1995_TEmean_catch': 'SPPR_1995_TEmean · catch weights (biomass fallback)',
                   'Ulanowicz_globalTEmean': 'Ulanowicz_globalTEmean · consumption weights',
                   'Ulanowicz_globalTEmean_catch': 'Ulanowicz_globalTEmean · catch weights (biomass fallback)'},
               'simple_units': export_simple_units(root),
               'catch_basis_policy':POLICY,'discard_response_source':response_package.get('_source_path',RESPONSE_PATH),
               'discard_study_version':response_package.get('study_version')}
    for unit, choice in selection['units'].items():
        data = {'note': choice['note'], 'selected_articles': choice.get('selected_articles', []),
                'years': [], 'taxa': [], 'catch': [], 'models': []}
        for upstream in bmw.mio.model_workbooks(root, unit):
            record = {'id': upstream.stem, 'label': choice.get('model_labels', {}).get(upstream.stem, upstream.stem.replace('_', ' ')),
                      'verified': False, 'scopes': {}, 'health': read_health(upstream),
                      'source': upstream.relative_to(root).as_posix(),
                      'source_sha256': hashlib.sha256(upstream.read_bytes()).hexdigest()}
            path = root / 'data' / unit / 'models' / upstream.name
            if path.exists():
                problems = verify.check(path, unit)
                if problems:
                    raise ValueError(f'{path}: {problems[:3]}')
                wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
                catch = list(wb['Catch'].values)
                taxa = [r[0] for r in catch[1:]]
                if data['taxa'] and data['taxa'] != taxa:
                    raise ValueError(f'{unit}: catch order differs across models')
                data.update(years=list(catch[0][4:]), taxa=taxa, catch=[list(r[4:]) for r in catch[1:]])
                labels = [{'taxon': r[0], 'common_name': r[1],
                           'by_year': dict(zip(data['years'], r[4:]))} for r in catch[1:]]
                trophic_levels = bmw.mio.read_trophic_levels(root, unit)
                data['unidentified'] = unidentified_metadata(labels, data['years'], trophic_levels)
                data['simple_sppr'] = [10 ** (trophic_levels[t] - 1)
                                       if finite(trophic_levels.get(t)) is not None else None for t in taxa]
                if 'landings' not in data:
                    components=read_catch_components(root,unit,taxa,data['years'])
                    data.update({key:value for key,value in components.items() if key not in ('_labels','years','taxa')})
                data['unidentified']['catch_bases']=catch_basis_metadata(data['unidentified'],taxa,data['years'],data)
                for scope in SCOPES:
                    sn, pn = ('SPPR', 'PPR by method') if scope == 'all' else ('sppr_' + scope, 'PPR ' + scope)
                    rows = list(wb[sn].values)
                    methods = list(rows[3][4:])
                    status = {r[0]: r[1] for r in wb[pn].values if r[0] in methods}
                    by_taxon = {r[0]: list(r[4:]) for r in rows[4:]}
                    # Simple trophic chain is retained only in all scope: it has no
                    # source decomposition and must not masquerade as PP-only SPPR.
                    if scope == 'all':
                        methods.append('simple trophic chain')
                        status['simple trophic chain'] = 'ok'
                        for r in rows[4:]:
                            by_taxon[r[0]].append(r[2])
                    record['scopes'][scope] = {'methods': methods, 'status': status,
                                               'values': [by_taxon[t] for t in taxa]}
                mappings=read_final_mappings(wb,record['id'])
                wb.close()
                record.update(verified=True, workbook=path.relative_to(root).as_posix(),
                              workbook_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                record['group_data'] = build_group_data(bmw.mio.read_groups(upstream),
                    read_scopes(upstream), taxa, mappings,
                    {key: record[key] for key in ('source', 'source_sha256', 'workbook', 'workbook_sha256')})
                record['mc_diagnostics'] = read_mc_diagnostics(upstream)
                record['discard_sensitivity'],record['discard_sensitivity_unavailable']=model_sensitivity(root,data,record,mappings,response_package)
            data['models'].append(record)
        data['default_model'] = next((i for i,m in enumerate(data['models']) if m['id'] == choice['default_model']), 0)
        central = root / 'data' / unit / f'{unit}.xlsx'
        if central.exists():
            data['sources'] = {'workbook': central.relative_to(root).as_posix()}
        payload['units'][unit] = data
    years = sorted({year for item in payload['units'].values() for year in item['years']} |
                   {year for item in payload['simple_units'].values() for year in item['years']} |
                   {int(year) for item in npp.values() for year in item.get('annual', {})})
    payload.update(npp_years=years, npp_methods=METHODS, npp_source=ANNUAL_PATH,
                   npp_sources=[{'path': path, 'sha256': hashlib.sha256((root / path).read_bytes()).hexdigest()}
                                for path in source_paths(root)],
                   npp={unit: annual_arrays(item, years) for unit, item in npp.items()},
                   npp_metadata={unit: annual_metadata(item) for unit, item in npp.items()})
    return payload


def main():
    from refresh_atlas_catalog import refresh_catalog
    db = refresh_catalog(ROOT)
    network = export_network()
    write_text_atomic(ROOT / 'PPRAtlas/data/network_ppr.json',
        json.dumps(network, ensure_ascii=False, separators=(',', ':'), allow_nan=False))
    for records in [db['regions'], db['articles']]:
        for record in records:
            for key in ['title','authors','region_name','recommendation','coverage_note','quality_rationale','geometry_note','geometry_method','search_notes','loadability_class','download_failure_reason']:
                if isinstance(record.get(key), str):
                    record[key] = html.escape(record[key], quote=True)
            for material in record.get('material_files', []):
                for key in ['filename','file_label']:
                    if isinstance(material.get(key), str):
                        material[key] = html.escape(material[key], quote=True)
    write_text_atomic(ROOT / 'PPRAtlas/index.html', render_map(ROOT / 'PPRAtlas', db))
    print(json.dumps({'selected_pilot_units': len(network['units']), 'simple_units': len(network['simple_units']),
                      'verified_models': sum(m['verified'] for u in network['units'].values() for m in u['models'])}))


if __name__ == '__main__':
    main()
