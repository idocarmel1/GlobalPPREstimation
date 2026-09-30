"""Package already independently checked evidence; does not run a calculator."""
from pathlib import Path
import json, hashlib, os, sys, math
from datetime import datetime, timezone

R=Path(__file__).resolve().parent.parent
ROOT=next(p for p in R.parents if (p/'Project.xlsx').exists())
region=R.parent.parent
model='32_1_Arabian_Sea_off_Karnataka_(2000)'
run_id='LME032_validation_20260930_zeroBA_mapping_v7'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:os.path.relpath(p,R).replace('\\','/')
put=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
shared=read(R/'qa/shared_integration.json')
assert shared['all_passed'] and shared['project_sha256']==sha(ROOT/'Project.xlsx')
assert shared['regional_workbook_sha256']==sha(region/'LME_032.xlsx')
checks=read(R/'qa/final_scientific_checks.json')
assert checks['all_passed']
native=read(R/'qa/native_excel_check.json')
assert native['native_open_succeeded'] and len(native['hyperlinks'])==22
assert math.isclose(native['simple_chain_ppr_tC'],shared['reference']['unrounded_ppr_tC'],rel_tol=1e-12)
observed={'simple trophic chain':514700000,'new_GE':259000000,'new_TE_EEfix':475600000,'new_WithEgestion':88190000}
annual={x['method']:x['ppr_tC_2019'] for x in shared['annual_2019']}
for method,display in observed.items():
    value=annual[method]
    magnitude=10**(math.floor(math.log10(abs(value)))-3)
    assert round(value/magnitude)*magnitude==display,(method,value,display)
browser={'run_id':run_id,'date':'2026-09-30','actual_browser':'Codex in-app browser; CUA DOM observations after final reload',
 'project_sha256_observed_in_DOM':shared['project_sha256'],
 'url':'http://127.0.0.1:8877/interactive_map/index.html',
 'controls':{'region':'LME_032','selected_model':model,'year':2019,'metric':'ppr','scope':'all','catch_basis':'landings','unidentified':'method','groups':'all'},
 'remembered_settings':'Reload preserved 2019/landings/method/all groups and the selected Karnataka model. Opening Arabian Sea displayed that same selected model in simple-chain mode.',
 'observed_ppr_tC':observed,'unrounded_ppr_tC':{m:annual[m] for m in observed},
 'coverage_visible':'100.00% of annual landings included (5,224,000 tonnes)',
 'source_metadata_visible':'2008; Reconstructed and executed; balance WARN; source-stated zero BA adopted;93 basic cells,24 landings totals and528 balanced-diet cells reconciled.',
 'warnings_visible_for_model_methods':'GE, TE and With Egestion WARN; strict input balance false and strict SPPR balance false.',
 'console_errors_or_warnings_observed':[], 'all_four_display_roundings_match':True}
put(R/'qa/browser_verification.json',browser)
put(R/'qa/global_html_verification.json',{'run_id':run_id,'project_sha256':shared['project_sha256'],
 'verifier':'tools/verify_html.py','executed_by':'Coordinated LME_034 integration chat',
 'independent_review':'Successful command output directly inspected in that chat, not inferred from a completion message.',
 'command_item_id':'exec-3ff8973f-7601-4015-942f-dbd450fd9e28','exit_code':0,
 'output':'Map/time-series layouts match the templates with file-link, basemap and provisional-display adapters; 2224320 annual cells and NPP match Project.xlsx; selected models, source files and archive page verified'})
put(R/'qa/visual_verification.json',{'run_id':run_id,'date':'2026-09-30',
 'docx_sha256':sha(region/f'Model_validation_{model}.docx'),
 'xlsx_sha256':sha(region/'LME032_taxon_mapping_appendix.xlsx'),
 'report':'All six rendered final pages visually inspected; context, diagnostics, coverage/rules, allocation, regional boundary and study figure readable without clipping.',
 'appendix':'All four tabs inspected using Artifact Tool range renders; top taxa, full reasons, zero-catch tail, coverage formulas, both rule tables, allocation candidates and Sources. Corrected Sources rows21–26 inspected after final export.',
 'docx_renderer':'Separate hidden Word instance ExportAsFixedFormat; bundled render_docx could not find LibreOffice.',
 'xlsx_native_check':'Separate hidden Excel instance opened the relocated final workbook read-only, recalculated totals and read22 hyperlinks.',
 'images':'Transient visual QA images are intentionally excluded from the permanent evidence inventory; retained scientific geographic figures remain linked.'})
