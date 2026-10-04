"""Freeze portable inventory after all browser and workbook checks succeed."""
from pathlib import Path
import json,hashlib,os
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=BASE.parents[3];REGION=ROOT/'regions/LME_013'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((OUT/'run_manifest.json').read_text(encoding='utf-8'))
assert sha(OUT/'run_direct_auto.py')==manifest['script_sha256']
calc=json.loads((OUT/'candidate_calculation_manifest.json').read_text(encoding='utf-8'))
assert sha(OUT/'calculate_auto.py')==calc['script_sha256']
verification=json.loads((OUT/'qa/integration_verification.json').read_text(encoding='utf-8'))
assert verification['project_sha256']==sha(ROOT/'Project.xlsx')
assert verification['map_sha256']==sha(ROOT/'interactive_map/index.html')
browser=json.loads((OUT/'qa/browser_verification.json').read_text(encoding='utf-8'))
assert browser['passed'] and browser['model_id']==BASE.name
assert browser['project_sha256']==sha(ROOT/'Project.xlsx')
assert browser['persistence']['reload_retained']
artifacts=[]
def add(role,p):
    assert p.is_file(),p
    artifacts.append({'role':role,'availability':'present','path':Path(os.path.relpath(p,OUT)).as_posix(),'sha256':sha(p)})
for role,p in [('canonical_source',BASE/'source/resolved_native/model.json'),('computational_input',BASE/'source/computational/model.json'),('mapping',BASE/'mapping/mapping_review.json'),('never_settings',BASE/'diagnostics/run_manifest.json'),('settings',OUT/'run_manifest.json'),('comparison',OUT/'never_vs_auto_comparison.json'),('preflight',OUT/'preflight_result.json'),('full_diagnostic_review',OUT/'full_direct_report.json'),('executed_code',OUT/'executed_code/run_direct_auto.py'),('arithmetic_code',OUT/'calculate_auto.py'),('taxon_coefficients',OUT/'taxon_scope_coefficients.json'),('group_coefficients',OUT/'group_scope_coefficients.csv'),('annual_ppr',OUT/'candidate_annual_totals.csv'),('annual_ratios',OUT/'candidate_annual_npp_ratios.csv'),('taxon_annual',OUT/'candidate_taxon_annual.csv.gz'),('regional_workbook',REGION/'LME_013.xlsx'),('project_workbook',ROOT/'Project.xlsx'),('map',ROOT/'interactive_map/index.html'),('trends',ROOT/'interactive_map/trends.html'),('validation_document',REGION/'Model_validation_HUM2018_Northern_Humboldt_candidate_20261003.docx'),('appendix',REGION/'LME013_HUM2018_candidate_taxon_mapping_appendix_20261003.xlsx'),('rendered_validation',OUT/'qa/selected_auto_validation.pdf'),('document_checks',OUT/'qa/review_artifact_verification.json'),('integration_checks',OUT/'qa/integration_verification.json'),('browser_checks',OUT/'qa/browser_verification.json')]:add(role,p)
for method in ['GE','TE','With_Egestion']:
    for name in ['diagnostic_return.json','full_return_lossless.json','full_return.pkl','detritus_resolution_info_lossless.json','runtime_before_exact.json','runtime_after_exact.json']:
        add(method+'/'+name,OUT/method/name)
    for matrix in ['SPPR','A','L']:
        for suffix in ['.csv','.npy','_axes.json','_masks.npz']:add(method+'/'+matrix+suffix,OUT/method/(matrix+suffix))
for i in range(1,8):add('Word_page_'+str(i),OUT/f'qa/page-{i}.png')
for name in ['browser_observations.json','browser_current_snapshot.json','browser_persistence.json','browser_current_GE.jpg']:
    add('browser_evidence/'+name,OUT/'qa'/name)
for name in ['integrate_active.py','verify_integration.py','verify_browser.py','finalize_handoff.py']:
    add('integration_code/'+name,OUT/name)
for name in ['build_html.py','original_atlas_data.py','researcher_review.js','update_project.py']:
    add('project_code/'+name,ROOT/'tools'/name)
add('selected_package_readme',BASE/'README.md')
add('regional_directory_guide',REGION/'README.md')
index={'schema_version':1,'run_id':manifest['run_id'],'region_id':'LME_013','model_id':BASE.name,'variant_id':'audited computational input; auto; provisional selection',
       'source_identity':{'path':'../source/resolved_native/model.json','sha256':sha(BASE/'source/resolved_native/model.json')},
       'computational_input_identity':{'path':manifest['input_path'],'sha256':manifest['input_sha256']},
       'methods':['GE','TE','With Egestion'],'required_roles':list(dict.fromkeys(a['role'] for a in artifacts)),
       'artifacts':artifacts,'reconciliation':{'all_direct_entries_inspected':True,'controlled_comparison':True,'coefficients_and_annual_cells':True,'portable_document_links_and_independent_denominator':True,'seven_Word_pages_inspected':True,'browser_and_saved_data':True},
       'scientific_limit':'All methods overall FAIL; production-ineligible; no researcher verdict. Inventory completeness is not scientific validation.'}
(OUT/'evidence_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
print('Portable evidence index saved with '+str(len(artifacts))+' hashed artifacts.',flush=True)
