# Projects Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify five sub-projects into one repository with a documented pipeline, simplify the SeaAroundUs PPR calculation to the taxon-level and Jensen-affected group-level estimates only, and distill per-taxon-per-year catch from the raw archives.

**Architecture:** Everything happens in the existing monorepo on `main`. The SeaAroundUs release tree is promoted to canonical by a manifest-driven merge; redundant archives are deleted only after byte-level verification against the directories they duplicate; the nested `FishEstimationAI` git repository is renamed to `PPREstimation` and its `.git` removed (its history lives on the remote and in two external clones). The PPR calculation keeps `calculate_sppr` unchanged and drops the corrected group aggregation. Distillation reuses the existing `standardize_catch` per year, so the 2019 slice reproduces today's `species.csv` by construction.

**Tech Stack:** Python 3.11+/3.13, pandas, numpy, pytest, nbformat, PyYAML, git, zipfile.

**Spec:** `docs/superpowers/specs/2026-09-05-projects-integration-design.md`

## Global Constraints

- Work directly on `main`. No branch. Commit per task.
- **Never push without explicit user confirmation.** The final push is a separate gated step.
- **Never commit inside, push to, or otherwise modify the nested `FishEstimationAI`/`PPREstimation` git repository.** Its history is preserved on `github.com/idocarmel1/PPREstimation` and in two independent clones at `../קוד/FishEstimation/` and `../קוד/FishEstimationAI/`. Only delete the nested `.git` directory.
- `PPREstimation/` (formerly `FishEstimationAI/`) is the main algorithm folder. **All Jensen behaviour there stays untouched** — `monte_carlo_SPPR`, `SPPR_Methods.md`, `USER_GUIDE.md`, `create_PPRS_excel.py`, `PPRCalculator.py`. Task B never touches this directory.
- `PPRAtlas/research/text/*.txt` is extracted paper text containing the author *Jensen, A.L. (1996)* and the species *Jensen's skate*. **Never edited.**
- `PPRAtlas/archive/files/` and `PPRAtlas/archive/regions/` are both live (`index.html` references them 565 and 509 times). **Neither is deleted.**
- `raw_data/SAU_downloads/` is the only source of per-taxon-per-year catch. **Never deleted, always committed.**
- Transfer efficiency is `0.1` from `config/global.yml`; `calculate_sppr(tl, te)` is `(1/te) ** (tl - 1)` and is **not modified**.
- Every deletion is verified against the artifact it duplicates *before* it runs.
- Repository root for all paths: `C:\Users\idoca\Desktop\אישי\אקדמיה\תואר שני\מחקר\BTN\GlobalPPREstimation`.

---

## File Structure

| File | Responsibility | Task |
| --- | --- | --- |
| `.gitignore` | root ignore rules, anchored so they cannot reach into project data | 1 |
| `tools/verify_redundant.py` | prove a zip duplicates an on-disk directory before deletion | 3 |
| `docs/superpowers/sau-promotion-manifest.csv` | per-path classification of the old vs release SeaAroundUs trees | 2 |
| `SeaAroundUsExtraction/src/ppr_pipeline/calculations.py` | SPPR/PPR maths; `aggregate_groups` trimmed 15 → 5 columns | 5 |
| `SeaAroundUsExtraction/src/ppr_pipeline/validation.py` | per-unit checks; drop Jensen violations, add TL-coverage assertion | 6 |
| `SeaAroundUsExtraction/src/ppr_pipeline/pipeline.py` | orchestration; summary columns renamed, `jensen_comparison.csv` no longer written | 7 |
| `SeaAroundUsExtraction/src/ppr_pipeline/notebook.py` | two generated validation notebooks; comparison section removed from both | 8 |
| `tools/migrate_group_columns.py` | one-shot rewrite of existing output CSVs to the new schema | 9 |
| `SeaAroundUsExtraction/src/ppr_pipeline/annual_catch.py` | distill a catch archive to per-taxon-per-year rows | 10 |
| `SeaAroundUsExtraction/tests/test_annual_catch.py` | tests for the above | 10 |
| `SeaAroundUsExtraction/tools/run_distillation.py` | batch-run distillation over every archive | 11 |
| `skills/ewe-species-to-group-mapper/` | renamed skill source | 12 |
| `skills/ewe-species-to-group-mapper.skill` | packaged zip | 12 |
| `README.md` | root pipeline documentation | 13 |

---

### Task 1: Establish a safety net and fix `.gitignore`

Nothing is committed yet, so every later deletion would be unrecoverable. This task fixes the ignore rules and commits all code and small files *before* anything moves.

**Files:**
- Modify: `.gitignore`
- Create: `docs/superpowers/baseline-tests.txt`

**Interfaces:**
- Consumes: nothing.
- Produces: a clean `.gitignore` that later tasks rely on; `docs/superpowers/baseline-tests.txt` recording pre-change test results for comparison in Task 15.

- [ ] **Step 1: Record the baseline test results**

Run each suite and save the output. Failures here are pre-existing, not caused by this work — record them, do not fix them.

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
{
  echo "=== baseline recorded before projects-integration work ==="
  echo "--- SeaAroundUsExtraction ---"
  (cd SeaAroundUsExtraction && python -m pytest tests -q 2>&1 | tail -20)
  echo "--- PPRAtlas ---"
  (cd PPRAtlas && python -m pytest tests -q 2>&1 | tail -20)
  echo "--- FishEstimationAI ---"
  (cd FishEstimationAI && python -m pytest tests -q 2>&1 | tail -20)
} > docs/superpowers/baseline-tests.txt
cat docs/superpowers/baseline-tests.txt
```

- [ ] **Step 2: Prove the `.gitignore` bug exists**

```bash
git check-ignore -v PPRAtlas/research/downloads
```

Expected: `.gitignore:14:downloads/	PPRAtlas/research/downloads` — real research data being silently excluded.

- [ ] **Step 3: Anchor the unanchored stock rules**

Edit `.gitignore`. Change these four lines so they only match at the repository root:

| Current line | Replace with |
| --- | --- |
| `downloads/` | `/downloads/` |
| `lib/` | `/lib/` |
| `var/` | `/var/` |
| `share/python-wheels/` | `/share/python-wheels/` |

- [ ] **Step 4: Append the project-specific rules**

Append this block to the end of `.gitignore`:

```gitignore

# --- project rules (projects-integration) ---
# Virtualenvs and IDE/editor state
.venv/
.idea/
.vscode/
.pytest_cache/
__pycache__/

# Excel lock files, created whenever a workbook anywhere in the tree is open
~$*

# Note: PPREstimation/output/ is deliberately NOT ignored. Ecobase_models/ and
# collected_PPRs.xlsx are tracked so a cloner receives them.
```

- [ ] **Step 5: Verify no real data is swallowed**

```bash
for p in PPRAtlas/research/downloads PPRAtlas/research/text PPRAtlas/inputs/legacy \
         PPRAtlas/archive/files PPRAtlas/archive/regions PPRAtlas/data \
         SeaAroundUsExtraction/spatial SeaAroundUsExtraction/global_output \
         SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04/raw_data/SAU_downloads \
         FishEstimationAI/real_models FishEstimationAI/output/Ecobase_models \
         FishEstimationAI/output/top10 NPPExtraction skills; do
  r=$(git check-ignore -v "$p" 2>/dev/null)
  if [ -n "$r" ]; then echo "FAIL ignored: $p <- $r"; else echo "ok   $p"; fi
done
```

Expected: every line reads `ok`. If any reads `FAIL`, fix `.gitignore` before continuing.

- [ ] **Step 6: Confirm `.venv` and `.idea` ARE ignored**

```bash
for p in PPRAtlas/.venv FishEstimationAI/.venv .idea FishEstimationAI/.idea; do
  if git check-ignore -q "$p"; then echo "ok   ignored: $p"; else echo "FAIL not ignored: $p"; fi
done
```

Expected: every line reads `ok`.

- [ ] **Step 7: Commit code and small files only, excluding the bulk directories**

This is the safety net. The bulk directories are added in Task 11 after deletions have shrunk them.

```bash
git add -A
git reset -q -- \
  SeaAroundUsExtraction/raw_data \
  SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04 \
  SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04_complete.zip \
  SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04_results.zip \
  SeaAroundUsExtraction/Global_history_TE010_2026-09-04 \
  SeaAroundUsExtraction/Global_history_TE010_2026-09-04.zip \
  SeaAroundUsExtraction/PPR_global_te005_results \
  SeaAroundUsExtraction/input/examples \
  PPRAtlas/archive \
  FishEstimationAI/graphify-out \
  FishEstimationAI/real_models
git status --short | head -20
git commit -m "Add code and small files as a pre-restructure safety net

Nothing was committed before this point, so every subsequent deletion would have
been unrecoverable. Commits all source, config, tables, notebooks and docs.
The bulk data directories are added in a later task, after the redundant
archives have been removed, so 2.5 GB of soon-to-be-deleted zips never enter
history.

Also anchors the stock Python gitignore rules. Unanchored 'downloads/' was
matching PPRAtlas/research/downloads and would have silently excluded real
research data from the first commit.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Promote the SeaAroundUs release tree

`EEZ_TE010_release_2026-09-04/` is newer and larger but **not** a strict superset: it has no `notebooks/`, and the two `global_output/PPR_global_summary.xlsx` differ. Classify before moving.

**Files:**
- Create: `docs/superpowers/sau-promotion-manifest.csv`
- Modify: the `SeaAroundUsExtraction/` tree

**Interfaces:**
- Consumes: the `.gitignore` from Task 1.
- Produces: a single canonical `SeaAroundUsExtraction/` with no `EEZ_TE010_release_2026-09-04/` subdirectory. Later tasks reference `SeaAroundUsExtraction/src/ppr_pipeline/*.py` at that path.

- [ ] **Step 1: Build the classification manifest**

Create and run this script (it writes the manifest and prints a summary; it moves nothing):

```python
# save as tools/build_promotion_manifest.py
from __future__ import annotations
import csv, hashlib
from pathlib import Path

ROOT = Path("SeaAroundUsExtraction")
REL = ROOT / "EEZ_TE010_release_2026-09-04"

def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def walk(base: Path, skip: Path | None = None) -> dict[str, Path]:
    out = {}
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if skip is not None and skip in p.parents:
            continue
        out[str(p.relative_to(base)).replace("\\", "/")] = p
    return out

old = walk(ROOT, skip=REL)
new = walk(REL)
rows = []
for rel in sorted(set(old) | set(new)):
    o, n = old.get(rel), new.get(rel)
    if o and not n:
        status = "only-in-old"
    elif n and not o:
        status = "only-in-release"
    elif o.stat().st_size == n.stat().st_size and digest(o) == digest(n):
        status = "identical"
    else:
        status = "differs"
    rows.append({
        "path": rel, "status": status,
        "old_bytes": o.stat().st_size if o else "",
        "release_bytes": n.stat().st_size if n else "",
    })

out = Path("docs/superpowers/sau-promotion-manifest.csv")
with out.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["path", "status", "old_bytes", "release_bytes"])
    w.writeheader(); w.writerows(rows)

from collections import Counter
counts = Counter(r["status"] for r in rows)
print(f"wrote {out}  ({len(rows)} paths)")
for k in ("identical", "only-in-release", "only-in-old", "differs"):
    print(f"  {k:16s} {counts.get(k, 0)}")
print("\n--- only-in-old (must be carried up) ---")
for r in rows:
    if r["status"] == "only-in-old":
        print("  ", r["path"])
print("\n--- differs (must be resolved explicitly) ---")
for r in rows:
    if r["status"] == "differs":
        print(f"   {r['path']}  old={r['old_bytes']} release={r['release_bytes']}")
```

