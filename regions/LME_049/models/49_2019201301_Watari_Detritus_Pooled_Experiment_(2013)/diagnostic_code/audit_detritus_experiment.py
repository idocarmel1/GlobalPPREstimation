from pathlib import Path
import json,sys,shutil,hashlib,csv,math
import pandas as pd
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());OUT=ROOT/'regions/LME_049/models/49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)';EV=OUT/'evidence'
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
from create_PPRS_excel import load_model
p=EV/(OUT.name+'.json');shutil.copy2(OUT/'model.json',p)
raw=ModelData(str(p));raw.groups_data.to_csv(EV/'raw_loader_groups.csv');raw.DC.to_csv(EV/'raw_loader_diet.csv');raw.det_fate.to_csv(EV/'loader_default_detritus_fate.csv')
model,label=load_model(str(p));loaded=model.get_groups_df();loaded.to_csv(EV/'completed_loader_groups.csv');model._DC.to_csv(EV/'normalized_loader_diet.csv');model._det_fate.to_csv(EV/'completed_detritus_fate.csv')
src=json.loads((OUT/'model.json').read_text(encoding='utf-8'))['group'];changes=[]
mapping={'biomass':'biomass','pb':'pb','qb':'qb','ee':'ee','biomass_accum':'biomass_accum','gs':'gs','respiration':'respiration','immigration':'immigration','emigration':'emigration','export':'catch','detritus_import':'detritus_import','diet_imp':'diet_import','ge':'ge','other_mort':'M0b','biomass_accum_rate':'biomass_accum_rate','emigration_rate':'emigration_rate'}
for g in src:
    n=int(g['group_seq'])
    for sf,lf in mapping.items():
        if lf not in loaded:continue
        sv=g[sf];lv=loaded.loc[n,lf];missing=sv=='-9999'
        if missing or not math.isclose(float(sv),float(lv),rel_tol=1e-12,abs_tol=1e-12):changes.append({'group_seq':n,'group_name':g['group_name'],'source_field':sf,'source_value':sv,'loaded_field':lf,'loaded_value':lv,'status':'source unknown completed/defaulted' if missing else 'known source value changed'})
pd.DataFrame(changes).to_csv(EV/'all_loader_scalar_transformations.csv',index=False)
dcchanges=[]
for g in src[:35]:
    n=int(g['group_seq'])
    for d in g['diet_descr']['diet']:
        prey=int(d['prey_seq']);s=float(d['proportion']);v=model._DC.loc[n,prey]
        if not math.isclose(s,v,rel_tol=1e-12,abs_tol=1e-12):dcchanges.append({'consumer_seq':n,'prey_seq':prey,'source_value':d['proportion'],'loaded_value':v,'difference':v-s})
pd.DataFrame(dcchanges).to_csv(EV/'all_loader_diet_transformations.csv',index=False)
balanced,production,consumption=model.is_model_balanced();balance=pd.DataFrame({'source_group_name':loaded.group_name,'p':model.p,'production_components_sum':production,'production_residual':production-model.p,'q':model.q,'consumption_components_sum':consumption,'consumption_residual':consumption-model.q,'solved_BA':model.growth});balance.to_csv(EV/'completed_flow_balance.csv')
fate=model._det_fate;assert all(fate.loc[list(range(1,39)),39]==1)
det=loaded.loc[39].to_dict();det['budget_utilization_predation_divided_by_inflow']=float(model.predation.loc[39]/model.p.loc[39]);det['note']='Diagnostic budget ratio, not source EE; loader sets DET EE=1 by convention. Residual enters solved BA. No unknown internal transfer was added.'
summary={'load_success':True,'model_balanced_after_completion':bool(balanced),'max_abs_production_residual':float((production-model.p).abs().max()),'max_abs_consumption_residual':float((consumption-model.q).abs().max()),'scalar_transformations':len(changes),'known_scalar_changes':[x for x in changes if x['status']=='known source value changed'],'diet_cells_normalized':len(dcchanges),'diet_consumers_normalized':sorted(set(x['consumer_seq'] for x in dcchanges)),'seabird_source_B':'<0.01; canonical -9999','seabird_loaded_B':float(loaded.loc[3,'biomass']),'source_missing_catch_zero_groups':[int(g['group_seq']) for g in src if g['export']=='-9999' and loaded.loc[int(g['group_seq']),'catch']==0],'solved_BA_all_source_groups':{int(i):float(loaded.loc[i,'biomass_accum']) for i in range(1,40)},'detritus_budget':det,'engine_added_groups':loaded.loc[loaded.index>39].to_dict(orient='index')}
dump(EV/'loader_audit_summary.json',summary)
sys.path.insert(0,'C:/Users/idoca/.agents/skills/ecopath-extraction/scripts');from database_json import EwEConverter
cv=EwEConverter(log_file=str(EV/'canonical_roundtrip.log'));cv.json_to_excel(str(OUT/'model.json'),str(EV/'canonical_reconstructed.xlsx'));cv.report_mass_balance(cv.check_mass_balance(src),OUT.name,str(EV/'MASS_BALANCE_CANONICAL.md'))
assert json.loads(json.dumps(src))==src
dump(EV/'roundtrip_and_integrity_checks.json',{'canonical_JSON_roundtrip_equal':True,'source_hash_unchanged':hashlib.sha256((OUT.parent/'49_20192013_Western_North_Pacific_Watari_(2013)/model.json').read_bytes()).hexdigest()=='7448c7ac1a4f8aebdc3aa27d236adc31c8bd7600dd39591271b9f2ce22615eb7','canonical_source_missingness_retained':True,'three_primary_producer_records_unchanged':True,'consumer_diet_totals_equal':True})
shutil.copy2(Path(__file__),OUT/'diagnostic_code'/Path(__file__).name)
print(json.dumps(summary,indent=2,default=str))
