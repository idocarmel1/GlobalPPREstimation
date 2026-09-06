"""pdfgrid — column-aware text extraction for numeric tables in scientific PDFs.

Why this exists: `pdftotext -layout` collapses whitespace heuristically and
silently shifts numbers between columns in densely-set tables (diet matrices,
Ecopath basic-input tables). A number landing one column left is a wrong number
that looks perfectly plausible, so it survives review. This module instead reads
word bounding boxes (`pdftotext -bbox-layout`) and reconstructs columns from
x-coordinates, so a misassignment shows up as a visibly ragged grid.

Typical use:

    from pdfgrid import get_words, build_grid, print_grid

    lines = get_words("paper.pdf", 14, merge_gap=0.4)   # tight-set table
    grid  = build_grid(lines, anchor_line=1)            # header row defines columns
    print_grid(grid)

CLI:

    python pdfgrid.py paper.pdf 14 --merge-gap 0.4 --anchor-line 1
    python pdfgrid.py paper.pdf 14 --raw            # inspect lines/coords first
"""

from __future__ import annotations

import argparse
import html
import re
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

__all__ = [
    "Word",
    "Line",
    "bbox_xml",
    "get_words",
    "build_grid",
    "print_grid",
    "grid_to_tsv",
    "column_sums",
]


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------


