"""Publish only the authorized LME003/014/037 retained packages.

Default/--preflight verifies packages and rehearses registration on an isolated
Project copy. --publish is the only production entry point. Neither route may
inventory methods, construct models, solve scientific methods or generate MC.
"""
from __future__ import annotations
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import time
import traceback

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
RUN = SCRIPT.parents[1]
ROOT = next(p for p in SCRIPT.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
PROJECT = ROOT / 'Project.xlsx'
BASELINE = RUN / 'inputs/Project_before_batch_2_registration.xlsx'
BASELINE_SHA = '9a3951c5e4342c3b8cc0ab2c0feccff9962aac3f91daf600e7a18a38e4c2e06b'
CURRENT_SHA = 'c9fb86a34119987348e7a4e89536cd154209ee8d7fc8769a8e1791c3db48ef9c'
ORDER = ('LME_003', 'LME_014', 'LME_037')
REGISTER = ('LME_014', 'LME_037')
PRIOR = ('HS_071', 'EEZ_598', 'EEZ_941', 'LME_038', 'LME_049', 'LME_050')
MODEL_PATHS = {
    'LME_003': 'regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014',
    'LME_014': 'regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native',
    'LME_037': 'regions/LME/LME_037/papers/LME037-Bacalso-2026/models/Bacalso2026_Visayan_Sea_1997_baseline',
}
MODELS = {u: ROOT / path for u, path in MODEL_PATHS.items()}
MIDS = {u: p.name for u, p in MODELS.items()}
REGIONS = {u: ROOT / f'regions/LME/{u}/{u}.xlsx' for u in ORDER}
REPORTS = {u: p / 'model_validation/validation.docx' for u, p in MODELS.items()}
WORK = {
    'LME_003': MODELS['LME_003'] / 'model_validation/work/2026-11-14_193900_retained_adoption',
    'LME_014': MODELS['LME_014'] / 'model_validation/work/2026-11-14_193100_retained_adoption',
    'LME_037': MODELS['LME_037'] / 'model_validation/work/2026-11-14_220000_configuration_compatibility',
}
SPECS = {
    'LME_003': ('code/retained_package.py', '50065e2390839f282070bf99248db9691234b4b01b3f141bdc6f3a70b823f597',
                'outputs/current_adoption_final/preparation.json', '9e59e6a4a9977219d569adcdc6af5963ab735b05b6fe4e15ed10cacb00545840'),
    'LME_014': ('code/adopt_retained.py', 'a645be60166bf5d04194593f3631c9e3f866050ab5e7bb84d4859e2e4f87b740',
                'outputs/retained_package_v2/preparation.json', '8784349c0283464f2eee5d5997e024491c1342e31871e85d7cc050720dae1569'),
    'LME_037': ('code/retained_metadata.py', '1d0f97bf329b4f6b268fd2d117ed755c262bc93848ce2731ee7d11900caac999',
                'outputs/preparation.json', 'bd72bf0d56bce05d27dae293a4c4214ee294cceb3d4fbfb27844d1b657523d54'),
}
INPUT_PINS = {
    'authorized_scope.json': 'fe419cfd21a3c16fba2fd51d343f80b673413b9f9dc91ee8d7715ebe0de8b11d',
    'display_exclusions.json': 'bcda684ada192cd50e1f1e2cbf0b7000b8ac29190e5c5cca3c66ab7b0db58a32',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(path):
    return sha(path) if Path(path).is_file() else None


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str, allow_nan=False) + '\n', encoding='utf-8')


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


