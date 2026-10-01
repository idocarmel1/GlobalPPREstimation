"""Bounded read-only QA of declared article folders and scientific assessments."""
import copy, hashlib, io, json, sys, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
WORK = ROOT / 'original_research_archive/research/selected_regions_validation_20260930/work/source_discovery_final_qa'
OUT = ROOT / 'original_research_archive/research/selected_regions_validation_20260930/verification/source_discovery_final_QA'
OUT.mkdir(parents=True, exist_ok=True)
FIXTURES = WORK / 'fixtures'
FIXTURES.mkdir(parents=True, exist_ok=True)
tempfile.tempdir = str(FIXTURES)
sys.path.insert(0, str(ROOT / 'tools'))
import original_atlas_data as atlas
import openpyxl

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

FILES = ['tools/original_atlas_data.py', 'tools/workflow_checks/test_paper_files.py',
         'common_reference_data/paper_file_roles.json',
         'common_reference_data/provenance/archive_relocation.csv',
         'original_research_archive/migration.csv']
BEFORE = {p: sha(ROOT / p) for p in FILES}
results = []

def probe(name, fn):
    try:
        details = fn()
        results.append({'name': name, 'passed': True, 'details': details})
    except Exception as exc:
        results.append({'name': name, 'passed': False, 'error': repr(exc)})

def actual_java():
    raw = (ROOT / 'Project.xlsx').read_bytes()
    project_hash = hashlib.sha256(raw).hexdigest()
    wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=False)
    try:
        header = None
        papers = []
        in_papers = False
        for row in wb['Papers'].values:
            values = list(row)
            while values and values[-1] is None:
                values.pop()
            if not values:
                continue
            if values[0] == '@table':
                in_papers = values[1] == 'Papers'
                header = None
            elif in_papers and header is None:
                header = values
            elif in_papers:
                papers.append(dict(zip(header, values + [None] * (len(header) - len(values)))))
    finally:
        wb.close()
    original = next(p for p in papers if p['article_id'] == 'INDO-1999__LME_038')
    # The atlas adapter parses embedded file records before path reconciliation.
    for key in ['material_files']:
        if isinstance(original.get(key), str):
            original[key] = json.loads(original[key])
    paper = atlas.SourcePaths(ROOT).rewrite(copy.deepcopy(original))
    assessment = paper.get('loadability_class')
    score = paper.get('quality_score_100')
    atlas.reconcile_paper_files(ROOT, [paper])
    target = '../regions/LME_038/papers/BUCHARY-1991/ubc_1999-0254.pdf.pdf'
    linked = [r for r in paper['material_files'] if r['relative_path'] == target]
    assert len(linked) == 1, paper['material_files']
    assert paper['main_file_status'] == 'local_file_present'
    assert linked[0]['role'] == 'main'
    assert linked[0]['sha256'] == 'eb2c504f176b230153cfd4caa0fc6671e02c5d1cdc0fd2bc0561d3590759f53d'
    assert paper.get('loadability_class') == assessment
    assert paper.get('quality_score_100') == score
    again = copy.deepcopy(paper)
    atlas.reconcile_paper_files(ROOT, [paper])
    assert paper == again
    return {'project_sha256': project_hash, 'paper_records': len(papers),
            'article_id': paper['article_id'], 'source_article_id': paper.get('source_article_id'),
            'article_dir': original.get('article_dir'), 'loadability_class_preserved': assessment,
            'quality_score_preserved': score, 'material_files': paper['material_files'],
            'idempotent': True}

def make_root(tmp):
    root = Path(tmp)
    declared = root / 'regions/LME_038/papers/Buchary'
    declared.mkdir(parents=True)
    (declared / 'thesis.pdf').write_bytes(b'%PDF-focal-thesis')
    return root, declared

def relocated_dedup():
    with tempfile.TemporaryDirectory() as tmp:
        root, declared = make_root(tmp)
        provenance = root / 'common_reference_data/provenance'
        provenance.mkdir(parents=True)
        relative = declared.relative_to(root).as_posix()
        (provenance / 'archive_relocation.csv').write_text(
            'old_path,new_path\nold-thesis-folder,intermediate-thesis-folder\nintermediate-thesis-folder,' + relative + '\n', encoding='utf-8')
        focal = declared / 'thesis.pdf'
        paper = {'article_id': 'INDO-1999__LME_038', 'unit_id': 'LME_038',
                 'source_article_id': 'Buchary', 'article_dir': 'old-thesis-folder',
                 'material_files': [{'relative_path': '../' + focal.relative_to(root).as_posix(),
                                     'role': 'main', 'status': 'downloaded_verified', 'sha256': sha(focal),
                                     'identity_status': 'consistent', 'validation': 'Exact reviewed bytes'}]}
        atlas.reconcile_paper_files(root, [paper])
        assert len(paper['material_files']) == 1
        record = paper['material_files'][0]
        assert record['status'] == 'downloaded_verified'
        assert record['identity_status'] == 'consistent'
        assert record['validation'] == 'Exact reviewed bytes'
        assert paper['main_file_status'] == 'local_file_present'
        prior = copy.deepcopy(paper)
        atlas.reconcile_paper_files(root, [paper])
        assert prior == paper
        return {'two_hop_relocation': True, 'canonical_and_declared_folder_deduplicated': True,
                'existing_link_deduplicated': True, 'exact_identity_retained': True, 'idempotent': True}

