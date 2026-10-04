# Northern Humboldt candidate evidence for review

This folder contains the fresh Chiaverano et al. (2018) detailed Northern Humboldt extraction, runtime diagnostics, catch mappings and regional candidate arithmetic. The review package is complete, but GE, TE and With Egestion all return **FAIL**. The saved numerical outputs are scientifically ineligible for adoption. The selected Chilean Patagonia 1980 model retains its existing WARN findings and southern spatial limitation.

Start with the [candidate Word validation](../../Model_validation_HUM2018_Northern_Humboldt_candidate_20261003.docx) and its [Excel mapping appendix](../../LME013_HUM2018_candidate_taxon_mapping_appendix_20261003.xlsx). The manual researcher calculation, open-issues and review fields remain available for the user's review. No researcher decision has been registered.

## Source reconstruction

The [source audit](source/REPORT.md), [conflict record](source/SOURCE_CONFLICTS.json) and [publication identity](source/SOURCE_IDENTITY.json) refer to the verified local PDF, native XLS supplement and Word figures/tables. The historical abbreviated title and unavailable-source metadata are not used as source evidence.

The detailed source has 39 ecological stocks and two fleet records. Its static baseline is 1995–1998 over 165,000 km², 4°S–16°S and up to 111 km offshore. The [aggregated alternative](source/aggregated_alternative_source.json) has 24 ecological groups plus a pooled fishery node; its rounding and reduced routing make it less suitable for this detailed audit. Structural scenarios remain separate from these static variants.

[Canonical source JSON](source/resolved_native/model.json), [eight EwE imports and reconstruction](source/resolved_native/), [taxonomy](source/resolved_native/Taxonomy.xlsx) and [round-trip comparisons](source/resolved_native/ROUND_TRIP_CHECKS.json) preserve printed values and missingness. Chrysaora diet sums to 1.045; gelatinous zooplankton production is far below its implied predation demand; supplement sardine landings conflict with the prose balanced baseline. No unsupported numerical repair has been applied.

## Runtime and diagnostics

The [separate computational input](source/computational/model.json) retains an [explicit convention ledger](source/computational/TRANSFORMATION_LEDGER.json). Anchovy eggs act as a nonfeeding pool, giving four operational detritus pools and 35 living groups. A synthetic diet import is runtime ID 40; it is distinct from native fleet ID 40.

[Full DIRECT returns](diagnostics/full_direct_report.json), [readable unabridged diagnostics](diagnostics/full_direct_report.md), [run settings and hashes](diagnostics/run_manifest.json), [labeled matrices](diagnostics/GE/SPPR.csv), and [all negative matrix entries](diagnostics/all_negative_matrix_entries.csv) cover all groups, including unfished groups. GE and With Egestion each contain 59 negative SPPR entries across three source columns; 26 entries involve unfished recipients. TE has no negative SPPR entries but fails strict balance.

The [raw/runtime cell ledger](diagnostics/loader_matrix_field_ledger.json), [normalization ledger](diagnostics/runtime_normalization_changed_cells.json) and [translation limits](diagnostics/source_translation_limitations.md) disclose 161 diet-cell normalizations, eight native detritus-fate overwrites, unsupported fishery discard-return ancestry and the multi-pool TE EE=0 restriction. These limits prevent the runtime from being a complete native EwE representation.

## Catch mapping and arithmetic

[All 218 catch-label decisions](mapping/mapping_review.json), [allocation quantities](mapping/allocation_ledger.json), [primary composition searches](mapping/search_records.json) and [mapping verification](mapping/verification.json) retain membership and allocation confidence separately. Overall counts are High 70, Medium 104, Low 17, Very low 27 and Unresolved 0. Very low decisions account for 3.1630253% of 2019 landings and 4.8644751% of independent classic PPR. All 42 zero-catch labels remain included.

The independent 2019 landings denominator is 277,099,551.4346593 tonnes C; saved wet-equivalent classic coefficients are multiplied by catch and divided by nine once. All 34 unavailable classic coefficients belong to zero-catch labels in that year. The [regional input snapshot](mapping/regional_arithmetic_snapshot.json) keeps the existing catch, classic and NPP inputs distinct from the candidate model coefficients.

[Candidate calculation manifest](diagnostics/candidate_calculation_manifest.json), [annual totals](diagnostics/candidate_annual_totals.csv), [compressed taxon-year contributions](diagnostics/candidate_taxon_annual.csv.gz), [2019 taxon results](diagnostics/candidate_reference_2019_taxa.csv) and [annual PPR/NPP](diagnostics/candidate_annual_npp_ratios.csv) retain all three methods, PP/inner/all scopes, catch/discards/landings bases and method/zero/simple unidentified treatments. Unavailable source decompositions, absent annual NPP and negative outputs remain explicit; every model result is marked production-ineligible. Reproduction details are in [REPRODUCE.md](diagnostics/REPRODUCE.md).

## Applicability and preservation

The [geographic assessment](geography/geographic_assessment.json) uses the original Figure 1 and the existing regional boundary. Approximate region coverage is 6–8%, and approximately 90–100% of the study lies inside the region. These are boundary-interpretation ranges, not statistical intervals. Fixed 1995–1998 coefficients and allocation proxies do not reconstruct ecosystem or catch composition changes through 1950–2019.

The recommendation is to retain this as candidate evidence and resolve the consequential source conflicts and native-flow translation limits before considering regional adoption. [Final verification](qa/final_verification.json) and the [package inventory](evidence_index.json) document arithmetic, links, rendering and preservation. Active LME_013.xlsx, selected-model documents, existing model files, Project.xlsx, map, trends, archive and knowledge graph are preserved. Work stops for researcher review.
