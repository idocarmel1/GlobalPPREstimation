"""Keep compact verified evidence, then remove only this run's scratch copies."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parent.parent
QA = RUN / 'qa'
ROOT = next(p for p in RUN.parents if (p / 'Project.xlsx').exists())
assert RUN.name == '2026-10-04_000009_skill_efficiency' and RUN.is_relative_to(ROOT)
def load(path): return json.loads(path.read_text(encoding='utf8'))
def save(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
if (QA / 'trial_copy_dispositions.json').is_file():
    print('Scratch-copy disposition already recorded; no second deletion.')
    raise SystemExit(0)

new = load(QA / 'new_word_trial.json')
retained = []
for page in new['render_evidence_reuse']['reused_page_images']:
    source = Path(page['path']).resolve()
    assert source.is_relative_to(RUN) and sha(source) == page['sha256']
    target = QA / 'word_render_evidence' / ('page-' + str(page['page']) + '.png')
    target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
    assert sha(target) == page['sha256']
    retained.append({'original_path': source.relative_to(RUN).as_posix(), 'retained_path': target.relative_to(RUN).as_posix(), 'sha256': sha(target)})
    page['original_verified_path'] = page['path']; page['path'] = str(target.resolve())
before = Path(new['render_evidence_reuse']['reused_page_images'][2]['original_verified_path']).parent.parent / 'before/page-3.png'
target = QA / 'word_render_evidence/before-page-3.png'
shutil.copyfile(before, target)
retained.append({'original_path': before.relative_to(RUN).as_posix(), 'retained_path': target.relative_to(RUN).as_posix(), 'sha256': sha(target)})
save(QA / 'new_word_trial.json', new)

blind = RUN / 'outputs/blind_extraction'
for relative, name in [('evidence/index.json', 'blind_inventory_verified_before_cleanup.json'),
                       ('evidence/completeness.json', 'blind_completeness_verified_before_cleanup.json'),
                       ('evidence/source_checks.json', 'blind_source_checks.json'),
                       ('evidence/source_identity.json', 'blind_source_identity.json'),
                       ('evidence/stage_trace.json', 'blind_stage_trace.json'),
                       ('model_2000s/SOURCE_FIDELITY_CHECK.json', 'blind_roundtrip_check.json')]:
    source = blind / relative
    if source.is_file():
        target = QA / name; shutil.copyfile(source, target)
        retained.append({'original_path': source.relative_to(RUN).as_posix(), 'retained_path': target.relative_to(RUN).as_posix(), 'sha256': sha(target)})
for source in (blind / 'evidence').glob('page_*_coordinates.json'):
    target = QA / 'source_locators' / source.name
    target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
    retained.append({'original_path': source.relative_to(RUN).as_posix(), 'retained_path': target.relative_to(RUN).as_posix(), 'sha256': sha(target)})

names = ['inputs/blind_extraction', 'outputs/blind_extraction', 'outputs/direct_diagnostics',
         'outputs/old_word_project', 'outputs/new_word_project', 'outputs/review_project',
         'qa/new_word_before_validation.docx']
targets = [(RUN / name).resolve() for name in names]
assert all(target.is_relative_to(RUN.resolve()) and target != RUN.resolve() and not target.is_symlink() for target in targets)
removed = []
for target in targets:
    if not target.exists(): continue
    paths = [target] if target.is_file() else [p for p in target.rglob('*') if p.is_file()]
    assert all(p.resolve().is_relative_to(RUN.resolve()) and not p.is_symlink() for p in paths)
    for path in paths:
        removed.append({'path': path.relative_to(RUN).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path),
                        'disposition': 'verified temporary trial copy removed; original source and compact metadata/reproducer preserved'})
    if target.is_dir(): shutil.rmtree(target)
    else: target.unlink()

proof = {'checked_at': datetime.now(timezone.utc).isoformat(), 'run_containment_verified': True,
         'retained': retained, 'removed': removed, 'removed_files': len(removed),
         'removed_bytes': sum(p['bytes'] for p in removed), 'scientific_live_files_removed': 0,
         'inventories': 'Original inventories prove presence/hashes at their recorded check time, before scratch cleanup. Current availability is this disposition record; no removed matrix/model/clone is claimed present.',
         'reproduction': 'Original source PDF remains at qa/blind_input_identity.json source path; exact input/code identities and reusable trial scripts remain. Reprepare isolated copies before replay. No second model JSON/extraction archive retained.'}
save(QA / 'trial_copy_dispositions.json', proof)
for name in ['diagnostic_replication_evidence_index.json', 'diagnostic_replication_completeness.json',
             'blind_inventory_verified_before_cleanup.json', 'blind_completeness_verified_before_cleanup.json',
             'old_word_trial.json', 'new_word_trial.json', 'new_word_trial_summary.json']:
    path = QA / name
    if path.is_file():
        data = load(path)
        data['current_artifact_availability'] = {'scope': 'verified at original execution before temporary cleanup',
                                                'dispositions': 'trial_copy_dispositions.json',
                                                'retained_render_evidence': 'word_render_evidence',
                                                'canonical_scientific_sources_preserved': True}
        save(path, data)
assert not list((RUN / 'outputs').rglob('model.json'))
print(json.dumps({'removed_files': proof['removed_files'], 'removed_bytes': proof['removed_bytes'], 'retained_compact_artifacts': len(retained), 'scientific_live_files_removed': 0}))
