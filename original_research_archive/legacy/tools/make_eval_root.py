"""Carve a minimal GlobalPPREstimation root holding one ecosystem, for A/B skill runs.

Two skills cannot be compared on the same ecosystem in the same checkout: whichever runs
second sees the first one's answers sitting in `data/<unit>/mapping/` and is no longer
running blind. Copying the whole repository to avoid that would cost gigabytes. This copies
only what a mapping run reads -- one catch archive, one or two model workbooks, that
ecosystem's papers, and the two index files -- which comes to a few megabytes.

The mapping scripts locate their checkout through `GLOBALPPR_ROOT`, so an agent pointed at
the result works normally and cannot see the other arm.

    python tools/make_eval_root.py LME_028 <dest>
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "claude" / "ewe-species-to-group-mapper" / "scripts"))
import mapping_io as mio  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("unit")
    ap.add_argument("dest", type=Path)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    dest = a.dest.resolve()
    if dest.exists():
        if not a.force:
            raise SystemExit(f"{dest} exists; pass --force to replace it")
        shutil.rmtree(dest)

    copied, missing = [], []

    def take(rel: str, *, optional=False):
        src = ROOT / rel
        if not src.exists():
            (copied if optional else missing).append(f"(absent) {rel}")
            return
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, out, dirs_exist_ok=True)
        else:
            shutil.copy2(src, out)
        copied.append(rel)

    take(f"SeaAroundUsExtraction/data/catch_by_taxon_year/{a.unit}.csv.gz")
    for base in ("global_output", "eez_output"):
        p = f"SeaAroundUsExtraction/{base}/tables/regions/{a.unit}/species.csv"
        if (ROOT / p).exists():
            take(p)
    for book in mio.model_workbooks(ROOT, a.unit):
        take(f"PPREstimation/output/top10/{book.name}")
    take(f"PPRAtlas/archive/regions/{a.unit}", optional=True)
    take("PPRAtlas/data/regions.csv", optional=True)
    take("data/INDEX.csv")
    take("data/model_selection.xlsx")
    take("skills/claude/ewe-species-to-group-mapper")
    take("skills/claude/ecopath-paper-to-ppr")
    take("skills/codex/ewe-species-to-group-mapper")
    take("skills/codex/ecopath-paper-to-ppr")

    if missing:
        raise SystemExit("cannot build an eval root, these are required:\n  "
                         + "\n  ".join(missing))

    (dest / "data" / a.unit).mkdir(parents=True, exist_ok=True)
    size = sum(p.stat().st_size for p in dest.rglob("*") if p.is_file())
    print(f"eval root for {a.unit} at {dest}")
    print(f"  {sum(1 for p in dest.rglob('*') if p.is_file())} files, {size / 1e6:.1f} MB")
    print("  point an agent at it with GLOBALPPR_ROOT")
    for c in copied:
        print(f"    {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
