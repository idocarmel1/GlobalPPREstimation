from pathlib import Path
import sys,json,time,hashlib,copy,shutil,math
import numpy as np,pandas as pd
R=Path.cwd();sys.path[:0]=[str(R/'tools'),str(R/'tools/scientific_code/PPREstimation')]
from workbooks import *
from regional import set_setting,result_hash
from ModelData import ModelData
from PPRCalculator import PPRCalculator
from create_PPRS_excel import _source_sums
MID='52_1_Sea_of_Okhotsk_NE_(1980)';REG=R/'regions/LME_052';E=REG/'validation_reports'/MID;O=E/'diet_reextraction_20261002';M=REG/'models'/MID/'model.json';W=REG/'LME_052.xlsx'
def save(name,value): (O/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def serial(x):
 if isinstance(x,pd.Series):x=x.to_frame()
 if isinstance(x,pd.DataFrame):return {'index':list(x.index),'columns':list(x.columns),'data':[[serial(v) for v in row] for row in x.values.tolist()]}
 if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [serial(v) for v in x]
 if isinstance(x,np.generic):return serial(x.item())
 if isinstance(x,float) and not math.isfinite(x):return None
 return x
before=sha(W);b=read_book(W);original=copy.deepcopy(b);settings=json.loads((E/'direct_diagnostics/execution_evidence.json').read_text())['constructor_settings']
raw=ModelData(str(M));old=ModelData(str(O/'baseline_normalized_model.json'))
norm=ModelData.validate_DC(raw.DC.copy(),raw.groups_data,normalize=True,tol=settings['DC_tol'])
oldnorm=ModelData.validate_DC(old.DC.copy(),old.groups_data,normalize=True,tol=settings['DC_tol'])
assert raw.groups_data.equals(old.groups_data) and raw.det_fate.equals(old.det_fate)
assert np.allclose(norm,oldnorm,rtol=0,atol=2e-16)
runtime={'source_sha256':sha(M),'prior_source_sha256':sha(O/'baseline_normalized_model.json'),'constructor_settings':settings,'runtime_normalization_allowed':True,'raw_row_sums':serial(raw.DC.sum(axis=1)),'normalized_row_sums':serial(norm.sum(axis=1)),'normalization_factors':serial(raw.DC.sum(axis=1).replace(0,np.nan).rdiv(1)),'raw_DC':serial(raw.DC),'normalized_DC':serial(norm),'raw_runtime_changed_cells':int(np.sum(raw.DC.values!=norm.values)),'prior_runtime_max_abs_DC_difference':float(np.max(abs(norm.values-oldnorm.values))),'source_groups_and_detritus_routing_exact_equal':True}
save('runtime_normalization.json',runtime)
c=PPRCalculator.from_modeldata(raw,**settings)
oldstate=json.loads((E/'direct_diagnostics/loaded_state.json').read_text());state={k:serial(getattr(c,k)) for k in oldstate};save('current_loaded_state.json',state)
checks={}
for k,v in oldstate.items():
 n=state[k];assert v['index']==n['index'] and v['columns']==n['columns']
 diffs=[]
 for i,(aa,bb) in enumerate(zip(v['data'],n['data'])):
  for j,(a,z) in enumerate(zip(aa,bb)):
   if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(z,(int,float)):
    if not math.isclose(a,z,rel_tol=1e-12,abs_tol=1e-12):diffs.append([i,j,a,z])
   elif a!=z:diffs.append([i,j,a,z])
 checks[k]={'exact_equal':v==n,'within_tolerance':not diffs,'differences':diffs}
assert all(v['within_tolerance'] for v in checks.values())
reports={};solutions={};matrix_comparisons={};coeff_comparisons=[];times={};methods={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}
oldsol=json.loads((E/'direct_diagnostics/direct_solutions.json').read_text())
for option,key in methods.items():
 start=time.time();report,s,A,L=c.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,det_open_mode='none',det_theta=1.0,det_external_sppr=0.0,det_collapse_mode='never');times[option]=time.time()-start
 reports[option]=serial(report);solutions[option]={'SPPR':serial(s),'A':serial(A),'L':serial(L)}
 prior=oldsol[option]['SPPR'];assert prior['index']==list(s.index) and prior['columns']==list(s.columns)
 a=np.array(prior['data'],dtype=float);assert np.allclose(a,s.values,rtol=1e-10,atol=1e-8,equal_nan=True)
 matrix_comparisons[option]={'max_abs_difference':float(np.nanmax(abs(a-s.values))),'same_negative_pairs':bool(np.array_equal(a<0,s.values<0)),'grade':report['status']}
 sums=_source_sums(c,s,True)
 for row in b['Selected model groups']['Group SPPR'][1]:
  if row[3]!=key:continue
  seq=c.name2seq[row[1]];col={'all':'SUM_ALL','inner':'SUM_INNER','PP':'SUM_PP'}[row[2]];fresh=float(sums[col].loc[seq]);saved=row[4]
  assert math.isclose(saved,fresh,rel_tol=1e-10,abs_tol=1e-6),(row,fresh)
  coeff_comparisons.append({'group':row[1],'scope':row[2],'method':key,'saved':saved,'fresh':fresh,'difference':fresh-saved})
