"""User-approved, detritus-only experimental derivation; never edits its parent."""
from pathlib import Path
from decimal import Decimal as D
import json,copy,hashlib,shutil,sys,csv
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
REG=ROOT/'regions/LME_049';SRC=REG/'models/49_20192013_Western_North_Pacific_Watari_(2013)'
MID='49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)';OUT=REG/'models'/MID
OUT.mkdir(exist_ok=True);EV=OUT/'evidence';EV.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def csvout(p,rows):
    with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f).writerows(rows)
assert sha(SRC/'model.json')=='7448c7ac1a4f8aebdc3aa27d236adc31c8bd7600dd39591271b9f2ce22615eb7'
src=json.loads((SRC/'model.json').read_text(encoding='utf-8'));g=src['group'];assert len(g)==41
assert [x['pp'] for x in g]==['0']*35+['1']*3+['2']*3
assert [x['biomass'] for x in g[38:]]==['9.58','6.04','28.50']
shutil.copy2(SRC/'model.json',EV/'source_model_frozen.json')
shutil.copy2(SRC/'source_manifest.json',EV/'source_publication_manifest.json')
shutil.copy2(SRC/'extracted_tables/censored_values.json',EV/'source_censored_values.json')
derived=copy.deepcopy(src);derived['group']=derived['group'][:39];dg=derived['group'];aggregations=[];totals=[]
for old,new in zip(g[:35],dg[:35]):
    items=old['diet_descr']['diet'];assert len(items)==41
    pool=[x for x in items if int(x['prey_seq'])>=39]
    assert all(x['detritus_fate']=='-9999' for x in items)
    amount=sum(D(x['proportion']) for x in pool)
    new['diet_descr']['diet']=copy.deepcopy(items[:38])+[{'prey_seq':'39','proportion':str(amount),'detritus_fate':'-9999'}]
    before=sum(D(x['proportion']) for x in items);after=sum(D(x['proportion']) for x in new['diet_descr']['diet']);assert before==after
    assert {k:v for k,v in old.items() if k!='diet_descr'}=={k:v for k,v in new.items() if k!='diet_descr'}
    assert new['diet_descr']['diet'][:38]==items[:38]
    aggregations.append([old['group_seq'],old['group_name'],*[x['proportion'] for x in pool],str(amount)])
    totals.append([old['group_seq'],old['group_name'],str(before),str(after)])
assert dg[35:38]==g[35:38]
det=dg[38];det['group_name']='Detritus (pooled OYC KC OF; experiment)'
det['biomass']=str(sum(D(x['biomass']) for x in g[38:]))
# Habitat=1 defines the new whole-domain pool; published habitat biomasses are NOT summed.
det['habitat_area']='1.00';det['biomass_habitat_area']=det['biomass']
det['taxon_descr']={'taxon':[{'taxon_name':'EXPERIMENT: shared OYC/KC/OF detritus pool; derived from source groups 39, 40, 41. Whole-model-area biomass sum; recycling routing is an explicit loader assumption, not published evidence.'}]}
assert det['biomass']=='44.12';assert det['ee']=='-9999';assert det['diet_descr'] is None
dump(OUT/'model.json',derived)
changes=[]
for old,new in zip(g[:39],dg):
    for field in old:
        if old[field]!=new[field]:changes.append({'group_seq':new['group_seq'],'field':field,'before':old[field],'after':new[field]})
changes.extend({'group_seq':x['group_seq'],'field':'group','before':x,'after':'merged into group 39'} for x in g[39:])
dump(EV/'changes_only_audit.json',changes)
csvout(EV/'original_to_derived_group_map.csv',[['source_seq','source_name','derived_seq','derived_name'],*[[x['group_seq'],x['group_name'],str(min(int(x['group_seq']),39)),dg[min(int(x['group_seq']),39)-1]['group_name']] for x in g]])
csvout(EV/'detritus_diet_aggregation.csv',[['consumer_seq','consumer_name','original_39','original_40','original_41','derived_39'],*aggregations])
csvout(EV/'consumer_diet_totals.csv',[['consumer_seq','consumer_name','source_total','derived_total'],*totals])
manifest={'parent_model_id':SRC.name,'experimental_model_id':MID,'source_model_sha256':sha(SRC/'model.json'),'derived_model_sha256':sha(OUT/'model.json'),'production_workbook_before_sha256':sha(REG/'LME_049.xlsx'),'publication_sources':json.loads((SRC/'source_manifest.json').read_text()),'source_area_km2':913102,'biomass_units':'t/km2 total model area','biomass_derivation':'9.58 + 6.04 + 28.50 = 44.12; no second habitat scaling','derived_pool_habitat':'1.00 defines whole-domain pooled representation; B_habitat=44.12 is derived, not printed','assumptions':['All living mortality and egestion routed to sole detritus pool by existing single-pool loader default.','Full retention and cross-block mixing of recycling; actual external losses and original three-pool routing unknown.','No detritus EE average. Unknown EE retained.','Unknown internal detritus transfers not invented or duplicated; original detritus diet rows absent.','Canonical diets are not normalized; censored seabird B and catch remain unknown with original bounds in sidecar.'],'checks':{'all_35_consumer_scalar_parameters_catches_unchanged':True,'all_3_phytoplankton_groups_exactly_unchanged':True,'all_consumer_diet_totals_exactly_unchanged':True,'only_three_detritus_prey_rows_aggregated':True,'unknown_fates_preserved':True,'no_added_catch_or_import':True,'n_groups':39,'detritus_B_sum':'44.12'}}
dump(EV/'derivation_manifest.json',manifest)
sys.path.insert(0,str(ROOT/'tools'));from workbooks import read_book,write_book
b=read_book(REG/'LME_049.xlsx');b={s:{n:(h,[]) for n,(h,rs) in ts.items()} for s,ts in b.items()}
b['Overview']['Settings']=(['field','value'],[['unit_id','LME_049'],['region_name','Kuroshio Current'],['selected_model_id',MID],['model_path','model.json'],['selection_rationale','ISOLATED USER-APPROVED DETRITUS-ONLY EXPERIMENT; not production adoption. Shared detritus routing and loader-completed unknowns are assumptions.'],['production_eligible',False],['catch_basis','landings'],['taxon_detail_year',2019]])
write_book(OUT/'candidate_diagnostics.xlsx',b)
snap=OUT/'diagnostic_code';snap.mkdir(exist_ok=True)
for p in [Path(__file__),ROOT/'tools/run_region.py',ROOT/'tools/workbooks.py',ROOT/'tools/regional.py',ROOT/'tools/scientific_helpers/ppr_scopes.py']:
    shutil.copy2(p,snap/p.name)
eng=ROOT/'tools/scientific_code/PPREstimation'
for p in eng.rglob('*.py'):
    if '__pycache__' not in p.parts:
        out=snap/'PPREstimation'/p.relative_to(eng);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
dump(OUT/'diagnostic_code_hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in [OUT/'model.json',*snap.rglob('*.py')]})
dump(OUT/'diagnostic_settings.json',{'scope':'39-group unselected detritus-only experiment','mc_samples_per_method':100,'method_timeout_seconds':180,'random_seed':'wrapper provides no seed argument; not fixed','loader_options':{'underdetermined':True,'zero_biomass_accum':False,'zero_catch':True,'default_gs':True,'weight_flow':1.0,'weight_guess':1.0,'DC_tol':0.001,'normalize_DC':True},'production_eligible':False})
print(OUT)
