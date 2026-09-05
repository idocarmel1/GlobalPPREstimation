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
