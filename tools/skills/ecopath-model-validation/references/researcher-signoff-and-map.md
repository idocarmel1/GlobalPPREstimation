# Register a signed review and refresh the map

Use this handoff when the user authorizes adopting an actual researcher-signed Word review into Project and the map, whether validated or disqualified. A report draft, healthy diagnostics, a file's existence or approval of a template does not authorize signoff, scientific changes or publishing. Never add a researcher identity, date or either verdict on the researcher's behalf. Explicit authorization to register the stated decision and update the map covers this bounded handoff; do not ask for the same authorization again.

## Source and applicable exclusions

1. Read the **latest final DOCX**, not an earlier edited baseline or registration script's frozen values. The supported signature is `Researcher name: <real name> | review date: dd/mm/yyyy` plus exactly one actual `MODEL VALIDATED` or `MODEL DISQUALIFIED` decision in **Review and reproducibility**. A disqualification requires `Reason – <researcher's reason>` immediately below its verdict. Preserve that reason exactly. Verify the exact selected model ID. `read_report(root, report, model_id)` in [researcher_review.py](../../../project_core/validation/researcher_review.py) returns `(name, ISO_date, summary)` and rejects missing signatures, ambiguous verdicts, missing rejection reasons or mismatched models. Reread after any reported edit, including a changed date; never substitute today's date for the signed date.
2. Preserve the source's paragraphs, hyperlink segments, rounded numbers and manual `w:br`, `w:cr` and `w:tab` breaks. The parser's segments preserve those breaks; joining only `w:t` text would lose them. Do not correct researcher prose or restore deleted diagnostics, prompts or links while registering. Keep any scientific discrepancy in separate supporting evidence.
   For a **validated** review's **Taxon mapping confidence**, transfer only the introductory text above the **Overall confidence** table and that table itself, following the LME036 presentation. Read DOCX body children in document order and stop at the actual table; a paragraph-only scan skips this boundary. Omit the separate appendix/Sources link paragraph (identify its workbook target, not its varying label); the map already supplies the appendix link. Do not include subsequent component summaries, group-assignment or allocation rules, Very low decisions, or geographic evidence. Verify the introduction and table directly against their Word positions, rather than relying only on equality with the parser output.
   **Before transferring a validated review's tables**, verify numeric percentages in every final Word table use two significant digits and an explicit `%`, following the template guide. Run bundled Python with `python tools/project_core/validation/validation_percentage_format.py --check <final.docx>` (or call `verify_report(Path(...))`); resolve any format failure within the authorized Word-edit scope before proceeding. After registration, require the map and trends confidence tables to match the checked Word values exactly; do not round them independently in the browser or modify scientific data to match display rounding. A disqualification transfers only verdict, reason, signer/date and report link; it does not transfer confidence tables, so their formatting does not block a verdict-only handoff or authorize Word edits.
3. For a validated review, derive proposed display exclusions anew from the source SPPR calculation notes and the authorized review scope. Resolve names against **Selected model groups / Groups** in the exact regional workbook and verify **Overview / Settings.selected_model_id**. Use its actual `seq` identifiers for registration; the saved display IDs are the corresponding exact group names. Do not reuse numbers in prose as identifiers without checking the model, join by row position, invent a group, or substitute a vaguely similar group. A disqualified review registers `excluded_seq=[]`: rejection does not adopt proposed removals in its diagnostic/SPPR notes, and no fresh exclusions follow from the rejection reason.
4. For a validated review, if the signed source declares no removals, the applicable list is `[]`; retain the ordinary no-exclusion note. A removed-group label absent from the selected model requires clarification, or an explicitly documented and authorized empty applicable-exclusion override. Preserve the source label and use an honest computed note explaining the absence. Do not silently turn unresolved or partly matched exclusions into an empty list. `register_review` can compute an absent-group note for a wholly absent declared list, but the caller must establish and document applicability; this helper is not permission to discard a source decision.

The reviewed LME032 marine-mammal removal and LME036 removals are region-specific examples. Final LME034 says `No groups were removed from the calculation.` and therefore has no applicable display exclusions; the earlier seabirds mismatch is superseded. None of these choices is a generic default.

## Bounded registration and refresh

Serialize shared Project/HTML writes. Finish or coordinate any other central updates first, then snapshot the current `Project.xlsx` **before** registration. Retain that pre-registration copy until refresh and source-equality checks pass. This workflow changes review metadata and display policy only; it does not call regional calculation, SPPR, `update_project.py`, or a full HTML build.

Use the real Python APIs, with `Path` arguments:

```python
# Run from the repository root with the bundled workspace Python runtime.
import shutil, sys, tempfile
from pathlib import Path

