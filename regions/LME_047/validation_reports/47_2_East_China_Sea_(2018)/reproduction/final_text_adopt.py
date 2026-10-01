from pathlib import Path
import json,sys,copy,math
ROOT=Path.cwd();Q=Path(__file__).parent;R=ROOT/'regions/LME_047';MID='47_2_East_China_Sea_(2018)';O=R/'validation_reports'/MID
sys.path.insert(0,str(ROOT/'tools'));from workbooks import *
from regional import result_hash,set_result_hash,set_setting
b=read_book(R/'LME_047.xlsx');before=copy.deepcopy(b);base=json.loads((Q/'current_book.json').read_text(encoding='utf-8'));ch=json.loads((O/'mapping_changes.json').read_text(encoding='utf-8'));h=b['PPR']['Matching'][0];oldnumeric={tuple(r[:3]):r[3]for r in b['PPR']['Matching'][1]};new=[[rr.get(k)for k in h]for c in ch for rr in c['new']];assert set(oldnumeric)=={tuple(r[:3])for r in new};assert all(math.isclose(oldnumeric[tuple(r[:3])],r[3],rel_tol=2e-14,abs_tol=1e-15)for r in new);b['PPR']['Matching']=(h,new)
b['Classic PPR']['Annual']=tuple(base['Classic PPR']['Annual'])
rh,rr=b['PPR–NPP']['Ratios'];simplebase={tuple(r[:6]):r for r in base['PPR–NPP']['Ratios'][1]if r[2]=='simple trophic chain'};rr=[simplebase.get(tuple(r[:6]),r)for r in rr];b['PPR–NPP']['Ratios']=(rh,rr)
set_setting(b,'calculation_input_sha256',input_hash(b));set_result_hash(b);write_book(R/'LME_047.xlsx',b)
b=read_book(R/'LME_047.xlsx');validate_region(b,R/'LME_047.xlsx',require_fresh=True);assert result_hash(b)==overview(b)['calculation_result_sha256']
assert b['Classic PPR']['Annual'][1]==base['Classic PPR']['Annual'][1]
for t in ['Annual','Taxon SPPR','Taxon PPR inspected year']:assert b['PPR'][t]==before['PPR'][t]
proof={'final_workbook_sha256':sha(R/'LME_047.xlsx'),'final_input_hash':input_hash(b),'final_result_hash':result_hash(b),'numeric_mapping_identity_preserved':True,'model_Annual_TaxonSPPR_detail_exactly_preserved':True,'Classic_Annual_entire_table_restored_exactly_to_accepted_baseline':True,'classic_ratio_rows_preserved_exactly':True,'reason':'Final native-source wording corrections only; original classic benchmark and bounds retained byte-for-value. Previous independent full arithmetic remains applicable.'}
(O/'final_text_adoption_verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print('FINAL TEXT',sha(R/'LME_047.xlsx'),result_hash(b))
