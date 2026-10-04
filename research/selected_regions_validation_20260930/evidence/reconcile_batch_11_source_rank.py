"""Authenticate the new source row's sole derived atlas rank after batch 11.

Read-only with respect to Project.xlsx; preserve the initial guard failure.
"""
import copy
import json
from pathlib import Path
from integrate_ready_batch import metadata_and_regions, sha

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    cache_path = HERE / 'central_source_metadata_current.json'
    receipt_path = HERE / 'verification/ready_batch_11_integration.json'
    cache = json.loads(cache_path.read_text(encoding='utf-8'))
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    before = 'a53bab4a1a0938911bfa9b30ec26200a113bee39b6d8149b40f3b1ebe7f76645'
    after = 'ce0b658e76432e13b4c8c38a2ef5b985a54f9d9b7b44e478224539dbb32e51fa'
    assert cache['project_sha256'] == receipt['project_before_sha256'] == before
    assert receipt['project_after_sha256'] == sha(ROOT / 'Project.xlsx') == after
    assert receipt['command_exit_code'] == 0 and not receipt['central_source_tables_unchanged']
    current = metadata_and_regions(ROOT / 'Project.xlsx')
    expected = copy.deepcopy(cache['tables'])
    article = 'Christensen-1998__LME_035'
    target = [r for r in expected['Papers'] if r['article_id'] == article]
    region = [r for r in current['Regions & status'] if r['unit_id'] == 'LME_035']
    assert len(target) == len(region) == 1
    assert target[0]['atlas_region_rank'] is None and region[0]['atlas_region_rank'] == 10
    target[0]['atlas_region_rank'] = 10
    for table in ('Models & coverage', 'Papers'):
        assert current[table] == expected[table], f'Unreviewed source change: {table}'
    ranks = {r['unit_id']: r['atlas_region_rank'] for r in current['Regions & status']}
    assert all(r['atlas_region_rank'] == ranks.get(r['unit_id']) for r in current['Papers'])
    for item in receipt['regional_inputs']:
        assert sha(ROOT / item['path']) == item['sha256']
        assert sha(ROOT / item['handoff']) == item['handoff_sha256']
    assert sha(ROOT / 'Project.xlsx') == after
    result = {
        'status': 'PASS', 'project_before_sha256': before, 'project_after_sha256': after,
        'derived_change': {'table': 'Papers', 'key': {'article_id': article, 'unit_id': 'LME_035'},
                           'field': 'atlas_region_rank', 'before': None, 'after': 10},
        'basis': 'Metadata batch12 inserted the previously absent selected source. update_project applies atlas_ranks.apply_atlas_ranks, copying the existing regional rank10 into this new paper row. Model/source selection and scientific inputs unchanged.',
        'all_other_source_values_exactly_preserved': True,
        'all_paper_ranks_match_current_region_ranks': True,
        'paper_records_checked': len(current['Papers']),
        'regional_inputs_and_handoffs_unchanged': True,
        'project_workbook_modified_by_this_reconciliation': False,
        'evidence': ['verification/metadata_batch_12_plan_applied.json',
                     'verification/ready_batch_11_integration.json', 'tools/atlas_ranks.py'],
    }
    result_path = HERE / 'verification/ready_batch_11_source_rank_resolution.json'
    result_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    receipt['guard_resolution'] = result_path.relative_to(HERE).as_posix()
    receipt['status'] = 'PASS after explicit derived-rank review; initial exact comparison retained'
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    cache['project_sha256'] = after
    cache['tables']['Papers'] = current['Papers']
    cache['provenance'] += '; ready_batch_11 consolidation; sole new-paper derived atlas rank explicitly reviewed, all other source fields exact'
    cache.setdefault('numerical_integration_evidence', []).extend([
        receipt_path.relative_to(HERE).as_posix(), result_path.relative_to(HERE).as_posix()])
    cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
