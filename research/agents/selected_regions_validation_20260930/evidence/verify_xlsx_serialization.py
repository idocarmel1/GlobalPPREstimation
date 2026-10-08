"""Read-only sparse XLSX row/cell ordering and unique-address verification."""
from pathlib import Path
from zipfile import ZipFile
import argparse
import hashlib
import json
import re

from lxml import etree

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path):
    before = sha(path)
    sheets = []
    with ZipFile(path) as package:
        for name in package.namelist():
            if not re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name):
                continue
            previous_row, rows, cells = 0, 0, 0
            with package.open(name) as stream:
                for _, row in etree.iterparse(stream, events=("end",), tag=NS + "row"):
                    row_number = int(row.get("r"))
                    assert row_number > previous_row, (path, name, row_number)
                    previous_column = 0
                    for cell in row.findall(NS + "c"):
                        address = cell.get("r")
                        match = re.fullmatch(r"([A-Z]+)([1-9][0-9]*)", address or "")
                        assert match and int(match[2]) == row_number, (path, name, address)
                        column = 0
                        for letter in match[1]:
                            column = column * 26 + ord(letter) - ord("A") + 1
                        assert column > previous_column, (path, name, address, previous_column)
                        previous_column = column
                        cells += 1
                    rows += 1
                    previous_row = row_number
                    row.clear()
                    while row.getprevious() is not None:
                        del row.getparent()[0]
            sheets.append({"member": name, "rows": rows, "cells": cells})
    assert sha(path) == before, f"Workbook changed during scan: {path}"
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": before,
            "sheets": sheets, "passed": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("units", nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = []
    for unit in args.units:
        result = verify(ROOT / "regions" / unit / (unit + ".xlsx"))
        results.append(result)
        print(json.dumps({"unit": unit, "passed": True,
                          "cells": sum(s["cells"] for s in result["sheets"])}), flush=True)
    args.output.write_text(json.dumps({"scope": "Strict ascending rows and columns, unique addresses and correct row identity. No values or files modified.",
                                      "workbooks": results, "passed": True}, indent=2) + "\n", encoding="utf-8")