@dataclass
class Word:
    """A word (or a run of words merged into one cell) with its bounding box."""

    text: str
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def xc(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def yc(self) -> float:
        return (self.y0 + self.y1) / 2

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    def merged_with(self, other: "Word") -> "Word":
        return Word(
            text=f"{self.text} {other.text}",
            x0=min(self.x0, other.x0),
            y0=min(self.y0, other.y0),
            x1=max(self.x1, other.x1),
            y1=max(self.y1, other.y1),
        )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Word({self.text!r} x={self.x0:.1f}-{self.x1:.1f} y={self.y0:.1f})"


@dataclass
class Line:
    """One rendered text line: cells left-to-right."""

    cells: list[Word] = field(default_factory=list)

    @property
    def y(self) -> float:
        return min(c.y0 for c in self.cells) if self.cells else 0.0

    @property
    def text(self) -> str:
        return " | ".join(c.text for c in self.cells)

    def __len__(self) -> int:
        return len(self.cells)

    def __iter__(self):
        return iter(self.cells)

    def __getitem__(self, i):
        return self.cells[i]


# --------------------------------------------------------------------------
# extraction
# --------------------------------------------------------------------------


def bbox_xml(pdf: str, page: int) -> str:
    """Return the `-bbox-layout` XHTML for a single page."""
    out = subprocess.run(
        ["pdftotext", "-bbox-layout", "-f", str(page), "-l", str(page), pdf, "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout


def _parse_words(xml_text: str) -> list[Word]:
    """Pull every <word> element out of the bbox XHTML, in document order."""
    words: list[Word] = []
    try:
        root = ET.fromstring(xml_text)
        for el in root.iter():
            if not el.tag.endswith("word"):
                continue
            text = (el.text or "").strip()
            if not text:
                continue
            words.append(
                Word(
                    text=html.unescape(text),
                    x0=float(el.get("xMin")),
                    y0=float(el.get("yMin")),
                    x1=float(el.get("xMax")),
                    y1=float(el.get("yMax")),
                )
            )
        return words
    except ET.ParseError:
        # Poppler occasionally emits XHTML with an entity it did not declare.
        # Fall back to a regex sweep rather than losing the page entirely.
        pat = re.compile(
            r'<word\s+xMin="([\d.]+)"\s+yMin="([\d.]+)"\s+'
            r'xMax="([\d.]+)"\s+yMax="([\d.]+)"\s*>(.*?)</word>',
            re.S,
        )
        for x0, y0, x1, y1, text in pat.findall(xml_text):
            t = html.unescape(text).strip()
            if t:
                words.append(Word(t, float(x0), float(y0), float(x1), float(y1)))
        return words


def get_words(
    pdf: str,
    page: int,
    merge_gap: float = 2.0,
    line_tol: float = 0.4,
) -> list[Line]:
    """Extract `page` as a list of Lines, adjacent words merged into cells.

    merge_gap is the maximum horizontal whitespace (in PDF points) that still
    counts as *within* one cell. It is the parameter that actually matters:

      * ~2.0 works for normally-set tables ("Small zooplankton" stays one cell).
      * ~0.4 is needed for tightly-set matrices where inter-column whitespace is
        barely wider than inter-word whitespace — at 2.0 the columns fuse and
        you silently lose the column structure. Azores- and Mauritania-style
        diet matrices need 0.4.

    If a group name comes back split across cells, raise merge_gap; if two
    numeric columns come back fused into one cell, lower it. Always eyeball the
    result before trusting it.
    """
    words = _parse_words(bbox_xml(pdf, page))
    if not words:
        return []

    # Group into rendered lines by vertical overlap, not exact y equality:
    # subscripts and different font sizes shift yMin within a single line.
    words.sort(key=lambda w: (w.y0, w.x0))
    med_h = sorted(w.height for w in words)[len(words) // 2] or 1.0
    tol = line_tol * med_h

    rows: list[list[Word]] = []
    for w in words:
        for row in rows:
            if abs(w.yc - (sum(x.yc for x in row) / len(row))) <= tol:
                row.append(w)
                break
        else:
            rows.append([w])

    lines: list[Line] = []
    for row in rows:
        row.sort(key=lambda w: w.x0)
        cells: list[Word] = [row[0]]
        for w in row[1:]:
            if w.x0 - cells[-1].x1 <= merge_gap:
                cells[-1] = cells[-1].merged_with(w)
            else:
                cells.append(w)
        lines.append(Line(cells))

    lines.sort(key=lambda ln: ln.y)
    return lines


# --------------------------------------------------------------------------
# grid reconstruction
# --------------------------------------------------------------------------


_NUMISH = re.compile(r"^[<>~(]?\s*[\d.,]+\s*[)%]?$")


def _cluster_anchors(lines, col_tol):
    """Derive column anchors by clustering cell positions across all lines."""
    cells = sorted((c for ln in lines for c in ln.cells), key=lambda c: c.xc)
    if not cells:
        return []
    anchors, cluster = [], [cells[0]]
    for c in cells[1:]:
        if c.xc - cluster[-1].xc <= col_tol:
            cluster.append(c)
        else:
            anchors.append(_mean_anchor(cluster))
            cluster = [c]
    anchors.append(_mean_anchor(cluster))
    return anchors


def _mean_anchor(cells):
    n = len(cells)
    return (
        sum(c.x0 for c in cells) / n,
        sum(c.xc for c in cells) / n,
        sum(c.x1 for c in cells) / n,
    )


def build_grid(
    lines: list[Line],
    anchor_line: int | None = None,
    col_tol: float = 6.0,
    first_col_is_label: bool = True,
    numeric_anchors_only: bool = True,
    snap_frac: float = 0.6,
) -> list[list[str]]:
    """Assign cells to columns and return a rectangular grid of strings.

    anchor_line: index into `lines` of the row whose cells define the column
      positions — normally the header row of predator numbers. Anchoring beats
      clustering whenever a header exists, because a blank cell in the body then
      stays blank in the right place instead of shifting every later value left.

    numeric_anchors_only: keep only numeric cells from the anchor row. Header
      rows usually also carry a stub label ("Prey \\ Predator"), which would
      otherwise become phantom columns and drag row labels into them.

    col_tol: when no anchor row is given, cells whose centres fall within this
      many points are treated as one column.

    snap_frac: a cell is matched to the nearest anchor only if it lies within
      snap_frac x (median column pitch) of it; anything farther is treated as a
      row label. Distance is the best of left-edge, centre and right-edge
      agreement, because these tables mix left-aligned names with right-aligned
      numbers and a centre-only match drops right-aligned values into the label.

    Empty string means "no cell there" — keep that distinct from "0", since a
    structural blank and a stated zero mean different things downstream.
    """
    if not lines:
        return []

    if anchor_line is not None:
        cells = lines[anchor_line].cells
        if numeric_anchors_only and any(_NUMISH.match(c.text) for c in cells):
            cells = [c for c in cells if _NUMISH.match(c.text)]
        anchors = [(c.x0, c.xc, c.x1) for c in cells]
    else:
        anchors = _cluster_anchors(lines, col_tol)
    if not anchors:
        return [[ln.text] for ln in lines]

    centres = [a[1] for a in anchors]
    pitch = (
        sorted(b - a for a, b in zip(centres, centres[1:]))[max(len(centres) // 2 - 1, 0)]
        if len(centres) > 1
        else col_tol * 4
    )
    max_snap = snap_frac * pitch

    def distance(cell, anchor):
        a0, ac, a1 = anchor
        return min(abs(cell.x0 - a0), abs(cell.xc - ac), abs(cell.x1 - a1))

    offset = 1 if first_col_is_label else 0
    grid: list[list[str]] = []
    for ln in lines:
        row = [""] * (len(anchors) + offset)
        for cell in ln.cells:
            j = min(range(len(anchors)), key=lambda k: distance(cell, anchors[k]))
            if first_col_is_label and distance(cell, anchors[j]) > max_snap:
                row[0] = f"{row[0]} {cell.text}".strip()
                continue
            slot = j + offset
            row[slot] = f"{row[slot]} {cell.text}".strip() if row[slot] else cell.text
        grid.append(row)
    return grid


def grid_to_tsv(grid: list[list[str]]) -> str:
    return "\n".join("\t".join(r) for r in grid)


def print_grid(grid: list[list[str]], width: int = 14) -> None:
    """Print the grid with fixed-width columns so misalignment is obvious."""
    for r in grid:
        print("".join(c[: width - 1].ljust(width) for c in r))


def column_sums(
    grid: list[list[str]], skip_rows: int = 1, skip_cols: int = 1
) -> list[float | None]:
    """Sum each numeric column — the cheap check on a diet matrix.

    Ecopath diet proportions sum to 1.0 per predator (plus any import). A column
    that lands on 0.87 or 1.13 is usually a parse error, not a rounding artefact;
    published matrices that round to 3 decimals land inside ±0.01. Investigate
    the deviation against a rendered image of the page before changing a number.
    """
    if not grid:
        return []
    ncols = max(len(r) for r in grid)
    sums: list[float | None] = []
    for j in range(skip_cols, ncols):
        total, seen = 0.0, False
        for r in grid[skip_rows:]:
            if j >= len(r) or not r[j]:
                continue
            try:
                total += float(r[j].replace(",", ".").replace("<", "").strip())
                seen = True
            except ValueError:
                continue
        sums.append(round(total, 6) if seen else None)
    return sums


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf")
    ap.add_argument("page", type=int)
    ap.add_argument("--merge-gap", type=float, default=2.0)
    ap.add_argument("--col-tol", type=float, default=6.0)
    ap.add_argument("--anchor-line", type=int, default=None)
    ap.add_argument("--raw", action="store_true", help="print lines with coordinates")
    ap.add_argument("--tsv", action="store_true", help="print grid as TSV")
    ap.add_argument("--sums", action="store_true", help="print column sums")
    args = ap.parse_args()

    lines = get_words(args.pdf, args.page, merge_gap=args.merge_gap)

    if args.raw:
        for i, ln in enumerate(lines):
            print(f"[{i:3d}] y={ln.y:7.1f}  {ln.text}")
        return

    grid = build_grid(lines, anchor_line=args.anchor_line, col_tol=args.col_tol)
    print(grid_to_tsv(grid) if args.tsv else "")
    if not args.tsv:
        print_grid(grid)
    if args.sums:
        print("\ncolumn sums:", column_sums(grid))


if __name__ == "__main__":
    main()
