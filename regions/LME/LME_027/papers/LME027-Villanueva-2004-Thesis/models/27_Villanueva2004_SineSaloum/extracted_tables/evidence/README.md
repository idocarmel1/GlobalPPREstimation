# Sine–Saloum thesis candidate review

Preferred candidate: **Villanueva (2004) doctoral thesis, Sine–Saloum, 1991–1992**, Table 6.5 / Annex II.A, 37 groups. Model ID `27_Villanueva2004_SineSaloum`; variant `thesis_1991-1992_Table6_5_AnnexIIA`.

The thesis was downloaded and registered in [the regional papers folder](../../../../sources/README.md), with a citation, retrieval URL/date, full PDF and SHA-256. The [supplied 38-group chapter](../../../../../LME027-Villanueva-2004/sources/010056023-adc18d15.pdf) remains a separate version and its evidence is preserved.

- [Unsigned Word review](../../model_validation/validation.docx)
- [512-taxon Excel appendix](../../model_validation/taxon_mapping.xlsx)
- [Literal source extraction](../thesis/literal_source_extraction.json) and [canonical partial source representation](../../model_notes.md#removed-extraction-evidence)
- [Full evidence index](evidence_index.json) and [scientific handoff completeness](completeness.json)
- [Package verification](qa/package_verification.json), [independent source review](evidence/source/final_artifact_review.json) and [visual review](qa/visual_verification.json)

## Scientific status

Review package is ready for researcher review; scientific calculation is **blocked before construction**. Table 6.5 identifies group 20 as *Epinephelus aeneus*, whereas Annex II.A identifies group 20 as *Hemichromis fasciatus*. Table 3.3 separates their compartments. Matching ordinal numbers cannot establish biological identity. A source-specific native input or author clarification is required. Unreported GS, BA, routing and discard scope are preserved as unknown. No defaults, normalization, biological repair or calculator execution were applied.

DIRECT GE, TE and With Egestion are **NOT_RUN**. Rho, b, negative-entry checks, detrital SPPR, matrices and model-derived coefficients/PPR are unavailable. Partial structural import findings are reconstruction checks, not model diagnostic results. `model.json` is evidence and must not be passed as an admitted input.

## Mapping and independent arithmetic

All 512 regional catch labels are retained, including zero-catch rows. Reference: **2019 landings excluding discards**. Landings total 5,421,499.956519 t; complete independent simple-chain PPR 244,709,206.366827 t C. All 100 missing classic coefficients occur on zero-catch labels in this reference, so their contributions are zero; their coefficients and TL remain unknown.

Confidence counts: 71 High, 23 Medium, 4 Low, 414 Very low, 0 Unresolved. Membership evidence and assumed allocation weights are audited independently; overall confidence takes the weaker required component. Source catch and biomass proportions are proxy assumptions, not observed regional catch compositions. The three model PPR columns remain unavailable.

Historical records cover 1950–2019 and three catch bases (210 records): 61 complete independent totals and 149 explicitly incomplete known subtotals. Unknown positive-catch contributions are not treated as zero. The 7,770 candidate group allocations conserve reported catch, using fixed source mixture assumptions; they do not establish historical ecological validity.

## Geographic and temporal fit

The thesis reports 546 km². This caps target-LME coverage A at 0.0485933% (approximately 0.049%), even if all study water were contained. This is an area upper bound, not measured polygon overlap. Study containment B is undetermined because the exact model-water boundary is unresolved and the schematic conflicts with the printed longitude strip. The localized estuarine model has poor whole-LME representativeness; 1991–1992 is 27–28 years before the 2019 reference catch.

## Preservation

The active LME_027 selection remains `27_118_Northwest_Africa_(1987)`. Its signed 02/10/2026 disqualification and prior Morissette candidate are retained. No candidate adoption, researcher signature or central registration was performed. This task wrote only this candidate folder and the newly registered thesis paper folder.

Protected baseline verification retains all original hashes. All 374 local protected files match. Three shared files (Project.xlsx, map index and trends) changed concurrently in the user-authorized LME_013 chat “Evaluate Northern Humboldt auto mode”; this task did not overwrite or restore those changes. LME_027 Project rows and map selection are independently checked in QA.

Office links resolve from these co-located files and remain relative. Word retains the supplied template parts and manual researcher fields. All 13 Word pages and five saved-workbook preview pages were inspected. Spreadsheet authoring used the skill's openpyxl fallback because the bundled artifact-tool module was unavailable; actual Excel rendered the saved workbook read-only for QA.