put(R/'qa/workflow_stages.json',{'run_id':run_id,'scope':'Validation of the currently selected model using retained reconstruction and independently rechecked source evidence.',
 'stages':[
 {'stage':'source reconstruction','state':'performed','evidence':'source/source_table_reconciliation.json','detail':'93 basic parameter cells,24 landings totals and528 balanced diet cells; source-stated zero BA adopted for all24 original groups. Original JSON frozen before adoption.'},
 {'stage':'taxonomy and membership','state':'performed','evidence':'mapping/adopted_taxon_audit.json','detail':'All430 catch labels;517 taxon/source-name queries,475 exact WoRMS responses. Authority response and independent assumption flags retained.'},
 {'stage':'allocation','state':'performed','evidence':'mapping/allocation_evidence.json','detail':'Complete eligible landings candidates including zero; seven identified-lineage regional total-catch mixtures reconstructed; weakest-component confidence applied.'},
 {'stage':'group SPPR','state':'performed','evidence':'../../models/'+model+'/sppr_source.xlsx','detail':'Standard SPPR stage rerun for22 methods ×25 groups ×3 scopes. All20 deterministic methods agree with retained baseline within1e-9;134 stochastic result cells differ under newly sampled Monte Carlo draws.'},
 {'stage':'direct diagnostics','state':'performed','evidence':'diagnostics/adopted_summary.json','detail':'Full exact adopted-input GE/TE/With Egestion returns, matrices, coefficients and typed axes retained and reconciled. All WARN, no negative SPPR entries; no numerical repair adopted.'},
 {'stage':'regional PPR','state':'performed','evidence':'../../LME_032.xlsx','detail':'Dependent regional outputs recalculated; catch and classic taxon coefficients unchanged. Common classic annual rows agree to floating-point precision; historical sensitivity bounds invalidated by the standard pipeline.'},
 {'stage':'NPP ingestion','state':'reused','evidence':'baseline/snapshot.json','detail':'Existing annual NPP support retained and verified unchanged; mapping/BA findings did not affect independent NPP.'},
 {'stage':'Project/map/trends/archive','state':'performed','evidence':'qa/shared_integration.json','detail':'Project metadata and results integrated; shared final rebuild coordinated with LME_034. Independent32 payload/browser checks plus successful global verifier output retained.'},
 {'stage':'native EwE database import/round trip','state':'inapplicable','evidence':None,'detail':'Selected operational route is the existing JSON model reconstructed from published tables. Native EwE database functionality is not claimed as tested.'}
 ]})