def canonical_and_alias_union():
    with tempfile.TemporaryDirectory() as tmp:
        root, declared = make_root(tmp)
        canonical = root / 'regions/LME_038/papers/INDO-1999'
        canonical.mkdir(parents=True)
        (canonical / 'supplement.xlsx').write_bytes(b'original-supplement')
        (declared / 'metadata.json').write_text('{}', encoding='utf-8')
        (declared / 'extracted').mkdir()
        (declared / 'extracted/derived.pdf').write_bytes(b'%PDF-derived')
        paper = {'article_id': 'INDO-1999__LME_038', 'unit_id': 'LME_038',
                 'article_dir': declared.relative_to(root).as_posix()}
        atlas.reconcile_paper_files(root, [paper])
        assert {f['filename'] for f in paper['material_files']} == {'thesis.pdf', 'supplement.xlsx'}
        assert paper['main_file_status'] == paper['supplement_status'] == 'local_file_present'
        return {'distinct_original_files_merged': True, 'administrative_and_nested_derived_excluded': True}

def containment():
    rejected = []
    with tempfile.TemporaryDirectory() as tmp:
        root, declared = make_root(tmp)
        provenance = root / 'common_reference_data/provenance'
        provenance.mkdir(parents=True)
        outside = root.parent / 'not-owned-source-folder'
        (provenance / 'archive_relocation.csv').write_text(
            'old_path,new_path\nrelocated-escape,../not-owned-source-folder\n', encoding='utf-8')
        for value in ['../not-owned-source-folder', str(outside), 'relocated-escape']:
            paper = {'article_id': 'P__LME_038', 'unit_id': 'LME_038', 'article_dir': value}
            before = copy.deepcopy(paper)
            try:
                atlas.reconcile_paper_files(root, [paper])
            except ValueError as exc:
                assert 'outside the repository' in str(exc)
                assert paper == before
                rejected.append(value)
            else:
                raise AssertionError('Escaped article_dir accepted: ' + value)
        paper = {'article_id': 'P__LME_038', 'unit_id': 'LME_038', 'article_dir': str(declared)}
        atlas.reconcile_paper_files(root, [paper])
        assert paper['main_file_status'] == 'local_file_present'
    return {'relative_absolute_and_relocated_escapes_rejected_before_paper_mutation': rejected,
            'absolute_in_repository_folder_allowed': True}

def assessment_matrix():
    cases = []
    with tempfile.TemporaryDirectory() as tmp:
        root, declared = make_root(tmp)
        stale = 'E — no verified downloadable file'
        for label, value, rationale in [
            ('specific_with_stale_rationale', 'Printed source invalid; accepted normalized derived model selected', stale + '. Loadability 0/55; cap 25.'),
            ('none', None, None), ('empty', '', ''),
            ('none_with_stale_rationale', None, stale + '. Historical score 25.'),
            ('specific_without_stale_rationale', 'Strict source fails admission', 'Historical uncertainty retained'),
            ('legacy_availability_only', stale, None),
        ]:
            paper = {'article_id': 'P__LME_038', 'unit_id': 'LME_038', 'article_dir': str(declared),
                     'loadability_class': value, 'quality_rationale': rationale, 'quality_score_100': 25,
                     'download_failure_reason': 'Source access attempt failed; historical retrieval evidence'}
            atlas.reconcile_paper_files(root, [paper])
            assert paper['quality_score_100'] == 25
            assert paper['download_failure_reason'] == 'Source access attempt failed; historical retrieval evidence'
            expected = 'Local sources available; model loadability not reassessed' if value == stale else value
            assert paper['loadability_class'] == expected, label
            if rationale and stale in rationale:
                assert stale not in paper['quality_rationale']
                assert rationale.replace(stale + '. ', '') in paper['quality_rationale']
            else:
                assert paper['quality_rationale'] == rationale
            previous = copy.deepcopy(paper)
            atlas.reconcile_paper_files(root, [paper])
            assert paper == previous
            cases.append({'case': label, 'loadability_class_after': paper['loadability_class'],
                          'quality_rationale_after': paper['quality_rationale'], 'idempotent': True})
        paper = {'article_id': 'P__LME_038', 'unit_id': 'LME_038', 'article_dir': str(declared)}
        atlas.reconcile_paper_files(root, [paper])
        assert 'loadability_class' not in paper and 'quality_rationale' not in paper
        cases.append({'case': 'absent_scientific_fields', 'no_assessment_invented': True})
    return cases

probe('actual_INDO_1999_alias_to_retained_BUCHARY_1991_thesis', actual_java)
probe('two_hop_relocation_and_three_route_same_file_deduplication', relocated_dedup)
probe('distinct_alias_and_canonical_sources_and_exclusions', canonical_and_alias_union)
probe('declared_article_directory_containment', containment)
probe('scientific_assessment_nullability_scores_and_idempotence', assessment_matrix)

suite = unittest.defaultTestLoader.loadTestsFromName('workflow_checks.test_paper_files')
log = io.StringIO()
run = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
(OUT / 'focused_paper_file_tests.txt').write_text(log.getvalue(), encoding='utf-8')
AFTER = {p: sha(ROOT / p) for p in FILES}
output = {'timestamp_utc': datetime.now(timezone.utc).isoformat(),
          'scope': 'Bounded new declared-folder/scientific-assessment delta; no pipeline writer or production writes',
          'source_hashes': BEFORE, 'source_hashes_after': AFTER,
          'reviewed_sources_unchanged_during_run': BEFORE == AFTER,
          'focused_existing_suite': {'tests_run': run.testsRun, 'failures': len(run.failures),
                                    'errors': len(run.errors), 'skipped': len(run.skipped),
                                    'passed': run.wasSuccessful()},
          'independent_probes': results,
          'passed': run.wasSuccessful() and BEFORE == AFTER and all(r['passed'] for r in results)}
(OUT / 'probe_results.json').write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(output, ensure_ascii=False, indent=2))
sys.exit(0 if output['passed'] else 1)
