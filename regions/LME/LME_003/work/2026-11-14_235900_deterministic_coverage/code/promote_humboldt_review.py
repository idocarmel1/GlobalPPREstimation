"""Promote the explicitly authorized EE-floor review inside the outer transaction.

Registration is metadata-only. Scientific adoption and the initial saved-data
build must finish first, while the original signed report is still canonical.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import zipfile


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def local(root, value):
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Review handoff escaped the project')
    return path


def parse_at_destination(root, staged, canonical, model_id):
    """Resolve retained relative links exactly as they will resolve on adoption."""
    from tools.project_core.validation.researcher_review import read_report
    fd, temporary = tempfile.mkstemp(prefix='.review-check-', suffix='.docx', dir=canonical.parent)
    os.close(fd)
    temporary = Path(temporary)
    try:
        temporary.write_bytes(staged.read_bytes())
        return read_report(root, temporary, model_id)
    finally:
        temporary.unlink(missing_ok=True)


def prepare_review(root, handoff_path):
    from tools.project_core.validation.researcher_review import read_report, STATUS, table_rows, review_group_sequences
    from tools.project_core.validation.validation_percentage_format import verify_report
    handoff_path = Path(handoff_path)
    handoff = json.loads(handoff_path.read_text(encoding='utf-8'))
    handoff['original_sha256'] = handoff.get('original_sha256', handoff.get('canonical_expected_before_sha256'))
    if handoff.get('ready_for_parent_promotion') is not True or handoff.get('all_other_parser_fields_identical') is not True:
        raise ValueError('The staged document has no completed QA handoff')
    consumed = {handoff_path: sha(handoff_path)}
    for name in ('signoff_before', 'signoff_after', 'parser_diff', 'render_qa', 'package_qa', 'numerical_evidence'):
        ref = handoff[name]
        evidence = local(root, ref['path'])
        if sha(evidence) != ref['sha256']:
            raise ValueError('Reviewed DOCX QA evidence changed: ' + name)
        consumed[evidence] = ref['sha256']
    if (handoff['unit_id'], handoff['model_id']) != (
            'LME_013', 'Chiaverano2018_detailed_Northern_Humboldt_1995_1998'):
        raise ValueError('This authorized amendment covers only the exact Humboldt model')
    canonical = local(root, handoff['canonical_report'])
    staged = local(root, handoff['staged_report'])
    if staged == canonical or canonical.name != 'validation.docx':
        raise ValueError('Require a separate staged report and the canonical destination')
    for key, path in [('original_sha256', canonical), ('staged_sha256', staged)]:
        if sha(path) != handoff[key]:
            raise ValueError('Review bytes changed: ' + key)
    verify_report(staged)
    before = read_report(root, canonical, handoff['model_id'])
    after = parse_at_destination(root, staged, canonical, handoff['model_id'])
    if before[:2] != after[:2]:
        raise ValueError('Researcher identity or actual signoff date changed')
    old, new = copy.deepcopy(before[2]), copy.deepcopy(after[2])
    if old.get('status', STATUS) != STATUS or new.get('status', STATUS) != STATUS:
        raise ValueError('The explicit validated decision must remain validated')
    if old['sections'][1]['heading'] != 'GE and TE diagnostics' or new['sections'][1]['heading'] != old['sections'][1]['heading']:
        raise ValueError('Unexpected diagnostic parser section')
    old['sections'][1] = new['sections'][1]
    if old != new:
        raise ValueError('Review amendment unexpectedly changed fields outside GE/TE diagnostics')
    with zipfile.ZipFile(root / 'Project.xlsx') as archive:
        metadata = [r for _, r in table_rows(archive, 'Models & coverage', 'Models')[3]
                    if (r.get('unit_id'), r.get('model_id')) == (handoff['unit_id'], handoff['model_id'])]
    if len(metadata) != 1 or metadata[0].get('researcher_review_status') != STATUS:
        raise ValueError('Humboldt must already have its exact registered validated review')
    metadata = metadata[0]
    if metadata.get('validation_report_sha256') != handoff['original_sha256']:
        raise ValueError('Original review registration changed')
    summary = json.loads(metadata['researcher_review_summary'])
    region = root / 'regions/LME/LME_013/LME_013.xlsx'
    with zipfile.ZipFile(region) as archive:
        settings = {r['field']: r.get('value') for _, r in table_rows(archive, 'Overview', 'Settings')[3]}
        if settings.get('results_model_id') != handoff['model_id']:
            raise ValueError('Regional group identities do not belong to the approved Humboldt model')
        groups = [r for _, r in table_rows(archive, 'Selected model groups', 'Groups')[3]]
    ids = review_group_sequences(groups)
    excluded = summary.get('excluded_group_ids', [])
    if any(name not in ids for name in excluded):
        raise ValueError('Original researcher exclusions do not resolve')
    return {'handoff': handoff, 'handoff_path': handoff_path, 'handoff_sha256': sha(handoff_path),
            'canonical': canonical, 'staged': staged, 'before': before, 'after': after,
            'consumed': consumed,
            'excluded_seq': [ids[name] for name in excluded], 'excluded_group_ids': excluded,
            'metadata_before': metadata}


def publish_review(root, work, prepared):
    from tools.project_core.registry.publication import publication_write
    from tools.project_core.validation.researcher_review import _register_review, read_report, STATUS
    from tools.project_core.maps.build_html import _refresh_reviews
    handoff = prepared['handoff']
    canonical, staged = prepared['canonical'], prepared['staged']
    if (sha(canonical) != handoff['original_sha256'] or sha(staged) != handoff['staged_sha256']
            or sha(prepared['handoff_path']) != prepared['handoff_sha256']):
        raise ValueError('Reviewed handoff changed before promotion')
    project = root / 'Project.xlsx'
    previous = work / 'inputs/Project_before_humboldt_review.xlsx'
    original = (local(root, handoff['retained_historical_original']) if handoff.get('retained_historical_original')
                else canonical.parent / 'evidence/ee_floor_amendment_20261115/original_signed_validation.docx')
    if original.exists() and sha(original) != handoff['original_sha256']:
        raise ValueError('Historical signed report already exists with different bytes')
    original.parent.mkdir(parents=True, exist_ok=True)
    with publication_write(previous, fingerprint=sha(project)):
        previous.write_bytes(project.read_bytes())
    with publication_write(original, fingerprint=handoff['original_sha256']):
        original.write_bytes(canonical.read_bytes())
    fd, temporary = tempfile.mkstemp(prefix='.review-promote-', suffix='.docx', dir=canonical.parent)
    os.close(fd)
    temporary = Path(temporary)
    try:
        temporary.write_bytes(staged.read_bytes())
        with publication_write(canonical, fingerprint=handoff['staged_sha256']):
            os.replace(temporary, canonical)
    finally:
        temporary.unlink(missing_ok=True)
    if read_report(root, canonical, handoff['model_id']) != prepared['after']:
        raise ValueError('Promoted report parser differs from the reviewed staged document')
    # These internal variants deliberately reuse the outer non-reentrant lock.
    with publication_write(project):
        registered = _register_review(project, canonical, handoff['unit_id'], handoff['model_id'], prepared['excluded_seq'])
    if registered['researcher_review_status'] != STATUS:
        raise ValueError('Humboldt lost its validated decision')
    summary = json.loads(registered['researcher_review_summary'])
    if summary['excluded_group_ids'] != prepared['excluded_group_ids']:
        raise ValueError('Researcher group exclusions changed')
    if (registered['researcher_name'], registered['researcher_review_date']) != prepared['before'][:2]:
        raise ValueError('Original signoff changed during registration')
    # The gate reconstructs the bounded registration and compares every ZIP
    # member, then checks both pages' pre-registration Project fingerprint.
    _refresh_reviews(project, previous, [], model_pairs={(handoff['unit_id'], handoff['model_id'])}, publish=True)
    return {'unit_id': handoff['unit_id'], 'model_id': handoff['model_id'],
            'configuration': {'use_ee_floor': True, 'ee_floor': 0.1, 'det_collapse_mode': 'auto'},
            'original_report_sha256': handoff['original_sha256'], 'current_report_sha256': sha(canonical),
            'report_path': canonical.relative_to(root).as_posix(),
            'historical_report_path': original.relative_to(root).as_posix(),
            'handoff_path': prepared['handoff_path'].relative_to(root).as_posix(),
            'handoff_sha256': prepared['handoff_sha256'],
            'researcher_review_status': registered['researcher_review_status'],
            'excluded_group_ids': summary['excluded_group_ids'],
            'checks': ['original reviewer, date, validated verdict and group exclusions preserved',
                       'only GE/TE parser diagnostics amended', 'exact bounded registration replay passed',
                       'both pages matched the pre-registration Project fingerprint']}
