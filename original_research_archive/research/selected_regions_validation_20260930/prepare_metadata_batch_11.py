"""Prepare reviewed Guinea/Benguela source metadata; apply separately with guards."""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import workbooks as W
from apply_reviewed_metadata import geometry_digest


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    current = read(HERE / 'central_source_metadata_current.json')
    assert W.sha(ROOT / 'Project.xlsx') == current['project_sha256']
    plan = {'project_sha256_at_review': current['project_sha256'],
            'scope': 'Reviewed source/version, current availability and approximate study coverage for LME028/029. No scientific or selected-model/rationale changes.',
            'regional_inputs': [], 'patches': [], 'geometry_patches': [], 'proposal_decisions': []}
    for unit, mid, filename in [('LME_028', '28_646_Guinea_(1998)', 'shared_metadata_proposals.json'), ('LME_029', 'BEN2020_Southern_Benguela_1978', 'central_metadata_proposals.json')]:
        ev = ROOT / 'regions' / unit / 'validation_reports' / mid
        handoff = ev / 'coordination_handoff.json'
        assert handoff.exists()
        proposal_path = ev / filename
        data = read(proposal_path)
        plan['regional_inputs'].extend({'path': p.relative_to(ROOT).as_posix(), 'sha256': W.sha(p)} for p in [handoff, proposal_path, ROOT / 'regions' / unit / (unit + '.xlsx')])
        changes = []
        if unit == 'LME_028':
            for group in data['proposals']:
                for field, proposed in group['proposed'].items():
                    changes.append({'table': group['table'], 'key': group['key'], 'field': field,
                                    'expected_old': group['expected_old'][field], 'proposed_new': proposed, 'evidence': group['evidence']})
        else:
            changes = data['updates']
        for c in changes:
            matches = [r for r in current['tables'][c['table']] if all(r.get(k) == v for k, v in c['key'].items())]
            assert len(matches) == 1 and matches[0].get(c['field']) == c['expected_old'], (unit, c['field'], 'stale proposal')
            value = c['proposed_new']
            if unit == 'LME_028' and c['field'] == 'geometry_confidence':
                value = 'low'
                plan['proposal_decisions'].append({'unit_id': unit, 'field': c['field'], 'decision': 'Use categorical low; detailed source-line/coast uncertainty remains in geometry/coverage notes.'})
            if value == c['expected_old']:
                continue
            plan['patches'].append({'sheet': c['table'], 'table': 'Models' if c['table'] == 'Models & coverage' else 'Papers',
                                    'key': c['key'], 'field': c['field'], 'expected_old': c['expected_old'],
                                    'proposed': value, 'evidence': c['evidence']})
        geometry_path = ev / 'geography/study_area_reconstructed.geojson'
        geometry = read(geometry_path)
        if geometry['type'] == 'FeatureCollection':
            assert len(geometry['features']) == 1
            geometry = geometry['features'][0]
        if geometry['type'] == 'Feature':
            geometry = geometry['geometry']
        article = 'GUI-2004__LME_028' if unit == 'LME_028' else 'BEN-2020__LME_029'
        key = 'article:' + article
        retained_map = read(HERE / 'verification' / (unit + '_current_map_metadata.json'))
        rows = [r['row'] for r in retained_map['map_records'] if r['row']['geometry_id'] == key]
        old = json.loads(''.join(r['geojson'] for r in sorted(rows, key=lambda r: r['part']))) if rows else None
        assert (old is None) == (unit == 'LME_028')
        plan['geometry_patches'].append({'unit_id': unit, 'key': key, 'action': 'insert' if old is None else 'replace',
                                        'expected_old_geometry_sha256': geometry_digest(old) if old is not None else None,
                                        'replacement_geojson': geometry_path.relative_to(ROOT).as_posix(),
                                        'replacement_file_sha256': W.sha(geometry_path),
                                        'replacement_geometry_sha256': geometry_digest(geometry),
                                        'geometry_role': 'Approximate source-figure study trace with calibrated vertices, ordered coastline and tested water controls; not author GIS. Target-region geometry and reported source area preserved.',
                                        'evidence': (HERE / 'verification' / (unit + '_geography_coordinator_review.json')).relative_to(ROOT).as_posix()})
    out = HERE / 'verification/metadata_batch_11_plan.json'
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'patches': len(plan['patches']), 'geometry_patches': len(plan['geometry_patches']), 'path': out.relative_to(ROOT).as_posix()}), flush=True)


if __name__ == '__main__':
    main()