root = Path.cwd().resolve()
from tools.project_core.validation.researcher_review import read_report, register_review
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.maps.build_html import refresh_reviews
from tools.project_core.registry.discovery import region_directory, resolve_model

project = root / 'Project.xlsx'
unit_id = '<exact unit ID>'
model_id = '<exact selected model ID>'
report = resolve_model(region_directory(root, unit_id), model_id).parent / 'model_validation' / 'validation.docx'
name, date, source_summary = read_report(root, report, model_id)
if source_summary.get('status') != 'Disqualified by researcher':
    verify_report(report)  # Validated confidence tables are transferred verbatim.
excluded_seq = []  # Required for disqualified; resolve approved Groups.seq for validated.
temporary = Path(tempfile.mkdtemp(prefix='signed-review-'))
previous_project = temporary / 'Project_before_registration.xlsx'
shutil.copyfile(project, previous_project)
register_review(project, report, unit_id, model_id, excluded_seq)
refresh_reviews(project, previous_project, [unit_id])
# Perform the targeted source-to-metadata/page checks below.
# Remove the temporary directory only after those checks pass; retain on failure.
```

Use the Python API for legitimate empty exclusions; the current CLI requires one or more `--exclude-group-seq` values. The latest actual usage and preservation proofs are under [LME034 researcher review](<../../../../regions/LME/LME_034/papers/LME034-Guenette-2013/models/34_1_Bay_of_Bengal_(1978)/model_validation/evidence/source_review/researcher_review_20261001/>); historic scripts contain fixed source hashes and decisions and must not be blindly replayed.

`register_review(project, report, unit_id, model_id, excluded_seq)` updates one central **Models & coverage / Models** row with researcher/date/status, report path and SHA, model/input identity and the applicable review snapshot. The central statuses are `Validated by researcher` and `Disqualified by researcher`; only the validated outcome carries approved sections/exclusions. It preserves regional science and model selection. `refresh_reviews(workbook, previous_workbook, unit_ids, directory=None)` in [build_html.py](../../../project_core/maps/build_html.py) accepts both outcomes and refreshes map and trends after verifying the existing page fingerprint against the pre-registration Project snapshot. It replays registration against that snapshot, compares every decompressed workbook part, and permits only the targeted review/exclusion payload fields and new Project fingerprint.

If that gate rejects unrelated changes or a stale page fingerprint, stop this handoff and explain the mismatch. Do not bypass it with a full build or new scientific run merely to update notes. Preserve the snapshot for diagnosis and resolve the authorized sequencing issue before retrying.

## Source-to-map acceptance

For this metadata-only handoff, check **only the intended review information against the signed Word** and the new Project fingerprint. Compare a fresh `read_report` result with the selected central row and both generated page payloads: reviewer/date and report SHA/path for both outcomes; exact verdict/reason for disqualification; section text/paragraph segments/links/breaks, rounded confidence table/reference, applicable exclusions and the computed note for validation. A later Word edit requires fresh registration/hash and this bounded refresh again. Changed model or calculation-input identities require the appropriate scoped review; do not relabel stale content as current.

The visible map contract is:

- Validated Ecopath model headings/names are green; disqualified headings/names are red. Preserve their normal labels rather than adding status prefixes/suffixes. Central model/status cells retain the same green/red distinction after Project refresh.
- A disqualified model replaces the pending line with **MODEL DISQUALIFIED**, then its exact **Reason – ...** immediately below. Show the actual researcher/date and report link. Do not show it as pending or green, and do not transfer its other report notes as approved sections. Keep it available in ordinary model selection but exclude it from **Validated by researcher**, whose eligibility requires that exact positive status rather than merely a review object.
- An unreviewed model shows only the red `Model not yet validated by researcher` line between the PPR description and PPR-through-time button; no fabricated review sections or extra status prose.
- Validated details use six flat headings: **Model extraction notes; GE diagnostics; TE diagnostics; SPPR Calculation Notes; Geographic fit; Taxon mapping confidence**. The saved summary currently combines GE/TE in one section; [researcher_review.js](../../../project_core/maps/researcher_review.js) splits them at display. Do not duplicate or nest headings to change that schema.
- Confidence remains tied to the signed Word's reference year, catch basis and independent simple-chain PPR universe. Changing live UI year/basis does not redefine the reviewed table.
- Approved removals affect **displayed webpage PPR only**. Preserve canonical models, SPPR, diagnostics, catch/coverage denominators, NPP and saved workbook science. Retain original allocation weights without redistributing omitted shares. Removed group controls stay unchecked and disabled; selection/reset/URL/storage must not restore their PPR contributions.

Do not broaden verification into new regional validations or scientific recalculation unless the user requests that scope. Retain concise provenance for any applicability override and source-equality check without adding workflow narratives to the researcher's Word.
