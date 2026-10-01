"""Publish the regional/shared verification index before graph and Git closeout."""
import copy
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
V = BASE / 'verification'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def relative(target, parent=BASE):
    return os.path.relpath(ROOT / target, parent).replace('\\', '/')


def main():
    now = datetime.now(timezone.utc).isoformat()
    synthesis_path = BASE / 'work/final_status_synthesis/final_23_region_status.json'
    synthesis = read(synthesis_path)
    retained = V / 'regional_synthesis_before_presentation'
    retained.mkdir(exist_ok=True)
    for name in ('final_23_region_status.json', 'final_23_region_table_proposal.md', 'verification.json'):
        src = synthesis_path.parent / name
        dst = retained / name
        assert not dst.exists(), 'One-time closeout already applied'
        shutil.copyfile(src, dst)
        assert sha(src) == sha(dst)
    progress_path = V / 'review_package_progress.json'
    progress = read(progress_path)
    shutil.copyfile(progress_path, retained / 'review_package_progress_before_presentation.json')
    wording_path = V / 'final_docx_wording/final_verification.json'
    wording = read(wording_path)
    patches = {r['unit']: r for r in wording['files']}
    checkpoint = read(V / 'current_all23_office_confidence_checkpoint.json')
    for row in progress['regions']:
        unit = row['unit_id']
        if unit in patches:
            p = patches[unit]
            assert row['report']['sha256'] == p['before_sha256']
            assert sha(ROOT / p['path']) == p['final_sha256']
            hpath = ROOT / row['handoff']['path']
            assert sha(hpath) == row['handoff']['sha256']
            shutil.copyfile(hpath, retained / f'{unit}_handoff_before_presentation.json')
            handoff = read(hpath)
            handoff['coordinator_final_presentation'] = {
                'recorded_utc': now,
                'scope': 'One automatic status text node only; earlier report hashes describe historical verification stages.',
                'current_report': {'path': p['path'], 'sha256': p['final_sha256']},
                'before_report_sha256': p['before_sha256'],
                'evidence': {'path': wording_path.relative_to(ROOT).as_posix(), 'sha256': sha(wording_path)},
                'scientific_parameters_and_manual_fields_unchanged': True,
                'shared_results_verified': True,
                'graph_and_git_closeout': 'Tracked by the coordinator; not certified by this regional handoff.',
            }
            save(hpath, handoff)
            row['report']['sha256'] = p['final_sha256']
            row['handoff']['sha256'] = sha(hpath)
        for role in ('report', 'appendix', 'handoff', 'workbook'):
            assert sha(ROOT / row[role]['path']) == row[role]['sha256'], (unit, role)
        row['phase'] = 'Regional review and shared result reconciliation complete; graph and Git closeout tracked centrally'
        c = next(c for c in checkpoint['regions'] if c['unit_id'] == unit)
        for role in ('report', 'appendix'):
            old = c[role]['file_sha256']
            current = row[role]['sha256']
            if old != current:
                assert role == 'report' and old == patches[unit]['before_sha256']
                c[role]['pre_presentation_file_sha256'] = old
                c[role]['file_sha256'] = current
                c[role]['unchanged_link_and_manual_xml_bridge'] = {
                    'path': wording_path.relative_to(ROOT).as_posix(), 'sha256': sha(wording_path)}
    progress['scope'] = 'Current regional packages and verified shared results. Scientific approval is not implied; graph and Git closeout remain separate.'
    progress['updated_utc'] = now
    progress['shared_results_reconciled'] = 23
    save(progress_path, progress)
    checkpoint['scope'] = 'All 46 current Office artifacts: original exact-hash link/relocation evidence plus bounded final wording proofs; all 6,289 confidence labels verified. No scientific approval implied.'
    checkpoint['recorded_utc'] = now
    save(V / 'final_all23_office_confidence_checkpoint.json', checkpoint)

    final = copy.deepcopy(synthesis)
    final['recorded_utc'] = now
    final['scope'] = 'All23 regional reviews and shared results reconciled. Graph publication and Git closeout are recorded separately.'
    final['historical_synthesis_inputs'] = final.pop('inputs')
    final['original_synthesis'] = {'path': (retained / synthesis_path.name).relative_to(ROOT).as_posix(), 'sha256': sha(retained / synthesis_path.name)}
    for row in final['regions']:
        current = next(r for r in progress['regions'] if r['unit_id'] == row['unit_id'])
        row['artifacts'] = {k: copy.deepcopy(current[k]) for k in ('report', 'appendix', 'handoff', 'workbook')}
        row['review_status'] = 'Review package complete; shared results reconciled; scientific limitations retained'
        row['historical_regional_evidence_bindings'] = row.pop('evidence')
    final['project_sha256'] = sha(ROOT / 'Project.xlsx')
    final['verification'] = [
        {'path': (V / name).relative_to(ROOT).as_posix(), 'sha256': sha(V / name)}
        for name in ('final_all23_protected_inputs_and_serialization.json', 'final_all23_office_confidence_checkpoint.json',
                     'final_all23_map_browser_values.json', 'final_trends_outputs/verification.json')]
    final['workflow_completion'] = {'regional_reviews': 'complete', 'shared_results': 'verified', 'knowledge_graph': 'tracked separately', 'git_commit_push': 'tracked separately'}
    save(BASE / 'final_23_region_status.json', final)

    lines = ['# Validation of all 23 selected regions', '',
        'All 23 regional review packages are complete and their selected models, annual results and source metadata are reconciled with Project.xlsx and the generated map, trends and archive. This is a review record, not scientific model approval. Diagnostic grades, result availability and accepted production flags remain distinct.', '',
        'The review covers 6,289 exact catch labels: 1,702 High, 2,750 Medium, 247 Low, 1,570 Very low and 20 Unresolved. Accepted scientific inputs, researcher review fields, catch, classic trophic levels and NPP were preserved. Only supported taxonomy, membership, allocation and confidence corrections were adopted.', '',
        'This index supersedes pending coordinator-stage wording in historical regional handoffs. Exact current artifact identities and regional evidence are in [the machine-readable status](final_23_region_status.json). Knowledge-graph publication and Git commit/push verification are separate final coordination records; they do not change these scientific conclusions.', '',
        '| Region | Selected model | GE / TE / Egestion diagnostics | Reports |', '|---|---|---|---|']
    for r in final['regions']:
        grades = ' / '.join(str(r['methods'][k]['diagnostic_status']) for k in ('GE','TE','With Egestion'))
        report = relative(r['artifacts']['report']['path'])
        appendix = relative(r['artifacts']['appendix']['path'])
        lines.append(f"| {r['unit_id']} — {r['region_name']} | `{r['model_id']}` | {grades} | [Word](<{report}>) · [Excel](<{appendix}>) |")
    lines += ['', '## Adopted mapping corrections and retained scientific limits', '',
        'Six selected modern-method choices remain unavailable: Celtic-Biscay TE, all three Mediterranean methods, Guinea TE (IMPLAUSIBLE), and Okhotsk TE (DIVERGED). Other numeric results can still carry WARN or FAIL diagnostics. The four-method trends comparison uses 19 ecosystems with common complete series and lists the four exclusions. It does not silently replace missing results with zero.', '']
    for r in final['regions']:
        lines += [f"### {r['unit_id']} — {r['region_name']}", '',
                  'Mapping: ' + ' '.join(r['key_mapping_corrections']), '',
                  'Accepted scientific edits retained: ' + r['accepted_manual_scientific_edits_preserved'], '',
                  'Inherited scientific conventions retained: ' + r.get('inherited_scientific_conventions_preserved','See regional evidence.'), '',
                  'Scientific limits: ' + r['diagnostic_limits'] + ' ' + ' '.join(r['unresolved_limitations']), '']
    lines += ['## Shared lessons', '',
        'Candidate group sets must be complete before allocation. Source observations, unknown catch, censored or rounded cells and loader-filled zeros are distinct. Biomass fallback uses the complete accepted vector only when the source catch vector is unsuitable; no balancing or scientific parameter repair follows from a mapping discrepancy.', '',
        'Taxonomic identity and rank must match the catch label. Ecological analogues need an explicit regional evidence trail and appropriately low confidence. Membership confidence and allocation confidence are separate. A source supplementary table can establish membership without establishing caught stage proportions. Geographic overlap uses explicit denominators and does not become a catch or PPR multiplier.', '',
        'Every adopted transferable lesson was revisited in completed reviews, including LME_032, LME_034 and LME_036. Regional differences remain governed by their own evidence. The [adoption ledger](adopted_shared_lessons.json) records the decisions and revisit evidence.', '',
        '## Verification and practical limits', '',
        'Protected-input and serialization checks cover 7,417,744 cells. Central reconciliation checks 1,387,050 regional annual cells; the generated-page verifier checks 2,179,380 annual cells plus NPP. Browser inspection compared 92 map values/availability states and all 23 group controls, plus trends aggregation and method/catch/source/NPP controls. The final 46 Office artifacts have blue underlined hyperlinks, portable destinations and retained layout evidence.', '',
        'The repository was physically relocated with 753 generated-page/supporting files and 1,155 local destinations. Map, trends and archive were opened from the relocated copy. External references were classified rather than represented as newly re-fetched. The in-app browser download event timed out; the exact embedded CSV and JSON export functions were instead exercised offline and checked against the observed results. Browser responsive-layout coverage is limited by the narrow in-app viewport.', '',
        'All scientific limitations and unavailable source material remain explicit in the regional reports. No parameter restoration, rebalancing or scientific approval is inferred from completion of this review.']
    (BASE / 'final_validation_status.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    plan_path = V / 'knowledge_graph_refresh_plan.json'
    plan = read(plan_path)
    master = (BASE / 'final_validation_status.md').relative_to(ROOT).as_posix()
    plan['proposed_new_sources'] = sorted(set(plan['proposed_new_sources']) | {master})
    indexes = [p for p in plan['proposed_new_sources'] if p.startswith('regions/') and p.endswith('/reports_index.md')]
    assert len(indexes) == 23
    for rel in indexes:
        p = ROOT / rel
        text = p.read_text(encoding='utf-8-sig')
        if rel == 'regions/LME_052/reports_index.md':
            text = text.replace('The report remains a pending alignment draft until the coordinator verifies the shared tables and browser display.', 'The regional review and shared table/browser reconciliation are complete; scientific limitations remain.')
        link = os.path.relpath(BASE / 'final_validation_status.md', p.parent).replace('\\','/')
        text += '\n## Coordinator reconciliation — 1 October 2026\n\nRegional review and shared result reconciliation are complete. Earlier pending coordinator tasks in the regional handoff describe its historical release stage. Current reports, appendices, preserved scientific inputs, limits and verification are indexed in [the 23-region coordinator record](<' + link + '>). Scientific approval is not implied; graph and Git closeout are tracked separately.\n'
        p.write_text(text, encoding='utf-8')
    plan['status'] = 'All regional sources complete; final coordinator index added. Root must freeze exact source bytes before extraction.'
    save(plan_path, plan)

    readme = ROOT / 'README.md'
    text = readme.read_text(encoding='utf-8-sig')
    text += '\n## Selected-region review — 1 October 2026\n\nAll 23 selected regions now have completed validation reports and linked Excel appendices. See the [current regional review index](original_research_archive/research/selected_regions_validation_20260930/final_validation_status.md) for selected-model identities, adopted mapping corrections, preserved manual scientific edits, diagnostics and limitations. Historical validation and restoration counts above remain dated evidence.\n\nCurrent shared verification reconciles 1,387,050 regional annual cells with Project.xlsx and 2,179,380 generated annual cells plus NPP with the workbooks. Live localhost browser checks verify all 23 model/group selectors, 92 map values or unavailable results, and representative trends controls; generated pages and supporting links were also physically relocated. These checks supersede the historical local-file browser-policy limitation above. The exact CSV/JSON serializers pass offline checks; the in-app browser did not deliver a download event. Scientific WARN, FAIL, NOT_RUN, unavailable coefficients and production flags remain distinct. Accepted model parameters were not restored or rebalanced.\n'
    readme.write_text(text, encoding='utf-8')
    log_path = BASE / 'coordination_log.json'
    log = read(log_path)
    log['shared_integration_pending'] = []
    log['active_region_leads'] = {}
    log['active_coordination_reviews'] = {}
    log['nested_slot_owner'] = None
    log['final_shared_verification_in_progress'] = None
    log['phase'] = 'All23 regional/shared review complete; knowledge graph and Git closeout underway'
    log['final_shared_verification'] = {'project_sha256': final['project_sha256'], 'map_values_and_group_controls': 'PASS', 'central_annual_cells': 1387050, 'generated_annual_cells':2179380, 'scientific_approval':False}
    save(log_path, log)
    save(V / 'coordinator_final_presentation_acceptance.json', {'recorded_utc':now,'status':'PASS','reports_changed':6,'handoffs_updated':6,'regional_indexes_updated':23,'master_status':master,'docx_qa':{'path':wording_path.relative_to(ROOT).as_posix(),'sha256':sha(wording_path)},'root_spot_visual_checks':['EEZ_598 page1','LME_038 page2'],'shared_scientific_files_unchanged_by_closeout':True})
    print(json.dumps({'status':'PASS','regions':23,'reports':6,'indexes':23,'master':master}))


if __name__ == '__main__':
    main()
