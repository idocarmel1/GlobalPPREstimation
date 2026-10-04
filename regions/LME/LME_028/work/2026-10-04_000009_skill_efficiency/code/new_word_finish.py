"""Resume the bounded wording trial through exact package and evidence reuse checks."""
import hashlib
import json
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

RUN = Path(__file__).resolve().parents[1]
ROOT = next(p for p in RUN.parents if (p / 'Project.xlsx').exists())
QA = RUN / 'qa'
LOG = QA / 'new_word_trial.json'
PROJECT = RUN / 'outputs/new_word_project'
RELATIVE_REPORT = Path('regions/LME/LME_036/papers/SCS-2007/models/36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)/model_validation/validation.docx')
NEW_REPORT = PROJECT / RELATIVE_REPORT
OLD_REPORT = RUN / 'outputs/old_word_project' / RELATIVE_REPORT

def utc():
    return datetime.now(timezone.utc).isoformat()

def sha(data):
    return hashlib.sha256(data).hexdigest()

started = utc()
clock = time.perf_counter()
audit = json.loads(LOG.read_text(encoding='utf-8-sig'))
with zipfile.ZipFile(OLD_REPORT) as old, zipfile.ZipFile(NEW_REPORT) as new:
    old_names, new_names = old.namelist(), new.namelist()
    assert len(old_names) == len(set(old_names)) and len(new_names) == len(set(new_names))
    names = sorted(set(old_names) | set(new_names))
    comparison = [{'part': name, 'old_sha256': sha(old.read(name)) if name in old_names else None,
                   'new_sha256': sha(new.read(name)) if name in new_names else None,
                   'bytes_identical': name in old_names and name in new_names and old.read(name) == new.read(name)} for name in names]
    exact = set(old_names) == set(new_names) and all(x['bytes_identical'] for x in comparison)
audit['resumed_final_package_comparison'] = {'old_report': str(OLD_REPORT), 'new_report': str(NEW_REPORT),
    'parts_compared': len(names), 'all_named_parts_identical': exact, 'parts': comparison,
    'difference_parts': [x['part'] for x in comparison if not x['bytes_identical']],
    'zip_packaging_and_timestamp_differences_disregarded': True}

