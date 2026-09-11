# Landings central estimate and discard-routing sensitivity

**Latest display instruction:** retain selectable all-catch and discards-only
PPR views without a sensitivity band, and make the landings-view sensitivity
optional. Catch basis and band visibility are separate controls, preserved in
links and downloads. All three numerators are computed from their own taxon
vectors; the default remains landings. “Discards only” means the discarded
component alone; “Landings only” means retained catch excluding discards.

The authorized production change evaluates the existing verified SPPR coefficients
on **reported plus unreported retained landings**, taxon by taxon. Total catch and
discards remain separate accounting fields. Source workbooks retain their original
combined-catch calculations as reproducible coefficient/source audits; they must
not be described as downloads of the revised landings headline.

The annual NPP extraction completed all supported years. The coordinated map
and graph exports now use its verified complete canonical data. Neither the experimental calculator nor
experimental source-model variants enter the production calculation engine.

## Versioned response contract

`results/discard_responses.v1.json` identifies the study version, model, original
model JSON SHA-256, upstream coefficient-workbook SHA-256, method, source scope,
baseline group coefficients and group identities. Each route contains computed
fraction points with validity, reasons, evidence class, catch-weight behavior and
explicit valid adjacent interpolation intervals. The catch convention is the same
actual landed vector for every route, with carbon conversion once at 1/9.

Production must reject a mismatching source hash, invalid baseline or incompatible
method/scope, and retain existing source-workbook plausibility/failure exclusions.
A numerically solved research scenario does not automatically remove a production
quality flag. It must verify that the baseline group coefficients, combined with
the exact persisted **Final mappings** weights, reproduce the production taxon
coefficients. Mapping weights stay fixed across scenarios. Changing those weights
is a separate experiment and must not happen implicitly during a response lookup.

For each ecosystem and year, use the observed `f = D / (L + D)`. Use full regional
catch to define exposure and also disclose covered landings and the covered catch
fraction. A uniform native-model discard allocation at this observed regional
fraction is a transfer assumption, not a group-specific reconstruction.

Evaluate perturbed coefficients on the same taxa supported by the central landed
estimate. Every positive supported landed amount must have a valid scenario
coefficient; missing scenario support invalidates that route rather than shrinking
the taxon set. The zero and reference-TL unidentified-taxon treatments preserve
their current meanings, including the all-sources-only reference-TL restriction.

Linear interpolation applies separately to group coefficients only between
explicitly permitted adjacent valid points. No extrapolation, interpolation across
invalid/missing samples, or bridging a catch-weight fallback at 100% is allowed.
Report whether the evaluation uses an exact computed fraction or interpolation.

The minimum and maximum across at least two valid named routes define the
**discard-routing sensitivity envelope**. Include excluded route names and reasons.
This is neither a confidence interval nor an estimate of all ecological uncertainty.
Do not add discarded-catch PPR to an endpoint. Divide both endpoints by the same
selected annual NPP; its ensemble spread remains a separate uncertainty source.

## Display and aggregation rules

- Map color and central detail value: **PPR from landings**, or that numerator
  divided by the selected annual NPP. Show the supported range, regional discard
  fraction, source model and validity next to it.
- Linked annual graphs and CSV downloads use the same landings definition,
  selected model/method/scope, unidentified treatment and NPP policy.
- For multiple ecosystems, shade a range only when every included ecosystem has
  compatible assessed bounds in that year. Sum corresponding named routes where
  possible; do not let unsupported ecosystems silently disappear from the band.
- Missing annual NPP suppresses ratio bounds but need not suppress PPR bounds.
- Known zero landings give zero central PPR for a valid supported method. A missing
  selected component is unavailable; a known component remains usable even when
  another component is unknown. No total catch means the discard fraction is
  undefined. D=0 is a zero perturbation, not evidence of zero ecological uncertainty.
- External taxon-TL simple-chain estimates have no measured routing uncertainty;
  label the range **not assessed / invariant benchmark**, rather than zero error.
- Okhotsk has no native harvest available for the experiment and supports no
  regional routing envelope. Untested models remain **not assessed**. No pooled
  cross-model proxy is introduced.

## Verification and reproducibility

Keep source-workbook total-catch validation as a separate check. Independently
verify new annual landings totals from source taxon catches, coefficient identities,
classification identities, response hashes and matching map/graph numbers. Test
different landed/discarded taxonomic composition, zero boundaries, missing NPP,
unavailable methods/scopes, unidentified treatments, invalid interpolation gaps,
out-of-range fractions, mismatching hashes and invariant reference methods.

The frozen Bay of Bengal 2019 model-TL reference changes from approximately 43.71%
to 42.26% PPR/NPP through the catch-boundary change alone. This is a regression
reference, not a global scaling factor. Final published values use the current
verified annual NPP export and document any legitimate denominator changes.

Future extensions require additional evidence: group-specific discard allocation,
post-release survival, source-supported return fates for Bay/Guinea, a recovered
Okhotsk model catch vector, and repaired/revalidated Humboldt recycling methods.
None should be replaced with an unlabeled global uncertainty percentage.