assert {k:v['status'] for k,v in reports.items()}=={'GE':'WARN','TE':'FAIL','With Egestion':'WARN'}
save('direct_reports.json',reports);save('direct_solutions.json',solutions)
save('scientific_revalidation.json',{'date':'2026-10-02','canonical_sha256':sha(M),'prior_source_sha256':runtime['prior_source_sha256'],'constructor_settings':settings,'diagnostic_options':{'short':False,'flat':False,'return_sppr':True,'det_open_mode':'none','det_theta':1.0,'det_external_sppr':0.0,'det_collapse_mode':'never'},'engine_sha256':{n:sha(R/'tools/scientific_code/PPREstimation'/n) for n in ['ModelData.py','PPRCalculator.py','utils.py']},'loaded_state_comparison':checks,'matrix_comparison':matrix_comparisons,'saved_direct_scoped_coefficient_comparisons':coeff_comparisons,'timings_seconds':times,'scope':'Only inherited direct GE, TE, With Egestion rerun; runtime state revalidated; saved numerical coefficients and annual results retained; historical legacy/Monte Carlo outputs not rerun and remain provisional','runtime_tolerance':{'rtol':1e-12,'atol':1e-12},'matrix_tolerance':{'rtol':1e-10,'atol':1e-8}})
shutil.copy2(W,O/'baseline_regional_before_runtime_revalidation.xlsx')
set_setting(b,'results_model_sha256',sha(M))
set_setting(b,'calculation_status','provisional: printed diet restored; runtime-normalized state and direct GE/TE/With Egestion revalidated; existing numerical results retained; TE FAIL and historical MC restrictions apply')
set_setting(b,'diet_source_state','printed proportions; researcher error classification pending; runtime normalization always allowed')
set_setting(b,'runtime_revalidation_evidence',f'validation_reports/{MID}/diet_reextraction_20261002/scientific_revalidation.json')
b['Diagnostics']['Diet runtime revalidation']=table_dict([{'date':'2026-10-02','model_sha256':sha(M),'GE':'WARN','TE':'FAIL','With Egestion':'WARN','evidence':f'validation_reports/{MID}/diet_reextraction_20261002/scientific_revalidation.json','saved_results':'retained after runtime state/direct coefficient parity; no historical MC rerun'}])
assert input_hash(b)==input_hash(original) and result_hash(b)==result_hash(original)
assert all(b[s]==original[s] for s in b if s not in ['Overview','Diagnostics'])
assert sha(W)==before,'Concurrent regional edit'
write_book(W,b);check=read_book(W);validate_region(check,W)
assert input_hash(check)==input_hash(original) and result_hash(check)==result_hash(original)
save('regional_revalidation.json',{'before_sha256':before,'after_sha256':sha(W),'input_hash_unchanged':True,'result_hash_unchanged':True,'production_eligible':overview(check)['production_eligible'],'all_numeric_tables_preserved':True,'source_sha256':sha(M),'freshness_validation':'passed after scientific revalidation, not a hash-only relabel'})
print(json.dumps({'grades':{k:v['status'] for k,v in reports.items()},'matrix_comparisons':matrix_comparisons,'unchanged_numerical_results':True,'runtime_state_checks':len(checks),'coefficient_checks':len(coeff_comparisons),'regional_sha256':sha(W)}))
