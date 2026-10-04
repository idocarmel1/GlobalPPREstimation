"""Read-only regional/source inventory for the 2026-10-03 adoption."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "tools"))
from workbooks import read_book, overview, records, finite, sha

region = ROOT / "regions/LME_052/LME_052.xlsx"
candidate = Path(__file__).resolve().parents[2]
book = read_book(region)
summary = {
    "workbook_sha256": sha(region),
    "overview": overview(book),
    "tables": {s: {n: {"columns": h, "rows": len(r)} for n, (h, r) in v.items()} for s, v in book.items()},
    "catch": [
        {k: v for k, v in r.items() if not isinstance(k, int)}
        | {"catch_2019": r.get(2019), "total_1950_2019": sum(v for k, v in r.items() if isinstance(k, int) and finite(v))}
        for r in records(book, "Catch", "Catch")
    ],
    "classic_taxa": records(book, "Classic PPR", "Taxa"),
    "old_groups": records(book, "Selected model groups", "Groups"),
    "old_matching": records(book, "PPR", "Matching"),
}
data = json.loads((candidate / "assumption_variants/researcher_readings_20261003/model.json").read_text(encoding="utf-8"))
summary["candidate_keys"] = list(data)
summary["candidate_groups"] = data.get("group", [])
(Path(__file__).parent / "baseline_inventory.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
