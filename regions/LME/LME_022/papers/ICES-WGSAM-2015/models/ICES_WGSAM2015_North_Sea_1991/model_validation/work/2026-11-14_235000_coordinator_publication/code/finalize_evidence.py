"""Bind completed ICES publication/control evidence and disclose unperformed UI QA.

Run only after publish_ices.py --publish and check_published_controls.js succeed.
This consumes saved evidence; it does not publish, solve, or repeat scientific QA.
"""
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from pathlib import Path
from zipfile import ZipFile
import json
import re
import sys

sys.dont_write_bytecode = True
RUN = Path(__file__).resolve().parents[1]
ROOT = next(p for p in RUN.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
from tools.project_core.validation.researcher_review import table_rows

UNIT = 'LME_022'
MID = 'ICES_WGSAM2015_North_Sea_1991'
MODEL = ROOT / f'regions/LME/{UNIT}/papers/ICES-WGSAM-2015/models/{MID}'
STAGE = MODEL / 'model_validation/work/2026-11-14_230000_retained_adoption'
PACKAGE = STAGE / 'outputs/retained_package_v2'
REPORT = MODEL / 'model_validation/validation.docx'
REPORT_SHA = 'aa5516a7d20ddd25ac803b026ea96627a8fd51897b02c675d6aedbb2f1643b90'
CANONICAL_SHA = '450e0f43822a34a02d4d26ad71358aeef32af8daaff7fcf07cd95ef2131cf97a'
ENGINE_COMMIT = '38cb75d066c5f78d47ba20fc6ab8545a9a6d5c69'
EXCLUDED = [1, 2, 3, 4, 65]
NAMES = ['BaleenWhales', 'ToothedWhales', 'Seals', 'SurfaceFeedingSeabirds', 'DivingSeabirds']
PRIOR_UI = ROOT / ('regions/LME/LME_014/papers/PAT-2023/models/'
    'PAT2024_FalklandShelf_2020_native/model_validation/work/'
    '2026-11-14_193033_coordinator_batch_2/qa/ui_verification.json')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return path, json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def reference(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def main():
    require(not (ROOT / '.project-write.lock').exists(), 'Central writer lock remains active')
    publication_path, publication = read(RUN / 'qa/publication.json')
    controls_path, controls = read(RUN / 'qa/published_controls.json')
    progress_path, progress = read(RUN / 'qa/progress.json')
    preflight_path, preflight = read(RUN / 'qa/preflight.json')
    stages = progress.get('stages', [])
    expected_stages = [
        'authenticate and verify frozen retained package',
        'check current baseline and staged independent inputs',
        'adopt authenticated ICES retained package',
        'register signed ICES review',
        'verify exact bounded review replay',
        'verify installed candidate review and diagnostics',
        'consolidate only LME022',
        'build saved-data pages only LME022',
        'final installed bytes sources reviews defaults and diagnostics',
    ]
    require([s['stage'] for s in stages] == expected_stages and
            all(s['status'] == 'passed' for s in stages), 'Completed publication stages required')
    require(preflight.get('passed') is True and preflight.get('live_mutations') is False,
            'Successful isolated preflight required')
    require(publication.get('promotions_verified') == 8 and
            publication.get('all_prior_reviews_and_defaults_preserved') is True,
            'Publication acceptance is incomplete')
    require(controls.get('passed') is True and controls.get('browser_UI_checked') is False,
            'Completed embedded controls with truthful browser scope required')
    ices_controls = controls['units'][UNIT]
    require(len(ices_controls['default_exclusions']) == len(NAMES) and
            set(ices_controls['default_exclusions']) == set(NAMES) and
            ices_controls['manual_override_pass'] is True and
            ices_controls['validated_filter_eligible'] is True,
            'ICES control acceptance differs')
    require(publication['project_sha256'] == sha(ROOT / 'Project.xlsx'), 'Current Project differs from publication')
    require(set(publication['pages']) == {'index.html', 'trends.html'}, 'Expected both published pages')
    for name, digest in publication['pages'].items():
        page = ROOT / 'interactive_map' / name
        require(sha(page) == digest, 'Current page differs: ' + name)
        require(controls_path.stat().st_mtime_ns >= page.stat().st_mtime_ns,
                'Controls predate current page: ' + name)
    receipts = sorted((RUN / 'outputs').glob('*/publication_receipt.json'))
    require(bool(receipts), 'Transaction publication receipt missing')
    transaction_path, transaction = read(receipts[-1])
    require(transaction == publication, 'Transaction and final publication receipt differ')
    require(sha(transaction_path.parent / 'Project_before_ICES_registration.xlsx') == preflight['project_sha256'],
            'Preflight and transaction baseline differ')
    require(sha(REPORT) == REPORT_SHA and sha(MODEL / 'model.json') == CANONICAL_SHA,
            'Signed report or canonical model changed')

    _, pins = read(RUN / 'inputs/package_pin.json')
    require(pins['package'] == PACKAGE.relative_to(ROOT).as_posix(), 'Wrong retained package')
    require(sha(STAGE / 'code/adopt_retained.py') == pins['wrapper_sha256'] and
            sha(PACKAGE / 'preparation.json') == pins['preparation_sha256'], 'Frozen package pin changed')
    preparation_path, preparation = read(PACKAGE / 'preparation.json')
    promotions = preparation['promotions']
    require(len(promotions) == 8 and len({item['target'] for item in promotions}) == 8,
            'Eight unique promotions required')
    for item in promotions:
        source = (PACKAGE / item['source']).resolve()
        target = (ROOT / item['target']).resolve()
        require(source.is_relative_to(PACKAGE) and target.is_relative_to(ROOT), 'Promotion path escapes scope')
        require(sha(source) == item['sha256'] == sha(target), 'Installed promotion differs: ' + item['target'])

    manifest_path, manifest = read(MODEL / 'results/result_manifest.json')
    retained = manifest['retained_adoption']
    flags = manifest['effective_flags']
    require(flags['runtime_initialization']['git_commit'] == ENGINE_COMMIT, 'Executed engine identity differs')
    require(flags['constructor']['use_ee_floor'] is True and flags['constructor']['ee_floor'] == 0.1,
            'Retained floor settings differ')
    require(retained['scientific_execution_performed'] is False and retained['new_MC_draws'] is False,
            'Retained publication must not claim fresh science')
    caveat = retained['historical_exclusion_caveat']
    require((caveat['taxon'], caveat['mapped_group_id'], caveat['mapped_group_name'],
             caveat['weight'], caveat['confidence'], caveat['positive_catch_years']) ==
            ('Cetorhinus maximus', 1, 'BaleenWhales', 1.0, 'Very low', 62), 'Historical allocation differs')
    for method in ('new_GE', 'new_TE_EEfix', 'new_WithEgestion'):
        _, diagnostic = read(MODEL / f'results/diagnostics/retained_adoption_20261114/{method}.json')
        require(diagnostic['diagnostic_status'] == 'WARN' and
                diagnostic['scientific_execution_performed'] is False and diagnostic['new_MC_draws'] is False,
                'Retained diagnostic restriction differs: ' + method)
    with ZipFile(ROOT / f'regions/LME/{UNIT}/{UNIT}.xlsx') as archive:
        settings = {row['field']: row['value'] for _, row in table_rows(archive, 'Overview', 'Settings')[3]}
    require(settings.get('production_eligible') == '0', 'Production restriction differs')

    index_path, index = read(MODEL / 'model_validation/evidence/evidence_index.json')
    binding = index['signed_report_binding']
    report_entries = [a for a in index['artifacts'] if a['role'] == 'report']
    require(len(report_entries) == 1 and report_entries[0]['sha256'] == REPORT_SHA and
            (index_path.parent / report_entries[0]['path']).resolve() == REPORT,
            'Evidence index does not bind the exact signed report')
    require(binding['signed_report_sha256'] == REPORT_SHA and
            binding['source_authorization']['excluded_ids'] == EXCLUDED and
            binding['source_authorization']['excluded_names'] == NAMES,
            'Signed-report authorization provenance differs')
    sources_path = ROOT / 'interactive_map/sources.html'
    sources = sources_path.read_text(encoding='utf-8')
    source_href = '../' + (MODEL / 'sppr_source.xlsx').relative_to(ROOT).as_posix()
    source_paragraphs = [unescape(p) for p in re.findall(r'<p>.*?</p>', sources, re.S) if source_href in unescape(p)]
    require(len(source_paragraphs) == 1 and 'EE floor ON (0.1)' in source_paragraphs[0] and
            'The signed researcher review applies to the model, diagnostics and calculation conditions recorded in its report.' in source_paragraphs[0],
            'Source page lacks exact saved-calculation and signed-review provenance')

    _, prior_ui = read(PRIOR_UI)
    require(prior_ui.get('status') == 'blocked_by_computer_use_policy' and prior_ui.get('passed') is False,
            'Prior browser limitation evidence differs')
    now = datetime.now(timezone.utc).isoformat()
    ui = {
        'passed': False, 'status': 'not_attempted_in_successor_after_prior_policy_block',
        'browser_UI_checked': False, 'attempted_in_successor': False,
        'project_sha256': publication['project_sha256'], 'timestamp_utc': now,
        'reason': 'Visible browser acceptance remains incomplete. The predecessor browser attempt was stopped because Computer Use could not reliably determine the browser URL. This successor made no browser attempt; embedded payload and JavaScript controls passed separately.',
        'prior_policy_block': reference(PRIOR_UI), 'embedded_controls': reference(controls_path),
    }
    ui_path = RUN / 'qa/ui_verification.json'
    receipt = {
        'schema_version': 1, 'unit_id': UNIT, 'model_id': MID,
        'report_sha256': REPORT_SHA, 'canonical_sha256': CANONICAL_SHA,
        'researcher_name': 'Ido Carmel', 'review_date': '2026-11-14',
        'status': 'Validated by researcher', 'excluded_seq': EXCLUDED, 'excluded_group_names': NAMES,
        'project_sha256': publication['project_sha256'], 'pages': publication['pages'],
        'sources_sha256': sha(sources_path), 'receipt_timestamp_utc': now,
        'publication_final_checks_started_utc': stages[-1]['started_utc'],
        'executed_engine_git_commit': ENGINE_COMMIT, 'scientific_runs': 0, 'new_monte_carlo_draws': 0,
        'diagnostic_status': {name: 'WARN' for name in ('GE', 'TE', 'With Egestion')},
        'production_eligible': False, 'excluded_groups_preserved_in_scientific_inputs': True,
        'historical_basking_shark_allocation': caveat,
        'all_prior_reviews_and_defaults_preserved': True, 'promotions_verified': 8,
        'browser_acceptance_passed': False, 'browser_acceptance_limitation': ui['reason'],
        'signed_report_provenance_in_evidence_index_verified': True,
        'signed_review_provenance_in_sources_page_verified': True,
        'scope': 'Authorized signed decision and authenticated retained package publication; no renewed scientific approval.',
        'evidence': {key: reference(path) for key, path in [
            ('preflight', preflight_path), ('publication', publication_path), ('transaction', transaction_path),
            ('progress', progress_path), ('controls', controls_path), ('retained_preparation', preparation_path),
            ('result_manifest', manifest_path), ('signed_report_index', index_path),
            ('publication_driver', RUN / 'code/publish_ices.py'),
        ]},
    }
    require(not (ROOT / '.project-write.lock').exists(), 'Writer appeared before receipt finalization')
    require(sha(ROOT / 'Project.xlsx') == publication['project_sha256'], 'Project changed during finalization')
    write(ui_path, ui)
    receipt['evidence']['browser'] = reference(ui_path)
    target = MODEL / 'model_validation/evidence/source_review/coordinator_publication_20261114.json'
    write(target, receipt)
    print(json.dumps({'publication_receipts': 1, 'receipt': reference(target),
                      'browser_acceptance_passed': False, 'scientific_runs': 0}))


if __name__ == '__main__':
    main()
