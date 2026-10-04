from pathlib import Path
import json,sys,hashlib,os
sys.stdout.reconfigure(encoding='utf-8');OUT=Path(__file__).parent;ROOT=OUT.parents[4];REG=ROOT/'regions/LME_013'
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
summary=load('comparison_summary.json');verification=load('verification.json');identity=load('baseline_identity.json');model=identity['settings']['selected_model_id']
roles={
 'baseline_manifest':OUT/'baseline_manifest.json','baseline_inputs':OUT/'baseline_tables.json','baseline_runtime_identity':OUT/'baseline_identity.json',
 'all_taxon_decision_ledger':OUT/'decision_ledger.json','keyed_adopted_decisions':OUT/'reconciled_decisions.json','allocation_review':OUT/'allocation_residual_review.json',
 'fish_squid_review':OUT/'fish_squid_review.json','cartilage_invertebrate_review':OUT/'elasm_invertebrate_review.json','comparison_summary':OUT/'comparison_summary.json',
 'root_completeness_and_additional_species_review':OUT/'root_additional_review.json',
 'final_component_classification_adjudication':OUT/'component_classification_adjudication.json',
 'complete_review_key_ownership':OUT/'review_completeness.json',
 'concurrent_shared_file_notice':OUT/'concurrent_protected_file_changes.json',
 'protected_inputs_and_output_verification':OUT/'verification.json','diagnostic_matrix_reconciliation':OUT/'diagnostic_verification.json',
 'current_regional_workbook':REG/'LME_013.xlsx','validation_document':REG/f'Model_validation_{model}.docx','mapping_appendix':REG/'LME013_taxon_mapping_appendix.xlsx',
 'source_model_parameters':REG/f'models/{model}/model.json','source_taxonomy_definitions':OUT.parent/'source_group_definitions.json',
 'retained_direct_GE':REG/'models/regional_ge_integration_20260928/direct_new_GE.json',
 'retained_direct_TE':REG/'models/regional_ge_integration_20260928/direct_new_TE_EEfix.json',
 'retained_direct_WithEgestion':REG/'models/regional_ge_integration_20260928/direct_new_WithEgestion.json',
 'rendered_pdf':OUT/'final_render/report.pdf','page_render_manifest':OUT/'final_render/render_manifest.json','visual_inspection':OUT/'visual_inspection.json'}
data={'schema_version':1,'run_id':'LME013_mapping_reassessment_20261003','region_id':'LME_013','model_id':model,'variant_id':'selected_1980_fixed_saved_coefficients_mapping_only','source_identity':{'main_source':'Neira et al. doi:10.1016/j.pocean.2025.103631','source_definition':'Table 1 PDF4','protected_model_sha256':identity['current_selected_model_sha256']},'computational_input_identity':{'retained_solver_input_sha256':identity['saved_result_input_identity'],'revised_regional_calculation_input_sha256':verification['fresh_input_hash'],'revised_regional_result_sha256':verification['fresh_result_hash'],'execution':'dependent regional arithmetic only; retained GE/TE/With Egestion inputs and diagnostics unchanged'},'methods':['new_GE','new_TE_EEfix','new_WithEgestion','simple trophic chain'],'required_roles':list(roles),'artifacts':[{'role':role,'availability':'present','path':os.path.relpath(p,OUT).replace('\\','/'),'sha256':sha(p)} for role,p in roles.items()],'reconciliation':{'all218labels_reviewed_and_agree':True,'weights_valid_and_confidence_uses_weaker_component':True,'independent_simple_chain_carbon_denominator_once':True,'protected_scientific_and_shared_files_unchanged':True,'retained_matrix_coefficients_actual_identity_checked':True,'regional_arithmetic_fresh_all_methods_scopes_bases':True,'manual_document_content_and_office_features_preserved':True,'very_low_list_exact_and_local_links_portable':True,'all_word_pages_and_appendix_views_inspected':True},'authorization_boundary':summary['shared_update'],'scientific_limits':'Taxon reassessment does not establish model validity or remove saved WARN/FAIL flags, spatial or temporal transfer limits. No extraction, group-SPPR solver or Monte Carlo was rerun.'}
data['reconciliation'].pop('protected_scientific_and_shared_files_unchanged')
data['reconciliation']['protected_scientific_inputs_unchanged']=True
data['reconciliation']['no_shared_file_written_by_this_task_concurrent_changes_recorded']=True
data['concurrent_shared_file_changes']=verification['concurrent_shared_file_changes']
(OUT/'evidence-index.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
index=OUT.parent/'reports_index.md'
original=index.read_text(encoding='utf-8');backup=OUT/'baseline/reports_index.md'
if not backup.exists():backup.write_text(original,encoding='utf-8')
addition='\n\n## Mapping reassessment for researcher review — 3 October 2026\n\nAll 218 catch labels were reassessed against the selected Chilean Patagonia 1980 definitions, provider reporting scope and primary regional evidence. Supported memberships, proxy allocations and component ratings were adopted in the regional workbook; only dependent regional arithmetic used the retained group coefficients. The existing Word validation and seven-column appendix now reflect those adopted rows. Pre-edit copies and every retained/changed decision are preserved. Researcher manual fields are unchanged. The saved diagnostic identities and warnings remain; no extraction, group-SPPR solver or Monte Carlo was rerun.\n\nThe Word document awaits researcher review. Project, map, trends, archive and knowledge graph remain unchanged, and no researcher approval has been registered.\n\n- [Complete reassessment and preservation evidence](mapping_improvement_20261003/evidence-index.json)\n- [Keyed adopted decisions](mapping_improvement_20261003/reconciled_decisions.json)\n- [Old and new taxon decision ledger](mapping_improvement_20261003/decision_ledger.json)\n- [Confidence coverage and regional PPR comparison](mapping_improvement_20261003/comparison_summary.json)\n- [Saved output verification](mapping_improvement_20261003/verification.json)\n'
addition=addition.replace('Project, map, trends, archive and knowledge graph remain unchanged, and no researcher approval has been registered.','This task has not written Project, map, trends, archive or knowledge graph, and no researcher approval has been registered. Concurrent changes to shared files since baseline are recorded in the verification evidence; they were left intact.')
if '## Mapping reassessment for researcher review — 3 October 2026' not in original:index.write_text(original.rstrip()+addition,encoding='utf-8')
print('Current evidence index and appended regional review navigation saved.')
