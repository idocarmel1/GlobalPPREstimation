"""Bounded requested scenario; canonical inputs and published results stay unchanged."""
from pathlib import Path
import sys,json,hashlib,gzip,copy,warnings,os,platform
from datetime import datetime, timezone
sys.dont_write_bytecode=True
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
MODEL=ROOT/'regions/LME/LME_049/papers/KUR-2019/models/49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'
OUT=Path(__file__).resolve().parent.parent/'outputs'
OUT.mkdir(exist_ok=True,parents=True)
ENGINE=Path(__file__).resolve().parent/'engine'
if not ENGINE.exists():ENGINE=ROOT/'tools/scientific_code/PPREstimation'
sys.path.insert(0,str(ENGINE))
sys.path.insert(1,str(ROOT/'research/agents/regional_ge_integration_20260928/evidence'))
import numpy as np
import pandas as pd
from ModelData import ModelData
from PPRCalculator import PPRCalculator
from runtime_codec import encode,decode
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def gz(name,obj):(OUT/(name+'.gz')).write_bytes(gzip.compress(json.dumps(obj,ensure_ascii=False,allow_nan=False).encode('utf-8'),mtime=0))
protected_paths=[ROOT/'Project.xlsx',ROOT/'regions/LME/LME_049/LME_049.xlsx',MODEL/'model.json',MODEL/'model_notes.md']
protected_paths += [p for folder in [MODEL/'inputs',MODEL/'extracted_tables',MODEL.parent.parent/'sources',ROOT/'interactive_map'] if folder.exists() for p in folder.rglob('*') if p.is_file()]
protected={p.relative_to(ROOT).as_posix():sha(p) for p in protected_paths if p.exists()}
save('protected_before.json',protected)
settings=dict(underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=True,weight_flow=1.,weight_guess=1.,normalize_DC=True,DC_tol=.001,balance_BA_after_DC_normalization=False,use_ee_floor=True,ee_floor=.1,ee_threshold=.1,refresh_missing_biomass_accum=True)
md=ModelData(str(MODEL/'model.json'))
raw_source=encode(vars(md))
scenario_md=copy.deepcopy(md)
before_fate=scenario_md.det_fate.copy()
scenario_md.det_fate.loc[3,:]=0.
assert md.det_fate.equals(before_fate)
assert scenario_md.groups_data.equals(md.groups_data) and scenario_md.DC.equals(md.DC)
save('settings.json',{'timestamp_utc':datetime.now(timezone.utc).isoformat(),'model_id':MODEL.name,'canonical_sha256':sha(MODEL/'model.json'),'constructor':settings,'routing_override':{'group':3,'name':'Seabirds (all)','detritus_fraction':0,'unrouted_fraction':1,'destination':'other external export (existing det_export sink, not catch or a trophic group)'},'scope':'Fresh GE, TE and With Egestion diagnostics; no publication or adoption','engine_hashes':{n:sha(ENGINE/n) for n in ['ModelData.py','PPRCalculator.py','utils.py','create_PPRS_excel.py']},'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__})
with warnings.catch_warnings(record=True) as ws:
 c=PPRCalculator.from_modeldata(scenario_md,**settings)
save('constructor_warnings.json',[str(x.message) for x in ws])
gz('initial_runtime.json',encode(vars(c)))
save('ee_floor_info.json',c.ee_floor_info)
save('ee_floor_ledger.json',encode(c.ee_floor_ledger))
save('missing_biomass_accum_ledger.json',encode(c.missing_biomass_accum_ledger))
c.missing_biomass_accum_ledger.to_csv(OUT/'missing_biomass_accum_ledger.csv',index_label='group_id')
c.ee_floor_ledger.to_csv(OUT/'ee_floor_ledger.csv',index_label='group_id')
c._groups_df.to_csv(OUT/'runtime_groups.csv',index_label='group_id')
c._det_fate.to_csv(OUT/'runtime_detritus_fates.csv',index_label='group_id')
base=encode(vars(c))
bal,production,consumption=c.is_model_balanced()
residuals=pd.DataFrame({'name':pd.Series(c.seq2name),'p':c.p,'q':c.q,'production_components':production,'production_residual':production-c.p,'consumption_components':consumption,'consumption_residual':consumption-c.q,'BA':c.growth,'predation':c.predation,'M0':c.M0,'egestion':c.egestion,'external_mortality_export':c.external_mortality_export,'det_export':c.det_export})
residuals.to_csv(OUT/'flow_residuals.csv',index_label='group_id')
results={};negative=[]
for option in ['GE','TE','With Egestion']:
 key=option.replace(' ','_'); calc=copy.deepcopy(c)
 with warnings.catch_warnings(record=True) as ws:
  try:
   ret=calc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
  except Exception as ex:
   save(key+'_exception.json',{'type':type(ex).__name__,'message':str(ex)})
   results[option]={'execution':'exception','message':str(ex)}
   continue
 report,S,A,L=ret
 save(key+'_full_return.json',encode(ret));save(key+'_diagnostic.json',report)
 gz(key+'_runtime_after.json',encode(vars(calc)))
 for name,m in [('source_coefficients',S),('A',A),('L',L)]:m.to_csv(OUT/(key+'_'+name+'.csv'),index_label='recipient_id')
 total=S.sum(axis=1).reindex(c.p.index)
 diet_s=c._DC@total
 unrouted=1-c._det_fate.sum(axis=1).reindex(total.index)
 mortality_export_value=float((unrouted*c.M0*total).sum())
 egestion_export_value=float((unrouted*c.egestion*diet_s).sum())
 terms=pd.DataFrame({'name':pd.Series(c.seq2name),'sppr':total,'BA_weighted':c.growth*total,'catch_weighted':c.catch*total,'floor_export_weighted':c.external_mortality_export*total,'unrouted_M0_weighted':unrouted*c.M0*total,'unrouted_egestion_prey_weighted':unrouted*c.egestion*diet_s,'production_residual_weighted':(production-c.p)*total})
 terms.to_csv(OUT/(key+'_budget_terms.csv'),index_label='group_id')
 for recipient in S.index:
  for basal in S.columns:
   value=float(S.loc[recipient,basal])
   if value<0:negative.append({'method':option,'recipient_id':int(recipient),'recipient_name':c.seq2name[recipient],'source_id':int(basal),'source_name':c.seq2name[basal],'value':value,'tolerance':0})
 # The corrected checker includes the method-specific export in its returned outflow.
 export_add= mortality_export_value if option=='GE' else mortality_export_value+egestion_export_value if option=='With Egestion' else 0.
 official_gap=report['balance']['outflow']-report['balance']['inflow']
 weighted_residual=float(((production-c.p)*total).sum())
 results[option]={'execution':'returned','status':report['status'],'divergence':report['divergence'],'balance':report['balance'],'model_input':report['model_input'],'warnings':[str(x.message) for x in ws],'negative_entries':int((S<0).sum().sum()),'all_coefficients_finite':bool(np.isfinite(S.to_numpy()).all()),'weighted_unrouted_M0':mortality_export_value,'weighted_unrouted_egestion':egestion_export_value,'additional_budget_audit':{'unrouted_export_included_in_checker':export_add,'official_signed_gap':official_gap,'gap_including_method_specific_unrouted_export':official_gap,'weighted_local_production_residual':weighted_residual,'difference':official_gap-weighted_residual,'not_an_engine_grade':True},'full_return_roundtrip_equal':encode(decode(json.loads((OUT/(key+'_full_return.json')).read_text(encoding='utf-8'))))==encode(ret)}
 print(option,json.dumps({'status':report['status'],'negative_entries':results[option]['negative_entries'],'balance':report['balance'],'additional_budget_audit':results[option]['additional_budget_audit']}),flush=True)
save('negative_entries.json',negative)
source_unchanged=encode(vars(md))==raw_source
changed=[p for p,h in protected.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
summary={'requested_configuration':settings,'results':results,'local_mass_balance':bool(bal),'seabird_runtime':{'p':float(c.p[3]),'q':float(c.q[3]),'EE':float(c.EE[3]),'M0':float(c.M0[3]),'egestion':float(c.egestion[3]),'floor_export':float(c.external_mortality_export[3]),'other_export':float(c.det_export[3]),'to_detritus':float(((c.M0+c.egestion)[3])*c._det_fate.loc[3].sum()),'TE':float(c.get_TE('TE',as_matrix=False)[3])},'source_ModelData_unchanged':source_unchanged,'initial_runtime_unchanged_by_diagnostics':encode(vars(c))==base,'protected_files':len(protected),'changed_files':changed,'adopted':False}
save('summary.json',summary)
checks={'source_ModelData_unchanged':source_unchanged,'canonical_and_existing_files_unchanged':not changed,'seabird_routes_zero_to_detritus':summary['seabird_runtime']['to_detritus']==0,'seabird_other_export_equals_M0_plus_egestion':np.isclose(c.det_export[3],c.M0[3]+c.egestion[3]),'EE_floor_applied_to_seabird':c.EE[3]==.1,'all_methods_returned':len(results)==3 and all(v['execution']=='returned' for v in results.values()),'full_returns_reopened_losslessly':all(v.get('full_return_roundtrip_equal',False) for v in results.values()),'runtime_unchanged_by_diagnostics':encode(vars(c))==base}
checks={k:bool(v) for k,v in checks.items()}
save('verification.json',checks)
assert all(checks.values()),checks
paths=list(OUT.iterdir())+list(Path(__file__).parent.glob('*.py'))+[MODEL/'model.json']+[ENGINE/n for n in ['PPRCalculator.py','ModelData.py','utils.py']]
artifacts=[{'role':'diagnostic evidence' if p.parent==OUT else 'code or canonical input','path':os.path.relpath(p,OUT).replace('\\','/'),'sha256':sha(p),'availability':'present'} for p in paths if p.is_file() and p.name not in ['evidence_index.json','completeness.json']]
save('evidence_index.json',{'schema_version':1,'run_id':'2026-11-14_final_flow_accounting','region_id':'LME_049','model_id':MODEL.name,'artifacts':artifacts,'methods':['GE','TE','With Egestion'],'canonical_input_sha256':sha(MODEL/'model.json')})
assert all(sha(OUT/x['path'])==x['sha256'] for x in artifacts)
save('completeness.json',{'all_artifacts_reopened_hash_verified':True,'artifact_count':len(artifacts),'verification_passed':all(checks.values()),'adoption':False,'scope':'three deterministic methods only; no Monte Carlo rerun, source extraction or publication'})
print('VERIFIED',json.dumps(summary['seabird_runtime']),flush=True)
