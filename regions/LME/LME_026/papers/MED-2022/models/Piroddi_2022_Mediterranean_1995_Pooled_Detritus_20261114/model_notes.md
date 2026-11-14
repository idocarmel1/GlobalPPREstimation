# Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114

## Source identity

This is a separate, explicitly authorized derived model of the [canonical 71-group model](../Piroddi_2022_Mediterranean_1995/model.json), SHA-256 `f038707bf7837962933eec3e6daeae53eb0b9a7f48837763b0ce621edcdc3a9e`. The original model and its review remain unchanged. The original source is Piroddi et al. (2022), Mediterranean Sea baseline for 1995 (supplement label: 1990s). Source values and exact aggregation changes are retained in the [aggregation ledger](results/diagnostics/pooled_20261114/aggregation_ledger.json).

## Modeled period and area

The source baseline remains 1995, basin-wide Mediterranean Sea; the source dynamic simulation period is 1995–2016. Pooling does not change geographic or temporal coverage. The derived model has 69 unchanged non-detrital groups and one nonliving pooled compartment.

## Departures from the publication

- Source group 70 Discards and group 71 Detritus become group 70 **Pooled Discards and Detritus**. Biomass and biomass_habitat_area are summed in their common t/km² basis: 0.07582324 + 0.44 = **0.51582324**.
- Each feeding consumer retains its original diet entries for prey 1–69 and its diet-import value. Published prey-70 and prey-71 proportions are summed exactly, without normalization. Unknown nonfeeding diet proportions remain unknown. Living-group parameters, source strings and fisheries values are preserved.
- The source does not report detritus routing. On 14 November 2026 the researcher explicitly authorized **100% of detritus-directed flows to pooled group 70**, including its own routing. This is a calculation assumption, not a recovered source value. The runtime EE-floor external nonfishery sink remains separate and must not be redirected into this pool.
- The two published detrital EE values, 0.4894103 and 0.03464372, cannot be averaged into a justified pooled EE. The canonical pooled EE remains unknown (`-9999`, input flag false); source values remain in the ledger. Shared TL=1 and pp=2 are retained. BA, imports, exports and other unknown inputs remain unknown.
- Both detrital groups lack source landings; the pooled source landings remain missing. Their 37 fleet-discard values are explicit zeros and sum to zero. Living fishery-discard quantities remain unchanged. No discard return is added by this builder; a runtime return to the single pool must occur exactly once.
- Any authorized runtime EE adjustment to `1 - M0_to_detritus / P` must retain the source living EE values here and document its before/after values and the separate external sink in runtime evidence. This builder does not calculate or change runtime EE.
- The inherited administrative `selected=false` and `production_eligible=false` fields are removed from scientific JSON and retained in [input provenance](inputs/provenance.json). This is a distinct model with no inherited researcher decision, exclusions, selection or numerical eligibility.

Pooling preserves the documented aggregate diet and biomass quantities, but it is not evidence that the two original compartments have equivalent dynamics or that their unpublished routing has been recovered. Source balance conflicts and missing inputs remain relevant. The original diagnostics do not establish this variant's diagnostic outcome.

## Evidence links

- [Original model notes](../Piroddi_2022_Mediterranean_1995/model_notes.md)
- [Original parameter and diet workbook](../../sources/41598_2022_18017_MOESM1_ESM-75e4d6d3.xlsx)
- [Input provenance](inputs/provenance.json)
- [Complete aggregation, crosswalk and missingness ledger](results/diagnostics/pooled_20261114/aggregation_ledger.json)
- [Reproducible canonical builder](results/diagnostics/pooled_20261114/code/build_pooled_model.py)

The canonical builder performs no solver run, selection, regional arithmetic, researcher registration or publication. Diagnostic evidence produced separately applies only to its explicitly recorded configuration.

## Current experimental diagnostics

The separate [diagnostic summary](results/diagnostics/pooled_20261114/diagnostic_summary.md) records the authorized 100% pooled-routing run with EE floor ON at 0.1. GE, TE and With Egestion returned finite numerical coefficients and overall **FAIL** grades. All living EE/M0 identities and exactly-once discard routing checks passed; source-budget discrepancies and the calculated detritus stock residual remain explicit. Full method returns, matrices, settings and independent verification are linked from that summary. This experiment remains unselected and has no registered researcher approval.
