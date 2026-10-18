# Process and decisions

## Request and scope

On 16 October 2026, the researcher requested an exact reconstruction of the preceding TE taxon-resolution analysis for GE, with results and process documented under `research`. This is a researcher-owned method comparison under `research/human/ppr_taxonomic_resolution_GE_20261016`.

The original TE study and original trophic-level experiment remain unchanged source packages. Scientific model inputs, selected models, workbooks, review decisions, catch mappings and published HTML are inputs, not edit targets. Pre-existing workspace changes are preserved.

## Replication design

1. Read the project README and current agent contract. Query the canonical knowledge graph only as an index; its October 8 snapshot does not certify October 16 results.
2. Reuse the TE pipeline structure and verify the GE definition against the project explainers and calculator. Select saved `new_GE` coefficients and `method='GE'` experiment records.
3. Retain identical 2019 catch support, eight default selected reviewed models, `all` scope, unidentified treatment `method`, review exclusions, original allocation shares, taxon TLs and operative group TLs. Do not renormalize omitted allocation shares.
4. Check positivity and missingness for GE independently. The original experiment supplies 261 positive GE consumer coefficients; its TE version supplied 260 positive coefficients and one zero. A GE logarithmic fit therefore includes that additional positive record when the sample definition permits it.
5. Fit the same sample/weight combinations: all consumers, review-included consumers, fished groups, catch weights and PPR weights. Retain pooled, within-ecosystem and between-ecosystem descriptions; use pooled/within slopes in the transported scenarios.
6. Apply the same anchored prediction, `s_ig = S_g × 10^[b(T_i − T_g)]`, with GE anchors and GE-fitted slopes. Calculate mean-shift, centered Jensen and full totals directly over actual allocations.
7. Compare the twelve scenarios to the GE baseline, grouped classic, taxon simple chain and corresponding TE scenarios. Retain eighty leave-one-ecosystem-out fits and dominant group/region contributions.
8. Independently verify sums and regression slopes, source hashes, identical TE/GE catch and TL support, document links and figure readability. A method review separately checks GE-specific interpretation and preserved restrictions.

## Interpretation

This replicates a saved-data statistical projection. It does not construct or solve a taxon-level food web. The relationship fitted between functional groups is assumed to apply within groups, with each group's multiplicative residual retained. Scenario and leave-one-model-out ranges measure sensitivity, not uncertainty intervals for biological truth. The project-specific GE and TE methods differ in both consumer efficiency and detritus accounting.

## Results and preserved evidence

The GE baseline is 2,026,099,644.7056048 tC. The review-included within-ecosystem fit has slope 0.9712867008699299 and predicts 2,628,814,715.84789 tC, a factor of 1.2974755327149077. The catch-weighted fit predicts 2,464,810,537.0629296 tC; the all-consumer within-ecosystem fit predicts 2,907,290,460.3626666 tC. All twelve scenarios, fifteen descriptive regressions and eighty leave-one-ecosystem-out fits completed.

The additional GE-positive observation is Eastern Tropical Pacific Toothed whales, which has zero TE SPPR and is excluded by the review defaults. Thus the GE all-consumer calibration contains 261 records, but the review-included calibration remains at 241 and the catch-bearing sample at 200. No missing or nonpositive GE consumer coefficient required a repair or invented replacement.

GE and TE have identical per-group mean-shift and Jensen factors when the same fixed slope is used. Their aggregate corrections differ because GE and TE assign different baseline PPR weights to groups. Method-specific fitted slopes introduce an additional difference. The comparison output explicitly separates fixed-slope and refitted scenarios.

The method audit confirmed GE production weighting, coupled detritus recycling and indirect EE-floor effects. Guinea's GE diagnostic is OK and its annual status is `ok`; the TE implausibility narrative was not copied. Northern Humboldt's GE diagnostic remains FAIL. Its current saved configuration uses `auto` and returns pooled detritus scaling, while the retained annual prose mentions historical `always`; these are reported with their distinct roles. Positive finite coefficients were not treated as proof of convergent recycling or production eligibility.

## Verification

The main script reconciles all 261 source GE coefficients and operative classic TL coefficients with the current published HTML, matches the previous catch/TL support, and verifies the direct allocation sum against mean-shift × Jensen factorization in every scenario. It verifies source identities before and after analysis.

The separate [independent verifier](../code/verify_independent.py) reads the current HTML directly, without importing the analysis module. It independently sums all twelve scenarios and fits ten pooled/within regression slopes using weighted design matrices. It also checks catch, mean taxon TL and operative group TL against the original TE output for all 200 groups.

All **662 numerical checks passed**, with maximum relative disagreement **5.49 × 10^-15**. All **44 source hashes matched**. Local report/README/process links are checked by the verifier. Both PNG figures were visually inspected for readable labels, clipping and agreement with numeric results; SVG companions were also generated. The baseline is explicitly labeled reconstructed, and the PPR-weighted stress test has grey hatched styling.

The analysis used the existing FishEstimation Python environment; the independent verifier used the bundled Python runtime. No packages were installed, no scientific solver was invoked, and no scientific source or original study was edited. Outputs are limited to this study and its entry in the research index. Runtime and code identities are retained in the verification records.

A final independent method review checked headline totals and ratios, slope/sample definitions, the local production-weighted aggregation argument, GE/TE distinctions, and diagnostic qualifications against saved evidence. It identified no further corrections. This review checks the analysis and its stated limits; it does not validate the hypothesized taxon-level response.
