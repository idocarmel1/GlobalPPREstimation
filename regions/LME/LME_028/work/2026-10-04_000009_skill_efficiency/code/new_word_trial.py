"""Bounded isolated wording edit and binary preservation/render audit."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as E

RUN = Path(__file__).resolve().parents[1]
PROJECT = RUN / 'outputs/new_word_project'
MODEL = PROJECT / 'regions/LME/LME_036/papers/SCS-2007/models/36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)'
REPORT = MODEL / 'model_validation/validation.docx'
QA = RUN / 'qa'
LOG = QA / 'new_word_trial.json'
BASELINE = QA / 'new_word_before_validation.docx'
OLD = b'Taxon mapping and coverage'
NEW = b'Taxon mapping coverage'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
BUNDLE = Path('C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies')
PYTHON = BUNDLE / 'python/python.exe'
RENDERER = Path('C:/Users/idoca/.codex/plugins/cache/openai-primary-runtime/documents/26.915.20218/skills/documents/render_docx.py')

def utc():
    return datetime.now(timezone.utc).isoformat()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(data):
    LOG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def load():
    return json.loads(LOG.read_text(encoding='utf-8-sig'))

def hashes():
    return {p.relative_to(PROJECT).as_posix(): sha(p.read_bytes()) for p in sorted(PROJECT.rglob('*')) if p.is_file()}

def inventory(archive):
    xml = E.fromstring(archive.read('word/document.xml'))
    manual = {}
    for tr in xml.iter(W + 'tr'):
        cells = tr.findall(W + 'tc')
        if not cells:
            continue
        label = ''.join(cells[0].itertext()).strip()
        if label in ('SPPR calculation', 'Open issues and next action', 'Review and reproducibility', 'Selection rationale'):
            manual[label] = sha(E.tostring(tr))
    headings = [E.tostring(p, encoding='unicode') for p in xml.iter(W + 'p') if ''.join(p.itertext()).strip() == OLD.decode()]
    return {'part_hashes': {i.filename: sha(archive.read(i.filename)) for i in archive.infolist()},
            'part_count': len(archive.infolist()), 'manual_row_hashes': manual,
            'break_counts': {name: len(list(xml.iter(W + name))) for name in ('br', 'cr', 'tab')},
            'heading_xml': headings, 'table_count': len(list(xml.iter(W + 'tbl'))),
            'paragraph_count': len(list(xml.iter(W + 'p')))}

def link_check():
    links = []
    bases = []
    fields = []
    for p in sorted(PROJECT.rglob('*')):
        if p.suffix not in ('.docx', '.xlsx'):
            continue
        with zipfile.ZipFile(p) as z:
            for name in z.namelist():
                if name.endswith('.rels'):
                    for rel in E.fromstring(z.read(name)):
                        if rel.get('Type', '').endswith('/hyperlink'):
                            target = rel.get('Target', '')
                            u = urlsplit(target)
                            remote = u.scheme.lower() in ('http', 'https', 'mailto')
                            local = not u.scheme and not u.netloc
                            resolved = (p.parent / unquote(u.path).replace('\\', '/')).resolve() if local and u.path else None
                            links.append({'file': p.relative_to(PROJECT).as_posix(), 'part': name,
                                          'id': rel.get('Id'), 'target': target, 'remote': remote,
                                          'relative_local': local, 'exists': resolved.exists() if resolved else None,
                                          'inside_isolated_project': resolved.is_relative_to(PROJECT.resolve()) if resolved else None})
                if name.endswith('.xml'):
                    tree = E.fromstring(z.read(name))
                    for node in tree.iter():
                        tag = node.tag.rsplit('}', 1)[-1]
                        if tag == 'HyperlinkBase':
                            bases.append({'file': p.relative_to(PROJECT).as_posix(), 'value': node.text})
                        if tag in ('instrText', 'f') and node.text and 'HYPERLINK' in node.text.upper():
                            fields.append({'file': p.relative_to(PROJECT).as_posix(), 'value': node.text})
    return {'relationships': links, 'hyperlink_bases': bases, 'hyperlink_fields_or_formulas': fields,
            'local_count': sum(x['relative_local'] for x in links),
            'remote_count': sum(x['remote'] for x in links),
            'missing_local': [x for x in links if x['relative_local'] and x['exists'] is False],
            'nonportable': [x for x in links if not x['remote'] and not x['relative_local']]}

def prepare():
    first = RUN / 'qa/new_word_trace.jsonl'
    data = {'task': 'Change only the named heading in the isolated revised-skill trial',
            'trace_created_utc': datetime.fromtimestamp(first.stat().st_ctime, timezone.utc).isoformat(),
            'binary_work_started_utc': utc(), 'report': str(REPORT),
            'baseline': str(BASELINE), 'source_sha256': sha(REPORT.read_bytes()),
            'environment_knowledge_reused': 'Parent supplied verified renderer capability: packaged renderer cannot locate soffice, bundled Python lacks fitz, native Poppler exists, Word COM fallback requires independent hidden Windows PowerShell 5.1 instance. Renderer discovery savings cannot be attributed to skill routing.',
            'operations': [], 'before_file_hashes': hashes()}
    shutil.copyfile(REPORT, BASELINE)
    with zipfile.ZipFile(REPORT) as z:
        data['before_package'] = inventory(z)
        assert len(data['before_package']['heading_xml']) == 1
        assert z.read('word/document.xml').count(OLD) == 1
    data['links_before'] = link_check()
    data['operations'].append({'operation': 'prepare_binary_baseline_and_preservation_inventory', 'utc': utc(), 'docx_copies': 1, 'workbook_parses': 0})
    save(data)
    print(json.dumps({'baseline_created': True, 'parts': data['before_package']['part_count'], 'files': len(data['before_file_hashes']), 'local_links': data['links_before']['local_count'], 'missing_links': len(data['links_before']['missing_local'])}))

def edit():
    data = load()
    start = time.perf_counter()
    staged = QA / 'new_word_validation_staged.docx'
    with zipfile.ZipFile(BASELINE) as src, zipfile.ZipFile(staged, 'w') as out:
        out.comment = src.comment
        for info in src.infolist():
            content = src.read(info.filename)
            if info.filename == 'word/document.xml':
                assert content.count(OLD) == 1
                content = content.replace(OLD, NEW, 1)
            out.writestr(info, content)
    shutil.copyfile(staged, REPORT)
    staged.unlink()
    with zipfile.ZipFile(BASELINE) as before, zipfile.ZipFile(REPORT) as after:
        assert before.namelist() == after.namelist()
        changed = [name for name in before.namelist() if before.read(name) != after.read(name)]
        assert changed == ['word/document.xml']
        assert after.read('word/document.xml') == before.read('word/document.xml').replace(OLD, NEW, 1)
        assert after.read('word/document.xml').count(OLD) == 0
        assert after.read('word/document.xml').count(NEW) == 1
        after_inv = inventory(after)
    assert data['before_package']['manual_row_hashes'] == after_inv['manual_row_hashes']
    assert data['before_package']['break_counts'] == after_inv['break_counts']
    data['after_package'] = after_inv
    data['changed_package_parts'] = changed
    data['operations'].append({'operation': 'minimal_OOXML_heading_replacement_and_package_verification', 'utc': utc(), 'elapsed_seconds': time.perf_counter() - start, 'docx_writes': 1, 'workbook_writes': 0, 'solver_calls': 0})
    data['exact_only_heading_change'] = True
    data['artifact_marker'] = {'operation_kind': 'edit', 'expected_output_count': 1, 'output_format': 'docx', 'successful_invocations': 1, 'timing': 'immediately before edit command'}
    save(data)
    print(json.dumps({'changed_parts': changed, 'manual_rows_preserved': len(after_inv['manual_row_hashes']), 'breaks': after_inv['break_counts'], 'paragraphs': after_inv['paragraph_count'], 'tables': after_inv['table_count']}))

def packaged():
    data = load()
    start = time.perf_counter()
    started = utc()
    result = subprocess.run([str(PYTHON), str(RENDERER), str(REPORT), '--output_dir', str(QA / 'new_word_packaged_render'), '--emit_pdf', '--verbose'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    op = {'operation': 'packaged_renderer', 'started_utc': started, 'elapsed_seconds': time.perf_counter() - start, 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr, 'render_calls': 1}
    data['operations'].append(op)
    save(data)
    print(json.dumps(op, ensure_ascii=False))

def percentage():
    data = load()
    start = time.perf_counter()
    checker = next(p for p in RUN.parents if (p / 'Project.xlsx').exists()) / 'tools/project_core/validation/validation_percentage_format.py'
    result = subprocess.run([str(PYTHON), str(checker), '--check', str(REPORT)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    op = {'operation': 'percentage_format_read_only_check', 'utc': utc(), 'elapsed_seconds': time.perf_counter() - start, 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr, 'docx_writes': 0}
    data['operations'].append(op)
    save(data)
    print(json.dumps(op, ensure_ascii=False))

def record_abort():
    data = load()
    completed = utc()
    started = '2026-10-04T05:53:46.989017+00:00'
    data['operations'].append({'operation': 'independent_hidden_Word_COM_render_blocked_and_stopped', 'helper_created_utc': started, 'cleanup_completed_utc': completed, 'observed_helper_lifetime_seconds': (datetime.fromisoformat(completed) - datetime.fromisoformat(started)).total_seconds(), 'before_pids': [21788,34812], 'owned_pid': 11488, 'surviving_prior_pids': [21788,34812], 'owned_helper_pid': 26528, 'word_and_helper_stopped': True, 'pdf_exports_completed': 0, 'error': 'Direct Unicode workspace path COM operation blocked without PDF. Retry uses short ASCII TEMP copies. Only owned Word11488 and uniquely identified helper26528 were stopped.', 'render_calls': 0, 'environment_retry': True})
    data['operations'].append({'operation': 'cleanup_proven_first_orphan_final_check', 'utc': completed, 'owned_orphan_pid': 17616, 'terminated': True, 'surviving_prior_pids': [21788,34812]})
    save(data)
    print(json.dumps(data['operations'][-2]))

def record_stop():
    data = load()
    stopped = '2026-10-04T06:03:01.9906908+00:00'
    temp = Path('C:/Users/idoca/AppData/Local/Temp/new_word_trial_b6b8fe7a735d42858a294d234aaffbf1')
    proxy_start = datetime.fromtimestamp(temp.stat().st_ctime, timezone.utc).isoformat()
    trace = [json.loads(x) for x in (QA / 'new_word_trace.jsonl').read_text(encoding='utf-8').splitlines()]
    counts = Counter(x['path'] for x in trace)
    data['trace_summary'] = {'events': len(trace), 'unique_paths': len(counts), 'repeated_reads': sum(n - 1 for n in counts.values()), 'workbook_parses': sum(x['workbook_parses'] for x in trace), 'read_bytes': sum(x['bytes'] for x in trace), 'path_counts': dict(counts), 'token_telemetry': 'unavailable', 'context': 'cold instruction/evidence reads; verified renderer capability environmental knowledge reused; extra failed render setup is not routing savings'}
    data['operations'].append({'operation': 'user_requested_safe_stop_of_blocked_ASCII_TEMP_export', 'attempt_directory_created_utc': proxy_start, 'stopped_utc': stopped, 'timing_basis': 'Temporary directory creation is a start proxy; the blocked helper did not flush its render stopwatch', 'observed_attempt_seconds_to_stop': (datetime.fromisoformat(stopped) - datetime.fromisoformat(proxy_start)).total_seconds(), 'before_pids': [21788,34812], 'proven_owned_word_pid': 12620, 'proven_owned_helper_pid': 6540, 'word_and_helper_stopped': True, 'surviving_word_pids': [21788,34812], 'prior_sessions_preserved': True, 'last_observed_stage': 'before.docx opened read-only; ExportAsFixedFormat(before.pdf,17) pending', 'pdf_exports_completed': 0, 'render_calls': 0, 'temporary_copies_preserved': str(temp), 'environment_retry': True})
    data['status'] = 'Stopped safely at user request; single heading edit preserved; all-page render/visual verification incomplete'
    data['visual_review'] = {'all_final_pages_inspected': False, 'inspected_final_pages': [], 'reason': 'No PDF/page images completed before the user requested stopping'}
    data['stopped_utc'] = stopped
    data['qa_updated_utc'] = utc()
    data['wall_seconds_trace_creation_to_stop'] = (datetime.fromisoformat(stopped) - datetime.fromisoformat(data['trace_created_utc'])).total_seconds()
    data['rendering_time_note'] = 'Packaged failure 0.289s; Hwnd failure 2.178s; first blocked helper observed lifetime315.011s; final blocked attempt measured from temporary-directory creation proxy to safe stop. Escalation/wait/debug overhead also exists. These environmental retries must not be attributed to revised-skill reading efficiency.'
    data['link_verification_partial'] = {'report_relationships': 36, 'report_local_targets_resolved_in_baseline': True, 'all_stored_targets_preserved_by_exact_package_part_comparison': True, 'appendix_relationships_missing_in_bounded_clone': 15, 'original_target_existence_hash_check': 'not performed before user stop; source-broken versus intentionally uncopied not yet distinguished'}
    save(data)
    print(json.dumps({'status': data['status'], 'trace': data['trace_summary'], 'trace_started_utc': data['trace_created_utc'], 'stopped_utc': stopped, 'wall_seconds': data['wall_seconds_trace_creation_to_stop'], 'last_attempt_proxy_seconds': data['operations'][-1]['observed_attempt_seconds_to_stop']}, ensure_ascii=False))

def raster():
    data = load()
    start = time.perf_counter()
    started = utc()
    poppler = BUNDLE / 'native/poppler/Library/bin'
    rendered = []
    results = []
    for name in ('before', 'final'):
        pdf = QA / 'new_word_render' / (name + '.pdf')
        prefix = QA / 'new_word_render' / name
        result = subprocess.run([str(poppler / 'pdftoppm.exe'), '-r', '150', '-png', str(pdf), str(prefix)], capture_output=True, text=True, encoding='utf-8', errors='replace')
        results.append({'name': name, 'returncode': result.returncode, 'stderr': result.stderr})
        assert result.returncode == 0
        info = subprocess.run([str(poppler / 'pdfinfo.exe'), str(pdf)], capture_output=True, text=True, encoding='utf-8', errors='replace')
        assert info.returncode == 0
        count = int(re.search(r'^Pages:\s+(\d+)', info.stdout, re.M).group(1))
        pages = sorted(prefix.parent.glob(name + '-*.png'))
        assert len(pages) == count
        rendered.append({'name': name, 'page_count': count, 'pages': [str(p) for p in pages], 'pdf_bytes': pdf.stat().st_size})
    from PIL import Image, ImageChops
    assert rendered[0]['page_count'] == rendered[1]['page_count']
    differences = []
    for i, (before, final) in enumerate(zip(rendered[0]['pages'], rendered[1]['pages']), 1):
        with Image.open(before) as a, Image.open(final) as b:
            assert a.size == b.size
            bbox = ImageChops.difference(a.convert('RGB'), b.convert('RGB')).getbbox()
            differences.append({'page': i, 'dimensions': a.size, 'difference_bbox': bbox, 'pixels_identical': bbox is None})
    data['rendered_pages'] = rendered
    data['page_pixel_comparison'] = differences
    data['operations'].append({'operation': 'bundled_Poppler_rasterize_and_baseline_pixel_compare', 'started_utc': started, 'elapsed_seconds': time.perf_counter() - start, 'dpi': 150, 'raster_calls': 2, 'results': results})
    save(data)
    print(json.dumps({'rendered': rendered, 'pixel_comparison': differences}, ensure_ascii=False))

def inspect_done():
    data = load()
    pages = next(x for x in data['rendered_pages'] if x['name'] == 'final')['page_count']
    changed_pages = [x['page'] for x in data['page_pixel_comparison'] if not x['pixels_identical']]
    data['visual_review'] = {'inspected_final_pages': list(range(1, pages + 1)), 'all_final_pages_inspected': True, 'inspection_method': 'view_image original images at native 150 dpi resolution', 'new_clipping_overlap_missing_glyphs_blank_pages': False, 'baseline_layout_preserved': True, 'pixel_changed_pages': changed_pages, 'notes': 'Every page inspected; changed pixels confined to the named heading. Existing page structure and scientific content preserved.'}
    data['operations'].append({'operation': 'all_final_page_visual_inspection', 'utc': utc(), 'page_image_views': pages})
    save(data)
    print(json.dumps(data['visual_review']))

def verify():
    data = load()
    after = hashes()
    keys = set(data['before_file_hashes']) | set(after)
    changed = sorted(k for k in keys if data['before_file_hashes'].get(k) != after.get(k))
    assert changed == [REPORT.relative_to(PROJECT).as_posix()]
    data['after_file_hashes'] = after
    data['changed_isolated_files'] = changed
    data['links_after'] = link_check()
    assert data['links_before'] == data['links_after']
    data['link_verification_limitation'] = '15 inherited appendix link relationships target files absent from the supplied isolated copy; all report-local links resolve and all stored targets remain exact.' if data['links_after']['missing_local'] else None
    assert not [x for x in data['links_after']['missing_local'] if x['file'].endswith('.docx')]
    assert not data['links_after']['nonportable']
    source_root = next(p for p in RUN.parents if (p / 'Project.xlsx').exists())
    missing_sources = {}
    for rel in data['links_after']['missing_local']:
        owner = PROJECT / rel['file']
        target = (owner.parent / unquote(urlsplit(rel['target']).path).replace('\\', '/')).resolve()
        assert target.is_relative_to(PROJECT.resolve())
        source = source_root / target.relative_to(PROJECT.resolve())
        source_key = source.relative_to(source_root).as_posix()
        missing_sources[source_key] = {'source_exists': source.exists(), 'source_sha256': sha(source.read_bytes()) if source.is_file() else None, 'source_bytes': source.stat().st_size if source.is_file() else None}
    data['missing_clone_targets_source_hash_checks'] = missing_sources
    data['report_link_counts'] = {'local': sum(x['relative_local'] and x['file'].endswith('.docx') for x in data['links_after']['relationships']), 'remote': sum(x['remote'] and x['file'].endswith('.docx') for x in data['links_after']['relationships']), 'missing_local': sum(x['file'].endswith('.docx') for x in data['links_after']['missing_local'])}
    data['operations'].append({'operation': 'original_targets_existence_and_hash_check_only', 'utc': utc(), 'unique_missing_clone_targets': len(missing_sources), 'source_targets_existing': sum(x['source_exists'] for x in missing_sources.values()), 'source_targets_missing': sum(not x['source_exists'] for x in missing_sources.values()), 'scientific_content_reads': 0})
    with zipfile.ZipFile(BASELINE) as before, zipfile.ZipFile(REPORT) as final:
        assert final.read('word/document.xml') == before.read('word/document.xml').replace(OLD, NEW, 1)
        assert all(final.read(n) == before.read(n) for n in before.namelist() if n != 'word/document.xml')
    trace = [json.loads(x) for x in (QA / 'new_word_trace.jsonl').read_text(encoding='utf-8').splitlines()]
    counts = Counter(x['path'] for x in trace)
    data['trace_summary'] = {'events': len(trace), 'unique_paths': len(counts), 'repeated_reads': sum(n - 1 for n in counts.values()), 'workbook_parses': sum(x['workbook_parses'] for x in trace), 'read_bytes': sum(x['bytes'] for x in trace), 'path_counts': dict(counts), 'token_telemetry': 'unavailable', 'context': 'cold instruction/evidence reads; renderer capability environmental knowledge reused'}
    data['operations'].append({'operation': 'final_binary_preservation_and_link_verification', 'utc': utc(), 'files_checked': len(after), 'unchanged_files': len(after) - 1, 'workbook_writes': 0, 'project_writes': 0})
    data['completed_utc'] = utc()
    data['trace_wall_seconds'] = (datetime.fromisoformat(data['completed_utc']) - datetime.fromisoformat(data['trace_created_utc'])).total_seconds()
    save(data)
    print(json.dumps({'changed_files': changed, 'unchanged_files': len(after) - 1, 'local_links_exist': data['links_after']['local_count'], 'trace': data['trace_summary'], 'completed_utc': data['completed_utc'], 'wall_seconds': data['trace_wall_seconds']}, ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['prepare', 'edit', 'packaged', 'percentage', 'record_abort', 'record_stop', 'raster', 'inspect_done', 'verify'])
    args = parser.parse_args()
    globals()[args.operation]()
