"""write_outputs.py — turn a model JSON into the eight EwE import files.

Run:  python write_outputs.py model.json --outdir <parent-dir> [--zip]

The files go into <parent-dir>/<model_number>_<model_name>_<model_year>,
a name derived from the JSON metadata rather than chosen per model, and
that path is printed on stdout. `--zip` adds an archive of it alongside.

Every number in the JSON is read as *text* (`parse_float=str`) and written
through unchanged, so 0.0169 stays "0.0169" and a source's "0.10" keeps its
trailing zero. Derived cells (Sum, Total) are computed with Decimal, not float,
so no 0.30000000000000004 ever reaches a file.

Two conventions this script exists to enforce, because both are easy to break by
hand and invisible afterwards:
  * no quote characters anywhere in the CSVs
  * CRLF line endings

Blank vs zero: a key absent from the JSON, or set to null, writes an empty cell.
A key set to 0 writes "0". These mean different things — EwE substitutes its own
default (0.2) for a blank Unassim. consumption on import, so a blank must be a
decision, never a shortcut.

Input JSON shape (see references/model-json.md for the annotated version):

{
  "metadata": {"LME": "...", "model_number": 13, "model_name": "...",
               "model_year": 1981},
  "groups": [
    {"n": 1, "name": "Baleen whales", "hab_area": 1, "biomass": 0.0169,
     "z": null, "pb": 0.02, "qb": 3.29, "ee": null, "other_mort": null,
     "pq": null, "unassim": 0.2, "detritus_import": null, "tl": 4.1,
     "ba": null, "ba_rate": null}
  ],
  "consumers": [3, 4, 5],
  "fleets": ["Beam trawl", "Otter trawl"],
  "landings": {"3": {"Beam trawl": 0.12}},
  "discards": {"3": {"Beam trawl": 0.03}},
  "detritus_groups": ["Pelagic detritus", "Benthic detritus"],
  "detritus_fate": {"3": {"Pelagic detritus": 1}},
  "diet": {"3": {"1": 0.25, "2": 0.75, "import": 0}},
  "diet_rows": 39
}
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASIC_HEADER = [
    "",
    "Group name",
    "Hab area (proportion)",
    "Biomass in habitat area (t/km^2)",
    "Total mortality (/year)",
    "Production / biomass (/year)",
    "Consumption / biomass (/year)",
    "Ecotrophic Efficiency",
    "Other mortality",
    "Production / consumption",
    "Unassim. consumption",
    "Detritus import (t/km^2/year)",
]

BASIC_FIELDS = [
    "hab_area",
    "biomass",
    "z",
    "pb",
    "qb",
    "ee",
    "other_mort",
    "pq",
    "unassim",
    "detritus_import",
]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def cell(value) -> str:
    """Render one value. None/absent -> empty. Everything else verbatim."""
    if value is None:
        return ""
    s = str(value).strip()
    if any(ch in s for ch in ',"\n\r'):
        raise ValueError(
            f"value {s!r} contains a comma, quote or newline; these files carry "
            "no quoting, so the field would corrupt the row. Fix the source value."
        )
    return s


def dec(value) -> Decimal | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return Decimal(str(value).strip())
    except InvalidOperation:
        return None


def dec_str(d: Decimal | None) -> str:
    """Decimal -> shortest exact text ('1.000' -> '1', never '1E+0')."""
    if d is None:
        return ""
    n = d.normalize()
    if n == n.to_integral_value():
        try:
            return str(n.quantize(Decimal(1)))
        except InvalidOperation:
            return str(n)
    return format(n, "f")


def write_csv(path: Path, rows: list[list[str]]) -> None:
    """Write rows with no quoting and CRLF endings, including a trailing CRLF."""
    text = "".join(",".join(r) + "\r\n" for r in rows)
    path.write_text(text, encoding="utf-8", newline="")


# --------------------------------------------------------------------------
# file builders
# --------------------------------------------------------------------------


def basic_input(model) -> list[list[str]]:
    rows = [BASIC_HEADER[:]]
    for g in model["groups"]:
        row = [cell(g["n"]), cell(g.get("name"))]
        row += [cell(g.get(f)) for f in BASIC_FIELDS]
        rows.append(row)
    return rows


def diet_composition(model) -> list[list[str]]:
    groups = model["groups"]
    consumers = [str(c) for c in model.get("consumers") or [g["n"] for g in groups]]
    n_rows = int(model.get("diet_rows") or len(groups))
    diet = model.get("diet", {})

    rows = [["", "Source / fate"] + consumers]
    for g in groups[:n_rows]:
        row = [cell(g["n"]), cell(g.get("name"))]
        for c in consumers:
            row.append(cell(diet.get(c, {}).get(str(g["n"]))))
        rows.append(row)

    imports = ["", "Import"]
    sums = ["", "Sum"]
    residual = ["", "(1 - Sum)"]
    for c in consumers:
        col = diet.get(c, {})
        imp = dec(col.get("import"))
        imports.append(dec_str(imp) if imp is not None else "0")
        total = sum(
            (dec(v) for k, v in col.items() if dec(v) is not None), Decimal(0)
        )
        sums.append(dec_str(total))
        # The reference export carries 0 across this whole row: EwE writes the
        # residual only for diets it was asked to balance, and published
        # matrices are already balanced. Rounding drift belongs in Sum, where a
        # reviewer can see it, not silently absorbed here.
        residual.append("0")
    rows += [imports, sums, residual]
    return rows


def catch_table(model, key: str) -> list[list[str]]:
    fleets = model.get("fleets", [])
    data = model.get(key, {})
    n_rows = int(model.get(f"{key}_rows") or model.get("diet_rows") or len(model["groups"]))
    rows = [["", "Group name"] + [cell(f) for f in fleets] + ["Total"]]
    for g in model["groups"][:n_rows]:
        entry = data.get(str(g["n"]), {})
        row = [cell(g["n"]), cell(g.get("name"))]
        vals = [entry.get(f) for f in fleets]
        row += [cell(v) for v in vals]
        present = [dec(v) for v in vals if dec(v) is not None]
        row.append(dec_str(sum(present, Decimal(0))) if present else "")
        rows.append(row)
    return rows


def detritus_fate(model) -> list[list[str]]:
    dets = model.get("detritus_groups", [])
    data = model.get("detritus_fate", {})
    rows = [["", "Source / fate"] + [cell(d) for d in dets] + ["Export", "Sum"]]
    for g in model["groups"]:
        entry = data.get(str(g["n"]), {})
        vals = [entry.get(d) for d in dets] + [entry.get("Export")]
        row = [cell(g["n"]), cell(g.get("name"))] + [cell(v) for v in vals]
        present = [dec(v) for v in vals if dec(v) is not None]
        row.append(dec_str(sum(present, Decimal(0))) if present else "")
        rows.append(row)
    return rows


def biomass_accumulation(model) -> list[list[str]]:
    """One row per group: BA as an absolute rate and/or as a rate per biomass.

    Most published models report no numeric BA and this file is entirely blank,
    which means unknown in the extraction rather than an asserted zero. Where a paper does
    report BA it may give either form; write whichever the paper states and
    leave the other blank rather than converting, because the conversion needs
    B and would silently manufacture a value at the paper's rounding.
    """
    rows = [[
        "", "Group name",
        "Biomass accumulation (t/km^2/year)",
        "Biomass accumulation rate (/year)",
    ]]
    for g in model["groups"]:
        rows.append([
            cell(g["n"]), cell(g.get("name")),
            cell(g.get("ba")), cell(g.get("ba_rate")),
        ])
    return rows


def write_xlsx(model, outdir: Path) -> None:
    import openpyxl

    tl = openpyxl.Workbook()
    ws = tl.active
    ws["C1"] = "TL"
    for i, g in enumerate(model["groups"], start=2):
        ws.cell(row=i, column=1, value=g["n"])
        ws.cell(row=i, column=2, value=g.get("name"))
        v = g.get("tl")
        if v is not None and str(v).strip() != "":
            ws.cell(row=i, column=3, value=float(v))
    tl.save(outdir / "TL.xlsx")

    md = openpyxl.Workbook()
    ws = md.active
    for i, key in enumerate(["LME", "model_number", "model_name", "model_year"], start=1):
        ws.cell(row=i, column=1, value=key)
        v = model.get("metadata", {}).get(key)
        if v is not None:
            ws.cell(row=i, column=2, value=v)
    md.save(outdir / "Metadata.xlsx")


# --------------------------------------------------------------------------


def model_dir_name(model) -> str:
    """<model_number>_<model_name>_<model_year>, safe for a filesystem.

    The name is derived, not chosen, so that every model in an extraction set
    sorts and cross-references the same way. Spaces and punctuation in the
    model name become underscores; a year already trailing the name is not
    repeated (a model_name of "North Sea 1981" with model_year 1981 gives
    680_North_Sea_1981, not 680_North_Sea_1981_1981).
    """
    meta = model.get("metadata") or {}
    number = str(meta.get("model_number") or "").strip()
    name = str(meta.get("model_name") or "").strip()
    year = str(meta.get("model_year") or "").strip()

    missing = [k for k, v in (("model_number", number), ("model_name", name))
               if not v]
    if missing:
        sys.exit(
            "metadata." + " and metadata.".join(missing) + " is required to "
            "name the model directory. Set it in the model JSON, or pass "
            "--dir-name to override."
        )

    if year:
        name = re.sub(r"[\s_(\[-]*" + re.escape(year) + r"[)\]]*\s*$", "", name)

    parts = [p for p in (number, name, year) if p]
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", "_".join(parts))
    return re.sub(r"_+", "_", slug).strip("._-") or "model"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("model_json")
    ap.add_argument(
        "--outdir", default=".",
        help="parent directory the model directory is created in (default: .)",
    )
    ap.add_argument(
        "--dir-name",
        help="override the derived <model_number>_<model_name>_<model_year> "
             "directory name",
    )
    ap.add_argument(
        "--zip", action="store_true",
        help="also write <outdir>/<dir-name>.zip containing the directory",
    )
    args = ap.parse_args()

    model = json.loads(
        Path(args.model_json).read_text(encoding="utf-8"), parse_float=str
    )
    outdir = Path(args.outdir) / (args.dir_name or model_dir_name(model))
    outdir.mkdir(parents=True, exist_ok=True)

    write_csv(outdir / "Basic_input.csv", basic_input(model))
    write_csv(outdir / "Diet_composition.csv", diet_composition(model))
    write_csv(outdir / "Landings.csv", catch_table(model, "landings"))
    write_csv(outdir / "Discards.csv", catch_table(model, "discards"))
    write_csv(outdir / "Detritus_fate.csv", detritus_fate(model))
    write_csv(outdir / "Biomass_accumulation.csv", biomass_accumulation(model))
    write_xlsx(model, outdir)

    print(f"wrote 8 files to {outdir}", file=sys.stderr)
    for p in sorted(outdir.iterdir()):
        print(" ", p.name, file=sys.stderr)

    if args.zip:
        archive = shutil.make_archive(
            str(outdir), "zip", root_dir=outdir.parent, base_dir=outdir.name
        )
        print(f"wrote {archive}", file=sys.stderr)

    # stdout carries the directory path alone, so the next step can use it:
    #   d=$(python scripts/write_outputs.py model.json) && python scripts/validate.py "$d"
    print(outdir)


if __name__ == "__main__":
    main()
