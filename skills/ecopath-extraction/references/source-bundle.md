# Source-bundle inventory

Use this reference whenever the input contains more than one file type or more
than one model. Do not begin row-level extraction until the inventory is stable.

## Build the inventory

For every supplied file, record:

| Field | What to capture |
|---|---|
| File | exact filename and format |
| Role | article, appendix, supplement, data table, prior extraction, or code |
| Model coverage | model name, area, period/year, and version where known |
| Contents | relevant pages, tables, figures, sections, or worksheet names |
| Authority | published source, author supplement, derived calculation, or prior work |

One paper may contain several Ecopath models. Create one model directory and one
provenance record per distinct parameterisation, even when their functional
groups are identical. Never let the first model's group order carry into the
second without an explicit comparison.

## Inspect each format

- **PDF:** use the PDF workflow and visual page verification. Record both PDF
  page number and printed page number when they differ.
- **XLSX/XLS/CSV/TSV:** use available spreadsheet capabilities. Inventory all
  sheets, including hidden sheets. Preserve displayed values and number
  precision; inspect formulas separately when they matter. Cite workbook,
  sheet, cell/range, and table title.
- **DOCX:** use available document capabilities to inspect paragraphs, tables,
  captions, footnotes, and endnotes. Render when layout determines table
  meaning. Cite document section/table and page in the rendered document.
- **Notebook or script:** use it to understand earlier transformations and
  naming, but do not treat its outputs as paper-stated values. Trace any value
  back to the publication or label it as derived.
- **Image or scanned page:** render/OCR if available, then verify every numeric
  transcription visually. Record OCR or manual transcription in `REPORT.md`.

## Resolve source conflicts

Use this authority order only as an investigation guide, not as permission to
discard conflicting evidence:

1. Author-supplied machine-readable model table
2. Final table in the paper or appendix
3. Explicit numeric prose or footnote
4. Figure-derived value
5. Prior calculation or secondary citation

When two authoritative sources disagree, preserve the value chosen for the
import files, record both values and locations in `REPORT.md`, and explain the
choice. Do not average, normalize, or silently substitute.

## Check completeness across files

Before declaring a field absent, search every file assigned to that model. A
blank in the article may point to an appendix; a supplement may omit definitions
that appear only in the methods; and a workbook may contain several model years
on separate sheets. `Deliberate blanks` in `REPORT.md` must therefore state the
whole source bundle searched, not only the main PDF.
