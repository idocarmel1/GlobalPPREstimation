"""Assemble the work order for one ecosystem, and stub the mapping files.

Run this first. It answers, from the repository rather than from memory, the four
questions every mapping starts with:

    which models does this ecosystem have, and are they usable?
    what are their exact group names, trophic levels, biomasses and model catches?
    which taxa must be mapped, and where is the tonnage concentrated?
    which of those taxa sit above genus and so may span several groups?

The taxon list is sorted by total catch, with a cumulative percentage, because effort
should follow tonnage. In a typical LME the top thirty taxa carry 90 % of the catch and
the tail of 200 rarities carries under 2 %; an hour spent on a rarity buys nothing.

Writes `data/<unit>/mapping/<model_stem>.csv` pre-filled with every taxon and an empty
decision, so the mapping is complete by construction and `validate_mapping.py` measures
progress rather than discovering omissions at the end.

    python prepare_mapping.py LME_047
    python prepare_mapping.py LME_047 --no-stub     # work order only
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapping_io as mio  # noqa: E402


def model_selection_rows(root: Path, unit: str) -> list:
    """Rows of `data/model_selection.xlsx` for this unit, so `usable` can be checked."""
    p = root / "data" / "model_selection.xlsx"
    if not p.exists():
        return []
    import openpyxl
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    hdr = None
    out = []
    for r in rows:
        if hdr is None:
            if r and r[0] == "unit_id":
                hdr = [str(h) if h is not None else "" for h in r]
            continue
        if not r or r[0] != unit:
            continue
        out.append({h: v for h, v in zip(hdr, r) if h})
    return out


def emit(root: Path, unit: str, out_path: Path, stub: bool) -> int:
    taxa, years = mio.read_catch(root, unit)
    if not taxa:
        print(f"no catch data for {unit}", file=sys.stderr)
        return 1
    tl = mio.read_trophic_levels(root, unit)
    books = mio.model_workbooks(root, unit)
    sel = model_selection_rows(root, unit)

    totals = {t: sum(v["by_year"].values()) for t, v in taxa.items()}
    grand = sum(totals.values())
    order = sorted(totals, key=lambda t: -totals[t])

    L = []
    w = L.append
    w(f"# Mapping work order — {unit}")
    w("")
    w(f"catch years        : {years[0]}-{years[-1]}" if years else "catch years        : none")
    w(f"taxa to map        : {len(taxa)}")
    w(f"total catch        : {grand:,.0f} tonnes over the whole period")
    w(f"Ecopath models     : {len(books)}")
    w("")

    if sel:
        w("## Model selection — check `usable` before mapping")
        w("")
        w("| author | title | usable | notes |")
        w("| --- | --- | --- | --- |")
        for r in sel:
            w("| {} | {} | **{}** | {} |".format(
                str(r.get("author") or "")[:40],
                str(r.get("title") or "")[:60],
                r.get("usable") or "?",
                str(r.get("notes") or "")[:60]))
        w("")
        w("A model marked `no` must not be mapped. Say so and stop.")
        w("")

    for book in books:
        groups = mio.read_groups(book)
        methods, _ = mio.read_methods(book)
        w(f"## Model `{book.stem}`")
        w("")
        w(f"{len(groups)} groups, {len(methods)} SPPR methods. "
          "Group names below are verbatim and authoritative — copy them exactly.")
        w("")
        w("| seq | group_name | type | TL | biomass | model catch |")
        w("| --- | --- | --- | --- | --- | --- |")
        for g in groups:
            def num(x):
                return f"{x:,.4g}" if isinstance(x, (int, float)) else ""
            w("| {} | `{}` | {} | {} | {} | {} |".format(
                g.get("seq"), g["group_name"], g.get("group_type") or "",
                num(g.get("tl")), num(g.get("biomass")), num(g.get("catch"))))
        w("")
        descr = [g for g in groups if (g.get("taxon_descr") or "").strip()]
        if descr:
            w("`taxon_descr` carries membership for "
              f"{len(descr)} of {len(groups)} groups — use it before the paper.")
            for g in descr:
                w(f"- `{g['group_name']}`: {g['taxon_descr']}")
        else:
            w("`taxon_descr` is empty for every group, so the paper and its supplements "
              "are the only source of membership. Record that limitation in the notes.")
        w("")

    w("## Taxa, by tonnage")
    w("")
    w("`coarse` marks a label above genus: it may legitimately span several groups, "
      "which is what the composite syntax is for.")
    w("")
    w("| # | cum % | tonnes | taxon | rank | common name | SAU functional group | "
      "SAU commercial group | TL |")
    w("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    cum = 0.0
    for i, t in enumerate(order, 1):
        cum += totals[t]
        rank = mio.taxon_rank(t)
        mark = f"**{rank}**" if mio.is_coarse(t) else rank
        w("| {} | {:.1f} | {:,.0f} | `{}` | {} | {} | {} | {} | {} |".format(
            i, 100 * cum / grand if grand else 0, totals[t], t, mark,
            taxa[t]["common_name"], taxa[t]["functional_group"],
            taxa[t]["commercial_group"],
            f"{tl[t]:.2f}" if t in tl else ""))
    w("")

    coarse = [t for t in order if mio.is_coarse(t)]
    ct = sum(totals[t] for t in coarse)
    w("## Where the difficulty is")
    w("")
    w(f"{len(coarse)} of {len(taxa)} labels sit above genus and together carry "
      f"**{ct:,.0f} tonnes ({100 * ct / grand if grand else 0:.1f} % of the catch)**.")
    w("Leaving these unresolved is what caps coverage near 78 %. Read "
      "`references/coarse-taxa-playbook.md` before deciding any of them.")
    w("")
    w("The ten largest:")
    w("")
    for t in coarse[:10]:
        w(f"- `{t}` — {totals[t]:,.0f} t "
          f"({100 * totals[t] / grand if grand else 0:.1f} %), "
          f"SAU: {taxa[t]['functional_group']} / {taxa[t]['commercial_group']}")
    w("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out_path}")
    print(f"  {len(taxa)} taxa, {len(books)} model(s), "
          f"{len(coarse)} coarse labels carrying {100 * ct / grand if grand else 0:.1f} % of catch")

    if stub:
        for book in books:
            dest = mio.mapping_dir(root, unit) / f"{book.stem}.csv"
            if dest.exists():
                print(f"  kept existing {dest.name}")
                continue
            mio.write_mapping_csv(dest, [{
                "taxon": t,
                "common_name": taxa[t]["common_name"],
                "functional_group": taxa[t]["functional_group"],
                "commercial_group": taxa[t]["commercial_group"],
                "group": "", "weights": "", "confidence": "", "evidence": "",
                "explanation": "",
            } for t in order])
            print(f"  stubbed {dest.name} with {len(order)} rows")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("unit", help="unit id, e.g. LME_047")
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--no-stub", action="store_true",
                    help="do not create empty mapping CSVs")
    a = ap.parse_args()
    root = a.root.resolve() if a.root else mio.find_root()
    out = a.out or (mio.mapping_dir(root, a.unit) / "WORK_ORDER.md")
    return emit(root, a.unit, out, stub=not a.no_stub)


if __name__ == "__main__":
    raise SystemExit(main())
