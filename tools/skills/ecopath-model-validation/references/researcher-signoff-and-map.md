# Register a signed review and refresh the map

Use this handoff when the user authorizes adopting an actual researcher-signed Word review into Project and the map. A report draft, healthy diagnostics, a file's existence or approval of a template does not authorize signoff, scientific changes or publishing. Never add a researcher identity, date or `MODEL VALIDATED` on the researcher's behalf.

## Source and applicable exclusions

1. Read the **latest final DOCX**, not an earlier edited baseline or registration script's frozen values. The supported signature is `Researcher name: <real name> | review date: dd/mm/yyyy` plus the researcher's actual `MODEL VALIDATED` decision in **Review and reproducibility**. Verify the exact selected model ID. `read_report(root, report, model_id)` in [researcher_review.py](../../../researcher_review.py) returns `(name, ISO_date, summary)` and rejects missing signatures or mismatched models.
2. Preserve the source's paragraphs, hyperlink segments, rounded numbers and manual `w:br`, `w:cr` and `w:tab` breaks. The parser's segments preserve those breaks; joining only `w:t` text would lose them. Do not correct researcher prose or restore deleted diagnostics, prompts or links while registering. Keep any scientific discrepancy in separate supporting evidence.
   For **Taxon mapping confidence**, transfer only the introductory text above the **Overall confidence** table and that table itself, following the LME036 presentation. Read DOCX body children in document order and stop at the actual table; a paragraph-only scan skips this boundary. Omit the separate appendix/Sources link paragraph (identify its workbook target, not its varying label); the map already supplies the appendix link. Do not include subsequent component summaries, group-assignment or allocation rules, Very low decisions, or geographic evidence. Verify the introduction and table directly against their Word positions, rather than relying only on equality with the parser output.
3. Derive proposed display exclusions anew from the source SPPR calculation notes and the authorized review scope. Resolve names against **Selected model groups / Groups** in the exact regional workbook and verify **Overview / Settings.selected_model_id**. Use its actual `seq` identifiers for registration; the saved display IDs are the corresponding exact group names. Do not reuse numbers in prose as identifiers without checking the model, join by row position, invent a group, or substitute a vaguely similar group.
4. If the signed source declares no removals, the applicable list is `[]`; retain the ordinary no-exclusion note. A removed-group label absent from the selected model requires clarification, or an explicitly documented and authorized empty applicable-exclusion override. Preserve the source label and use an honest computed note explaining the absence. Do not silently turn unresolved or partly matched exclusions into an empty list. `register_review` can compute an absent-group note for a wholly absent declared list, but the caller must establish and document applicability; this helper is not permission to discard a source decision.

The reviewed LME032 marine-mammal removal and LME036 removals are region-specific examples. Final LME034 says `No groups were removed from the calculation.` and therefore has no applicable display exclusions; the earlier seabirds mismatch is superseded. None of these choices is a generic default.

## Bounded registration and refresh

Serialize shared Project/HTML writes. Finish or coordinate any other central updates first, then snapshot the current `Project.xlsx` **before** registration. Retain that pre-registration copy until refresh and source-equality checks pass. This workflow changes review metadata and display policy only; it does not call regional calculation, SPPR, `update_project.py`, or a full HTML build.

Use the real Python APIs, with `Path` arguments:

```python
# Run from the repository root with the bundled workspace Python runtime.
import shutil, sys, tempfile
from pathlib import Path

root = Path.cwd().resolve()
sys.path.insert(0, str(root / 'tools'))
from researcher_review import read_report, register_review
from build_html import refresh_reviews

project = root / 'Project.xlsx'
unit_id = '<exact unit ID>'
model_id = '<exact selected model ID>'
report = root / 'regions' / unit_id / f'Model_validation_{model_id}.docx'
name, date, source_summary = read_report(root, report, model_id)
excluded_seq = []  # Replace only with source-approved, exact Groups.seq values.
# [] is valid only after establishing that no applicable exclusions remain.
temporary = Path(tempfile.mkdtemp(prefix='signed-review-'))
previous_project = temporary / 'Project_before_registration.xlsx'
shutil.copyfile(project, previous_project)
register_review(project, report, unit_id, model_id, excluded_seq)
refresh_reviews(project, previous_project, [unit_id])
# Perform the targeted source-to-metadata/page checks below.
# Remove the temporary directory only after those checks pass; retain on failure.
```

Use the Python API for legitimate empty exclusions; the current CLI requires one or more `--exclude-group-seq` values. The latest actual usage and preservation proofs are under [LME034 researcher review](../../../../regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/researcher_review_20261001/); historic scripts contain fixed source hashes and decisions and must not be blindly replayed.

`register_review(project, report, unit_id, model_id, excluded_seq)` updates one central **Models & coverage / Models** row with researcher/date/status, report path and SHA, model/input identity, approved sections and applicable display exclusions. It preserves regional science. `refresh_reviews(workbook, previous_workbook, unit_ids, directory=None)` in [build_html.py](../../../build_html.py) refreshes map and trends after verifying the existing page fingerprint against the pre-registration Project snapshot. It replays registration against that snapshot, compares every decompressed workbook part, and permits only the targeted review/exclusion payload fields and new Project fingerprint.

If that gate rejects unrelated changes or a stale page fingerprint, stop this handoff and explain the mismatch. Do not bypass it with a full build or new scientific run merely to update notes. Preserve the snapshot for diagnosis and resolve the authorized sequencing issue before retrying.

## Source-to-map acceptance

For this metadata-only handoff, check **only the intended review information against the signed Word** and the new Project fingerprint. Compare a fresh `read_report` result with the selected central row and both generated page payloads: reviewer/date, report SHA/path, section text/paragraph segments/links/breaks, rounded confidence table and reference, applicable exclusions and the computed note. A later Word edit requires fresh registration/hash and this bounded refresh again. Changed model or calculation-input identities require the appropriate scoped review; do not relabel stale content as current.

The visible map contract is:

- Reviewed model names are green, with their normal labels. Never prefix/suffix the Ecopath dropdown name with `Validated by researcher`.
- An unreviewed model shows only the red `Model not yet validated by researcher` line between the PPR description and PPR-through-time button; no fabricated review sections or extra status prose.
- Reviewed details use six flat headings: **Model extraction notes; GE diagnostics; TE diagnostics; SPPR Calculation Notes; Geographic fit; Taxon mapping confidence**. The saved summary currently combines GE/TE in one section; [researcher_review.js](../../../researcher_review.js) splits them at display. Do not duplicate or nest headings to change that schema.
- Confidence remains tied to the signed Word's reference year, catch basis and independent simple-chain PPR universe. Changing live UI year/basis does not redefine the reviewed table.
- Approved removals affect **displayed webpage PPR only**. Preserve canonical models, SPPR, diagnostics, catch/coverage denominators, NPP and saved workbook science. Retain original allocation weights without redistributing omitted shares. Removed group controls stay unchecked and disabled; selection/reset/URL/storage must not restore their PPR contributions.

Do not broaden verification into new regional validations or scientific recalculation unless the user requests that scope. Retain concise provenance for any applicability override and source-equality check without adding workflow narratives to the researcher's Word.
