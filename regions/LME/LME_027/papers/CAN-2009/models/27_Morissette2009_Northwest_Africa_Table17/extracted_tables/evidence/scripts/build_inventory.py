"""Freeze portable evidence hashes without confusing review readiness with source completeness."""
from pathlib import Path
import json,hashlib,importlib.util

C=Path(__file__).resolve().parents[1];ROOT=C.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

roles={
 'model.json':'canonical_source_model',
 'Taxonomy.xlsx':'candidate_taxonomy',
 'Model_validation_27_Morissette2009_Northwest_Africa_Table17.docx':'word_review',
 'LME027_candidate_taxon_mapping_appendix.xlsx':'excel_appendix',
 'extracted_tables/REPORT.md':'source_extraction_report',
 'extracted_tables/MODEL_PROFILE.md':'source_model_profile',
 'evidence/source_extraction/extraction.json':'source_cell_evidence',
 'evidence/source_extraction/source_admission.json':'source_admission',
 'evidence/identity/identity_review.json':'model_identity',
 'evidence/identity/ecobase118_official_input.xml':'official_native_source',
 'computational_inputs/official_EcoBase118.json':'native_computational_input',
 'diagnostics/direct_solutions.json':'complete_direct_solutions',
 'diagnostics/execution_evidence.json':'execution_settings',
 'diagnostics/loaded_state.json':'loaded_state',
 'diagnostics/transformation_ledger.json':'transformations',
 'mapping/taxon_audit.json':'all_taxon_audit',
 'mapping/allocation_evidence.json':'allocation_evidence',
 'mapping/coverage_summary.json':'mapping_coverage',
 'calculations/candidate_model_annual.csv':'candidate_annual_calculations',
 'calculations/candidate_model_npp_ratios.csv':'candidate_npp_calculations',
 'calculations/independent_classic_annual.csv':'independent_classic_calculations',
 'calculations/regional_input_snapshot.json':'catch_classic_npp_inputs',
 'evidence/geography/geographic_assessment.json':'geographic_assessment',
 'evidence/identity/independent_release_review.json':'independent_scientific_review',
 'evidence/protected_files_before.json':'protected_file_baseline',
 'qa/visual_review.json':'final_visual_qa',
 'reports_index.md':'review_handoff'
}
for filename in ['Basic_input','Diet_composition','Landings','Discards','Detritus_fate','Biomass_accumulation']:
    roles[f'extracted_tables/{filename}.csv']='import_'+filename
for filename in ['TL','Metadata']:
    roles[f'extracted_tables/{filename}.xlsx']='import_'+filename
pdf=C/'../../papers/FCRR_2009_17-2.pdf.pdf'
artifacts=[{'role':'source_pdf','path':'../../papers/FCRR_2009_17-2.pdf.pdf','availability':'present','sha256':sha(pdf)}]
excluded={'evidence_index.json','evidence_completeness.json','qa/release_verification.json'}
for p in sorted(C.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts or 'prior_render' in p.parts:continue
    rel=p.relative_to(C).as_posix()
    if rel in excluded or p.suffix in ('.pyc','.tmp') or p.name.startswith('~$'):continue
    artifacts.append({'role':roles.get(rel,'supporting_evidence'),'path':rel,'availability':'present','sha256':sha(p)})
artifacts.append({'role':'source_only_executable_input','availability':'missing',
 'reason':'The paper omits the zooplankton predator diet and complete GS, BA, routing and baseline-catch specification. Missing cells remain unknown. Verified native supplementation is executable but is the same EcoBase 118 model and is retained as a separate companion.',
 'acquisition_status':'Completed final-paper tables/prose review and official native retrieval; paper-only completion unsupported. No imputation or independent replacement claimed.'})
idx={'schema_version':1,'run_id':'20261003_LME027_Morissette2009_Table17_candidate_review',
 'region_id':'LME_027','model_id':C.name,'variant_id':'paper_only_extraction_with_separate_official_EcoBase118_diagnostic_companion',
 'source_identity':{'path':'../../papers/FCRR_2009_17-2.pdf.pdf','sha256':sha(pdf),'chapter':'Northwest Africa, printed pp.6-52; Tables17-18'},
 'computational_input_identity':{'path':'computational_inputs/official_EcoBase118.json','sha256':sha(C/'computational_inputs/official_EcoBase118.json'),'origin':'official EcoBase118 native companion; not paper-only reconstruction'},
 'methods':['GE','TE','With Egestion','independent classic simple-chain PPR'],
 'required_roles':['source_pdf',*roles.values(),'source_only_executable_input'],
 'artifacts':artifacts,
 'reconciliation':{'paper_to_native_identity_verified':True,'all_printed_diet_cells_compared':True,'all_taxa_audited':True,'all_native_companion_annual_rows_and_ratios_independently_reconciled':True,'all_scoped_coefficients_reconciled':True,'paper_only_missingness_retained':True},
 'release_notes':{'source_only_complete':False,'review_package_ready':'See qa/release_verification.json after final artifact and preservation checks.','adopted':False,'scientific_approval':False,'distinct_replacement_supported':False,
 'hash_exclusions':['This index and its computed completeness report','qa/release_verification.json, which checks this frozen inventory','Transient caches and superseded page renders']}}
save(C/'evidence_index.json',idx)
spec=importlib.util.spec_from_file_location('check_evidence',ROOT/'tools/skills/original_skill_resources/combined-src/scripts/check_evidence.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
result=m.check(C/'evidence_index.json');save(C/'evidence_completeness.json',result)
assert not result['errors'],result['errors']
assert result['missing_roles']==['source_only_executable_input'],result['missing_roles']
print(json.dumps({'verified_artifacts':len(result['verified_artifacts']),'integrity_errors':result['errors'],'missing_roles':result['missing_roles']}))
