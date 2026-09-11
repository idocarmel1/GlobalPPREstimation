# Discard routing changes coefficients as well as the catch boundary

The completed experiment distinguishes two effects: evaluating PPR on retained
landings removes discarded biomass from the numerator; changing how those discards
move through a food web can also change SPPR. These effects must not be combined
by adding discarded-catch PPR to an uncertainty endpoint.

Results are available in [the interactive report](report.html),
[ecosystem calculations](results/ecosystem_ppr.csv),
[group coefficients](results/group_sppr.csv),
[flow ledgers](results/flow_ledger.csv) and
[paired decomposition](results/effect_decomposition.csv). Machine-readable results
and assumptions are in [study.json](results/study.json). Every native quantity below
is per square kilometre per year, rather than an annual regional total.

## Main numerical findings

The table uses the same original modeled harvest H in every calculation, all basal
sources, and designates 10% of H as discards. SC leaves that amount in combined
fishery catch; SM removes it from fishery catch and routes it through other
mortality. Both use the original H only as an evaluation vector.

| Source model | Method | SC PPR | SM PPR | Interpretation |
|---|---|---:|---:|---|
| Bay of Bengal 1978 | Gross efficiency recycling | 132.936577 | 140.020895 | Coefficients increase PPR; dropping discards from evaluation is a separate effect |
| Bay of Bengal 1978 | Transfer efficiency recycling | 223.485732 | 248.401199 | Response differs substantially by method |
| Guinea 1998 | Gross efficiency recycling | 127.116320 | 129.542812 | Positive response, smaller than the Bay comparison |
| Guinea 1998 | Transfer efficiency recycling | 378.280448 | 420.309436 | The method response is much larger than the GE response |
| Northern Humboldt 1995–1998 | Ulanowicz TE reference | 676.712793 | 741.367630 | Cycle-pruned methodological reference; not an exact recycling-budget estimator |

PPR units: **t carbon-equivalent primary production km⁻² yr⁻¹**, using the retained
project conversion of wet biomass equivalents divided by 9. Native producer
production divided by 9 supplies the report's native denominator. It is explicitly
separate from satellite NPP and from the 2019 external application.
When the all-source numerator includes imported production, the native internal-PP
ratio is unavailable because those boundaries do not match. PPR remains available;
compatible internal-source comparisons retain their named denominator.

SC is invariant across designated fractions because its physical source model is
unchanged. SE preserves the same external physical removal while separating fishery
weights from another external sink; the displayed fixed-production comparisons
therefore commonly coincide with SC. Uniformly scaling normalized fishery weights
does not change their mean while some fishery catch remains. At 100%, methods may
switch to biomass weights or become undefined; those endpoints are not connected
as a smooth ecological response.

The fixed baseline group-TL reference is **not consistently higher** than recycling
methods. For Bay at 10% SM, its signed difference is −47.3438% relative to GE and
−70.3183% relative to the transfer-efficiency calculation. Against the Bay Ulanowicz
reference it is +16.3211%. These are differences from specified scenarios, not
established real-world bias. A total-only trophic-chain reference has no invented
internal-source or primary-producer decomposition.

## Experimental design and closure

Four immutable imported models use the fraction grid 0, 1, 5, 10, 20, 30, 40, 50,
75 and 100%. The last two are stress tests. H is each model's existing living-group
harvest, D=fH and L=(1−f)H. No annual historical source models are fitted, and regional
annual tonnes are never inserted into a source expressed in t/km²/year.

S0 reproduces the saved converted pipeline, including its documented normalization
and inferred missing parameters. The preserved source files are untouched; the
completed baseline is not represented as an unchanged published steady-state fit.
The frozen runner's settings and exact source revision are recorded in
[baseline invocation provenance](verification/baseline_invocation_source.json).

Each scenario freezes completed living production, consumption, diet, predation,
biomass accumulation and migration. The ledger keeps fishery catch, distinct
external loss and returned material separate:

- **SC:** all H remains fishery catch, with no new internal return credited.
- **SM:** fishery catch becomes L; M0 increases by D; EE becomes 1−M0/P. This is
  an accounting proxy, not a claim that fishing mortality is natural mortality.
- **SE:** fishery catch becomes L and a distinct external sink receives D. M0 and
  EE remain at baseline. No fabricated migration term closes the budget.
- **SR:** fishery mortality remains H, with designated D returned through a
  documented source pathway. The internally returned amount is removed from net
  external export exactly once. Only Humboldt has a supported destination here.

Detritus production/inflow changes with routing; its residual accumulation is solved
while detritus predation stays fixed. Extra return is **not assumed to be entirely
reconsumed**. Negative living accumulation already inferred during baseline loading
is disclosed. This constrained accounting experiment does not validate a new
ecological equilibrium, dynamic fishery response or survival assumption.

The primary result multiplies each perturbed coefficient by the same H. A separate
result uses L. The decomposition is:

`coefficient effect = H × (a1−a0) / 9`

`catch effect = (L−H) × a0 / 9`

`interaction = (L−H) × (a1−a0) / 9`

Their sum equals `L × a1 / 9 − H × a0 / 9`, summed across the same supported groups.
Missing coefficients never become zero or silently change the comparison cohort.

## Source evidence and limits

Full primary-source page/cell citations, hashes and rendered evidence are in
[the source audit](results/source_evidence.md).

