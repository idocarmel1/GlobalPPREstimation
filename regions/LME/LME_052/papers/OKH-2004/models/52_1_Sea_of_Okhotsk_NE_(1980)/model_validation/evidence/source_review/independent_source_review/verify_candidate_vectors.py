"""Read-only regional QA. Only writes independent review output beside this script."""
from pathlib import Path
from decimal import Decimal
import collections, hashlib, json, math, sys

OUT = Path(__file__).resolve().parent
ROOT = next(p for p in OUT.parents if (p / 'regions/LME_052').is_dir() and (p / 'tools').is_dir())
MID = '52_1_Sea_of_Okhotsk_NE_(1980)'
REGION = ROOT / 'regions/LME_052'
EVIDENCE = REGION / 'validation_reports' / MID
CANONICAL = REGION / 'models' / MID / 'model.json'
sys.path.insert(0, str(ROOT / 'tools'))
import workbooks as W

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def same(actual, expected, label):
    assert math.isclose(actual, expected, rel_tol=2e-13, abs_tol=2e-14), (label, actual, expected)

assert sha(CANONICAL) == '61b6176affe6051948b3ec972fe87d95dabd8d98b66744b4c7350fcf303b9099'
input_paths = [CANONICAL, REGION / 'LME_052.xlsx', EVIDENCE / 'taxon_audit.json',
               EVIDENCE / 'candidate_and_allocation_evidence.json', EVIDENCE / 'coverage_summary.json',
               OUT / 'native_basic_parameter_ledger.json']
if '--verify-adopted' in sys.argv:
    input_paths.append(EVIDENCE / 'adoption_record.json')
input_hashes = {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in input_paths}
audit = read(EVIDENCE / 'taxon_audit.json')
candidates = read(EVIDENCE / 'candidate_and_allocation_evidence.json')
coverage = read(EVIDENCE / 'coverage_summary.json')
native = read(OUT / 'native_basic_parameter_ledger.json')
canonical = read(CANONICAL)
model = {int(g['group_seq']): g for g in canonical['group']}
source = {g['id']: g for g in native['rows']}
biomass = {s: Decimal(r['printed_cells']['biomass']) for s, r in source.items() if r['printed_cells']['biomass']}
book = W.read_book(REGION / 'LME_052.xlsx')
catch = {r['taxon']: r for r in W.records(book, 'Catch', 'Catch') if r['catch_basis'] == 'landings'}
classic = {r['taxon']: r for r in W.records(book, 'Classic PPR', 'Taxa')}
groups = {int(r['seq']): r for r in W.records(book, 'Selected model groups', 'Groups')}
rank = ['Unresolved', 'Very low', 'Low', 'Medium', 'High']
assert len(audit) == len(candidates) == len(catch) == 151
assert len({r['taxon'] for r in audit}) == len(audit)
assert len({r['taxon'] for r in candidates}) == len(candidates)
assert {r['taxon'] for r in audit} == set(catch) == {r['taxon'] for r in candidates}
candidate_by_taxon = {r['taxon']: r for r in candidates}
checks = []
max_vector_error = 0.0
for row in audit:
    taxon = row['taxon']
    c = candidate_by_taxon[taxon]
    ids = row['group_ids']
    weights = row['weights']
    assert len(ids) == len(set(ids)) == len(weights)
    assert ids == [r['seq'] for r in c['included']]
    excluded = [r['seq'] for r in c['excluded']]
    assert len(excluded) == len(set(excluded))
    assert not set(ids) & set(excluded)
    assert set(ids) | set(excluded) == set(groups), taxon
    assert 30 not in ids, 'Synthetic diet-import group is not a biological catch candidate'
    assert row['group_names'] == [model[s]['group_name'] for s in ids]
    assert row['membership_rule'] == c['membership_rule']
    assert row['allocation_rule'] == c['allocation_rule']
    assert row['overall_confidence'] == min([row['membership_confidence'], row['allocation_confidence']], key=rank.index)
    same(row['catch_tonnes'], catch[taxon][2019], (taxon, 'catch'))
    assert row['common_name'] == catch[taxon]['common_name']
    assert row['functional_group'] == catch[taxon]['functional_group']
    assert row['tl'] == classic.get(taxon, {}).get('tl')
    assert row['classic_sppr'] == classic.get(taxon, {}).get('sppr')
    if not W.finite(row['classic_sppr']):
        assert row['catch_tonnes'] == 0, (taxon, 'missing classic coefficient with nonzero catch')
    for rec in c['included']:
        s = rec['seq']
        assert rec['group'] == model[s]['group_name']
        assert rec['source_catch'] is None
        assert rec['canonical_export'] == model[s]['export'] == '0'
        assert rec['loaded_catch'] == groups[s]['catch'] == 0
        same(rec['source_biomass'], float(biomass[s]), (taxon, s, 'source B'))
    if not ids:
        assert not weights and row['overall_confidence'] == 'Unresolved'
        assert row['allocation_rule'] == 'W8'
    elif len(ids) == 1:
        assert weights == [1.0]
        assert row['allocation_rule'] == 'W1' and row['allocation_confidence'] == 'High'
    else:
        assert row['allocation_rule'] == 'W9' and row['allocation_confidence'] == 'Medium'
        assert c['catch_vector_complete'] is False and c['catch_total'] is None
        total = sum((biomass[s] for s in ids), Decimal(0))
        same(c['biomass_total'], float(total), (taxon, 'B total'))
        for s, weight in zip(ids, weights):
            expected = float(biomass[s] / total)
            max_vector_error = max(max_vector_error, abs(weight - expected))
            same(weight, expected, (taxon, s, 'W9'))
        same(math.fsum(weights), 1, (taxon, 'sum'))
    assert all(math.isfinite(w) and 0 <= w <= 1 for w in weights)
    for rec, weight in zip(c['included'], weights):
        same(rec['weight'], weight, (taxon, 'candidate weight'))
    checks.append({'taxon': taxon, 'included': ids, 'excluded': excluded,
                   'weights': weights, 'overall_confidence': row['overall_confidence'],
                   'zero_catch': row['catch_tonnes'] == 0,
                   'candidate_partition_and_vector_verified': True})