Run: `python tools/build_promotion_manifest.py`

- [ ] **Step 2: Confirm the old `raw_data` is a strict subset**

The spec permits deleting the old 172-file `raw_data/` only if every file is matched in the release. Verify:

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
python - <<'PY'
from pathlib import Path
old = Path("SeaAroundUsExtraction/raw_data/SAU_downloads")
new = Path("SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04/raw_data/SAU_downloads")
o = {p.name: p.stat().st_size for p in old.glob("*")}
n = {p.name: p.stat().st_size for p in new.glob("*")}
missing = sorted(set(o) - set(n))
sizediff = sorted(k for k in set(o) & set(n) if o[k] != n[k])
print(f"old={len(o)} release={len(n)}")
print(f"missing from release : {len(missing)} {missing[:10]}")
print(f"size mismatches      : {len(sizediff)} {sizediff[:10]}")
print("VERDICT:", "SUBSET - safe to delete old" if not missing and not sizediff
      else "NOT A SUBSET - do not delete, resolve first")
PY
```

Expected: `VERDICT: SUBSET - safe to delete old`. If not, stop and report; do not delete.

- [ ] **Step 3: Resolve every `differs` path**

For each path the manifest marks `differs`, decide and record. The known cases:

- `src/ppr_pipeline/download.py`, `ingest.py`, `pipeline.py`, `provenance.py`, `years.py` — the release versions are newer and support the EEZ and te005 pipelines. **Take the release version.**
- `global_output/PPR_global_summary.xlsx` — **take the release version**; it corresponds to the release's `global_output/tables`, which also wins.

For any *other* `differs` path the manifest reports that is not in this list, stop and report it rather than guessing.

Append a `resolution` column to the manifest recording the choice per path:

```python
# save as tools/record_resolutions.py
import csv
from pathlib import Path
p = Path("docs/superpowers/sau-promotion-manifest.csv")
rows = list(csv.DictReader(p.open(encoding="utf-8")))
for r in rows:
    if r["status"] == "differs":
        r["resolution"] = "take-release (newer, supports EEZ and te005 pipelines)"
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
```

Run: `python tools/record_resolutions.py`

- [ ] **Step 4: Carry up the `only-in-old` paths, then promote**

```python
# save as tools/promote_release.py
from __future__ import annotations
import csv, shutil
from pathlib import Path

ROOT = Path("SeaAroundUsExtraction")
REL = ROOT / "EEZ_TE010_release_2026-09-04"
rows = list(csv.DictReader(Path("docs/superpowers/sau-promotion-manifest.csv").open(encoding="utf-8")))

