from pathlib import Path
import json,hashlib
C=Path(__file__).resolve().parents[1]
read=lambda f:json.loads((C/f).read_text(encoding='utf8'))
cov=read('mapping/coverage_summary.json');qa=read('qa/package_verification.json')
report='Model_validation_27_Villanueva2004_SineSaloum_Thesis_1991-1992.docx';appendix='LME027_Villanueva2004_thesis_taxon_mapping_appendix.xlsx'
present={
 'registered_source':'../../papers/LME027-Villanueva-2004-Thesis/Villanueva2004_thesis_29305.pdf',
 'source_metadata':'../../papers/LME027-Villanueva-2004-Thesis/metadata.json',
 'source_literal_extraction':'extracted_tables/thesis/literal_source_extraction.json',
 'canonical_partial_model':'model.json',
 'source_admission':'computational_inputs/ADMISSION.json',
 'source_fidelity':'extracted_tables/thesis/partial_import_evidence/SOURCE_FIDELITY_CHECK.json',
 'identity_assessment':'evidence/identity/identity_review.json',
 'geography_assessment':'evidence/geography/geographic_assessment.json',
 'taxon_mapping':'mapping/taxon_mapping_audit.json',
 'allocation_evidence':'mapping/allocation_evidence.json',
 'coverage_denominators':'mapping/coverage_summary.json',
 'annual_independent_ppr':'calculations/annual_independent.json',
 'annual_candidate_catch_allocation':'calculations/annual_candidate_allocated_catch.json',
 'direct_execution_status':'diagnostics/execution_evidence.json',
 'direct_NOT_RUN_reports':'diagnostics/direct_reports.json',
 'independent_mapping_arithmetic_review':'evidence/identity/independent_final_checks.json',
 'independent_artifact_review':'evidence/source/final_artifact_review.json',
 'word_review':report,'excel_appendix':appendix,
 'package_verification':'qa/package_verification.json',
 'template_fidelity':'qa/template_fidelity.json',
 'visual_verification':'qa/visual_verification.json'
}
missing=['admitted_computational_input','loaded_constructor_state']+[f'{m}_{r}' for m in ['GE','TE','WithEgestion'] for r in ['full_diagnostic_return','SPPR_matrix','A_matrix','L_matrix','group_coefficients','taxon_coefficients','model_annual_PPR']]
artifacts=[]
for role,p in present.items():
 path=C/p
 assert path.is_file(),str(path)
 artifacts.append({'role':role,'availability':'present','path':p,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
for role in missing:artifacts.append({'role':role,'availability':'missing','reason':'Pre-constructor source admission blocked: Table6.5 group20 Epinephelus aeneus versus AnnexII.A Hemichromis fasciatus; no defensible source-supported join. GS/BA/routing also unreported.','acquisition_status':'Public thesis, related2005 chapter and official EcoBase612 endpoint checked. Author/native clarification still needed; no speculative reconstruction executed.'})
index={'schema_version':1,'run_id':'Villanueva2004_thesis_candidate_review_20261003','region_id':'LME_027','model_id':C.name,'variant_id':'thesis_1991-1992_Table6_5_AnnexIIA','source_identity':{'preferred':'registered_source','literal_tables':'Table6.5 PDF138 and AnnexII.A PDF235–236','period':'1991–1992','groups':37},'computational_input_identity':{'availability':'missing','admission':'BLOCKED_SOURCE_IDENTITY','canonical_partial':'model.json'},'methods':['GE','TE','With Egestion'],'required_roles':list(present)+missing,'artifacts':artifacts,'reconciliation':{'source_fidelity':True,'mapping_arithmetic_independent_review':True,'review_package_checks':qa['status']=='PASS'},'review_package_status':'READY_FOR_RESEARCHER_REVIEW' if qa['status']=='PASS' else 'QA_FAILED','scientific_execution_status':'BLOCKED_SOURCE_IDENTITY','adopted':False}
(C/'evidence_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf8')
text=f'''# Sine–Saloum thesis candidate review

Preferred candidate: **Villanueva (2004) doctoral thesis, Sine–Saloum, 1991–1992**, Table 6.5 / Annex II.A, 37 groups. Model ID `{C.name}`; variant `thesis_1991-1992_Table6_5_AnnexIIA`.

The thesis was downloaded and registered in [the regional papers folder](../../papers/LME027-Villanueva-2004-Thesis/README.md), with a citation, retrieval URL/date, full PDF and SHA-256. The [supplied 38-group chapter](../../papers/LME027-Villanueva-2004/010056023-adc18d15.pdf) remains a separate version and its evidence is preserved.

- [Unsigned Word review]({report})
- [512-taxon Excel appendix]({appendix})
- [Literal source extraction](extracted_tables/thesis/literal_source_extraction.json) and [canonical partial source representation](model.json)
- [Full evidence index](evidence_index.json) and [scientific handoff completeness](completeness.json)
- [Package verification](qa/package_verification.json), [independent source review](evidence/source/final_artifact_review.json) and [visual review](qa/visual_verification.json)

## Scientific status

Review package is ready for researcher review; scientific calculation is **blocked before construction**. Table 6.5 identifies group 20 as *Epinephelus aeneus*, whereas Annex II.A identifies group 20 as *Hemichromis fasciatus*. Table 3.3 separates their compartments. Matching ordinal numbers cannot establish biological identity. A source-specific native input or author clarification is required. Unreported GS, BA, routing and discard scope are preserved as unknown. No defaults, normalization, biological repair or calculator execution were applied.

DIRECT GE, TE and With Egestion are **NOT_RUN**. Rho, b, negative-entry checks, detrital SPPR, matrices and model-derived coefficients/PPR are unavailable. Partial structural import findings are reconstruction checks, not model diagnostic results. `model.json` is evidence and must not be passed as an admitted input.

## Mapping and independent arithmetic

All 512 regional catch labels are retained, including zero-catch rows. Reference: **2019 landings excluding discards**. Landings total {cov['total_catch_tonnes']:,.6f} t; complete independent simple-chain PPR {cov['total_simple_chain_ppr_tC']:,.6f} t C. All 100 missing classic coefficients occur on zero-catch labels in this reference, so their contributions are zero; their coefficients and TL remain unknown.

Confidence counts: {', '.join(str(r['taxa'])+' '+r['label'] for r in cov['confidence_summary'])}. Membership evidence and assumed allocation weights are audited independently; overall confidence takes the weaker required component. Source catch and biomass proportions are proxy assumptions, not observed regional catch compositions. The three model PPR columns remain unavailable.

Historical records cover 1950–2019 and three catch bases (210 records): 61 complete independent totals and 149 explicitly incomplete known subtotals. Unknown positive-catch contributions are not treated as zero. The 7,770 candidate group allocations conserve reported catch, using fixed source mixture assumptions; they do not establish historical ecological validity.

## Geographic and temporal fit

The thesis reports 546 km². This caps target-LME coverage A at 0.0485933% (approximately 0.049%), even if all study water were contained. This is an area upper bound, not measured polygon overlap. Study containment B is undetermined because the exact model-water boundary is unresolved and the schematic conflicts with the printed longitude strip. The localized estuarine model has poor whole-LME representativeness; 1991–1992 is 27–28 years before the 2019 reference catch.

## Preservation

The active LME_027 selection remains `27_118_Northwest_Africa_(1987)`. Its signed 02/10/2026 disqualification and prior Morissette candidate are retained. No candidate adoption, researcher signature or central registration was performed. This task wrote only this candidate folder and the newly registered thesis paper folder.

Protected baseline verification retains all original hashes. All 374 local protected files match. Three shared files (Project.xlsx, map index and trends) changed concurrently in the user-authorized LME_013 chat “Evaluate Northern Humboldt auto mode”; this task did not overwrite or restore those changes. LME_027 Project rows and map selection are independently checked in QA.

Office links resolve from these co-located files and remain relative. Word retains the supplied template parts and manual researcher fields. All 13 Word pages and five saved-workbook preview pages were inspected. Spreadsheet authoring used the skill's openpyxl fallback because the bundled artifact-tool module was unavailable; actual Excel rendered the saved workbook read-only for QA.
'''
(C/'README.md').write_text(text,encoding='utf8')
stages={'source_registration':'COMPLETE','literal_extraction':'COMPLETE','source_admission':'BLOCKED_SOURCE_IDENTITY','constructor':'NOT_RUN','DIRECT_GE':'NOT_RUN','DIRECT_TE':'NOT_RUN','DIRECT_WithEgestion':'NOT_RUN','candidate_taxon_mapping':'COMPLETE_UNADOPTED','independent_classic_PPR':'COMPLETE_REFERENCE_WITH_HISTORICAL_MISSINGNESS','review_package':index['review_package_status'],'scientific_evidence_handoff':'INCOMPLETE_EXPECTED','regional_integration':'NOT_AUTHORIZED_NOT_RUN','researcher_verdict':'UNSIGNED'}
(C/'stage_statuses.json').write_text(json.dumps(stages,indent=2),encoding='utf8');print('Portable index and README created.')