expected_broad = {
    'Actinopterygii': list(range(6, 20)),
    'Marine fishes not identified': list(range(6, 20)),
    'Marine pelagic fishes not identified': [6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 19],
    'Miscellaneous aquatic invertebrates': list(range(20, 27)),
    'Miscellaneous marine crustaceans': [20, 23, 24, 25, 26],
    'Mollusca': [21, 23, 24],
    'Gadus chalcogrammus': [6, 7],
    'Gadidae': [6, 7, 12],
    'Perciformes': [8, 9, 14, 15, 16, 19],
    'Panulirus': [20, 23],
    'Squillidae': [20, 23],
}
audit_by_taxon = {r['taxon']: r for r in audit}
for taxon, ids in expected_broad.items():
    assert audit_by_taxon[taxon]['group_ids'] == ids, taxon
pollock = audit_by_taxon['Gadus chalcogrammus']
same(pollock['weights'][0], float(Decimal('2.475') / Decimal('4.594')), 'adult pollock')
same(pollock['weights'][1], float(Decimal('2.119') / Decimal('4.594')), 'juvenile pollock')
total_catch = math.fsum(r['catch_tonnes'] for r in audit)
same(coverage['total_catch_tonnes'], total_catch, 'coverage total catch')
for summary in coverage['confidence_summary']:
    rows = [r for r in audit if r['overall_confidence'] == summary['label']]
    assert summary['taxa'] == len(rows)
    same(summary['catch_tonnes'], math.fsum(r['catch_tonnes'] for r in rows), ('coverage', summary['label']))
assert input_hashes == {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in input_paths}, 'Input changed during verification; rerun on stable bytes'
adopted_matching_verified = False
if '--verify-adopted' in sys.argv:
    adoption = read(EVIDENCE / 'adoption_record.json')
    assert adoption['workbook_sha256'] == sha(REGION / 'LME_052.xlsx')
    assert adoption['canonical_model_sha256'] == sha(CANONICAL)
    assert adoption['taxa'] == 151
    matching = collections.defaultdict(list)
    for row in W.records(book, 'PPR', 'Matching'):
        if row['model_id'] == MID:
            matching[row['taxon']].append(row)
    assert set(matching) == set(audit_by_taxon)
    for taxon, row in audit_by_taxon.items():
        actual = matching[taxon]
        if not row['group_ids']:
            assert len(actual) == 1 and actual[0]['group'] is None and actual[0]['weight'] is None
            assert actual[0]['confidence'] == 'unresolved'
        else:
            assert len(actual) == len(row['group_ids'])
            actual_by_group = {r['group']: r for r in actual}
            assert set(actual_by_group) == set(row['group_names'])
            for name, weight in zip(row['group_names'], row['weights']):
                same(actual_by_group[name]['weight'], weight, (taxon, name, 'adopted matching'))
                assert actual_by_group[name]['confidence'] == row['overall_confidence'].lower().replace(' ', '_')
                assert actual_by_group[name]['explanation'] == row['reason']
    assert input_hashes == {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in input_paths}, 'Input changed during adopted verification'
    adopted_matching_verified = True
result = {
    'status': 'PASS numeric, label, confidence and candidate-partition checks; scientific limitations remain',
    'scope': 'Every draft label including zero catch; no solver, Monte Carlo or production writer called',
    'selected_model_id': MID,
    'input_hashes': input_hashes,
    'input_hashes_unchanged_during_verification': True,
    'adopted_workbook_matching_verified': adopted_matching_verified,
    'taxa': len(audit),
    'zero_catch_taxa': sum(r['catch_tonnes'] == 0 for r in audit),
    'split_taxa': sum(len(r['group_ids']) > 1 for r in audit),
    'confidence_counts': dict(collections.Counter(r['overall_confidence'] for r in audit)),
    'all_candidate_partitions_complete_for_current_loaded_groups': True,
    'biological_source_groups': 29,
    'synthetic_group30_excluded_everywhere': True,
    'maximum_W9_vector_absolute_error_vs_native_Decimal_B': max_vector_error,
    'pollock': {'source_biomass': [2.475, 2.119], 'weights': pollock['weights'],
                'catch_scope': '2019 all-source landings, all taxa, no group filter',
                'catch_tonnes': pollock['catch_tonnes'], 'total_catch_tonnes': total_catch,
                'catch_share_percent': 100 * pollock['catch_tonnes'] / total_catch,
                'allocation_confidence': pollock['allocation_confidence'],
                'stage_caught_mass_or_cutoff_recovered': False},
    'unresolved': [r['taxon'] for r in audit if r['overall_confidence'] == 'Unresolved'],
    'limits': ['Partition arithmetic does not demonstrate unknown guild species composition.',
               'All native group catch observations remain unavailable; canonical zero is not observed catch.',
               'Catch share is bound to this 2019 scope, not the older coordinator estimate or every year.',
               'No independent SPPR matrix solve was requested or performed.',
               'This is not scientific approval of the model or shared production eligibility.'],
    'rows': checks,
}
(OUT / 'candidate_vector_verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, ensure_ascii=False, indent=2))
