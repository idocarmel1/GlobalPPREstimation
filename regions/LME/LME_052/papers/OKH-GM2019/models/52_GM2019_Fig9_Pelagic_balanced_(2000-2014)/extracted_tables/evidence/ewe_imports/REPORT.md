# Derived carbon model EwE imports

The eight standard files preserve the authorized derived input, in tC/km² and
annual rates, rather than source wet units. The authoritative native input is
[../model.json](../../../model.json); its exact actual LIM results are
[../native_reload_result.json](../native_reload_result.json).

GS remains unknown in 20 consumer inputs. A vanilla EwE import may assign its
0.2 software default, which is not the native model's solved GS. The eight-table
indicative balance check is therefore INDETERMINATE despite the separately
verified native mathematical balance. Usual P/Q outliers remain scientific
warnings and must not be erased.

The raw generated database JSON retains all 22 groups and their correct roles,
but drops nonfeeding producer/detritus routing representation and treats their
import fractions as unknown. Its actual singular-matrix failure is retained in
[raw_converter_admission.json](raw_converter_admission.json). This file is not
the adopted scientific model.

[constructor_admission.json](../../../model_notes.md#removed-extraction-evidence) restores exact exported
Detritus_fate.csv routes, nonfeeding import structural zeros, non-pool fate
structural zeros, and the unsupported native fields in the retained companion.
[The admission ledger](constructor_admission_ledger.json) records every change.
The actual native reload of that copy balances and reproduces all authoritative
runtime fields within 1e-12; [verification](../ewe_roundtrip_verification.json)
retains 1,210 input-cell checks, groups/roles, companion/source-workbook missing
masks, and loaded flow comparisons.

The converter scripts and the original rejected extraction output are not
modified. No legacy balanced copy, altered migration, patched balanced flag,
biological fallback stock or post-load vector adjustment is used.
