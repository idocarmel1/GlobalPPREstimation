# Proposed response interface v2

`results/discard_responses.v2.json` is an isolated, versioned response artifact.
It has **not** been copied into PPRAtlas or any production uncertainty layer.

Each `response_models[]` identifies the cohort, exact source JSON and saved-workbook
SHA-256, canonical ecological hash where available, immutable group IDs/names and
native H. Every method/scope package supplies baseline validity and coefficients,
then route-specific exact fraction points with coefficients, validity, status,
reasons and catch-weight mode. Invalid coefficients remain auditable but must never
be applied as valid. Zero-source-harvest reference models are explicitly unassessed.

The proposed consumer contract is:

1. Match an exact tested source model and immutable group identities. Confirm native
   currency/scope compatibility. A similarly named LME is not an exact model match.
2. Preserve the same actual retained-landings vector and taxon-to-group mapping
   weights across scenario comparisons. Multiply by the selected coefficient
   vector, then apply the existing `/9` carbon convention. No yearly Ecopath refit.
3. Use observed regional exposure `D/(L+D)`, not `D/L`. Report it separately from the
   hypothetical fraction experiment. New mappings or extrapolation require a
   separately reviewed applicability rule.
4. Prefer exact solved fractions. `eligible_adjacent_intervals` identifies paired
   valid grid neighbors for a later explicitly labeled interpolation policy; no
   interpolation may cross invalid points or TEmean/1986 endpoint weight changes.
   A paired baseline effect requires a valid baseline and valid compared endpoints;
   a method that becomes usable only after perturbation has no valid baseline ratio.
5. Hold the selected annual NPP denominator fixed for every compared endpoint. The
   main task's selected/global denominator choice must be part of the evaluation
   key, together with year, source method, taxon setting and catch boundary.
6. Keep the central estimate landings-only. A discard-routing min/max envelope on
   those same landings is a sensitivity range, not a statistical confidence interval.
   Preserve donor/model counts and missing support. No unsupported case becomes zero.
7. Distinguish within-method routing sensitivity from signed fixed-standard versus
   recycling-method discrepancy. A fixed-TL standard's invariance is by construction
   and is not evidence that ecological recycling-model discrepancy vanishes.

Suggested cache identity is `(response schema/study version, source model hash,
method, scope, route, fraction, exact-or-interpolated status, catch-data hash,
mapping hash, retained-landings boundary, year, NPP method, selected/global
denominator option, NPP-data hash)`. The same denominator applies to both endpoints;
NPP uncertainty is a separate issue.

Pooled summaries in this experiment describe the 20 selected cases only. They do
not authorize a global uncertainty proxy or replace the main task's native NPP
work. A later consumer should default to **not assessed** when exact source/model
support is absent. Integration can copy this immutable response file only after
ownership coordination, with its hash and schema version retained in provenance.
