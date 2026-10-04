"""Independent JSON-input/missingness check; no paper extraction or construction claim."""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
RUN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools/scientific_code/PPREstimation'))
from ModelData import ModelData

path = ROOT / 'regions/LME/LME_047/ecobase/47_1_East_China_Sea_(1997)/model.json'
original = path.read_bytes()
raw = json.loads(original)
model = ModelData(str(path))
assert model.data_json == raw
ids = [int(float(group['group_seq'])) for group in raw['group']]
assert len(ids) == len(set(ids))
assert {model.seq2name[seq] for seq in ids} == {group['group_name'] for group in raw['group']}
fields = ['biomass', 'pb', 'qb', 'ee', 'gs', 'biomass_accum', 'emigration', 'immigration', 'respiration']
mask = []; mismatches = []; maximum = 0.0; checked = 0
for group in raw['group']:
    seq = int(float(group['group_seq']))
    for field in fields:
        source = group.get(field)
        missing = source is None or str(source) in {'', '-9999', '-9999.0', '-9999.000'}
        actual = model.groups_data.at[seq, field]
        mask.append([seq, field, missing])
        checked += 1
        if missing:
            if not math.isnan(float(actual)): mismatches.append([seq, field, 'source missing', float(actual)])
        else:
            difference = abs(float(source) - float(actual)); maximum = max(maximum, difference)
            if difference > 1e-12: mismatches.append([seq, field, float(source), float(actual)])
assert not mismatches, mismatches
assert path.read_bytes() == original
result = {'role': 'independent consumption and loader check of supplied JSON-only input; not independent paper extraction',
          'source': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(original).hexdigest(),
          'source_provenance_limit': 'No distinct original native/publication input established in current package; model-name year is not new source provenance',
          'model_identity': {'number': model.model_number, 'year': model.model_year},
          'groups': len(ids), 'fields_checked': checked, 'missing_cells': sum(row[2] for row in mask),
          'raw_missing_mask_sha256': hashlib.sha256(json.dumps(mask).encode()).hexdigest(),
          'source_json_exactly_preserved': True, 'parsed_source_dictionary_exact': True,
          'group_ids_and_names_exact': True, 'source_parameter_masks_exact_in_loader': True,
          'rtol': 0, 'atol': 1e-12, 'maximum_absolute_difference': maximum, 'changed_keys': [],
          'engine_load_calls': 1, 'construction_calls': 0, 'diagnostic_calls': 0,
          'runtime_transformations': 'Synthetic diet_import group and runtime diet/detritus fill semantics belong to ModelData; no canonical default/repair written',
          'diet_and_native_conversion_replication': 'not independently converted; raw diet fields preserved in unchanged input',
          'full_pipeline_replication': False}
(RUN / 'qa/json_input_check.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
print(json.dumps({k: result[k] for k in ['groups', 'fields_checked', 'missing_cells', 'maximum_absolute_difference']}))
