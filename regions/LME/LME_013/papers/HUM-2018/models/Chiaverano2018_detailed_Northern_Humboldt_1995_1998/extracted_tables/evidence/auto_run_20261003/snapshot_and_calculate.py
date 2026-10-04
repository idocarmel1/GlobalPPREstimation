from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=BASE.parents[3]
assert json.loads((OUT/'preflight_result.json').read_text())['passed']
before=json.loads((OUT/'active_baseline.json').read_text(encoding='utf-8'))
snapshot=OUT/'baseline'
assert not snapshot.exists()
for rel,expected in before.items():
    p=ROOT/rel
    assert hashlib.sha256(p.read_bytes()).hexdigest()==expected, f'Changed before snapshot: {rel}'
    if rel in ['Project.xlsx','regions/LME_013/LME_013.xlsx'] or p.suffix in ['.docx','.xlsx','.html']:
        target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
code=(BASE/'diagnostics/calculate_candidate.py').read_text(encoding='utf-8')
code=code.replace("'FAIL coefficients retained for arithmetic-only investigation; no active adoption or publication.'", "'Explicitly authorized provisional selection; actual FAIL grades and production ineligibility preserved.'")
(OUT/'calculate_auto.py').write_text(code,encoding='utf-8')
summary=(BASE/'diagnostics/summarize_direct.py').read_text(encoding='utf-8')
(OUT/'summarize_direct.py').write_text(summary,encoding='utf-8')
print('Preflight verified; protected active files snapshotted. Arithmetic script prepared.',flush=True)
