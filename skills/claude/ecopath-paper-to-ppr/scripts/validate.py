"""validate.py — check a finished model directory before it is called done.

Run:  python validate.py <model-dir>

These checks catch the failure modes that actually happen in this workflow:
a column of the diet matrix parsed one place left, a group dropped between
files, a quote character introduced by a spreadsheet round-trip, LF endings from
a text editor. They do not check whether the numbers are the right numbers —
only a human comparing against the page can do that.

The script never edits anything. A diet column that sums to 1.04 may be exactly
what the paper printed; the correct response is to look at the page, not to
normalise the column. Exit code is 1 if any ERROR is raised, 0 otherwise.
"""

from __future__ import annotations

import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

TOL = Decimal("0.01")

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def read_raw(path: Path) -> bytes:
    return path.read_bytes()


def read_rows(path: Path) -> list[list[str]]:
    text = read_raw(path).decode("utf-8")
    return [ln.split(",") for ln in text.split("\r\n") if ln != ""]


def num(s: str) -> Decimal | None:
    s = s.strip()
    if s == "":
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def check_format(path: Path) -> None:
    raw = read_raw(path)
    if b'"' in raw or b"'" in raw:
        err(f"{path.name}: contains a quote character; these files carry no quoting")
    if b"\r\n" not in raw:
        err(f"{path.name}: no CRLF line endings found")
    stray = raw.replace(b"\r\n", b"")
    if b"\n" in stray or b"\r" in stray:
        err(f"{path.name}: mixed line endings (bare LF or CR present)")


