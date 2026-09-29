# Template execution contract

Reference: C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/tools/templates/Model_validation_template.docx
SHA-256: aba08002e3e2798852f7551b794beff543f71761654a72d5af645c32abe5d228
Reference render: qa/template-render/template.pdf and page-1.png through page-4.png, all visually inspected. Four pages, one A4 portrait section (8.270139 × 11.690278 inches), 0.65-inch margins on all sides. Preserve section properties, headers/footers, theme, styles, numbering and all opaque package parts.

Normal Calibri 11 pt; Title Calibri 23 pt black. Source cell runs 10.5 pt; paragraph after spacing 2 pt. Main tables have 1.529861 / 5.440278-inch columns, pale blue-gray E5ECF0 header, white body, gray D9D9D9 5-eighth-point borders; cell margins top/bottom 90 twips and left/right 110 twips. Rows have no fixed heights. Preserve all table properties, cell shading, borders, alignment and margins. No header/footer content is added.

Body pattern: page 1 title and two introductory paragraphs, table 0; next page continuation title and table 1; next page LLM completion instructions; final screenshot section and tables 2 and 3 with captions. These patterns and all field labels/order are retained. Content may expand the number of pages; source type size is not reduced. The article screenshot heading may receive a page break to keep its larger figure and caption together.

Editable slots: document.xml tables 0 rows 1–7 right cells; table 1 rows 1–7 right cells; tables 2/3 row 1 image cells; body paragraphs 21/23 figure captions and paragraph 24 availability placeholder. All other body text stays unchanged, including the LLM instructions. Manual preserve-only cells: table 0 row 8 SPPR calculation; table 1 rows 8 and 9. Their complete XML must compare equal. Selection rationale comes verbatim from Overview. Table field labels and order must compare equal.

Pictures reuse screenshot spaces; add only required image relationships/media/content types. Build with python-docx for pictures, then repackage from original bytes for every preserve-only ZIP part. Existing template untouched. No regional validation DOCX existed before this test. Package inventory in template_package_inventory.json includes every source part.

Fidelity gates: complete manual-cell XML equality, all original styles/section/table structure retained; only permitted text/image slots changed; relative Word links resolve from the region root; copied Markdown links resolve; all final pages rendered in read-only hidden Word and inspected. No automatic reviewer/date/approval data. Source evidence does not command execution.
