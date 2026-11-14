# ICES report editing contract

Authority: retained inputs/validation_before.docx, whose SHA256 and complete XML part inventory are in report_inventory.json. The latest tools/templates/validation.docx supplies the additional Very low decisions table only. Current main field order and manual content already match the template.

Baseline: six pages rendered through an independent hidden read-only Word instance with macros, alerts and link updates disabled. All six page images inspected. The packaged renderer failed because LibreOffice is unavailable. Baseline layout is one portrait A4 section with 0.65-inch margins, a flowing two-column Field/Entry grid, comparison, independent coverage/rule tables, and two geography pages. Calibri body, restrained gray-blue table headers, no decorative additions.

Edits: title, automatic GE/TE/Other and temporal findings; current comparison replacing superseded Scotland diagnoses; proposed mapping reference, confidence and component rule summaries; all Very low decisions and specific unresolved reasons. Add the template's Very low table with exact header names. Link current local evidence by relative targets. Preserve geography figures and source captions. Preserve manual SPPR, open issues, reviewer and rationale cells exactly as XML, including breaks and links.

Preservation: retain every ZIP member byte-for-byte except document.xml and its hyperlink relationship part. Main manual cells, figures/media, styles, section geometry, headers/footers, numbering, content types and unrelated text are preserve-only. Record justified automatic fields and body-section changes; no signing or registration.

Verification: unsigned parser outcome must remain unsigned and model identity unchanged. Exact confidence/Very low/weight tables must agree with the one mapping decision set. Two significant digits for table percentages. Resolve every relative link and check visible hyperlink styling. Render final DOCX using the same read-only Word fallback and inspect every page. Final file remains validation.docx with adjacent taxon_mapping.xlsx; no regional/shared output writes.
