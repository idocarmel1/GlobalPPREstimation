"""Exact signed-registry cohort for the 18 October successor analysis."""
from datetime import datetime, timezone
import hashlib
import json
import zipfile

EXCLUDED_PAIR = ('LME_028', '28_646_Guinea_(1998)')
REQUIRED_PAIRS = (
    ('HS_077', '077HS_1_Eastern_tropical_Pacific_(1993-1997)'),
    ('LME_013', 'Chiaverano2018_detailed_Northern_Humboldt_1995_1998'),
    ('LME_032', '32_1_Arabian_Sea_off_Karnataka_(2000)'),
    ('LME_034', '34_1_Bay_of_Bengal_(1978)'),
    ('LME_035', '35_412_Gulf_of_Thailande_(1963)'),
    ('LME_036', '36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)'),
    ('LME_047', '47_2_East_China_Sea_(2018)'),
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_pairs(pairs):
    pairs = [tuple(pair) for pair in pairs]
    if len(pairs) != len(set(pairs)):
        raise ValueError('Duplicate model-region pair in cohort')
    if set(pairs) != set(REQUIRED_PAIRS):
        raise ValueError(f'Unexpected cohort: {sorted(pairs)!r}')
    return sorted(pairs)


def registry_rows(root):
    from tools.project_core.validation.researcher_review import table_rows
    with zipfile.ZipFile(root / 'Project.xlsx') as archive:
        rows = [row for _, row in table_rows(archive, 'Models & coverage', 'Models')[3]]
    pairs = [(r['unit_id'], r['model_id']) for r in rows
             if r.get('researcher_review_status') == 'Validated by researcher']
    validate_pairs(pairs)
    excluded = [r for r in rows if (r['unit_id'], r['model_id']) == EXCLUDED_PAIR]
    if len(excluded) != 1 or excluded[0].get('researcher_review_status') != 'Disqualified by researcher':
        raise ValueError('The exact excluded pair lacks its registered signed disqualification')
    return rows, excluded[0]


def capture_cohort(root, path):
    project_hash = sha(root / 'Project.xlsx')
    rows, excluded = registry_rows(root)
    fields = ('unit_id', 'model_id', 'researcher_review_status', 'researcher_name',
              'researcher_review_date', 'validation_report_path', 'validation_report_sha256')
    pairs = []
    for key in sorted(REQUIRED_PAIRS):
        row = next(r for r in rows if (r['unit_id'], r['model_id']) == key)
        if sha(root / row['validation_report_path']) != row['validation_report_sha256']:
            raise ValueError(f'Signed report no longer matches registry: {key}')
        pairs.append({field: row.get(field) for field in fields})
    if sha(root / excluded['validation_report_path']) != excluded['validation_report_sha256']:
        raise ValueError('Disqualification source no longer matches registry')
    manifest = {
        'schema_version': 1,
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'project_path': 'Project.xlsx', 'project_sha256': project_hash,
        'selection_rule': 'Exactly the seven remaining registered researcher-validated model-region pairs after the signed 18 October 2026 withdrawal.',
        'pairs': pairs,
        'excluded_pairs': [{**{field: excluded.get(field) for field in fields},
                            'status_at_run': excluded['researcher_review_status'],
                            'reason': 'Researcher approval withdrawn; excluded from this current validated cohort'}],
        'scientific_scope': 'Saved coefficients and original scientific restrictions; no engine runs or new scientific approval.',
    }
    if sha(root / 'Project.xlsx') != project_hash:
        raise ValueError('Registry changed during cohort capture')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


def assert_cohort_current(root, path):
    manifest = json.loads(path.read_text(encoding='utf-8'))
    validate_pairs((p['unit_id'], p['model_id']) for p in manifest['pairs'])
    if sha(root / 'Project.xlsx') != manifest['project_sha256']:
        raise ValueError('Registry bytes changed after cohort capture')
    registry_rows(root)
    for row in manifest['pairs'] + manifest['excluded_pairs']:
        if sha(root / row['validation_report_path']) != row['validation_report_sha256']:
            raise ValueError(f"Signed source changed: {row['unit_id']}/{row['model_id']}")
    return manifest
