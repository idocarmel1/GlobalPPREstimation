"""Compare retained numerical returns and authenticate the sensitivity handoff.

This script does not import or execute any scientific calculator.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent / 'pooled_20261114'
MODEL = ROOT.parents[2]
REPO = next(p for p in MODEL.parents if (p / 'Project.xlsx').is_file())
GROUPS = (1, 2, 3, 4, 11, 12)
METHODS = (('ge', 'GE'), ('te', 'TE'), ('with_egestion', 'With Egestion'))


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frame(path):
    data = read(path)
    assert data['type'] == 'dataframe'
    return {seq: dict(zip(data['columns'], row)) for seq, row in zip(data['index'], data['data'])}


def production_residual(row):
    return sum(row[k] for k in ('predation', 'catch', 'biomass_accum', 'net_migration', 'M0', 'external_mortality_export')) - row['p']


def main():
    summary = read(ROOT / 'outputs/summary.json')
    assert summary['status'] == 'COMPLETE_OUTCOME_INVENTORY'
    assert summary['protected_bytes_unchanged']
    assert all(m['execution'] == 'RETURNED' for m in summary['methods'])
    assert summary['constructor']['use_ee_floor'] is True and summary['constructor']['ee_floor'] == 0.1
    preparation = read(ROOT / 'preparation.json')
    assert sha(ROOT / 'code/run_diagnostics.py') == preparation['runner_sha256']
    assert sha(BASE / 'evidence_index.json') == preparation['baseline_index_sha256']
    check = runpy.run_path(str(REPO / 'tools/skills/paper-to-ppr/scripts/check_evidence.py'))['check']
    baseline_check = check(BASE / 'evidence_index.json')
    assert baseline_check['complete'], baseline_check

    before = frame(BASE / 'outputs/effective_groups.json')
    after = frame(ROOT / 'outputs/effective_groups.json')
    staging = {r['group_id']: r for r in read(ROOT / 'outputs/catch_and_discard_staging.json')}
    groups = []
    for seq in GROUPS:
        old, new = before[seq], after[seq]
        old_r, new_r = production_residual(old), production_residual(new)
        expected = old_r - 0.9 * staging[seq]['baseline_discards']
        assert math.isclose(new_r, expected, rel_tol=1e-12, abs_tol=1e-15)
        assert all(old[k] == new[k] for k in old if k != 'catch'), seq
        groups.append({'group_id': seq, 'group_name': new['group_name'], 'production': new['p'],
                       'baseline_discards': staging[seq]['baseline_discards'], 'scenario_discards': staging[seq]['discards'],
                       'baseline_signed_outflow_minus_production': old_r, 'scenario_signed_outflow_minus_production': new_r,
                       'baseline_absolute_relative_residual': abs(old_r / old['p']),
                       'scenario_absolute_relative_residual': abs(new_r / new['p']),
                       'scenario_exceeds_10_percent': abs(new_r / new['p']) > 0.1,
                       'scenario_direction': 'outflow excess' if new_r > 0 else 'outflow deficit'})
    failures = [{'group_id': seq, 'group_name': row['group_name'],
                 'absolute_relative_residual': abs(production_residual(row) / row['p'])}
                for seq, row in after.items() if 1 <= seq <= 69 and row['p'] > 0 and abs(production_residual(row) / row['p']) > 0.1]
    method_results = []
    for slug, name in METHODS:
        old = read(BASE / f'outputs/{slug}/diagnostic_report.json')
        new = read(ROOT / f'outputs/{slug}/diagnostic_report.json')
        old_c = frame(BASE / f'outputs/{slug}/coefficients.json')
        new_c = frame(ROOT / f'outputs/{slug}/coefficients.json')
        coefficient_changes = []
        for seq in old_c:
            for scope in ('all', 'inner', 'PP'):
                a, b = old_c[seq][scope], new_c[seq][scope]
                assert math.isfinite(a) and math.isfinite(b)
                coefficient_changes.append({'group_id': seq, 'group_name': after[seq]['group_name'], 'scope': scope,
                                            'baseline': a, 'scenario': b, 'absolute_change': b-a,
                                            'relative_change': (b/a-1) if a else None})
        nonzero = [x for x in coefficient_changes if x['relative_change'] is not None and x['group_id'] <= 69]
        worst = max(nonzero, key=lambda x: abs(x['relative_change']))
        method_results.append({'method': name, 'slug': slug, 'baseline': old, 'scenario': new,
                               'ppr_all_relative_change': new['footprint']['ppr_all']/old['footprint']['ppr_all']-1,
                               'max_living_coefficient_relative_change': worst,
                               'six_group_coefficients': [x for x in coefficient_changes if x['group_id'] in GROUPS],
                               'all_group_coefficient_changes': coefficient_changes})
    comparison = {'schema_version': 1, 'run_id': 'discards_div10_20261114', 'variant_id': summary['variant_id'],
                  'baseline_run': '../pooled_20261114', 'scenario': summary['scenario'],
                  'constructor': summary['constructor'], 'method_options': summary['method_options'],
                  'production_residual_definition': '(predation + catch + BA + net migration + M0 + external floor sink) minus P; absolute relative residual divides by P.',
                  'groups': groups, 'remaining_production_failures': failures, 'methods': method_results,
                  'baseline_flow_accounting': read(BASE / 'outputs/flow_reconciliation.json'),
                  'scenario_flow_accounting': read(ROOT / 'outputs/flow_reconciliation.json'),
                  'interpretation': 'Hypothetical sensitivity. Overall FAIL restrictions remain. Model-catch PPR is not regional fisheries time-series PPR and these failed results are not adopted.'}
    (ROOT / 'comparison.json').write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = ['# Discards divided by ten: pooled model sensitivity', '',
             '**Result: all three methods still return overall FAIL.** Five of the six flagged groups remain above the 10% production-residual threshold. This is a user-authorized hypothesis, not a source correction.', '',
             'Only discards for groups 1, 2, 3, 4, 11 and 12 were divided by ten. Their donor catch and single-pool returns were reduced together. All living biological parameters, diets, 100% pooled routing, EE floor ON at 0.1 and the external mortality sink were retained. The original and pooled canonical models were not changed.', '',
             '## Production-budget changes', '',
             '| Group | Baseline absolute discrepancy | Discards / 10 | New direction |',
             '|---|---:|---:|---|']
    for g in groups:
        lines.append(f"| {g['group_name']} | {100*g['baseline_absolute_relative_residual']:.4f}% | {100*g['scenario_absolute_relative_residual']:.4f}% | {g['scenario_direction']} |")
    lines += ['', 'Bottlenose dolphin falls below the 10% failure threshold, but remains above the warning threshold. Fin whale and Common dolphin improve but still fail. Striped dolphin and both turtles worsen because their total production outflows were already too small; reducing discards increases that deficit. No other living group exceeds 10%.', '',
              'Fin-whale discards after scaling are 0.00002808 t/km²/year, below production of 0.000190034526. However, its retained M0 plus floor sink already consumes almost all production, so the remaining catch still produces a 14.7753% discrepancy. EE = 1 - M0/P continues to hold; it does not force the rest of the production budget to close.', '',
              '## SPPR diagnostic changes', '',
              '| Method | PP-budget gap: baseline → sensitivity | PP-budget grade: baseline → sensitivity | Overall |',
              '|---|---:|---|---|']
    for m in method_results:
        a, b = m['baseline'], m['scenario']
        lines.append(f"| {m['method']} | {100*a['balance']['rel_gap']:.4f}% → {100*b['balance']['rel_gap']:.4f}% | {a['balance']['status']} → {b['balance']['status']} | {b['status']} |")
    lines += ['', 'All strict budget-balance flags remain false. The largest consumption residual rises from 2.9451% to 9.4646%, still below the 10% failure threshold. The small diet-sum warning is unchanged. TE retains its near-zero-efficiency warning.', '',
              '## Model-catch PPR and coefficient changes', '',
              'These are all-source PPR values for the model’s own catch density, in the model mass basis per km²/year. They are diagnostic footprints, not recalculated regional catch time series or eligible published estimates.', '',
              '| Method | Baseline PPR | Sensitivity PPR | Relative change | Largest living-group SPPR coefficient change across all/inner/PP |',
              '|---|---:|---:|---:|---:|']
    for m in method_results:
        a, b = m['baseline'], m['scenario']
        lines.append(f"| {m['method']} | {a['footprint']['ppr_all']:.6f} | {b['footprint']['ppr_all']:.6f} | {100*m['ppr_all_relative_change']:.4f}% | {100*m['max_living_coefficient_relative_change']['relative_change']:.6f}% |")
    lines += ['', 'The catch-weighted PPR decrease combines lower discards with altered all-source SPPR coefficients; the two effects should not be conflated. PP-only SPPR coefficients are exactly unchanged for every group and method. The largest living all/inner coefficient decrease occurs in Mobile benthos (group 61). Complete group/scope coefficient comparisons are in [comparison.json](comparison.json).', '',
              '## Accounting, evidence and limits', '',
              '- All three methods returned full numerical results using the same five pinned engine/serialization files as the baseline.',
              '- SPPR contributions remain finite and nonnegative; all returned matrices remain finite and recycling converges. These are numerical checks, not ecological validation.',
              '- All living effective EE values, M0 and external mortality sink amounts are unchanged; EE = 1 - M0/P is preserved.',
              '- Total discard returns fall from 0.0759254449376 to 0.0752188642616 t/km²/year. Total catch falls from 0.5038960229357493 to 0.5031894422597494; external landings remain 0.4279705779981493.',
              '- The floor sink remains 0.000670250768124695 t/km²/year. The calculated pool stock residual decreases with the discard reduction; it remains a runtime balance quantity, not an observed biomass trend.',
              '- No model, workbook, DOCX, selection, Project.xlsx, map/trends or researcher decision was updated.', '',
              '[Scenario plan](plan.md) · [Exact comparison](comparison.json) · [Independent numerical audit](independent_review.json) · [Execution summary](outputs/summary.json) · [Evidence index](evidence_index.json) · [Completeness](completeness.json)', '',
              '[Baseline diagnostics](../pooled_20261114/diagnostic_summary.md) · [Original source check](../fin_whale_source_audit_20261114/findings.md)', '']
    (ROOT / 'diagnostic_summary.md').write_text('\n'.join(lines), encoding='utf-8')

    independent = read(ROOT / 'independent_review.json')
    assert sha(ROOT / 'independent_review.json') == '2ede6838144a064e2e349929272b2334bccdee8886fc7b4c95f01c07ca02dc09'
    assert not independent['failed_independent_checks']
    assert all(value is True for value in independent['independent_checks'].values())
    # The independent audit carries its own checks; preserve it verbatim.
    artifacts = []
    def add(role, path, expected=None):
        actual = sha(path)
        if expected is not None:
            assert actual == expected, path
        artifacts.append({'role': role, 'path': Path(os.path.relpath(path, ROOT)).as_posix(),
                          'sha256': actual, 'availability': 'present'})
    manifest = read(ROOT / 'outputs/artifact_manifest.json')
    for item in manifest['artifacts']:
        add('diagnostic_output/' + item['role'], ROOT / 'outputs' / item['path'], item['sha256'])
    for item in preparation['pinned_executed_engine']:
        add('executed_engine/' + item['repository_relative_path'], ROOT / item['pinned_path'], item['sha256'])
    for name in ['plan.md', 'preparation.json', 'run.log', 'comparison.json', 'diagnostic_summary.md', 'independent_review.json',
                 'code/prepare_sensitivity.py', 'code/run_diagnostics.py', 'code/finalize_comparison.py', 'outputs/artifact_manifest.json']:
        add(name, ROOT / name)
    old_index = read(BASE / 'evidence_index.json')
    add('authenticated_baseline_index', BASE / 'evidence_index.json', preparation['baseline_index_sha256'])
    for item in old_index['artifacts']:
        if item['role'] in {'original_canonical_model', 'derived_canonical_model', 'published_paper_pdf', 'published_parameter_workbook', 'published_parameter_document'}:
            add(item['role'], (BASE / item['path']).resolve(), item['sha256'])
    index = {'schema_version': 1, 'run_id': 'discards_div10_20261114', 'region_id': 'LME_026',
             'model_id': summary['model_id'], 'variant_id': summary['variant_id'], 'created_at': datetime.now(timezone.utc).isoformat(),
             'source_identity': old_index['source_identity'],
             'computational_input_identity': {'canonical_model_sha256': preparation['canonical_model_sha256'],
                 'runtime_initialization': summary['runtime_initialization'], 'scenario': summary['scenario'],
                 'constructor': summary['constructor'], 'method_options': summary['method_options'],
                 'runner_sha256': preparation['runner_sha256'], 'pinned_engine': preparation['pinned_executed_engine']},
             'methods': [name for _, name in METHODS], 'required_roles': [a['role'] for a in artifacts], 'artifacts': artifacts,
             'reconciliation': {'baseline_package_hashes_reverified': baseline_check['complete'],
                               'protected_bytes_unchanged': summary['protected_bytes_unchanged'],
                               'six_signed_residual_changes_match_independent_formula': True,
                               'six_groups_living_biology_unchanged': True,
                               'all_27_independent_runtime_checks_pass': all(independent['independent_checks'].values()),
                               'all_three_methods_returned': True,
                               'explicit_ee_floor_on_0_1': True},
             'scientific_disposition': 'GE FAIL; TE FAIL; With Egestion FAIL. Hypothetical sensitivity, not adopted or researcher approved.'}
    (ROOT / 'evidence_index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    result = check(ROOT / 'evidence_index.json')
    assert result['complete'], result
    (ROOT / 'completeness.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    links = re.findall(r'\[[^\]]+\]\(([^\)]+)\)', (ROOT / 'diagnostic_summary.md').read_text(encoding='utf-8'))
    assert all((ROOT / path).is_file() for path in links if '://' not in path)
    print(json.dumps({'complete': result['complete'], 'verified_artifacts': len(result['verified_artifacts']),
                      'baseline_artifacts_verified': len(baseline_check['verified_artifacts']), 'links_verified': len(links),
                      'methods': [{'method': m['method'], 'budget_gap': m['scenario']['balance']['rel_gap'],
                                   'ppr_change': m['ppr_all_relative_change'], 'max_coefficient_change': m['max_living_coefficient_relative_change']} for m in method_results]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
