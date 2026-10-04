"""Load only our isolated canonical JSON; deny legacy answer preloads before read."""
from pathlib import Path
import csv, datetime, hashlib, json, math, sys, time, traceback, warnings
ROOT=Path(__file__).resolve().parents[7]
RUN=ROOT/'regions/LME/LME_028/work/2026-10-04_000009_skill_efficiency'
OUT=RUN/'outputs/blind_extraction'; E=OUT/'evidence'; MODEL=OUT/'model_2000s/model.json'
ENGINE=ROOT/'tools/scientific_code/PPREstimation'
denied=[]
def guard(event,args):
    if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
    p=Path(args[0].decode() if isinstance(args[0],bytes) else args[0]).resolve()
    if 'real_models' in [part.casefold() for part in p.parts] or (p.is_relative_to(ROOT/'regions') and not p.is_relative_to(OUT) and not p.is_relative_to(RUN/'code/blind_extraction')):
        denied.append({'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'action':'blocked before open/read','event':event})
        raise PermissionError('Blind-extraction guard prohibits answer/data access')
sys.addaudithook(guard)
sys.path.insert(0,str(ENGINE))
start=datetime.datetime.now(datetime.timezone.utc).isoformat(); clock=time.perf_counter()
from ModelData import ModelData
data=json.loads(MODEL.read_text(encoding='utf-8'))
missing_before=[{'seq':g['group_seq'],'name':g['group_name'],'field':f,'value':g.get(f)} for g in data['group'] for f in ['biomass','pb','qb','ee'] if g.get(f) in (None,'-9999')]
loaded=ModelData(str(MODEL))
species={g.group_seq:g for g in ModelData.get_species_groups(data)}
rows=[['group_seq','group_name','scope','field','source_json_field','source_value','runtime_value','change_status','reason']]
def ser(v):
    if v is None:return 'null'
    if isinstance(v,float) and math.isnan(v):return 'NaN'
    return str(v)
def add(seq,name,scope,f,sf,source,runtime,reason=''):
    try:equal=source not in (None,'-9999') and abs(float(source)-float(runtime))<=1e-12
    except (TypeError,ValueError):equal=source==runtime
    status='same_known_value' if equal else 'unknown_to_NaN' if source in (None,'-9999') and ser(runtime)=='NaN' else 'transformed_or_defaulted'
    rows.append([seq,name,scope,f,sf,ser(source),ser(runtime),status,reason])
mapping={'biomass':'biomass','pb':'pb','qb':'qb','ee':'ee','ge':'ge','gs':'gs','tl':'tl','M0b':'other_mort','respiration':'respiration','biomass_accum':'biomass_accum','biomass_accum_rate':'biomass_accum_rate','immigration':'immigration','emigration':'emigration','export':'export','detritus_import':'detritus_import','diet_import':'diet_imp','group_name':'group_name'}
for g in data['group']:
    n=int(g['group_seq']);name=g['group_name'];s=species[n]
    for f,sf in mapping.items():
        reason='derived PB*(1-EE), not published M0 rate' if f=='M0b' else 'non-detritus forced0 by loader' if f=='detritus_import' and n!=38 else 'loader always sets TL NaN' if f=='tl' else ''
        add(n,name,'species_group',f,sf,g.get(sf),getattr(s,f),reason)
    for item in (g.get('diet_descr') or {}).get('diet',[]) or []:
        prey=int(item['prey_seq']);add(n,name,'diet','prey_'+str(prey),'diet_descr.diet.proportion',item['proportion'],float(loaded.DC.loc[n,prey]),'source absent-prey sentinel interpreted0; positive cells unnormalized')
    add(n,name,'diet','outside_import','diet_imp',g['diet_imp'],float(loaded.DC.loc[n,39]),'unknown import remainsNaN')
    add(n,name,'routing','to_detritus38','detritus_fate_by_pool.38',g['detritus_fate_by_pool']['38'],float(loaded.det_fate.loc[n,38]),'Single-pool closed routing1 imposed by ModelData; detritus self-identity imposed')
add('model','Northern South China Sea','metadata','LME','metadata.LME',data['metadata']['LME'],loaded.lme,'ModelData hardcodes13, whereas extracted metadataLME28; no source change')
rows.append([39,'diet_import','synthetic','group','absent','absent','added','transformed_or_defaulted','Loader adds import pseudo-group; TL1, respiration0, no source biomass'])
with (E/'loader_transformation_ledger.csv').open('w',encoding='utf-8',newline='') as f:csv.writer(f).writerows(rows)
known_checks=[]
for g in data['group']:
    n=int(g['group_seq'])
    for f in ['biomass','pb','qb','ee']:
        if g[f]!='-9999':known_checks.append(abs(float(g[f])-float(loaded.groups_data.loc[n,f]))<=1e-12)
assert all(known_checks)
assert all(g['group_name']==loaded.groups_data.loc[int(g['group_seq']),'group_name'] for g in data['group'])
settings={'underdetermined':False,'zero_catch':False,'zero_biomass_accum':False,'default_gs':False,'weight_flow':1.0,'weight_guess':1.0,'normalize_DC':False,'DC_tol':0.001,'balance_BA_after_DC_normalization':False}
constructor={'attempted':False}
try:
    from PPRCalculator import PPRCalculator
    constructor['attempted']=True
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always');calc=PPRCalculator(str(MODEL),**settings)
    constructor.update({'completed':True,'warnings':[str(w.message) for w in caught]})
except Exception as error:
    constructor.update({'completed':False,'exception_type':type(error).__name__,'exception':str(error),'traceback':traceback.format_exc()})
result={'started_utc':start,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-clock,'canonical_sha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'engine_code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ENGINE/'ModelData.py',ENGINE/'PPRCalculator.py',ENGINE/'utils.py']},'constructor_settings':settings,'raw_modeldata_load_success':True,'real_source_groups':38,'loaded_groups':len(loaded.groups_data),'source_unknown_B_PB_QB_EE_before_load':missing_before,'known_B_PB_QB_EE_same_within_1e12':all(known_checks),'known_parameter_cells_checked':len(known_checks),'known_group_names_identical':True,'diet_known_positive_cells_unchanged':all(abs(float(item['proportion'])-loaded.DC.loc[int(g['group_seq']),int(item['prey_seq'])])<=1e-12 for g in data['group'] for item in (g.get('diet_descr') or {}).get('diet',[]) or [] if item['proportion']!='-9999'),'normalization_requested':False,'constructor':constructor,'denied_preload_attempts':denied,'diagnostics_or_PPR_calculation':'not requested; not executed','loaded_state_not_saved':'Ephemeral runtime; only field transformation ledger retained, no loaded-model JSON','audit_wrapper_repair':'Initial wrapper AttributeError on basal null diet_descr corrected by treating null as absent; no model numerical changes'}
(E/'load_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
