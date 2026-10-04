"""Refresh source documentation and evidence hashes without changing model inputs."""
from pathlib import Path
import hashlib, json, re

R = Path(__file__).resolve().parent
input_paths = [R / 'resolved_native/model.json', R / 'computational/model.json']
before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths}

for name in ['REPORT.md', 'REPORT.template.md']:
    p = R / name
    text = p.read_text(encoding='utf-8').replace('6,823 exact/numeric comparisons', '23,838 exact/numeric comparisons')
    old = 'Fleet nodes 40/41 send their discard fate entirely to Offal 37.'
    new = ('Fleet nodes 40/41 send their discard fate entirely to Offal 37. '
           'Neither detailed Table B nor aggregate Table F supplies a fleet diet column; '
           '[FIELD_AVAILABILITY.json](resolved_native/FIELD_AVAILABILITY.json) records this missingness explicitly.')
    if '[FIELD_AVAILABILITY.json]' not in text:
        text = text.replace(old, new)
    p.write_text(text, encoding='utf-8')

for name in ['README', 'MODEL_PROFILE']:
    (R / (name + '.template.md')).write_text((R / (name + '.md')).read_text(encoding='utf-8'), encoding='utf-8')

p = R / 'finalize_source.py'
code = p.read_text(encoding='utf-8')
code = code.replace("(R/'MODEL_PROFILE.md').write_text(profile,encoding='utf-8')",
                    "(R/'MODEL_PROFILE.md').write_text((R/'MODEL_PROFILE.template.md').read_text(encoding='utf-8'),encoding='utf-8')")
code, count = re.subn(r"\(R/'README\.md'\)\.write_text\('''.*?''',encoding='utf-8'\)",
                      "(R/'README.md').write_text((R/'README.template.md').read_text(encoding='utf-8'),encoding='utf-8')", code, flags=re.S)
if count not in [0, 1]:
    raise RuntimeError('Unexpected README generator match count')
if "'methods':[]" not in code:
    code = code.replace("'methods_options':", "'methods':[],'methods_options':")
code = code.replace("'recovery_record':'RECOVERY_SEARCH.json'", "'recovery_record':'RECOVERY_SEARCH.json','field_availability':'resolved_native/FIELD_AVAILABILITY.json','source_identity_metadata':'SOURCE_IDENTITY.json','readme':'README.md','group_identity':'resolved_native/GROUP_IDENTITY.json','catch_biomass_vector':'resolved_native/GROUP_CATCH_BIOMASS.csv'")
compile(code, str(p), 'exec')
p.write_text(code, encoding='utf-8')

index_path = R / 'evidence_index.json'
index = json.loads(index_path.read_text(encoding='utf-8'))
index['methods'] = []
extra = {'field_availability': 'resolved_native/FIELD_AVAILABILITY.json',
         'source_identity_metadata': 'SOURCE_IDENTITY.json', 'readme': 'README.md',
         'group_identity': 'resolved_native/GROUP_IDENTITY.json',
         'catch_biomass_vector': 'resolved_native/GROUP_CATCH_BIOMASS.csv'}
existing = {a['role'] for a in index['artifacts']}
for role, path in extra.items():
    if role not in existing:
        index['artifacts'].append({'role': role, 'path': path, 'availability': 'present'})
    if role not in index['required_roles']:
        index['required_roles'].append(role)
for artifact in index['artifacts']:
    if artifact['availability'] == 'present':
        artifact['sha256'] = hashlib.sha256((R / artifact['path']).read_bytes()).hexdigest()
index['reconciliation']['extended_23838_source_field_checks'] = json.loads((R / 'resolved_native/ROUND_TRIP_CHECKS.json').read_text(encoding='utf-8'))['passed']
after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths}
if before != after:
    raise RuntimeError('Frozen model input changed during documentation refresh')
index['reconciliation']['frozen_model_inputs_unchanged'] = True
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
print(json.dumps({'input_hashes_unchanged': before == after, 'source_field_checks': 23838,
                  'available_indexed_artifacts': sum(a['availability'] == 'present' for a in index['artifacts'])}, ensure_ascii=False))
