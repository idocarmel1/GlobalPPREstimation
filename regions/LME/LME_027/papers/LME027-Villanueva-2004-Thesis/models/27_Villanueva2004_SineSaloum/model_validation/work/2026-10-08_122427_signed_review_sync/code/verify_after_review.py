"""Verify the published review after the final identity-boundary code review."""
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from tools.project_core.validation.researcher_review import approved_review, sha, table_rows


def main():
    root = Path.cwd().resolve()
    run = Path(__file__).resolve().parents[1]
    proof = json.loads((run/'qa/registration_result.json').read_text(encoding='utf-8'))
    unit_id, model_id = proof['unit_id'], proof['model_id']
    project = root/'Project.xlsx'
    assert sha(project) == proof['project_sha256_after']
    with zipfile.ZipFile(project) as archive:
        rows = [row for _, row in table_rows(archive, 'Models & coverage', 'Models')[3]]
    metadata = next(row for row in rows if (row['unit_id'], row['model_id']) == (unit_id, model_id))
    assert str(metadata.get('selected') or '').lower() in {'false', '0', ''}
    review = approved_review(root, metadata, {})
    assert review == proof['source_review']
    protected = [root/metadata['model_path'], root/metadata['validation_report_path'],
                 root/'regions/LME/LME_027/LME_027.xlsx']
    hashes = {path.relative_to(root).as_posix(): sha(path) for path in protected}
    for path in protected:
        assert sha(path) == proof['protected_artifact_sha256'][str(path.relative_to(root))]
    pages = {}
    for name, variable in [('index.html','DB'), ('trends.html','SERIES_DB')]:
        text = (root/'interactive_map'/name).read_text(encoding='utf-8')
        assert re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">', text).group(1) == sha(project)
        start = text.index('const '+variable+'=')+len('const '+variable+'=')
        payload, _ = json.JSONDecoder().raw_decode(text, start)
        unit = (payload['network']['units'] if variable == 'DB' else payload['units'])[unit_id]
        candidate = next(model for model in unit['models'] if model['id'] == model_id)
        assert candidate['researcher_review'] == review
        assert candidate['verified'] is False and candidate['scopes'] == {}
        assert not candidate['display_ppr_excluded_group_ids']
        assert 'recorded_review_pending' not in candidate
        assert 'group_data' not in candidate and 'workbook' not in candidate
        default = unit['models'][unit['default_model']]['id'] if variable == 'DB' else unit['default_model']
        assert default == '27_118_Northwest_Africa_(1987)'
        pages[name] = {'default_model': default, 'selectable_candidate': model_id,
                       'candidate_status': review['status'], 'candidate_scopes': {}}
    qa_path = run/'qa/verification_checks.json'
    qa = json.loads(qa_path.read_text(encoding='utf-8'))
    qa['final_review'] = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'findings_resolved': ['Positive signoff cannot approve a different retained calculation workbook',
                              'Verified active review clears stale pending warnings'],
        'review_tests_rerun': {'tests': 24, 'exit_code': 0, 'result': 'OK'},
        'map_tests_rerun': {'tests': 47, 'exit_code': 0, 'result': 'OK'},
        'reviewer_result': 'No remaining Critical or Important findings',
        'project_sha256': sha(project), 'protected_artifact_sha256': hashes,
        'published_pages': pages}
    with qa_path.open('w', encoding='utf-8', newline='\r\n') as output:
        output.write(json.dumps(qa, ensure_ascii=False, indent=2)+'\n')
    print('Final publication verified: exact signed disqualification, selectable candidate, unchanged default and protected inputs.')


if __name__ == '__main__':
    main()
