# save as tools/record_resolutions.py
import csv
from pathlib import Path
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
        r["resolution"] = "carry-up (unique to old tree)"
    elif r["status"] == "only-in-release":
        r["resolution"] = "keep-release"
    else:
        r["resolution"] = "identical (no action)"
with p.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["path", "status", "old_bytes", "release_bytes", "resolution"])
    w.writeheader(); w.writerows(rows)
print(f"resolutions recorded for {len(rows)} paths")
