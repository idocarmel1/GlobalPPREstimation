"""Independent reference arithmetic from frozen accepted catch/coefficient inputs."""
import json
import math

from check_accepted_inputs import HERE, ROOT, read_protected
from workbooks import finite, overview, records, sha, SIMPLE


def main():
    inventory = json.loads((HERE / "preflight.json").read_text(encoding="utf-8"))["regions"]
    results = []
    for item in inventory:
        path = ROOT / item["baseline_directory"] / (item["unit_id"] + ".xlsx")
        book = read_protected(path)
        settings = overview(book)
        year, basis = int(settings.get("taxon_detail_year", 2019)), settings["catch_basis"]
        catches = [r for r in records(book, "Catch", "Catch") if r["catch_basis"] == basis]
        assert len(catches) == len({r["taxon"] for r in catches})
        coefficients = {r["taxon"]: r for r in records(book, "Classic PPR", "Taxa")}
        known, missing_catch, unknown_ppr, zero_missing_coefficient = [], [], [], []
        for row in catches:
            taxon, catch = row["taxon"], row.get(year)
            coefficient = coefficients.get(taxon, {}).get("sppr")
            if not finite(catch):
                missing_catch.append(taxon)
            elif catch == 0:
                known.append(0.)
                if not finite(coefficient):
                    zero_missing_coefficient.append(taxon)
            elif not finite(coefficient):
                unknown_ppr.append({"taxon": taxon, "catch_tonnes": catch})
            else:
                known.append(catch * coefficient / 9.)
        total = math.fsum(known)
        saved = [r for r in records(book, "Classic PPR", "Annual")
                 if r.get("method") == SIMPLE and r.get("scope") == "all"
                 and r.get("catch_basis") == basis and r.get("unidentified") == "method"
                 and r.get("metric") == "ppr"]
        assert len(saved) == 1, (item["unit_id"], len(saved))
        saved_tC = saved[0].get(year) / 9 if finite(saved[0].get(year)) else None
        results.append({
            "unit_id": item["unit_id"], "model_id": item["model_id"],
            "baseline_workbook_sha256": sha(path), "year": year, "catch_basis": basis,
            "taxa": len(catches), "known_catch_tonnes": math.fsum(r[year] for r in catches if finite(r.get(year))),
            "known_simple_chain_ppr_tC": total, "saved_simple_chain_ppr_tC": saved_tC,
            "reconciles_saved_total": saved_tC is not None and math.isclose(total, saved_tC, rel_tol=1e-10, abs_tol=1e-6),
            "positive_catch_unknown_ppr": unknown_ppr, "missing_catch_taxa": missing_catch,
            "zero_catch_missing_coefficient": zero_missing_coefficient,
            "conversion": "Stored wet-weight-equivalent coefficient multiplied by catch tonnes, divided by9 once.",
        })
        print(item["unit_id"], len(catches), f"{total:.6f}", len(unknown_ppr), flush=True)
    target = HERE / "verification" / "independent_reference_totals.json"
    target.write_text(json.dumps({"scope": "Frozen accepted-input arithmetic; no mapping/SPPR dependency or new TL values.", "regions": results}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    assert all(r["reconciles_saved_total"] for r in results), "Inspect unmatched saved independent totals"


if __name__ == "__main__":
    main()
