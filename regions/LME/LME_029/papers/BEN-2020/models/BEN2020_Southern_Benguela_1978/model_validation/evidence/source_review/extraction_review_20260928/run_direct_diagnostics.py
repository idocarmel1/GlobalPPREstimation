from pathlib import Path
import sys,json,copy,traceback,warnings,time,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[3];MODEL=ROOT/'regions/LME_029/models/BEN2020_Southern_Benguela_1978';TABLES=MODEL/'extracted_tables';OUT=MODEL/'diagnostics';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from PPRCalculator import PPRCalculator
from ModelData import ModelData

def encode(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if hasattr(x,'to_dict'):return x.to_dict()
 raise TypeError(str(type(x)))
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,default=encode),encoding='utf-8')
if len(sys.argv)==1:
 source=next(TABLES.glob('29_*.json'));canonical=json.loads(source.read_text());ex=json.loads((ROOT/'regions/LME_029/extraction_review_20260928/extraction_input.json').read_text(encoding='utf-8'))
 for g,s in zip(canonical['group'],ex['groups']):
  # Explicit source-fidelity adapter: undo converter diet normalization; preserve unknown routing.
  seq=str(g['group_seq'])
  if seq in ex['diet']:
   g['diet_imp']=ex['diet'][seq]['import']
   g['diet_descr']={'diet':[{'prey_seq':k,'proportion':v,'detritus_fate':'-9999'} for k,v in ex['diet'][seq].items() if k!='import' and float(v)>0]}
  g['habitat_area']='-9999'
  g['vbk']={7:'2.590',8:'2.590',9:'1.060',10:'1.060',13:'0.400',14:'0.400',28:'0.046',29:'0.046',30:'0.046',31:'0.046'}.get(int(seq),'-9999')
  g['shadow_price']='-9999'
  if int(seq)==49:g['export']='-9999'
  # Converter omits printed Z, TL and PQ; preserve them in the canonical representation.
  g['source_total_mortality']=s['z'] if s['z'] is not None else '-9999';g['source_trophic_level']=s['tl']
  g['ge']=s['pq'] if s['pq'] is not None else '-9999';g['ge_input']='true' if s['pq'] is not None else 'false'
 canonical['source_metadata']={'model_id':MODEL.name,'paper_id':'BEN-2020','baseline_year':1978,'Ecosim_period':'1978–2015','area_km2':220000,'selected':False,'catch':'total catch, no landings/discards separation','PB_source_caveat':'Table 2 puts ten multi-stanza rates in total-mortality Z; supplementary S1 explicitly supplies PB for eight, deep-water hake PB remains blank. No Z=PB substitution.','BA_source_caveat':'Sardine BA/B=0.3 at stock level in S1 applied to both stanzas as the shared proportional rate; possible EwE multi-stanza accounting mismatch. WC rock lobster absolute BA=-0.603 in Table 2 footnote.','GS_source_caveat':'Supplement 3.10 gives conditional GS=.35 zooplanktivorous fish, .30 fish+zooplankton, .20 heavily predatory groups. .35 recorded only for five fish with exclusively zooplankton diets; exact scope of remaining groups unspecified.','converter_conventions':['Converter habitat area1 removed: source habitat fraction remains-9999; biomass density unchanged','Unreported discard split is blank; reported total catch stored in Landings','Routing source unknown; converter zeros are not source evidence','Source growth K from S1 retained in vbk for ten stanzas; remaining vbk and all shadow prices remain unknown'],'source_fleet_catch':ex['landings'],'source_fleets':ex['fleets']}
 dump(MODEL/'model.json',canonical)
 staged=copy.deepcopy(canonical);changes=[]
 for n in [30,31]:
  g=staged['group'][n-1];s=ex['groups'][n-1];v=float(s['pq'])*float(s['qb']);g['pb']=str(v)
  changes.append({'seq':n,'group':g['group_name'],'field':'pb','canonical':'-9999','diagnostic_value':v,'equation':f"published P/Q {s['pq']} × Q/B {s['qb']}",'basis':'algebraic completion using rounded printed ratios; not a published PB cell or fitted repair'})
 adapter=OUT/'29_20201978_Southern_Benguela_PQ_completed_(1978).json';adapter.write_text(json.dumps(staged,indent=2,ensure_ascii=True),encoding='ascii')
 dump(OUT/'staging_transformations.json',{'source_to_staging':changes,'runtime':{'underdetermined':False,'zero_catch':False,'zero_biomass_accum':True,'default_gs':True,'normalize_DC':False,'DC_tol':0.001},'defaults':['Unknown BA becomes0 except the source sardine and WCRL values','40 consumer GS values receive default0.2; five canonical planktivore fish retain source-derived0.35','No diet normalization: source maximum sum1.0002 within stated loader tolerance','Unknown one-pool detritus routing receives loader closed-pool default; not paper-stated routing','Detritus EE overwritten from0.243 to1; detritus BA completed by loader','Unreported migration and detritus imports become0','No missing biological biomass; synthetic diet_import biomass may default1','ModelData LME hardcode13 corrected in memory to29; adapter number local study identifier, not EcoBase accession'],'strict_source_admission':'qualified/not complete: two PB missing, exact conditional GS scope unresolved, unknown BA for46groups, no detritus routing or native multistanza equations','production_eligible':False,'canonical_sha256':hashlib.sha256((MODEL/'model.json').read_bytes()).hexdigest()})
else:
 option=sys.argv[1];key=option.lower().replace(' ','_');start=time.time()
 try:
  with warnings.catch_warnings(record=True) as caught:
   warnings.simplefilter('always');md=ModelData(str((OUT/'29_20201978_Southern_Benguela_PQ_completed_(1978).json').resolve()));md.lme=29
   calc=PPRCalculator.from_modeldata(md,underdetermined=False,zero_catch=False,zero_biomass_accum=True,default_gs=True,normalize_DC=False,DC_tol=.001)
   calc._groups_df.to_csv(OUT/'loaded_groups.csv',encoding='utf-8');calc._DC.to_csv(OUT/'loaded_diet.csv',encoding='utf-8')
   result=calc.diagnose_sppr(TE_option=option,short=False,flat=False)
  dump(OUT/f'{key}_direct_return.json',result);dump(OUT/f'{key}_execution.json',{'status':'completed','seconds':time.time()-start,'call':f'PPRCalculator.diagnose_sppr(TE_option={option!r},short=False,flat=False)','warnings':[str(w.message) for w in caught]});print(option,'completed',result.get('status'),list(result))
 except Exception as e:
  dump(OUT/f'{key}_execution.json',{'status':'NOT_RUN','seconds':time.time()-start,'exception':str(e),'traceback':traceback.format_exc()});print(option,'NOT_RUN',str(e));raise
