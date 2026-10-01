"""Apply reviewed source metadata only; retain every scientific table and result."""
import copy
import json
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import workbooks as W
import regional as R
from bounded_workbook_update import update_blocks


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def write(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main():
    path = ROOT / 'regions/LME_028/LME_028.xlsx'
    ev = path.parent / 'validation_reports/28_646_Guinea_(1998)'
    proposal = read(ev / 'shared_metadata_proposals.json')['regional_metadata_proposals'][0]
    fingerprint = W.sha(path)
    assert fingerprint == proposal['reviewed_workbook_sha256']
    before = W.read_book(path)
    old = W.validate_region(before, path)
    assert R.result_hash(before) == old['calculation_result_sha256']
    assert old['selected_paper_ids'] == proposal['expected_old']
    after = copy.deepcopy(before)
    R.set_setting(after, 'selected_paper_ids', proposal['proposed_new'])
    assert W.input_hash(after) == W.input_hash(before)
    assert R.result_hash(after) == R.result_hash(before)
    backup = HERE / 'work/LME_028_source_metadata'
    backup.mkdir(exist_ok=True)
    shutil.copy2(path, backup / path.name)
    handoff_path = ev / 'coordination_handoff.json'
    shutil.copy2(handoff_path, backup / handoff_path.name)
    parts = update_blocks(path, before, after, expected_sha256=fingerprint)
    current = W.read_book(path)
    W.validate_region(current, path)
    assert current == after
    with ZipFile(backup / path.name) as a, ZipFile(path) as b:
        changed = [n for n in a.namelist() if a.read(n) != b.read(n)]
    assert changed == parts == ['xl/worksheets/sheet1.xml']
    current_hash = W.sha(path)
    receipt = {'unit_id': 'LME_028', 'scope': 'Source association metadata only; exact accepted selected model and all scientific/mapping inputs retained.',
               'proposal': proposal, 'before_workbook_sha256': fingerprint, 'current_workbook_sha256': current_hash,
               'changed_package_parts': parts, 'exact_table_diff': {'Overview/Settings/selected_paper_ids': [proposal['expected_old'], proposal['proposed_new']]},
               'input_hash_unchanged': W.input_hash(current), 'result_hash_unchanged': R.result_hash(current),
               'all_other_table_values_exact': True, 'canonical_freshness_passed': True,
               'scientific_rerun': False, 'report_appendix_changed': False,
               'evidence': proposal['evidence'], 'shared_integration_pending': True}
    write(ev / 'coordinator_source_association.json', receipt)
    calculation_path = ev / 'calculation_verification.json'
    calculation = read(calculation_path)
    calculation['before_source_metadata_workbook_sha256'] = calculation['workbook_sha256']
    calculation['workbook_sha256'] = current_hash
    calculation['source_metadata_followup'] = 'coordinator_source_association.json; all calculation inputs/results and checked cells unchanged.'
    write(calculation_path, calculation)
    index_path = ev / 'evidence_index.json'
    index = read(index_path)
    for item in index['files']:
        p = ev / item['path']
        assert p.exists(), p
        item['sha256'] = W.sha(p)
        item['bytes'] = p.stat().st_size
    index['files'].append({'path': 'coordinator_source_association.json', 'sha256': W.sha(ev / 'coordinator_source_association.json'), 'bytes': (ev / 'coordinator_source_association.json').stat().st_size})
    index['source_metadata_followup'] = 'Current regional source association corrected; prior protected-input records describe unchanged scientific tables and the preceding file hash.'
    write(index_path, index)
    handoff = read(handoff_path)
    handoff['files']['before_source_metadata_workbook_sha256'] = fingerprint
    handoff['files']['regional_workbook_sha256'] = current_hash
    handoff['files']['evidence_index_sha256'] = W.sha(index_path)
    handoff['calculations'] = calculation
    handoff['source_association_applied'] = receipt
    handoff['shared_integration']['post_metadata_refresh'] = 'Regional source association applied and final workbook/handoff/index identities refreshed. Scientific input/result hashes and all numerical tables unchanged. Shared Project/source metadata and browser reconciliation remain pending.'
    write(handoff_path, handoff)
    write(HERE / 'verification/LME_028_source_association_applied.json', {**receipt, 'current_handoff_sha256': W.sha(handoff_path), 'current_evidence_index_sha256': W.sha(index_path)})
    print(json.dumps({'unit_id': 'LME_028', 'workbook_sha256': current_hash, 'handoff_sha256': W.sha(handoff_path), 'all_numerical_inputs_results_unchanged': True}), flush=True)


if __name__ == '__main__':
    main()
