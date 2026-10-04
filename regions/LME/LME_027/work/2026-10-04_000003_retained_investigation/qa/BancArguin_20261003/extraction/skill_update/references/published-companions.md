# Published fields and compatible EwE imports

Preserve every published field relevant to the model, including fields that the
target calculator cannot use. The eight standard import filenames, headers,
column order and row conventions in output-formats.md stay unchanged. Z and P/Q
already have columns in Basic_input.csv; do not append new columns there.

Additional data belong in **separate purpose-specific CSV evidence companions**
under `companions/`. These files are not asserted to be directly importable by
EwE. Suitable purposes include stanza links/transition ages/growth, migration,
fleet routing/prices, alternative table versions, scenario constraints,
vulnerability values, and exact cell provenance. Separate model-period inputs
from time-series/scenario outputs. Retain fields even if a calculator has no
supported representation, and explicitly report that limit.

In the extraction JSON, add an optional `companions` object:

```json
{
  "companions": {
    "Source_stanzas.csv": {
      "description": "Published stanza linkage and growth; source evidence, not an EwE import",
      "rows": [
        ["stock", "adult_group", "juvenile_group", "transition_age_months", "vbk_per_year", "source", "locator"],
        ["Example fish", "3", "4", "12", "", "Supplement", "Text S1"]
      ]
    }
  }
}
```

Use decimal strings for source literals and empty strings/null for unknowns;
printed `0` stays zero. Each file needs a descriptive header, explicit units and
source locators, with status distinguishing published, inherited, derived,
accepted correction and unknown where applicable. Arbitrary columns and quoted
CSV cells are allowed only in companions. Record every extra source field in a
companion; do not hide it solely in prose or an opaque native-file attachment.
`write_outputs.py` writes the files and a SHA-256 manifest; companions are kept in
a subdirectory so import-file discovery cannot mistake a provenance table for
Basic_input or Diet_composition.

`database_json.py` retains all companion rows in `published_companions`, restores
the standard fields from the eight import tables, and reconstructs standard and
companion sheets with a manifest. `SOURCE_FIDELITY_CHECK.json` checks all source
values and missing masks after reopening the workbook. Standard import fidelity
and biological validity are separate outcomes. A companion has no automatic
calculation effect: an explicit field/units/basis mapping and transformation
ledger are needed before a calculator uses it.

Set `metadata.biomass_basis` to `whole_model_area` only when supported by the
source. Otherwise biomass can be converted from habitat density only when the
habitat fraction is known; a missing habitat fraction is not silently one.
BA remains in its published absolute or per-biomass form. Derived complementary
BA belongs in a separate calculation/companion with its operands. Known fleet
subtotals do not establish complete catch when a fleet cell or discards is
unknown. Source table blanks and unpublished variant cells need separate status
in the evidence companion even though both remain blank in standard imports.

For native or alternate source versions, preserve their fields in a separately
identified model or source companion. A different deposited model is not an
accepted correction to a published matrix. Never normalize diets or routing in
canonical extraction/conversion/reconstruction.

Table companions require rectangular rows and unique nonempty headers. Use
`layout: "source_grid"` only for verbatim source tables with merged/multiline
headers; ragged source rows are padded with blanks. Safe CSV basenames are
required. Regeneration removes only omitted prior generated companions whose
hashes still match; manually changed omitted files raise an error.

Standard reconstructed sheets use numeric cells with source-compatible decimal
formats; source JSON and companions retain literal text. Verification compares
missing masks and numerical values (absolute 1e-12 or relative 1e-14 tolerance),
and reports the largest difference. Input flags describe values supplied to the
importer; provide each group's `parameter_roles` mapping to mark published
`model_estimated` or `derived` values as non-input while retaining their numbers.
Preserve author provenance separately from these importer flags.

The default database `export` requires known landings plus known discards. An
explicit source convention `metadata.export_basis: "reported_landings"` can retain
published catch there, with `export_scope` identifying that limited basis and
unknown total removals kept unknown. Absolute BA in habitat units is scaled by
known habitat fraction for the database's whole-model-area basis; source literal
and imports stay unchanged. `metadata.ba_basis: "whole_model_area"` prevents
scaling already area-standardized absolute BA. Missing area fraction prevents
an unsupported absolute-area conversion.
