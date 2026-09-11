# Mortality, discard fate and calculation boundaries

Read when reconciling article mortality with loaded model values, extracting fleet
returns, or handing an extraction to a discard-routing study. Preserve the paper's
parameters separately from values completed or changed by a calculator.

## Compare rates with rates, and flows with flows

An article's natural-mortality rate `M` can include predation `M2` plus other
mortality. Check the source definition before comparing it with `M0`. In the
GlobalPPREstimation calculator, `model.M0` is a biomass flow, not an annual rate:

```
P = B * PB
model.M0 = P * (1 - EE)
other_mortality_rate = model.M0 / B = PB * (1 - EE)
```

For the inherited Bay of Bengal oceanic-shark record, `B=0.202`, `PB=0.249` and
`EE=0.582` give `model.M0=0.021024564` in model biomass/area/year units, or
`0.104082/year` after dividing by B. Neither is automatically the article's total
natural-mortality rate. Reconcile predation, fishing, accumulation and migration,
the paper's original versus balanced table, and the loaded model version before
calling a discrepancy an extraction error. Do not overwrite EE to force equality.

The standalone Ecopath reference uses `M0_i` for the *rate* in its mortality
equation; the calculator attribute above uses the same name for a *flow*. Record
units and the actual field being inspected. Source units can be wet biomass, dry
biomass, carbon or energy: read the model's metadata instead of imposing a unit.

## Capture the full fisheries ledger

Extract reported landings, discards, total catch, fleet identity, mortality or
survival assumptions, return destination and any subsequent detritus transfers.
A missing split or return fate stays unknown. A paper's assumed discard amount
is not a measurement. An explicit zero is different from a loader default.

Check how the importer represents each field. The project's legacy loader aliases
raw `export` to `catch` and clears detritus catches; those field names do not create
two independent sinks. It can also omit fleet returns and detritus-to-detritus
fates from the solved representation. Preserve such source information in the
extraction and provenance even if the current calculator cannot consume it.
Detritus export must not enter living fishery catch weights.

If discards enter an offal group that then supplies other detritus pools, record
both transfers. Count the returned amount once, retain donor identity, and check
whether offal has direct consumers before collapsing the intermediate transfer.
Do not add an undocumented processing-offal amount or renormalize fate shares.

## Separate an experiment from the source extraction

A routing experiment starts from one frozen, reproduced model. Record source
hashes, model/group identifiers, initializer settings and all inferred values,
including biomass accumulation. Keep the extraction and production engine intact;
use an explicit experimental adapter for changed equations.

For a designated amount D from existing catch H, distinguish these mechanisms:

| Route | Accounting change |
| --- | --- |
| Catch removal | Retain H as a fishery sink; credit no return |
| Mortality-to-detritus proxy | Move D from fishery catch to M0 and update EE consistently |
| External loss | Move D to a distinct external sink; keep M0/EE fixed |
| Documented discard return | Retain fishery mortality H and route D internally to an evidenced destination |

The second is an accounting proxy, not newly observed natural mortality. A source
can support a return destination without supporting the experimental amount.
Do not encode external loss as migration merely to make an equation balance.
Separate the physical sink from the catch vector used to evaluate or weight a
method. State the closure: fixed living production, consumption and predation do
not imply that all extra detritus is consumed; residual detritus accumulation may
change instead. Never present that accounting experiment as a newly fitted annual
Ecopath model.

Report source evidence, physical budgets, numerical validity, method-specific
conservation and ecological limitations separately. A convergent result may still
violate a method identity or an existing plausibility check. A fixed-TL benchmark's
routing invariance is not evidence of zero ecological uncertainty.

For the repository's completed four-model experiment and source-specific limits,
consult `research/discard_sensitivity_2026_09_10/METHODS_AND_FINDINGS.md` and
`NUMERICAL_NOTES.md` from the checkout. These findings are model-specific; they do
not authorize changing other source models or extending atlas coverage.
