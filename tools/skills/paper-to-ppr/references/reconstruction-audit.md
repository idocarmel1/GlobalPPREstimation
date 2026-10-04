# Source, conversion and reconstruction audit

Keep source evidence, the exact canonical model/variant with documented departures, and ephemeral loaded calculator state identifiable. A scientifically distinct computational variant has its own model ID and one model.json; do not retain separate source_model.json, computational_input.json or loaded-model JSON companions. Numerical success at one layer does not establish fidelity at another.

## Source and identity

- Build a crosswalk of native IDs, Sequence/order, source names, life stages and table versions. Join continued tables by verified identities, not positions alone. Reconcile conflicts against independent parameter signatures or membership evidence.
- Record each symbol and sentinel by field: printed zero, missing blank, inequality, rounded display zero, unknown-input sentinel and unused placeholder are different. For Excel use stored numeric values and retain display formats as evidence; floating-point tails do not add scientific precision.
- Preserve all known fisheries components. Missing landings plus known discards means incomplete total removals, not zero catch. Reconcile fleet sums against published group totals; do not infer a catch multiplier from fishing effort.
- Record units and spatial denominators, particularly habitat versus whole-area biomass, rate versus flow BA, catch density multipliers, Z versus P/B and immigration/export terms. Do not apply an area or unit conversion twice.
- For multistanza sources, inventory links, transition ages, growth and stock-level BA conventions. State which native equations the target checker/calculator supports. A translation residual does not by itself prove the author's native model is wrong.
- Preserve shared stage-specific taxonomy and source spelling conflicts. Representative species lists are not automatically exhaustive group definitions.

## Conversion and loader checks

Compare source → eight import tables → canonical JSON → reconstructed tables field by field, including group count/identity, B/PB/QB/EE, P/Q, TL, GS, BA, migration, diet/import, habitat area, routing, fleets, landings/discards, taxonomy and unknown markers. Label lossy views as such. A converter exit code or round trip is not an ecological balance verdict.

Keep raw converter output in temporary work while reconciling changed source values; promote necessary cell evidence, then remove redundant conversion packages. Record every restoration with group, field, old/new value and source evidence. Regenerate or clearly supersede reports that describe an earlier normalized intermediate. Authentic apostrophes in names must not be removed to satisfy a false-positive quote validator.

Before loading, enumerate unknown biological B/PB/QB/EE. When source equations determine unknowns, solve the coupled system as an explicitly authorized distinct computational variant with one canonical model.json and model_notes.md; verify rank/uniqueness, residuals, admissibility and published outputs or an independent formulation. Record equation, operands and precision limits. Do not accept a loader's B=1 placeholder as biological reconstruction or use free tuning to turn an underdetermined system into a source-derived solution.

After initialization, save a machine-readable field-by-field transformation ledger. Highlight censored values becoming zero, real-group biomass imputation, changed known rates, detritus EE forced to one, known BA replacement, derived BA, diet normalization and synthetic groups. Keep source and loaded budget checks distinct. Solved BA can close equations without demonstrating source steady state or observed stock trends.

Use explicit UTF-8 for reads and writes; compare group names and taxonomy as well as numbers. For Word visual checks on Windows, a hidden, read-only installed Word export to a separate PDF is a fallback when LibreOffice is unavailable. Close only automation-owned documents/processes in cleanup; never modify the original or close the user's sessions.

## Authorized variants

Respect source-preservation rules and existing user authorization. Normalization, parameter adjustments, pooling and non-source flow completion need explicit provenance and a distinct derived identity; do not overwrite canonical evidence or ask again for an already authorized experiment.

- **Diet normalization:** extraction/conversion/export/round trips never normalize prey or import cells. Preserve source literals and explicit accepted corrections. Runtime normalization is always allowed on a separate copy; quantify raw/runtime sums, save factors and changed cells, and recompute any authorized dependent predation/EE from that exact runtime state. Researcher verification establishes trust, not execution permission. Inspect continuation blocks, imports and source images before classifying discrepancies: material deficits are not rounding, and small drift is not approval. A tolerance change is a separate choice. For an existing-model audit first establish whether canonical normalization occurred; re-extract only confirmed cases. Follow [the diet evidence contract](../resources/extraction/references/diet-source-runtime.md).
- **Pooling:** record the group crosswalk and precisely which compatible stocks, diets and flows are summed. Preserve unchanged consumer fields/totals; do not average EE or infer fate from habitat fractions. Pooling missing detritus routing introduces mixing assumptions and may still fail source balance.
- **Discards:** independently check donor fishery removal, recipient inflow, recycling ancestry and external-export accounting. Count internal returns once. Natural M0/egestion fate and fleet-discard fate are distinct; a fate matrix alone may not encode all four parts.
- **Parameter scenarios:** state which source quantities are preserved and which are adjusted. An improved diagnostic grade does not make a scenario author-confirmed. Closure residuals are unexplained flows, not automatically source parameters.
- **Reload:** save source/derived hashes, exact loader options, code identity and a bounded reproduction entry point. Reload the persisted input and compare state, flows and requested diagnostic returns with the audited state before using its coefficients.

When exceptions appear, inspect basal/nonfeeding rows, NaNs, imports and expected basis dimension before attributing them to biology. Document exact cells for any structural-zero convention and retain the original exception. Trace disagreements through source, converter, loader and diagnostic equations before declaring a cause.

## Completion record

For authorized downstream refresh after a canonical diet correction, compare the
actual loaded runtime state/settings against retained state; a source hash change
alone does not trigger reruns. The current project instruction ignores numerical
differences within 1e-12 and excludes human-authorized changes to biomass
accumulation, its rate/calculator growth alias, and predation from the refresh
trigger (record those changes separately). All other runtime fields remain
compared. Equivalent runtime preserves existing results with an
explicit source/runtime identity bridge; changed runtime refreshes affected
diagnostics, coefficients, calculations and display/report sections. Preserve
actual historical hashes, model selection and researcher review gates. Serialize
shared updates and coordinate existing report owners.

Report source recovery/extraction, source admission, reconstruction assumptions, diagnostic outcome, taxonomy/catch coverage, spatial suitability, selection and regional calculation readiness separately. Preserve exact page/table/cell provenance and all unknowns. Record a failed or blocked candidate completely rather than inventing a successful numerical run.

## Published fields and EwE compatibility

Preserve every published model field. Keep the eight EwE import CSV/XLSX schemas
unchanged; place additional stanza, migration, fleet, scenario and provenance
fields in separate purpose-specific evidence CSVs under `companions/`. Those
companions are not asserted to be directly importable by EwE. The extraction
[companion reference](../resources/extraction/references/published-companions.md) documents their manifest/schema.
Retain all companion cells in canonical JSON and reconstructed sheets; verify
source/import/JSON/workbook values and missing masks. Unsupported calculator
fields remain retained evidence until an explicit mapping is reviewed.
