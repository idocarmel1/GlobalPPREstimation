"""Read-only reference-year method contributions, distinct from classic-PPR shares."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from workbooks import finite, overview, read_book, records, sha


def inspect(unit):
    path = ROOT / "regions" / unit / f"{unit}.xlsx"
    fingerprint = sha(path)
    book = read_book(path)
    config = overview(book)
    year = int(config.get("taxon_detail_year", 2019))
    basis = config.get("catch_basis", "landings")
    model = config["selected_model_id"]
    catch = {}
    for row in records(book, "Catch", "Catch"):
        if row["catch_basis"] == basis:
            assert row["taxon"] not in catch
            catch[row["taxon"]] = row.get(year)
    levels = defaultdict(set)
    for row in records(book, "PPR", "Matching"):
        assert row["model_id"] == model
        level = str(row.get("confidence") or "unresolved").strip().lower().replace("_", " ")
        assert level in {"high", "medium", "low", "very low", "unresolved"}, level
        levels[row["taxon"]].add(level)
    assert all(len(v) == 1 for v in levels.values()), "Split taxon confidence differs between rows"
    confidence = {t: next(iter(v)) for t, v in levels.items()}
    annual = {}
    for row in records(book, "PPR", "Annual"):
        if row["scope"] == "all" and row["catch_basis"] == basis and row["unidentified"] == "method" and row["metric"] == "ppr":
            assert row["method"] not in annual
            annual[row["method"]] = row
    methods = defaultdict(list)
    for row in records(book, "PPR", "Taxon SPPR"):
        if row["scope"] != "all":
            continue
        assert row["model_id"] == model
        taxon = row["taxon"]
        c, coefficient = catch.get(taxon), row.get("sppr")
        if finite(c) and finite(coefficient):
            methods[row["method"]].append({"taxon": taxon, "catch_t": c,
                                           "sppr_wet": coefficient,
                                           "ppr_wet_t": c * coefficient,
                                           "confidence": confidence.get(taxon, "unresolved")})
    result = {"unit_id": unit, "model_id": model, "workbook_sha256": fingerprint,
              "year": year, "basis": basis, "scope": "all", "unidentified": "method", "methods": []}
    for method, rows in sorted(methods.items()):
        saved = annual[method]
        total = math.fsum(r["ppr_wet_t"] for r in rows)
        available = finite(saved.get(year))
        if available:
            assert math.isclose(total, saved[year], rel_tol=1e-12, abs_tol=1e-6), (unit, method, total, saved[year])
        negatives = [r for r in rows if r["ppr_wet_t"] < 0]
        sums = {level: math.fsum(r["ppr_wet_t"] for r in rows if r["confidence"] == level)
                for level in sorted({r["confidence"] for r in rows})}
        nonnegative_shares = available and total > 0 and not negatives
        for r in rows:
            r["share_percent"] = 100 * r["ppr_wet_t"] / total if nonnegative_shares else None
        top = sorted(rows, key=lambda r: (-abs(r["ppr_wet_t"]), r["taxon"]))[:5]
        result["methods"].append({"method": method, "annual_status": saved["status"],
                                  "annual_value_available": available, "annual_value_reproduced": available,
                                  "reconstructed_mapped_ppr_wet_t": total,
                                  "displayed_ppr_tC": saved[year] / 9 if available else None,
                                  "confidence_ppr_wet_t": sums,
                                  "confidence_percent": {k: 100 * v / total for k, v in sums.items()} if nonnegative_shares else None,
                                  "negative_taxon_contributions": negatives,
                                  "largest_absolute_contributions": top})
    assert sha(path) == fingerprint, f"Region changed during exposure check: {unit}"
    return result


def main(units):
    output = {"scope": "Method-specific mapped contribution audit; classic-PPR confidence percentages remain independent. No scientific input or result is changed, and no model is approved.",
              "regions": [inspect(unit) for unit in units]}
    destination = HERE / "verification" / ("method_exposure_" + "_".join(units) + ".json")
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for region in output["regions"]:
        print(json.dumps({"unit_id": region["unit_id"], "methods": [
            {"method": m["method"], "available": m["annual_value_available"],
             "very_low_percent": (m["confidence_percent"] or {}).get("very low"),
             "largest": m["largest_absolute_contributions"][0] if m["largest_absolute_contributions"] else None}
            for m in region["methods"] if m["method"] in {"new_GE", "new_TE_EEfix", "new_WithEgestion"}]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("units", nargs="+")
    main(parser.parse_args().units)