readme="""# LME_032 validation evidence

This directory records the 30 September 2026 review of the selected Karnataka model. It authenticates review evidence; regional Overview and Project.xlsx remain the configuration and selection authorities.

The source-stated zero biomass accumulation was adopted for all 24 source groups. All 430 catch labels were reassessed under filling-guide version 7. The report reflects adopted regional mappings, not proposed changes. Forty Very low decisions account for 3.3265% of the independent 2019 landings simple-chain PPR. All three direct formulations retain balance WARN; the TE marine-mammal coefficient is near singular. Nonnegative coefficients do not establish model balance.

The published 27,000 km² footprint describes the Karnataka shelf and parts of slope. The geographic ranges are judgment-based approximations: A about 0.65–0.69% of the LME, B about 95–100% of the study. The coordinate rectangle is only a locator and containment check, not the study-area denominator.

* [Validation report](../../Model_validation_32_1_Arabian_Sea_off_Karnataka_(2000).docx)
* [Taxon appendix and descriptive sources](../../LME032_taxon_mapping_appendix.xlsx)
* [Keyed old/adopted taxon review](mapping/adopted_taxon_audit.json)
* [Allocation quantities, candidates and assumptions](mapping/allocation_evidence.json)
* [Ecological searches and material actually read](mapping/ecological_source_checks.json)
* [Source table reconciliation](source/source_table_reconciliation.json)
* [Adopted direct diagnostics](diagnostics/adopted_summary.json)
* [Run settings and code identities](diagnostics/adopted_provenance.json)
* [Workflow stage evidence](qa/workflow_stages.json)
* [Final regional arithmetic and adoption checks](qa/final_scientific_checks.json)
* [Classic annual comparison and invalidated bounds](qa/classic_annual_comparison.json)
* [Final Project/map/trend reconciliation](qa/shared_integration.json)
* [Visible browser verification](qa/browser_verification.json)
* [Portable evidence inventory](evidence_index.json)
* [Inventory completeness result](completeness.json)

The frozen baseline precedes the review. The source-table audit's baseline JSON is deliberately frozen; it must not be regenerated from adopted model inputs and presented as an original-input comparison. Catch, classic taxon coefficients and NPP were reused unchanged. Deterministic group coefficients did not change within the declared tolerance; adopted numerical mapping changes can change regional model-based PPR. The Monte Carlo stage generated new draws and is not claimed byte-identical. The current recalculation removes historical sensitivity bounds requiring reassessment; these were not copied back from old outputs.

Native EwE database import and native round-trip tests are inapplicable to this selected JSON route and are not claimed as performed. No author digital study polygon was available; its absence does not turn the coordinate envelope into measured coverage. Scientific limitations are distinct from inventory completeness.

All repository links resolve from their containing file. Final DOCX/XLSX local links were reopened after relocation and hash matched. Public URLs retain their public destinations; inaccessible pages and access modes are recorded separately. Temporary builders, render pages and runtime dependencies are excluded under work/.
"""
(R/'README.md').write_text(readme,encoding='utf-8')
report_index=f"""# LME_032 validation reports

Current selected model: `{model}`. Reviewed 30 September 2026 using the current model-validation skill, unified paper-to-PPR workflow and filling-guide version 7.

* [Validation DOCX](Model_validation_{model}.docx)
* [Linked taxon appendix](LME032_taxon_mapping_appendix.xlsx)
* [Evidence and scientific limitations](validation_reports/{model}/README.md)
* [Evidence inventory](validation_reports/{model}/evidence_index.json)
* [Completeness check](validation_reports/{model}/completeness.json)

These are adopted-data validation deliverables. GE, TE and With Egestion retain balance WARN; manual researcher rows are preserved. Overview and Project.xlsx remain selection/configuration authorities.
"""
(region/'reports_index.md').write_text(report_index,encoding='utf-8')
roles={
 'source/source_table_reconciliation.json':'source_reconciliation',
 'source/published_balanced_basic.csv':'published_basic_inputs',
 'source/published_landings.csv':'published_landings',
 'source/published_modified_diet_cells.csv':'published_balanced_diet',
 'baseline/model_original.json':'original_computational_input',
 'baseline/snapshot.json':'original_catch_coefficients_npp_snapshot',
 'baseline/LME_032.xlsx':'original_regional_workbook',
 'baseline/sppr_source.xlsx':'original_group_coefficients',
 'mapping/WoRMS_response.json':'taxonomy_authority_responses',
 'mapping/taxonomy_lookup.json':'taxonomy_lineages',
 'mapping/adopted_taxon_audit.json':'mapping_discrepancy_and_assumptions',
 'mapping/allocation_evidence.json':'allocation_quantities_and_candidates',
 'mapping/retained_weight_reconstruction.json':'regional_lineage_weight_reconstruction',
 'mapping/ecological_source_checks.json':'ecological_search_record',
 'mapping/coverage_summary.json':'arithmetic_universe_and_coverage',
 'diagnostics/adopted_loaded_state.json':'loaded_computational_state',
 'diagnostics/adopted_provenance.json':'effective_settings_and_runtime',
 'diagnostics/adopted_GE.json':'direct_GE_return_matrices_coefficients',
 'diagnostics/adopted_TE.json':'direct_TE_return_matrices_coefficients',
 'diagnostics/adopted_With_Egestion.json':'direct_WithEgestion_return_matrices_coefficients',
 'diagnostics/group_coefficient_comparison.json':'group_coefficient_comparison',
 'geography/geography_assessment.json':'geographic_denominators_and_uncertainty',
 'geography/region_boundary.png':'region_figure',
 'geography/source_study_area.png':'source_study_figure',
 'qa/final_scientific_checks.json':'scientific_and_adoption_reconciliation',
 'qa/shared_project_snapshot.json':'retained_selected_project_rows',
 'qa/map_payload.json':'retained_final_map_payload',
 'qa/shared_integration.json':'shared_integration_reconciliation',
 'qa/browser_verification.json':'visible_browser_verification',
 'qa/global_html_verification.json':'global_map_trend_archive_verification',
 'qa/portable_links.json':'relocated_local_link_verification',
 'qa/native_excel_check.json':'native_excel_recalculation',
 'qa/template_fidelity.json':'preserved_template_and_manual_rows',
 'qa/visual_verification.json':'artifact_visual_verification',
 'qa/workflow_stages.json':'workflow_stage_availability'}
