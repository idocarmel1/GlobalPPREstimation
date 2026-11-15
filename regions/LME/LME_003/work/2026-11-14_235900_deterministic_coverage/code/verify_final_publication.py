"""Read-only final acceptance after the coordinator confirms publication.

Run with --published. Only the requested QA JSON is written. No engine,
registration, workbook mutation, publication, or scientific calculation runs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import traceback
import zipfile

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))

from tools.project_core.calculations.coverage import _method_rows
from tools.project_core.maps.original_atlas_data import embedded
from tools.project_core.registry.discovery import region_directory, resolve_model
from tools.project_core.validation.researcher_review import STATUS, approved_review, read_report, table_rows
from tools.project_core.workbooks.workbooks import overview, read_book
from final_cohort_audit import object_sha


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def local(value):
    path = (ROOT / value).resolve()
    require(path.is_relative_to(ROOT), 'Evidence path escaped the project: ' + str(value))
    return path


def verify(audit_path):
    consumed = {}

    def bind(path, expected=None):
        path = Path(path).resolve()
        fingerprint = sha(path)
        require(expected is None or fingerprint == expected, 'Hash differs: ' + str(path))
        require(path not in consumed or consumed[path] == fingerprint, 'Input changed: ' + str(path))
        consumed[path] = fingerprint
        return fingerprint

    inventory_path = WORK / 'inputs/validated_inventory.json'
    inventory_hash = bind(inventory_path)
    inventory = read(inventory_path)
    expected = {(r['unit_id'], r['model_id']): r for r in inventory['pairs']}
    require(len(expected) == len(inventory['pairs']) == 16, 'Expected exactly 16 unique validated pairs')
    adoption_path = WORK / 'outputs/adoption_publication.json'
    bind(adoption_path)
    adoption = read(adoption_path)
    audit_hash = bind(audit_path)
    audit = read(audit_path)
    require(audit.get('status') == 'PASS_PRE_PUBLICATION', 'Final cohort audit did not pass')
    require(audit.get('audit_helper_sha256'), 'Final cohort audit has no helper fingerprint')
    bind(Path(__file__).with_name('final_cohort_audit.py'), audit['audit_helper_sha256'])
    require(audit.get('inventory_sha256') == inventory_hash, 'Audit used another inventory')
    audited = {(r['unit_id'], r['model_id']): r for r in audit['pairs']}
    require(set(audited) == set(expected), 'Audit cohort differs from inventory')
    require(adoption.get('scientific_execution_performed') is False, 'Adoption certificate includes scientific execution')
    required_checks = {
        'all canonical inputs and consumed evidence unchanged',
        'retained finite/MC coefficients, arithmetic and diagnostics unchanged',
        'Catch, Classic PPR, NPP, groups, matching and selections unchanged',
        'signed reviews unchanged except the authorized Humboldt GE/TE amendment',
        'all validated decisions and researcher exclusions preserved',
        'saved-data publication only',
    }
    require(required_checks.issubset(set(adoption.get('checks', []))), 'Adoption preservation assertions are incomplete')
    project = ROOT / 'Project.xlsx'
    project_hash = bind(project, adoption.get('project_sha256'))
    require(adoption.get('project_sha256') is not None, 'Adoption lacks the final Project fingerprint')
    with zipfile.ZipFile(project) as archive:
        metadata = [r for _, r in table_rows(archive, 'Models & coverage', 'Models')[3]
                    if r.get('researcher_review_status') == STATUS]
    registered = {(r['unit_id'], r['model_id']): r for r in metadata}
    require(len(metadata) == 16 and set(registered) == set(expected), 'Current Project validated cohort differs')

    continuation_path = WORK / 'outputs/continuation_handoff.json'
    bind(continuation_path)
    continuation = read(continuation_path)
    handoff_path = local(continuation['humboldt']['handoff'])
    handoff_hash = bind(handoff_path, continuation['humboldt']['handoff_sha256'])
    handoff = read(handoff_path)
    humboldt_pair = handoff['unit_id'], handoff['model_id']
    canonical = local(handoff['canonical_report'])
    original = local(handoff['retained_historical_original'])
    canonical_hash = bind(canonical, handoff['staged_sha256'])
    original_hash = bind(original, handoff.get('original_sha256', handoff['canonical_expected_before_sha256']))
    amendment = adoption['humboldt_review_amendment']
    for key, expected_value in {
        'unit_id': humboldt_pair[0], 'model_id': humboldt_pair[1],
        'original_report_sha256': original_hash, 'current_report_sha256': canonical_hash,
        'handoff_sha256': handoff_hash, 'researcher_review_status': STATUS,
        'excluded_group_ids': handoff['excluded_group_names'],
    }.items():
        require(amendment.get(key) == expected_value, 'Adoption amendment differs at ' + key)
    after_ref = handoff['signoff_after']
    after_path = local(after_ref['path'])
    bind(after_path, after_ref['sha256'])
    actual_signoff = list(read_report(ROOT, canonical, humboldt_pair[1]))
    require(actual_signoff == read(after_path), 'Canonical Humboldt parser differs from reviewed staged parser')
    require(actual_signoff[:2] == [handoff['reviewer'], handoff['signed_date']], 'Humboldt signer/date changed')

    reviews, pair_reports = {}, []
    for pair, item in expected.items():
        print('Final acceptance ' + pair[0] + ': review, inputs and retained MC', flush=True)
        row, prior = registered[pair], audited[pair]
        model = resolve_model(region_directory(ROOT, pair[0]), pair[1])
        require(model.parent == local(item['model_dir']), 'Canonical model discovery differs: ' + str(pair))
        bind(model, item['canonical_model_sha256'])
        require(prior['model_sha256'] == item['canonical_model_sha256'], 'Audit model identity differs: ' + str(pair))
        report = local(row['validation_report_path'])
        bind(report, canonical_hash if pair == humboldt_pair else prior['review_sha256'])
        require(row['validation_report_sha256'] == consumed[report], 'Registered report hash differs: ' + str(pair))
        require(row['reviewed_model_sha256'] == consumed[model], 'Registered model hash differs: ' + str(pair))
        mapping = model.parent / 'model_validation/taxon_mapping.xlsx'
        mapping_key = mapping.relative_to(ROOT).as_posix()
        if mapping_key in audit['protected_files']:
            bind(mapping, audit['protected_files'][mapping_key])

        region = region_directory(ROOT, pair[0])
        regional = region / (region.name + '.xlsx')
        bind(regional)
        book = read_book(regional, sheets=['Overview', 'Selected model groups'])
        if overview(book).get('results_model_id') != pair[1]:
            snapshot = model.parent / 'results/regional_snapshot.xlsx'
            bind(snapshot)
            book = read_book(snapshot, sheets=['Overview', 'Selected model groups'])
        require(overview(book).get('results_model_id') == pair[1], 'Saved result identity differs: ' + str(pair))
        # This API freshly checks the signed Word parser, central summary, model
        # hash and exact current group identities; it performs no publication.
        reviews[pair] = approved_review(ROOT, row, book)
        require(reviews[pair] and reviews[pair]['status'] == STATUS, 'Review is no longer valid: ' + str(pair))
        if pair == humboldt_pair:
            require(reviews[pair]['excluded_group_ids'] == handoff['excluded_group_names'], 'Humboldt exclusions changed')

        manifest_path = model.parent / 'results/result_manifest.json'
        bind(manifest_path)
        methods = read(manifest_path).get('method_coverage', {}).get('methods', {})
        current_mc = {key: value for key, value in methods.items() if key.startswith('MC_')}
        require(set(current_mc) == set(prior['mc']), 'MC outcome presence changed: ' + str(pair))
        _, group_hashes = _method_rows(book)
        mc_records = {}
        for key, previous in prior['mc'].items():
            require(group_hashes.get(key) == previous['group_rows_sha256'], 'MC coefficient rows changed: ' + str(pair) + '/' + key)
            current = current_mc[key]
            trace_verified = False
            if object_sha(current) != previous['outcome_sha256']:
                ref = current.get('evidence', {})
                certificate_path = (model.parent / 'results/diagnostics' / ref.get('path', '')).resolve()
                require(certificate_path.is_relative_to(model.parent), 'MC trace path escaped model')
                bind(certificate_path, ref.get('sha256'))
                certificate = read(certificate_path)
                trace = certificate.get('prior_method_trace') or {}
                require(current.get('preserve_saved') is True
                        and certificate.get('evidence_kind') == 'retained_saved_method'
                        and object_sha(trace.get('recorded_outcome')) == previous['outcome_sha256'],
                        'Changed MC outcome lacks its exact original trace: ' + str(pair) + '/' + key)
                trace_verified = True
            if previous.get('evidence_path'):
                bind(local(previous['evidence_path']), previous['evidence_sha256'])
            mc_records[key] = {'group_rows_sha256': group_hashes.get(key),
                               'original_evidence_sha256': previous.get('evidence_sha256'),
                               'original_outcome_preserved_in_trace': trace_verified}
        pair_reports.append({'unit_id': pair[0], 'model_id': pair[1],
                             'model_sha256': consumed[model], 'report_sha256': consumed[report],
                             'excluded_group_ids': reviews[pair]['excluded_group_ids'],
                             'mc_absent': not current_mc, 'mc': mc_records})
    require(sum(len(r['excluded_group_ids']) for r in reviews.values()) == 57, 'Expected exactly 57 researcher exclusions')

    pages = []
    for filename, variable in [('index.html', 'DB'), ('trends.html', 'SERIES_DB')]:
        path = ROOT / 'interactive_map' / filename
        page_hash = bind(path)
        data, layout = embedded(path, variable)
        require(f'<meta name="ppr-project-sha256" content="{project_hash}">' in layout,
                filename + ': final Project fingerprint differs')
        units = data['network']['units'] if variable == 'DB' else data['units']
        payload_rows = [((unit_id, model['id']), model) for unit_id, unit in units.items()
                        for model in unit.get('models', [])
                        if (model.get('researcher_review') or {}).get('status') == STATUS]
        payload_models = dict(payload_rows)
        require(len(payload_rows) == 16 and set(payload_models) == set(expected),
                filename + ': validated cohort differs')
        for pair, wanted in reviews.items():
            actual = payload_models[pair]
            require(actual.get('researcher_review') == wanted, filename + ': review object differs ' + str(pair))
            require(actual.get('display_ppr_excluded_group_ids') == wanted['excluded_group_ids'],
                    filename + ': exclusions differ ' + str(pair))
            require(not actual.get('recorded_review_pending'), filename + ': current review is pending ' + str(pair))
        pages.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': page_hash,
                      'validated_pairs': len(payload_models), 'researcher_exclusions': 57,
                      'project_sha256': project_hash})
        del data, layout, units, payload_models, payload_rows

    for path, fingerprint in consumed.items():
        require(sha(path) == fingerprint, 'Consumed input changed during final verification: ' + str(path))
    return {'schema_version': 1, 'status': 'PASS_FINAL_PUBLICATION',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'helper_sha256': sha(__file__), 'project_sha256': project_hash,
            'validated_pairs': 16, 'researcher_exclusions': 57,
            'humboldt': {'current_report_sha256': canonical_hash, 'original_report_sha256': original_hash,
                         'reviewer': actual_signoff[0], 'signed_date': actual_signoff[1],
                         'fresh_parser_matches_reviewed_staged_parser': True},
            'pages': pages, 'pairs': pair_reports,
            'preservation_evidence': {'adoption_path': adoption_path.relative_to(ROOT).as_posix(),
                                      'adoption_sha256': consumed[adoption_path],
                                      'audit_path': Path(audit_path).relative_to(ROOT).as_posix(),
                                      'audit_sha256': audit_hash,
                                      'reused_transaction_checks': sorted(required_checks),
                                      'independent_mc_checks': 'Original outcome or exact retained trace, original evidence bytes, and group coefficient row hashes'},
            'consumed_files': {path.relative_to(ROOT).as_posix(): fingerprint for path, fingerprint in consumed.items()},
            'limitations': ['Scientific inputs and method eligibility are not recalculated.',
                            'Full retained arithmetic, source-workbook coefficients, diagnostics and independent-input preservation reuse the successful adoption transaction assertions.',
                            'Production table and complete HTML layout/annual-cell verification are separate coordinator checks.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--published', action='store_true', required=True,
                        help='Coordinator confirms the authorized publication completed')
    parser.add_argument('--audit', type=Path, default=WORK / 'outputs/final_cohort_audit.json')
    parser.add_argument('--output', type=Path, default=WORK / 'qa/final_publication_verification.json')
    args = parser.parse_args()
    output = args.output.resolve()
    require(output.is_relative_to((WORK / 'qa').resolve()), 'QA output must stay within WORK/qa')
    try:
        report = verify(args.audit.resolve())
    except Exception as error:
        output.write_text(json.dumps({'status': 'FAIL_FINAL_PUBLICATION', 'error': str(error),
                                     'traceback': traceback.format_exc()}, indent=2) + '\n', encoding='utf-8')
        raise
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'validated_pairs': 16, 'researcher_exclusions': 57,
                      'output': str(output), 'sha256': sha(output)}, indent=2), flush=True)


if __name__ == '__main__':
    main()
