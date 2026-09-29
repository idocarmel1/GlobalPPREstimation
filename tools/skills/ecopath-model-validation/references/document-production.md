# Produce the validation document

Use the current [Word template](../../../templates/Model_validation_template.docx) and [filling guide](../../../templates/Model_validation_template_instructions.md). This reference covers artifact handling and verification; it does not authorize a scientific run.

## Inputs and output paths

For a new regional record, the default output is:

`regions/<unit_id>/Model_validation_<model_id>.docx`

Supporting evidence belongs under:

`regions/<unit_id>/validation_reports/<model_id>/`

Use an explicit user-specified destination instead when provided. If a destination already contains researcher work, preserve it and use a clearly named review copy unless an in-place update is authorized. Do not silently overwrite a current report with a historical reconstruction. The master template is an input and is not rewritten when filling a regional report.

Keep transient builders, extracted XML, render images, PDFs and QA logs in a task-specific temporary directory. The final deliverable is the Word report unless the user requests other formats. Do not create a new report-output hierarchy or authoritative status file outside the project's existing conventions.

When copying existing evidence into the model's validation folder, copy required linked assets too. Reuse an identical existing copy; avoid overwriting a same-named file with different content. Record source/copy paths and provenance in `reports_index.md` without replacing unrelated entries. A newly authored analysis must be labeled as this review's analysis, not presented as an old source report.

## Preserve the researcher's document

Read only explicitly permitted documents. Inventory their paragraphs, table cells, manual entries and full hyperlink targets. Word may split a URL between its relationship target and a `w:anchor`; retain both. For local links, resolve relative to the output document's directory, not the repository root.

Manual cells are **SPPR calculation**, **Open issues and next action**, and **Review and reproducibility**. Preserve researcher text and formatting in these cells when updating a record. Preserve the researcher's Article/Model selection rationales as well. Use semantic field labels or stable bookmarks to locate cells; row numbers shift when the other-models or mapping sections change.

Do not restore introductions, the removed long diagnostic paragraphs, repeated provenance warnings, deleted links, or the completion-instructions section. Retain important newly discovered limitations in a concise finding or supporting report. Do not insert old regional examples as generic template content.

When a user-edited record is the layout/content authority, distill its structure and intended editable areas before editing a copy. Use the documents skill's reference-preservation workflow. Prefer small OOXML changes when they preserve styles, relationships and manual-cell XML. Never attach to an active Word document to obtain unsaved edits unless that interaction was explicitly requested and permitted.

## Main report

Follow the template field order:

1. Region; Catch source; Selected article; Other known articles.
2. Selected model; Other models from the same article; Selection rationale with Article and Model entries.
3. Model extraction; manual SPPR calculation.
4. GE diagnostics; TE diagnostics.
5. Taxon mapping and coverage; Geographic fit; Temporal fit; optional Other.
6. Manual Open issues and next action; manual Review and reproducibility.
7. Geographic evidence figures.
8. Landscape Appendix A Taxon mappings and its sources.

Use short, useful entries. The mapping summary has the year/basis, group/taxon counts, catch/PPR totals, and High/Medium/Low/Unresolved rows. Retain Membership evidence and Weights and assumptions lines, plus a missing-PPR note only when needed. Avoid a separate Catch coverage row.

The negative-SPPR findings must pair each source column with its affected groups. Preserve names and IDs even when the list expands the GE or TE cell. If a large list needs a supporting detail table, retain explicit per-column group information in the delivered report or its clearly referenced diagnostic attachment; never reduce the finding to an unpaired count.

Geographic percentages must identify whether they are calculated, approximately digitized or visually estimated. Include the definitions of A and B. Remove legacy caption wording prohibiting estimates. Keep readable source figures and captions together; use separate pages when an image needs the space.

## Appendix layout and content

Use the landscape section with repeated table headers. Keep the seven agreed columns and one row per catch label. Do not create separate per-confidence tables, split one taxon into multiple counted rows, or omit unresolved/zero-catch taxa from the defined universe.

State reference year, catch basis, simple-chain method/units, missing-value notation and **descending simple-chain PPR order** above the table. Use exact group names and displayed percentages; `?` remains visible for unresolved weights. A known partial allocation may retain known weights with the remaining candidates marked `?` and explained.

Keep Reason concise but substantive: membership basis; required weighting basis/transfer assumption; short source IDs. Rule IDs can be included where useful. Full sources beneath the table must identify relevant pages, tables or online entries, with links and retrieval dates as appropriate. Include TL and simple-chain-method sources too.

Do not shrink a long appendix until it becomes unreadable. Allow more pages, repeat headers, wrap group lists, and allocate enough width to Reason. Check that no single unsplittable row becomes taller than a page. For unusually long rows, permit a controlled row break or move extended explanation to a linked report while preserving its essential reason and all groups/weights.

## Rendering and integrity

Load the bundled workspace dependencies and apply the documents skill's required artifact marker once immediately before the first create/edit authoring operation. Retain a pre-edit reference and compare relevant package parts and manual cells after writing.

Run the packaged DOCX renderer and inspect every page image. If the renderer fails, diagnose the logs first. On Windows where LibreOffice is unavailable, an available fallback is an independent hidden Word instance: disable alerts/macros, open only the permitted output read-only, export a temporary PDF, close that document without saving and quit only the instance created for this task. Never use the active user instance. Rasterize the PDF and inspect all pages. If no renderer is available, report that the output could not be visually verified rather than claiming completed QA.

Check portrait body/landscape appendix orientation, table widths, readable font sizes, repeated headers, source captions, no clipping, no stranded section headings and no accidental blank pages. Table/figure placeholders should be filled or explicitly unavailable; remove template-only prompts from completed automatic fields. Retain meaningful researcher/manual placeholders.

Verify local hyperlink targets exist and external links point to the intended sources. Check URI decoding and fragments without corrupting literal paths. Do not reopen every remote reference merely to claim that formatting links work; distinguish destination verification from evidence retrieval.

Use targeted before/after checks for the relevant allowed scientific inputs to confirm a report-only run did not change them. Never inspect excluded files for this check. Preserve the edited researcher original and master template. No workbook writer, SPPR solver, project updater or map builder is part of ordinary document production.

## Delivery

Return the Word report with a brief statement of material gaps and what was verified. Detailed audit files are linked from the report as needed; QA screenshots, temporary PDFs and builders are not deliverables by default. Offer no claim that the model is approved, that a pipeline was rerun, or that historical evidence was freshly reproduced unless supported.

When the user asks to review a skill/template before a regional test, deliver those requested artifacts and stop. When the later test is authorized, apply this skill to the specified region, preserving any continuing file exclusions and using a new output path that protects researcher work. If that validation reveals a need for a fresh scientific run, recommend the necessary scope, explain why, and ask for explicit confirmation before starting it. Authorization for a validation test is not authorization for a scientific rerun.
