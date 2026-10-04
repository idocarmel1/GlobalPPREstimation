"""Guarded file-role correction; preserve unrelated metadata and scientific inputs."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / 'tools'))
from original_atlas_data import embedded, reconcile_paper_files

ROLE_PATH = ROOT / 'common_reference_data/paper_file_roles.json'
SOURCE = ROOT / 'regions/LME_052/papers/OKH-GM2019'
PREFIX = SOURCE.relative_to(ROOT).as_posix() + '/'
ARTICLE_ID = 'OKH-GM2019__LME_052'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    before_bytes = ROLE_PATH.read_bytes()
    before_hash = sha(ROLE_PATH)
    before = read(ROLE_PATH)
    assert before['schema_version'] == 1
    previous = {r['path']: r for r in before['files']}
    assert len(previous) == len(before['files']), 'Duplicate role path'

    evidence_prefix = PREFIX + 'source_manifest.json'
    specs = {
        'gorbatenko_melnikov_2019.pdf': (
            'main', 'Primary article: Gorbatenko and Melnikov (2019), original Russian PDF',
            'Primary 2019 article, Izvestiya TINRO 198:143–163, DOI 10.26428/1606-9919-2019-198-143-163. '
            'Original PDF page 1 establishes publication identity; Table 3 and Figure 9 establish this reconstruction source. '
            'Exact source URL, 21-page identity and hash are retained in ' + evidence_prefix + '.'),
        'gorbatenko_melnikov_2019_English_translation.pdf': (
            'context', 'Unofficial English translation: Gorbatenko and Melnikov (2019)',
            'Translation front matter explicitly identifies an unofficial AI-assisted research translation, '
            'not an author-approved or publisher-issued edition; the original Russian PDF remains authoritative. '
            'Its exact output hash and source hash are retained in ' + PREFIX + 'English_translation_work/verification.json.'),
        'gorbatenko_2018_dissertation.pdf': (
            'context', 'Supporting dissertation: Gorbatenko (2018), Okhotsk Sea trophodynamics',
            'PDF page 1 identifies K. M. Gorbatenko, Trophodynamics of marine organisms in the Okhotsk Sea, '
            'doctoral dissertation, Vladivostok 2018. It is a separate 468-page supporting source, '
            'including recovered feeding tables, rather than the focal 2019 journal article. Identity and hash: ' + evidence_prefix + '.'),
        'gorbatenko_levitskaya_2016_pollock.pdf': (
            'context', 'Supporting study: Gorbatenko and Levitskaya (2016), pollock feeding',
            'PDF page 1 identifies a separate 2016 Izvestiya TINRO 185:194–203 study of pollock food composition, '
            'daily rations and prey consumption in the Okhotsk Sea. DOI 10.26428/1606-9919-2016-185-194-203. '
            'Supporting feeding context; exact identity and hash: ' + evidence_prefix + '.'),
        'gorbatenko_melnikov_2016_herring.pdf': (
            'context', 'Supporting study: Gorbatenko and Melnikov (2016), herring feeding',
            'PDF page 1 identifies a separate 2016 Izvestiya TINRO 185:185–193 herring trophic study. '
            'DOI 10.26428/1606-9919-2016-185-185-193. Supporting feeding context; '
            'exact identity and hash: ' + evidence_prefix + '.'),
        'gorbatenko_2016_euphausiids.pdf': (
            'context', 'Supporting study: Gorbatenko (2016), euphausiid distribution and feeding',
            'PDF page 1 identifies a separate 2016 Izvestiya TINRO 185:204–214 study of quantitative euphausiid '
            'distribution and feeding in the Okhotsk Sea. DOI 10.26428/1606-9919-2016-185-204-214. '
            'Supporting context; exact identity and hash: ' + evidence_prefix + '.'),
        'gorbatenko_2016_sagitta.pdf': (
            'context', 'Supporting study: Gorbatenko (2016), Sagitta distribution and biomass',
            'PDF page 1 identifies a separate 2016 Izvestiya TINRO 184:168–177 study of Sagitta distribution, '
            'biomass and interannual dynamics in the Okhotsk Sea. DOI 10.26428/1606-9919-2016-184-168-177. '
            'Supporting context; exact identity and hash: ' + evidence_prefix + '.'),
        'discovery_feeding_sources_manifest.json': (
            'context', 'Provenance: supporting feeding-source discovery manifest (JSON)',
            'This file is a list of retrieved feeding-publication names, DOIs, URLs, page counts and hashes. '
            'Its contents record acquisition provenance; they contain no native Ecopath group parameters or diet matrix.'),
        'discovery_gorbatenko2019_routes.json': (
            'context', 'Provenance: 2019 article retrieval routes (JSON)',
            'This file lists article landing-page and DOI retrieval routes, HTML response paths and response hashes. '
            'It is retrieval provenance, rather than a native Ecopath model.'),
        'discovery_verification.json': (
            'context', 'Provenance: recovered-source verification record (JSON)',
            'This file records acquisition verification of documents, URLs, hashes, page counts and attachment checks. '
            'Its qualified_complete_replacement_found flag is a historical discovery assessment, not a model parameter or current adoption verdict.'),
        'source_manifest.json': (
            'context', 'Provenance: original source identities and hashes (JSON)',
            'This manifest identifies six original PDFs, their acquisition URLs, roles, hashes, page counts and earlier paths. '
            'It is a source inventory and exact-byte provenance record, rather than a native Ecopath model.'),
        'source_use.json': (
            'context', 'Provenance: original source-use plan, 2 October 2026 (JSON)',
            'This historical record describes extraction uses and limitations of the source bundle during its unselected candidate stage. '
            'The included model_id and selected=false describe that plan; the file supplies no native Ecopath model and is not the current adopted selection.'),
    }
    assert len(specs) == 12
    manifest = {s['file']: s['sha256'] for s in read(SOURCE / 'source_manifest.json')['sources']}
    translation_hash = read(SOURCE / 'English_translation_work/verification.json')['output_sha256']
    source_hashes = {name: sha(SOURCE / name) for name in specs}
    for name, expected in manifest.items():
        assert source_hashes[name] == expected, ('Original source bytes differ from manifest', name)
    assert source_hashes['gorbatenko_melnikov_2019_English_translation.pdf'] == translation_hash
    for name in specs:
        if name.endswith('.json'):
            content = read(SOURCE / name)
            assert not isinstance(content, dict) or 'group' not in content, ('Unexpected native group payload', name)

    catalog, _ = embedded(ROOT / 'interactive_map/index.html', 'DB')
    article_before = deepcopy(next(a for a in catalog['articles'] if a['article_id'] == ARTICLE_ID))
    proposed = [dict(path=PREFIX + name, sha256=source_hashes[name], role=role, file_label=label, evidence=evidence)
                for name, (role, label, evidence) in specs.items()]
    for item in proposed:
        if item['path'] in previous:
            assert previous[item['path']] == item, 'Conflicting existing keyed role record: ' + item['path']
    after = deepcopy(before)
    after['files'].extend(item for item in proposed if item['path'] not in previous)
    target_paths = {item['path'] for item in proposed}
    old_unrelated = [r for r in before['files'] if r['path'] not in target_paths]
    new_unrelated = [r for r in after['files'] if r['path'] not in target_paths]
    assert old_unrelated == new_unrelated
    assert {k: v for k, v in before.items() if k != 'files'} == {k: v for k, v in after.items() if k != 'files'}
    backup = HERE / ('paper_file_roles.before_' + before_hash[:12] + '.json')
    if backup.exists():
        assert backup.read_bytes() == before_bytes
    else:
        backup.write_bytes(before_bytes)
    assert sha(ROLE_PATH) == before_hash, 'Role metadata changed during guarded preparation'
    temporary = ROLE_PATH.with_name('paper_file_roles.LME052.tmp.json')
    save(temporary, after)
    assert sha(ROLE_PATH) == before_hash, 'Role metadata changed before commit'
    os.replace(temporary, ROLE_PATH)
    assert read(ROLE_PATH) == after

    article_after = deepcopy(article_before)
    reconcile_paper_files(ROOT, [article_after])
    material = {r['filename']: r for r in article_after['material_files']}
    checks = {
        'all_12_files_present_and_hash_guarded': all(material[n]['sha256'] == source_hashes[n] for n in specs),
        'all_12_roles_and_labels_applied_by_standard_reconciler': all(material[n]['role'] == role and material[n]['file_label'] == label for n, (role, label, _) in specs.items()),
        'five_provenance_JSON_are_context': all(material[n]['role'] == 'context' for n in specs if n.endswith('.json')),
        'only_original_2019_PDF_is_main': {n for n, r in material.items() if r['role'] == 'main'} == {'gorbatenko_melnikov_2019.pdf'},
        'no_model_source_files_claimed': not any(r['role'] == 'model' for r in article_after['material_files']),
        'model_file_status_not_found': article_after['model_file_status'] == 'not_found',
        'all_unrelated_role_records_unchanged': old_unrelated == new_unrelated,
        'top_level_role_metadata_unchanged': {k: v for k, v in before.items() if k != 'files'} == {k: v for k, v in after.items() if k != 'files'},
        'source_bytes_unchanged': all(sha(SOURCE / name) == value for name, value in source_hashes.items()),
    }
    changes = [dict(path=item['path'], before=previous.get(item['path']), after=item) for item in proposed if previous.get(item['path']) != item]
    proof = dict(schema_version=1, timestamp_UTC=datetime.now(timezone.utc).isoformat(), article_id=ARTICLE_ID,
                 metadata_path=ROLE_PATH.relative_to(ROOT).as_posix(), before_sha256=before_hash, after_sha256=sha(ROLE_PATH),
                 before_backup=backup.name, before_records=len(before['files']), after_records=len(after['files']),
                 unrelated_preserved_records=len(old_unrelated), changes=changes, checks=checks, passed=all(checks.values()),
                 article_metadata_before=article_before, expected_article_metadata_after=article_after,
                 limits='Updates only keyed paper_file_roles.json and retained integration evidence. The standard reconciler result here is an in-memory preview; root performs map/trends metadata regeneration and scientific-payload preservation checks separately.')
    save(HERE / 'paper_file_role_metadata_proof.json', proof)
    save(HERE / 'paper_file_roles.after_LME052.json', after)
    assert proof['passed'], checks
    print(json.dumps({'passed': proof['passed'], 'added_records': len(changes), 'unrelated_preserved_records': len(old_unrelated), 'after_sha256': proof['after_sha256']}, indent=2))

if __name__ == '__main__':
    main()