- **Humboldt:** the original supplement records D/H=3.996307735%, with fleet
  discards going to Fishery offal and onward 10% to pelagic / 90% to benthic
  detritus. The direct offal diet row has no consumers. The converted loader drops
  fleet returns and forces detritus-to-detritus fates to identity. SR restores the
  designated source-supported route with an explicit offal transfer ledger; the
  hypothetical fraction does not become an observed source fact. No separate
  processing-offal amount is invented. See [Chiaverano et al. (2018)](https://doi.org/10.1016/j.pocean.2018.04.009).
- **Bay:** the original 1978 catch explicitly combines landings and discards;
  their source split and fleet return destination are unresolved. SM uses the
  source biological detritus route as a proxy. SR is unavailable. The report's
  6,205,000 km² domain also differs from treating an atlas polygon as identical.
  See [Guénette's BOBLME report](https://www.boblme.org/documentRepository/Bengal%20report%2028april2014.pdf),
  catch discussion p. 9 and Appendix A2.1 p. 46 of the frozen recovered copy.
- **Guinea:** Table 16 contains published assumed discards, but no verified fleet
  destination. An assumption stated as 30% of industrial landings is D/L, not
  D/(L+D), and does not apply uniformly to all harvest. The raw detritus export
  1670.48071 is excluded from H. Source area extends beyond Guinea's EEZ and is
  not the whole Guinea Current LME. See the [2004 compilation](https://www.seaaroundus.org/doc/publications/books-and-reports/2004/Palomares-et-al-west-africa-ecosystems.pdf),
  printed pp. 124–159, especially pp. 149 and 153.
- **Okhotsk:** the frozen harvest vector is zero. Its fH experiments are degenerate
  mathematical controls and provide **no regional discard-routing envelope**. NE
  labels the source Ecopath variant; it does not establish a northeastern subregion.
  The chapter describes the whole Sea during the 1980s. See [Chaikina's chapter](https://epic.awi.de/id/eprint/52730/1/Palomares20_FishCentResaRep28.pdf),
  printed pp. 23–34. Recovering original group catches requires additional evidence.

Humboldt GE/egestion methods already diverge or yield negative coefficients in the
saved baseline. Its transfer-efficiency method converges but misses its own
PP-equivalent export identity by about 14.22%, beyond the frozen diagnostic's 5%
failure threshold. These failures remain visible and are excluded from production
envelopes. Physical biomass-ledger closure, numerical convergence, method-specific
conservation and source validity are separate flags. The Ulanowicz cycle-pruned
reference is not required to satisfy the recycling identity it does not claim.

Production retains its existing source-workbook quality gates in addition to the
research checks. Guinea's transfer-efficiency all/inner scopes remain flagged by
the source workbook as implausibly large relative to the trophic-chain reference,
although their private accounting scenarios solve. Its PP scope remains eligible.
Thus compatible production response coverage is 14 method/scope combinations for
Bay, 12 for Guinea, 5 for Humboldt and none for Okhotsk; these are not global bounds.

The private SR donor-return equation is implemented for GE/egestion. SR is
unavailable for `new_TE_EEfix` at positive fractions because its frozen direct-PP
detritus scaling cannot represent that donor ancestry. Substituting SM under the
SR label would conceal a different equation and has not been done.

## Separate 2019 catch-boundary control

The independently reproduced [2019 reference audit](results/external_reference_audit.csv)
holds coefficients and NPP fixed and sums taxon-level landings/discards separately.
For the Bay model-TL method, total-catch PPR/NPP is about 43.71%; landings-only
PPR/NPP is **42.2575%**. Discards are 3.6664% of catch but 3.3186% of its PPR.
Different taxonomic composition explains why a regional catch percentage cannot
replace taxon-level evaluation. This panel measures the direct boundary effect,
not coefficient recycling sensitivity, and is independent of the native fraction
selector.

## Reporting protocol

1. Report annual **PPR from landings** as the default estimate, with selected
   model, method, source scope, catch year, unidentified-taxon treatment, unit
   conversion and coverage. Preserve landings, discards and total catch separately.
   The owner's additional all-catch and discards-only display options evaluate
   those taxon vectors without a routing envelope. The landings-view envelope can
   be shown or hidden independently.
2. Record source-period catch/discard semantics, the origin of assumed fractions,
   return destinations, source domain and conversion limitations per model.
3. Apply only compatible tested response coefficients to the same actual landed
   vector, using observed annual D/(L+D), fixed mappings and valid interpolation.
   Report named included/excluded routes and a **discard-routing sensitivity
   envelope**, not a confidence interval. Unsupported cases remain not assessed.
4. Hold the selected annual NPP fixed across that comparison. Keep satellite
   model spread, unobserved years, parameter uncertainty, mapping uncertainty and
   survival/destination uncertainty separate. An earliest-year NPP proxy remains
   explicitly optional and labeled; it does not generate observations.
5. Prioritize recovering Okhotsk source catches and source-supported Bay/Guinea
   return fates, then resolving Humboldt source conversion and recycling failures.
   Broader parameter studies require independent source justification.

The production contract, aggregation rules and remaining extensions are specified
in [INTEGRATION_PROPOSAL.md](INTEGRATION_PROPOSAL.md). No experimental calculator
changes replace the live calculator.
