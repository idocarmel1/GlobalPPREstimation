"""Coordinator freshness/candidate checks on released WCPO and 003/034 reviews."""
import json
import math
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import workbooks as W
import regional as R


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def write(p, d):
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main():
    progress_path = HERE / 'verification/review_package_progress.json'
    progress = read(progress_path)
    inputs = read(HERE / 'verification/WCPO_broad_candidate_protected_inputs.json')
    assert all(x['all_checked_protected_inputs_preserved'] for x in inputs)
    links_path = HERE / 'verification/office_links_EEZ_598_EEZ_941_HS_071.json'
    links = read(links_path)
    wanted = {1, 2, 5, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 20, 22, 24, 26}
    units = ['EEZ_598', 'EEZ_941', 'HS_071', 'LME_003', 'LME_034']
    for unit in units:
        row = next(x for x in progress['regions'] if x['unit_id'] == unit)
        if unit.startswith(('EEZ_', 'HS_')):
            release = read(HERE / 'work/qa_residual_fish_scope' / (unit + '_release.json'))
            for key in ['final_workbook', 'final_report', 'final_appendix', 'final_handoff']:
                assert W.sha(ROOT / release[key]['path']) == release[key]['sha256']
            path = ROOT / release['final_workbook']['path']
            book = W.read_book(path)
            overview = W.validate_region(book, path)
            assert R.result_hash(book) == overview['calculation_result_sha256']
            groups = {g['group_name']: g for g in W.records(book, 'Selected model groups', 'Groups')}
            matching = W.records(book, 'PPR', 'Matching')
            checks = []
            for taxon in ['Marine fishes not identified', 'Marine pelagic fishes not identified']:
                rows = [r for r in matching if r['taxon'] == taxon]
                assert {int(groups[r['group']]['seq']) for r in rows} == wanted
                denominator = math.fsum(groups[r['group']]['biomass'] for r in rows)
                assert math.isclose(denominator, 9.00221, rel_tol=1e-14)
                for r in rows:
                    assert math.isclose(r['weight'], groups[r['group']]['biomass'] / denominator, rel_tol=1e-14)
                    assert r['confidence'].lower() == 'very low'
                assert math.isclose(math.fsum(r['weight'] for r in rows), 1, abs_tol=1e-14)
                checks.append({'taxon': taxon, 'candidate_ids': sorted(wanted), 'denominator': denominator, 'rule': 'W9 Medium; M10 Very low', 'weight_reproduction_passed': True})
            ev = (ROOT / release['final_handoff']['path']).parent
            qa = read(ev / 'residual_scope_independent_QA.json')
            assert qa['workbook_sha256'] == release['final_workbook']['sha256']
            assert qa['report_sha256'] == release['final_report']['sha256']
            assert qa['appendix_sha256'] == release['final_appendix']['sha256']
            assert qa['protected_tables_exact'] and qa['manual_researcher_fields_preserved']
            for item in [f for f in links['files'] if f['unit_id'] == unit]:
                assert W.sha(ROOT / item['file']) == item['sha256']
                assert all(x['blue_underlined'] for x in item['links'])
                assert all(x.get('relocated_destination_verified') for x in item['links'] if 'repository_destination' in x)
            proof = {'unit_id': unit, 'released_identities': release, 'candidate_checks': checks,
                     'independent_full_arithmetic_evidence': {'path': (ev / 'residual_scope_independent_QA.json').relative_to(ROOT).as_posix(), 'sha256': W.sha(ev / 'residual_scope_independent_QA.json')},
                     'root_visual_check': 'Current page 4 and long changed appendix row inspected in coordinator turn; all six pages/changed rows/Sources separately inspected by QA agent.',
                     'office_link_evidence': links_path.relative_to(ROOT).as_posix(), 'passed': True,
                     'shared_final_reconciliation_pending': True}
            write(HERE / 'verification' / (unit + '_broad_candidate_release.json'), proof)
            for dest, src in [('workbook', 'final_workbook'), ('report', 'final_report'), ('appendix', 'final_appendix'), ('handoff', 'final_handoff')]:
                row[dest] = release[src]
        else:
            release = read(HERE / 'verification' / (unit + '_broad_candidate_release.json'))
            for path, fingerprint in release['files'].items():
                assert W.sha(ROOT / path) == fingerprint
                dest = 'report' if path.endswith('.docx') else 'appendix' if 'appendix' in path else 'workbook'
                row[dest] = {'path': path, 'sha256': fingerprint}
            assert W.sha(ROOT / release['handoff']['path']) == release['handoff']['sha256']
            row['handoff'] = release['handoff']
        row['phase'] = 'regional review and complete-candidate follow-up complete; shared final reconciliation pending'
        row['followup'] = 'closed with current source/candidate, protected-input, arithmetic and Office relocation proof'
    for unit in ['LME_013', 'LME_036']:
        release = read(HERE / 'work/qa_residual_fish_scope' / (unit + '_release.json'))
        row = next(x for x in progress['regions'] if x['unit_id'] == unit)
        for dest, src in [('workbook', 'final_workbook'), ('report', 'final_report'), ('appendix', 'final_appendix'), ('handoff', 'final_handoff')]:
            assert W.sha(ROOT / release[src]['path']) == release[src]['sha256']
            row[dest] = release[src]
        proof = (ROOT / release['final_handoff']['path']).parent / 'xml_cell_order_followup.json'
        assert proof.exists()
        row['serialization_followup'] = {'path': proof.relative_to(ROOT).as_posix(), 'sha256': W.sha(proof), 'scope': 'Original XML cell values and calculation hashes unchanged; ascending cell order restored.'}
    progress['serialization_integrity_pending'] = []
    progress['serialization_scope'] = 'Five value-preserving XML ordering corrections released; current canonical freshness and input/result hashes verified. No scientific reruns or Office edits.'
    progress['additional_candidate_review_regions'] = [u for u in progress['additional_candidate_review_regions'] if u not in units]
    progress['additional_candidate_review'] = 'All five complete-candidate follow-ups released with current identities; source exceptions and Very low confidence remain explicit.'
    progress['current_packages_fully_released'] = progress['regional_reviews_released'] - len(set(progress['open_followup_regions']) | set(progress['additional_candidate_review_regions']))
    progress['status_note'] = f"{progress['regional_reviews_released']} regional reviews released; complete-candidate follow-ups closed. Shared final/browser/graph/commit/push verification incomplete; active and pending region leads remain."
    write(progress_path, progress)
    print(json.dumps({'accepted': units, 'fully_released_packages': progress['current_packages_fully_released']}), flush=True)


if __name__ == '__main__':
    main()
