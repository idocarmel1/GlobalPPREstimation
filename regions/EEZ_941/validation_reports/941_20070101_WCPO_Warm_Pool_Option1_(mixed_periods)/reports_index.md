# EEZ_941 validation evidence index

Review date: 30 September 2026. Exact selected model: `941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)`. This is a new regional validation analysis using retained source/runtime evidence, with explicitly authorized mapping adoption and regional dependent calculations. It is not researcher approval or a new native EwE validation.

## Final regional artifacts

- [Word validation record](../../Model_validation_941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods).docx)
- [Seven-column taxon appendix and descriptive Sources](../../EEZ941_taxon_mapping_appendix.xlsx)
- [Updated canonical regional workbook](../../EEZ_941.xlsx)
- [All 63 adopted decisions and allocation candidates](taxon_audit.json)
- [Source interpretation, taxonomy, stage assumptions and geography](source_review.md)

## Exact accepted scientific evidence

- [Accepted selected JSON](../../models/941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)/941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods).json), [variant provenance](../../models/941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)/SELECTION_AND_PROVENANCE.json), [original source audit](../../models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)/extracted_tables/REPORT.md)
- [Allain et al. source PDF](../../papers/WCP-2007/download-0adcf55e.pdf#page=9), [source evidence](../../papers/WCP-2007/extraction_evidence), [retained direct returns](../../evidence/2026-09-28_integration/direct_diagnostics.json), [runtime settings/engine identity](../../evidence/2026-09-28_integration/runtime_verification.json), [transformation ledger](../../evidence/2026-09-28_integration/transformation_ledger.json), [engine snapshots](../../evidence/2026-09-28_integration/engine_snapshot)
- Full retained group × basal-source matrices: [GE](../../evidence/2026-09-28_integration/SPPR_GE.csv), [TE](../../evidence/2026-09-28_integration/SPPR_TE.csv), [With Egestion](../../evidence/2026-09-28_integration/SPPR_With_Egestion.csv). [This review's full axis/sign/coefficient verification](diagnostics_verification.json) inspected all 32 recipients, including unfished groups, and all four basal-source columns.
- [Protected-table adoption receipt](adoption_receipt.json), [arithmetic and mapping verification](verification.json), [exact classic before/after differences and preservation](classic_preservation_verification.json), [final candidate-completeness correction](pre_completion_corrections.json)

## Geographic/source images and online evidence

- [Geographic calculation](geographic_estimate.json), [region boundary](region_boundary.png), [fixed source study rectangle](study_domain.png), [article Figure 1 crop](article_figure1_crop.png), [full source PDF3 rendering](article_figure1_pdf3.png)
- [Kiribati 2020 report copy](online/Kiribati_2020.pdf) and [extracted text](online/Kiribati_2020.txt), copied without changes from `original_research_archive/research/size_allocation_20260929/pacific/online/`; [retained primary stage-data search audit](online/20260929_search_audit.json) and [original source hashes](online/20260929_source_hashes.json), copied without changes from that archive. The all-region audit has historical paths; the required Kiribati file is retained locally here, and this review makes no new claim of full retrieval of its other listed materials.
- Taxonomy/ecology web references are described with exact material read, retrieval date and access limits in [source review](source_review.md#membership-and-reporting-scope) and the appendix Sources sheet. NCBI full entries were read; WoRMS indexed corroboration had direct timeout/403. FAO primary sources support taxonomy/ecology, not regional caught-mass composition. No arbitrary observed stage shares were inferred.

## Builders and QA

- [Regional audited adoption builder](../../build_validation.py), [geographic boundary builder](../../geography_validation.py), [report builder](qa/build_document.py), [artifact-tool appendix builder](qa/build_appendix.mjs), [native hyperlink formatting helper](qa/native_links.py), [independent numerical verifier](qa/check_evidence.py)
- [Template fidelity proof](qa/document_fidelity.json), [packaged renderer failure log](qa/packaged_renderer.log), [owned hidden Word PDF fallback](qa/word_export.ps1), [rendered report](qa/report.pdf). Page and appendix-sheet PNGs in `qa/` are review evidence, not additional final deliverables. The fallback opens only the generated output read-only and closes only the separately created Word instance.
- Artifact-tool could not calculate HYPERLINK formulas. They were replaced with literal descriptive labels and native OOXML hyperlinks; explicit font color/underline was applied without changing scientific values or table layout. A first native-patching attempt lost table relationships, was diagnosed and superseded; final patch preserves them. The final XLSX imports and renders successfully with artifact-tool.
- [Coordination handoff](coordination_handoff.json) records protected state, keyed old/adopted mappings, exact selected model/diagnostic identities, proposed shared keyed edits and remaining Project/map/browser integration.

The shared integration/browser completion gate remains coordinator-owned. This regional evidence supports the intended classic all-taxon 2019 landings view at 167,307,899.00452706 t C. It does not claim the current shared map has already been refreshed or reconciled.

## Coordinator reconciliation — 1 October 2026

Regional review and shared result reconciliation are complete. Earlier pending coordinator tasks in the regional handoff describe its historical release stage. Current reports, appendices, preserved scientific inputs, limits and verification are indexed in [the 23-region coordinator record](<../../../../original_research_archive/research/selected_regions_validation_20260930/final_validation_status.md>). Scientific approval is not implied; graph and Git closeout are tracked separately.
