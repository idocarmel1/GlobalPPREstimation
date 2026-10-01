import json,sys,hashlib,shutil,subprocess,importlib.util,datetime,traceback,ast
from pathlib import Path
import numpy as np,pandas as pd
W=Path(__file__).parent;ROOT=W.parents[4];R=ROOT/'regions/LME_028';MID='28_646_Guinea_(1998)';M=R/'models'/MID;O=R/'validation_reports'/MID/'direct_diagnostics';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'));sys.path.insert(0,str(ROOT/'tools'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
from workbooks import read_book,records
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encode(x):
 if isinstance(x,pd.DataFrame):return {'type':'DataFrame','index':encode(list(x.index)),'columns':encode(list(x.columns)),'values':encode(x.to_numpy().tolist()),'dtypes':[str(t) for t in x.dtypes]}
 if isinstance(x,pd.Series):return {'type':'Series','index':encode(list(x.index)),'values':encode(x.tolist()),'name':encode(x.name)}
 if isinstance(x,np.ndarray):return {'type':'ndarray','values':encode(x.tolist())}
 if isinstance(x,dict):return {'type':'dict','items':[[encode(k),encode(v)] for k,v in x.items()]}
 if isinstance(x,tuple):return {'type':'tuple','values':[encode(v) for v in x]}
 if isinstance(x,list):return [encode(v) for v in x]
 if isinstance(x,np.generic):x=x.item()
 if isinstance(x,float) and not np.isfinite(x):return {'type':'float','value':str(x)}
 if x is None or isinstance(x,(str,int,float,bool)):return x
 raise TypeError(type(x))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
named=O/(MID+'.json');shutil.copy2(M/'model.json',named)
oldbytes=subprocess.check_output(['git','show','01bed58f^:tools/scientific_code/PPREstimation/ModelData.py'],cwd=ROOT);oldpath=W/'ModelData_retained.py';oldpath.write_bytes(oldbytes)
spec=importlib.util.spec_from_file_location('ModelData_retained',oldpath);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
a=mod.ModelData(str(named));b=ModelData(str(named));parity={}
for k in ['groups_data','DC','det_fate']:
 pd.testing.assert_frame_equal(getattr(a,k),getattr(b,k),check_exact=True);parity[k]=True
for k in ['seq2name','name2seq','model_name','model_number','model_year']:parity[k]=getattr(a,k)==getattr(b,k)
calc=PPRCalculator.from_modeldata(b,underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=True,normalize_DC=True,DC_tol=0.001)
book=read_book(R/'LME_028.xlsx');existing=pd.DataFrame(records(book,'Selected model groups','Groups')).set_index('seq')
live=calc.get_groups_df()
inventory=[]
for i,row in existing.iterrows():
 for k in row.index:
  if k not in live.columns:continue
  x,y=row[k],live.loc[i,k]
  same=(pd.isna(x) and pd.isna(y)) or x==y or (isinstance(x,(int,float)) and isinstance(y,(int,float)) and np.isclose(x,y,rtol=1e-14,atol=1e-14))
  if not same:inventory.append({'group_id':int(i),'field':k,'accepted':encode(x),'loaded':encode(y)})
