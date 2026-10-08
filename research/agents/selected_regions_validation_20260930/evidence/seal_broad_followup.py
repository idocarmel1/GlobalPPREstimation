"""Seal reviewed 003/034 follow-ups; change provenance, never scientific inputs."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import workbooks as W
import regional as R


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def seal(unit):
    folder = ROOT / 'regions' / unit
    workbook = folder / (unit + '.xlsx')
    fingerprint = W.sha(workbook)
    book = W.read_book(workbook)
    settings = W.overview(book)
    assert settings['calculation_input_sha256'] == W.input_hash(book)
    assert settings['calculation_result_sha256'] == R.result_hash(book)
    ev = folder / 'validation_reports' / settings['selected_model_id']
    handoff_path = ev / 'coordination_handoff.json'
    handoff = read(handoff_path)
    receipt = read(ev / 'broad_candidate_followup.json')
    proof = read(ev / 'broad_candidate_calculations_verification.json')
    assert proof['passed'] and proof['workbook_sha256'] == fingerprint
    assert read(ev / 'broad_candidate_method_exposure.json')['workbook_sha256'] == fingerprint
    office = [x for x in read(HERE / 'verification/office_links_LME_003_LME_034.json')['files'] if x['unit_id'] == unit]
    assert len(office) == 2
    for item in office:
        assert W.sha(ROOT / item['file']) == item['sha256'], item['file']
        assert all(x['blue_underlined'] for x in item['links'])
        assert all(x.get('relocated_destination_verified') for x in item['links'] if 'repository_destination' in x)
    final_files = {str(workbook.relative_to(ROOT)).replace('\\', '/'): fingerprint}
    final_files.update({x['file']: x['sha256'] for x in office})
    report = next(ROOT / x['file'] for x in office if x['file'].endswith('.docx'))
    appendix = next(ROOT / x['file'] for x in office if x['file'].endswith('.xlsx'))
    receipt['status'] = 'Regional follow-up complete: independent arithmetic, preserved inputs, six-page visual review and portable Office links pass; shared browser reconciliation pending.'
    receipt['after_workbook_sha256'] = fingerprint
    receipt['source_proposal'] = next(x for x in read(HERE / 'work/qa_residual_fish_scope/broad_scope_candidate_proposals.json') if x['unit_id'] == unit)
    receipt['current_input_sha256'] = settings['calculation_input_sha256']
    receipt['current_result_sha256'] = settings['calculation_result_sha256']
    receipt['office_refresh']['after_hashes'] = {report.name: W.sha(report), appendix.name: W.sha(appendix)}
    receipt['current_verification'] = {
        'arithmetic': 'broad_candidate_calculations_verification.json',
        'method_exposure': 'broad_candidate_method_exposure.json',
        'word_pages': 6,
        'visual_review': 'Coordinator inspected all six final Word pages and all changed appendix rows, sources and relevant allocation-table ranges; passed.',
        'retained_images': {p.relative_to(ev).as_posix(): W.sha(p) for p in sorted((ev / 'qa/broad_candidates').glob('*.png'))},
        'office_links': {'path': str((HERE / 'verification/office_links_LME_003_LME_034.json').relative_to(ROOT)).replace('\\', '/'), 'sha256': W.sha(HERE / 'verification/office_links_LME_003_LME_034.json')},
        'shared_final_reconciliation_pending': True,
    }
    write(ev / 'broad_candidate_followup.json', receipt)
    historical = ['calculations_verification.json', 'mapping_changes.json'] if unit == 'LME_003' else ['reuse_arithmetic_and_office_checks.json', 'mixed_guild_reuse_addendum.json', 'reuse_layout_verification.json', 'reuse_current_hyperlink_verification.json']
    for name in historical:
        path = ev / name
        previous = read(path)
        if not isinstance(previous, dict):
            continue  # Keep historical list schema; current index/handoff qualify it.
        previous['scope_of_stored_numbers'] = 'Historical evidence preceding the complete broad-candidate follow-up. Original recorded values/hashes are retained; use broad_candidate_followup.json and broad_candidate_calculations_verification.json for the current mapping/results and Office QA.'
        previous['superseded_by'] = 'broad_candidate_followup.json'
        write(path, previous)
    index = ev / 'reports_index.md'
    banner = ('# Current complete-candidate follow-up\n\n'
              'Current mappings, arithmetic and Office evidence are recorded in the [follow-up](broad_candidate_followup.json), '
              '[independent calculations](broad_candidate_calculations_verification.json), '
              '[method-specific exposure](broad_candidate_method_exposure.json) and [handoff](coordination_handoff.json). '
              'Accepted scientific inputs, classic results and manual review fields remain preserved. Shared final browser verification remains pending. '
              'Earlier review records below retain historical numbers and hashes; they do not supersede this follow-up.\n\n---\n\n')
    if not index.read_text(encoding='utf-8').startswith('# Current complete-candidate follow-up'):
        index.write_text(banner + index.read_text(encoding='utf-8'), encoding='utf-8')
    annual = {(r['method'], r['catch_basis'], r['scope'], r['unidentified']): r
              for r in W.records(book, 'PPR', 'Annual') if r['metric'] == 'ppr'}
    classic = {(r['method'], r['catch_basis'], r['scope'], r['unidentified']): r
               for r in W.records(book, 'Classic PPR', 'Annual') if r['metric'] == 'ppr'}
    if unit == 'LME_003':
        audit = {r['taxon']: r for r in read(ev / 'taxon_audit.json')['rows']}
        for taxon, decision in handoff['adopted_decisions_keyed_by_taxon'].items():
            for key in decision:
                if key in audit[taxon]:
                    decision[key] = audit[taxon][key]
        handoff['final_workbook_sha256'] = fingerprint
        handoff['current_calculation_input_sha256'] = settings['calculation_input_sha256']
        handoff['current_calculation_result_sha256'] = settings['calculation_result_sha256']
        browser = read(ev / 'expected_browser_controls_results.json')
        for item in browser['expected_results']:
            row = (annual if item['sheet'] == 'PPR' else classic)[item['method'], 'landings', 'all', 'method']
            item.update(ppr_wet_tonnes=row[2019], ppr_tC=row[2019] / 9 if W.finite(row[2019]) else None, status=row['status'])
        ratios = {(r['method'], r['catch_basis'], r['scope'], r['unidentified'], r['npp_method']): r for r in W.records(book, 'PPR–NPP', 'Ratios')}
        for item in browser['expected_PPR_NPP_percent']:
            item['2019'] = ratios[item['method'], item['catch_basis'], item['scope'], item['unidentified'], item['npp_method']][2019]
        for item in browser['taxon_trace_checks']:
            item['expected'] = handoff['adopted_decisions_keyed_by_taxon'][item['taxon']]
        browser['workbook_sha256'] = fingerprint
        write(ev / 'expected_browser_controls_results.json', browser)
        handoff['derived_arithmetic']['default_results'] = browser['expected_results']
        handoff['derived_arithmetic']['verification'] = 'broad_candidate_calculations_verification.json'
        handoff['derived_arithmetic']['counts'] = proof['checks']
        handoff['mapping_corrections'] = ['mapping_changes.json (historical first review)', 'broad_candidate_followup.json (current additional corrections)']
        handoff['assignment_or_weight_changed_taxa_first_review'] = handoff.pop('assignment_or_weight_changed_taxa', handoff.get('assignment_or_weight_changed_taxa_first_review'))
        handoff['additional_assignment_or_weight_changed_taxa'] = [c['taxon'] for c in receipt['changes']]
        handoff['artifacts']['QA'].update(report_sha256=W.sha(report), appendix_sha256=W.sha(appendix), current_followup='broad_candidate_followup.json', calculation_evidence='broad_candidate_calculations_verification.json', historical_visual_evidence_note='Older image/link records retain the preceding review; current six-page and changed-appendix image hashes are in broad_candidate_followup.json.')
        handoff['artifacts']['portable_links'] = receipt['current_verification']['office_links']
        hashes_key = 'hashes'
    else:
        handoff['accepted_inputs']['model_settings'] = settings
        handoff['mapping_summary']['first_review_candidate_sets_changed'] = handoff['mapping_summary'].pop('candidate_sets_changed', 3)
        handoff['mapping_summary']['candidate_rows_current'] = len(W.records(book, 'PPR', 'Matching'))
        handoff['mapping_summary']['complete_candidate_followup_taxa'] = [c['taxon'] for c in receipt['changes']]
        handoff['regional_calculation'].update(verification='broad_candidate_calculations_verification.json', maximum_relative_difference=proof['max_relative_arithmetic_difference'], independent_taxon_coefficients_checked=proof['checks']['taxon_coefficients'], independent_annual_cells_checked=proof['checks']['annual_cells'])
        for item in handoff['expected_browser_values']['model_annual_values']:
            row = annual[item['method'], item['basis'], item['scope'], item['unidentified']]
            value = row[int(item['year'])]
            item.update(wet_ppr=value, ppr_tC=value / 9 if W.finite(value) else None, status=row['status'])
        handoff['expected_browser_values']['workbook_sha256'] = fingerprint
        handoff['current_office']['links'] = [{k: v for k, v in x.items() if k != 'links'} for x in office]
        handoff['current_office']['layout_evidence'] = 'broad_candidate_followup.json#/current_verification'
        handoff['current_office']['local_link_evidence'] = receipt['current_verification']['office_links']
        handoff['historical_evidence'] = 'Initial adoption and reuse evidence retain their original observations/hashes. Current broad candidates, arithmetic, method exposure, Office layout and links are identified in broad_candidate_followup.json; older results are historical.'
        handoff['manifest_verification']['interpretation'] = 'Previous manifest verified the preceding review. Current changed artifacts and complete-candidate QA are sealed in this handoff and broad_candidate_followup.json. Native scientific source and shared browser gaps remain explicit.'
        hashes_key = 'final_hashes'
        for path in handoff['evidence_hashes']:
            handoff['evidence_hashes'][path] = W.sha(ROOT / path)
    handoff['broad_candidate_followup'] = 'broad_candidate_followup.json'
    for path in handoff[hashes_key]:
        handoff[hashes_key][path] = W.sha(ROOT / path)
    handoff[hashes_key].update(final_files)
    for name in ['broad_candidate_followup.json', 'broad_candidate_calculations_verification.json', 'broad_candidate_method_exposure.json', 'reports_index.md']:
        handoff[hashes_key][(ev / name).relative_to(ROOT).as_posix()] = W.sha(ev / name)
    write(handoff_path, handoff)
    assert W.sha(workbook) == fingerprint
    release = {'unit_id': unit, 'regional_followup_complete': True, 'shared_final_reconciliation_pending': True,
               'files': final_files, 'handoff': {'path': handoff_path.relative_to(ROOT).as_posix(), 'sha256': W.sha(handoff_path)}}
    write(HERE / 'verification' / (unit + '_broad_candidate_release.json'), release)
    print(json.dumps(release), flush=True)


if __name__ == '__main__':
    for unit in sys.argv[1:]:
        seal(unit)
