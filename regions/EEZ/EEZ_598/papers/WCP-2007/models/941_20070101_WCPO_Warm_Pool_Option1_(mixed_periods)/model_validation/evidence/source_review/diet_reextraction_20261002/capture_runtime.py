"""Load only, with pinned code. No diagnostics or scientific-output adoption."""
from pathlib import Path
import sys, json, math, hashlib, contextlib
import numpy as np
import pandas as pd

code, inp, output, settings_file = map(Path, sys.argv[1:5])
sys.path.insert(0, str(code.resolve()))
from ModelData import ModelData
from PPRCalculator import PPRCalculator

def pack(x, depth=0):
    if isinstance(x, np.generic): return pack(x.item(), depth)
    if isinstance(x, float) and not math.isfinite(x): return {'nonfinite':str(x)}
    if x is None or isinstance(x, (str,int,float,bool)): return x
    if isinstance(x, pd.DataFrame):
        return {'type':'DataFrame','index':pack(x.index.tolist()),'columns':pack(x.columns.tolist()),'values':pack(x.to_numpy().tolist())}
    if isinstance(x, pd.Series):
        return {'type':'Series','index':pack(x.index.tolist()),'name':pack(x.name),'values':pack(x.tolist())}
    if isinstance(x, np.ndarray): return {'type':'ndarray','shape':list(x.shape),'values':pack(x.tolist())}
    if isinstance(x, dict): return {str(k):pack(v,depth+1) for k,v in x.items()}
    if isinstance(x, (tuple,list)): return [pack(v,depth+1) for v in x]
    if hasattr(x,'__dict__') and depth < 3:
        return {'type':type(x).__name__,'attributes':{k:pack(v,depth+1) for k,v in vars(x).items() if k not in ['balanced_model']}}
    return {'type':type(x).__name__,'representation':repr(x)}

output.mkdir(exist_ok=True)
settings=json.loads(settings_file.read_text(encoding='utf-8'))
with (output/'load.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    modeldata=ModelData(str(inp.resolve()))
    model=PPRCalculator.from_modeldata(modeldata,**settings)
    # All available ordinary loaded attributes, plus the separate cached balanced state.
    state={k:pack(v) for k,v in vars(model).items() if k!='balanced_model'}
    state['_cached_balanced_state']=pack(getattr(model,'balanced_model',None))
    (output/'state.json').write_text(json.dumps(state,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    model.get_groups_df().to_csv(output/'loaded_groups.csv')
    model._DC.to_csv(output/'loaded_diet.csv')
    model._det_fate.to_csv(output/'loaded_detritus_fate.csv')
    modeldata.DC.to_csv(output/'raw_loaded_diet.csv')
    for key in ['diet_normalization_rows','diet_normalization_balance_ledger']:
        value=getattr(model,key,None)
        if isinstance(value,pd.DataFrame): value.to_csv(output/(key+'.csv'))
    (output/'settings.json').write_text(json.dumps(settings,indent=2),encoding='utf-8')
print(json.dumps({'output':str(output),'state_keys':list(state),'input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest()}))
