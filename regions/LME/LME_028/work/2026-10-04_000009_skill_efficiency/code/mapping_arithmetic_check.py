"""Independently reconcile current saved mapping/appendix arithmetic, without adoption."""
import collections
import hashlib
import json
import math
import sys
from pathlib import Path
import openpyxl

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
RUN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records, sha

path = ROOT / 'regions/LME/LME_036/LME_036.xlsx'
appendix = next((ROOT / 'regions/LME/LME_036/papers/SCS-2007/models').glob('*/model_validation/taxon_mapping.xlsx'))
hashes = {str(p): sha(p) for p in [path, appendix]}
book = read_book(path, sheets=['Catch', 'Classic PPR', 'PPR'])
catch = {r['taxon']: r[2019] for r in records(book, 'Catch', 'Catch') if r['catch_basis'] == 'landings'}
classic = {r['taxon']: r['sppr'] for r in records(book, 'Classic PPR', 'Taxa')}
matching = collections.defaultdict(list)
for row in records(book, 'PPR', 'Matching'): matching[row['taxon']].append(row)
assert set(matching) == set(catch), 'Mapping universe mismatch'
def finite(value): return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
def contribution(c, coefficient):
    if c == 0: return 0.0
    return c * coefficient / 9 if finite(c) and finite(coefficient) else None
expected = {taxon: contribution(c, classic.get(taxon)) for taxon, c in catch.items()}
assert contribution(0, None) == 0 and contribution(1, None) is None
weight_failures = []
for taxon, mappings in matching.items():
    weights = [row['weight'] for row in mappings]
    if all(finite(w) for w in weights) and abs(sum(weights) - 1) > 1e-12:
        weight_failures.append([taxon, sum(weights)])
workbook = openpyxl.load_workbook(appendix, read_only=True, data_only=False)
values = list(workbook['Taxon appendix'].values); workbook.close()
header_index = next(i for i, row in enumerate(values) if row and row[0] == 'Taxon name')
headers = list(values[header_index]); supplied = {}
for row in values[header_index + 1:]:
    if row[0] in catch:
        if row[0] in supplied: raise ValueError('Duplicate appendix taxon')
        supplied[row[0]] = dict(zip(headers, row))
assert set(supplied) == set(catch), 'Appendix universe mismatch'
ppr_column = next(h for h in headers if isinstance(h, str) and 'PPR' in h)
catch_column = next(h for h in headers if isinstance(h, str) and h.startswith('Catch'))
confidence_column = next(h for h in headers if isinstance(h, str) and h.startswith('Confidence'))
differences = []; masks = []; catch_differences = []; categories = collections.defaultdict(lambda: {'count': 0, 'catch_tonnes': 0.0, 'known_ppr_tC': 0.0})
maximum = 0.0
for taxon, row in supplied.items():
    actual = row[ppr_column]; wanted = expected[taxon]
    if finite(actual) != finite(wanted): masks.append([taxon, actual, wanted])
    elif finite(actual):
        delta = abs(actual - wanted); maximum = max(maximum, delta)
        if delta > 1e-12: differences.append({'taxon': taxon, 'appendix_tC': actual, 'recomputed_tC': wanted, 'absolute_difference': delta})
    if row[catch_column] != catch[taxon]: catch_differences.append(taxon)
    category = categories[row[confidence_column]]; category['count'] += 1
    if finite(catch[taxon]): category['catch_tonnes'] += catch[taxon]
    if finite(wanted): category['known_ppr_tC'] += wanted
total = sum(value for value in expected.values() if finite(value))
order = list(supplied)
expected_order = sorted(supplied, key=lambda t: (not finite(supplied[t][ppr_column]), -supplied[t][ppr_column] if finite(supplied[t][ppr_column]) else 0, t))
result = {'role': 'independent arithmetic and complete-universe checks on intentionally supplied saved coefficients/mapping/appendix; source mapping interpretation reused',
          'unit_id': 'LME_036', 'year': 2019, 'basis': 'landings', 'method': 'independent simple trophic chain',
          'input_hashes': hashes, 'taxa': len(catch), 'mapping_rows': sum(map(len, matching.values())),
          'split_taxa': sum(len(v) > 1 for v in matching.values()), 'all_taxa_in_appendix_once': True,
          'zero_catch_missing_coefficient_taxa': [t for t in catch if catch[t] == 0 and not finite(classic.get(t))],
          'positive_catch_missing_coefficient_taxa': [t for t in catch if finite(catch[t]) and catch[t] > 0 and not finite(classic.get(t))],
          'synthetic_missing_coefficient_behavior': {'zero_catch': 0.0, 'positive_catch': None, 'real_replication': False},
          'carbon_conversion': 'wet-weight catch * retained classic coefficient / 9 exactly once',
          'known_ppr_denominator_tC': total, 'catch_denominator_tonnes': sum(v for v in catch.values() if finite(v)),
          'categories': dict(categories), 'weight_failures': weight_failures, 'catch_differences': catch_differences,
          'missing_mask_differences': masks, 'rtol': 0, 'atol': 1e-12,
          'maximum_absolute_difference_tC': maximum, 'changed_numeric_keys': differences,
          'appendix_order_matches_unrounded_saved_numeric_values': order == expected_order,
          'source_mapping_confidence_and_assumptions': 'consumed and preserved, not independently re-researched',
          'no_scientific_adoption': True, 'full_pipeline_replication': False}
assert all(sha(Path(p)) == h for p, h in hashes.items())
(RUN / 'qa/mapping_arithmetic_check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({k: result[k] for k in ['taxa', 'mapping_rows', 'split_taxa', 'known_ppr_denominator_tC', 'maximum_absolute_difference_tC', 'appendix_order_matches_unrounded_saved_numeric_values']}))
print('numeric discrepancies', len(differences), 'mask discrepancies', len(masks), 'weight failures', len(weight_failures))
