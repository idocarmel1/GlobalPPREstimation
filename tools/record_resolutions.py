# save as tools/record_resolutions.py
import csv
from pathlib import Path
from collections import Counter

# Mirrors the PRESERVE set and skip logic that promote_release.py actually
# applied to only-in-old rows (task-2 review finding: the original text
# labeled every only-in-old row "carry-up", but ruling 11's fix meant only
# the two real notebooks were carried up -- the other 3932 were deliberately
# skipped, either because they belong to a PRESERVE-owned top-level entry or
# because they are a __pycache__/.pytest_cache build cache). This uses the
# same first-path-component test promote_release.py used, not a substring
# match, so the classification matches what actually happened on disk.
PRESERVE = {
    "EEZ_TE010_release_2026-09-04",
    "EEZ_TE010_release_2026-09-04_complete.zip",
    "EEZ_TE010_release_2026-09-04_results.zip",
    "EEZ_TE010_release_2026-09-04_delivery.json",
    "Global_history_TE010_2026-09-04",
    "Global_history_TE010_2026-09-04.zip",
    "Global_history_TE010_2026-09-04.delivery.json",
    "PPR_global_te005_results",
}

p = Path("docs/superpowers/sau-promotion-manifest.csv")
rows = list(csv.DictReader(p.open(encoding="utf-8")))
for r in rows:
    if r["status"] == "differs":
        # Applies uniformly to all differing paths (14, not just the six
        # src/ppr_pipeline/*.py + xlsx files originally called out) per
        # task-2 ruling 12: the release tree is newer overall and every
        # differs path -- README.md, requirements.txt, tests/test_ingest.py,
        # tests/test_pipeline.py, and the four tools/ scripts included --
        # resolves to take-release.
        r["resolution"] = "take-release (release tree is newer; see task-2 ruling 12)"
    elif r["status"] == "only-in-old":
        parts = r["path"].split("/")
        if parts[0] in PRESERVE:
            r["resolution"] = "skipped (PRESERVE-owned; Task 3 deletes through its verification gate)"
        elif "__pycache__" in parts or ".pytest_cache" in parts:
            r["resolution"] = "skipped (build cache, gitignored)"
        else:
            r["resolution"] = "carried-up (unique to old tree)"
    elif r["status"] == "only-in-release":
        r["resolution"] = "keep-release"
    else:
        r["resolution"] = "identical (no action)"
with p.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["path", "status", "old_bytes", "release_bytes", "resolution"])
    w.writeheader(); w.writerows(rows)

counts = Counter(r["resolution"] for r in rows)
print(f"resolutions recorded for {len(rows)} paths")
for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {v:6d}  {k}")

carried = counts.get("carried-up (unique to old tree)", 0)
if carried != 2:
    raise SystemExit(
        f"expected exactly 2 carried-up rows, got {carried} -- "
        "promotion and record disagree, stop and report."
    )
