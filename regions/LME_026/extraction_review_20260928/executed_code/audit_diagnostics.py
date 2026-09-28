from pathlib import Path
from decimal import Decimal
import json,sys,traceback,warnings,copy,pickle,csv
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
MD=ROOT/'regions/LME_026/models/Piroddi_2022_Mediterranean_1995';DOUT=MD/'diagnostics';DOUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
def encode(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if hasattr(x,'to_dict'):return x.to_dict()
 return str(x)
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=encode),encoding='utf8')
src=json.loads((MD/'model.json').read_text(encoding='utf8'));inp=json.loads((OUT/'extraction_input.json').read_text(encoding='utf8'))
B=np.array([float(g['biomass']) for g in inp['groups']]);PB=np.array([float(g['pb']) if g['pb'] is not None else np.nan for g in inp['groups']]);QB=np.array([float(g['qb']) if g['qb'] is not None else 0 for g in inp['groups']]);EE=np.array([float(g['ee']) for g in inp['groups']]);DC=np.array([[float(inp['diet'][str(j)][str(i)]) for j in range(1,66)] for i in range(1,72)])
pred=DC@(B[:65]*QB[:65]);rows=[];sums={}
for j,d in inp['diet'].items():sums[j]=str(sum(map(Decimal,d.values()),Decimal(0)))
for i,g in enumerate(inp['groups']):
 n=i+1;sg=src['group'][i];L=None if sg['source_landings']=='-9999' else float(sg['source_landings']);D=float(sg['source_discards']);Y=(L or 0)+D;P=B[i]*PB[i]
 rows.append({'seq':n,'group_name':g['name'],'biomass':B[i],'PB':PB[i] if np.isfinite(PB[i]) else None,'production':P if np.isfinite(P) else None,'predation':pred[i],'landings':L,'discards':D,'known_removals':Y,'printed_EE':EE[i],'EE_if_unreported_BA_NM_and_landings_are_zero':(pred[i]+Y)/P if P>0 else None,'residual_BA_plus_NM_if_unreported_landings_zero':P*EE[i]-pred[i]-Y if P>0 else None,'conditional_EE_gt_1':bool(P>0 and (pred[i]+Y)>P),'diet_sum':sums.get(str(n)),'biomass_cell':f"'Basic input parameters'!D{n+4}",'PB_cell':f"'Basic input parameters'!E{n+4}",'EE_cell':f"'Basic input parameters'!G{n+4}"})
save(OUT/'independent_source_balance.json',{'assumptions':'Conditional arithmetic only: missing BA, net migration, and unlisted landings set to zero solely to expose residuals. No results written into source or runtime parameters. Negative residual is required BA+net-export, not a recovered source input. Multistanza links may require separate terms.','groups':rows,'diet_sums':sums})
with (OUT/'source_balance_groups.csv').open('w',encoding='utf8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
staged=copy.deepcopy(src);transforms=[]
for g in staged['group']:
 if g['export']=='-9999':
  g['export']=g['source_discards'];transforms.append({'seq':int(g['group_seq']),'field':'export','source':'unknown total; landings not tabulated','staged_value':g['export'],'assumption':'unlisted landings zero; preserve all explicitly reported discards'})
path=DOUT/'26_2602022_Mediterranean_Piroddi_(1995).json';path.write_text(json.dumps(staged,ensure_ascii=True,indent=2),encoding='ascii')
strict_path=DOUT/'26_2602022_Mediterranean_Piroddi_Source_(1995).json';strict_path.write_text(json.dumps(src,ensure_ascii=True,indent=2),encoding='ascii')
save(DOUT/'staging_transformations.json',{'source_to_staging':transforms,'requested_runtime_defaults':{'zero_catch':False,'zero_biomass_accum':True,'default_gs':True,'underdetermined':False,'normalize_DC':False},'unknowns_retained_in_source':['GS','BA','net migration','detritus routing','detritus imports','habitat area','unlisted landings'],'source_biomass_completion':'none; all 71 groups have source B','biological_repairs':'none','routing_or_pooling':'none'})
audit={};results=[]
for label,settings in [('strict_source',{'zero_catch':False,'zero_biomass_accum':False,'default_gs':False}),('documented_loader_defaults',{'zero_catch':False,'zero_biomass_accum':True,'default_gs':True})]:
 try:
  with warnings.catch_warnings(record=True) as caught:
   warnings.simplefilter('always');data=ModelData(str((strict_path if label=='strict_source' else path).resolve()));data.lme=26
   data.groups_data.to_csv(DOUT/'loader_groups_before_defaults.csv');data.DC.to_csv(DOUT/'loader_diet.csv');data.det_fate.to_csv(DOUT/'loader_detritus_fate.csv')
   calc=PPRCalculator.from_modeldata(data,underdetermined=False,normalize_DC=False,**settings)
  audit[label]={'status':'LOADED','warnings':[str(w.message) for w in caught]}
 except Exception as exc:
  audit[label]={'status':'EXCEPTION','type':type(exc).__name__,'exception':str(exc),'traceback':traceback.format_exc()};continue
 if label=='documented_loader_defaults':
  for method in ['GE','TE','With Egestion']:
   try:
    raw=calc.diagnose_sppr(TE_option=method,short=False,flat=False);name=method.replace(' ','_')
    save(DOUT/f'{name}_direct_return.json',raw);(DOUT/f'{name}_direct_return.pkl').write_bytes(pickle.dumps(raw))
    results.append({'TE_option':method,'status':'RETURNED','direct_return':raw})
   except Exception as exc:results.append({'TE_option':method,'status':'EXCEPTION','exception':str(exc),'traceback':traceback.format_exc()})
if not results:
 for method in ['GE','TE','With Egestion']:results.append({'TE_option':method,'call':f'PPRCalculator.diagnose_sppr(TE_option={method!r}, short=False, flat=False)','status':'NOT_RUN','direct_return':None,'reason':audit['documented_loader_defaults']['exception']})
save(DOUT/'loader_audit.json',audit);save(DOUT/'diagnostics_results.json',results)
print(json.dumps({'diet_sum_range':[min(map(float,sums.values())),max(map(float,sums.values()))],'conditional_EE_gt1':[(r['seq'],r['group_name'],r['EE_if_unreported_BA_NM_and_landings_are_zero']) for r in rows if r['conditional_EE_gt_1']],'loader':audit},indent=2))
