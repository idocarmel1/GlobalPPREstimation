"""Verify recomputed successor rows against unchanged dated source evidence.

This check compares individual retained rows after recomputation. It never
produces a new aggregate by subtracting a previous total.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys

STUDY = Path(__file__).resolve().parents[1]
ROOT = next(p for p in STUDY.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
from cohort import EXCLUDED_PAIR, REQUIRED_PAIRS, assert_cohort_current


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


cohort = assert_cohort_current(ROOT, STUDY / 'inputs/cohort.json')
old = ROOT / 'research/human/sppr_trophic_level_20261016'
records = read(STUDY / 'results/group_records.json')
old_records = read(old / 'results/group_records.json')
expected = [r for r in old_records if (r['unit'], r['model_id']) != EXCLUDED_PAIR]
assert records == expected, 'Recomputed retained SPPR records changed'
assert {(r['unit'], r['model_id']) for r in records} == set(REQUIRED_PAIRS)
panel = read(STUDY / 'results/method_panel_data.json')
old_panel = read(old / 'results/method_panel_data.json')
assert panel['group_records'] == [r for r in old_panel['group_records']
                                  if (r['unit'], r['model_id']) != EXCLUDED_PAIR]
assert panel['focal_anchors'] == old_panel['focal_anchors']
assert read(STUDY / 'results/comparison.json')['LME027_anchors'] == read(old / 'results/comparison.json')['LME027_anchors']
hash_checks = 0
for ledger in (read(STUDY / 'inputs/source_hashes.json'), panel['source_hashes']):
    for path, expected_hash in ledger.items():
        assert digest(ROOT / path) == expected_hash, ('Source changed', path)
        hash_checks += 1
agg = ROOT / 'regions/LME/LME_028/work/2026-10-18_121535_trophic_aggregation_validated7'
decomposition = read(agg / 'outputs/decomposition.json')
historical = read(ROOT / 'regions/LME/LME_028/work/2026-10-16_202757_trophic_aggregation/outputs/decomposition.json')
historical_models = {r['unit_id']: r['model_id'] for r in historical['regional']}
for key in ('groups', 'regional'):
    expected_rows = [r for r in historical[key]
                     if (r['unit_id'], historical_models[r['unit_id']]) != EXCLUDED_PAIR]
    assert decomposition[key] == expected_rows, ('Recomputed retained allocation rows changed', key)
assert sorted(map(tuple, decomposition['cohort_pairs'])) == sorted(REQUIRED_PAIRS)
assert (agg / 'inputs/cohort.json').read_bytes() == (STUDY / 'inputs/cohort.json').read_bytes()
for path, expected_hash in decomposition['sources_sha256'].items():
    assert digest(ROOT / path) == expected_hash, ('Aggregation source changed', path)
    hash_checks += 1
evidence = {
    'verified_at_utc': datetime.now(timezone.utc).isoformat(),
    'passed': True, 'validated_pairs': len(cohort['pairs']),
    'retained_sppr_records_exact': len(records),
    'retained_method_panel_records_exact': len(panel['group_records']),
    'recomputed_allocation_groups_exact': len(decomposition['groups']),
    'recomputed_regional_rows_exact': len(decomposition['regional']),
    'source_hash_checks': hash_checks,
    'lme027_overlays_unchanged': True,
    'historical_outputs_used_only_as_independent_row_checks': True,
    'engine_invocations': 0,
}
(STUDY / 'evidence/source_subset_verification.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
print(json.dumps(evidence, indent=2))
