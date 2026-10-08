# Expanded discard-routing experiment: methods and findings

Exactly **20 additional distinct real marine model JSONs** passed the numerical and amended source-fidelity eligibility checks. Four original models were extended as a separate reference cohort and are excluded from the addition count. Sea of Okhotsk NE remains a zero-native-harvest null control. No paper extraction, parameter recovery, annual reconstruction, SAU mapping or production-atlas export was performed.

## Design and limits

Each source model retains its original living harvest H. Every integer percentage from 0% through 20%, plus 25%, 30%, 40%, 50%, 75% and 100%, is an exact solved fraction f. Designated D=fH is reclassified through SC (remains catch), SM (catch becomes L=(1−f)H; M0 gains D; EE falls D/P) or SE (catch becomes L, separate external loss gains D). Only the original Humboldt reference has supported SR destination information. Other SR cases remain explicitly unavailable.
Living physiology, diet, predation, original accumulation and migration are held fixed. The dependent detritus accumulation absorbs changed inflows at fixed predation; returned material is not assumed to become additional consumption. This is a constrained accounting sensitivity, not a fitted Ecopath dynamics forecast.
All selected additional metadata use the WetWeight currency enum. Those records do not explicitly state the mass/area/time normalization. PPR is therefore reported as native wet-weight production equivalent /9; unknown normalization is not relabeled tonnes per square kilometre per year. Relative coefficient responses and native ratios use matching within-model units. Absolute native PPR is never pooled across models. The /9 factor preserves the original assumed carbon convention. All-source ratios are unavailable with positive imported support and an internal-only PP denominator.

## Selection and numerical eligibility

Candidate order was fixed before sensitivity directions: EwE_jsons first, geographical metadata strata in round-robin order, then ecosystem type, structural group-size bin and numeric model identifier. The original reference inputs, canonical ecological duplicates, toy/broken and nonmarine models, and incompatible currencies were excluded. All 252 JSON files were inventoried. Twenty passed after assessing the first 52 queued candidates. Remaining candidates are explicitly untested after the count was met, not presumed valid. The 99-group Albatross Bay baseline exceeded the 180-second resource guard and is unassessed, not scientifically invalid.
Eligibility requires compatible finite source inputs, positive living harvest, primary producers and detritus, admissible EE/diet/fates, no material invented living accumulation, physical closure and at least one usable recycling method. Diet normalization is allowed only within a raw row-sum deviation of 0.001; every change is logged. Physical residuals allow 1e−4 group-relative living/consumption/whole-system rounding and 1e−7 absolute constructed detritus closure. Source changes beyond 1e−4 of a supplied biological parameter reject a candidate. Recycling methods also require finite nonnegative coefficients, spectral radii below 1, and their frozen PP-equivalent identity gap at most 5%. These checks do not validate ecological realism.

The source-fidelity amendment followed an input audit of the provisional set, after its scenario runs, and did not use sensitivity direction or magnitude. It rejects nonzero documented detritus onward fates overwritten by the frozen loader and unsupplied negative baseline detritus accumulation used to finance consumption. Santa Pola Bay (explicitly a marine fish farm) and Western Channel overwrite nonzero source routes; Moreton Bay and Western Bering Sea require unobserved detritus stock draw. All four provisional runs remain under results/excluded_provisional_models and do not enter valid aggregate distributions. They were replaced by South Benguela, Lagoon Chiku, Independence Bay and Northern Gulf of St Lawrence using the unchanged queue.
Detritus fate classifications among the final additions: {'zero_row_identity_bookkeeping': 19, 'unchanged': 1}. Zero source rows changed to identity are disclosed as bookkeeping representation changes: detritus M0/egestion is zero, so no nonzero onward source flow is erased. Scenario detritus accumulation remains a dependent residual; that modeling convention is not claimed to be an observed source accumulation.
The 20 model/time cases represent 18 named ecosystems. Central Atlantic (1950/1990) and North Atlantic (1950/1997) are dependent temporal observations. Their separate cases describe model response diversity and do not constitute independent ecosystem replicates. No global-population inference is made.

## Findings on the fixed original H

| Method, SM | Fraction | Paired models | Median coefficient change | Min–max change |
|---|---:|---:|---:|---:|
| new_GE | 20% | 20/20 | +0.9628% | +0.0001% to +20.9640% |
| new_GE | 50% | 20/20 | +2.4422% | +0.0003% to +75.9963% |
| new_TE_EEfix | 20% | 18/20 | +24.9853% | +0.0244% to +25.0000% |
| new_TE_EEfix | 50% | 18/20 | +99.9362% | +0.0611% to +100.0000% |
| new_WithEgestion | 20% | 20/20 | +0.2522% | +0.0001% to +18.0439% |
| new_WithEgestion | 50% | 20/20 | +0.6329% | +0.0002% to +61.5441% |
| Ulanowicz_TE | 20% | 20/20 | +18.8469% | +0.0243% to +25.0000% |
| Ulanowicz_TE | 50% | 20/20 | +67.7685% | +0.0607% to +100.0000% |
| SPPR_1995_TEmean | 20% | 20/20 | +16.0142% | +0.0271% to +68.6679% |
| SPPR_1995_TEmean | 50% | 20/20 | +47.3967% | +0.0678% to +372.7741% |

