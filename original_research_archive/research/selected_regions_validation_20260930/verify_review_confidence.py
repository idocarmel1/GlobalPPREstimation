"""Read-only audit of released confidence components and canonical mappings."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RANK = {"unresolved": 0, "very low": 1, "low": 2, "medium": 3, "high": 4}
AUDITS = {
    "LME_026": "adopted_taxon_audit.json",
    "LME_032": "mapping/adopted_taxon_audit.json",
    "LME_034": "adopted_taxon_audit.json",
    "LME_036": "selected_regions_review_20260930/taxon_audit_adopted.json",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(value):
    return str(value).strip().lower().replace("_", " ")


def table(book, sheet, name):
    active, header = False, None
    for values in book[sheet].values:
        if not values or values[0] is None:
            continue
        if values[0] == "@table":
            if active:
                return
            active = values[1] == name
        elif active and header is None:
            header = values
        elif active:
            yield dict(zip(header, values))


def verify(item):
    unit = item["unit_id"]
    handoff = ROOT / item["handoff"]["path"]
    audit = handoff.parent / AUDITS.get(unit, "taxon_audit.json")
    book_path = ROOT / item["workbook"]["path"]
    identities = {str(p.relative_to(ROOT).as_posix()): sha(p)
                  for p in [handoff, audit, book_path]}
    assert sha(handoff) == item["handoff"]["sha256"]
    assert sha(book_path) == item["workbook"]["sha256"]
    data = json.loads(audit.read_text(encoding="utf-8"))
    rows = data.get("rows", data.get("records")) if isinstance(data, dict) else data
    assert len({r["taxon"] for r in rows}) == len(rows)
    overall_field = "review_confidence" if unit == "LME_036" else None
    findings, historical_aliases, canonical_labels = [], [], defaultdict(set)
    reviewed = {}
    for row in rows:
        member = normalized(row["membership_confidence"])
        weight = normalized(row.get("allocation_confidence", row.get("weight_confidence")))
        overall = normalized(row[overall_field] if overall_field else
                             row.get("overall_confidence", row.get("confidence")))
        if any(c not in RANK for c in [member, weight, overall]):
            findings.append({"taxon": row["taxon"], "issue": "unknown confidence", "values": [member, weight, overall]})
        elif RANK[overall] != min(RANK[member], RANK[weight]):
            findings.append({"taxon": row["taxon"], "issue": "weakest-component mismatch", "values": [member, weight, overall]})
        if overall_field and "overall_confidence" in row and normalized(row["overall_confidence"]) != overall:
            historical_aliases.append({"taxon": row["taxon"], "current_review_confidence": overall,
                                       "inherited_overall_confidence": row["overall_confidence"]})
        reviewed[row["taxon"]] = overall
    book = openpyxl.load_workbook(book_path, read_only=True, data_only=False)
    try:
        catch_taxa = {r["taxon"] for r in table(book, "Catch", "Catch")}
        for row in table(book, "PPR", "Matching"):
            if row.get("model_id") == item["model_id"] and row.get("group"):
                canonical_labels[row["taxon"]].add(normalized(row.get("confidence")))
    finally:
        book.close()
    if catch_taxa != set(reviewed):
        findings.append({"issue": "catch-universe mismatch", "missing": sorted(catch_taxa-set(reviewed)),
                         "extra": sorted(set(reviewed)-catch_taxa)})
    for taxon, values in canonical_labels.items():
        if values != {reviewed.get(taxon)}:
            findings.append({"taxon": taxon, "issue": "canonical confidence differs", "canonical": sorted(values), "review": reviewed.get(taxon)})
    for relative, digest in identities.items():
        assert sha(ROOT / relative) == digest, "Input changed during audit: " + relative
    return {"unit_id": unit, "taxa": len(rows), "counts": dict(Counter(reviewed.values())),
            "passed": not findings, "findings": findings, "identities": identities,
            "authoritative_overall_field": overall_field or "overall_confidence (or confidence where that is the schema)",
            "inherited_alias_disagreements": historical_aliases,
            "scope": "Exact catch-label completeness, unique rows, weakest reviewed component and canonical Matching confidence; source scientific judgments are checked separately."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("units", nargs="+")
    args = parser.parse_args()
    progress = json.loads((HERE / "verification/review_package_progress.json").read_text(encoding="utf-8"))
    results = []
    for unit in args.units:
        result = verify(next(r for r in progress["regions"] if r["unit_id"] == unit))
        results.append(result)
        print(json.dumps({"unit": unit, "taxa": result["taxa"], "passed": result["passed"],
                          "findings": result["findings"][:10]}), flush=True)
    output = HERE / "verification" / ("review_confidence_" + "_".join(args.units) + ".json")
    output.write_text(json.dumps({"results": results, "passed": all(r["passed"] for r in results)},
                                 indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    raise SystemExit(0 if all(r["passed"] for r in results) else 1)
