# Okhotsk Sea pelagic carbon reconstruction, 2000–2014

This is an authorized scientific assumption model derived from Gorbatenko and
Melnikov (2019), Figure 9 and Table 3, primary feeding prose, and the recovered
2018 dissertation feeding tables. It is not an author-confirmed Ecopath export.
Original article, extraction, and accepted human Figure readings remain intact.

The exact [native model](../../model.json), SHA-256
`9beff5a4e525dcf4253bf83472253c7a4a9f7e7db10379ecef64eb33cd32a656`,
loads with the unmodified PPRCalculator and passes its actual main balance check.
[Final verification](final_verification.json) also checks finite physical flows,
the standard EE/GS bounds, 22 biological groups and the native external-food
helper, zero catch and migration, and complete mortality/egestion routing.

## Scientific choices

Native stocks and annual flows are tonnes carbon per km²; rates are per year.
The implied Table 3 area is 1,544,000 km². Absolute food ledgers use million wet
tonnes or million tonnes carbon per year. This implied denominator is not a
measured geographic overlap. Wet food is converted by each prey's factor.

Figure production is preserved for all 21 living groups. Source wet stocks and
body factors determine carbon stocks; P/B is derived from those stocks and the
rounded Figure production. Bacteria and protozoa share the pooled source P/B of
20, with a production-proportional carbon stock split. Protozoa's factor 10 is
an explicitly authorized estimate. The resulting microbial carbon stock is
6.81 million tonnes versus the rounded source 6.8; its wet equivalent is
65.067 million tonnes versus the source pooled 64. This difference and the small
copepod pooled-food split adjustment are recorded in
[microbial consistency](microbial_split_consistency.json).

The completed food inputs preserve quantitative source totals and partial
fractions. Missing components remain explicit food imports. Hyperiid residual
food uses an assumed 40% chaetognaths, 50% absent larval crustaceans/tunicates,
and 10% gelatinous split. Salmon uses the complete residence-integrated species
table, including the 0.14 kt rounded-total discrepancy. Jellyfish uses all
recovered categories, with absent prey imported and the 2006–2014 source period
explicitly distinguished from 2000–2014. Squid retains the article's aggregate
32.4 million wet tonnes and 64% plankton/36% nekton, with unresolved food assigned
between its two groups as a documented assumption. All 74 food components and
conversion/representation choices are in [the food ledger](food_component_ledger.json).

Twelve Figure arrows receive low-confidence 10× or 100× decimal hypotheses.
These are not demonstrated article errors. They are the minimum number of
changed labels within the tested decimal-reduction family for the six prey
production deficits. Accepted F62 = 0.023, F67 = 0.05, and F77's medium-pollock
origin remain unchanged. [All 78 decisions](all_arrow_decisions.json) retain
unchanged and text-overridden labels as well as corrections.
[Alternative hypotheses](alternative_hypotheses.json) quantify the rejected
stock/P/B multipliers and the limited combinatorial search.

Living accumulation is explicitly zero. GS is unknown in all 20 consumer input
rows and solved by the actual standard LIM; it is not supplied as 0.2.
Detritus import/export are zero. All living other mortality and egestion reach
the sole detritus pool, whose positive accumulation is the residual. Its carbon
inventory of 15.5 million tonnes is an explicit 18.25-day inventory-turnover
assumption and does not determine the food fluxes. The native import group's
B = 1 is a nonbiological runtime dummy; its actual completed P/Q equal imported
food demand. No biological B = 1 or failed-solver fallback is accepted.

The saved diagnostic state has detritus accumulation of
242.50886238380988 tC/km²/year. The saved native reload, final independent reload
and a fresh repeat reproduce all group flows and the GE, TE and With Egestion
SPPR matrices exactly; see [reload consistency](reload_consistency.json).
The engine uses deterministic coordinated initial guesses. An earlier approximate
242.537 value in commentary was stale, rather than solver variation. No reload
nonuniqueness was observed; unsupplied GS remains a model inference, not an
empirically identified parameter. Regional coefficients stay tied to the retained
diagnostic returns.

This accumulation is approximately 374.4336835 million tC/year, or 24.157 times
the assumed 15.5 million tC detritus inventory each year. It is a large nonsteady
residual imposed by zero detritus import/export and complete mortality/egestion
routing. Positive algebraic balance does not establish measured burial or a
validated ecological stock trend; the detritus inventory and its accumulation
must remain explicit scientific limitations.

## Actual diagnostics and sensitivities

[The eight required cases](case_coverage.json) cover Figure-only, unrepaired
text plus Figure, selective source repairs, and the completed text case under
F62 = 0.023 and 0.025. Figure-only fails energy completion for groups 6, 8 and 14.
The unrepaired hybrid can pass the algebraic main identities with negative M0
and EE above one; it fails physical admission. The adopted cases pass both.

The actual full direct GE, TE and With Egestion returns are all WARN. Divergence
and PPR budgets are OK. Their named-source matrices are finite and have no
negative source contributions. Warnings retain zero model catch and the four
unpredated terminal groups with EE = 0. TE returns zero coefficients for those
groups; those zeros are not invented or replaced. Its b = 0 convention does not
mean physical detritus recycling is absent. Actual GE recycling b is about
0.45293; detritus SPPR is about 1.89128.

[F62 sensitivity](sensitivity/F62_summary.json) reruns all three direct methods
on 0.025. All remain WARN with convergent and balanced returns; the maximum group
coefficient change is about 3.035% depending on method/scope. This is a coefficient
sensitivity, not a catch-weighted regional-total estimate.

Mathematical closure does not settle high P/Q values for copepods, euphausiids,
chaetognaths, salmon or jellyfish, low mammal P/Q, unknown food composition,
source periods, taxonomy/stage allocation, or tentative Figure endpoints.
Every supplied input-cell change is retained in
[the source-to-final ledger](source_to_final_ledger.json).

## EwE exports and reproduction

[Eight EwE imports](ewe_imports/) preserve 22 groups, diets/imports and unknown
GS. Structural validation returns zero errors and one unknown-GS warning.
Indicative source-table checks return zero errors and eight biological warnings;
their software GS = 0.2 assumption is not the native LIM solution.

The raw converter output is retained and rejected for runtime use: it omits
producer/detritus nonfeeding import zeros and native routing representation,
leading to a singular trophic-level solve. The separate
[constructor-admission ledger](ewe_imports/constructor_admission_ledger.json)
restores exact exported routing, non-pool structural zeros and the retained
native fields companion. It changes no biological food input and no engine.
All 1,210 native supported-cell checks pass, and actual loaded flows, ratios,
diet and fate match the authoritative model within 1e-12; see
[round-trip verification](ewe_roundtrip_verification.json).

Use [runtime settings](runtime_settings.json) with the native model; environment,
engine hashes, solver settings and tolerances are in
[runtime provenance](runtime_provenance.json). Reproduction scripts and source
hashes are retained. Diagnostic returns include lossless types/axes and explicit
nonfinite tags, separate masks, scoped sums and a keyed negative-entry table.
The native model stays unchanged during export, sensitivity and integration.
