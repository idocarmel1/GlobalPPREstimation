# LME_035 diet preservation audit — 2026-10-02

Verified unchanged relative to raw native EcoBase accession 412. The current
selected `35_412_Gulf_of_Thailande_(1963)` model matches every retained native
diet/import value and structure exactly: 154 diet cells and 29 import fields.
The raw library payload was fetched by direct XML parsing, with no normalization
step in the retained fetch notebook. Three independently retained project copies
also match. Unit sums are recorded, but are not used as proof of preservation.

Canonical SHA-256 remains
`dc6b45d6a5f532a5ebd294b3365e43b8bd74b66ca0dea5a035793fcad8f836e9`.
No added canonical normalization is identified. Under the user's updated scope,
no re-extraction or canonical/import rewrite was performed. There are no selected
model extraction imports; the 1973 imports belong to a different candidate and
remain untouched. No diet cell correction was located in the current DOCX;
accepted current values remain intact.

The exact native cells, per-consumer sums, source hashes, unchanged-file checks
and historical diagnostic identity are recorded in [audit_result.json](audit_result.json),
[diet_cell_ledger.json](diet_cell_ledger.json) and [consumer_sums.json](consumer_sums.json).
An exact input snapshot is retained under `original_inputs/`. The regional
workbook and validation DOCX are byte-identical before/after the audit.

Unresolved evidence: the complete printed diet/import matrix for the focal
1980 payload is unavailable. Existing review documents establish a 1980
numerical payload under the inherited 1963 join identity. Native preservation
does not establish that EcoBase reproduces unavailable printed cells or that
normalization never occurred upstream of the repository. This audit makes no
printed-source-faithful or scientific-approval claim.

Historical direct diagnostics already used this same canonical input hash and
runtime `normalize_DC=true`; they are not newly stale because of this audit.
The latest explicit user steering permits runtime normalization. No fresh
calculations, coefficient adoption, workbook refresh, DOCX changes, selection
changes or shared Project/map writes occurred.