write(O/'loaded_state.json',{'modeldata_groups':encode(b.groups_data),'DC':encode(b.DC),'det_fate':encode(b.det_fate),'calculator_groups':encode(live),'calculator_DC':encode(calc.get_DC()),'seq2name':encode(b.seq2name)})
oldcalc=PPRCalculator.from_modeldata(a,underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=True,normalize_DC=True,DC_tol=0.001)
pd.testing.assert_frame_equal(oldcalc.get_groups_df(),live,check_exact=True)
pd.testing.assert_frame_equal(oldcalc.get_DC(),calc.get_DC(),check_exact=True)
parity['accepted_historical_calculator_groups_exact']=True
parity['accepted_historical_normalized_DC_exact']=True
delta=calc.get_DC()-b.DC.reindex(index=calc.get_DC().index,columns=calc.get_DC().columns,fill_value=0)
write(O/'inherited_normalization.json',{'scientific_normalization_newly_introduced':False,'convention':'Original retained exporter constructor normalize_DC=True; raw canonical and modeldata DC unchanged. Same constructor with old/current loaders produces exactly identical normalized calculator diet and calculated accepted group state.','changed_cells':int((delta.abs()>0).sum().sum()),'maximum_absolute_change':float(delta.abs().max().max()),'raw_DC':encode(b.DC),'historical_normalized_DC':encode(oldcalc.get_DC()),'current_normalized_DC':encode(calc.get_DC())})
prov={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_id':MID,'canonical_sha256':sha(M/'model.json'),'computational_sha256':sha(named),'old_ModelData_sha256':hashlib.sha256(oldbytes).hexdigest(),'current_ModelData_sha256':sha(ROOT/'tools/scientific_code/PPREstimation/ModelData.py'),'loader_parity':parity,'accepted_loaded_inventory_mismatches':inventory,'constructor':{'underdetermined':True,'zero_catch':True,'zero_biomass_accum':False,'default_gs':True,'normalize_DC':True,'DC_tol':0.001},'diagnose_kwargs':{'short':False,'flat':False,'return_sppr':True,'det_open_mode':'none','det_theta':1.0,'det_external_sppr':0.0,'det_collapse_mode':'never'},'python':sys.version,'engines':{}}
for n in ['ModelData.py','PPRCalculator.py','create_PPRS_excel.py']:
 p=ROOT/'tools/scientific_code/PPREstimation'/n;dest=O/'engine'/n;dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest);prov['engines'][n]=sha(p)
write(O/'inventory_comparison.json',{'mismatches':inventory,'compared_fields':[k for k in existing.columns if k in live.columns],'metadata_fields_not_in_calculator':[k for k in existing.columns if k not in live.columns]})
assert not inventory,inventory
checks={}
for option in ['GE','TE','With Egestion']:
 slug=option.replace(' ','_');print('RUN',option,flush=True)
 try:
  ret=calc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,det_open_mode='none',det_theta=1.0,det_external_sppr=0.0,det_collapse_mode='never')
  write(O/(slug+'_full_return.json'),encode(ret));report,s,A,L=ret
  s.to_csv(O/(slug+'_source_matrix.csv'),encoding='utf-8',index_label='group_id',float_format='%.17g')
  neg=[{'method':option,'source_id':int(j),'source_name':b.seq2name[int(j)],'group_id':int(i),'group_name':b.seq2name[int(i)],'value':float(s.loc[i,j])} for i in s.index for j in s.columns if s.loc[i,j]<0]
  coefficients=[]
  method={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}[option]
  for scope in ['all','inner','PP']:
   columns=[j for j in s.columns if scope=='all' or (live.loc[j,'trophic_info']!='Import' and (scope!='PP' or live.loc[j,'trophic_info']!='DET'))]
   sums=s[columns].sum(axis=1,min_count=1)
   saved={r['group']:r['sppr'] for r in records(book,'Selected model groups','Group SPPR') if r['scope']==scope and r['method']==method}
   for i in sums.index:
    name=b.seq2name[int(i)];x=saved.get(name);y=float(sums.loc[i]);ok=x is not None and np.isclose(x,y,rtol=1e-10,atol=1e-9)
    coefficients.append({'scope':scope,'group_id':int(i),'group_name':name,'stored':x,'recovered':y,'matches':bool(ok)})
  checks[option]={'shape':list(s.shape),'row_ids':[int(x) for x in s.index],'column_ids':[int(x) for x in s.columns],'column_names':[b.seq2name[int(x)] for x in s.columns],'negative_entries':neg,'nonfinite_entries':int((~np.isfinite(s.to_numpy())).sum()),'unfished_group_ids':[int(x) for x in s.index if live.loc[x,'catch']==0],'coefficients':coefficients,'all_saved_coefficients_reproduced':all(x['matches'] for x in coefficients),'status':report['status'],'divergence':encode(report['divergence'])}
  print(option,report['status'],s.shape,'negative',len(neg),'reproduces',checks[option]['all_saved_coefficients_reproduced'],flush=True)
 except Exception as e:checks[option]={'outcome':'exception','exception':repr(e),'traceback':traceback.format_exc()};print(checks[option],flush=True)
 write(O/'matrix_inspection.json',checks)
write(O/'run_provenance.json',prov)