artifacts=[]
required=[]
def add(role,p,required_role=True):
    assert p.is_file(),p
    artifacts.append({'role':role,'path':rel(p),'sha256':sha(p),'availability':'present'})
    if required_role:required.append(role)
for sub in ['baseline','diagnostics','geography','mapping','source','qa']:
    for p in sorted((R/sub).rglob('*')):
        if not p.is_file() or p.name.casefold()=='notes for ai.txt':continue
        key=p.relative_to(R).as_posix()
        add(roles.get(key,'support_'+key.replace('/','_').replace('.','_')),p,key in roles)
for role,p in [
 ('source_PDF',region/'papers/ARAB-2005/CMFRI-Bulletin-51-88a9c885.pdf'),
 ('adopted_computational_input',region/f'models/{model}/model.json'),
 ('adopted_group_coefficients',region/f'models/{model}/sppr_source.xlsx'),
 ('source_group_taxonomy_contract',region/f'models/{model}/source_evidence/mapping/{model}.taxonomy.csv'),
 ('adopted_regional_workbook',region/'LME_032.xlsx'),
 ('frozen_catch_download',region/'raw/LME_032-catch.zip'),
 ('frozen_taxon_metadata',region/'raw/LME_032-exploited.json'),
 ('validation_DOCX',region/f'Model_validation_{model}.docx'),
 ('linked_Excel_appendix',region/'LME032_taxon_mapping_appendix.xlsx'),
 ('template_input',ROOT/'tools/templates/Model_validation_template.docx'),
 ('filling_guide',ROOT/'tools/templates/Model_validation_template_instructions.md'),
 ('evidence_readme',R/'README.md'),('regional_report_index',region/'reports_index.md')]:add(role,p)
for role,reason,status in [
 ('native_EwE_database_roundtrip','Existing JSON route validated against source tables; no native EwE database was required or tested.','not_applicable_to_selected_JSON_route'),
 ('author_digitized_study_polygon','No defensible author digital polygon located; approximate coverage uses published study area and landmarks.','unavailable_after_source_review'),
 ('fresh_NPP_download','Existing independent annual NPP outputs are adequate and verified unchanged.','reused_existing_supported_outputs')]:
    artifacts.append({'role':role,'availability':'inapplicable' if role!='author_digitized_study_polygon' else 'missing','reason':reason,'acquisition_status':status})
prov=read(R/'diagnostics/adopted_provenance.json')
index={'schema_version':1,'run_id':run_id,'region_id':'LME_032','model_id':model,'variant_id':'published_balanced_diet_source_zero_BA',
 'source_identity':{'citation':'Mohamed et al. (2008), CMFRI Bulletin51','article_id':'ARAB-2005__LME_032','doi':None,
 'path':rel(region/'papers/ARAB-2005/CMFRI-Bulletin-51-88a9c885.pdf'),'sha256':sha(region/'papers/ARAB-2005/CMFRI-Bulletin-51-88a9c885.pdf'),
 'locators':'Study printed8/PDF18; group membership printed11–12/PDF21–22; landings printed13/PDF23; basic parameters and zero BA printed21/PDF31; balanced diet printed53/PDF63.'},
 'computational_input_identity':{'path':rel(region/f'models/{model}/model.json'),'sha256':prov['model_sha256'],'runtime_provenance':'diagnostics/adopted_provenance.json'},
 'methods':sorted(annual),'options':{'direct':prov['direct_settings'],'constructor':prov['constructor'],'reference':shared['reference'],'numeric_tolerances':'qa/final_scientific_checks.json'},
 'required_roles':required,'artifacts':artifacts,
 'reconciliation':{'source_parameter_catch_diet_reconciled':True,'full_direct_matrices_and_scopes_reconciled':True,'all_taxa_weights_confidences_and_denominator_reconciled':checks['all_passed'],'shared_project_map_trends_reconciled':shared['all_passed'],'native_appendix_values_reconciled':True,'visible_result_roundings_reconciled':True,'template_manual_rows_preserved':True,'relocated_local_links_verified':True},
 'limitations':'Inventory integrity is separate from scientific balance and geographic/mapping uncertainty. Three direct formulations remain WARN. No native EwE or author digital-polygon claim.'}
assert index['computational_input_identity']['sha256']==sha(region/f'models/{model}/model.json')
put(R/'evidence_index.json',index)
print(f'Prepared portable evidence index: {len(artifacts)} artifacts; {len(required)} applicable required roles; run {run_id}')
