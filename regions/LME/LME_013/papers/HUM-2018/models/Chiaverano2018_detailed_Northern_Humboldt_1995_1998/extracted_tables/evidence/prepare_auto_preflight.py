"""Prepare isolated auto diagnostics; never mutate existing scientific evidence."""
from pathlib import Path
import hashlib, json

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
OUT = BASE / 'auto_run_20261003'
OUT.mkdir(exist_ok=False)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

protected = [ROOT / 'Project.xlsx']
protected += [p for folder in [ROOT/'regions/LME_013', ROOT/'interactive_map', ROOT/'tools/knowledge_graph']
              for p in folder.rglob('*') if p.is_file() and OUT not in p.parents
              and '__pycache__' not in p.parts and 'vendor' not in p.parts]
baseline = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected}
(OUT/'protected_before.json').write_text(json.dumps(baseline, indent=2, ensure_ascii=False), encoding='utf-8')

original = BASE/'diagnostics/run_direct_candidate.py'
code = original.read_text(encoding='utf-8')
code = code.replace('HERE / "vendor"', 'HERE.parent / "diagnostics" / "vendor"')
code = code.replace('det_collapse_mode="never"', 'det_collapse_mode="auto"')
code = code.replace("'HUM2018_20261003_detailed_source_candidate'", "'HUM2018_20261003_auto_preflight'")
code = code.replace("'not authorized; candidate evidence only'", "'Conditional selection authorized only after all preflight conditions pass; no researcher verdict authorized'")
# Preserve the entire actual return before any convenience summary could fail.
code = code.replace("manifest['runtime_before_sha256']", "shutil.copyfile(Path(__file__), code_folder/'run_direct_auto.py')\n    manifest['runtime_before_sha256']")
(OUT/'run_direct_auto.py').write_text(code, encoding='utf-8')
old = json.loads((BASE/'diagnostics/run_manifest.json').read_text(encoding='utf-8'))
engine = {n: sha(ROOT/'tools/scientific_code/PPREstimation'/n) for n in old['engine']}
checks = {'previous_engine_hashes_equal_current': engine == old['engine'],
          'audited_input_matches_previous': sha(BASE/'source/computational/model.json') == old['input_sha256'],
          'original_driver_sha256': sha(original), 'engine': engine,
          'never_manifest_sha256': sha(BASE/'diagnostics/run_manifest.json'),
          'canonical_source_sha256': sha(BASE/'source/resolved_native/model.json'),
          'computational_input_sha256': sha(BASE/'source/computational/model.json')}
(OUT/'comparison_setup.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
assert checks['previous_engine_hashes_equal_current'], 'Engine changed: cannot claim only mode changed.'
assert checks['audited_input_matches_previous'], 'Audited computational input changed.'
print(json.dumps(checks, indent=2))
