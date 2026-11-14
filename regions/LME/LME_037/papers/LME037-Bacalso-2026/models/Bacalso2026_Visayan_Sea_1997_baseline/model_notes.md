# Bacalso2026_Visayan_Sea_1997_baseline

## Source identity

Paper/application: `LME037-Bacalso-2026__LME_037`. Regional application: `LME_037`.

The canonical source JSON remains unchanged, SHA-256 `a361c3dbf6abef5cedb0d0d480492e55907efde57b573278c5a7db2b7dbaf270`. The 1997 full-area parameters correspond to Bacalso (2026), Table 1; the diet and catch lineage comes from the Bacalso, Romagnoni and Wolff (2023) supplement, including diet Table S2, pages 7–8. The retained source-cell review verified 191 populated parameter cells. No new extraction was performed for the November 2026 accounting changes.

## Modeled period and area

Period: 1997. The selected model represents the local Visayan Sea baseline, not an independently reconstructed whole-LME food web. The study includes commercial waters plus inside-domain and outside-domain municipal waters of all 33 municipalities/cities (2023 §2.1, PDF page 2), with reported area 16,728.5 km²; the 2026 §2.2 baseline reuse supports that extent. Approximate marine overlap remains A 1–2% of the Sulu-Celebes target and B 90–100% of the study. The retained figure-based trace estimated A 1.59156%, B 98.04861%, and reconstructed marine area 16,457.4 km²; these are not author-supplied GIS measurements.

All 250 regional catch labels retain their reviewed mapping. The later 2004/2009/2014 surveys support membership, not measured 1997 stage caught-mass fractions. Applying fixed 1997 coefficients and proxy allocations across the whole LME and later catch years remains an assumption. The 2018 endpoint remains unselected and NOT_RUN.

## Departures from the publication

On 14/11/2026, Ido Carmel explicitly instructed that diets be normalized, biomass accumulation be changed to close the production equations, all Seabirds M0 be routed to an external sink rather than detritus, and Seabirds be marked as removed in the validation report's SPPR calculation field. These are researcher-authorized computational assumptions, not newly recovered publication measurements.

The original diet cells and missing BA values remain in `model.json` and the extraction tables. Runtime feeding diets are normalized to sum to one; nonfeeding basal rows retain their structural-zero diets. Biomass accumulation is calculated from the final production balance, including the external mortality sink, with positive and negative residuals retained. These values do not establish observed stock accumulation or depletion.

For Seabirds (group 1), the original EE is 0.02. The runtime external-sink transformation uses eligibility threshold 0.1 and replacement EE 1.0; it must affect only this group. All of its completed nonpredatory mortality leaves the modeled food web through the explicit nonfishery sink, while its egestion retains the specified detritus route. The sink is not fishery catch and does not enter catch-based allocation weights or fishery PPR. The original, completed and effective EE/M0 values are retained in the execution ledger.

The remaining inherited assumptions include GS 0.2 when missing, zero unknown diet imports and migration, and single-detritus accounting. Detritus production, EE and accumulation follow the documented runtime accounting rather than being presented as published source values. The full constructor settings, normalization factors and changed cells, BA residuals, sink ledger, runtime states, complete GE/TE/With Egestion returns and executed code identities accompany the current diagnostics.

Seabirds remains in the ecological group inventory and the diagnostic matrices. The researcher removal in the signed review specifies the initial displayed-PPR exclusion; it is not deletion of the trophic compartment or redistribution of its allocation weights.

The new GE, TE and With Egestion diagnostics all return OK, with strict input and global budget balance true and no negative or nonfinite basal-source coefficients. Inflow is 2,570.715 in the model's production units; each method's outflow matches within 1e-12. Thirty feeding diets sum to one; 99 runtime diet cells changed. All 32 living groups received final-flow BA completion, including 13 negative BA values. Original living biomass, P/B, Q/B, GS, catch and migration remain preserved. Seabirds external M0 is 0.000784; its near-zero-TE warning is absent in this configuration.

The earlier unnormalized configuration returned WARN, strict input/global balance false, and a near-zero Seabirds TE. Those results remain historical evidence and do not describe the newly requested configuration. Exact settings, precision and diagnostic outcomes are recorded in the linked execution evidence and final validation report. Researcher identity and decision are recorded in the DOCX; Project.xlsx registration and map/trend publication are assigned to the coordinator.

## Evidence links

- [Canonical Ecopath representation](model.json)
- [Original-input provenance](inputs/provenance.json)
- [Validation report](model_validation/validation.docx)
- [Current diagnostic execution evidence](results/diagnostics/researcher_adjustments_20261114/execution_evidence.json)
- [Current diagnostic evidence index](results/diagnostics/researcher_adjustments_20261114/evidence_index.json)
- [Earlier source and diagnostic review](model_validation/evidence/review_update_20261114.json)
- [Source review](model_validation/evidence/source_review/source_review.md)
- [Extraction report](extracted_tables/REPORT.md)
- [Result manifest](results/result_manifest.json)
- [Portable source dispositions](../../../../../../../common_reference_data/provenance/source_paths.csv)

## Removed extraction evidence

Superseded extraction packages and their unique old evidence were removed under the project's latest-only policy. Original paths, hashes and reasons remain in the linked disposition ledger. Missing former payloads are not replaced by claims of completed verification.
