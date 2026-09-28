"""Record user's exact selection, preserve prior state, retain scientific pending gates."""
from pathlib import Path
import sys,json,hashlib,shutil
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_049';MID='49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)';DEST=REG/'models'/MID;EV=DEST/'evidence';PATH=REG/'LME_049.xlsx'
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,write_book,overview,sha,validate_region,input_hash
from regional import set_setting,set_result_hash
from run_region import prepare_selection
b=read_book(PATH);before=overview(b);backup=EV/('LME_049_before_user_selection_'+sha(PATH)[:12]+'.xlsx')
if backup.exists():raise RuntimeError('Selection backup already exists; inspect state instead of rerunning')
shutil.copy2(PATH,backup)
# Empty omitted sheets need their contract blocks before supported preparation.
b.setdefault('Selected model groups',{'Groups':(['group_seq','group_name'],[]),'Group SPPR':(['model_id','group','scope','method','sppr'],[])})
b.setdefault('Diagnostics',{})
set_setting(b,'selected_model_id',MID);set_setting(b,'model_path',f'models/{MID}/model.json')
set_setting(b,'selection_rationale','USER SELECTED 2026-09-28: exact detritus-only39-group Watari2013 experiment, because source routing among3detritus pools is unavailable. Retains35consumers and3regional phytoplankton; B_DET=44.12t/km2(total area), diets aggregate only source39–41. Adopted assumption variant: shared detritus mixing/full internal retention is not source-observed. Selection is not numerical/scientific clearance. GE/Egestion threshold-health OK but strict SPPR balance false; TE FAIL. Missing/censored inputs, seabird loader B=1/PB=QB=0, diet normalization, GS/default completion and solved BA remain material. User requests deferred investigation of TE failure; no repair authorized. See model/evidence/DECISIONS_AND_LIMITATIONS.md.')
prepare_selection(b,PATH)
set_setting(b,'selected_paper_ids','KUR-2019');set_setting(b,'production_eligible',False)
set_setting(b,'calculation_status','selected adopted assumption variant; diagnostics retained; mapping and model annual PPR blocked by unresolved scientific admission; TE investigation deferred by user')
set_setting(b,'source_note',f'Organized decisions: models/{MID}/evidence/DECISIONS_AND_LIMITATIONS.md. Full diagnostic report: models/extraction_review_20260928/EXTRACTION_AND_SPPR_REPORT.md. Original41-group source unchanged. Shared-pool routing is assumed, not measured.')
set_setting(b,'deferred_TE_investigation','USER REQUEST 2026-09-28: investigate why TE failed later. Observed4negative basal-source coefficients in seabird3 (catch defaulted0),2near-singular TE cases,MC_TE0/100 accepted and100diverged despite rho_living<1. Cause unresolved; no repair or sensitivity performed.')
# Reuse unchanged diagnostics as evidence, not selected production Group SPPR.
candidate=read_book(DEST/'candidate_diagnostics.xlsx')
for name,value in candidate.get('Diagnostics',{}).items():b['Diagnostics'][name]=value
b['Diagnostics']['Scientific admission']=(['item','status','evidence','interpretation'],[
 ['selection','USER SELECTED',MID,'Exact adopted assumption variant; numerical clearance remains separate'],
 ['source admission','BLOCKED','evidence/loader_audit_summary.json','Censored inputs and substantial loader completion unresolved'],
 ['GE / With Egestion','CONDITIONAL HEALTH OK','sppr_source.xlsx','Strict balance false; cannot establish source-valid production coefficients'],
 ['TE','FAIL; INVESTIGATE LATER','all_basal_source_coefficients.csv','4negative coefficients for unfished/defaulted seabird3;2near-singular cases;100/100MC diverged; cause unresolved'],
 ['downstream mapping / annual PPR','PENDING SCIENTIFIC ADMISSION','DECISIONS_AND_LIMITATIONS.md','No unsupported mappings or annual results generated'],
 ['diagnostic reuse','EXACT CANONICAL HASH VERIFIED',sha(DEST/'model.json'),'Retained unselected experimental run:100MCdraws/method,180s/method; no new stochastic realization']])
set_setting(b,'calculation_input_sha256',input_hash(b));set_result_hash(b)
write_book(PATH,b);fresh=read_book(PATH);validate_region(fresh,PATH)
old=read_book(backup)
for s in ['Catch','Classic PPR','NPP']:assert fresh[s]==old[s],s
assert not fresh['PPR']['Annual'][1];assert not fresh['PPR']['Matching'][1]
assert overview(fresh)['selected_model_id']==MID
assert sha(DEST/'model.json')=='ce1c22a1e20e2a5de8a8ac75e6ddb00c3f0db619849354df9f1527277e36d15c'
result={'date':'2026-09-28','before_overview':before,'after_overview':overview(fresh),'backup_path':str(backup.relative_to(ROOT)),'backup_sha256':sha(backup),'regional_workbook_sha256':sha(PATH),'model_sha256':sha(DEST/'model.json'),'checks':{'validate_region_passed':True,'Catch_ClassicPPR_NPP_all_blocks_unchanged':True,'stale_model_results_cleared':True,'model_matching_and_annual_outputs_not_created':True,'Project_xlsx_not_written':True,'selected_is_not_scientific_clearance':True}}
(EV/'selection_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
