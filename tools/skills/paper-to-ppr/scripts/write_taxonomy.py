"""Write `Taxonomy.xlsx` in the exact shape `database_json.py` expects.

That reader indexes on the *second* column and takes the *last* column as the description,
so a stray fourth column silently becomes the taxonomy and a reordered sheet silently keys
on the wrong thing. Writing it by hand invites both. This writes three columns in order and
nothing else.

    python write_taxonomy.py taxonomy.csv <model_dir>/Taxonomy.xlsx

The input CSV needs `seq`, `group_name`, `taxon_descr`. Pass `--from-model <model_dir>` to
seed one from the model's own group list, so the group names cannot be mistyped:

    python write_taxonomy.py --from-model <model_dir> --stub taxonomy.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

COLUMNS = ["seq", "group_name", "taxon_descr"]


def read_group_list(model_dir: Path) -> list:
    """Group seq and name from `Basic_input.csv` — the file everything else is keyed to."""
    p = model_dir / "Basic_input.csv"
    if not p.exists():
        raise SystemExit(f"no Basic_input.csv in {model_dir}")
    with p.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        raise SystemExit(f"{p} is empty")
    hdr = [h.strip() for h in rows[0]]
    seq_i = next((i for i, h in enumerate(hdr) if h.lower() in ("seq", "group", "id", "#")), 0)
    name_i = next((i for i, h in enumerate(hdr)
                   if "name" in h.lower() or h.lower() == "group name"), 1)
    out = []
    for r in rows[1:]:
        if len(r) <= max(seq_i, name_i) or not r[name_i].strip():
            continue
        out.append((r[seq_i].strip(), r[name_i].strip()))
    return out


def stub(model_dir: Path, dest: Path) -> int:
    groups = read_group_list(model_dir)
    with dest.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for seq, name in groups:
            w.writerow([seq, name, ""])
    print(f"wrote {dest} with {len(groups)} groups and empty descriptions")
    print("Fill taxon_descr for every row. Where the paper does not say, write")
    print("'not documented' and what you checked — an empty cell cannot be told apart")
    print("from one nobody looked at.")
    return 0


def convert(src: Path, dest: Path) -> int:
    import openpyxl
    with src.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    missing = [c for c in COLUMNS if not rows or c not in rows[0]]
    if missing:
        raise SystemExit(f"{src} is missing column(s) {missing}; needs {COLUMNS}")
    blank = [r["group_name"] for r in rows if not (r.get("taxon_descr") or "").strip()]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Taxonomy"
    ws.append(COLUMNS)
    for r in rows:
        ws.append([r["seq"], r["group_name"], r["taxon_descr"]])
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 34
    ws.column_dimensions["C"].width = 110
    wb.save(dest)
    wb.close()
    print(f"wrote {dest} with {len(rows)} groups")
    if blank:
        print(f"  WARNING: {len(blank)} group(s) have an empty taxon_descr: {blank[:6]}")
        print("  An empty cell reads as 'nobody looked'. Write 'not documented' instead.")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="?", type=Path, help="taxonomy CSV")
    ap.add_argument("dest", nargs="?", type=Path, help="Taxonomy.xlsx to write")
    ap.add_argument("--from-model", type=Path, help="model directory to read the group list from")
    ap.add_argument("--stub", type=Path, help="write an empty taxonomy CSV here")
    a = ap.parse_args()

    if a.stub:
        if not a.from_model:
            raise SystemExit("--stub needs --from-model")
        return stub(a.from_model, a.stub)
    if not a.src or not a.dest:
        ap.print_help(sys.stderr)
        return 2
    return convert(a.src, a.dest)


if __name__ == "__main__":
    raise SystemExit(main())
