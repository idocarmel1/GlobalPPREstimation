"""Bounded read-only production review; synthetic fixtures live only here."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[4]
STUDY = EVIDENCE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location('qa_reviewed_metadata', STUDY / 'apply_reviewed_metadata.py')
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)
import original_atlas_data as atlas


def metadata_case(change_during_backup=False):
    with tempfile.TemporaryDirectory(dir=EVIDENCE) as tmp:
        root = Path(tmp)
        original_root, original_here = metadata.ROOT, metadata.HERE
        metadata.ROOT = metadata.HERE = root
        try:
            book = {
                'Papers': {'Papers': (['article_id', 'unit_id', 'title'], [['old', 'LME_035', 'Protected']])},
                'Models & coverage': {'Models': (['unit_id', 'model_id', 'paper_ids'], [['LME_035', 'accepted', None]])},
            }
            project = root / 'Project.xlsx'
            metadata.write_book(project, book)
            handoff = root / 'handoff.json'
            handoff.write_text('{"review": "old accepted evidence"}', encoding='utf-8')
            reviewed_hash = metadata.sha(handoff)
            plan = {'regional_inputs': [{'path': 'handoff.json', 'sha256': reviewed_hash}], 'patches': [],
                    'record_inserts': [{'sheet': 'Papers', 'table': 'Papers',
                                       'key': {'article_id': 'new', 'unit_id': 'LME_035'},
                                       'expected_old': 'record_absent',
                                       'proposed': {'article_id': 'new', 'unit_id': 'LME_035', 'title': 'Reviewed'},
                                       'evidence': 'handoff.json'}]}
            plan_path = root / 'plan.json'
            plan_path.write_text(json.dumps(plan), encoding='utf-8')
            original_copy = metadata.shutil.copy2
            def copy_then_change(*args, **kwargs):
                result = original_copy(*args, **kwargs)
                handoff.write_text('{"review": "new contradictory evidence"}', encoding='utf-8')
                return result
            error = None
            with contextlib.redirect_stdout(io.StringIO()):
                try:
                    with patch.object(metadata.shutil, 'copy2', copy_then_change if change_during_backup else original_copy):
                        metadata.apply(plan_path, True)
                except ValueError as exc:
                    error = str(exc)
            result = metadata.read_book(project)
            return {'rejected': error is not None, 'error': error,
                    'regional_input_changed': metadata.sha(handoff) != reviewed_hash,
                    'new_record_saved': any(row[0] == 'new' for row in result['Papers']['Papers'][1])}
        finally:
            metadata.ROOT, metadata.HERE = original_root, original_here


def context_cases():
    with tempfile.TemporaryDirectory(dir=EVIDENCE) as tmp:
        root = Path(tmp)
        folder = root / 'regions/LME_035/papers/Christensen-1998'
        folder.mkdir(parents=True)
        source = folder / 'related.pdf'
        source.write_bytes(b'%PDF-contextual-publication')
        refs = root / 'common_reference_data'
        refs.mkdir()
        registry = refs / 'paper_file_roles.json'
        item = {'path': source.relative_to(root).as_posix(), 'sha256': atlas.sha(source),
                'role': 'context', 'file_label': 'Reviewed context', 'evidence': 'Reviewed original bytes'}
        registry.write_text(json.dumps({'schema_version': 1, 'files': [item]}), encoding='utf-8')
        existing = {'article_id': 'Christensen-1998__LME_035', 'unit_id': 'LME_035', 'material_files': [
            {'relative_path': '../' + item['path'], 'role': 'main', 'file_label': 'Paper PDF',
             'sha256': item['sha256'], 'status': 'downloaded_verified', 'identity_status': 'consistent'}]}
        shared = {'article_id': 'Christensen-1998__LME_036', 'unit_id': 'LME_036'}
        atlas.reconcile_paper_files(root, [existing, shared])
        original = copy.deepcopy(existing)
        atlas.reconcile_paper_files(root, [existing])
        result = {'existing_main_overridden': existing['material_files'][0]['role'] == 'context',
                  'existing_verified_provenance_retained': existing['material_files'][0]['status'] == 'downloaded_verified',
                  'idempotent': existing == original,
                  'shared_source_role': shared['material_files'][0]['role'],
                  'shared_source_main_file_status': shared['main_file_status']}
        source.write_bytes(b'%PDF-changed-contextual-publication')
        atlas.reconcile_paper_files(root, [existing])
        current = existing['material_files'][0]
        result['stale_existing_role'] = current['role']
        result['stale_existing_main_file_status'] = existing['main_file_status']
        result['stale_role_evidence_removed'] = 'role_evidence' not in current
        result['prior_hash_retained'] = current['prior_file_assessment']['sha256'] == item['sha256']
        source.write_bytes(b'%PDF-contextual-publication')
        relocated = folder / 'renamed-related.pdf'
        source.rename(relocated)
        ledger = refs / 'provenance'
        ledger.mkdir()
        (ledger / 'archive_relocation.csv').write_text('old_path,new_path\n' + item['path'] + ',' + relocated.relative_to(root).as_posix() + '\n', encoding='utf-8')
        paper = {'article_id': 'Christensen-1998__LME_035', 'unit_id': 'LME_035', 'material_files': [
            {'relative_path': '../' + item['path'], 'role': 'main', 'sha256': item['sha256']}]}
        paper = atlas.SourcePaths(root).rewrite(paper)
        atlas.reconcile_paper_files(root, [paper])
        result['relocation_old_manifest_role'] = paper['material_files'][0]['role']
        result['relocation_old_manifest_main_file_status'] = paper['main_file_status']
        return result


def actual_context_cases():
    registry = json.loads((ROOT / 'common_reference_data/paper_file_roles.json').read_text(encoding='utf-8'))
    results = []
    for item in registry['files']:
        source = ROOT / item['path']
        unit = Path(item['path']).parts[1]
        source_id = Path(item['path']).parts[3]
        paper = {'article_id': source_id + '__' + unit, 'unit_id': unit}
        atlas.reconcile_paper_files(ROOT, [paper])
        record = next(r for r in paper['material_files'] if r['relative_path'] == '../' + item['path'])
        results.append({'article_id': paper['article_id'], 'hash_matches_review': atlas.sha(source) == item['sha256'],
                        'role': record['role'], 'main_file_status': paper['main_file_status'],
                        'link_exists': (ROOT / 'interactive_map' / record['relative_path']).is_file(),
                        'file_label': record['file_label']})
    return results


results = {'metadata_baseline': metadata_case(),
           'metadata_handoff_change_during_backup': metadata_case(True),
           'context_role_probes': context_cases(), 'actual_context_files': actual_context_cases()}
(EVIDENCE / 'probe_results.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
print(json.dumps(results, indent=2))