class Progress:
    def __init__(self, publish):
        self.start = time.monotonic()
        self.path = RUN / ('qa/combined_publication.json' if publish else 'qa/combined_preflight.json')
        self.data = {'mode': 'publish' if publish else 'preflight', 'passed': False,
                     'units': list(ORDER), 'registration_order': list(REGISTER),
                     'excluded_pending_units': ['LME_026'], 'scientific_runs': 0,
                     'new_MC_draws': 0, 'script_sha256': sha(SCRIPT), 'stages': []}

    def step(self, name, action):
        item = {'stage': name, 'started_utc': datetime.now(timezone.utc).isoformat(),
                'elapsed_seconds': round(time.monotonic() - self.start, 3), 'status': 'running'}
        self.data['stages'].append(item)
        print(f"[{item['started_utc']} +{item['elapsed_seconds']:.3f}s] {name}", flush=True)
        write(self.path, self.data)
        begun = time.monotonic()
        try:
            result = action()
        except Exception as error:
            item.update(status='failed', error_type=type(error).__name__, error=str(error))
            self.data['failure_stage'] = name
            raise
        else:
            item['status'] = 'passed'
            return result
        finally:
            item['duration_seconds'] = round(time.monotonic() - begun, 3)
            write(self.path, self.data)

    def finish(self, **values):
        self.data.update(values, timestamp_utc=datetime.now(timezone.utc).isoformat(),
                         elapsed_seconds=round(time.monotonic() - self.start, 3))
        write(self.path, self.data)


def central_rows(project):
    from tools.project_core.validation.researcher_review import table_rows
    with ZipFile(project) as archive:
        return {(r['unit_id'], r['model_id']): r for _, r in table_rows(archive, 'Models & coverage', 'Models')[3]}


def page_state():
    result = {}
    for name, variable in (('index.html', 'DB'), ('trends.html', 'SERIES_DB')):
        path = ROOT / 'interactive_map' / name
        page = path.read_text(encoding='utf-8')
        mark = re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">', page)
        require(mark is not None, 'Page has no Project fingerprint: ' + name)
        start = page.index('const ' + variable + '=') + len('const ' + variable + '=')
        payload, _ = json.JSONDecoder().raw_decode(page, start)
        units = payload['network']['units'] if variable == 'DB' else payload['units']
        result[name] = {'sha256': sha(path), 'project_sha256': mark.group(1), 'units': units, 'variable': variable}
    return result


def default_id(page, unit):
    value = page['units'][unit]
    return value['models'][value['default_model']]['id'] if page['variable'] == 'DB' else value['default_model']


def review_state(page, unit):
    fields = ('researcher_review', 'display_ppr_excluded_group_ids', 'recorded_review_pending')
    return {'default_model': default_id(page, unit), 'models': {
        m['id']: {k: copy.deepcopy(m[k]) for k in fields if k in m}
        for m in page['units'][unit]['models']}}


def check_sources(expected):
    for path, digest in expected.items():
        require(fingerprint(path) == digest, 'Protected source changed: ' + relative(path))


