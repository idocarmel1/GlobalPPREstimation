# Diet source values and runtime normalization

Read this when extracting, converting, reviewing or restoring diet/import data.

The eight import tables, extraction JSON, canonical model JSON, exports and round
trips retain exact printed/native diet and import proportions plus documented
researcher-accepted corrections. Never normalize these artifacts, fill a deficit
with an invented prey share, or increase precision by undoing normalization using
an approximate sum. Preserve source decimal text where supplied. A printed zero,
missing cell and corrected value need separate evidence.

For an audit of an existing model, first compare its selected JSON cells with
retained source/import cells and conversion history. Re-extract only when
normalization is established. A column summing to one does not establish either
source fidelity or normalization. A raw native export can establish faithful
conversion while printed-table fidelity or earlier upstream processing remains
unresolved. Ambiguous evidence does not justify overwriting a model.

Retain a cell ledger with consumer/prey IDs, source literal, adopted literal,
file/hash/page/table/coordinates or native JSON pointer, and correction evidence.
An accepted correction needs the actual researcher decision, its date/identity
when available and before/after values. Preserve existing accepted overrides;
never substitute raw paper values for them. Source differences without such a
decision stay unresolved. Keep per-consumer sums including imports, missing-cell
status and researcher review state. Extraction or a small deviation does not
establish approval or prove that all discrepancies are rounding.

`write_outputs.py` preserves cell values, including import decimal text.
Explicitly unknown imports remain blank in CSV/Excel and `-9999` in model JSON;
their diet-plus-import total is unknown, with the prey-only sum recorded separately.
A known zero remains zero. Do not substitute structural zero for explicit unknown.
`database_json.py` preserves them in JSON and writes `DIET_SOURCE_SUMS.json` with
the input-table hash and exact decimal totals. That receipt documents conversion
input, not primary-source fidelity or a human review. Keep the writer-input JSON
in temporary work during reconciliation; promote its necessary cell ledger as
current extracted_tables/evidence, then remove redundant JSONs. Reconstructed Excel holds numeric cells;
the source JSON/ledger retains printed formatting and provenance.

Runtime normalization is always permitted on a separate computational copy.
Researcher verification determines trust in the results; it is not an execution
permission gate. Record the source input hash, raw/runtime consumer sums, factors,
changed diet/import cells and settings in the runtime transformation ledger.
Diagnose material deficits, rounding and unresolved source errors separately:
normalization does not resolve them. Never write runtime-normalized cells back to
canonical/extracted data. Do not change detritus fate or unrelated parameters as
part of a diet restoration.

Before an authorized restoration, record original hashes and exact cell changes,
preserving original publication/native sources. Temporary transaction copies are
removed after verification; superseded extraction inputs are recoverable through
Git history rather than a new archive or merged legacy package.
Preserve retained diagnostics/calculations under their actual input hashes and
record canonical changes and runtime equivalence/staleness in new local
provenance. A canonical byte/hash change alone is not a changed runtime model.
When dependent refresh is authorized, compare the actual old/new loaded runtime
state, including normalized diet/imports, group parameters, routing and settings,
with the retained calculation state. Retain results when equivalent; refresh
affected diagnostics, coefficients, scientific workbook values, project/map and
report sections only when runtime differs. Record comparison tolerance explicitly
(the current GlobalPPREstimation instruction ignores differences within 1e-12).
For this comparison the human also permits runtime rebalancing changes in
`biomass_accum`, `biomass_accum_rate`, its calculator alias `growth`, and
`predation`. Record these changes separately and exclude them from the refresh
trigger. Compare all other runtime values, including production, consumption,
mortality, diet and routing; an allowed BA/predation change does not exempt them.
Verified equivalence must connect distinct source and historical runtime identities
through the maintained verifier and actually retained admissible evidence. A
historical certificate whose required source was removed does not certify current
results: preserve its historical hash, make numerical readiness pending, and state
the missing proof. Never overwrite actual diagnostic input hashes or bypass freshness checks.
Scientific refresh does not change model selection or establish a new researcher
signoff. Serialize shared updates and coordinate existing regional report owners.

Store cell statuses, source literals, corrections and variant constraints in
separate evidence companion CSVs under the
[published-companions contract](published-companions.md), keeping the standard
Diet_composition.csv schema unchanged. A known-cell sum is not a complete sum
when a source/variant component is missing; retain both the subtotal and missing
cell identities. Reconstruction preserves the missing mask.
