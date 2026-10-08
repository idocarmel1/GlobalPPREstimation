"""Authorized detritus-only experiment; leaves source canonical unchanged."""
from pathlib import Path
from decimal import Decimal as D
import json,copy,hashlib,shutil,sys,subprocess,contextlib,traceback,csv
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
SRC=ROOT/'regions/EEZ_941/models/941_201901_Warm_Pool_(2005)'
MID='941_20190101_Warm_Pool_Detritus_Pooled_Experiment_(2005)'
OUT=SRC.parent/MID;EV=OUT/'evidence';DIAG=OUT/'diagnostics';TABLES=OUT/'extracted_tables'
for p in [OUT,EV,DIAG,TABLES]:p.mkdir(exist_ok=True)
SKILL=Path.home()/'.agents/skills/ecopath-extraction/scripts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(x):
    import numpy as np
    if isinstance(x,dict):return {str(k):safe(v) for k,v in x.items()}
    if isinstance(x,(list,tuple,np.ndarray)):return [safe(v) for v in x]
    if isinstance(x,np.generic):return safe(x.item())
    return x
def dump(p,x):p.write_text(json.dumps(safe(x),indent=2,ensure_ascii=False,default=str)+'\n',encoding='utf-8')
def run(script,args,log):
    p=subprocess.run([sys.executable,str(SKILL/script),*map(str,args)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    log.write_text(p.stdout+'\n'+p.stderr,encoding='utf-8');return p.returncode
expected='523cefaa423538f0609b96b75064594f426d87c8dca997a7973515792c1bafc3'
assert sha(SRC/'model.json')==expected
original=json.loads((SRC/'model.json').read_text(encoding='utf-8'));src=original['group'];assert len(src)==46
shutil.copy2(SRC/'model.json',EV/'source_model_frozen.json')
derived=copy.deepcopy(original);derived['group']=derived['group'][:45];groups=derived['group'];rows=[]
for old,new in zip(src[:42],groups[:42]):
    items=old['diet_descr']['diet'];before=sum((D(d['proportion']) for d in items),D(0))
    a=sum((D(d['proportion']) for d in items if d['prey_seq']=='45'),D(0));b=sum((D(d['proportion']) for d in items if d['prey_seq']=='46'),D(0))
    newitems=[copy.deepcopy(d) for d in items if int(d['prey_seq'])<45]
    if a+b:newitems.append({'prey_seq':'45','proportion':str(a+b),'detritus_fate':'-9999'})
    new['diet_descr']['diet']=newitems;after=sum((D(d['proportion']) for d in newitems),D(0));assert before==after
    assert {k:v for k,v in old.items() if k!='diet_descr'}=={k:v for k,v in new.items() if k!='diet_descr'}
    rows.append({'consumer_seq':old['group_seq'],'consumer':old['group_name'],'detritus_45':str(a),'discards_46':str(b),'pooled_45':str(a+b),'diet_before':str(before),'diet_after':str(after)})
assert groups[42:44]==src[42:44]
pool=groups[44];pool['group_name']='Detritus and fishery discards (pooled experiment)'
pool['biomass']=str(sum(D(g['biomass']) for g in src[44:]));assert D(pool['biomass'])==D('53.001775')
pool['biomass_habitat_area']=pool['biomass'];pool['ee']='-9999';pool['ee_input']='false'
pool['biomass_accum']=str(sum(D(g['biomass_accum']) for g in src[44:]));pool['net_migration']='0'
pool['taxon_descr']='EXPERIMENT: source non-living groups 45 Detritus and 46 Fishery discards combined. Single-pool recycling is a computational assumption; the distinct fishery-return pathway is lost.'
derived['_experiment']={'id':MID,'parent':SRC.name,'authorization':'User allowed merging all detritus groups after online routing search found no recoverable numerical split.','only_ecological_edit':'Merge groups 45 and 46; sum B and prey fractions; pooled EE unknown, never averaged.','selection_status':'UNSELECTED_EXPERIMENT','source_parameter_repairs':False}
dump(OUT/'model.json',derived);shutil.copy2(OUT/'model.json',OUT/(MID+'.json'));dump(EV/'diet_conservation.json',rows)
changes=[]
for old,new in zip(src[:45],groups):
    for k in old:
        if old[k]!=new[k]:changes.append({'group_seq':new['group_seq'],'field':k,'source':old[k],'experiment':new[k]})
changes.append({'group_seq':'46','field':'group','source':src[45],'experiment':'Merged into group 45'})
dump(EV/'changes_only_audit.json',changes)

# Separate experiment import set, preserving original 46-group extraction unchanged.
ex=json.loads((SRC/'source_review/FINAL_EXTRACTION.json').read_text(encoding='utf-8'));ex=copy.deepcopy(ex)
ex['metadata'].update(model_number=20190101,model_name='Warm Pool Detritus Pooled Experiment')
ex['groups']=ex['groups'][:45];g=ex['groups'][44];g.update(name=pool['group_name'],biomass=pool['biomass'],ee=None,ba='0',taxon_descr=pool['taxon_descr'])
ex['diet']={new['group_seq']:{d['prey_seq']:d['proportion'] for d in new['diet_descr']['diet']} for new in groups[:42]}
ex['detritus_groups']=[pool['group_name']];ex['detritus_fate']={};ex['diet_rows']=45;ex['experiment']=derived['_experiment']
dump(EV/'EXPERIMENT_EXTRACTION.json',ex)
run('write_outputs.py',[EV/'EXPERIMENT_EXTRACTION.json','--outdir',OUT,'--dir-name','extracted_tables'],TABLES/'WRITE_OUTPUTS.txt')
import openpyxl
wb=openpyxl.Workbook();ws=wb.active;ws.title='Taxonomy';ws.append(['seq','group_name','taxon_descr'])
for g in groups:ws.append([int(g['group_seq']),g['group_name'],g['taxon_descr']])
wb.save(TABLES/'Taxonomy.xlsx')
run('validate.py',[TABLES],TABLES/'VALIDATION.txt');run('massbalance_check.py',[TABLES],TABLES/'MASS_BALANCE.txt')
run('database_json.py',['-d',TABLES],TABLES/'DATABASE_CONVERSION.txt')
run('database_json.py',['-j',OUT/(MID+'.json')],TABLES/'CANONICAL_RECONSTRUCTION.txt')
recon=OUT/(MID+'_reconstructed.xlsx')
if recon.exists():shutil.move(str(recon),str(TABLES/'CANONICAL_reconstructed.xlsx'))

CODE=DIAG/'executed_code';CODE.mkdir(exist_ok=True)
for n in ['ModelData.py','PPRCalculator.py','utils.py']:shutil.copy2(ROOT/'tools/scientific_code/PPREstimation'/n,CODE/n)
shutil.copy2(__file__,CODE/Path(__file__).name);sys.path.insert(0,str(CODE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
settings=dict(underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=True,weight_flow=1.,weight_guess=1.,DC_tol=.001,normalize_DC=True)
outcomes={};load={};results={}
with (DIAG/'execution.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    try:
        data=ModelData(str(OUT/(MID+'.json')))
        data.groups_data.loc[data.groups_data['trophic_info']!='Import','net_migration']=0.0
        data.groups_data.to_csv(DIAG/'modeldata_groups_before_defaults.csv');data.DC.to_csv(DIAG/'loaded_diet.csv');data.det_fate.to_csv(DIAG/'loaded_detritus_fate.csv')
        calc=PPRCalculator.from_modeldata(data,**settings);load={'status':'LOADED','settings':settings}
        for attr in ['_groups_df','_DC','_det_fate']:
            obj=getattr(calc,attr,None)
            if hasattr(obj,'to_csv'):obj.to_csv(DIAG/(attr+'_after_completion.csv'))
        for option in ['GE','TE','With Egestion']:
            try:
                result=calc.diagnose_sppr(TE_option=option,short=False,flat=False)
                dump(DIAG/('diagnose_'+option.replace(' ','_')+'.json'),result);results[option]=result
                outcomes[option]={'call_status':'RETURNED','return_file':'diagnose_'+option.replace(' ','_')+'.json'}
            except Exception as e:
                outcomes[option]={'call_status':'RAISED','exception_type':type(e).__name__,'message':str(e)};traceback.print_exc()
    except Exception as e:
        load={'status':'BLOCKED','exception_type':type(e).__name__,'message':str(e),'settings':settings};traceback.print_exc()
        outcomes={o:{'call_status':'NOT_RUN_LOADER_BLOCKED'} for o in ['GE','TE','With Egestion']}
dump(DIAG/'LOAD_STATUS.json',load);dump(DIAG/'CALL_OUTCOMES.json',outcomes)
dump(DIAG/'DIRECT_DIAGNOSTICS.json',results)
dump(DIAG/'RUN_PROVENANCE.json',{'source_sha256':expected,'experiment_sha256':sha(OUT/'model.json'),'code_sha256':{p.name:sha(p) for p in CODE.glob('*.py')},'calls':[{'TE_option':o,'short':False,'flat':False} for o in ['GE','TE','With Egestion']],'global_excluded':True,'settings':settings})
assert sha(SRC/'model.json')==expected
dump(EV/'DERIVATION_CHECKS.json',{'source_unchanged':True,'source_sha256':expected,'living_scalar_parameters_catch_taxonomy_unchanged':True,'phytoplankton_exactly_unchanged':True,'all_42_consumer_diet_sums_exactly_conserved':True,'only_detritus_prey_rows_aggregated':True,'pooled_B':pool['biomass'],'pooled_EE':'unknown; no average','diet_normalized':False,'source_balance_repairs':False,'selected':False})
print(json.dumps({'model':MID,'load':load,'outcomes':outcomes},indent=2))