def initialize():
    from tools.project_core.validation.researcher_review import read_report, FIELDS
    from tools.project_core.validation.validation_percentage_format import verify_report
    from tools.project_core.workbooks.workbooks import read_book, overview
    from tools.project_core.calculations.coverage import _preserved_inputs
    from tools.project_core.registry.discovery import resolve_model, region_directory
    for name, digest in INPUT_PINS.items():
        require(sha(RUN / 'inputs' / name) == digest, 'Authorization input changed: ' + name)
    authority = read(RUN / 'inputs/authorized_scope.json')
    exclusions = read(RUN / 'inputs/display_exclusions.json')
    require(set(authority['units']) == set(ORDER) and authority['scientific_execution_authorized_for_this_batch'] is False,
            'Authorization scope differs from retained-only batch')
    require(sha(BASELINE) == BASELINE_SHA and sha(PROJECT) == CURRENT_SHA, 'Project baseline/current identity changed')
    pages = page_state()
    require(all(p['project_sha256'] == BASELINE_SHA for p in pages.values()), 'Pages are not the reviewed pre-batch baseline')
    rows = central_rows(PROJECT)
    source_paths = {SCRIPT, BASELINE, *(RUN / 'inputs' / n for n in INPUT_PINS)}
    protected, selection, staged_books = {}, {}, {}
    for unit in ORDER:
        auth = authority['units'][unit]
        require(auth['model_id'] == MIDS[unit], 'Authorized model differs: ' + unit)
        require(resolve_model(REGIONS[unit].parent, MIDS[unit]).parent == MODELS[unit], 'Canonical discovery differs: ' + unit)
        require(sha(REPORTS[unit]) == auth['report_sha256'], 'Signed report changed: ' + unit)
        require(sha(MODELS[unit] / 'model.json') == auth['canonical_sha256'], 'Canonical model changed: ' + unit)
        name, date, summary = read_report(ROOT, REPORTS[unit], MIDS[unit])
        require(summary.get('status', 'Validated by researcher') == 'Validated by researcher', 'Unexpected decision: ' + unit)
        verify_report(REPORTS[unit])
        source_paths.update((REPORTS[unit], MODELS[unit] / 'model.json', MODELS[unit] / 'model_validation/taxon_mapping.xlsx'))
        book = read_book(REGIONS[unit]); settings = overview(book)
        require(settings['selected_model_id'] == settings['results_model_id'] == MIDS[unit], 'Selected/results model differs: ' + unit)
        protected[unit] = _preserved_inputs(book)
        selection[unit] = {key: settings.get(key) for key in ('selected_model_id', 'results_model_id', 'selection_rationale', 'model_path')}
        staged_books[unit] = book if unit == 'LME_037' else None
    require(sha(REGIONS['LME_037']) == authority['units']['LME_037']['regional_and_snapshot_sha256'], 'LME037 adopted workbook changed')
    prior_rows = {key: {f: r.get(f) for f in (*FIELDS, 'selected', 'selection_rationale')}
                  for key, r in rows.items() if key[0] in PRIOR}
    prior_regions = {}
    for unit in PRIOR:
        old_id = default_id(pages['index.html'], unit)
        require(default_id(pages['trends.html'], unit) == old_id, 'Prior page selections disagree: ' + unit)
        row = rows[(unit, old_id)]
        source_paths.update((ROOT / row['validation_report_path'], ROOT / row['model_path']))
        require(sha(ROOT / row['validation_report_path']) == row['validation_report_sha256'], 'Prior signed report changed: ' + unit)
        require(sha(ROOT / row['model_path']) == row['reviewed_model_sha256'], 'Prior reviewed model changed: ' + unit)
        prior_regions[unit] = region_directory(ROOT, unit) / (unit + '.xlsx')
        source_paths.add(prior_regions[unit])
        for page in pages.values():
            selected = next(m for m in page['units'][unit]['models'] if m['id'] == old_id)
            require(selected.get('display_ppr_excluded_group_ids', []) == exclusions[unit], 'Prior exclusions differ: ' + unit)
    # These hashes bind current publication machinery, not historical engines.
    source_paths.update(ROOT / 'tools/project_core' / name for name in (
        'validation/researcher_review.py', 'maps/build_html.py', 'maps/original_atlas_data.py',
        'registry/update_project.py', 'registry/publication.py', 'registry/writes.py'))
    return {'authority': authority, 'exclusions': exclusions, 'pages': pages, 'central_before': rows,
            'prior_rows': prior_rows, 'sources': {p: fingerprint(p) for p in source_paths},
            'protected': protected, 'selection': selection, 'staged_books': staged_books}


def verify_packages(progress):
    packages, targets = {}, {}
    for unit in ORDER:
        script, script_sha, plan_name, plan_sha = SPECS[unit]
        source, path = WORK[unit] / script, WORK[unit] / plan_name
        progress.step('authenticate frozen wrapper and plan ' + unit, lambda s=source, p=path, a=script_sha, b=plan_sha, u=unit:
            require(sha(s) == a and sha(p) == b, 'Frozen package identity changed: ' + u))
        spec = importlib.util.spec_from_file_location('batch2_' + unit, source)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        verify = module.verify_package if unit == 'LME_037' else lambda m=module, p=path.parent: m.verify_package(p)
        plan = progress.step('verify retained package ' + unit, verify)
        require(plan == read(path), 'Verifier returned a different preparation: ' + unit)
        require(sha(source) == script_sha and sha(path) == plan_sha, 'Package changed during verification: ' + unit)
        promotions = []
        for item in plan['promotions']:
            src = ((ROOT if unit == 'LME_037' else path.parent) / item['source']).resolve()
            target = (ROOT / item['target']).resolve()
            require(src.is_relative_to(ROOT) and target.is_relative_to(ROOT), 'Package path outside project')
            require(target not in targets, 'Overlapping package promotion: ' + relative(target))
            targets[target] = unit
            require(sha(src) == item['sha256'], 'Staged promotion changed: ' + relative(src))
            promotions.append((src, target, item['sha256']))
        packages[unit] = {'module': module, 'directory': path.parent, 'plan_path': path,
                          'plan': plan, 'promotions': promotions}
    for unit, package in packages.items():
        for name in package['plan']['consumed_inputs']:
            target = (ROOT / name).resolve()
            require(target not in targets or targets[target] == unit, 'Cross-package target/input overlap: ' + name)
    return packages


