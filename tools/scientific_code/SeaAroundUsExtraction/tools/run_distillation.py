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