def main() -> int:
    argv = sys.argv[1:]
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    d = Path(argv[0] if argv else ".")
    if not d.is_dir():
        print(f"not a directory: {d}\n\nRun:  python validate.py <model-dir>",
              file=sys.stderr)
        return 2
    expected = [
        "Basic_input.csv",
        "Diet_composition.csv",
        "Landings.csv",
        "Discards.csv",
        "Detritus_fate.csv",
        "Biomass_accumulation.csv",
        "TL.xlsx",
        "Metadata.xlsx",
    ]
    for name in expected:
        if not (d / name).exists():
            err(f"missing output file: {name}")

    csvs = [n for n in expected if n.endswith(".csv") and (d / n).exists()]
    for name in csvs:
        check_format(d / name)

    # ---- Basic_input: the group list every other file is checked against ----
    groups: dict[str, str] = {}
    biomass: dict[str, Decimal | None] = {}
    if (d / "Basic_input.csv").exists():
        rows = read_rows(d / "Basic_input.csv")
        header, body = rows[0], rows[1:]
        if header[1] != "Group name":
            err("Basic_input.csv: header does not match the template")
        for i, r in enumerate(body, start=1):
            if len(r) != len(header):
                err(f"Basic_input.csv row {i}: {len(r)} fields, header has {len(header)}")
            if r[0] != str(i):
                err(f"Basic_input.csv row {i}: group number is {r[0]!r}, expected {i}")
            if not r[1].strip():
                err(f"Basic_input.csv row {i}: group name is blank")
            groups[r[0]] = r[1]
            biomass[r[0]] = num(r[3]) if len(r) > 3 else None
            if not any(x.strip() for x in r[3:8]):
                warn(
                    f"Basic_input.csv row {i} ({r[1]}): B, Z, P/B, Q/B and EE are all "
                    "blank — likely a missed row rather than a deliberate blank"
                )
        blanks = [
            r[1] for r in body if len(r) > 10 and not r[10].strip()
        ]
        if blanks:
            warn(
                f"{len(blanks)} group(s) have a blank Unassim. consumption — EwE will "
                f"substitute 0.2 on import: {', '.join(blanks[:8])}"
                + (" ..." if len(blanks) > 8 else "")
            )

    # ---- Diet composition ----
    if (d / "Diet_composition.csv").exists():
        rows = read_rows(d / "Diet_composition.csv")
        header = rows[0]
        consumers = header[2:]
        body = [r for r in rows[1:] if r[1] not in ("Import", "Sum", "(1 - Sum)")]
        tail = {r[1]: r for r in rows[1:] if r[1] in ("Import", "Sum", "(1 - Sum)")}
        for name in ("Import", "Sum", "(1 - Sum)"):
            if name not in tail:
                err(f"Diet_composition.csv: missing trailing {name!r} row")
        for r in body:
            if groups and r[0] in groups and r[1] != groups[r[0]]:
                err(
                    f"Diet_composition.csv row {r[0]}: name {r[1]!r} does not match "
                    f"Basic_input {groups[r[0]]!r}"
                )
        for j, c in enumerate(consumers):
            total = sum(
                (num(r[2 + j]) or Decimal(0) for r in body if len(r) > 2 + j),
                Decimal(0),
            )
            imp = num(tail.get("Import", [""] * (2 + len(consumers)))[2 + j]) or Decimal(0)
            total += imp
            if total == 0:
                warn(f"Diet_composition.csv column {c}: empty (no diet recorded)")
            elif abs(total - 1) > TOL:
                err(
                    f"Diet_composition.csv column {c}: diet + import sums to {total} "
                    "— check the column against a rendered image of the page"
                )
            stated = num(tail.get("Sum", [""] * (2 + len(consumers)))[2 + j])
            if stated is not None and abs(stated - total) > Decimal("0.000001"):
                err(
                    f"Diet_composition.csv column {c}: written Sum {stated} does not "
                    f"equal the column total {total}"
                )

    # ---- Landings / Discards ----
    for name in ("Landings.csv", "Discards.csv"):
        if not (d / name).exists():
            continue
        rows = read_rows(d / name)
        header = rows[0]
        if header[-1] != "Total":
            err(f"{name}: last column should be 'Total'")
        for r in rows[1:]:
            vals = [num(x) for x in r[2:-1]]
            present = [v for v in vals if v is not None]
            stated = num(r[-1])
            if present and stated is None:
                err(f"{name} row {r[0]}: fleet values present but Total is blank")
            if present and stated is not None and abs(sum(present) - stated) > Decimal("0.000001"):
                err(f"{name} row {r[0]}: Total {stated} != sum of fleets {sum(present)}")

    # ---- Detritus fate ----
    # ---- Biomass_accumulation: blank is normal, inconsistent is not --------
    if (d / "Biomass_accumulation.csv").exists():
        rows = read_rows(d / "Biomass_accumulation.csv")
        header, body = rows[0], rows[1:]
        if len(header) != 4 or not header[2].startswith("Biomass accumulation"):
            err("Biomass_accumulation.csv: header does not match the template")
        if groups and len(body) != len(groups):
            err(
                f"Biomass_accumulation.csv: {len(body)} rows, "
                f"Basic_input.csv has {len(groups)}"
            )
        filled = 0
        for i, r in enumerate(body, start=1):
            if len(r) != len(header):
                err(
                    f"Biomass_accumulation.csv row {i}: {len(r)} fields, "
                    f"header has {len(header)}"
                )
                continue
            if r[0] != str(i):
                err(
                    f"Biomass_accumulation.csv row {i}: group number is "
                    f"{r[0]!r}, expected {i}"
                )
            if groups and r[0] in groups and r[1] != groups[r[0]]:
                err(
                    f"Biomass_accumulation.csv row {i}: group name {r[1]!r} "
                    f"does not match Basic_input {groups[r[0]]!r}"
                )
            ba, rate = num(r[2]), num(r[3])
            if ba is not None or rate is not None:
                filled += 1
            # both forms given: they have to agree through B, or one of them
            # was read from the wrong column
            if ba is not None and rate is not None and r[0] in biomass:
                b = biomass[r[0]]
                if b:
                    implied = ba / b
                    if abs(implied - rate) > abs(rate) * Decimal("0.1") + Decimal("0.005"):
                        warn(
                            f"Biomass_accumulation.csv row {i} ({r[1]}): "
                            f"BA {ba} over B {b} implies a rate of "
                            f"{implied:.3f}/year, but the rate column says {rate}"
                        )
        if filled == 0:
            warn(
                "Biomass_accumulation.csv is entirely blank — BA is unknown in "
                "this extraction; say in REPORT.md where BA and any explicit "
                "steady-state statement were checked"
            )

    if (d / "Detritus_fate.csv").exists():
        rows = read_rows(d / "Detritus_fate.csv")
        header = rows[0]
        if header[-2:] != ["Export", "Sum"]:
            err("Detritus_fate.csv: last two columns should be 'Export','Sum'")
        for r in rows[1:]:
            vals = [num(x) for x in r[2:-1]]
            present = [v for v in vals if v is not None]
            if not present:
                warn(f"Detritus_fate.csv row {r[0]}: no fate recorded")
                continue
            total = sum(present)
            if abs(total - 1) > TOL:
                err(f"Detritus_fate.csv row {r[0]}: fate sums to {total}, expected 1")

    # ---- TL / Metadata ----
    try:
        import openpyxl

        if (d / "TL.xlsx").exists():
            ws = openpyxl.load_workbook(d / "TL.xlsx").active
            if ws["C1"].value != "TL":
                err("TL.xlsx: cell C1 should contain 'TL'")
            missing = [
                ws.cell(row=i, column=2).value
                for i in range(2, ws.max_row + 1)
                if ws.cell(row=i, column=1).value is not None
                and ws.cell(row=i, column=3).value is None
            ]
            if missing:
                warn(f"TL.xlsx: {len(missing)} group(s) have no trophic level")
        if (d / "Metadata.xlsx").exists():
            ws = openpyxl.load_workbook(d / "Metadata.xlsx").active
            keys = [ws.cell(row=i, column=1).value for i in range(1, 5)]
            if keys != ["LME", "model_number", "model_name", "model_year"]:
                err(f"Metadata.xlsx: column A should be LME/model_number/model_name/model_year, got {keys}")
            for i in range(1, 5):
                if ws.cell(row=i, column=2).value in (None, ""):
                    warn(f"Metadata.xlsx: {keys[i-1]} is empty")
    except ImportError:
        warn("openpyxl not installed; skipped the .xlsx checks")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