def check_package_inputs(packages, *, installed=False):
    all_targets = {target for p in packages.values() for _, target, _ in p['promotions']}
    for unit, package in packages.items():
        script, script_sha, _, plan_sha = SPECS[unit]
        require(sha(WORK[unit] / script) == script_sha and sha(package['plan_path']) == plan_sha, 'Frozen package changed: ' + unit)
        for name, digest in package['plan']['consumed_inputs'].items():
            path = (ROOT / name).resolve()
            if installed and path in all_targets:
                continue
            require(fingerprint(path) == digest, 'Consumed package input changed: ' + name)
        for source, target, digest in package['promotions']:
            require(sha(source) == digest, 'Staged output changed: ' + relative(source))
            if installed:
                require(sha(target) == digest, 'Installed promotion differs: ' + relative(target))


def signed_reviews(project, state, books):
    from tools.project_core.validation.researcher_review import approved_review, read_report
    rows = central_rows(project); result = {}
    for unit in ORDER:
        row = rows[(unit, MIDS[unit])]
        review = approved_review(ROOT, row, books[unit])
        require(review is not None, 'Signed review did not validate: ' + unit)
        name, date, summary = read_report(ROOT, REPORTS[unit], MIDS[unit])
        require((review['researcher_name'], review['review_date']) == (name, date), 'Reviewer/date mismatch: ' + unit)
        require(review['sections'] == summary['sections'], 'Signed source sections differ: ' + unit)
        require(review['excluded_group_ids'] == state['exclusions'][unit], 'Signed exclusions differ: ' + unit)
        result[unit] = review
    return result


def candidate_semantics(project, state, packages):
    from tools.project_core.workbooks.workbooks import read_book
    from tools.project_core.maps.original_atlas_data import detail_from_book
    from tools.project_core.validation.researcher_review import attach_payload_review
    books = state['staged_books']; candidates = {}; rows = central_rows(project)
    for unit in ORDER:
        if books[unit] is None:
            books[unit] = read_book(packages[unit]['directory'] / 'regional' / (unit + '.xlsx'))
    reviews = signed_reviews(project, state, books)
    for unit in ORDER:
        _, candidate = detail_from_book(books[unit], unit, MIDS[unit])
        attach_payload_review(ROOT, rows[(unit, MIDS[unit])], books[unit], candidate, reviews[unit])
        require(not candidate.get('recorded_review_pending'), 'Candidate review is pending: ' + unit)
        wanted = state['authority']['units'][unit]['retained_result_status']
        for option, status in wanted.items():
            require(candidate['health'][option]['status'] == status, 'Candidate diagnosis differs: ' + unit + '/' + option)
        if unit in ('LME_003', 'LME_014'):
            require(candidate['health']['With Egestion']['status'] == 'NOT_RUN', 'Historical WithE is marked current: ' + unit)
            for scope in candidate['group_data']['scopes'].values():
                index = candidate['group_data']['methods'].index('new_WithEgestion')
                require(all(row[index] is None for row in scope), 'Unavailable WithE coefficient exposed: ' + unit)
        provenance = candidate.get('calculation_provenance', {})
        floor = 1.0 if unit == 'LME_037' else .1
        require(provenance.get('use_ee_floor') is True and provenance.get('ee_floor') == floor,
                'Supported page floor provenance differs: ' + unit)
        candidates[unit] = candidate
    return {'reviews': reviews, 'models': candidates}


