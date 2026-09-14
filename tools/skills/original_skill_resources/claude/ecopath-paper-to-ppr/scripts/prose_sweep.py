"""prose_sweep.py — find parameter values that live in the text, not the tables.

Run:  python prose_sweep.py paper.pdf
      python prose_sweep.py paper.pdf --family assimilation,pointers --context 2
      python prose_sweep.py paper.pdf --terms "phagotroph,ciliate" --pages 3-12

Why this exists: a table looks complete, so it gets extracted and the prose
never gets read. But in these papers the assimilation fraction is often stated
only in the methods paragraph, the microbial-loop diets are described in
sentences, and a footnote reading "see text" is the only sign that a blank cell
has a value elsewhere. This script turns "read the whole paper carefully" into a
checklist you can actually finish.

It reports *candidates*, not values. Every hit still has to be read in context
on the page before anything is extracted from it.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict

from pdf_backend import page_count, page_text

# Families are deliberately over-inclusive: a false positive costs a glance, a
# missed prose parameter costs a wrong number in the database.
FAMILIES: dict[str, list[str]] = {
    # Footnote and caption pointers — read these FIRST. A pointer means the
    # table is knowingly incomplete and the author told you where the rest is.
    "pointers": [
        r"see\s+(?:the\s+)?text",
        r"in\s+the\s+text",
        r"(?:described|explained|given|discussed|listed|detailed)\s+in\s+the\s+text",
        r"from\s+the\s+text",
        r"cf\.\s*text",
        r"see\s+(?:section|methods|above|below)",
        r"voir\s+(?:le\s+)?texte",  # francophone FCRR chapters
        r"dans\s+le\s+texte",
        r"v[ée]ase\s+el\s+texto",
        r"en\s+el\s+texto",
        r"as\s+(?:in|for)\s+(?:table|Tab\.|tableau)",
        r"\bibid\b",
    ],
    "assimilation": [
        r"unassimilat\w*",
        r"assimilat\w*",
        r"egest\w*",
        r"excret\w*",
        r"\bGS\b",
        r"faece\w*|fecal",
    ],
    "diet": [
        r"\bdiet\w*",
        r"stomach\s+content\w*",
        r"\bpre(?:y|dat\w+)\b",
        r"feed\w*\s+(?:on|upon)",
        r"graz\w*\s+(?:on|upon)",
        r"consum\w*\s+(?:on|mainly|primarily|exclusively)",
        r"phagotroph\w*|heterotroph\w*|bacterivor\w*|microbial\s+loop",
        r"ciliate\w*|flagellate\w*|protozoa\w*",
        r"cannibalis\w*",
    ],
    "rates": [
        r"\bP\s*/\s*B\b|production\s*(?:/|:|\s+to\s+)\s*biomass",
        r"\bQ\s*/\s*B\b|consumption\s*(?:/|:|\s+to\s+)\s*biomass",
        r"\bP\s*/\s*Q\b|gross\s+(?:food\s+)?conversion",
        r"ecotrophic\s+efficienc\w*|\bEE\b",
        r"\bZ\b\s*(?:=|value|was)|total\s+mortality",
        r"natural\s+mortality|\bM\s*=",
        r"fishing\s+mortality|\bF\s*=",
        r"turnover\s+rate",
    ],
    "biomass": [
        r"biomass\w*\s+(?:was|were|of|estimat\w+|assum\w+|taken)",
        r"\bt\s*(?:\.|·)?\s*km\s*(?:-2|−2|\^?-?2|/km)",
        r"wet\s+weight|\bw\.?w\.?\b|dry\s+weight",
        r"swept[- ]area|acoustic\s+(?:survey|estimat\w+)|VPA|virtual\s+population",
    ],
    "catch": [
        r"landing\w*",
        r"discard\w*",
        r"by[- ]?catch",
        r"catch\w*\s+(?:was|were|of|statistic\w*|data)",
        r"\bfleet\w*",
        r"offal",
    ],
    "detritus": [
        r"detrit\w*",
        r"\bexport\w*\s+(?:to|of|out)",
        r"sediment\w*",
        r"\bDOM\b|dissolved\s+organic",
    ],
    "trophic": [r"trophic\s+level\w*", r"\bTL\b", r"omnivor\w*\s+index"],

    # Biomass accumulation / migration. A non-steady-state model breaks the
    # EE identity, so BA has to be found before a mass-balance mismatch can be
    # read as an extraction error. It is often reported only in a mortality
    # table, a stock-trend figure, or a single sentence about a declining or
    # recovering stock.
    "accumulation": [
        r"biomass\s+accumulat\w*",
        r"accumulation\s+(?:rate|of\s+biomass|term)",
        r"\bBA\b",
        r"\bdB\s*/\s*dt\b",
        r"(?:net\s+)?(?:in|de)crease\s+in\s+(?:the\s+)?(?:stock|biomass)",
        r"(?:stock|biomass)\s+(?:was\s+)?(?:in|de)creas\w+",
        r"(?:stock|biomass)\s+(?:decline|declining|depletion|recover\w*|build[- ]?up)",
        r"non[- ]?steady[- ]?state",
        r"not\s+(?:in\s+)?(?:a\s+)?steady\s+state",
        r"steady[- ]?state\s+assumption",
        r"(?:emigration|immigration|net\s+migration)",
        r"accumulation\s+de\s+biomasse",     # francophone FCRR chapters
        r"biomasse\s+accumul\w*",
    ],
    # Phrases that mark a number as borrowed, assumed, or adjusted — these
    # change the number's provenance even when the value itself came off a table.
    "provenance": [
        r"assum\w+",
        r"estimat\w+\s+(?:by|from|as|using)",
        r"taken\s+from",
        r"borrow\w+|adopt\w+\s+from",
        r"same\s+as\s+(?:for|in|that)",
        r"following\s+[A-Z][a-z]+(?:\s+et\s+al\.)?",
        r"pers\.?\s*comm\.?|personal\s+communication",
        r"balanc\w+\s+(?:the\s+)?model|to\s+achieve\s+(?:mass\s+)?balance",
        r"adjust\w+|modif\w+\s+(?:to|so)",
        r"calculated\s+(?:by|as|from)",
        r"by\s+difference",
        r"unpublished",
    ],
}


def page_texts(
    pdf: str, first: int | None, last: int | None, backend: str = "auto"
) -> dict[int, str]:
    n = page_count(pdf, backend)
    lo = first or 1
    hi = min(last or n, n)
    return {p: page_text(pdf, p, backend) for p in range(lo, hi + 1)}


def sentences(text: str) -> list[str]:
    """Split loosely. Table pages have no sentences, so fall back to lines."""
    flat = re.sub(r"-\n(\w)", r"\1", text)  # rejoin hyphenated line breaks
    flat = re.sub(r"\s*\n\s*", " ", flat)
    parts = re.split(r"(?<=[.;:])\s+(?=[A-Z(])", flat)
    return [p.strip() for p in parts if p.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf")
    ap.add_argument(
        "--family",
        help=f"comma-separated subset of: {','.join(FAMILIES)} (default: all)",
    )
    ap.add_argument("--terms", help="extra comma-separated regexes to search")
    ap.add_argument("--pages", help="page range, e.g. 3-12")
    ap.add_argument("--context", type=int, default=0, help="extra sentences either side")
    ap.add_argument("--numbers-only", action="store_true",
                    help="only report hits whose sentence also contains a number")
    ap.add_argument(
        "--backend", choices=["auto", "pymupdf", "poppler"], default="auto",
        help="PDF text backend (default: prefer PyMuPDF, then Poppler)",
    )
    args = ap.parse_args()

    fams = {k: v for k, v in FAMILIES.items()}
    if args.family:
        want = [f.strip() for f in args.family.split(",")]
        unknown = [f for f in want if f not in fams]
        if unknown:
            print(f"unknown family: {unknown}; available: {list(fams)}", file=sys.stderr)
            return 2
        fams = {k: fams[k] for k in want}
    if args.terms:
        fams["custom"] = [t.strip() for t in args.terms.split(",") if t.strip()]

    first = last = None
    if args.pages:
        bits = args.pages.split("-")
        first = int(bits[0])
        last = int(bits[-1])

    pages = page_texts(args.pdf, first, last, args.backend)
    hits: dict[str, list[tuple[int, str]]] = defaultdict(list)
    has_num = re.compile(r"\d")

    for p, text in pages.items():
        sents = sentences(text)
        for i, s in enumerate(sents):
            for fam, pats in fams.items():
                if any(re.search(pat, s, re.I) for pat in pats):
                    if args.numbers_only and fam != "pointers" and not has_num.search(s):
                        continue
                    lo = max(0, i - args.context)
                    hi = min(len(sents), i + args.context + 1)
                    hits[fam].append((p, " ".join(sents[lo:hi])))
                    break

    order = ["pointers"] + [k for k in fams if k != "pointers"]
    total = 0
    for fam in order:
        if fam not in hits:
            continue
        print(f"\n{'=' * 70}\n{fam.upper()}  ({len(hits[fam])} hit(s))\n{'=' * 70}")
        for p, s in hits[fam]:
            total += 1
            print(f"\n  p.{p}: {s[:600]}{'...' if len(s) > 600 else ''}")

    print(f"\n{total} candidate passage(s) across {len(pages)} page(s).")
    if "pointers" in hits:
        print(
            "Read the POINTERS hits first: each one is the author saying a table is "
            "incomplete and the value is elsewhere."
        )
    print("These are candidates, not values. Read each in context on the page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
