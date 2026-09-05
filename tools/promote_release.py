# save as tools/promote_release.py
from __future__ import annotations
import csv, shutil
from pathlib import Path

ROOT = Path("SeaAroundUsExtraction")
REL = ROOT / "EEZ_TE010_release_2026-09-04"
rows = list(csv.DictReader(Path("docs/superpowers/sau-promotion-manifest.csv").open(encoding="utf-8")))

# PRESERVE lists top-level ROOT entries that Task 3 owns and deletes later
# through its own verification gate. They must never be copied into the
# release tree during carry-up below (task-2 ruling 11: that would just
# duplicate multiple gigabytes of data pointlessly and set up a false
# collision against step 3's no-clobber guard), and must never be removed
# by this script's own cleanup pass.
PRESERVE = {
    REL.name,
    "EEZ_TE010_release_2026-09-04_complete.zip",
    "EEZ_TE010_release_2026-09-04_results.zip",
    "EEZ_TE010_release_2026-09-04_delivery.json",
    "Global_history_TE010_2026-09-04",
    "Global_history_TE010_2026-09-04.zip",
    "Global_history_TE010_2026-09-04.delivery.json",
    "PPR_global_te005_results",
}

# 1. copy every only-in-old file into the release tree so nothing unique is
#    lost -- except (task-2 ruling 11):
#      - files whose first path component is a PRESERVE-owned top-level
#        entry: those are siblings of the release dir, not part of the old
#        tree being retired here, and Task 3 handles them later through its
#        own verification gate.
#      - build-cache files (__pycache__ / .pytest_cache): gitignored,
#        regenerable, not worth carrying anywhere.
carried_paths = []
skipped_preserve = 0
skipped_cache = 0
for r in rows:
    if r["status"] != "only-in-old":
        continue
    path = r["path"]
    parts = path.split("/")
    if parts[0] in PRESERVE:
        skipped_preserve += 1
        continue
    if "__pycache__" in parts or ".pytest_cache" in parts:
        skipped_cache += 1
        continue
    src, dst = ROOT / path, REL / path
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    carried_paths.append(path)

print(f"carried up {len(carried_paths)} files unique to the old tree:")
for cp in carried_paths:
    print("   ", cp)
print(f"skipped {skipped_preserve} files under PRESERVE-owned top-level entries (Task 3 owns these)")
print(f"skipped {skipped_cache} build-cache files (__pycache__/.pytest_cache)")

# Auditable guardrail: the only files expected to survive both exclusions
# are the two real notebooks unique to the old tree. If anything else shows
# up here, stop before touching anything else in the tree.
expected_carry = {"notebooks/global_validation.ipynb", "notebooks/pilot_validation.ipynb"}
if set(carried_paths) != expected_carry:
    unexpected = sorted(set(carried_paths) - expected_carry)
    missing = sorted(expected_carry - set(carried_paths))
    raise SystemExit(
        "carry-up set does not match the expected two notebooks -- stopping "
        f"before step 2/3. unexpected={unexpected} missing={missing}"
    )

# 2. remove only the old top-level entries the release actually supersedes.
#    Anything Task 3 deletes through its verification gate is preserved here, so the
#    gate stays meaningful and every deletion remains attributable to one task.
release_top = {child.name for child in REL.iterdir()}
removed, kept = [], []
for child in list(ROOT.iterdir()):
    if child.name in PRESERVE:
        kept.append(child.name)
        continue
    if child.name not in release_top:
        # nothing in the release will replace this; leave it and report
        kept.append(child.name)
        continue
    shutil.rmtree(child) if child.is_dir() else child.unlink()
    removed.append(child.name)
print(f"removed {len(removed)} superseded entries: {sorted(removed)}")
print(f"preserved {len(kept)} entries: {sorted(kept)}")

# 3. move release contents up one level
for child in list(REL.iterdir()):
    destination = ROOT / child.name
    if destination.exists():
        raise SystemExit(
            f"refusing to overwrite {destination}: step 2 should have removed it. "
            "Resolve manually rather than clobbering."
        )
    shutil.move(str(child), str(destination))
leftovers = list(REL.iterdir())
if leftovers:
    raise SystemExit(f"release directory not empty: {[p.name for p in leftovers]}")
REL.rmdir()
print("release promoted; release directory removed")
