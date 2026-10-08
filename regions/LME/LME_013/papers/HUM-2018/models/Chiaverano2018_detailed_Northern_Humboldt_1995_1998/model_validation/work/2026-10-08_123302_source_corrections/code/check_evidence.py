"""Check retained correction evidence and its scope without recalculating SPPR."""
from pathlib import Path
import csv
import hashlib
import json
import math

RUN = Path(__file__).resolve().parents[1]
MODEL = Path(__file__).resolve().parents[4]
REPO = next(p for p in MODEL.parents if (p/'Project.xlsx').exists())
OUT = RUN/'outputs'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

index = read(OUT/'evidence_index.json')
audit = read(OUT/'correction_scenarios.json')
for rel, expected in index['consumed_scientific_inputs'].items():
    assert sha(REPO/rel)==expected, rel
for item in index['artifacts']:
    assert sha(MODEL/item['path'])==item['sha256'], item['path']
for item in index['context_sources']:
    assert sha(MODEL.parents[1]/'sources'/item['path'])==item['sha256']
assert len(audit['scenarios']) == 16
matrix = {r['prey_group_seq']:r for r in audit['matrix_diet_reconstruction']}
assert matrix[1]['Acp']==matrix[6]['Acp']==0
assert abs(matrix[4]['diet_from_Acp_times_Qprey_over_Qjellyfish']-.68)<1e-7
assert abs(matrix[5]['diet_from_Acp_times_Qprey_over_Qjellyfish']-.17)<1e-7
with (OUT/'living_group_residuals.csv').open(encoding='utf-8',newline='') as f:
    rows=list(csv.DictReader(f))
checks=[]
for rec in audit['scenarios']:
    group_rows=[r for r in rows if r['scenario']==rec['scenario'] and
                r['runtime_BA_compensation']==str(rec['runtime_BA_compensation'])]
    assert len(group_rows)==35
    assert all(math.isfinite(float(r['residual'])) for r in group_rows)
    checks.append(dict(scenario=rec['scenario'],runtime_BA_compensation=rec['runtime_BA_compensation'],
        balanced=rec['balanced'],max_living_abs_residual=max(abs(float(r['residual'])) for r in group_rows),
        max_living_absolute_percent_residual=max(abs(float(r['percent_residual'])) for r in group_rows)))
    if 'reestimate_EE' in rec['scenario'] or rec['scenario']=='production_matrix_diet_only':
        assert rec['balanced']
        if not rec['runtime_BA_compensation']:
            assert rec['living_max_abs_BA']==0
    if 'reestimate_EE' in rec['scenario']:
        sardine=next(r for r in group_rows if r['group_seq']=='9')
        calculated=(float(sardine['predation'])+float(sardine['catch']))/float(sardine['production'])
        assert abs(calculated-rec['sardine_EE'])<1e-12
        assert abs(rec['native_pool_budget_with_reestimated_EE_zero_BA'][0]['reestimated_EE']-.8843322396278381)<1e-7
        assert abs(rec['native_pool_budget_with_reestimated_EE_zero_BA'][3]['reestimated_EE']-.8885209520422097)<1e-12
result=dict(status='PASS',scope='Evidence integrity and saved balance calculations; not approval or SPPR readiness',
            input_hashes_unchanged=True,context_hashes_verified=True,runs=checks)
(RUN/'qa/verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
