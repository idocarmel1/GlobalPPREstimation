from pathlib import Path
import sys, json, pickle, hashlib, importlib.util, io, copy, ast, math
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
OUT=HERE.parent
ROOT=next(p for p in HERE.parents if (p/'Project.xlsx').exists())
MODEL=OUT.parents[3]
BASE=OUT.parent/'ee_floor_20261114'
HIST=BASE/'code/historical'
CURRENT=BASE/'code/current'
def file_hash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert file_hash(MODEL/'model.json')=='b4ba75b14c47a23b2b97aaacdc4b392f2183679e201942c35f36b910c92b63cf'
for item in json.loads((BASE/'authentication.json').read_text(encoding='utf-8')):
 p=BASE/'code'/item['file'] if item['file'].startswith('current/') else HIST/item['file']
 assert file_hash(p)==item['sha256'],str(p)
for f in ('PPRCalculator.py','ModelData.py','utils.py'):
 assert file_hash(CURRENT/f)==file_hash(ROOT/'tools/scientific_code/PPREstimation'/f),f+' changed after snapshot'
def load(name, file):
 spec=importlib.util.spec_from_file_location(name,file);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
oldutils=load('utils',HIST/'utils.py')
olddata=load('ModelData',HIST/'ModelData.py')
oldcalc=load('PPRCalculator',HIST/'PPRCalculator.py')
oldadapter=load('routing_adapter',HIST/'routing_adapter.py')
allowed={('routing_adapter','RoutingExperimentCalculator'),('ModelData','ModelData'),('pandas.core.frame','DataFrame'),('pandas.core.internals.managers','BlockManager'),('pandas.core.internals.managers','SingleBlockManager'),('pandas._libs.internals','_unpickle_block'),('numpy._core.multiarray','_reconstruct'),('numpy','ndarray'),('numpy','dtype'),('builtins','slice'),('pandas.core.indexes.base','_new_Index'),('pandas.core.indexes.base','Index'),('pandas.core.series','Series')}
class Restricted(pickle.Unpickler):
 def find_class(self,module,name):
  if (module,name) not in allowed:raise ValueError('Unapproved pickle global '+module+'.'+name)
  return super().find_class(module,name)
 def persistent_load(self,pid):raise ValueError('Persistent ID disallowed')
