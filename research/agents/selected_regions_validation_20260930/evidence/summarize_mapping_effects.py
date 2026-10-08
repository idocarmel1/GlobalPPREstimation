"""Read-only before/after reference totals for released regional packages."""
import argparse
import hashlib
import json
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def reference_rows(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
    result, active, header = [], False, None
    try:
        for cells in wb["PPR"].values:
            values = list(cells)
            if not values or values[0] is None:
                continue
            if values[0] == "@table":
                if active:
                    break
                active = values[1] == "Annual"
                header = None
            elif active and header is None:
                header = [int(v) if isinstance(v, str) and v.isdigit() else v for v in values]
            elif active:
                r = dict(zip(header, values))
                if r.get("scope") == "all" and r.get("unidentified") == "method" and r.get("metric") in {"ppr", "catch", "covered_catch"}:
                    result.append({k: r.get(k) for k in ["model_id", "method", "catch_basis", "metric", "status", 2019]})
    finally:
        wb.close()
    return result


def main(units):
    output = []
    for unit in units:
        path = ROOT / "regions" / unit / (unit + ".xlsx")
        current_hash = sha(path)
        previous = reference_rows(HERE / "baseline" / unit / path.name)
        current = reference_rows(path)
        key = lambda r: tuple(r[k] for k in ("model_id", "method", "catch_basis", "metric"))
        old = {key(r): r for r in previous}
        changes = []
        for row in current:
            prior = old.get(key(row), {})
            a, c = prior.get(2019), row[2019]
            divisor = 9 if row["metric"] == "ppr" else 1
            item = {k: row[k] for k in ("method", "catch_basis", "metric", "status")}
            item.update({"before": a / divisor if isinstance(a, (int, float)) else None,
                         "after": c / divisor if isinstance(c, (int, float)) else None,
                         "units": "t C" if divisor == 9 else "t wet catch"})
            if item["before"] is not None and item["after"] is not None:
                item["difference"] = item["after"] - item["before"]
            changes.append(item)
        assert sha(path) == current_hash, f"Regional workbook changed during read: {unit}"
        output.append({"unit_id": unit, "workbook_sha256": current_hash, "year": 2019,
                       "source_scope": "all", "unidentified": "method", "rows": changes})
        print(unit, len(changes), "reference rows compared", flush=True)
    path = HERE / "verification" / ("mapping_effects_" + "_".join(units) + ".json")
    path.write_text(json.dumps({"scope": "Selected model mapping-dependent totals; positive changes are not a scientific-quality score. Accepted parameters are checked separately.",
                                "regions": output}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("units", nargs="+")
    main(parser.parse_args().units)
