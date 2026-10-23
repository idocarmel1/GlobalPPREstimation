"""Reconcile saved group, level and summary evidence without calculator execution."""
import csv
import hashlib
import json
import math
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
ROOT = next(p for p in STUDY.parents if (p / 'Project.xlsx').is_file())
OUT = STUDY / 'results/validated7'
EVIDENCE = STUDY / 'evidence/validated7'
VARIANTS = ('fixed_0.1', 'consumer_mean_Q', 'aggregated_II_IV')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def close(left, right):
    assert math.isclose(left, right, rel_tol=1e-10, abs_tol=1e-8), (left, right)


def main():
    results = read(OUT / 'comparison.json')
    groups = read(OUT / 'group_records.json')
    levels = read(OUT / 'level_records.json')
    allocations = read(EVIDENCE / 'allocations_2019.json')
    sources = read(STUDY / 'inputs/validated7/source_hashes.json')
    for path, expected in sources.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    pairs = {tuple(pair) for pair in results['pairs']}
    assert len(pairs) == 7
    assert {(row['unit_id'], row['model_id']) for row in groups} == pairs
    assert len({(g['unit_id'], g['group']) for g in groups}) == len(groups) == 249
    assert sum(g['group_type'] == 'Regular' for g in groups) == 219
    assert len(levels) == 21
    checks = []
    for unit_id, model_id in sorted(pairs):
        local = [g for g in groups if g['unit_id'] == unit_id]
        scalar_rows = [r for r in results['summary'] if r['unit_id'] == unit_id]
        assert {r['variant'] for r in scalar_rows} == set(VARIANTS)
        levels_local = [r for r in levels if r['unit_id'] == unit_id]
        for row in levels_local:
            close(row['throughput'], sum(row[k] for k in ('predation', 'export', 'respiration', 'flow_to_detritus')))
            close(row['TE'], (row['predation'] + row['export']) / row['throughput'])
        scalar = next(r['TE'] for r in scalar_rows if r['variant'] == 'aggregated_II_IV')
        close(scalar, math.prod(row['TE'] for row in levels_local) ** (1 / 3))
        for g in local:
            parts = [a['catch_tonnes'] for a in allocations if a['unit_id'] == unit_id
                     and a['group'] == g['group'] and a['review_included']]
            close(sum(parts), g['regional_2019_included_catch_tonnes'])
        for row in scalar_rows:
            coefficient = row['variant'] + '_sppr'
            for g in local:
                close(g[coefficient], row['TE'] ** (1 - g['TL_cycle_broken_detritus_basal']))
            included = [g for g in local if g['review_included']]
            close(row['native_included_catch'], sum(g['native_catch'] for g in included))
            if row['native_included_catch'] > 0:
                close(row['native_catch_times_sppr'], sum(g['native_catch'] * g[coefficient] for g in included))
            else:
                assert row['native_catch_times_sppr'] is None and row['native_catch_weighted_sppr'] is None
            close(row['regional_2019_included_catch_tonnes'], sum(g['regional_2019_included_catch_tonnes'] for g in included))
            close(row['regional_2019_ppr_tC'], sum(g['regional_2019_included_catch_tonnes'] * g[coefficient] for g in included) / 9)
        checks.append({'unit_id': unit_id, 'groups': len(local), 'variants': len(scalar_rows),
                       'coefficients_and_both_catch_totals_reconciled': True})
    for variant, aggregate in results['regional_total'].items():
        rows = [r for r in results['summary'] if r['variant'] == variant]
        close(aggregate['regional_2019_ppr_tC'], sum(r['regional_2019_ppr_tC'] for r in rows))
        close(aggregate['included_catch_tonnes'], 39684336.471269056)
    for filename, expected_count in [('summary.csv', 21), ('group_records.csv', 249), ('level_records.csv', 21)]:
        with (OUT / filename).open(encoding='utf-8-sig', newline='') as stream:
            assert len(list(csv.DictReader(stream))) == expected_count
    report = {'passed': True, 'source_hashes_rechecked': len(sources), 'models': checks,
              'summary_rows': 21, 'group_rows': 249, 'level_rows': 21,
              'verification_scope': 'Saved coefficients, scalar TE and TL identities, original allocation totals, native and regional PPR arithmetic, CSV row counts and consumed-source hashes; no new scientific approval',
              'result_sha256': hashlib.sha256((OUT / 'comparison.json').read_bytes()).hexdigest(),
              'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (EVIDENCE / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