These are descriptive pointwise model distributions, not confidence intervals. The HTML separately offers the same-model support across all 27 fractions, so invalid high-discard scenarios cannot silently change a response curve’s donor population.
At 20% under SM, the fixed standard exceeds new_GE in 5 of 20 cases and is below it in 15; against new_WithEgestion the signs split 12 versus 8. Standard overestimation is therefore not universal and depends on the recycling formulation. The GE coefficient median rises 0.9628%, while the retained-catch footprint median falls 19.2298%. By contrast, the TE_EEfix coefficient increase is often close to 25%, nearly canceling a 20% retained-catch reduction. In Prince William Sound, the TEmean coefficient rises 68.6679%, giving a 34.9343% increase in the retained-catch footprint despite the 20% lower retained amount. These are exact uniform-reclassification algebra on the original H, not a forecast of changing ecosystem biomass.
SC is invariant under fraction relabeling. SC and SE have the same coefficients below 100% under uniform reclassification. At 100%, normalized catch weights vanish: TEmean uses a biomass fallback and SPPR_1986 is undefined. The fixed baseline-TL TE=0.1 standard is invariant by definition; its signed excess or deficit against recycling methods can still be substantial. Positive and negative standard discrepancies are reported, without assuming universal overestimation.
Some finite 100% flow-method coefficients are extremely large (including TE_EEfix and Ulanowicz), where remaining removal approaches zero and source rounding can dominate. Their finite/convergent status does not establish conditioning or ecological robustness. These explicitly labeled stress endpoints should not be interpreted as realistic discard-effect magnitudes. Exact values and invalid masks remain exposed; zero retained L is not evidence that the underlying coefficient is reliable.
The 0–20% grid contains **0 method/scope/route validity transitions** across adjacent solved points. The exact brackets and reasons are in `results/low_fraction_validity_boundaries.csv`. Curvature is measured by second differences of the coefficient-response percentage at adjacent one-percentage-point increments; it is not a confidence or error bound.

Largest fully supported low-range curvature: 2_2_Alaska,_Prince_William_Sound_(1980) / SPPR_1995_TEmean, second difference 0.180611 response percentage points near f=0.19. Its change at 20% is +68.6679%. No uncomputed point is presented as solved.

## Verification and deliverables

The final output audit checks 62,784 scenario records and 999,500 coefficient rows. It covers immutable input/engine hashes, zero-fraction identity, SC invariance, SC/SE equivalence, fixed harvest support, exact designated amounts, living production residual preservation, SM EE adjustment, no double-counted return, separate external loss without migration, finite/convergent/nonnegative validity, missing-data propagation, native denominator boundaries and decomposition reconciliation. Original overlap comparisons cover all 3,936 old records. Maximum absolute decomposition residual is 2.9036323e-06 native units.
Baseline comparisons: 486 strict matches, 16 unavailable, 49 strict differences. Of those differences, 49 are reproduced by replaying the existing workbook with unnormalized raw diet rows. The experiment retains the original study's normalize_DC=True, restricted to documented rounding tolerance. No tolerance is loosened. Provenance counts: {'fresh_unmodified_vs_adapter': 192, 'existing_saved_workbook': 359}. Saved workbooks were snapshotted only after selection; no production export was run.
`report.html` embeds compact verified data, scripts and assets. `results/ecosystem_ppr.csv`, `group_sppr.csv`, `effect_decomposition.csv`, `scenario_envelopes.csv`, `aggregate_distributions.csv` and `standard_method_comparison.json` provide machine-readable results. Per-model `study.validated.json`, `flow_ledger.csv`, `parameter_changes.csv` and diagnostics retain full numerical provenance. `results/discard_responses.v2.json` is a proposed exact-model group-coefficient interface, not an installed atlas uncertainty layer.

## Selected model catalog

| Existing model | Groups | Metadata ecosystem type |
|---|---:|---|
| 429_429_Sørfjord_(1993) | 25 | bay/fjord |
| 153_153_Tampa_Bay_(1950) | 52 | bay/fjord |
| 28_28_Central_Atlantic_(1950) | 38 | open ocean |
| 111_111_North_Atlantic_(1950) | 38 | open ocean |
| 115_115_Northern_Benguela_(1956) | 32 | upwelling |
| 663_663_South_Shetlands_(1990) | 30 | open ocean |
| 464_464_Germany,_Schlei_Fjord_(1980) | 10 | bay/fjord |
| 496_496_Eritrea_(1998) | 19 | coral reef |
| 266_266_Kuosheng_Bay_(1998) | 17 | bay/fjord |
| 2_2_Alaska,_Prince_William_Sound_(1980) | 19 | bay/fjord |
| 436_436_Western_Tropical_Pacific_Ocean_(1990) | 20 | open ocean |
| 489_489_Sechura_Bay_(1996) | 21 | bay/fjord |
| 756_756_Western_Antarctic_Peninsula_(1996) | 35 | Continental shelf |
| 446_446_Hudson_Bay_(1970) | 40 | bay/fjord |
| 29_29_Central_Atlantic_(1990) | 38 | open ocean |
| 112_112_North_Atlantic_(1997) | 38 | open ocean |
| 485_485_South_Benguela_(1978) | 32 | upwelling |
| 267_267_Lagoon_Chiku_-_Taiwan_(1997) | 13 | coastal lagoon |
| 490_490_Independence_Bay_(1996) | 20 | bay/fjord |
| 462_462_Northern_Gulf_of_St_Lawrence_(1990) | 32 | channel/strait |
