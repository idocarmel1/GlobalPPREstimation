"""Fill registry assertions only from the exact independently reloaded model."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FINAL = HERE.parents[1] / 'assumption_variants/adopted_balanced_20261003'
gate = json.loads((HERE/'independent_final_gate.json').read_text(encoding='utf-8'))
assert gate['all_checks_passed'] and gate['actual_returned_main_balanced']
diagnostics = json.loads((FINAL/'diagnostics/summary.json').read_text(encoding='utf-8'))
grades = '; '.join(f"{name} {entry['report']['status']}" for name,entry in diagnostics.items())
spec_path = HERE/'registry_patch_spec.json'
spec = json.loads(spec_path.read_text(encoding='utf-8'))
spec['expected_model_sha256'] = gate['native_model_sha256']
spec['model']['availability'] = (
    'Exact persisted native carbon model reloads with main balance true and finite physically admissible flows. '
    '22 biological groups plus native external-food import; catch/migration zero; all living BA zero; '
    'detritus BA positive; GS solved by standard LIM. '+grades+'. '
    'Zero model catch and four terminal groups with EE=0 retain diagnostic warnings. '
    'Twelve explicit decimal-flow hypotheses and source-supported plus assumed diets are reconstruction assumptions, '
    'not established author corrections. Scientific validation remains pending; provisional regional coefficients '
    'retain method flags and the documented group-specific carbon bridge. Evidence: '
    'regions/LME_052/models/52_GM2019_Fig9_Pelagic_(2000-2014)/assumption_variants/adopted_balanced_20261003/'
)
description = 'Derived native reconstruction loads and physically balances; '+grades+'; scientific validation pending'
spec['paper']['loadability_class'] = description
spec['paper']['full_model_loadable'] = description
spec_path.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Registry assertions tied to final native SHA256 '+gate['native_model_sha256'])
