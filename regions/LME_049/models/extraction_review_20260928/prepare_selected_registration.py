from pathlib import Path
import json,sys
root=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());out=Path(__file__).parent
mid='49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)';d=root/'regions/LME_049/models'/mid
p=json.loads((d/'metadata_registration_proposal.json').read_text(encoding='utf-8'));note=p['paper_updates'][0]['append_notes']
diag='regions/LME_049/models/extraction_review_20260928/SPPR_DIAGNOSTICS_REPORT.md';dec='regions/LME_049/models/'+mid+'/evidence/DECISIONS_AND_LIMITATIONS.md'
p['paper_updates']=[{'article_id':'KUR-2019__LME_049','changes':{'notes':note+' Current SPPR diagnostic report (GE, TE, With Egestion only): '+diag+' Exact source-membership preparation:7/253taxa,20.6518%2019totalcatch;246unresolved. Annual model PPR pending, not zero.','documentation_evidence':dec+'; '+diag,'recommendation':'USER SELECTED derived39-group detritus-only assumption variant '+mid+'. Shared routing/full retention assumed because source routing missing; GE/Egestion conditional estimates, TEFAIL. User requests deferred TE investigation; cause unresolved. Source41-group remains separate.'}}]
p['model_rows_to_register'][0]['model_path']=p['model_rows_to_register'][0]['model_path'].replace('\\','/')
p['model_rows_to_register'][0]['availability']+=' Direct diagnose_sppr report: '+diag+'; membership preparation7/253taxa (20.6518%2019catch), not accepted fullmapping.'
(out/'selected_registration_proposal.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
s=(out/'register_central_metadata.py').read_text(encoding='utf-8')
s=s.replace('central_metadata_proposal.json','selected_registration_proposal.json').replace('CENTRAL_REGISTRATION_VERIFICATION.json','SELECTED_REGISTRATION_VERIFICATION.json').replace('Project_before_LME049_registration_','Project_before_LME049_selected_registration_')
(out/'register_selected_metadata.py').write_text(s,encoding='utf-8')
s=(root/'regions/LME_038/models/extraction_review_20260928/consolidate_selected_region.py').read_text(encoding='utf-8')
s=s.replace('LME_038','LME_049').replace('LME038','LME049').replace('38_38003_Java_Sea_normalized_BA_completed_(mid1970s)',mid).replace("region['production_eligible'] is True","region['production_eligible'] is False").replace("region['atlas_region_rank']==13","region['atlas_region_rank']==12")
(out/'consolidate_selected_region.py').write_text(s,encoding='utf-8')
sys.path.insert(0,str(root/'tools'));from workbooks import read_book,write_book,validate_region
path=root/'regions/LME_049/LME_049.xlsx';b=read_book(path)
b['Diagnostics']['Selection and next steps']=(['item','status','evidence'],[['Exact selected variant','USER SELECTED; annual model PPR pending',mid],['Decisions and limitations','Documented authorized pooling and incidental loader transformations',dec],['SPPR report','Direct diagnose_sppr:GE OK;TEFAIL;With Egestion OK',diag],['TE investigation','USER REQUESTED DEFERRED; cause unresolved','4negative seabird basal-source coefficients;2near-singular TE cases;0/100MC_TE accepted; no repair authorized'],['Independent membership preparation','7exact of253taxa;246unresolved;20.6518%2019totalcatch','models/'+mid+'/evidence/matching_preparation_summary.json']])
write_book(path,b);validate_region(read_book(path),path)
assert (root/diag).is_file() and (root/dec).is_file()
print('Registration and updater prepared; regional links validated')