def register_remaining(project, state):
    from tools.project_core.validation.researcher_review import _register_review
    from tools.project_core.registry.publication import publication_write
    for unit in REGISTER:
        # Journal each completed registration separately: failure of the second
        # registration must still roll back the first one's Project replacement.
        with publication_write(project) if project == PROJECT else nullcontext():
            _register_review(project, REPORTS[unit], unit, MIDS[unit], state['authority']['units'][unit]['excluded_seq'])


def gate(project):
    from tools.project_core.maps.build_html import _refresh_reviews
    _refresh_reviews(project, BASELINE, list(ORDER), model_ids=MIDS, publish=False)


def preflight(progress, state, packages):
    before = sha(PROJECT)
    fd, name = tempfile.mkstemp(prefix='.batch2-review-gate-', suffix='.xlsx', dir=ROOT); os.close(fd)
    temporary = Path(name).resolve()
    require(temporary.parent == ROOT, 'Preflight Project copy outside root')
    try:
        shutil.copyfile(PROJECT, temporary)
        progress.step('register remaining reviews on isolated copy', lambda: register_remaining(temporary, state))
        progress.step('exact bounded replay gate 003 014 037 on copy', lambda: gate(temporary))
        candidate = progress.step('staged candidate page review and scientific status semantics', lambda: candidate_semantics(temporary, state, packages))
        progress.step('verify unchanged preflight sources and package inputs',
                      lambda: (check_sources(state['sources']), check_package_inputs(packages)))
        require(sha(PROJECT) == before, 'Live Project changed during preflight')
        require(all(sha(ROOT / 'interactive_map' / name) == p['sha256'] for name, p in state['pages'].items()), 'Live pages changed during preflight')
        return {'bounded_gate': True, 'candidate_review_units': list(candidate['reviews']),
                'live_project_sha256': before, 'live_project_and_pages_unchanged': True,
                'scientific_execution_performed': False, 'page_build_performed': False}
    finally:
        temporary.unlink(missing_ok=True)


def verify_final(state, packages, candidate):
    from tools.project_core.workbooks.workbooks import read_book, overview
    from tools.project_core.calculations.coverage import _preserved_inputs
    from tools.project_core.validation.researcher_review import FIELDS
    check_sources(state['sources']); check_package_inputs(packages, installed=True)
    books = {u: read_book(REGIONS[u]) for u in ORDER}
    reviews = signed_reviews(PROJECT, state, books)
    for unit, book in books.items():
        require(_preserved_inputs(book) == state['protected'][unit], 'Protected regional inputs changed: ' + unit)
        settings = overview(book)
        require({k: settings.get(k) for k in state['selection'][unit]} == state['selection'][unit], 'Selection or rationale changed: ' + unit)
    require(sha(REGIONS['LME_037']) == state['authority']['units']['LME_037']['regional_and_snapshot_sha256'], 'LME037 workbook bytes changed')
    rows = central_rows(PROJECT)
    prior = {key: {f: row.get(f) for f in (*FIELDS, 'selected', 'selection_rationale')}
             for key, row in rows.items() if key[0] in PRIOR}
    require(prior == state['prior_rows'], 'Previous six central decisions/selections changed')
    pages = page_state()
    for filename, page in pages.items():
        require(page['project_sha256'] == sha(PROJECT), 'Published page has wrong Project hash: ' + filename)
        for unit in PRIOR:
            require(review_state(page, unit) == review_state(state['pages'][filename], unit), 'Prior page review/exclusion/default changed: ' + filename + '/' + unit)
        for unit in ORDER:
            matches = [m for m in page['units'][unit]['models'] if m['id'] == MIDS[unit]]
            require(len(matches) == 1 and default_id(page, unit) == MIDS[unit], 'Published model/default differs: ' + unit)
            actual, expected = matches[0], candidate['models'][unit]
            require(actual.get('researcher_review') == reviews[unit] == expected['researcher_review'], 'Published review differs: ' + unit)
            require(actual.get('display_ppr_excluded_group_ids', []) == state['exclusions'][unit] and not actual.get('recorded_review_pending'), 'Published exclusions/pending differ: ' + unit)
            for key in ('health', 'calculation_provenance'):
                require(actual.get(key) == expected.get(key), 'Published staged semantics differ: ' + unit + '/' + key)
            require(actual['group_data']['methods'] == expected['group_data']['methods'] and actual['group_data']['scopes'] == expected['group_data']['scopes'], 'Published coefficient/missingness matrix differs: ' + unit)
            require([g['id'] for g in actual['group_data']['groups']] == [g['id'] for g in expected['group_data']['groups']], 'Published ecological group identities differ: ' + unit)
            scopes = actual['scopes'] if filename == 'index.html' else actual['taxon_scopes']
            require(scopes == expected['scopes'], 'Published taxon coefficients/statuses differ: ' + unit)
    return {'project_sha256': sha(PROJECT), 'page_hashes': {n: p['sha256'] for n, p in pages.items()},
            'promotions_verified': sum(len(p['promotions']) for p in packages.values()),
            'prior_six_reviews_exclusions_and_defaults_preserved': True,
            'protected_inputs_and_staged_semantics_verified': True, 'LME037_workbook_bytes_unchanged': True}


