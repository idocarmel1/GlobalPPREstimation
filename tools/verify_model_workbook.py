"""Check a model workbook's internals, including the formulas nothing else evaluates.

`PPR by taxon` is formula-driven so the reader can change the year. openpyxl writes those
formulas without evaluating them, so a wrong column letter produces a workbook that opens
cleanly and shows wrong numbers -- or `#N/A` in one corner nobody scrolls to. This script
resolves the INDEX/MATCH by hand against the sheets they point at and compares the result
with the arithmetic those cells are supposed to perform.

Checks:

    every formula in `PPR by taxon` resolves to catch(taxon, year) x SPPR(taxon, method)
    the per-taxon values sum to the matching year column of `PPR by method`
    every group named in `Taxon-Group Map` exists on `Model groups`
    composite weights sum to 1 and match the number of groups
    the `SPPR` sheet's group column agrees with `Taxon-Group Map`
    the `Catch` totals are unchanged from the source archive

    python tools/verify_model_workbook.py                 # every model workbook
    python tools/verify_model_workbook.py --units LME_035
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "ewe-species-to-group-mapper" / "scripts"))
import mapping_io as mio  # noqa: E402

TOL = 1e-6

# =IFERROR($C8*INDEX(SPPR!$E:$X,MATCH($A8,SPPR!$A:$A,0),3),"")
PPR_CELL = re.compile(
    r"^=IFERROR\(\$C(\d+)\*INDEX\(SPPR!\$([A-Z]+):\$([A-Z]+),"
    r"MATCH\(\$A\1,SPPR!\$A:\$A,0\),(\d+)\),\"\"\)$")
# =IFERROR(INDEX(Catch!$E:$BV,MATCH($A8,Catch!$A:$A,0),MATCH($B$4,Catch!$E$1:$BV$1,0)),0)
CATCH_CELL = re.compile(
    r"^=IFERROR\(INDEX\(Catch!\$([A-Z]+):\$([A-Z]+),MATCH\(\$A(\d+),Catch!\$A:\$A,0\),"
    r"MATCH\(\$B\$4,Catch!\$([A-Z]+)\$1:\$([A-Z]+)\$1,0\)\),0\)$")


def col_index(letter: str) -> int:
    n = 0
    for ch in letter:
        n = n * 26 + (ord(ch) - 64)
    return n


def grid(ws):
    return [list(r) for r in ws.iter_rows(values_only=True)]


def check(path: Path, unit: str) -> list:
    bad = []
    wbf = openpyxl.load_workbook(path)                     # formulas as written
    for need in ("Catch", "SPPR", "PPR by method", "PPR by taxon", "Taxon-Group Map",
                 "Model groups"):
        if need not in wbf.sheetnames:
            return [f"{path.name}: missing sheet {need!r}"]

    catch = grid(wbf["Catch"])
    sppr = grid(wbf["SPPR"])
    bymethod = grid(wbf["PPR by method"])
    bytaxon = wbf["PPR by taxon"]
    tmap = grid(wbf["Taxon-Group Map"])
    mgroups = grid(wbf["Model groups"])

    # --- indexes into the sheets the formulas point at ------------------------------
    catch_hdr = catch[0]
    catch_row = {r[0]: i for i, r in enumerate(catch) if i and r[0]}
    sppr_hdr = sppr[3]
    sppr_row = {r[0]: i for i, r in enumerate(sppr) if i > 3 and r[0]}
    methods = [m for m in sppr_hdr[4:] if m]

    year = bytaxon["B4"].value
    if year not in catch_hdr:
        bad.append(f"selected year {year!r} is not a Catch header")
        return bad
    ycol = catch_hdr.index(year)

    # --- the formulas ---------------------------------------------------------------
    hdr_row = None
    for i, r in enumerate(bytaxon.iter_rows(values_only=True), start=1):
        if r and r[0] == "taxon":
            hdr_row = i
            break
    if hdr_row is None:
        return [f"{path.name}: no header row on 'PPR by taxon'"]
    first = hdr_row + 2

    checked = 0
    per_taxon_sum = [0.0] * len(methods)
    for row in range(first, bytaxon.max_row + 1):
        taxon = bytaxon.cell(row, 1).value
        if not taxon:
            continue
        if taxon not in catch_row:
            bad.append(f"row {row}: {taxon!r} is not on the Catch sheet")
            continue

        m = CATCH_CELL.match(str(bytaxon.cell(row, 3).value or ""))
        if not m:
            bad.append(f"row {row}: catch formula not in the expected shape: "
                       f"{bytaxon.cell(row, 3).value!r}")
            continue
        lo, hi, _r, lo2, hi2 = m.groups()
        if (lo, hi) != (lo2, hi2):
            bad.append(f"row {row}: catch INDEX range {lo}:{hi} differs from the "
                       f"MATCH range {lo2}:{hi2}")
        base = col_index(lo) - 1
        # MATCH(year) inside E1:BV1 is 1-based within that range
        pos = catch_hdr[base:col_index(hi)].index(year) + 1
        resolved_catch = catch[catch_row[taxon]][base + pos - 1] or 0.0
        expected_catch = catch[catch_row[taxon]][ycol] or 0.0
        if abs(resolved_catch - expected_catch) > TOL:
            bad.append(f"row {row} {taxon}: catch formula resolves to {resolved_catch} "
                       f"but the {year} column holds {expected_catch}")

        for j, method in enumerate(methods):
            cell = bytaxon.cell(row, 4 + j)
            f = PPR_CELL.match(str(cell.value or ""))
            if not f:
                bad.append(f"row {row} col {4 + j}: formula not in the expected shape: "
                           f"{cell.value!r}")
                continue
            frow, slo, shi, k = f.groups()
            if int(frow) != row:
                bad.append(f"row {row}: formula points at row {frow}")
            sbase = col_index(slo) - 1
            if int(k) < 1 or sbase + int(k) - 1 >= col_index(shi):
                bad.append(f"row {row} {method}: INDEX offset {k} is outside "
                           f"{slo}:{shi}")
                continue
            got_col = sbase + int(k) - 1
            if sppr_hdr[got_col] != method:
                bad.append(f"row {row}: column {4 + j} is headed {method!r} but its "
                           f"formula reads SPPR column {sppr_hdr[got_col]!r}")
                continue
            v = sppr[sppr_row[taxon]][got_col]
            if isinstance(v, (int, float)):
                per_taxon_sum[j] += expected_catch * v
        checked += 1

    if not checked:
        bad.append("no taxon rows found on 'PPR by taxon'")

    # --- the aggregate sheet must agree with the per-taxon sheet ---------------------
    bm_hdr = next((r for r in bymethod if r and r[0] == "method"), None)
    if bm_hdr is None:
        bad.append("no header row on 'PPR by method'")
    else:
        ycol2 = bm_hdr.index(year)
        rows_by_method = {r[0]: r for r in bymethod if r and r[0] in methods}
        for j, method in enumerate(methods):
            r = rows_by_method.get(method)
            if r is None:
                bad.append(f"'PPR by method' has no row for {method}")
                continue
            agg = r[ycol2]
            if agg is None:
                if per_taxon_sum[j] > TOL:
                    bad.append(f"{method} {year}: aggregate is blank but the taxa sum to "
                               f"{per_taxon_sum[j]:,.3f}")
                continue
            if abs(agg - per_taxon_sum[j]) > max(1e-3, abs(agg) * 1e-9):
                bad.append(f"{method} {year}: 'PPR by method' says {agg:,.3f}, the taxa "
                           f"sum to {per_taxon_sum[j]:,.3f}")

    # --- mapping integrity -----------------------------------------------------------
    known = {r[1] for r in mgroups[4:] if r and r[1]}
    map_hdr = next(i for i, r in enumerate(tmap) if r and r[0] == "taxon")
    map_group = {}
    for r in tmap[map_hdr + 1:]:
        if not r or not r[0]:
            continue
        names = mio.parse_groups_cell(r[4])
        map_group[r[0]] = r[4]
        for n in names:
            if n != "Unresolved" and n not in known:
                bad.append(f"{r[0]}: group {n!r} is not on 'Model groups'")
        w = [x for x in str(r[5] or "").split("|") if x.strip()]
        if w:
            if len(w) != len(names):
                bad.append(f"{r[0]}: {len(w)} weights for {len(names)} groups")
            elif abs(sum(float(x) for x in w) - 1.0) > 1e-4:
                bad.append(f"{r[0]}: weights sum to {sum(float(x) for x in w):.6f}")
        elif len(names) > 1:
            bad.append(f"{r[0]}: {len(names)} groups but no weights recorded")

    for taxon, i in sppr_row.items():
        if map_group.get(taxon) != sppr[i][3]:
            bad.append(f"{taxon}: SPPR sheet says group {sppr[i][3]!r}, the map says "
                       f"{map_group.get(taxon)!r}")

    # --- catch must be unchanged from the archive ------------------------------------
    src, years = mio.read_catch(ROOT, unit)
    # the builder rounds the catch once, at load; compare like with like
    src_total = sum(round(t, 3) for v in src.values() for t in v["by_year"].values())
    bk_total = sum(v for r in catch[1:] for v in r[4:] if isinstance(v, (int, float)))
    if abs(src_total - bk_total) > max(1.0, src_total * 1e-9):
        bad.append(f"catch total {bk_total:,.3f} differs from the archive's "
                   f"{src_total:,.3f}")
    if len(catch) - 1 != len(src):
        bad.append(f"Catch has {len(catch) - 1} taxa, the archive has {len(src)}")

    wbf.close()
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", nargs="*")
    a = ap.parse_args()

    books = []
    for d in sorted((ROOT / "data").iterdir()):
        if not d.is_dir() or (a.units and d.name not in a.units):
            continue
        md = d / "models"
        if md.is_dir():
            books += [(d.name, p) for p in sorted(md.glob("*.xlsx"))
                      if not p.name.startswith("~$")]
    if not books:
        print("no model workbooks found", file=sys.stderr)
        return 1

    failed = 0
    for unit, p in books:
        problems = check(p, unit)
        if problems:
            failed += 1
            print(f"FAIL  {p.relative_to(ROOT).as_posix()}")
            for m in problems[:20]:
                print(f"        {m}")
            if len(problems) > 20:
                print(f"        ... and {len(problems) - 20} more")
        else:
            print(f"ok    {p.relative_to(ROOT).as_posix()}")
    print(f"\n{len(books) - failed} of {len(books)} model workbook(s) verified")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
