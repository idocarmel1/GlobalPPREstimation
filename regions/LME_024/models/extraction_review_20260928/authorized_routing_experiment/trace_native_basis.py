from pathlib import Path
import pickle,json,traceback
import numpy as np
import pandas as pd
from routing_adapter import RoutingExperimentCalculator,PPRCalculator
OUT=Path(__file__).resolve().parent
c=pickle.loads((OUT/'faithful_printed_BA_state.pkl').read_bytes())
try:
 PPRCalculator.SPPR_new(c,TE_option='GE')
except Exception as exc:
 tb=exc.__traceback__;rows=[]
 while tb:
  frame=tb.tb_frame
  if frame.f_code.co_name=='SPPR_new' and frame.f_code.co_filename.endswith('PPRCalculator.py'):
   loc=frame.f_locals
   info={k:loc[k] for k in ['new_index','new_columns','DET_seq'] if k in loc}
   for k in ['SPPR','A','L','DC','GE']:
    if k in loc and isinstance(loc[k],pd.DataFrame):
     loc[k].to_csv(OUT/f'native_basis_failure_{k}.csv')
     info[k]={'shape':loc[k].shape,'columns':loc[k].columns.tolist(),'index':loc[k].index.tolist()}
   info['n_nullspace_vectors']=len(loc.get('ns',[]))
   if 'rref_matrix' in loc: info['rref_shape']=loc['rref_matrix'].shape
   rows.append(info)
  tb=tb.tb_next
 (OUT/'native_basis_failure_trace.json').write_text(json.dumps({'exception':repr(exc),'frames':rows},indent=2,default=lambda v:v.item() if isinstance(v,np.generic) else str(v)),encoding='utf8')
 print((OUT/'native_basis_failure_trace.json').read_text(encoding='utf8'))
