from pathlib import Path
import sys,json,shutil,hashlib,warnings
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
REG=ROOT/'regions/LME_003';MODEL=REG/'models/CAL-2016_California_Current_2000-2014';OUT=MODEL/'selected_pipeline';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'tools'));from workbooks import *
from regional import set_setting,set_result_hash
from run_region import prepare_selection
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from PPRCalculator import PPRCalculator
from ModelData import ModelData
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,default=lambda x:x.item() if isinstance(x,np.generic) else x),encoding='utf-8')
runtime=OUT/'3_2016_Author_solved_California_Current_(2000-2014).json'
shutil.copy2(MODEL/'diagnostics'/runtime.name,runtime)
code=OUT/'code';code.mkdir(exist_ok=True)
for name in ['PPRCalculator.py','ModelData.py','utils.py']:shutil.copy2(ROOT/'tools/scientific_code/PPREstimation'/name,code/name)
for name in ['workbooks.py','regional.py','run_region.py']:shutil.copy2(ROOT/'tools'/name,code/name)
shutil.copy2(__file__,code/Path(__file__).name)
book=read_book(REG/'LME_003.xlsx');archive=REG/'models/previous_results';archive.mkdir(exist_ok=True)
before=archive/f'LME_003_before_CAL2016_selection_{sha(REG/"LME_003.xlsx")[:12]}.xlsx'
shutil.copy2(REG/'LME_003.xlsx',before)
set_setting(book,'selected_model_id',MODEL.name);set_setting(book,'model_path',runtime.relative_to(REG).as_posix())
set_setting(book,'selected_paper_ids','CAL-2016__LME_003')
set_setting(book,'selection_rationale','User explicitly selected the extracted CAL-2016 California Current model (2000–2014). Selected runtime preserves the audited author-equation solution for source-unknown B/EE; canonical source model.json remains unchanged. Three direct SPPR configurations retain WARN and documented loader GS=0.2 and detritus accounting extensions.')
set_setting(book,'source_note','Source model has 93 groups, 302000 km² domain; regional geographic coverage fraction not established. Runtime resolves 26 source-unknown B and 67 EE from author equations. GS=0.2 and egestion-to-detritus are documented loader assumptions. Total model catch includes discards without a split. Annual regional results use this fixed 2000–2014 model and explicit catch mapping; unsupported taxa remain blank.')
prepare_selection(book,REG/'LME_003.xlsx');write_book(REG/'LME_003.xlsx',book)
md=ModelData(str(runtime));md.lme=3
m=PPRCalculator.from_modeldata(md,underdetermined=False,zero_catch=False,zero_biomass_accum=False,default_gs=True,normalize_DC=False)
gr=m.get_groups_df();gr.to_csv(OUT/'selected_groups.csv',encoding='utf-8')
coeff=[];health=[];verification=[]
def close(a,b):
 if isinstance(a,dict):
  a={str(k):v for k,v in a.items()};b={str(k):v for k,v in b.items()}
  return a.keys()==b.keys() and all(close(a[k],b[k]) for k in a)
 if isinstance(a,list):return len(a)==len(b) and all(close(x,y) for x,y in zip(a,b))
 if isinstance(a,(int,float)) and not isinstance(a,bool):return np.isclose(a,b,rtol=1e-12,atol=1e-12,equal_nan=True)
 return a==b
for option,method,key in [('GE','new_GE','ge'),('TE','new_TE_EEfix','te'),('With Egestion','new_WithEgestion','with_egestion')]:
 report,raw,A,L=m.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
 assert close(report,load(MODEL/'diagnostics'/f'{key}_direct_return.json')),'Audited diagnostic changed'
 assert report['status']!='FAIL' and np.isfinite(raw.to_numpy()).all() and (raw.to_numpy()>=0).all()
 dump(OUT/f'{key}_direct_return.json',report);raw.to_csv(OUT/f'{key}_source_resolved_sppr.csv',encoding='utf-8')
 det=[c for c in m.get_DET_seq() if c in raw.columns];imp=[c for c in m.get_Import_seq() if c in raw.columns]
 for scope,frame in [('all',raw),('inner',raw.drop(columns=imp)),('PP',raw.drop(columns=imp+det))]:
  for seq,val in frame.sum(axis=1,min_count=1).items():coeff.append([MODEL.name,m.seq2name[int(seq)],scope,method,float(val)])
 flat=PPRCalculator._flatten_diagnostics(report);flat['TE_option']=option;health.append(flat)
 verification.append({'option':option,'method':method,'matches_audited_full_report':True,'status':report['status'],'n_negative_source_contributions':int((raw.to_numpy()<0).sum()),'n_nonfinite_source_contributions':int((~np.isfinite(raw.to_numpy())).sum())})
book=read_book(REG/'LME_003.xlsx')
groupframe=gr.reset_index();groupframe=groupframe.replace({np.nan:None})
book['Selected model groups']={'Groups':(list(groupframe.columns),groupframe.values.tolist()),'Group SPPR':(['model_id','group','scope','method','sppr'],coeff)}
hh=list(dict.fromkeys(k for r in health for k in r));book['Diagnostics']['model_health']=(hh,[[r.get(k) for k in hh] for r in health])
book['Diagnostics']['run_notes']=(['item','value'],[['scope','Only full direct GE, TE and With Egestion with return_sppr=True; all reproduce audited reports'],['source_canonical',f'models/{MODEL.name}/model.json'],['source_admission','Qualified: source GS unknown and catch split unavailable'],['runtime_assumptions','Solved author B/EE; GS0.2; all unused production and runtime egestion to sole detritus pool; loader detritusEE1'],['annual_interpretation','Fixed 2000–2014 model applied to historical catch; model ecosystem state is not recalibrated yearly']])
book['PPR']['Annual']=(ANNUAL_HEADER,[[MODEL.name,s,meth,'landings','method','ppr','ok',*[None]*70] for s in ['all','inner','PP'] for meth in ['new_GE','new_TE_EEfix','new_WithEgestion']])
set_setting(book,'results_model_id',MODEL.name);set_setting(book,'results_model_sha256',sha(runtime));set_setting(book,'calculation_input_sha256',None);set_setting(book,'calculation_status','Selected model three-configuration SPPR complete; catch mapping pending');set_setting(book,'production_eligible',False);set_result_hash(book)
write_book(REG/'LME_003.xlsx',book)
dump(OUT/'coefficient_verification.json',{'runtime_sha256':sha(runtime),'canonical_sha256':sha(MODEL/'model.json'),'previous_workbook':before.relative_to(REG).as_posix(),'configurations':verification,'coefficients':len(coeff),'engine_hashes':{p.name:sha(p) for p in code.glob('*.py')}})
print(json.dumps(verification,indent=2));print('coefficients',len(coeff))
