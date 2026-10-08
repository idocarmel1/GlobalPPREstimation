from pathlib import Path
import sys,json,numpy as np
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
OUT=ROOT/'regions/EEZ_941/models/941_20190101_Warm_Pool_Detritus_Pooled_Experiment_(2005)';DIAG=OUT/'diagnostics'
sys.path.insert(0,str(DIAG/'executed_code'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
d=ModelData(str(OUT/(OUT.name+'.json')));d.groups_data.loc[d.groups_data.trophic_info!='Import','net_migration']=0.
c=PPRCalculator.from_modeldata(d,underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=True,normalize_DC=False,DC_tol=.001)
c._groups_df.to_csv(DIAG/'groups_after_completion.csv')
evidence={}
def trace(frame,event,arg):
    if frame.f_code.co_name=='SPPR_new' and event=='line' and frame.f_lineno==2537:
        f=frame.f_locals;s=f['SPPR'];s.to_csv(DIAG/'exception_SPPR_basis.csv');f['A'].to_csv(DIAG/'exception_A.csv')
        evidence.update(columns=list(map(int,s.columns)),new_index=list(map(int,f['new_index'])),det_seq=list(map(int,f['DET_seq'])),nullity=len(f['ns']),shape=list(s.shape),rref_pivots=list(f['_']),identity_rows=[int(i) for i in f['A'].index if np.count_nonzero(f['A'].loc[i].values)==1 and f['A'].loc[i,i]==1])
    return trace
sys.settrace(trace)
try:c.diagnose_sppr(TE_option='GE',short=False,flat=False)
except Exception as e:evidence['exception']=repr(e)
finally:sys.settrace(None)
(DIAG/'EXCEPTION_PROBE.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8');print(json.dumps(evidence,indent=2))
