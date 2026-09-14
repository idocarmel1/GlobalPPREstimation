"""Render one PDF page to PNG for visual verification."""

from __future__ import annotations

import argparse
from pathlib import Path

from pdf_backend import available_backends, render_page


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf")
    parser.add_argument("page", type=int, help="1-based page number")
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--outdir", default=".")
    parser.add_argument("--backend", choices=["auto", "pymupdf", "poppler"], default="auto")
    args = parser.parse_args()

    if args.dpi < 72:
        parser.error("--dpi must be at least 72")
    source = Path(args.pdf)
    output = Path(args.outdir) / f"{source.stem}_page_{args.page}_{args.dpi}dpi.png"
    result = render_page(source, args.page, output, args.dpi, args.backend)
    print(result.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
