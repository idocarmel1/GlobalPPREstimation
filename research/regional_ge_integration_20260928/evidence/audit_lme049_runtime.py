from pathlib import Path
import sys,json,shutil,hashlib,math,warnings
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
import pandas as pd,numpy as np
from ModelData import ModelData
from PPRCalculator import PPRCalculator
from create_PPRS_excel import build_groups_table,_source_sums
from runtime_codec import encode,decode

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
for rid,mid,settings in [('LME_049','49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)',dict(underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=True,weight_flow=1.,weight_guess=1.,normalize_DC=True,DC_tol=.001))]:
 M=ROOT/'regions'/rid/'models'/mid;D=ROOT/'regions'/rid/'models'/'regional_ge_integration_20260928';D.mkdir(exist_ok=True)
 source=M/'model.json';ip=D/'input';ip.mkdir(exist_ok=True)
 if rid!='LME_037': p=ip/f'{mid}.json';shutil.copy2(source,p)
 else:
  orig=M/'diagnostics/zero_import_default/37_3702026_Visayan_Sea_Bacalso_baseline_(1997).json';p=ip/orig.name;shutil.copy2(orig,p)
 md=ModelData(str(p));c=PPRCalculator.from_modeldata(md,**settings)
 save(D/'computational_state.json',encode(vars(c)));restored=PPRCalculator.__new__(PPRCalculator);restored.__dict__.update(decode(json.loads((D/'computational_state.json').read_text(encoding='utf-8'))));assert encode(vars(c))==encode(vars(restored))
 groups=build_groups_table(c);groups.to_csv(D/'loaded_groups.csv');md.groups_data.to_csv(D/'source_loaded_groups.csv');md.DC.to_csv(D/'source_loaded_diet.csv');c._DC.to_csv(D/'runtime_diet.csv')
 ledger=[]
 for seq in md.groups_data.index:
  for field in md.groups_data.columns:
   if field in c._groups_df.columns:
    a=md.groups_data.loc[seq,field];b=c._groups_df.loc[seq,field]
    if encode(a)!=encode(b):ledger.append({'seq':int(seq),'group':c.seq2name[seq],'field':field,'modeldata':encode(a),'runtime':encode(b)})
 for seq in md.DC.index:
  for prey in md.DC.columns:
   a=md.DC.loc[seq,prey];b=c._DC.loc[seq,prey]
   if a!=b:ledger.append({'seq':int(seq),'prey':int(prey),'field':'diet','modeldata':encode(a),'runtime':encode(b)})
 save(D/'loader_transformations.json',ledger)
 health=[];rr={};matches=[]
 for option,key in [('GE','new_GE'),('TE','new_TE_EEfix'),('With Egestion','new_WithEgestion')]:
  ret=c.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
  report,sppr,A,L=ret;save(D/f'direct_{key}.json',encode(ret));save(D/f'diagnostic_{key}.json',report)
  again=restored.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True);assert encode(ret)==encode(again)
  flat=c._flatten_diagnostics(report);health.append(flat);rr[key]=sppr
  if rid!='LME_037': old=pd.read_excel(M/'sppr_source.xlsx',sheet_name='model_health');old=old[old.TE_option==option].iloc[0].to_dict()
  else:old=c._flatten_diagnostics(json.loads((M/'diagnostics/zero_import_default'/f'{option.replace(" ","_")}_raw.json').read_text()))
  for f in ['status','divergence_rho_living','balance_rel_gap','model_input_p_max_rel_residual']:
   assert math.isclose(flat[f],old[f],rel_tol=1e-10,abs_tol=1e-12) if isinstance(flat[f],(int,float)) else flat[f]==old[f],(rid,f,flat[f],old[f])
  assert np.isfinite(sppr.to_numpy(dtype=float)).all()
  matches.append({'option':option,'status':flat['status'],'retained_health_matches':True,'exact_runtime_reload_matches':True,'all_source_coefficients_finite_nonnegative':bool((sppr.to_numpy(dtype=float)>=-1e-10).all())})
  print(rid,option,flat['status'],flush=True)
 for scope,sumkey in [('PP','SUM_PP'),('inner','SUM_INNER'),('all','SUM_ALL')]:
  table=pd.DataFrame(index=groups.index);table['group_name']=[c.seq2name[int(s)] for s in table.index]
  for key,sppr in rr.items():table[key]=_source_sums(c,sppr,True)[sumkey].reindex(table.index)
  table.to_csv(D/f'group_sppr_{scope}.csv')
  if rid!='LME_037':
   old=pd.read_excel(M/'sppr_source.xlsx',sheet_name='sppr_'+scope,index_col=0)
   for key in rr:np.testing.assert_allclose(table[key],old.loc[table.index,key],rtol=1e-10,atol=1e-9)
 save(D/'health.json',health)
 save(D/'runtime_verification.json',{'unit_id':rid,'canonical_sha256':sha(source),'computational_input_sha256':sha(p),'computational_state_sha256':sha(D/'computational_state.json'),'constructor':settings,'methods':matches,'engine_sha256':{n:sha(ROOT/'tools/scientific_code/PPREstimation'/n) for n in ['PPRCalculator.py','ModelData.py']},'source_unchanged':True,'interpretation':'Conditional reconstruction using previously retained settings. Unknown BA, GS, imports/routing and diet rounding assumptions remain assumptions, not recovered source measurements.'})
 print('VERIFIED',rid,flush=True)
