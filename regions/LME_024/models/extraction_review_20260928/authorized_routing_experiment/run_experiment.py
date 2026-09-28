from pathlib import Path
from copy import deepcopy
from decimal import Decimal
import json,sys,hashlib,pickle,warnings,traceback,argparse,contextlib,io
import numpy as np
import pandas as pd
from routing_adapter import RoutingExperimentCalculator,PPRCalculator
from ModelData import ModelData
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent;REVIEW=OUT.parent
MD=ROOT/'regions/LME_024/models/Hernvann_2020_Celtic_Sea_1985'
NORM=next((REVIEW/'authorized_diet_normalization').glob('*.json'))
NORM=next((REVIEW/'authorized_diet_normalization').glob('24_*.json'))
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,np.ndarray):return clean(x.tolist())
 if isinstance(x,np.generic):return clean(x.item())
 if isinstance(x,float) and not np.isfinite(x):return str(x)
 return x
def save(name,obj):
 (OUT/name).write_text(json.dumps(clean(obj),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def snapshot(c,prefix):
 c._groups_df.to_csv(OUT/(prefix+'_groups.csv'))
 pd.DataFrame({k:getattr(c,k) for k in ['p','q','catch','predation','growth','M0','egestion','respiration','net_migration','EE','GE','GS']}).to_csv(OUT/(prefix+'_vectors.csv'))
 c._DC.to_csv(OUT/(prefix+'_diet.csv'));c._det_fate.to_csv(OUT/(prefix+'_natural_fate.csv'))

def prepare():
 files=[MD/'model.json',NORM,*list((ROOT/'regions/LME_024/papers/LME024-Hernvann-2020').glob('*')),*[ROOT/'tools/scientific_code/PPREstimation'/x for x in ['PPRCalculator.py','ModelData.py','utils.py']]]
 before={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in files if p.is_file()}
 save('original_hashes_before.json',before)
 inp=read(REVIEW/'extraction_input.json');model=read(NORM)
 returns={int(k):Decimal(v['Total fishery']) for k,v in inp['discards'].items()}
 landings={int(k):Decimal(v['Total fishery']) for k,v in inp['landings'].items()}
 B={int(g['group_seq']):Decimal(g['biomass']) for g in model['group']}
 Q={int(g['group_seq']):B[int(g['group_seq'])]*Decimal(g['qb']) if g['qb']!='-9999' else Decimal(0) for g in model['group']}
 pred={i:Decimal(0) for i in B}
 for g in model['group']:
  diets=g['diet_descr']['diet'] if g['diet_descr'] else []
  if isinstance(diets,dict):diets=[diets]
  for d in diets:
   if d['proportion']!='-9999':pred[int(d['prey_seq'])]+=Q[int(g['group_seq'])]*Decimal(d['proportion'])
 derived=[]
 for g in model['group']:
  i=int(g['group_seq'])
  if i in range(9,15):
   value=Decimal(g['ge'])*Decimal(g['qb'])
   derived.append({'group_seq':i,'field':'pb','before':g['pb'],'after':str(value),'equation':'PB=printed_PQ*QB; source-rounded multistanza completion, not a fitted rate'})
   g['pb']=str(value)
  if i==18:
   value=(pred[i]+landings[i]+returns[i]+B[i]*Decimal(g['biomass_accum_rate']))/(B[i]*Decimal(g['pb']))
   derived.append({'group_seq':i,'field':'ee','before':g['ee'],'after':str(value),'equation':'EE=(normalized predation+landings+discards+B*BA_rate)/(B*PB); zero net migration convention'})
   g['ee']=str(value)
  diets=g['diet_descr']['diet'] if g['diet_descr'] else []
  if isinstance(diets,dict):diets=[diets]
  for d in diets:
   prey=int(d['prey_seq'])
   if prey in [53,54]:d['detritus_fate']='1' if i<=52 and prey==54 else '0'
  # ModelData will impose pool self-identity anyway; no inter-pool transfer asserted.
  g['diet_descr']={'diet':diets}
 path=OUT/'24_2402020_Celtic_Sea_Hernvann_Routing_Experiment_(1985).json'
 save(path.name,model);save('derived_parameters.json',derived)
 data=ModelData(str(path));data.groups_data.to_csv(OUT/'native_predefaults_groups.csv')
 data.det_fate.to_csv(OUT/'native_loader_fate.csv')
 with warnings.catch_warnings(record=True) as ws,contextlib.redirect_stdout(io.StringIO()) as txt:
  warnings.simplefilter('always')
  base=PPRCalculator.from_modeldata(data,underdetermined=False,zero_catch=True,zero_biomass_accum=True,default_gs=True,normalize_DC=False)
 save('native_initializer_log.json',{'warnings':[str(w.message) for w in ws],'stdout':txt.getvalue()})
 snapshot(base,'native_initializer')
 changes=[]
 for i in data.groups_data.index:
  for col in data.groups_data:
   a=data.groups_data.loc[i,col];b=base._groups_df.loc[i,col]
   equal=(pd.isna(a) and pd.isna(b)) or (not pd.isna(a) and not pd.isna(b) and a==b)
   if not equal:changes.append({'seq':int(i),'field':col,'before':a,'after':b})
 save('native_initializer_transformations.json',changes)
 c=RoutingExperimentCalculator.__new__(RoutingExperimentCalculator)
 c.__dict__=deepcopy(base.__dict__);c.balanced_model=None
 c.discard_return=pd.DataFrame(0.,index=c.p.index,columns=c.get_DET_seq())
 for i,d in returns.items():c.discard_return.loc[i,53]=float(d)
 natural=c._det_fate.mul(c.M0+c.egestion,axis=0).sum(axis=0)
 inflow=natural+c.discard_return.sum(axis=0)
 for det in c.get_DET_seq():
  c.p.loc[det]=c.q.loc[det]=inflow[det]
  # Restore the source interpretation: BA is a rate, not a freely solved residual.
  g=model['group'][det-1]
  c.growth.loc[det]=float(Decimal(g['biomass'])*Decimal(g['biomass_accum_rate']))
 for col,attr in {'p':'p','q':'q','biomass_accum':'growth'}.items():c._groups_df[col]=getattr(c,attr)
 c._groups_df['pb']=c.p/c._groups_df['biomass'];c._groups_df['qb']=c.q/c._groups_df['biomass']
 c.is_balanced=c.is_model_balanced()[0]
 snapshot(c,'faithful_printed_BA');c.discard_return.to_csv(OUT/'discard_returns_by_donor.csv')
 c.get_Z(False).to_csv(OUT/'faithful_all_flows_Z.csv')
 # Assertions verify scientific accounting rather than demanding a biological pass.
 np.testing.assert_allclose(c.catch,base.catch);np.testing.assert_allclose(c.M0,base.M0)
 np.testing.assert_allclose(c._DC,base._DC)
 for i in range(1,55):assert c._groups_df.loc[i,'biomass']==float(B[i])
 assert c._groups_df.loc[1,'biomass']==0 and c._groups_df.loc[2,'biomass']==0
 assert float(c.discard_return[54].sum())==0
 np.testing.assert_allclose(c.get_Z(False).loc[53],c.discard_return[53])
 np.testing.assert_allclose(c.get_Z(False).loc[54],c.M0+c.egestion)
 assert np.isclose(c.discard_return.to_numpy().sum(),float(sum(returns.values())))
 prod_rhs=c.catch+c.predation+c.growth+c.net_migration+c.M0
 consumption_rhs=c.p+c.egestion+c.respiration
 ledger=pd.DataFrame({'name':c._groups_df.group_name,'P':c.p,'Q':c.q,'predation':c.predation,'M0':c.M0,'egestion':c.egestion,'respiration':c.respiration,'fishery_L_plus_D':c.catch,'fishery_D_return':c.discard_return.sum(axis=1),'external_fishery_L':c.catch-c.discard_return.sum(axis=1),'BA':c.growth,'net_migration':c.net_migration,'P_minus_sinks':c.p-prod_rhs,'Q_minus_sinks':c.q-consumption_rhs})
 ledger.to_csv(OUT/'physical_budget_by_group.csv')
 pool=[]
 for det in c.get_DET_seq():pool.append({'seq':det,'name':c.seq2name[det],'natural_M0_plus_egestion_inflow':natural[det],'fishery_return_inflow':c.discard_return[det].sum(),'total_inflow':inflow[det],'consumer_removal':c.predation[det],'printed_BA':c.growth[det],'source_BA_rate':model['group'][det-1]['biomass_accum_rate'],'deficit_removal_plus_BA_minus_inflow':c.predation[det]+c.growth[det]-inflow[det],'residual_BA_that_would_close':inflow[det]-c.predation[det],'residual_BA_adopted':False})
 save('detritus_budgets.json',pool)
 pp_import=c.p[c.get_PP_seq()+c.get_Import_seq()].sum()
 exports=(c.catch-c.discard_return.sum(axis=1)+c.growth+c.net_migration+c.det_export+c.respiration).sum()
 save('physical_accounting_summary.json',{'fishery_landings_row_sum':str(sum(landings.values())),'fishery_discards_row_sum':str(sum(returns.values())),'printed_B3_discard_total':'0.2559104','difference_row_sum_minus_printed_total':str(sum(returns.values())-Decimal('0.2559104')),'conditional_discard_deficit_printed_total':str(pred[53]+Decimal('.1')-Decimal('.2559104')),'conditional_discard_deficit_donor_sum':str(pred[53]+Decimal('.1')-sum(returns.values())),'input_pp_plus_diet_import':pp_import,'external_sinks_including_respiration':exports,'whole_system_biomass_residual':pp_import-exports,'no_source_biomass_filled':True,'retained_catch_M0_diet':True,'source_detritus_BA_preserved':True,'interpool_transfers':'none assumed; no native transfer values available','external_detritus_imports':'zero default, no gap-filling inflow','native_initializer_detritus_BA_overwrite_demonstrated':True})
 (OUT/'faithful_printed_BA_state.pkl').write_bytes(pickle.dumps(c))
 save('original_hashes_after_prepare.json',{p:sha(ROOT/p) for p in before})
 assert before==read(OUT/'original_hashes_after_prepare.json')
 print(json.dumps(clean(pool),indent=2))

def diagnose(te):
 c=pickle.loads((OUT/'faithful_printed_BA_state.pkl').read_bytes())
 label=te.replace(' ','_');log={'call':f'PPRCalculator.diagnose_sppr(experimental_adapter, TE_option={te!r}, short=False, flat=False)','subclass':'RoutingExperimentCalculator','experimental_not_native':True}
 try:
  with warnings.catch_warnings(record=True) as ws,contextlib.redirect_stdout(io.StringIO()) as txt:
   warnings.simplefilter('always')
   # Call the unchanged inherited direct diagnostic explicitly; overridden accounting
   # hooks are precisely documented in routing_adapter.py.
   raw=PPRCalculator.diagnose_sppr(c,TE_option=te,short=False,flat=False)
  (OUT/f'diagnose_{label}_raw.pkl').write_bytes(pickle.dumps(raw));save(f'diagnose_{label}_raw.json',raw)
  log.update(status='RETURNED',diagnostic_status=raw['status'],warnings=[str(w.message) for w in ws],stdout=txt.getvalue())
  if hasattr(c,'last_solve'):
   S,A,L=c.last_solve
   for name,obj in [('SPPR',S),('A',A),('L',L)]:obj.to_csv(OUT/f'{label}_{name}.csv')
   totals=S.sum(axis=1)
   save(f'{label}_negative_audit.json',{'negative_totals':[{'seq':int(i),'name':c.seq2name[i],'coefficient':totals[i]} for i in totals.index[totals<0]],'negative_contributions':[{'seq':int(i),'name':c.seq2name[i],'source':int(j),'contribution':S.loc[i,j]} for i in S.index for j in S.columns if S.loc[i,j]<0],'nonfinite_contributions':int((~np.isfinite(S.to_numpy())).sum()),'all_biological_groups_checked':54})
   S.assign(total=totals,name=[c.seq2name[i] for i in S.index],catch=c.catch.reindex(S.index)).to_csv(OUT/f'{label}_group_coefficients.csv')
  if hasattr(c,'last_recycling_system'):save(f'{label}_recycling_system.json',c.last_recycling_system)
  if hasattr(c,'detritus_resolution_info'):save(f'{label}_detritus_resolution.json',c.detritus_resolution_info)
 except Exception as e:log.update(status='EXCEPTION',exception_type=type(e).__name__,exception=str(e),traceback=traceback.format_exc())
 save(f'diagnose_{label}_execution.json',log)
 print(json.dumps(clean(log),indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--diagnose',choices=['GE','TE','With Egestion']);a=p.parse_args()
 if a.prepare:prepare()
 if a.diagnose:diagnose(a.diagnose)
