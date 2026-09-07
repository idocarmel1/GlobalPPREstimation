"""Export verified model-workbook values and render the existing atlas catalog.

The explicit selected-article pilot gate prevents archived candidate articles or
isolated validation models from silently becoming colored estimation coverage.
"""
import hashlib
import html
import json
import sys
from pathlib import Path

import openpyxl

from ppr_scopes import SCOPES, read_health
import build_model_workbook as bmw
import verify_model_workbook as verify

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'PPRAtlas'))
from atlas.render import render_map


def export_network(root=ROOT):
    selection = json.loads((root / 'data/atlas_selection.json').read_text(encoding='utf-8'))
    payload = {'schema_version': 1, 'scopes': SCOPES, 'units': {}}
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
                wb.close()
                record.update(verified=True, workbook=path.relative_to(root).as_posix(),
                              workbook_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            data['models'].append(record)
        data['default_model'] = next((i for i,m in enumerate(data['models']) if m['id'] == choice['default_model']), 0)
        payload['units'][unit] = data
    return payload


def main():
    network = export_network()
    (ROOT / 'PPRAtlas/data/network_ppr.json').write_text(
        json.dumps(network, ensure_ascii=False, separators=(',', ':'), allow_nan=False), encoding='utf-8')
    db = json.loads((ROOT / 'PPRAtlas/data/catalog.json').read_text(encoding='utf-8'))
    for records in [db['regions'], db['articles']]:
        for record in records:
            for key in ['title','authors','region_name','recommendation','coverage_note','quality_rationale','geometry_note','geometry_method','search_notes','loadability_class','download_failure_reason']:
                if isinstance(record.get(key), str):
                    record[key] = html.escape(record[key], quote=True)
            for material in record.get('material_files', []):
                for key in ['filename','file_label']:
                    if isinstance(material.get(key), str):
                        material[key] = html.escape(material[key], quote=True)
    (ROOT / 'PPRAtlas/index.html').write_text(render_map(ROOT / 'PPRAtlas', db), encoding='utf-8')
    print(json.dumps({'selected_pilot_units': len(network['units']), 'verified_models': sum(m['verified'] for u in network['units'].values() for m in u['models'])}))


if __name__ == '__main__':
    main()
