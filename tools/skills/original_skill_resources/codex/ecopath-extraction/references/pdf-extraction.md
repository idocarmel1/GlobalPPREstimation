# Getting numbers out of these PDFs

Contents: [Why not -layout](#why-not--layout) · [The workflow](#the-workflow) ·
[pdfgrid](#pdfgrid) · [merge_gap](#merge_gap-the-parameter-that-matters) ·
[Rotated pages](#rotated-pages) · [Visual checking](#visual-checking) ·
[Troubleshooting](#troubleshooting)

## Why not `-layout`

`pdftotext -layout` reconstructs columns by inserting spaces from its own
heuristics. In a diet matrix with narrow gutters and many blank cells it
regularly emits a row whose numbers are all real numbers from the page but
sitting under the wrong predators. Nothing about the output looks broken. That
single failure mode is responsible for most silent corruption in this kind of
work, so the workflow uses word bounding boxes instead:

```bash
pdftotext -bbox-layout -f 14 -l 14 paper.pdf -    # XHTML with xMin/yMin per word
```

`scripts/pdfgrid.py` wraps this geometry-based approach. It prefers PyMuPDF,
which works on Windows, macOS, and Linux without separate Poppler executables,
and falls back to Poppler when available. It groups words into rendered lines by
vertical overlap, merges words into cells by horizontal gap, and assigns cells
to columns by geometry. A misassignment then shows up as a visibly ragged grid
or a diet column that doesn't sum to 1, instead of as a plausible wrong number.

## The workflow

Run every bundled script by absolute path from the installed skill directory:

```text
# 1. inspect the page visually
python <skill-root>/scripts/render_pdf_page.py <paper.pdf> 14 --dpi 200 --outdir <work-dir>

# 2. look at raw lines and coordinates before assuming anything
python <skill-root>/scripts/pdfgrid.py <paper.pdf> 14 --raw

# 3. reconstruct the grid, anchoring columns on the header row
python <skill-root>/scripts/pdfgrid.py <paper.pdf> 14 --merge-gap 0.4 --anchor-line 2 --sums

# 4. once it looks right, get machine-readable output
python <skill-root>/scripts/pdfgrid.py <paper.pdf> 14 --merge-gap 0.4 --anchor-line 2 --tsv
```

Always run `--raw` first. It tells you the line index of the header row (needed
for `--anchor-line`) and whether the table's header wrapped across two lines,
which is common and changes everything downstream.

## pdfgrid

```python
from pdfgrid import get_words, build_grid, print_grid, column_sums

lines = get_words("paper.pdf", 14, merge_gap=0.4)
grid  = build_grid(lines, anchor_line=2)
print_grid(grid)
print(column_sums(grid))
```

`get_words(pdf, page, merge_gap=2.0, line_tol=0.4)` → list of `Line`, each with
`.cells` (list of `Word`) and `.text`. `Word` carries `text, x0, y0, x1, y1` plus
`xc`, `yc`, `height`.

`build_grid(lines, anchor_line=None, col_tol=6.0, first_col_is_label=True,
numeric_anchors_only=True, snap_frac=0.6)` → rectangular list of rows of
strings. Empty string means no cell was there; keep that distinct from `"0"`.

**Prefer `anchor_line`.** When a header row of predator numbers exists, its cell
positions define the columns, and a blank body cell then stays blank in the
right place. Without an anchor the columns are clustered from the body, and one
sparse column can vanish or split — shifting everything to its right.
`numeric_anchors_only` drops non-numeric header cells (e.g. a `Prey \ Predator`
stub) so they don't become phantom columns.

Cells are matched to columns by the best agreement of left edge, centre, or
right edge. This matters because these tables mix left-aligned group names with
right-aligned numbers; centre-only matching drops right-aligned values into the
label column.

`column_sums(grid, skip_rows=1, skip_cols=1)` sums each numeric column — the
cheap first check on a diet matrix.

## `merge_gap`: the parameter that matters

`merge_gap` is the largest horizontal whitespace (in points) still counted as
*inside* one cell.

| Value | Use when | Failure if wrong |
|---|---|---|
| ~2.0 | normally-set tables | fine for most basic-input tables |
| ~0.4 | tightly-set matrices where inter-column gutters are barely wider than inter-word spaces | at 2.0, adjacent numeric columns **fuse into one cell** and the column structure is silently lost |

Diet matrices in the Azores and Mauritania papers need 0.4. Symptom-driven
tuning:

- group names arriving split across cells (`Small` | `zooplankton`) → raise it
- two numbers arriving in one cell (`0.250 0.100`) → lower it

At low `merge_gap` group names *will* split; that's expected and harmless,
because the label column re-joins them. Fusing numbers is the dangerous
direction, so when in doubt go lower.

## Rotated pages

Landscape tables are often stored as rotated portrait pages. Their text layer
may have coordinates that do not match the rendered orientation, so column
reconstruction can produce mirrored nonsense. Preserve the source and create a
rotated working copy:

```text
python <skill-root>/scripts/rotate_pdf.py <paper.pdf> <rotated.pdf> --pages 14-17 --degrees 90
```

Check the direction by rendering the rotated page (below) before extracting; if
the text comes out upside down, use `-90`. Guinea's `Tableau 8` is the worked
example of this.

## Visual checking

Any number that a check flags gets compared against the rendered page, not
against another extraction:

```text
python <skill-root>/scripts/render_pdf_page.py <paper.pdf> 14 --dpi 200 --outdir <work-dir>
```

Then view the image. Render at 200 dpi or higher — at 100 dpi, 6-point table
digits are unreliable to read, and misreading `0.058` as `0.038` while
"verifying" is worse than not checking.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Grid empty, no words | scanned page, no text layer | use an available OCR capability if authorised; otherwise transcribe from a 300 dpi render and note the method in the report |
| Two numeric columns in one cell | `merge_gap` too high | lower toward 0.4 |
| Every row shifted left by one from some row down | column clustered away | use `--anchor-line` |
| Header row has fewer cells than body | header wrapped over two lines | anchor on the line holding the numbers, not the words |
| Numbers appear in the label column | right-aligned column further from anchors than `snap_frac` allows | raise `snap_frac`, or anchor on a body row that's fully populated |
| A group name lands in a numeric column | label sits unusually far right | lower `snap_frac`, or fix that row by hand and note it |
| Diet column sums to ~0.5 or ~1.5 | a value read into the wrong column, or a continued table whose second half was missed | check whether the matrix continues on the next page |
| Decimal points missing (`0250`) | font without a mapped period glyph | verify against the rendered image; transcribe by hand |
| Values differ between the table and the text | genuine inconsistency in the paper | prefer the table, record both in the report |
