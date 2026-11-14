# Gulf of Alaska official Rpath aggregate

## Source identity

Whitehouse, G.A. and Aydin, K.Y. (2020). Assessing the sensitivity of three Alaska marine food webs to perturbations: an example of Ecosim simulations using Rpath. Ecological Modelling 429, 109074. https://doi.org/10.1016/j.ecolmodel.2020.109074

This is the official NOAA-EDAB/Rpath **Ecosense.GOA** parameter object, pinned to commit `fe63f6d370d942ff1786f4d649e432fbfb85f81b`. It contains **49 biological groups (46 consumers, one primary producer and two detritus pools) plus one fleet**. The original CSVs and R object are retained in [inputs/native](inputs/native/); [provenance](inputs/provenance.json) records exact bytes and SHA-256 hashes. At initial extraction the RDA file was archived but not independently decoded; the dated native reproduction follow-up below records the subsequent verification. The extraction uses the three CSVs that the official builder identifies as the object's inputs.

## Modeled period and area

The source documentation calls this a 1990s model aggregated from Aydin et al. (2007); **1990–1994** is the inherited original model period. The 2020 article is the publication of the aggregate, available online 25 May 2020. Its modeled shelf area is **291,840 km²**, 140°W–170°W (article §2.2.3, p.4). No new geographic coverage percentage or boundary was derived.

## Departures from the publication

The native aggregate is a distinct model from the 133-compartment published extraction. The 2020 article describes summing B and catch and biomass-weighting P/B, Q/B and DC, with one producer, two detritus pools and one fleet. Its text calls the preaggregation GOA model138 groups; this does not establish a one-to-one relationship with the133 published Appendix C compartments. The official documentation says no stanzas. Neither the original detailed diets nor a balanced native result have been substituted into this aggregate.

All native numeric literals, blanks, zeros and source order are preserved in companions. The canonical49 biological groups retain exact native names. Only strict import files use `Urchins dollars cucumbers` for native `Urchins, dollars, cucumbers` (group31), because the maintained writer forbids commas. This reversible representation decision was made by the extraction agent under the authorized task, not as a researcher scientific correction. [Label crosswalk](extracted_tables/companions/Group_label_crosswalk.csv) and [independent verification](extracted_tables/evidence/native_canonical_verification.json) record the mapping. Embedded import source tables intentionally retain the alias.

Native all-blank EE values and the two missing detritus biomasses remain unknown. Source BA values are retained, including pollock−1.35, pelagic forage fish−0.11 and other demersals−0.002 t/km²/year. Habitat fraction, TL, mortality Z, other mortality, detritus export and unavailable native fields are not filled. The native producer diet column is nonfeeding and all prey cells are blank, with Import0. Its full column is preserved in the native diet companion and its Import0 in canonical `diet_imp`.

Rpath's balance routine changes NA diet cells to0 on a separate runtime array. This extraction preserves raw NA cells as blanks in imports and−9999 in canonical diet entries. Therefore the canonical model is a source-faithful sparse parameter representation; it is not a balanced Rpath execution result. A future authorized calculation must explicitly reconcile native NA-as-zero semantics, unknown EE and detritus biomass. No balance or PPR solve was performed.

Two source fate rows (the detritus pools) are explicitly0+0, so the generic import validator reports two sum errors. No export fraction was invented to remove them. The native fleet routing fractions0.3908825/0.6091174 are retained in the companion; exact destination-name duplicate columns make these supported by ModelData without changing native fields. These are native fleet returns, distinct from the biological detritus fate rows.

## Evidence links

[Extraction report](extracted_tables/evidence/REPORT.md), [source reconstruction check](extracted_tables/evidence/SOURCE_FIDELITY_CHECK.json), [native/canonical checks](extracted_tables/evidence/native_canonical_verification.json), [schema admission](extracted_tables/evidence/loader_schema_check.json), [mass-balance source check](extracted_tables/evidence/MASS_BALANCE.md), [Table1 membership](extracted_tables/companions/Aggregation_membership_Table1.csv), [illustrative comparison](extracted_tables/evidence/comparison_with_original_publication.json), [evidence inventory](extracted_tables/evidence/evidence_index.json).

The NOAA article was read through its indexed full text; local PDF retrieval returned 403 and screenshot retrieval failed. Table 1's membership companion is therefore explicitly pending visual verification and did not determine numerical extraction. ModelData schema admission is `True`; this is not calculator construction, numerical readiness, model selection or researcher approval.

The [source-to-loader ledger](extracted_tables/evidence/source_to_loader_ledger.json) checks 490 scalar fields and 2,254 diet entries. All diet values and NaN masks agree. The only 47 scalar differences are blank native DetInput values becoming runtime 0; the native Rpath code explicitly uses that runtime default too. Canonical source blanks stay unknown. All 49 unknown EE values and both unknown detritus biomasses remain unknown in the loader. The source checker uses a generic “BA unknown” section heading, but the actual indeterminate reasons are sparse diet cells; all 49 BA values are known.


## Candidate group structure and taxonomy

[MODEL_PROFILE.md](MODEL_PROFILE.md) records source guild/stage/spatial structure and the period/area basis. [Candidate Taxonomy.xlsx](extracted_tables/Taxonomy.xlsx) retains the source Table 1 functional-group membership for all 49 exact native labels, with visual and taxonomic-authority review pending. It has not been applied to canonical taxon_descr, which remains null. The canonical model bytes and numerical extraction are unchanged. See [candidate evidence](extracted_tables/evidence/candidate_taxonomy_evidence.json).

## Native reproduction follow-up — 2026-11-14

The official Rpath balance has now been reproduced in a [separate computational variant](../Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance/model_notes.md). The archived RDA model, diet and pedigree match the native CSV reader objects exactly. The raw extraction and its unknown values remain unchanged. All three direct PPR methods returned FAIL in the current translation; see the variant results for the detritus accounting explanation. This follow-up does not select or approve either model.
