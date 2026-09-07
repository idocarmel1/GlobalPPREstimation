"""Create a rotated PDF working copy without modifying the source PDF."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_pages(spec: str, page_count: int) -> set[int]:
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = (int(x) for x in part.split("-", 1))
        else:
            start = end = int(part)
        if start < 1 or end < start or end > page_count:
            raise ValueError(f"invalid page range {part!r}; document has {page_count} pages")
        pages.update(range(start, end + 1))
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pdf")
    parser.add_argument("output_pdf")
    parser.add_argument("--pages", required=True, help="1-based list/ranges, e.g. 14-17,22")
    parser.add_argument("--degrees", required=True, type=int, choices=[-90, 90, 180])
    args = parser.parse_args()

    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError as exc:
            parser.error("PyMuPDF is required for portable PDF rotation")

    source = Path(args.input_pdf)
    target = Path(args.output_pdf)
    if source.resolve() == target.resolve():
        parser.error("input and output must differ; preserve the source PDF")
    target.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open(source) as doc:
        try:
            pages = parse_pages(args.pages, len(doc))
        except ValueError as exc:
            parser.error(str(exc))
        for number in pages:
            page = doc[number - 1]
            page.set_rotation((page.rotation + args.degrees) % 360)
        doc.save(target)
    print(target.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
