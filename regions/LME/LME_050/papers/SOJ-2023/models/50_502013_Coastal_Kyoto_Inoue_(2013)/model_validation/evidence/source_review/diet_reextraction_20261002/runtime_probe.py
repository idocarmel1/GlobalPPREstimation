"""Read-only loader probe; never calls diagnose_sppr or writes canonical inputs."""
from pathlib import Path
import json, sys, math, inspect, hashlib
sys.dont_write_bytecode = True
import pandas as pd

root = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
model = root / 'regions/LME_050/models/50_502013_Coastal_Kyoto_Inoue_(2013)'
code = model / 'diagnostic_code' if sys.argv[1] == 'historical' else root / 'tools/scientific_code/PPREstimation'
sys.path.insert(0, str(code))
code_hashes = {n: hashlib.sha256((code/n).read_bytes()).hexdigest() for n in ['ModelData.py', 'PPRCalculator.py', 'utils.py']}
from ModelData import ModelData
from PPRCalculator import PPRCalculator

def clean(x):
    if isinstance(x, dict): return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [clean(v) for v in x]
    if isinstance(x, float) and not math.isfinite(x): return {'nonfinite': str(x)}
    if hasattr(x, 'tolist'): return clean(x.tolist())
    if hasattr(x, 'item'): return clean(x.item())
    return x

md = ModelData(str(model / 'evidence/50_502013_Coastal_Kyoto_Inoue_(2013).json'))
settings = dict(underdetermined=True, zero_catch=True, zero_biomass_accum=False,
                default_gs=True, weight_flow=1.0, weight_guess=1.0,
                DC_tol=0.001, normalize_DC=True)
m = PPRCalculator.from_modeldata(md, **settings)
loaded = {}
for key, val in vars(m).items():
    if isinstance(val, pd.DataFrame):
        loaded[key] = {'kind': 'DataFrame', 'index': val.index.tolist(), 'columns': val.columns.tolist(), 'data': clean(val.values.tolist())}
    elif isinstance(val, pd.Series):
        loaded[key] = {'kind': 'Series', 'index': val.index.tolist(), 'data': clean(val.tolist())}
    elif isinstance(val, (str, int, float, bool, dict, list, tuple, type(None))):
        try:
            json.dumps(clean(val)); loaded[key] = clean(val)
        except TypeError: pass
out = Path(__file__).parent / ('loaded_state_' + sys.argv[1] + '.json')
code_after = {n: hashlib.sha256((code/n).read_bytes()).hexdigest() for n in code_hashes}
assert code_after == code_hashes, 'Concurrent runtime code changed during probe'
out.write_text(json.dumps({'settings': settings, 'code_sha256': code_hashes, 'loaded_state': loaded}, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
print(json.dumps({'output': str(out), 'state_keys': len(loaded), 'diagnostics_called': False}))
