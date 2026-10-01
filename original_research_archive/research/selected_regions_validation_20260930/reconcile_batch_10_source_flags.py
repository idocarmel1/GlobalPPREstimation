"""Authenticate the sole reviewed derived-paper-selection change after batch 10.

Read-only with respect to Project.xlsx. The failed exact source-table guard is
retained in the original integration receipt; this records its narrow resolution.
"""
import copy
import json
from pathlib import Path
from integrate_ready_batch import metadata_and_regions, sha

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    cache_path = HERE / 'central_source_metadata_current.json'
    receipt_path = HERE / 'verification/ready_batch_10_integration.json'
    cache = json.loads(cache_path.read_text(encoding='utf-8'))
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    before = '25746daf74f7aa99eabcf14dad26b078981501e24f11d07dd9984551bf4354d7'
    after = '81c201b01db1025d7840e05531bd334427e07b9a626c9497a75c923f2533a791'
    assert cache['project_sha256'] == receipt['project_before_sha256'] == before
    assert receipt['project_after_sha256'] == sha(ROOT / 'Project.xlsx') == after
    assert receipt['command_exit_code'] == 0 and not receipt['central_source_tables_unchanged']
    current = metadata_and_regions(ROOT / 'Project.xlsx')
    expected = copy.deepcopy(cache['tables'])
    article = 'LME028-Gascuel-2009__LME_028'
    targets = [r for r in expected['Papers'] if r['article_id'] == article]
    assert len(targets) == 1 and targets[0]['selected'] is True
    targets[0]['selected'] = False
    for table in ('Models & coverage', 'Papers'):
        assert current[table] == expected[table], f'Unreviewed source change: {table}'
    selected_papers = {pid for r in current['Models & coverage'] if r.get('selected')
                       for pid in str(r.get('paper_ids') or '').split(';') if pid}
    assert article not in selected_papers
    assert all(r.get('selected') == (r['article_id'] in selected_papers)
               for r in current['Papers'])
    for item in receipt['regional_inputs']:
        assert sha(ROOT / item['path']) == item['sha256']
        assert sha(ROOT / item['handoff']) == item['handoff_sha256']
    assert sha(ROOT / 'Project.xlsx') == after
    result = {
        'status': 'PASS', 'project_before_sha256': before, 'project_after_sha256': after,
        'derived_change': {'table': 'Papers', 'key': {'article_id': article},
                           'field': 'selected', 'before': True, 'after': False},
        'basis': 'Metadata batch 11 removed the unrelated 2009 paper from the selected 1998 Guinea model. Only two unselected 1985 models still cite this paper. update_project recomputed the derived selected flag correctly.',
        'all_other_source_values_exactly_preserved': True,
        'all_195_paper_flags_equal_selected_model_references': True,
        'regional_inputs_and_handoffs_unchanged_during_review': True,
        'project_workbook_modified_by_this_reconciliation': False,
        'evidence': ['verification/metadata_batch_11_plan_applied.json',
                     'verification/LME_028_source_association_applied.json',
                     'verification/ready_batch_10_integration.json'],
    }
    result_path = HERE / 'verification/ready_batch_10_source_flag_resolution.json'
    result_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    receipt['guard_resolution'] = result_path.relative_to(HERE).as_posix()
    receipt['status'] = 'PASS after explicit source-flag review; initial exact comparison retained'
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    cache['project_sha256'] = after
    cache['tables']['Papers'] = current['Papers']
    cache['provenance'] += '; ready_batch_10 numerical consolidation; sole derived Guinea 2009 selected-paper flag explicitly reviewed, all other source fields exact'
    cache.setdefault('numerical_integration_evidence', []).extend([
        receipt_path.relative_to(HERE).as_posix(), result_path.relative_to(HERE).as_posix()])
    cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
