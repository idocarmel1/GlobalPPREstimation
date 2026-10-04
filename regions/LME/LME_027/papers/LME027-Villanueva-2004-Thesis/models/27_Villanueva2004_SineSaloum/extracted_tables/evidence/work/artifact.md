# Validation document template contract

Reference: `tools/templates/Model_validation_template.docx`, SHA-256
`2a6cb630b4697a87ac310a2a3871891ab189ee0466cef218a28d0b4ff384dbc4`.
Read-only template inventory is in `../qa/template_inventory.json`; every package
part is hashed in `../qa/template_parts.json`. Three reference pages were rendered
with a separately created hidden Word instance after the packaged renderer
reported missing LibreOffice; images are in `../qa/template_render/`.

The single A4 portrait section is 8.27014 by 11.69028 inches with 0.65-inch
margins. Retain section geometry, fonts and paragraph/table styles, headers,
footers, theme and numbering. The reference has no content-control slots.
Its restrained pale blue table headers and existing exact column grids govern
the result. Main grid rows may flow over pages, with repeating header, rather
than a second main table or a continued title. Use source paragraph and row
prototypes for new entries. Manual calculation, next-action and researcher
review cells stay unfilled and unsigned.

Editable slots: title and opening finding; main table semantic entries;
candidate labels replacing Selected article/model labels; coverage reference,
counts, independent PPR, actual missing-coefficient note, method and relative
appendix link; the five confidence rows and two component rule tables; exact
Very low decisions grouped only by identical reasons; two geography figures
and their captions. Remove optional template-only prompt text. Preserve the
three manual slots. Large grouped taxon lists may clone decision-row prototypes
with an explicit identical reason, splitting lists into readable rows while
ensuring each taxon occurs once. Figures use existing single-cell table slots.

All local hyperlinks are relative to the candidate directory (the user chose
co-location of the review package); public URLs remain external. Style visible
links explicitly blue and underlined. Additions require document.xml,
document relationships and image parts; every unrelated existing package part
is preserve-only. Compare preserve-only hashes after authoring. Final page
count is content-dependent. Inspect every final rendered page for clipping,
readable columns, table header repetition, figure labels and page flow.