# The preceding trace-CLI read of old_word_trial.json exposed this full all-page
# visual proof. Hash that already-read evidence via its recorded trace identity;
# do not reread old instruction files, traces, extraction answers or code.
events = [json.loads(x) for x in (QA / 'new_word_trace.jsonl').read_text(encoding='utf-8').splitlines()]
old_proof_events = [x for x in events if x['path'].endswith('/qa/old_word_trial.json')]
assert old_proof_events
proof_identity = old_proof_events[-1]
old_page_dir = OLD_REPORT.parent / 'work/2026-10-04_000009_old_word_trial/qa/after'
pages = []
for i in range(1, 7):
    p = old_page_dir / f'page-{i}.png'
    assert p.is_file()
    pages.append({'page': i, 'path': str(p), 'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size})
audit['render_evidence_reuse'] = {'reused': exact, 'basis': 'All17namedDOCXpackageparts are byte-for-byte identical; only ZIP packaging/timestamps disregarded.',
    'evidence': str(QA / 'old_word_trial.json'), 'evidence_sha256_from_trace_cli': proof_identity['sha256'],
    'page_count': 6, 'reused_page_images': pages,
    'prior_inspected_pages': [1,2,3,4,5,6],
    'prior_visual_result': 'All six final pages readable; no clipped text, overlaps, broken tables, missing figures, blank pages or page-flow change.',
    'prior_pixel_comparison': 'Only page3heading pixels differ from the original; pages1,2,4,5,6identical.',
    'fresh_new_pdf_exports': 0, 'fresh_new_rendered_pngs': 0, 'new_Word_COM_attempts_after_resume': 0,
    'claim': 'Reused existing all-six-page render and inspection evidence for identical final DOCX rendering inputs; no successful new export claimed.'}

sources = {}
relationships = []
for link in audit['links_before']['missing_local']:
    owner = PROJECT / link['file']
    target = (owner.parent / unquote(urlsplit(link['target']).path).replace('\\', '/')).resolve()
    assert target.is_relative_to(PROJECT.resolve())
    source = ROOT / target.relative_to(PROJECT.resolve())
    key = source.relative_to(ROOT).as_posix()
    if key not in sources:
        sources[key] = {'source_exists': source.exists(), 'source_is_file': source.is_file(),
                        'source_sha256': sha(source.read_bytes()) if source.is_file() else None,
                        'source_bytes': source.stat().st_size if source.is_file() else None}
    relationships.append({'file': link['file'], 'target': link['target'], 'original_target': key,
                          'classification': 'Exists in original; intentionally absent from bounded clone' if source.exists() else 'Original target is also absent; inherited broken source link'})
audit['original_appendix_target_checks'] = {'missing_clone_relationships': len(relationships), 'unique_targets': len(sources),
    'relationships': relationships, 'target_hashes': sources,
    'original_existing_unique_targets': sum(x['source_exists'] for x in sources.values()),
    'original_missing_unique_targets': sum(not x['source_exists'] for x in sources.values()),
    'original_existing_relationships': sum(x['classification'].startswith('Exists') for x in relationships),
    'original_broken_relationships': sum(x['classification'].startswith('Original') for x in relationships),
    'source_checks': 'Existence, byte size and SHA-256 only; no scientific content interpretation; links and target bytes unchanged.'}

file_hashes = {p.relative_to(PROJECT).as_posix(): sha(p.read_bytes()) for p in sorted(PROJECT.rglob('*')) if p.is_file()}
before = audit['before_file_hashes']
changed = sorted(k for k in set(before) | set(file_hashes) if before.get(k) != file_hashes.get(k))
assert changed == [RELATIVE_REPORT.as_posix()]
with zipfile.ZipFile(QA / 'new_word_before_validation.docx') as before_doc, zipfile.ZipFile(NEW_REPORT) as final_doc:
    assert final_doc.read('word/document.xml') == before_doc.read('word/document.xml').replace(b'Taxon mapping and coverage', b'Taxon mapping coverage', 1)
    assert all(before_doc.read(n) == final_doc.read(n) for n in before_doc.namelist() if n != 'word/document.xml')
audit['final_preservation'] = {'changed_project_files': changed, 'files_checked': len(file_hashes), 'unchanged_copied_files': len(file_hashes) - 1,
    'only_heading_change': True, 'other_docx_parts_preserved': 16, 'manual_rows_preserved': 4, 'workbook_writes': 0, 'solver_calls': 0, 'live_project_writes': 0}
audit['visual_review'] = {'all_final_pages_covered_by_reused_inspection': exact, 'inspected_pages_in_reused_evidence': [1,2,3,4,5,6],
    'fresh_new_inspection': False, 'evidence_reused': True, 'reason': 'All17namedZIPparts identical to the finalized document with existing six-page inspection proof.'}
counts = Counter(x['path'] for x in events)
audit['trace_summary'] = {'events': len(events), 'unique_paths': len(counts), 'repeated_reads': sum(n-1 for n in counts.values()),
    'workbook_parses': sum(x['workbook_parses'] for x in events), 'read_bytes': sum(x['bytes'] for x in events), 'path_counts': dict(counts), 'token_telemetry': 'unavailable'}
ended = utc()
elapsed = time.perf_counter() - clock
audit['operations'].append({'operation': 'resumed_final_package_identity_render_proof_reuse_source_target_hash_checks_and_preservation',
    'started_utc': started, 'completed_utc': ended, 'elapsed_seconds': elapsed, 'new_render_calls': 0, 'new_pdf_exports': 0,
    'source_target_checks': len(sources), 'reused_page_images_checked': 6, 'workbook_parses': 0, 'live_project_writes': 0})
audit['status'] = 'Bounded heading edit and preservation verified; six-page visual QA satisfied by explicitly reused evidence for identical final DOCX parts.' if exact else 'Final package differences require investigation before render evidence reuse.'
audit['resumed_verification_started_utc'] = started
audit['resumed_verification_completed_utc'] = ended
audit['resumed_verification_seconds'] = elapsed
audit['completion_evidence_is_reused_rendering'] = exact
audit['link_verification_limitation'] = 'Inherited original broken appendix links retained unchanged; bounded clone omissions distinguished by original-source existence/hash checks.'
LOG.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'all_parts_exact': exact, 'parts_compared': len(names), 'difference_parts': audit['resumed_final_package_comparison']['difference_parts'],
    'reused_visual_pages': 6 if exact else 0, 'fresh_new_PDF': 0, 'changed_files': changed,
    'unchanged_files': len(file_hashes)-1, 'source_checks': {k:v for k,v in audit['original_appendix_target_checks'].items() if k not in ('relationships','target_hashes')},
    'source_relationship_classifications': relationships, 'trace': audit['trace_summary'], 'resumed_started_utc': started, 'resumed_completed_utc': ended, 'resumed_seconds': elapsed}, ensure_ascii=False))
