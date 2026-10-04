# Banc d’Arguin: completed candidate assessments

Guénette, Meissa and Gascuel (2014), DOI [10.1371/journal.pone.0094742](https://doi.org/10.1371/journal.pone.0094742). Assessment date: 3 October 2026. All feasible requested stages are complete. None of the three published parameterizations is presently eligible for production or automatic regional selection.

| Variant | Published-source direct diagnostics | Independent regional model PPR | Review files |
|---|---|---|---|
| Base | NOT_RUN: five diet rows reject constructor admission; source stanza production remains incomplete | Unavailable. A separately identified approximation returns FAIL for GE, TE and With Egestion and has provisional arithmetic only | [DOCX](../../../../papers/CAN-2014/models/Guenette2014_BancArguin_Base_1991/model_validation/validation.docx) · [Excel](../../../../papers/CAN-2014/models/Guenette2014_BancArguin_Base_1991/model_validation/taxon_mapping.xlsx) · [canonical evidence](../../../../papers/CAN-2014/models/Guenette2014_BancArguin_Base_1991/extracted_tables/evidence/evidence_index.json) |
| M30 | NOT_RUN: 114 unpublished diet components across 14 consumers, plus original source blanks | Unavailable; no Base coefficients inherited | [DOCX](../../../../papers/CAN-2014/models/Guenette2014_BancArguin_M30_1991/model_validation/validation.docx) · [Excel](../../../../papers/CAN-2014/models/Guenette2014_BancArguin_M30_1991/model_validation/taxon_mapping.xlsx) · [canonical evidence](../../../../papers/CAN-2014/models/Guenette2014_BancArguin_M30_1991/extracted_tables/evidence/evidence_index.json) |
| P30 | NOT_RUN: 114 unpublished diet components across 14 consumers, plus original source blanks | Unavailable; no Base coefficients inherited | [DOCX](../../../../papers/CAN-2014/models/Guenette2014_BancArguin_P30_1991/model_validation/validation.docx) · [Excel](../../../../papers/CAN-2014/models/Guenette2014_BancArguin_P30_1991/model_validation/taxon_mapping.xlsx) · [canonical evidence](../../../../papers/CAN-2014/models/Guenette2014_BancArguin_P30_1991/extracted_tables/evidence/evidence_index.json) |

The completed records are candidate assessments, not researcher signoffs. Template cells reserved for manual researcher choices remain unchanged. Each DOCX has eight rendered, visually inspected pages; each appendix contains all 512 catch labels, including zero catches. Final document and appendix QA is under `qa/` and `mapping/`.

## Source fidelity and extraction skill

One canonical directory remains per variant. Published coastal-bird diet totals **0.980331**; adult groupers’ Banc large-crustacean entry is **1.34**, with diet total **2.2006**. These replace the former normalized values. Original zero P/B for the two meagre groups, negative/zero biomass-accumulation rates, total mortality, P/Q, fleet catches, diet imports, unknowns and precision are retained. Fifty Table1/S8 Base numeric differences and competing authorities are documented. Unpublished variant diets remain unknown.

Each extraction has eight standard EwE import tables and **22 separate companion CSVs** retaining additional published fields, source grids, stanza/scenario information and provenance. The canonical JSON and reconstructed workbook preserve their contents. Every reconstructed workbook’s 58,293 checked cells reconciles with its tables. Unsupported fields remain available as evidence instead of being silently discarded or interpreted by the calculator.

The installed extraction skill and project portable fallback were improved and tested: the original regression baseline passed 3/13, the revised version 13/13, and independent adversarial tests 14/14. The active pipeline now prefers the current installed skill. The eight import schemas remain unchanged. **Compatibility was checked against those schemas; an actual EwE GUI import was not performed. Companion evidence CSVs are not claimed to be native EwE import tables.** See [skill validation](extraction/SKILL_VALIDATION.json).

## Diagnostic and regional arithmetic

The Base experiment uses a separate input with explicit diet normalization, four unverified source-blank-to-zero conventions, missing P/B approximated from rounded Q/B × P/Q, default egestion and closed single-detritus routing. Known P/B zeros remain unchanged; BA rate × biomass is a documented dimensional conversion. These choices do not reconstruct or validate the authors’ multistanza model. Full input/loaded states, settings, transformations, direct returns, all matrices and masks, coefficients and residuals are retained under [runtime](../../../../papers/CAN-2014/models/EcoBase689_native_1991).

For 2019 landings, all basal sources, no exclusions, full-precision weighted coefficients, wet PPR divided by nine once:

| Base experiment only | PPR (million t C/year) | PPR / ensemble NPP |
|---|---:|---:|
| GE | 105.8422206 | 22.3785% |
| TE | 1,362.7576460 | 288.1316% |
| With Egestion | 55.0193325 | 11.6329% |

Every value above is a **diagnostic-FAIL experiment**, not a production estimate. Ensemble NPP is 472.9635450 million t C/year. No negative SPPR entries or nonfinite values were found in the experiment’s complete 52 × 5 contribution matrices; strict model-input balance still fails. The separate authoritative EcoBase 689 deposit also fails all three flat-model diagnostics and differs materially from the published variants; it was not substituted into them.

All annual combinations of three catch bases, three treatments, three scopes, three methods and 1950–2019 are retained, with six available NPP series and explicit unknown masks. Missing NPP remains missing. Recorded zero catch contributes zero without inventing a coefficient; positive catch with an unavailable coefficient prevents a complete total. Independent arithmetic QA checks 18,432 taxon coefficients, 22,680 annual records and 136,080 PPR/NPP records. See [regional comparison](regional_comparison.json) and [arithmetic QA](mapping/candidate_arithmetic_qa.json).

## Taxonomy, mapping and applicability

All 51 source groups retain numbering, life stages, habitat and membership evidence. The source S1 Hake/Octopus row-number conflict is preserved. All 512 regional catch labels were assessed separately for each variant. Overall confidence counts are 116 High, 283 Medium, 45 Low, 68 Very low and 0 unresolved. Very low mappings account for 23.83% of 2019 landings. Assumption-dependent mappings account for 50.54%; numerical weight sums do not establish observational support.

For 2019 landings, the independent classic-chain PPR reference is 244,709,206.36682716 t C. All 100 labels missing a classic coefficient have zero catch in that year, so this annual reference total is complete. It is independent of candidate SPPR validity. Source-catch proxies are retained with transfer assumptions; original zero-weight candidates are not dropped. Base/M30 weights are identical; P30 differs for four biomass-proxy labels, as recorded in the mapping evidence.

The source covers the 1991 Mauritanian shelf, approximately 33,224 km²; Ecosim calibration spans 1991–2006. Approximate Figure1 reconstruction supports A≈3% of the full Canary Current LME and B≈95–100% of the study area. The old 9% claim is unsupported. Fixed transfer across the entire LME and 1950–2019 remains a substantial geographic and temporal assumption.

## Consolidation, selection and remaining requirements

The four obsolete Banc model folders and prior paper extraction tree were removed after all **161 files** were preserved and hash-verified in [the archive](../../../../../../../common_reference_data/provenance/source_paths.csv). The current [paper index](../../../../../../../common_reference_data/provenance/source_paths.csv), Project candidate records, paper metadata and map references now point to the new assessment. Frozen historical source context remains archived; future map builds filter candidates through the current inventory.

Original publications, the selected regional workbook and results, Northwest Africa 1987, its signed researcher record and the Morissette2009 candidate are preserved. Project still records the historical 1987 selection and the subsequent **Ido Carmel, 2 October 2026, disqualification** for excessive living-compartment recycling. Neither determines the independent Banc verdict. Candidate calculations were not inserted into selected regional results.

**No variant currently merits adoption.** Base is worth targeted reconsideration only after authoritative resolution of the diet and multistanza conflicts and a validated equivalent computational representation. M30/P30 additionally require complete authoritative variant diet exports. Better spatial applicability and mapping evidence would still be needed for whole-LME production use.

The [portable evidence inventory](evidence_index.json), [completeness result](completeness.json), [final verification](qa/final_verification.json) and [protected-file audit](qa/protected_files.json) identify available artifacts and unavailable scientific results precisely. Inventory completeness is not a scientific pass.

## Reproduction

Use Python with the versions recorded in `runtime/requirements.txt`. `runtime/run_direct.py` is the bounded entry point; each execution’s `execution_evidence.json` records source identity, constructor options, method settings, thresholds and code hashes. The three current canonical JSONs are source data. Do not run their import tables through an unrecorded diet-normalizing process.

`calculate_candidates.py` performs candidate-only arithmetic; `verify_diagnostics.py` and `mapping/verify_candidate_arithmetic.py` independently reconcile persisted outputs. `build_handoff.py` rechecks final identities, protected files, local Office links and portable inventories. Consolidation scripts are one-shot historical operations and should not be replayed on the consolidated tree.
