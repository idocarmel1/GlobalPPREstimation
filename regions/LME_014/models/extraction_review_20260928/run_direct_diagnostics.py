from pathlib import Path
import sys,json,time,traceback,warnings,hashlib,contextlib,shutil
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[4];REVIEW=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
def convert(x):
 if isinstance(x,dict):return {str(k):convert(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [convert(v) for v in x]
 if isinstance(x,np.ndarray):return convert(x.tolist())
 if isinstance(x,np.generic):return convert(x.item())
 if isinstance(x,float) and not np.isfinite(x):return str(x)
 if isinstance(x,(str,int,float,bool)) or x is None:return x
 return str(x)
def dump(p,x):p.write_text(json.dumps(convert(x),indent=2,ensure_ascii=False),encoding='utf-8')
ids=json.loads((REVIEW/'model_ids.json').read_text())
if len(sys.argv)>1:ids=[sys.argv[1]]
for mid in ids:
 folder=ROOT/'regions/LME_014/models'/mid
 status={'model_id':mid,'model_sha256':hashlib.sha256((folder/'model.json').read_bytes()).hexdigest(),'diagnostics':{},'source_admission':'See source_report.md; no adoption authorized'}
 if mid.endswith('_native') and (folder/'diagnostics_raw.json').exists():
  prior=folder/'default_loader_diagnostics';prior.mkdir(exist_ok=True)
  for p in list(folder.glob('diagnostic*'))+list(folder.glob('loader_*.csv')):
   if p.is_file() and not (prior/p.name).exists():shutil.copy2(p,prior/p.name)
 with (folder/'diagnostic_execution.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log),warnings.catch_warnings(record=True) as w:
  warnings.simplefilter('always')
  try:
   alias_dir=folder/'loader_input';alias_dir.mkdir(exist_ok=True)
   year=1970 if mid.startswith('Ocampo') else 2020
   alias=alias_dir/f'14_140001_{mid}_({year}).json'
   alias_data=json.loads((folder/'model.json').read_text(encoding='utf-8'))
   if mid.endswith('_native'):
    audit=json.loads((REVIEW/'evidence/native_independent_balance_audit.json').read_text(encoding='utf-8'))
    changes=[]
    for g,r in zip(alias_data['group'],audit['groups']):
     if g['biomass']=='-9999':
      g['biomass']=str(r['biomass_solved']);g['biomass_habitat_area']=str(r['biomass_solved']/float(g['habitat_area']))
      changes.append({'group':g['group_seq'],'field':'biomass','value':g['biomass'],'source':'Derived coupled Ecopath production balance; native B remains unknown in canonical JSON'})
     if g['ee']=='-9999':
      g['ee']=str(r['ee_recomputed']);changes.append({'group':g['group_seq'],'field':'ee','value':g['ee'],'source':'Derived native production balance; no source replacement'})
    status['derived_native_completion']={'changes':changes,'matrix_residual_max':audit['matrix_residual_max'],'canonical_source_unchanged':True,'scope':'Only unknown living/producer B and EE; no changes to diet, catches, routing, GS, native migration or BA.'}
   alias.write_text(json.dumps(alias_data,ensure_ascii=True,indent=2),encoding='ascii')
   status['loader_alias']={'path':str(alias.relative_to(ROOT)),'reason':'Legacy parser requires numeric id and parenthesized year; 140001 is local diagnostic placeholder, not EcoBase accession. ASCII escapes; any native-derived completions listed separately.'}
   md=ModelData(str(alias))
   md.groups_data.to_csv(folder/'loader_input_groups.csv');md.DC.to_csv(folder/'loader_diet.csv');md.det_fate.to_csv(folder/'loader_detritus_fate.csv')
   try:
    PPRCalculator.from_modeldata(md,zero_catch=False,zero_biomass_accum=False,default_gs=False,normalize_DC=False)
    status['strict_loader']='constructed without missing catch/BA/GS defaults'
   except Exception as e:status['strict_loader']={'exception_type':type(e).__name__,'message':str(e)}
   # Structural nonconsumer rows have no consumption; missing import entries otherwise
   # propagate NaN through linear algebra. Keep this boundary completion out of source JSON.
   import_seq=max(md.seq2name)
   noncons=md.groups_data.index[md.groups_data['trophic_info'].isin(['PP','DET'])]
   structural_missing=[int(s) for s in noncons if pd.isna(md.DC.loc[s,import_seq])]
   if structural_missing:
    md.DC.loc[structural_missing,import_seq]=0.0
    status['structural_loader_completion']={'nonconsumer_diet_import_zero':structural_missing,'reason':'No consumption by PP/DET groups; source unknown cells retained in canonical JSON. No consumer diet change.'}
   # Preserve diet values; source rounding tolerance is a separately declared loader allowance.
   tol=0.0021 if mid.startswith('Ocampo') else 0.001
   status['loader_configuration']={'underdetermined':False,'zero_catch':True,'zero_biomass_accum':True,'default_gs':True,'normalize_DC':False,'DC_tol':tol,'detritus_pooling':False}
   pc=PPRCalculator.from_modeldata(md,normalize_DC=False,DC_tol=tol)
   pc._groups_df.to_csv(folder/'loader_completed_groups.csv')
   for option in ['GE','TE','With Egestion']:
    start=time.monotonic()
    try:
     result=pc.diagnose_sppr(TE_option=option,short=False,flat=False,det_collapse_mode='never',det_open_mode='none')
     dump(folder/('diagnostics_'+option.replace(' ','_')+'.json'),result)
     status['diagnostics'][option]={'execution':'returned','elapsed_seconds':time.monotonic()-start,'return':result}
    except Exception as e:
     status['diagnostics'][option]={'execution':'exception','exception_type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
  except Exception as e:
   status['loader_exception']={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
   for option in ['GE','TE','With Egestion']:status['diagnostics'][option]={'execution':'not_run','reason':'Loader failed before diagnose_sppr: '+str(e)}
  status['warnings']=[str(x.message) for x in w]
 dump(folder/'diagnostic_run_record.json',status)
 text=['# Direct SPPR diagnostic returns\n',f'Model: `{mid}`. Source assumptions, transformations, and limits are in source_report.md.\n']
 raw={}
 for option,r in status['diagnostics'].items():
  text.append('## '+option+'\n')
  if r['execution']=='returned':
   raw[option]=r['return'];text.append('```json\n'+json.dumps(convert(r['return']),indent=2,ensure_ascii=False)+'\n```\n')
  else:text.append('No direct return. '+r.get('reason',r.get('message',''))+'\n')
 dump(folder/'diagnostics_raw.json',raw)
 (folder/'diagnostic_report.md').write_text('\n'.join(text),encoding='utf-8')
 print(mid,{k:v['execution'] for k,v in status['diagnostics'].items()},flush=True)
