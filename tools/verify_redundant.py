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
    ok = checked > 0 and not missing and not mismatched
    print("   VERDICT:", "REDUNDANT - safe to delete" if ok else "NOT REDUNDANT - keep")
    return ok

if __name__ == "__main__":
    strip = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    sys.exit(0 if verify(sys.argv[1], sys.argv[2], strip) else 1)