def publish(progress, state, packages):
    from tools.project_core.registry.publication import publication_transaction
    from tools.project_core.registry.update_project import _update
    from tools.project_core.maps.build_html import _build
    before = RUN / 'inputs/Project_before_combined_publication.xlsx'
    if before.exists():
        require(sha(before) == CURRENT_SHA, 'Existing transaction snapshot differs')
    else:
        shutil.copyfile(PROJECT, before)
    require(sha(before) == sha(PROJECT) == CURRENT_SHA, 'Project changed before transaction')
    with publication_transaction(ROOT, extra_region_paths=list(REGIONS.values()), extra_model_dirs=list(MODELS.values())) as publication:
        progress.step('register LME014 and LME037 on live Project', lambda: register_remaining(PROJECT, state))
        publication.checkpoint([PROJECT])
        progress.step('exact bounded replay gate 003 014 037 before adoption', lambda: gate(PROJECT))
        candidate = progress.step('verify staged candidate reviews before adoption', lambda: candidate_semantics(PROJECT, state, packages))
        progress.step('recheck sources and consumed inputs before first adoption',
                      lambda: (check_sources(state['sources']), check_package_inputs(packages)))
        for unit in ORDER:
            package = packages[unit]
            apply = (lambda p=package: p['module'].apply(publication)) if unit == 'LME_037' else (
                lambda p=package: p['module'].apply(publication, p['directory']))
            progress.step('adopt authenticated retained package ' + unit, apply)
        progress.step('verify every installed promotion byte', lambda: check_package_inputs(packages, installed=True))
        progress.step('consolidate only LME003 LME014 LME037 once', lambda: _update(ROOT, [REGIONS[u] for u in ORDER], False))
        publication.checkpoint([PROJECT])
        progress.step('build saved-data pages only LME003 LME014 LME037 once', lambda: _build(PROJECT, only_units=set(ORDER)))
        return progress.step('verify final sources reviews selections and staged semantics', lambda: verify_final(state, packages, candidate))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--preflight', action='store_true')
    mode.add_argument('--publish', action='store_true')
    args = parser.parse_args(argv)
    progress = Progress(args.publish)
    try:
        from tools.project_core.registry.writes import central_lock
        with central_lock(ROOT):
            with patch('tools.project_core.calculations.coverage.ensure_validated_coverage',
                       side_effect=AssertionError('Scientific inventory forbidden in retained-only batch 2')):
                state = progress.step('authenticate scope sources current Project and baseline pages', initialize)
                packages = verify_packages(progress)
                result = publish(progress, state, packages) if args.publish else preflight(progress, state, packages)
                progress.finish(passed=True, **result)
        print(json.dumps({'passed': True, 'published': args.publish, 'units': list(ORDER),
                          'project_sha256': sha(PROJECT), 'qa': relative(progress.path)}, ensure_ascii=False), flush=True)
    except Exception as error:
        progress.finish(passed=False, failure_stage=progress.data.get('failure_stage', 'lock or between-stage guard'),
                        error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc(),
                        project_sha256_after_failure=fingerprint(PROJECT))
        raise


if __name__ == '__main__':
    main()
