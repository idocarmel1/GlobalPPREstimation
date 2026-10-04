"""Compare finalized blind extraction; never repair or adopt either model."""
import collections
import decimal
import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
RUN = Path(__file__).resolve().parent.parent
fresh = RUN / 'outputs/blind_extraction/model_2000s/model.json'
retained = ROOT / 'regions/LME/LME_036/papers/SCS-2007/models/36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)/model.json'
a, b = [json.loads(p.read_text(encoding='utf8')) for p in (fresh, retained)]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {str(p.relative_to(ROOT)): sha(p) for p in (fresh, retained)}
def value(v):
    if v is None: return ('null', None)
    try:
        number = decimal.Decimal(str(v))
        return ('missing_sentinel', None) if number == -9999 else ('number', number)
    except decimal.InvalidOperation:
        return ('text', v)
def differences(left, right):
    return value(left) != value(right)
groups_a = {g['group_seq']: g for g in a['group']}
groups_b = {g['group_seq']: g for g in b['group']}
assert list(groups_a) == list(groups_b)
name_changes = [{'group_seq': k, 'blind': groups_a[k]['group_name'], 'retained': groups_b[k]['group_name']}
                for k in groups_a if groups_a[k]['group_name'] != groups_b[k]['group_name']]
scalar_changes = []
checked = 0
basic_checked = basic_known = 0
basic_changes = []
for seq in groups_a:
    left, right = groups_a[seq], groups_b[seq]
    for field in left.keys() & right.keys():
        if field == 'diet_descr': continue
        checked += 1
        if differences(left[field], right[field]):
            item = {'group_seq': seq, 'field': field, 'blind': left[field], 'retained': right[field],
                    'blind_mask': value(left[field])[0], 'retained_mask': value(right[field])[0]}
            scalar_changes.append(item)
    for field in ['biomass', 'pb', 'qb', 'ee']:
        basic_checked += 1
        basic_known += value(left[field])[0] == 'number'
        if differences(left[field], right[field]): basic_changes.append({'group_seq': seq, 'field': field})
def diet(g):
    data = g.get('diet_descr')
    if not isinstance(data, dict): return {}
    entries = data['diet']
    if isinstance(entries, dict): entries = [entries]
    return {x['prey_seq']: x for x in entries}
numeric_changes, mask_changes, fate_changes = [], [], []
positive_a = positive_b = common_known = 0
for seq in groups_a:
    left, right = diet(groups_a[seq]), diet(groups_b[seq])
    for prey in groups_a:
        va = value(left[prey]['proportion']) if prey in left else ('omitted', None)
        vb = value(right[prey]['proportion']) if prey in right else ('omitted', None)
        positive_a += va[0] == 'number' and va[1] > 0
        positive_b += vb[0] == 'number' and vb[1] > 0
        if va[0] == vb[0] == 'number':
            common_known += 1
            if va[1] != vb[1]: numeric_changes.append({'consumer': seq, 'prey': prey, 'blind': str(va[1]), 'retained': str(vb[1])})
        elif va != vb:
            mask_changes.append({'consumer': seq, 'prey': prey, 'blind_mask': va[0], 'retained_mask': vb[0]})
        if prey in left and prey in right and differences(left[prey].get('detritus_fate'), right[prey].get('detritus_fate')):
            fate_changes.append({'consumer': seq, 'prey': prey})
roundtrip = json.loads((fresh.parent / 'SOURCE_FIDELITY_CHECK.json').read_text(encoding='utf8'))
load = json.loads((fresh.parent.parent / 'evidence/load_checks.json').read_text(encoding='utf8'))
result = {'role': 'independent original-publication extraction compared only after extracting agent finalized',
          'source_sha256': '87ea9ea00b6b71b896f89c0364bba09071f1683a71f5a66c71ea4da6bdbe3468',
          'model_hashes': before, 'group_ids_order_exact': True,
          'group_names_exact': not name_changes, 'group_name_differences': name_changes, 'groups': 38,
          'basic_parameter_cells_checked': basic_checked, 'known_basic_cells': basic_known,
          'basic_parameter_differences': basic_changes, 'scalar_cells_checked': checked,
          'scalar_difference_counts': dict(collections.Counter(x['field'] for x in scalar_changes)),
          'scalar_differences': scalar_changes, 'blind_positive_diets': positive_a,
          'retained_positive_diets': positive_b, 'common_known_diet_cells': common_known,
          'diet_numeric_differences': numeric_changes, 'diet_mask_difference_count': len(mask_changes),
          'diet_mask_difference_types': dict(collections.Counter(x['blind_mask'] + ' -> ' + x['retained_mask'] for x in mask_changes)),
          'diet_mask_differences': mask_changes, 'common_detritus_fate_differences': fate_changes,
          'roundtrip': roundtrip, 'load_checks': load,
          'interpretation': 'Known basic and positive diet equality does not establish canonical field/mask/provenance equality. Retained diet omissions differ from explicit missing source blanks; parameter role flags and source-unknown versus derived mortality/import values remain differences. Researcher taxonomy descriptions are intentionally preserved in the retained model. No adoption or repair.',
          'source_locator': 'Final Table 6.1(b), PDF191/printed176; Table 6.2 PDF193-194/printed178-179; diet Appendix 6.2 PDF357-363/printed342-348. Exact cell boxes in extraction companion ledger generated by reusable blind code.',
          'native_stanza_equations_reproduced': False, 'full_pipeline_replication': False,
          'live_scientific_writes': 0, 'frozen_comparison': {'rtol': 0, 'atol': 1e-12, 'decimal_known_inputs_exact': True}}
assert all(sha(ROOT / path) == wanted for path, wanted in before.items())
(RUN / 'qa/blind_extraction_comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({k: result[k] for k in ['groups', 'known_basic_cells', 'basic_parameter_differences', 'scalar_difference_counts', 'blind_positive_diets', 'retained_positive_diets', 'diet_numeric_differences', 'diet_mask_difference_count', 'diet_mask_difference_types']}))