pickle_path=OUT.parent/'diet_reextraction_20261002/inputs_by_sha256/99a217b06fc7ad7ab2cc057ba54194ee02d5d3906dd78ee84114c27cca009099/faithful_printed_BA_state.pkl'
raw=pickle_path.read_bytes();assert raw[-1:]==b'.';assert hashlib.sha256(raw).hexdigest()=='99a217b06fc7ad7ab2cc057ba54194ee02d5d3906dd78ee84114c27cca009099'
historical=Restricted(io.BytesIO(raw)).load()
print('Authenticated state loaded',flush=True)
encoder_ast=ast.parse((CURRENT/'method_coverage.py').read_text(encoding='utf-8'))
encoder_ast.body=[n for n in encoder_ast.body if isinstance(n,ast.FunctionDef) and n.name in ('_mask_kind','encode_lossless')]
exec(compile(encoder_ast,str(CURRENT/'method_coverage.py'),'exec'))
def save(name,value):
 (OUT/name).write_text(json.dumps(encode_lossless(value),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
newutils=load('utils',CURRENT/'utils.py')
newdata=load('ModelData',CURRENT/'ModelData.py')
newcalc=load('current_calculator',CURRENT/'PPRCalculator.py')
current=newcalc.PPRCalculator.__new__(newcalc.PPRCalculator)
current.__dict__=copy.deepcopy(historical.__dict__)
# Construction is deliberately bypassed: this is the authenticated completed initialization.
current._discard_returns=copy.deepcopy(historical.discard_return)
current.discard_returns_metadata={'status':'complete','source':'Authenticated historical explicit fishery-discard return matrix; natural mortality/egestion to Detritus54, fishery discard to Discards53','schema':'authenticated historical Celtic routing-adapter matrix','units':'t wet weight per square kilometre per year, as retained catch','catch_modified':False,'amount_source':'Hernvann supplement B3 donor discard amounts','routing_basis':'Previously accepted assumption: all donor fishery discards to Discards53; none to Detritus54','unresolved':[],'provenance':'../ee_floor_20261114/authentication.json'}
current._initialize_discard_returns()
if '--inspect' in sys.argv:
 save('state_inspection.json',{'attributes':{k:str(type(v)) for k,v in historical.__dict__.items()},'nested_model_attributes':{k:str(type(v)) for k,v in historical._model.__dict__.items()},'groups':historical._groups_df,'source_groups':historical._model.groups_data,'returns':historical.discard_return,'Z_old':historical.get_Z(False),'Z_current':current.get_Z(False)})
 print('Inspection saved',flush=True)
 raise SystemExit(0)

import time, platform, traceback, warnings, datetime
from pandas.testing import assert_frame_equal, assert_series_equal
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
checks={}
def same(a,b):
 if isinstance(a,pd.DataFrame):assert_frame_equal(a,b,check_exact=True)
 elif isinstance(a,pd.Series):assert_series_equal(a,b,check_exact=True)
 elif isinstance(a,np.ndarray):np.testing.assert_array_equal(a,b)
 elif isinstance(a,dict):
  assert a.keys()==b.keys()
  for k in a:same(a[k],b[k])
 elif isinstance(a,(list,tuple)):
  assert len(a)==len(b)
  for av,bv in zip(a,b):same(av,bv)
 elif hasattr(a,'__dict__'):same(a.__dict__,b.__dict__)
 else:assert a==b or (isinstance(a,float) and isinstance(b,float) and np.isnan(a) and np.isnan(b)),(a,b)
for k,v in historical.__dict__.items():same(v,current.__dict__[k])
checks['all_historical_attributes_and_nested_model_exact_before_import_completion']=True
assert set(historical.discard_return.columns)==set(current._discard_returns.columns)
assert_frame_equal(historical.discard_return,current._discard_returns.reindex(index=historical.discard_return.index,columns=historical.discard_return.columns),check_exact=True,check_names=False)
checks['return_matrix_values_exact_after_explicit_label_alignment']=True
same(historical.get_Z(False),current.get_Z(False))
checks['all_native_donor_flows_equal_historical_adapter_before_import_completion']=True
np.testing.assert_allclose(current._external_catch(),historical.catch-historical.discard_return.sum(axis=1),rtol=0,atol=0)
checks['external_catch_counts_returns_once']=True
source=json.loads((MODEL/'model.json').read_text(encoding='utf-8'))['group']
source_by_id={int(g['group_seq']):g for g in source}
for seq,g in source_by_id.items():
 assert current._groups_df.loc[seq,'biomass']==float(g['biomass'])
 assert current.seq2name[seq]==g['group_name']
checks['source_biomass_names_and_printed_zero_groups_preserved']=True
assert current.growth[53]==.1 and current.growth[54]==481.12
assert current.seq2name[20]=='Plaice' and np.isclose(current.growth[20],-.0004,rtol=0,atol=1e-15)
current.source_EE=pd.Series({seq:(float(source_by_id[seq]['ee']) if seq in source_by_id and source_by_id[seq]['ee']!='-9999' else np.nan) for seq in current.p.index})
current.source_M0=pd.Series(np.nan,index=current.p.index)
assert np.isnan(current.source_EE[18])
current._initialization_settings={'historical_state':'faithful_printed_BA_state.pkl','underdetermined':False,'zero_catch':True,'zero_biomass_accum':True,'default_gs':True,'normalize_DC':False,'historical_separate_diet_normalization':True,'bridge':'deepcopy completed historical state to plain current PPRCalculator; native discard-return validator only; no loader/default/completion rerun'}
fields=('_groups_df','_DC','_det_fate','p','q','catch','predation','growth','immigration','emigration','net_migration','respiration','egestion','M0','det_export','EE','GE','GS','TL','seq2name','name2seq','_discard_returns','source_EE','source_M0','_initialization_settings')
def state(c):return {k:getattr(c,k) for k in fields if hasattr(c,k)}
save('historical_before_import_state.json',state(current))
import_before=copy.deepcopy(current._DC)
current._DC=current._DC.copy(deep=True)
flow_before=current.get_Z(False).copy(deep=True)
corrections=[]
for seq,raw_sum in ((3,.999),(28,1.0)):
 assert source_by_id[seq]['diet_imp']=='-9999'
 assert np.isnan(import_before.loc[seq,55])
 assert np.isclose(import_before.loc[seq].sum(skipna=True),1.,rtol=0,atol=1e-12)
 current._DC.loc[seq,55]=0.
 corrections.append({'group_seq':seq,'group_name':current.seq2name[seq],'source_field':'diet_imp','source_literal':'-9999','source_meaning':'blank Import cell in supplement B2 pp14-15','runtime_before':np.nan,'runtime_after':0.,'raw_internal_diet_sum':raw_sum,'normalization_preserved':True,'outside_feeding_statement_found':False,'basis':'User instruction: fill missing diet import with 0 when source does not mention external feeding','canonical_changed':False})
expected_dc=import_before.copy(deep=True)
expected_flow=flow_before.copy(deep=True)
for seq in (3,28):
 expected_dc.loc[seq,55]=0.
 expected_flow.loc[seq,55]=0.
same(expected_dc,current._DC)
same(historical._model.__dict__,current._model.__dict__)
checks['nested_historical_source_model_unchanged_after_import_completion']=True
same(expected_flow,current.get_Z(False))
for f in fields:
 if f not in ('_DC','_initialization_settings','source_EE','source_M0') and hasattr(historical,f):same(getattr(historical,f),getattr(current,f))
checks['only_two_runtime_import_cells_completed_before_floor']=True
checks['only_two_nan_import_flow_cells_changed_before_floor']=True
checks['other_historical_scientific_attributes_exact_after_import_completion']=True
current._initialization_settings['import_completion']={'groups':[3,28],'source_column':55,'value':0.,'application_stage':'after authenticated normalization and before EE floor','source_inputs_preserved':True,'policy':'published explicit imports take precedence; no external feeding statement found for these groups, so zero under user instruction'}
save('import_completion.json',{'corrections':corrections,'historical_base':'../ee_floor_20261114/evidence_index.json','canonical_sha256':file_hash(MODEL/'model.json'),'scope':'authorized initialization completion only; no production rebalancing; original source blanks retained','source_document':'../../../../../../sources/Data_Sheet_1_TheCelticSeaThroughTimeandSpa-165f24b6.docx'})
before=copy.deepcopy(state(current))
save('pre_floor_state.json',before)
save('historical_source_model_state.json',historical._model.__dict__)
save('pre_floor_flow_matrix.json',current.get_Z(False))
assert not hasattr(current,'_ee_floor_base')
print('Pre-floor invariants passed; applying ON 0.1',flush=True)
with warnings.catch_warnings(record=True) as caught:
 warnings.simplefilter('always')
 current.apply_ee_floor(use_ee_floor=True,ee_floor=.1,ee_threshold=.1)
 floor_warnings=[str(w.message) for w in caught]
assert current.use_ee_floor is True and current.ee_floor==.1 and current.ee_threshold==.1
assert current is not current.balanced_model
living=current._groups_df.index[current._groups_df.trophic_info.isin(['Regular','PP'])]
for f in ('p','q','catch','predation','growth','net_migration','respiration','egestion'):
 same(before[f].loc[living],getattr(current,f).loc[living])
for f in ('_DC','_det_fate','_discard_returns','GE','GS'):
 same(before[f],getattr(current,f))
same(before['_groups_df']['biomass'],current._groups_df['biomass'])
checks['living_biology_catch_diet_fate_returns_unchanged_after_floor']=True
np.testing.assert_allclose(before['M0']-current.M0,current.external_mortality_export,rtol=0,atol=1e-12)
assert (current.external_mortality_export>=0).all()
applied=current.ee_floor_ledger.index[current.ee_floor_ledger.applied]
np.testing.assert_allclose(current.M0.loc[applied],current.p.loc[applied]*(1-current.EE.loc[applied]),rtol=0,atol=1e-12)
assert not current.ee_floor_ledger.loc[18,'applied']
checks['source_missing_ee_excluded_and_sink_reconciled']=True
assert set(int(x) for x in applied)=={3,4,28}
assert current.EE.loc[3]==.1 and current.EE.loc[28]==.1
assert np.isfinite(current._DC.loc[[3,28]].to_numpy(dtype=float)).all()
te_vector=current.get_TE('TE',as_matrix=False)
assert te_vector.loc[3]>0 and te_vector.loc[28]>0
save('TE_efficiency_vector.json',te_vector)
checks['completed_import_groups_floor_eligible_and_positive_TE']=True
pool=[]
for d in current.get_DET_seq():
 natural=float(((current.M0+current.egestion)*current._det_fate[d].reindex(current.p.index).fillna(0)).sum())
 returned=float(current._discard_returns[d].sum())
 expected=natural+returned
 np.testing.assert_allclose([current.p[d],current.q[d]],[expected,expected],rtol=0,atol=1e-10)
 residual=expected-current.predation[d]-current.net_migration[d]-current.catch[d]
 np.testing.assert_allclose(current.growth[d],residual,rtol=0,atol=1e-10)
 pool.append({'group_seq':d,'name':current.seq2name[d],'printed_pre_floor_BA':before['growth'][d],'pre_floor_inflow':before['p'][d],'effective_natural_inflow':natural,'fishery_return':returned,'effective_inflow':expected,'effective_stock_residual':residual,'source_BA_retained_as_evidence_not_effective_residual':True})
checks['detritus_inflow_and_floor_effective_residual_reconciled']=True
ledger={'floor_info':current.ee_floor_info,'groups':current.ee_floor_ledger,'detritus':pool,'warnings':floor_warnings,'scope':'Hypothetical runtime sink; source/derived/pre-floor/effective values remain distinct. No canonical input edits; balanced_model cache never diagnosed.'}
save('floor_accounting.json',ledger)
current.ee_floor_ledger.to_csv(OUT/'floor_accounting.csv',encoding='utf-8')
save('effective_state.json',state(current))
save('effective_flow_matrix.json',current.get_Z(False))
options={'TE':None,'DET_TE_vals':1,'det_collapse_mode':'never','det_open_mode':'none','det_theta':1.0,'det_external_sppr':0.0,'fix_EE_0_cases':True}
summaries={}
negative=[]
effective_before_solve=copy.deepcopy(state(current))
for method in ('GE','TE'):
 print('Running '+method,flush=True)
 t=time.perf_counter()
 try:
  with warnings.catch_warnings(record=True) as caught:
   warnings.simplefilter('always')
   report,S,A,L=current.diagnose_sppr(TE_option=method,short=False,flat=False,return_sppr=True,thresholds=dict(newcalc.DEFAULT_DIAGNOSTIC_THRESHOLDS),**options)
  returned={'report':report,'SPPR':S,'A':A,'L':L}
  save(method+'_full_return.json',returned)
  matrices={}
  for name,M in [('SPPR',S),('A',A),('L',L)]:
   if M is None:
    matrices[name]={'availability':'unavailable','reason':'Solver returned no matrix'};continue
   assert M.index.is_unique and M.columns.is_unique
   a=M.to_numpy(dtype=float)
   masks={k:np.where(fn(a),True,False).tolist() for k,fn in [('nan',np.isnan),('positive_infinity',np.isposinf),('negative_infinity',np.isneginf)]}
   matrices[name]={'shape':list(M.shape),'rows':M.index.tolist(),'columns':M.columns.tolist(),'nonfinite_masks':masks,'finite_min':float(a[np.isfinite(a)].min()) if np.isfinite(a).any() else None,'negative_count':int((a<0).sum()),'orientation':'recipient rows x source columns' if name=='SPPR' else 'native labeled group matrix'}
   M.to_csv(OUT/(method+'_'+name+'.csv'),encoding='utf-8')
   for i,j in zip(*np.where(a<0)):
    negative.append({'method':method,'matrix':name,'recipient_id_or_name':M.index[i],'source_id_or_name':M.columns[j],'value':a[i,j],'comparison_tolerance':0.0})
  if S is not None:
   assert set(int(x) for x in S.index)==set(range(1,56))
   assert set(int(x) for x in S.columns)=={51,52,53,54,55}
   coefficient=S.sum(axis=1,skipna=False)
   coefficient.to_csv(OUT/(method+'_coefficients_all.csv'),encoding='utf-8')
   save(method+'_coefficient_scopes.json',{'all':coefficient,'PP':S.loc[:,[col for col in S.columns if col in current.get_PP_seq() or col in [current.seq2name[s] for s in current.get_PP_seq()]]].sum(axis=1,skipna=False),'scope_definition':'all is all returned basal columns; PP is only source columns51/52. Retains synthetic import55 and every unfished row.'})
   checks[method+'_full_group_universe_retained']=True
  summaries[method]={'outcome':'returned','status':report['status'],'elapsed_seconds':time.perf_counter()-t,'report':report,'matrices':matrices,'warnings':[str(w.message) for w in caught]}
 except Exception as e:
  summaries[method]={'outcome':'execution_exception','status':'EXCEPTION','scientific_status':None,'exception_type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc(),'elapsed_seconds':time.perf_counter()-t}
  save(method+'_full_return.json',summaries[method])
 same(effective_before_solve,state(current))
 checks[method+'_scientific_state_unchanged_by_diagnostic']=True
 save(method+'_post_solve_state.json',state(current))
 save('diagnostic_summary.json',summaries)
 print(method+': '+summaries[method]['status'],flush=True)
save('negative_entries.json',negative)
save('reconciliation.json',checks)
import scipy,sympy,igraph
save('execution.json',{'started_utc':started,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'sympy':sympy.__version__,'igraph':igraph.__version__,'platform':platform.platform(),'runner_sha256':file_hash(Path(__file__)),'canonical_sha256':file_hash(MODEL/'model.json'),'historical_state_sha256':file_hash(pickle_path),'floor':{'use_ee_floor':True,'ee_floor':.1,'ee_threshold':.1},'constructor':current._initialization_settings,'options':options,'thresholds':newcalc.DEFAULT_DIAGNOSTIC_THRESHOLDS,'methods':['GE','TE'],'balanced_model_used':False,'source_scope':'current review/evidence only; no regional or central result adoption'})
print('DONE',flush=True)