# 1. copy every only-in-old file into the release tree so nothing unique is lost
carried = 0
for r in rows:
    if r["status"] != "only-in-old":
        continue
    src, dst = ROOT / r["path"], REL / r["path"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    carried += 1
print(f"carried up {carried} files unique to the old tree")

# 2. remove the old top-level entries the release now supersedes
for name in [p.name for p in ROOT.iterdir() if p.name != REL.name]:
    target = ROOT / name
    shutil.rmtree(target) if target.is_dir() else target.unlink()
print("removed superseded old top-level entries")

# 3. move release contents up one level
for child in list(REL.iterdir()):
    shutil.move(str(child), str(ROOT / child.name))
REL.rmdir()
print("release promoted; release directory removed")
```

Run: `python tools/promote_release.py`

- [ ] **Step 5: Verify the promotion**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
test ! -d SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04 && echo "ok  release dir gone"
test -d SeaAroundUsExtraction/notebooks && echo "ok  notebooks carried up"
test -f SeaAroundUsExtraction/src/ppr_pipeline/eez_spatial.py && echo "ok  eez_spatial.py present"
test -f SeaAroundUsExtraction/run_eez_pipeline.py && echo "ok  run_eez_pipeline.py present"
test -d SeaAroundUsExtraction/eez_output && echo "ok  eez_output present"
echo -n "raw archives: " && ls SeaAroundUsExtraction/raw_data/SAU_downloads | wc -l
```

Expected: all five `ok` lines, and `raw archives: 739`.

- [ ] **Step 6: Run the SeaAroundUs test suite**

Run: `cd SeaAroundUsExtraction && python -m pytest tests -q`
Expected: results match the SeaAroundUs section of `docs/superpowers/baseline-tests.txt`.

- [ ] **Step 7: Commit**

```bash
git add -A tools docs SeaAroundUsExtraction
git reset -q -- SeaAroundUsExtraction/raw_data SeaAroundUsExtraction/input/examples
git commit -m "Promote the SeaAroundUs release tree to canonical

EEZ_TE010_release_2026-09-04/ held newer code (eez_spatial.py, the EEZ and te005
pipelines, newer download/ingest/pipeline/provenance/years) and 739 raw archives
against the old tree's 172, but was not a strict superset: it had no notebooks/.

Classified every path first (docs/superpowers/sau-promotion-manifest.csv), carried
up everything unique to the old tree, resolved each differing file explicitly, then
moved the release contents up and removed the release directory.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Delete redundant archives and superseded outputs

**Files:**
- Create: `tools/verify_redundant.py`
- Delete: four zips, two superseded output directories, one stale graph directory

**Interfaces:**
- Consumes: the promoted tree from Task 2.
- Produces: a tree roughly 3 GB smaller. No code depends on the deleted paths.

- [ ] **Step 1: Write the redundancy verifier**

```python
# save as tools/verify_redundant.py
"""Prove a zip's contents already exist on disk before the zip is deleted."""
from __future__ import annotations
import sys, zipfile
from pathlib import Path

def verify(archive: str, directory: str, strip: int = 1) -> bool:
    zpath, dpath = Path(archive), Path(directory)
    if not zpath.exists():
        print(f"SKIP  {zpath} does not exist"); return True
    if not dpath.exists():
        print(f"FAIL  {zpath}: directory {dpath} does not exist"); return False
    missing, mismatched, checked = [], [], 0
    with zipfile.ZipFile(zpath) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            parts = Path(info.filename).parts[strip:]
            if not parts:
                continue
            on_disk = dpath.joinpath(*parts)
            if not on_disk.exists():
                missing.append(info.filename)
            elif on_disk.stat().st_size != info.file_size:
                mismatched.append((info.filename, info.file_size, on_disk.stat().st_size))
            checked += 1
    print(f"{zpath.name}: checked {checked} entries against {dpath}")
    print(f"   missing on disk : {len(missing)}   {missing[:5]}")
    print(f"   size mismatches : {len(mismatched)}   {mismatched[:5]}")
    ok = not missing and not mismatched
    print("   VERDICT:", "REDUNDANT - safe to delete" if ok else "NOT REDUNDANT - keep")
    return ok

if __name__ == "__main__":
    strip = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    sys.exit(0 if verify(sys.argv[1], sys.argv[2], strip) else 1)
```

- [ ] **Step 2: Verify each zip against the directory it duplicates**

`strip` is the number of leading path components inside the zip to drop. Determine it per zip by inspecting the first entries, then run the verifier.

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
for z in PPRAtlas/archive/regions.zip \
         SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04_complete.zip \
         SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04_results.zip; do
  echo "=== $z ==="; python -c "
import zipfile,sys
with zipfile.ZipFile('$z') as zf:
    for n in zf.namelist()[:4]: print('   ', n)
"
done
```

Then verify each with the `strip` value that makes entries line up:

```bash
python tools/verify_redundant.py PPRAtlas/archive/regions.zip PPRAtlas/archive/regions 1
python tools/verify_redundant.py SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04_complete.zip SeaAroundUsExtraction 1
python tools/verify_redundant.py SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04_results.zip SeaAroundUsExtraction/eez_output 1
```

Expected: `VERDICT: REDUNDANT - safe to delete` for each. If any reports `NOT REDUNDANT`, stop and report — do not delete that zip.

Note the `_complete.zip` was made before promotion, so its paths are relative to the old release directory; after promotion those files sit directly under `SeaAroundUsExtraction/`. If `strip` cannot be made to line up, report rather than guessing.

- [ ] **Step 3: Delete the verified-redundant zips**

```bash
rm -v PPRAtlas/archive/regions.zip
rm -v SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04_complete.zip
rm -v SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04_results.zip
```

- [ ] **Step 4: Delete the superseded outputs**

These are **not** recoverable from another on-disk copy. The user authorised each explicitly: they implement the 1995 SPPR/PPR method from `PPRCalculator`, which will be recomputed per LME later.

```bash
rm -rv SeaAroundUsExtraction/Global_history_TE010_2026-09-04
rm -v  SeaAroundUsExtraction/Global_history_TE010_2026-09-04.zip
rm -v  SeaAroundUsExtraction/Global_history_TE010_2026-09-04.delivery.json
rm -rv SeaAroundUsExtraction/PPR_global_te005_results
rm -rv FishEstimationAI/graphify-out
```

- [ ] **Step 5: Confirm nothing in the code referenced the deleted paths**

```bash
grep -rn "Global_history\|te005\|graphify-out\|regions\.zip\|_complete\.zip\|_results\.zip" \
  --include="*.py" --include="*.yml" --include="*.yaml" --include="*.md" \
  --exclude-dir=.git --exclude-dir=.venv --exclude-dir=docs . | grep -v "^./tools/verify_redundant.py" || echo "no live references (good)"
```

Any hit outside `docs/` must be resolved before committing.

- [ ] **Step 6: Report space reclaimed and commit**

```bash
du -sh SeaAroundUsExtraction PPRAtlas FishEstimationAI
git add -A
git commit -m "Delete redundant archives and superseded 1995-method outputs

Verified-redundant zips, each proven against the on-disk directory it duplicates
before deletion (tools/verify_redundant.py):
  PPRAtlas/archive/regions.zip                          579 MB
  EEZ_TE010_release_2026-09-04_complete.zip             1.7 GB
  EEZ_TE010_release_2026-09-04_results.zip               16 MB

Superseded outputs, authorised by the user because they implement the 1995
SPPR/PPR method from PPRCalculator which will be recomputed per LME:
  Global_history_TE010_2026-09-04/ and its zip             470 MB
  PPR_global_te005_results/                                 13 MB

Stale partial knowledge graph, replaced later by a repo-wide one:
  FishEstimationAI/graphify-out/                            15 MB

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Rename `FishEstimationAI` to `PPREstimation` and collapse its git repository

**Files:**
- Rename: `FishEstimationAI/` → `PPREstimation/`
- Modify: `PPREstimation/CLAUDE.md`, `PPREstimation/README.md`, `PPREstimation/information/USER_GUIDE.md`, `PPREstimation/notebooks/hackaton040926.ipynb`, `PPREstimation/.claude/settings.local.json`
- Delete: `PPREstimation/.git`, `PPREstimation/.gitignore`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `PPREstimation/` as a plain tracked directory. Tasks 13 and 14 reference it by that name.

- [ ] **Step 1: Record the nested repository's provenance before removing it**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
{
  echo "remote: $(git -C FishEstimationAI remote get-url origin)"
  echo "HEAD:   $(git -C FishEstimationAI rev-parse HEAD)"
  echo "branch: $(git -C FishEstimationAI rev-parse --abbrev-ref HEAD)"
  echo "uncommitted changes at time of collapse:"
  git -C FishEstimationAI status --short
} > docs/superpowers/ppre-provenance.txt
cat docs/superpowers/ppre-provenance.txt
```

- [ ] **Step 2: Confirm the external clones exist and are untouched**

This is what makes deleting the nested `.git` safe.

```bash
for d in "../קוד/FishEstimation" "../קוד/FishEstimationAI"; do
  if [ -d "$d/.git" ]; then
    echo "ok  $d -> $(git -C "$d" remote get-url origin)"
  else
    echo "FAIL  $d is not a git repository"
  fi
done
```

Expected: both `ok`, both pointing at `https://github.com/idocarmel1/PPREstimation.git`. If either fails, **stop** and report — do not delete the nested `.git`.

- [ ] **Step 3: Delete the nested `.git` and the now-redundant nested `.gitignore`**

Do not commit inside it, do not push to it.

```bash
rm -rf FishEstimationAI/.git
rm -f  FishEstimationAI/.gitignore
test ! -d FishEstimationAI/.git && echo "ok  nested .git removed"
```

The nested `.gitignore` is removed because its `output/*` / `!output/top10/` rule would keep `output/Ecobase_models/` and `output/collected_PPRs.xlsx` from reaching a cloner. The root `.gitignore` from Task 1 already carries forward the rules that still apply.

- [ ] **Step 4: Rename the directory**

```bash
git mv FishEstimationAI PPREstimation 2>/dev/null || mv FishEstimationAI PPREstimation
test -d PPREstimation && echo "ok  renamed"
```

- [ ] **Step 5: Update the textual references**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
for f in PPREstimation/CLAUDE.md PPREstimation/README.md \
         PPREstimation/information/USER_GUIDE.md \
         PPREstimation/notebooks/hackaton040926.ipynb \
         PPREstimation/.claude/settings.local.json; do
  [ -f "$f" ] && sed -i 's/FishEstimationAI/PPREstimation/g' "$f" && echo "updated $f"
done
```

- [ ] **Step 6: Verify no stale references remain outside ignored paths**

```bash
grep -rn "FishEstimationAI" --exclude-dir=.git --exclude-dir=.venv --exclude-dir=.idea \
  --exclude-dir=__pycache__ --exclude-dir=docs --exclude-dir=archive . || echo "no stale references (good)"
```

Hits inside `docs/` are historical records in the spec and provenance file and are expected — leave them.

- [ ] **Step 7: Confirm the Jensen behaviour is untouched**

```bash
grep -c -i "jensen" PPREstimation/information/SPPR_Methods.md PPREstimation/information/USER_GUIDE.md \
                    PPREstimation/create_PPRS_excel.py PPREstimation/CLAUDE.md
```

Expected: non-zero counts, unchanged from before the rename. This directory's Jensen handling is the real Monte-Carlo correction and must survive intact.

- [ ] **Step 8: Run the PPREstimation test suite**

Run: `cd PPREstimation && python -m pytest tests -q`
Expected: matches the FishEstimationAI section of `docs/superpowers/baseline-tests.txt`.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "Rename FishEstimationAI to PPREstimation and collapse its nested git repo

The directory now matches the name of the repository it came from. Its nested .git
is deleted rather than merged: history is preserved on github.com/idocarmel1/PPREstimation
and in two independent clones outside this repository, both verified present before
deletion. Nothing was committed to or pushed to that remote.

Provenance recorded in docs/superpowers/ppre-provenance.txt.

The nested .gitignore is removed so output/Ecobase_models/ and collected_PPRs.xlsx
reach a cloner; the rules that still apply were folded into the root .gitignore.

All Jensen behaviour in this directory is untouched - it is the genuine
Jensen's-inequality Monte-Carlo correction, unrelated to the SeaAroundUs comparison
baseline removed elsewhere in this work.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Trim `aggregate_groups` to the Jensen-affected calculation

**Files:**
- Modify: `SeaAroundUsExtraction/src/ppr_pipeline/calculations.py:45-129`
- Test: `SeaAroundUsExtraction/tests/test_calculations.py:43-105`

**Interfaces:**
- Consumes: `calculate_sppr(tl, te)` (unchanged).
- Produces: `aggregate_groups(species, group_column, te=0.1, catch_column="catch_tonnes", tl_column="tl")` returning a DataFrame with exactly these columns in this order: `[group_column, "catch_tonnes_matched", "tl_weighted", "sppr", "ppr"]`. Tasks 6, 7 and 9 depend on these names.

- [ ] **Step 1: Rewrite the tests for the new schema**

Replace `test_group_aggregation_reports_correct_and_jensen_results` and `test_jensen_difference_is_zero_for_uniform_trophic_level` in `SeaAroundUsExtraction/tests/test_calculations.py` with:

```python
def test_group_aggregation_returns_catch_weighted_jensen_values() -> None:
    species = pd.DataFrame(
        {
            "commercial_group": ["Cod-likes", "Cod-likes"],
            "catch_tonnes": [5.0, 5.0],
            "tl": [2.0, 3.0],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    result = calculations.aggregate_groups(species, "commercial_group", te=0.1)

    assert list(result.columns) == [
        "commercial_group",
        "catch_tonnes_matched",
        "tl_weighted",
        "sppr",
        "ppr",
    ]
    row = result.iloc[0]
    assert row["catch_tonnes_matched"] == pytest.approx(10.0)
    # catch-weighted mean TL of 2.0 and 3.0 at equal catch
    assert row["tl_weighted"] == pytest.approx(2.5)
    # 10 ** (2.5 - 1)
    assert row["sppr"] == pytest.approx(31.6227766017)
    assert row["ppr"] == pytest.approx(316.227766017)


def test_group_aggregation_matches_taxon_sum_for_uniform_trophic_level() -> None:
    """With one TL there is no Jensen gap, so the group value equals the taxon sum."""
    species = pd.DataFrame(
        {
            "commercial_group": ["Anchovies", "Anchovies"],
            "catch_tonnes": [4.0, 6.0],
            "tl": [3.0, 3.0],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    result = calculations.aggregate_groups(species, "commercial_group", te=0.1)

    assert result.iloc[0]["ppr"] == pytest.approx(float(species["ppr"].sum()))


def test_group_aggregation_underestimates_taxon_sum_when_trophic_levels_differ() -> None:
    """The retained group figure is deliberately the Jensen-affected one."""
    species = pd.DataFrame(
        {
            "commercial_group": ["Mixed", "Mixed"],
            "catch_tonnes": [5.0, 5.0],
            "tl": [2.0, 4.0],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    result = calculations.aggregate_groups(species, "commercial_group", te=0.1)

    taxon_sum = float(species["ppr"].sum())
    assert result.iloc[0]["ppr"] < taxon_sum


def test_group_aggregation_returns_nan_when_no_taxon_has_a_trophic_level() -> None:
    species = pd.DataFrame(
        {
            "commercial_group": ["Unknown"],
            "catch_tonnes": [10.0],
            "tl": [float("nan")],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    result = calculations.aggregate_groups(species, "commercial_group", te=0.1)

    row = result.iloc[0]
    assert row["catch_tonnes_matched"] == pytest.approx(0.0)
    assert pd.isna(row["tl_weighted"])
    assert pd.isna(row["sppr"])
    assert pd.isna(row["ppr"])
```

Also update the column-ordering test at lines 93-105 to assert the new five-column list rather than the old fifteen.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd SeaAroundUsExtraction && python -m pytest tests/test_calculations.py -q`
Expected: FAIL — `assert list(result.columns) == [...]` mismatches, because the current implementation returns fifteen columns with `_jensen` suffixes.

- [ ] **Step 3: Rewrite `aggregate_groups`**

Replace the whole function body in `SeaAroundUsExtraction/src/ppr_pipeline/calculations.py` with:

```python
def aggregate_groups(
    species: pd.DataFrame,
    group_column: str,
    te: float = 0.1,
    catch_column: str = "catch_tonnes",
    tl_column: str = "tl",
) -> pd.DataFrame:
    """Aggregate taxa to groups using the catch-weighted mean trophic level.

    This is deliberately the Jensen-affected aggregation: the catch-weighted mean TL
    is exponentiated once per group, rather than summing each taxon's PPR. Because
    ``10 ** (TL - 1)`` is convex, the result understates the taxon-level sum whenever
    a group spans more than one trophic level. That gap is the point - it is what
    makes the cost of moving from taxa to groups visible, which an Ecopath model
    cannot show on its own because it has no taxon level.

    The correctly-aggregated value is not returned. It is exactly the sum of taxon
    ``ppr`` within the group, recoverable from the taxon table with a ``groupby``.
    """

    _validate_te(te)
    required = {group_column, catch_column, tl_column, "ppr"}
    missing = required - set(species.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    work = species.copy()
    work[group_column] = work[group_column].fillna("Unclassified").replace("", "Unclassified")
    work[catch_column] = pd.to_numeric(work[catch_column], errors="raise")
    if (work[catch_column] < 0).any():
        raise ValueError("Catch must be non-negative.")
    work[tl_column] = pd.to_numeric(work[tl_column], errors="raise")
    work["is_tl_matched"] = work[tl_column].notna()

    output_columns = [
        group_column,
        "catch_tonnes_matched",
        "tl_weighted",
        "sppr",
        "ppr",
    ]
    rows: list[dict[str, Any]] = []
    for group, part in work.groupby(group_column, sort=True, dropna=False):
        matched = part.loc[part["is_tl_matched"]]
        catch_matched = float(matched[catch_column].sum())

        if catch_matched > 0:
            tl_weighted = float(
                np.average(matched[tl_column].to_numpy(), weights=matched[catch_column].to_numpy())
            )
            sppr = float(calculate_sppr(tl_weighted, te=te))
            ppr = catch_matched * sppr
        else:
            tl_weighted = np.nan
            sppr = np.nan
            ppr = np.nan

        rows.append(
            {
                group_column: group,
                "catch_tonnes_matched": catch_matched,
                "tl_weighted": tl_weighted,
                "sppr": sppr,
                "ppr": ppr,
            }
        )
    return pd.DataFrame(rows, columns=output_columns)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd SeaAroundUsExtraction && python -m pytest tests/test_calculations.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add SeaAroundUsExtraction/src/ppr_pipeline/calculations.py SeaAroundUsExtraction/tests/test_calculations.py
git commit -m "Trim aggregate_groups to the Jensen-affected calculation

Fifteen columns become five: group, catch_tonnes_matched, tl_weighted, sppr, ppr.
Dropped the corrected aggregation (sppr_correct, ppr_correct), the comparison
machinery (jensen_difference, jensen_ratio_correct_to_error,
jensen_percent_difference) and five QA columns.

The retained group figures are deliberately the Jensen-affected ones - they expose
the bias in moving from taxa to groups, which PPRCalculator cannot show because
Ecopath models are group-based. The corrected value is not stored because it is
exactly the taxon-ppr sum within the group, recoverable with a groupby.

The _jensen suffix is dropped since the file name states the grouping.
calculate_sppr is unchanged: (1/te) ** (tl - 1), which at te=0.1 is 10 ** (TL - 1).

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Replace the Jensen-violations check with a TL-coverage assertion

Dropping `catch_coverage_fraction` from the group tables is safe only while TL coverage is complete. It is complete today (2268 group rows, none below 100 %) but that is measured on 2019 alone, and Task 10 extends to 1950-2019.

**Files:**
- Modify: `SeaAroundUsExtraction/src/ppr_pipeline/validation.py`
- Test: `SeaAroundUsExtraction/tests/test_validation.py`

**Interfaces:**
- Consumes: `aggregate_groups` output from Task 5 (columns `catch_tonnes_matched`, `ppr`).
- Produces: `validate_region(...)` emitting a `tl_coverage_complete` boolean check and no `*_jensen_violations` checks. `_sum_ppr` now reads the `ppr` column.

- [ ] **Step 1: Write the failing tests**

In `SeaAroundUsExtraction/tests/test_validation.py`, replace the Jensen assertions with:

```python
def test_validate_region_flags_complete_trophic_level_coverage() -> None:
    species = pd.DataFrame(
        {
            "commercial_group": ["Cod-likes", "Anchovies"],
            "functional_group": ["Large demersals", "Small pelagics"],
            "catch_tonnes": [10.0, 5.0],
            "tl": [4.0, 3.0],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    commercial = calculations.aggregate_groups(species, "commercial_group", te=0.1)
    functional = calculations.aggregate_groups(species, "functional_group", te=0.1)

    metrics = validation.validate_region(
        "LME_003", species, commercial, functional, raw_filtered_tonnes=15.0
    ).set_index("check")["value"].to_dict()

    assert metrics["tl_coverage_complete"] is True
    assert "commercial_jensen_violations" not in metrics
    assert "functional_jensen_violations" not in metrics


def test_validate_region_reports_incomplete_trophic_level_coverage() -> None:
    species = pd.DataFrame(
        {
            "commercial_group": ["Cod-likes", "Unknown"],
            "functional_group": ["Large demersals", "Unknown"],
            "catch_tonnes": [10.0, 5.0],
            "tl": [4.0, float("nan")],
        }
    )
    species = calculations.add_species_ppr(species, te=0.1)
    commercial = calculations.aggregate_groups(species, "commercial_group", te=0.1)
    functional = calculations.aggregate_groups(species, "functional_group", te=0.1)

    metrics = validation.validate_region(
        "LME_003", species, commercial, functional, raw_filtered_tonnes=15.0
    ).set_index("check")["value"].to_dict()

    assert metrics["tl_coverage_complete"] is False
    assert metrics["unmatched_taxa_count"] == 1
```

Delete `test_validate_region_reconciles_catch_ppr_coverage_and_jensen`'s Jensen assertions (lines 37-38) and update the test at line 55 that mutates `commercial.loc[0, "ppr_correct"]` to mutate `commercial.loc[0, "ppr"]` instead.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd SeaAroundUsExtraction && python -m pytest tests/test_validation.py -q`
Expected: FAIL — `KeyError: 'ppr_correct'` from `_sum_ppr`, and `tl_coverage_complete` missing.

- [ ] **Step 3: Update `validation.py`**

In `SeaAroundUsExtraction/src/ppr_pipeline/validation.py`:

Change `_sum_ppr` to read the renamed column:

```python
def _sum_ppr(frame: pd.DataFrame) -> float:
    return float(pd.to_numeric(frame["ppr"], errors="coerce").sum())
```

Delete `_jensen_violations` entirely (lines 11-16).

Note that `commercial_ok` / `functional_ok` compare the group PPR against the taxon sum. Those two comparisons now hold only when every group spans a single TL, which is not generally true — the group value is deliberately the Jensen-affected one. Replace those two metric rows and the two Jensen rows with the coverage assertion. In the `metrics` list, remove:

```python
        ("commercial_ppr_reconciled", commercial_ok, "boolean"),
        ("functional_ppr_reconciled", functional_ok, "boolean"),
        ("commercial_jensen_violations", _jensen_violations(commercial, tolerance), "count"),
        ("functional_jensen_violations", _jensen_violations(functional, tolerance), "count"),
```

and add in their place:

```python
        ("tl_coverage_complete", bool(species["tl"].notna().all()), "boolean"),
```

Also delete the now-unused `commercial_ok` and `functional_ok` assignments (lines 38-39). Keep `commercial_ppr_difference` and `functional_ppr_difference` — with the corrected value gone, those differences now measure the Jensen gap itself, which is worth reporting. Update the docstring of `validate_region` to say so:

```python
    """Return long-form validation metrics for one unit.

    ``commercial_ppr_difference`` and ``functional_ppr_difference`` are the group PPR
    minus the taxon-summed PPR. Because the group figures use the catch-weighted mean
    trophic level, these differences are the Jensen gap and are expected to be
    negative wherever a group spans more than one trophic level.

    ``tl_coverage_complete`` guards the decision to drop the per-group coverage
    columns: it is False as soon as any taxon lacks a trophic level, which would make
    the group PPR a silent underestimate.
    """
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd SeaAroundUsExtraction && python -m pytest tests/test_validation.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add SeaAroundUsExtraction/src/ppr_pipeline/validation.py SeaAroundUsExtraction/tests/test_validation.py
git commit -m "Replace Jensen-violation checks with a TL-coverage assertion

Dropped _jensen_violations and the two *_ppr_reconciled checks: both compared the
group value against the taxon sum, a comparison that no longer holds now the group
value is deliberately the Jensen-affected one.

Added tl_coverage_complete. This is what licenses dropping the five per-group QA
columns in the previous commit - coverage is 100% across all 2268 group rows today,
but only for the 2019 analysis year, and distillation extends to 1950-2019 where
older taxa may lack a TL match. One assertion replaces five columns and turns a
silent underestimate into a visible failure.

Kept the *_ppr_difference metrics: with the corrected value gone they now measure
the Jensen gap directly.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: Update the pipeline summary columns and stop writing `jensen_comparison.csv`

**Files:**
- Modify: `SeaAroundUsExtraction/src/ppr_pipeline/pipeline.py:138-142` and `:352,359`
- Test: `SeaAroundUsExtraction/tests/test_pipeline.py:186`

**Interfaces:**
- Consumes: `aggregate_groups` output from Task 5.
- Produces: `summarize_units(...)` emitting `ppr_species`, `ppr_commercial`, `ppr_functional` (no `_correct`/`_jensen` variants). No `jensen_comparison.csv` is written. Task 9 migrates existing CSVs to match.

- [ ] **Step 1: Update the failing test**

In `SeaAroundUsExtraction/tests/test_pipeline.py`, change line 186 from `summary.loc["A", "ppr_commercial_correct"]` to `summary.loc["A", "ppr_commercial"]`, and add:

```python
def test_summary_has_no_corrected_or_jensen_suffixed_columns() -> None:
    """The corrected aggregation and the _jensen suffix are both gone."""
    results = _minimal_results()          # reuse the fixture the other tests use
    summary = pipeline.summarize_units(results, scope_label="pilot")

    assert "ppr_species" in summary.columns
    assert "ppr_commercial" in summary.columns
    assert "ppr_functional" in summary.columns
    assert not [c for c in summary.columns if c.endswith("_correct")]
    assert not [c for c in summary.columns if c.endswith("_jensen")]
```

If `test_pipeline.py` has no reusable results fixture, build one inline from `calculations.add_species_ppr` and `calculations.aggregate_groups` matching the shape `summarize_units` expects (`{"name", "region_type", "year", "species", "commercial", "functional"}`).

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd SeaAroundUsExtraction && python -m pytest tests/test_pipeline.py -q`
Expected: FAIL — `KeyError: 'ppr_correct'` when `summarize_units` sums the group frames.

- [ ] **Step 3: Update the summary row construction**

In `SeaAroundUsExtraction/src/ppr_pipeline/pipeline.py`, replace these four lines:

```python
                "ppr_commercial_correct": float(commercial["ppr_correct"].sum()),
                "ppr_functional_correct": float(functional["ppr_correct"].sum()),
                "ppr_commercial_jensen": float(commercial["ppr_jensen"].sum()),
                "ppr_functional_jensen": float(functional["ppr_jensen"].sum()),
```

with:

```python
                # Group values use the catch-weighted mean TL, so they are the
                # Jensen-affected aggregation. ppr_species is the taxon-level truth.
                "ppr_commercial": float(commercial["ppr"].sum()),
                "ppr_functional": float(functional["ppr"].sum()),
```

- [ ] **Step 4: Stop writing `jensen_comparison.csv`**

Once the corrected columns are gone, that file is just `commercial.csv` and `functional.csv` concatenated. Remove the line that builds it:

```python
    jensen = pd.concat([commercial_all, functional_all], ignore_index=True)
```

and the line that writes it:

```python
    jensen.to_csv(table_dir / "jensen_comparison.csv", index=False, encoding="utf-8-sig")
```

`commercial_all` and `functional_all` are still produced by `_combined_group_table`. Check whether they are used elsewhere in the function; if they are now unused, remove those two assignments too. If they are used, leave them.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd SeaAroundUsExtraction && python -m pytest tests -q`
Expected: PASS, other than any failure already recorded in `docs/superpowers/baseline-tests.txt`.

- [ ] **Step 6: Commit**

```bash
git add SeaAroundUsExtraction/src/ppr_pipeline/pipeline.py SeaAroundUsExtraction/tests/test_pipeline.py
git commit -m "Rename summary PPR columns and stop emitting jensen_comparison.csv

Summary columns are now ppr_species (taxon-level), ppr_commercial and
ppr_functional (both Jensen-affected group aggregations). The _correct and _jensen
suffixed pairs are gone.

jensen_comparison.csv is no longer written: with the corrected columns removed it
was exactly commercial.csv and functional.csv concatenated.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 8: Remove the comparison section from both generated notebooks

`notebook.py` has **two** builders, and both carry the Jensen section:
`build_validation_notebook(output_path)` (pilot scope, lines 9-140) and
`build_scope_validation_notebook(output, scope_label, output_directory, unit_description)`
(lines 143-287). Both must be updated.

**Files:**
- Modify: `SeaAroundUsExtraction/src/ppr_pipeline/notebook.py` — lines 62-71 and 88-106 in the first builder, lines 209-212 and 239-256 in the second
- Test: `SeaAroundUsExtraction/tests/test_notebook.py:8-18`

**Interfaces:**
- Consumes: the check names produced in Task 6 (`tl_coverage_complete`; no `*_ppr_reconciled`, no `*_jensen_violations`).
- Produces: both builders emit notebooks with no reference to `jensen_comparison.csv` or the removed checks.

- [ ] **Step 1: Update the existing test, which currently asserts the opposite**

`test_validation_notebook_contains_required_scientific_checks` asserts
`"Jensen" in text` and asserts on `commercial_ppr_reconciled` /
`functional_ppr_reconciled`. All three are removed by this work, so the test must be
updated, not merely added to. Replace lines 8-18 of
`SeaAroundUsExtraction/tests/test_notebook.py` with:

```python
def test_validation_notebook_contains_required_scientific_checks(tmp_path) -> None:
    output = tmp_path / "pilot_validation.ipynb"
    build_validation_notebook(output)
    notebook = nbformat.read(output, as_version=4)
    text = "\n".join("".join(cell.source) for cell in notebook.cells)
    assert "SPPR = 10" in text
    assert "catch_reconciled" in text
    assert "tl_coverage_complete" in text
    assert sum(cell.cell_type == "code" for cell in notebook.cells) >= 5


def test_validation_notebook_has_no_jensen_comparison(tmp_path) -> None:
    output = tmp_path / "pilot_validation.ipynb"
    build_validation_notebook(output)
    notebook = nbformat.read(output, as_version=4)
    text = "\n".join("".join(cell.source) for cell in notebook.cells)
    assert "jensen_comparison.csv" not in text
    assert "jensen_violations" not in text
    assert "Jensen" not in text
    assert "ppr_correct" not in text


def test_scope_validation_notebook_has_no_jensen_comparison(tmp_path) -> None:
    output = tmp_path / "global_validation.ipynb"
    build_scope_validation_notebook(
        output,
        scope_label="global",
        output_directory="global_output",
        unit_description="all 66 LMEs and 18 High Seas units",
    )
    notebook = nbformat.read(output, as_version=4)
    text = "\n".join("".join(cell.source) for cell in notebook.cells)
    assert "jensen_comparison.csv" not in text
    assert "jensen_violations" not in text
    assert "Jensen" not in text
    assert "ppr_correct" not in text
    assert "tl_coverage_complete" in text
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd SeaAroundUsExtraction && python -m pytest tests/test_notebook.py -q`
Expected: FAIL — `assert "Jensen" not in text` fails for both builders, and
`tl_coverage_complete` is absent.

- [ ] **Step 3: Fix the reconciliation cell in `build_validation_notebook`**

Replace the code-cell body at lines 62-71 (the one starting
`validation = pd.read_csv(TABLES / 'validation.csv')`) with:

```python
validation = pd.read_csv(TABLES / 'validation.csv')
key_checks = ['catch_reconciled', 'tl_coverage_complete']
display(validation[validation['check'].isin(key_checks)].pivot(index='unit_id', columns='check', values='value'))

boolean_checks = validation[validation['check'].isin(key_checks)]
assert boolean_checks['value'].astype(str).str.lower().isin(['true', '1', '1.0']).all()
```

- [ ] **Step 4: Delete the comparison cells from `build_validation_notebook`**

Delete the `new_markdown_cell` at lines 88-93 beginning
`"## Correct aggregation versus intentional Jensen-error aggregation"` and the
`new_code_cell` immediately after it (lines 94-106) that reads
`jensen_comparison.csv` and plots `underestimate_fraction`.

- [ ] **Step 5: Fix the reconciliation cell in `build_scope_validation_notebook`**

At line 209, replace:

```python
boolean_names = ['catch_reconciled', 'commercial_ppr_reconciled', 'functional_ppr_reconciled']
```

with:

```python
boolean_names = ['catch_reconciled', 'tl_coverage_complete']
```

and delete line 212, `violation_checks = validation[validation['check'].str.endswith('jensen_violations')].copy()`,
together with any assertion that consumes `violation_checks`.

- [ ] **Step 6: Delete the comparison cells from `build_scope_validation_notebook`**

Delete the `new_markdown_cell` at lines 239-244 beginning
`"## Correct aggregation versus intentional Jensen-error aggregation"` and the
`new_code_cell` after it (lines 245-256) that reads `jensen_comparison.csv` and
computes `global_bias` and `regional_bias`.

- [ ] **Step 7: Run the tests to verify they pass**

Run: `cd SeaAroundUsExtraction && python -m pytest tests/test_notebook.py -q`
Expected: PASS.

- [ ] **Step 8: Regenerate or delete the committed executed notebooks**

`global_output/global_validation_executed.ipynb` and `notebooks/global_validation.ipynb`
are committed artifacts that still contain the removed section and still read
`jensen_comparison.csv`, which no longer exists. Regenerate them with the updated
builder if the pipeline can be re-run cheaply; otherwise delete them and note in
`global_output/README.md` that they are regenerated by `build_global_notebook.py`.
Leaving a committed notebook that reads a deleted file is not acceptable.

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/SeaAroundUsExtraction"
grep -l "jensen_comparison" notebooks/*.ipynb global_output/*.ipynb eez_output/*.ipynb 2>/dev/null || echo "none remain"
```

- [ ] **Step 9: Commit**

```bash
git add SeaAroundUsExtraction/src/ppr_pipeline/notebook.py SeaAroundUsExtraction/tests/test_notebook.py \
        SeaAroundUsExtraction/notebooks SeaAroundUsExtraction/global_output SeaAroundUsExtraction/eez_output
git commit -m "Remove the Jensen-comparison section from both notebook builders

notebook.py has two builders and both carried the section. Their narrative cells
and underestimation plots read jensen_comparison.csv, which is no longer produced.
Reconciliation cells now assert on catch_reconciled and tl_coverage_complete
instead of the removed *_ppr_reconciled and *_jensen_violations checks.

The existing test asserted that Jensen appears in the notebook text and asserted on
the reconciled checks, so it was updated rather than extended.

Committed executed notebooks that referenced the deleted CSV are regenerated.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 9: Migrate the existing output CSVs to the new schema

Code and data must agree. This rewrites the already-generated outputs by column removal and renaming, rather than re-running the pipeline, so the change is deterministic and every surviving value is provably unchanged.

**Files:**
- Create: `tools/migrate_group_columns.py`
- Modify: `SeaAroundUsExtraction/global_output/tables/**`, `SeaAroundUsExtraction/eez_output/tables/**`, `PPRAtlas/inputs/annual_regions.csv`
- Delete: every `jensen_comparison.csv`

**Interfaces:**
- Consumes: the column names produced in Tasks 5 and 7.
- Produces: on-disk CSVs matching the new code. Task 13 documents them.

- [ ] **Step 1: Write the migration script with a built-in value-identity check**

```python
# save as tools/migrate_group_columns.py
"""Rewrite existing SeaAroundUs outputs to the trimmed schema.

Every surviving value must be byte-identical to its pre-change counterpart; only
whole columns disappear or change name. The script proves this as it goes.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

GROUP_DROP = [
    "taxon_count_total", "taxon_count_matched", "catch_tonnes_total",
    "catch_tonnes_missing_tl", "catch_coverage_fraction",
    "sppr_correct", "ppr_correct",
    "jensen_difference", "jensen_ratio_correct_to_error", "jensen_percent_difference",
]
GROUP_RENAME = {"tl_weighted_jensen": "tl_weighted", "sppr_jensen": "sppr", "ppr_jensen": "ppr"}

SUMMARY_DROP = ["ppr_commercial_correct", "ppr_functional_correct"]
SUMMARY_RENAME = {"ppr_commercial_jensen": "ppr_commercial", "ppr_functional_jensen": "ppr_functional"}

def migrate(path: Path, drop: list[str], rename: dict[str, str]) -> str:
    before = pd.read_csv(path, encoding="utf-8-sig")
    after = before.drop(columns=[c for c in drop if c in before.columns])
    after = after.rename(columns={k: v for k, v in rename.items() if k in before.columns})
    # prove every surviving value is unchanged
    for new_name in after.columns:
        old_name = next((k for k, v in rename.items() if v == new_name), new_name)
        if old_name not in before.columns:
            raise AssertionError(f"{path}: column {new_name} has no source column")
        lhs, rhs = before[old_name], after[new_name]
        if not lhs.equals(rhs.rename(old_name)):
            raise AssertionError(f"{path}: values changed in {old_name} -> {new_name}")
    if list(after.columns) == list(before.columns):
        return "unchanged"
    after.to_csv(path, index=False, encoding="utf-8-sig")
    return f"{len(before.columns)} -> {len(after.columns)} cols"

def main() -> int:
    touched = deleted = 0
    for root in (Path("SeaAroundUsExtraction/global_output"), Path("SeaAroundUsExtraction/eez_output")):
        if not root.exists():
            continue
        for name in ("commercial.csv", "functional.csv"):
            for f in root.rglob(name):
                print(f"  {f}: {migrate(f, GROUP_DROP, GROUP_RENAME)}"); touched += 1
        for f in list(root.rglob("*_summary.csv")):
            print(f"  {f}: {migrate(f, SUMMARY_DROP, SUMMARY_RENAME)}"); touched += 1
        for f in list(root.rglob("jensen_comparison.csv")):
            f.unlink(); print(f"  deleted {f}"); deleted += 1
    annual = Path("PPRAtlas/inputs/annual_regions.csv")
    if annual.exists():
        print(f"  {annual}: {migrate(annual, SUMMARY_DROP, SUMMARY_RENAME)}"); touched += 1
    print(f"\nmigrated {touched} files, deleted {deleted} jensen_comparison.csv")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Snapshot a sample file for independent verification**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
cp SeaAroundUsExtraction/global_output/tables/regions/LME_003/commercial.csv /tmp/before_commercial.csv 2>/dev/null \
  || cp SeaAroundUsExtraction/global_output/tables/regions/LME_003/commercial.csv "$TEMP/before_commercial.csv"
head -2 SeaAroundUsExtraction/global_output/tables/regions/LME_003/commercial.csv
```

- [ ] **Step 3: Run the migration**

Run: `python tools/migrate_group_columns.py`

Expected: each group file reports `15 -> 5 cols`, each summary reports `17 -> 15 cols`, and the `jensen_comparison.csv` files are deleted. Any `AssertionError` means a value changed — stop and investigate rather than continuing.

- [ ] **Step 4: Verify the migrated sample independently**

```bash
python - <<'PY'
import pandas as pd, os, pathlib
tmp = pathlib.Path(os.environ.get("TEMP", "/tmp"))
before = pd.read_csv(tmp / "before_commercial.csv", encoding="utf-8-sig")
after = pd.read_csv("SeaAroundUsExtraction/global_output/tables/regions/LME_003/commercial.csv", encoding="utf-8-sig")
print("after columns:", list(after.columns))
assert list(after.columns) == ["commercial_group", "catch_tonnes_matched", "tl_weighted", "sppr", "ppr"]
assert after["ppr"].equals(before["ppr_jensen"].rename("ppr")), "ppr must equal the old ppr_jensen"
assert after["sppr"].equals(before["sppr_jensen"].rename("sppr"))
assert after["tl_weighted"].equals(before["tl_weighted_jensen"].rename("tl_weighted"))
assert after["catch_tonnes_matched"].equals(before["catch_tonnes_matched"])
print("verified: every surviving value is byte-identical")
PY
```

- [ ] **Step 5: Confirm no `jensen_comparison.csv` survives and no stale column names remain**

```bash
find SeaAroundUsExtraction -name "jensen_comparison.csv" | head || echo "none (good)"
grep -rl "ppr_correct\|sppr_correct\|_jensen" --include="*.csv" SeaAroundUsExtraction PPRAtlas/inputs 2>/dev/null || echo "no stale columns (good)"
```

- [ ] **Step 6: Update the prose that describes the removed outputs**

`SeaAroundUsExtraction/global_output/README.md` and any `deliverable_manifest.json` still describe `jensen_comparison.csv`, the Jensen-violation count and the 22.93 % underestimate. Remove those sections and replace with a short statement that group PPR is the catch-weighted-mean-TL aggregation and is therefore Jensen-affected by design, and that the taxon-level sum in `species.csv` is the unbiased figure.

- [ ] **Step 7: Commit**

```bash
git add -A SeaAroundUsExtraction PPRAtlas/inputs tools
git commit -m "Migrate existing outputs to the trimmed schema

Group tables 15 -> 5 columns, summaries drop the _correct pair and rename the
_jensen pair. Every jensen_comparison.csv deleted. Migration asserts value
identity per column as it runs, so only whole columns disappear or change name -
no number moved.

README and manifest prose updated: group PPR is the catch-weighted-mean-TL
aggregation and Jensen-affected by design; species.csv carries the unbiased
taxon-level sum.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 10: Build the per-taxon-per-year distillation module

`standardize_catch` already returns exactly the taxon columns needed, for one year. Distillation reuses it per year, so a 2019 slice reproduces today's `species.csv` by construction.

**Files:**
- Create: `SeaAroundUsExtraction/src/ppr_pipeline/annual_catch.py`
- Create: `SeaAroundUsExtraction/tests/test_annual_catch.py`

**Interfaces:**
- Consumes: `ingest.read_catch_archive(path, year=None, required_only=False)` and `ingest.standardize_catch(raw, year, include_catch_types, include_reporting_status)`, which returns `(DataFrame, dict)` where the frame has columns `taxon, common_name, functional_group, commercial_group, catch_tonnes, landings_tonnes, discards_tonnes, reported_tonnes, unreported_tonnes`.
- Produces: `distill_archive(archive_path, unit_id, *, include_catch_types=("Landings","Discards"), include_reporting_status=("Reported","Unreported")) -> pd.DataFrame` with columns `["unit_id","year","taxon","common_name","functional_group","commercial_group","catch_tonnes","landings_tonnes","discards_tonnes","reported_tonnes","unreported_tonnes"]`, and `write_distilled(frame, out_path) -> Path`. Task 11 calls both.

- [ ] **Step 1: Probe three archives for realistic output sizes**

The spec's 50-150 MB estimate is unverified. Measure before committing to it.

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/SeaAroundUsExtraction"
python - <<'PY'
import sys, gzip, io
sys.path.insert(0, "src")
from pathlib import Path
import pandas as pd
from ppr_pipeline import ingest

for name in ("HS_018-catch.zip", "LME_003-catch.zip", "LME_026-catch.zip"):
    p = Path("raw_data/SAU_downloads") / name
    if not p.exists():
        print(f"{name}: missing"); continue
    raw = ingest.read_catch_archive(p, required_only=True)
    if raw.empty:
        print(f"{name:22s} empty archive"); continue
    years = sorted(pd.to_numeric(raw["year"], errors="coerce").dropna().astype(int).unique())
    frames = []
    for y in years:
        std, _ = ingest.standardize_catch(raw, year=y)
        if len(std):
            std.insert(0, "year", y)
            frames.append(std)
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(out.to_csv(index=False).encode("utf-8"))
    print(f"{name:22s} zip={p.stat().st_size/1e6:7.1f}MB  years={len(years):3d}  rows={len(out):7d}  csv.gz={len(buf.getvalue())/1e6:6.2f}MB")
PY
```

Record the numbers. Extrapolating by the number of archives gives the real total; if it greatly exceeds 150 MB, report it before Task 11 runs the full set.

- [ ] **Step 2: Write the failing tests**

```python
# save as SeaAroundUsExtraction/tests/test_annual_catch.py
from __future__ import annotations

import gzip
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from ppr_pipeline import annual_catch

RAW_HEADER = [
    "area_name", "area_type", "year", "scientific_name", "common_name",
    "functional_group", "commercial_group", "fishing_entity", "fishing_sector",
    "catch_type", "reporting_status", "gear_type", "end_use_type", "tonnes", "landed_value",
]


def _row(year: int, taxon: str, group: str, comm: str, entity: str,
         catch_type: str, status: str, tonnes: float) -> list:
    return [
        "California Current", "lme", year, taxon, f"{taxon} common",
        group, comm, entity, "Industrial", catch_type, status, "lines",
        "Direct human consumption", tonnes, tonnes * 100,
    ]


@pytest.fixture()
def archive(tmp_path: Path) -> Path:
    rows = [
        # 1950: one taxon split across two fishing entities - must sum to 3.0
        _row(1950, "Merluccius productus", "Medium benthopelagics", "Cod-likes", "USA", "Landings", "Reported", 1.0),
        _row(1950, "Merluccius productus", "Medium benthopelagics", "Cod-likes", "Canada", "Landings", "Reported", 2.0),
        # 1950: a discard, and an unreported landing
        _row(1950, "Merluccius productus", "Medium benthopelagics", "Cod-likes", "USA", "Discards", "Unreported", 0.5),
        # 1951: a different taxon
        _row(1951, "Engraulis mordax", "Small pelagics", "Anchovies", "USA", "Landings", "Reported", 7.0),
    ]
    csv = ",".join(RAW_HEADER) + "\n" + "\n".join(",".join(str(v) for v in r) for r in rows) + "\n"
    path = tmp_path / "LME_003-catch.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("LME_003-catch.csv", csv)
    return path


def test_distill_archive_returns_one_row_per_taxon_per_year(archive: Path) -> None:
    out = annual_catch.distill_archive(archive, "LME_003")

    assert list(out.columns) == [
        "unit_id", "year", "taxon", "common_name", "functional_group",
        "commercial_group", "catch_tonnes", "landings_tonnes",
        "discards_tonnes", "reported_tonnes", "unreported_tonnes",
    ]
    assert set(out["year"]) == {1950, 1951}
    assert len(out) == 2  # one taxon per year
    assert (out["unit_id"] == "LME_003").all()


def test_distill_archive_sums_over_fishing_entity(archive: Path) -> None:
    out = annual_catch.distill_archive(archive, "LME_003")
    row = out[(out["year"] == 1950)].iloc[0]

    # 1.0 + 2.0 landings + 0.5 discards
    assert row["catch_tonnes"] == pytest.approx(3.5)
    assert row["landings_tonnes"] == pytest.approx(3.0)
    assert row["discards_tonnes"] == pytest.approx(0.5)


def test_distill_archive_honours_the_catch_type_filter(archive: Path) -> None:
    out = annual_catch.distill_archive(archive, "LME_003", include_catch_types=("Landings",))
    row = out[(out["year"] == 1950)].iloc[0]

    assert row["catch_tonnes"] == pytest.approx(3.0)
    assert row["discards_tonnes"] == pytest.approx(0.0)


def test_distill_archive_returns_empty_frame_for_empty_archive(tmp_path: Path) -> None:
    path = tmp_path / "HS_999-catch.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("HS_999-catch.csv", "")

    out = annual_catch.distill_archive(path, "HS_999")
    assert out.empty
    assert list(out.columns)[:2] == ["unit_id", "year"]


def test_write_distilled_produces_a_readable_gzip(archive: Path, tmp_path: Path) -> None:
    frame = annual_catch.distill_archive(archive, "LME_003")
    out = annual_catch.write_distilled(frame, tmp_path / "LME_003.csv.gz")

    assert out.exists()
    with gzip.open(out, "rt", encoding="utf-8") as fh:
        reread = pd.read_csv(fh)
    assert len(reread) == len(frame)
    assert list(reread.columns) == list(frame.columns)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `cd SeaAroundUsExtraction && python -m pytest tests/test_annual_catch.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'ppr_pipeline.annual_catch'`.

- [ ] **Step 4: Write the module**

```python
# save as SeaAroundUsExtraction/src/ppr_pipeline/annual_catch.py
"""Distill a Sea Around Us catch archive to one row per taxon per year.

The processed tables elsewhere in this project cover a single analysis year. This
module produces the full 1950-2019 series, which is the only place per-taxon
per-year catch exists outside the raw archives.

It reuses :func:`ingest.standardize_catch` once per year rather than reimplementing
the filtering, so a distilled table sliced to the analysis year reproduces the
existing ``species.csv`` catch figures by construction.
"""
from __future__ import annotations

import gzip
from pathlib import Path
from typing import Iterable

import pandas as pd

from .ingest import read_catch_archive, standardize_catch

COLUMNS = [
    "unit_id",
    "year",
    "taxon",
    "common_name",
    "functional_group",
    "commercial_group",
    "catch_tonnes",
    "landings_tonnes",
    "discards_tonnes",
    "reported_tonnes",
    "unreported_tonnes",
]


def distill_archive(
    archive_path: str | Path,
    unit_id: str,
    *,
    include_catch_types: Iterable[str] = ("Landings", "Discards"),
    include_reporting_status: Iterable[str] = ("Reported", "Unreported"),
) -> pd.DataFrame:
    """Return one row per taxon per year for a single catch archive.

    Tonnage is summed over fishing entity, sector, gear and end-use, honouring the
    catch-type and reporting-status filters. An archive with no rows yields an empty
    frame carrying the full column set.
    """

    raw = read_catch_archive(archive_path, required_only=True)
    if raw.empty:
        return pd.DataFrame(columns=COLUMNS)

    years = sorted(pd.to_numeric(raw["year"], errors="coerce").dropna().astype(int).unique())
    frames: list[pd.DataFrame] = []
    for year in years:
        standardized, _audit = standardize_catch(
            raw,
            year=year,
            include_catch_types=include_catch_types,
            include_reporting_status=include_reporting_status,
        )
        if standardized.empty:
            continue
        standardized = standardized.copy()
        standardized.insert(0, "year", year)
        standardized.insert(0, "unit_id", unit_id)
        frames.append(standardized)

    if not frames:
        return pd.DataFrame(columns=COLUMNS)

    out = pd.concat(frames, ignore_index=True)
    missing = [c for c in COLUMNS if c not in out.columns]
    if missing:
        raise KeyError(f"standardize_catch did not supply: {missing}")
    return out[COLUMNS].sort_values(["year", "taxon"]).reset_index(drop=True)


def write_distilled(frame: pd.DataFrame, out_path: str | Path) -> Path:
    """Write a distilled frame as gzipped CSV and return the path."""

    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        frame.to_csv(handle, index=False)
    return path
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd SeaAroundUsExtraction && python -m pytest tests/test_annual_catch.py -q`
Expected: PASS.

- [ ] **Step 6: Prove the 2019 slice reproduces the existing `species.csv`**

This is the correctness gate for the whole task.

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/SeaAroundUsExtraction"
python - <<'PY'
import sys; sys.path.insert(0, "src")
from pathlib import Path
import pandas as pd
from ppr_pipeline import annual_catch

unit = "LME_003"
dist = annual_catch.distill_archive(Path(f"raw_data/SAU_downloads/{unit}-catch.zip"), unit)
slice_2019 = dist[dist["year"] == 2019].set_index("taxon")["catch_tonnes"].sort_index()

ref = pd.read_csv(f"global_output/tables/regions/{unit}/species.csv", encoding="utf-8-sig")
ref = ref.set_index("taxon")["catch_tonnes"].sort_index()

common = slice_2019.index.intersection(ref.index)
print(f"distilled 2019 taxa : {len(slice_2019)}")
print(f"species.csv taxa    : {len(ref)}")
print(f"common taxa         : {len(common)}")
print(f"only in distilled   : {sorted(set(slice_2019.index) - set(ref.index))[:5]}")
print(f"only in species.csv : {sorted(set(ref.index) - set(slice_2019.index))[:5]}")
diff = (slice_2019[common] - ref[common]).abs()
print(f"max abs catch diff  : {diff.max():.10f}")
assert len(slice_2019) == len(ref), "taxon count must match"
assert diff.max() < 1e-6, "catch tonnage must match"
print("GATE PASSED: the 2019 slice reproduces species.csv")
PY
```

Expected: `GATE PASSED`. If it fails, the distillation misreads the schema — fix before Task 11.

- [ ] **Step 7: Commit**

```bash
git add SeaAroundUsExtraction/src/ppr_pipeline/annual_catch.py SeaAroundUsExtraction/tests/test_annual_catch.py
git commit -m "Add per-taxon-per-year catch distillation

Per-taxon-per-year catch existed only inside the raw SAU archives; every processed
table covers a single analysis year. distill_archive reuses standardize_catch once
per year rather than reimplementing the filtering, so a distilled table sliced to
2019 reproduces the existing species.csv catch figures by construction - verified
against LME_003 as the correctness gate.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 11: Run distillation across every archive and commit the bulk data

**Files:**
- Create: `SeaAroundUsExtraction/tools/run_distillation.py`
- Create: `SeaAroundUsExtraction/data/catch_by_taxon_year/<unit_id>.csv.gz`

**Interfaces:**
- Consumes: `annual_catch.distill_archive` and `annual_catch.write_distilled` from Task 10.
- Produces: one gzipped table per unit. Task C (deferred) will absorb or reference these.

- [ ] **Step 1: Write the batch runner**

```python
# save as SeaAroundUsExtraction/tools/run_distillation.py
"""Distill every Sea Around Us catch archive to per-taxon-per-year tables."""
from __future__ import annotations

import sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ppr_pipeline import annual_catch  # noqa: E402

RAW = ROOT / "raw_data" / "SAU_downloads"
OUT = ROOT / "data" / "catch_by_taxon_year"


def main() -> int:
    archives = sorted(RAW.glob("*-catch.zip"))
    if not archives:
        print(f"no archives under {RAW}"); return 1
    OUT.mkdir(parents=True, exist_ok=True)
    total_bytes = written = empty = 0
    started = time.time()
    for i, archive in enumerate(archives, 1):
        unit_id = archive.name.replace("-catch.zip", "")
        frame = annual_catch.distill_archive(archive, unit_id)
        if frame.empty:
            empty += 1
            print(f"[{i}/{len(archives)}] {unit_id:12s} empty archive, skipped")
            continue
        path = annual_catch.write_distilled(frame, OUT / f"{unit_id}.csv.gz")
        size = path.stat().st_size
        total_bytes += size
        written += 1
        print(f"[{i}/{len(archives)}] {unit_id:12s} rows={len(frame):7d} "
              f"years={frame['year'].nunique():3d} {size/1e6:6.2f}MB")
    print(f"\nwrote {written} tables ({empty} empty archives skipped) "
          f"totalling {total_bytes/1e6:.1f} MB in {time.time()-started:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run the distillation**

Run: `cd SeaAroundUsExtraction && python tools/run_distillation.py`

This processes 739 archives and will take a while. Record the reported total size.

- [ ] **Step 3: Sanity-check the output**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/SeaAroundUsExtraction"
echo -n "tables written: " && ls data/catch_by_taxon_year | wc -l
du -sh data/catch_by_taxon_year
python - <<'PY'
import gzip, pandas as pd, random
from pathlib import Path
files = sorted(Path("data/catch_by_taxon_year").glob("*.csv.gz"))
for f in random.sample(files, min(3, len(files))):
    with gzip.open(f, "rt", encoding="utf-8") as fh:
        df = pd.read_csv(fh)
    assert list(df.columns)[:2] == ["unit_id", "year"]
    assert df["catch_tonnes"].ge(0).all(), f"{f}: negative catch"
    print(f"{f.name:20s} rows={len(df):7d} years {df['year'].min()}-{df['year'].max()} taxa={df['taxon'].nunique()}")
print("spot checks passed")
PY
```

- [ ] **Step 4: Add the bulk data directories held back in Task 1**

Now that deletions have shrunk the tree, add everything.

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
git add -A
git status --short | wc -l
du -sh .git
```

- [ ] **Step 5: Verify nothing important is still unstaged**

```bash
git status --porcelain --ignored=matching | grep "^!!" | awk '{print $2}' | head -20
```

Review the list. Only `.venv/`, `.idea/`, `.vscode/`, `__pycache__/`, `.pytest_cache/` and Excel lock files should appear. Anything else means `.gitignore` needs another fix.

- [ ] **Step 6: Commit**

```bash
git commit -m "Distill per-taxon-per-year catch and commit the bulk data

739 archives distilled to one gzipped table per unit under
SeaAroundUsExtraction/data/catch_by_taxon_year/. This is the only per-taxon
per-year catch series in the project; every other processed table covers a single
analysis year.

Also adds the bulk directories held back from the safety-net commit: the raw SAU
archives and the PPRAtlas source archive. A cloner now receives all catch data.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 12: Package the species-to-group mapper skill

**Files:**
- Rename: `skills/artifact-template-ewe-species-to-group-mapper/` → `skills/ewe-species-to-group-mapper/`
- Rename: `skills/ewe-species-to-group-mapper/example outputs/` → `skills/ewe-species-to-group-mapper/examples/`
- Modify: `skills/ewe-species-to-group-mapper/SKILL.md`
- Create: `skills/ewe-species-to-group-mapper.skill`

**Interfaces:**
- Consumes: nothing.
- Produces: an installable `.skill` zip matching the convention of `ecopath-extraction-claude.skill` — a single top-level directory containing `SKILL.md`.

- [ ] **Step 1: Confirm the target format**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/skills"
unzip -l ecopath-extraction-claude.skill | head -8
```

Expected: entries under a single top-level directory, `ecopath-extraction/SKILL.md` first.

- [ ] **Step 2: Rename the directory and the examples folder**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/skills"
git mv "artifact-template-ewe-species-to-group-mapper" "ewe-species-to-group-mapper" \
  2>/dev/null || mv "artifact-template-ewe-species-to-group-mapper" "ewe-species-to-group-mapper"
cd ewe-species-to-group-mapper
git mv "example outputs" "examples" 2>/dev/null || mv "example outputs" "examples"
ls -la
```

- [ ] **Step 3: Rename the skill in the frontmatter**

Edit `skills/ewe-species-to-group-mapper/SKILL.md`. Change line 2 from:

```yaml
name: artifact-template-ewe-species-to-group-mapper
```

to:

```yaml
name: ewe-species-to-group-mapper
```

Leave the `description` unchanged — it already names the trigger conditions correctly.

- [ ] **Step 4: Make the examples discoverable from `SKILL.md`**

`SKILL.md` currently references `assets/reference.xlsx` but never mentions the worked examples. Under the `## Required inputs` section, add:

```markdown
## Worked examples

`examples/` holds three completed mappings — `LME_032_Arabian_Sea.xlsx`,
`LME_034_Bay_of_Bengal.xlsx` and `LME_047_East_China_Sea.xlsx`. Read one before
starting to see the expected column layout, confidence colouring and provenance
sheet. They are reference output, not biological lookup tables: never copy an
assignment from one ecosystem into another without evidence from that ecosystem's
own sources.
```

- [ ] **Step 5: Build the `.skill` zip**

Exclude the artifact-template and OpenAI scaffolding, which a Claude skill never reads. Both stay in the repository for the later GPT adaptation.

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/skills"
rm -f ewe-species-to-group-mapper.skill
zip -r ewe-species-to-group-mapper.skill ewe-species-to-group-mapper \
  -x "ewe-species-to-group-mapper/artifact-template.json" \
  -x "ewe-species-to-group-mapper/agents/*" \
  -x "*/__pycache__/*" -x "*/.DS_Store" -x "*~\$*"
unzip -l ewe-species-to-group-mapper.skill
```

- [ ] **Step 6: Verify the bundle**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/skills"
python - <<'PY'
import zipfile
z = zipfile.ZipFile("ewe-species-to-group-mapper.skill")
names = z.namelist()
tops = {n.split("/")[0] for n in names}
assert tops == {"ewe-species-to-group-mapper"}, f"expected one top-level dir, got {tops}"
assert "ewe-species-to-group-mapper/SKILL.md" in names, "SKILL.md missing"
assert not [n for n in names if "artifact-template.json" in n], "scaffolding leaked in"
assert not [n for n in names if "/agents/" in n], "openai.yaml leaked in"
assert [n for n in names if n.startswith("ewe-species-to-group-mapper/examples/")], "examples missing"
assert [n for n in names if n.startswith("ewe-species-to-group-mapper/assets/")], "assets missing"
head = z.read("ewe-species-to-group-mapper/SKILL.md").decode("utf-8")[:200]
assert "name: ewe-species-to-group-mapper" in head, "frontmatter name not updated"
print(f"bundle valid: {len(names)} entries")
for n in sorted(names)[:12]: print("   ", n)
PY
```

Expected: `bundle valid`.

- [ ] **Step 7: Commit**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
git add -A skills
git commit -m "Package the EwE species-to-group mapper as an installable skill

Renamed from artifact-template-ewe-species-to-group-mapper: the prefix described
the distribution format it arrived in, not what the skill does. 'example outputs'
becomes 'examples' so the path can be referenced from SKILL.md without a space,
and SKILL.md now points at the three worked mappings.

The zip excludes artifact-template.json and agents/openai.yaml, which a Claude
skill never reads. Both remain in the repository for the later GPT adaptation.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 13: Document the pipeline

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: the final structure from Tasks 2, 3, 4, 9, 11, 12.
- Produces: the root README. Task 14 graphs the repository including it.

- [ ] **Step 1: Verify every figure before writing it down**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
echo -n "archived regions      : " && ls PPRAtlas/archive/regions | wc -l
echo -n "NPP rows              : " && expr $(wc -l < NPPExtraction/NPP_2019_filled_SAU_regions.csv) - 1
echo -n "global cover models   : " && ls PPREstimation/real_models/global_cover_jsons | wc -l
echo -n "SPPR workbooks (top10): " && ls PPREstimation/output/top10 | wc -l
echo -n "EwE model JSONs       : " && ls PPREstimation/real_models/EwE_jsons | wc -l
echo -n "distilled catch tables: " && ls SeaAroundUsExtraction/data/catch_by_taxon_year | wc -l
echo -n "raw SAU archives      : " && ls SeaAroundUsExtraction/raw_data/SAU_downloads | wc -l
```

Use the printed numbers in the README rather than the ones in this plan.

- [ ] **Step 2: Write the root README**

Replace `README.md` with the following, substituting the verified counts from Step 1 wherever a number appears:

```markdown
# GlobalPPREstimation

Estimating the primary production required (PPR) to sustain global marine fisheries,
ecosystem by ecosystem.

## The pipeline

    1. sweep          find published Ecopath models for each ecosystem
    2. archive        store the article, supplements and provenance   -> PPRAtlas/archive/regions/<unit_id>/
    3. extract        pull model parameters out of the paper          -> skills/ecopath-extraction-*.skill
    4. estimate       compute SPPR per group by several methods       -> PPREstimation/
    5. integrate      join SPPR with catch and NPP data               -> (in design)
    6. map            render the result on one interactive map        -> PPRAtlas/index.html

Ecosystems are keyed by `unit_id` throughout: `LME_003`, `EEZ_711`, `HS_018`.

## Sub-projects

| Directory | Role | Key inputs | Key outputs |
| --- | --- | --- | --- |
| `SeaAroundUsExtraction/` | Fishing-catch and spatial-unit extraction from Sea Around Us, plus a first-pass PPR ranking | `raw_data/SAU_downloads/*.zip` | `global_output/`, `eez_output/`, `data/catch_by_taxon_year/` |
| `PPRAtlas/` | Curated archive of source articles per ecosystem, and the interactive map | `archive/regions/`, `data/catalog.json` | `index.html`, `archive/index.html` |
| `PPREstimation/` | The main algorithm: Ecopath model loading, automatic balancing, SPPR estimation by several methods | `real_models/*.json` | `output/` — one workbook per model |
| `NPPExtraction/` | Net primary production per region, five satellite models | — | `NPP_2019_filled_SAU_regions.csv` |
| `skills/` | Packaged skills: parameter extraction from papers, taxon-to-group mapping | source papers, catch workbooks | model JSON, mapping workbooks |

## Coverage

This is the honest state of the work, not a target.

| Asset | Coverage |
| --- | --- |
| Ecosystems with an archived source article | <verified count> |
| Regions with an NPP value | <verified count> |
| Ecosystems with an extracted model and SPPR workbook | <verified count> |

The modelled set is a pilot: the top ten ecosystems by the 1995 PPR ranking, which
yielded more models than ecosystems because several ecosystems have more than one
published model.

## How PPR is calculated, and the two different meanings of "Jensen"

Two calculations in this repository share a name and are easy to confuse.

**SeaAroundUsExtraction — a first-pass estimate.** Specific PPR is `(1/TE)^(TL-1)`,
which at the configured `TE = 0.1` is `10^(TL-1)`. It is applied at three levels:

- **per taxon**, using that taxon's own trophic level. This is the unbiased figure,
  in `global_output/tables/regions/<unit_id>/species.csv`.
- **per commercial group** and **per functional group**, using the group's
  catch-weighted mean trophic level, in `commercial.csv` and `functional.csv`.

The group figures are **deliberately Jensen-affected**. Because `10^(TL-1)` is convex,
exponentiating a mean trophic level understates the sum of the individual taxa
whenever a group spans more than one level. That gap is kept on purpose: it measures
what is lost by moving from taxa to groups, and an Ecopath model cannot show it
because Ecopath has no taxon level. The corrected value is not stored — it is exactly
the taxon sum within the group, recoverable with a `groupby`.

**PPREstimation — the real method.** `monte_carlo_SPPR` applies a genuine
**Jensen's-inequality correction**, resampling transfer efficiency and averaging,
because `SPPR` is convex in `1/TE` and solving once at the mean underestimates the
expectation. This is unrelated to the SeaAroundUs comparison above and is documented
in `PPREstimation/information/SPPR_Methods.md`.

## Data

Everything needed to reproduce the analysis is committed, including the raw
Sea Around Us catch archives and the curated article archive. Clones are large.

`SeaAroundUsExtraction/data/catch_by_taxon_year/<unit_id>.csv.gz` holds catch per
taxon per year, 1950-2019. Every other processed table covers a single analysis year.

## Not yet built

- **The per-ecosystem data spine** — one directory per ecosystem gathering catch,
  geography, articles, the selected model, SPPR results and NPP.
- **The per-ecosystem workbook** — a single lean spreadsheet per ecosystem: catch per
  taxon per year, taxon SPPR by method, PPR, NPP, and a PPR/NPP summary.

Both are designed in `docs/superpowers/specs/`. Output locations named above are
staging locations until that spine exists.
```

- [ ] **Step 3: Verify the README's claims against reality**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
for p in PPRAtlas/archive/regions PPRAtlas/index.html PPREstimation/output \
         PPREstimation/information/SPPR_Methods.md NPPExtraction/NPP_2019_filled_SAU_regions.csv \
         SeaAroundUsExtraction/data/catch_by_taxon_year SeaAroundUsExtraction/global_output \
         SeaAroundUsExtraction/eez_output skills; do
  test -e "$p" && echo "ok   $p" || echo "FAIL missing: $p"
done
```

Expected: every line `ok`. Any `FAIL` means the README describes something that does not exist — fix the README, not the check.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "Document the pipeline and the two meanings of Jensen

States the sweep -> archive -> extract -> estimate -> integrate -> map flow, each
sub-project's role and its inputs and outputs, and the honest coverage numbers.

Distinguishes the two calculations that share the name Jensen: the SeaAroundUs
group aggregation, which is deliberately Jensen-affected so the taxon-to-group cost
stays visible, and PPREstimation's monte_carlo_SPPR, which applies the genuine
Jensen's-inequality correction. Confusing these would be easy and consequential.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 14: Build the repository-wide knowledge graph

**Files:**
- Create: `graphify-out/`

**Interfaces:**
- Consumes: the cleaned repository from Tasks 1-13.
- Produces: `graphify-out/graph.json`, `graphify-out/graph.html`, `graphify-out/GRAPH_REPORT.md`.

- [ ] **Step 1: Confirm the tree is clean before graphing**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
git status --short | head
test ! -d FishEstimationAI && echo "ok  rename complete"
test ! -d SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04 && echo "ok  promotion complete"
test ! -d FishEstimationAI/graphify-out && echo "ok  stale graph gone"
```

Expected: a clean working tree and three `ok` lines. Graphing a half-restructured tree produces a graph of the mess.

- [ ] **Step 2: Run the graphify skill**

Invoke the `graphify` skill over the repository root, with output to `graphify-out/`. Follow the skill's own instructions; do not hand-roll a graph.

- [ ] **Step 3: Verify the graph covers all five sub-projects**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
python - <<'PY'
import json, pathlib
p = pathlib.Path("graphify-out/graph.json")
assert p.exists(), "graph.json missing"
blob = p.read_text(encoding="utf-8")
for name in ("SeaAroundUsExtraction", "PPRAtlas", "PPREstimation", "NPPExtraction", "skills"):
    print(f"  {'ok  ' if name in blob else 'MISS'} {name}")
g = json.loads(blob)
print("nodes:", len(g.get("nodes", [])), " edges:", len(g.get("edges", g.get("links", []))))
PY
```

Expected: all five present. `FishEstimationAI` should not appear except in historical docs.

- [ ] **Step 4: Commit**

```bash
git add -A graphify-out
git commit -m "Build the repository-wide knowledge graph

Replaces the per-project graph that lived under FishEstimationAI, which covered one
sub-project and predated the restructure. Built after the promotion, deletions,
rename and documentation so it reflects the unified tree.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 15: Final verification, then push on confirmation

**Files:**
- Create: `docs/superpowers/final-verification.txt`

**Interfaces:**
- Consumes: everything.
- Produces: a verification record, and a pushed `main` only after the user says so.

- [ ] **Step 1: Run all three test suites and compare against the baseline**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
{
  echo "=== final verification ==="
  echo "--- SeaAroundUsExtraction ---"
  (cd SeaAroundUsExtraction && python -m pytest tests -q 2>&1 | tail -20)
  echo "--- PPRAtlas ---"
  (cd PPRAtlas && python -m pytest tests -q 2>&1 | tail -20)
  echo "--- PPREstimation ---"
  (cd PPREstimation && python -m pytest tests -q 2>&1 | tail -20)
} > docs/superpowers/final-verification.txt
diff docs/superpowers/baseline-tests.txt docs/superpowers/final-verification.txt || true
cat docs/superpowers/final-verification.txt
```

Any suite that passed at baseline must still pass. Report honestly if one does not — do not claim success.

- [ ] **Step 2: Confirm the structural invariants**

```bash
cd "C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation"
echo "--- must NOT exist ---"
for p in FishEstimationAI SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04 \
         SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04_complete.zip \
         SeaAroundUsExtraction/Global_history_TE010_2026-09-04 \
         SeaAroundUsExtraction/PPR_global_te005_results \
         PPRAtlas/archive/regions.zip PPREstimation/.git; do
  test ! -e "$p" && echo "ok   gone: $p" || echo "FAIL still present: $p"
done
echo "--- must exist ---"
for p in PPREstimation PPRAtlas/archive/files PPRAtlas/archive/regions \
         SeaAroundUsExtraction/raw_data/SAU_downloads \
         SeaAroundUsExtraction/data/catch_by_taxon_year \
         skills/ewe-species-to-group-mapper.skill graphify-out README.md; do
  test -e "$p" && echo "ok   present: $p" || echo "FAIL missing: $p"
done
echo "--- no jensen columns survive in SAU/PPRAtlas data ---"
grep -rl "_jensen\|ppr_correct\|sppr_correct" --include="*.csv" SeaAroundUsExtraction PPRAtlas/inputs 2>/dev/null \
  || echo "ok   none"
echo "--- PPREstimation Jensen intact ---"
grep -c -i jensen PPREstimation/information/SPPR_Methods.md
```

- [ ] **Step 3: Report the size change**

```bash
du -sh .git
du -sh SeaAroundUsExtraction PPRAtlas PPREstimation NPPExtraction skills graphify-out
git count-objects -vH | grep size-pack
```

- [ ] **Step 4: Commit the verification record**

```bash
git add docs/superpowers/final-verification.txt
git commit -m "Record final verification results

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

- [ ] **Step 5: Show the user what will be pushed, and ask**

Do **not** push yet. Show:

```bash
git log --oneline 6ca29af..HEAD
git count-objects -vH | grep size-pack
```

Then ask the user to confirm the push to `origin main`, noting the pack size so they know what the upload involves.

- [ ] **Step 6: Push, only after an explicit yes**

```bash
git push -u origin main
```

If the user declines, stop here and leave the commits local.

---

## Self-Review

**Spec coverage.** A1 → Task 2. A2, A3 → Task 3. A4 (keep both archive stores, keep raw_data) → Global Constraints, verified in Task 15. A5 rename → Task 4. A6 nested git → Task 4. A7 gitignore → Task 1. B calculations → Task 5. B validation → Task 6. B pipeline → Task 7. B notebook → Task 8. B data migration → Task 9. D probe/module/gate → Task 10. D full run → Task 11. F → Task 14. G → Task 13. H → Task 12. Verification and commit discipline → Task 15. No spec section is unimplemented.

**Placeholder scan.** No `TBD`/`TODO`. Two deliberate placeholders remain and are both explicitly resolved by a preceding step: the `<verified count>` markers in the Task 13 README template, filled from Task 13 Step 1; and the `strip` argument in Task 3 Step 2, determined by inspecting each zip's entries in the same step. Task 8 was rewritten after reading `notebook.py`: there are **two** builders (`build_validation_notebook`, `build_scope_validation_notebook`), both carrying the section, and the existing test asserted `"Jensen" in text`, so it had to be updated rather than extended. Exact line numbers are given.

**Type consistency.** `aggregate_groups` returns `[group_column, "catch_tonnes_matched", "tl_weighted", "sppr", "ppr"]` in Task 5; Task 6 `_sum_ppr` reads `ppr`; Task 7 sums `commercial["ppr"]`; Task 9 renames `ppr_jensen` → `ppr`. Consistent. `distill_archive` and `write_distilled` are defined in Task 10 with the exact signatures Task 11 calls. `COLUMNS` in Task 10 matches the assertion in Task 10's first test and the spec's column list.
