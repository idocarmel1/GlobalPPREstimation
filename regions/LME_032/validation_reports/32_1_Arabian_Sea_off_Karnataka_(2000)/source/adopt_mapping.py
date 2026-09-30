from pathlib import Path
import sys,json,csv,math
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import set_setting
R=Path(__file__).resolve().parent.parent
path=ROOT/'regions/LME_032/LME_032.xlsx';b=read_book(path);o=overview(b)
audit=json.loads((R/'mapping/adopted_taxon_audit.json').read_text(encoding='utf-8'))
assert o['selected_model_id']=='32_1_Arabian_Sea_off_Karnataka_(2000)'
matching=[]
for x in audit:
 for g in x['groups']:matching.append([o['selected_model_id'],x['taxon'],g['group'],g['weight'],x['overall_confidence'].lower(),x['membership_rule']+'; '+x['allocation_rule'],x['reason']])
b['PPR']['Matching']=(['model_id','taxon','group','weight','confidence','evidence','explanation'],matching)
review=[]
for x in audit:review.append({'model_id':o['selected_model_id'],'taxon':x['taxon'],'membership_rule':x['membership_rule'],'membership_confidence':x['membership_confidence'],'allocation_rule':x['allocation_rule'],'allocation_confidence':x['allocation_confidence'],'confidence':x['overall_confidence'],'stored_confidence':x['previous_confidence'],'accepted_name':x['accepted_name'],'membership_reason':x['membership_reason'],'allocation_reason':x['allocation_reason'],'evidence_path':'validation_reports/'+o['selected_model_id']+'/mapping/adopted_taxon_audit.json','review_date':'2026-09-30'})
b['PPR']['Mapping review']=table_dict(review)
alloc=json.loads((R/'mapping/allocation_evidence.json').read_text(encoding='utf-8'))
b['PPR']['Allocation assumptions']=table_dict([{'model_id':o['selected_model_id'],**x} for x in alloc])
b['Diagnostics']['Source reconstruction review']=table_dict([{'model_id':o['selected_model_id'],'source_year':2008,'source_model_period':'1999–2001','audit_date':'2026-09-30','basic_parameters':'93 published cells agree','landings':'24 total landings agree','diet':'528 balanced-diet cells agree after actual column-sum normalization','biomass_accumulation':'Adopted source-stated zero for all24 groups; formerly missing and solved as residual','GS':'Unreported; runtime default0.2 for regular consumers; basal0','input_status':'WARN: source-rounded model remains unbalanced; no repair invented','evidence_path':'validation_reports/'+o['selected_model_id']+'/source/source_table_reconciliation.json'}])
set_setting(b,'source_note','Karnataka 1999–2001 shelf model transferred to Arabian Sea catch. Source-stated zero BA adopted; GE/TE/With Egestion retain balance warnings. Taxon mappings reassessed 2026-09-30; Very low assumptions explicit.')
write_book(path,b)
print('Adopted',len(audit),'taxon decisions;',len(matching),'taxon/group rows;',len(alloc),'allocation candidate rows')
