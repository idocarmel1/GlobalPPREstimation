# save as tools/verify_redundant.py
"""Prove a zip's contents already exist on disk before the zip is deleted.

An entry counts as proven-on-disk in either of two ways:
  - matched-in-place: a file exists at the entry's (stripped) path with the same size.
  - relocated: no file exists at that path, but some file elsewhere under the target
    directory has byte-identical content (same SHA-256). This happens when a file was
    renamed/moved on disk after the zip was created.

The on-disk hash index used for the relocation fallback is built lazily -- only once at
least one entry fails the in-place check -- so the common all-matched case never pays the
cost of hashing a large target tree.
"""
from __future__ import annotations
import hashlib
import sys, zipfile
from pathlib import Path

_HASH_CHUNK = 1 << 20  # 1 MiB


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_HASH_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def _build_hash_index(directory: Path) -> dict[str, Path]:
    """Map sha256 -> a file on disk under `directory` with that content.

    First file found wins for a given hash; that is sufficient here since we only need
    to prove *some* on-disk copy exists, not enumerate every duplicate.
    """
    index: dict[str, Path] = {}
    for p in directory.rglob("*"):
        if not p.is_file():
            continue
        try:
            digest = _sha256_file(p)
        except OSError:
            continue
        index.setdefault(digest, p)
    return index


def verify(archive: str, directory: str, strip: int = 1) -> bool:
    zpath, dpath = Path(archive), Path(directory)
    if not zpath.exists():
        print(f"SKIP  {zpath} does not exist"); return True
    if not dpath.exists():
        print(f"FAIL  {zpath}: directory {dpath} does not exist"); return False

    missing, mismatched, relocated, checked = [], [], [], 0
    unresolved: list[tuple] = []  # (info,) entries that failed the in-place check

    with zipfile.ZipFile(zpath) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            parts = Path(info.filename).parts[strip:]
            if not parts:
                continue
            checked += 1
            on_disk = dpath.joinpath(*parts)
            if not on_disk.exists():
                unresolved.append(info)
            elif on_disk.stat().st_size != info.file_size:
                mismatched.append((info.filename, info.file_size, on_disk.stat().st_size))

        hash_index: dict[str, Path] | None = None
        for info in unresolved:
            if hash_index is None:
                hash_index = _build_hash_index(dpath)
            digest = hashlib.sha256(zf.read(info)).hexdigest()
            found = hash_index.get(digest)
            if found is None:
                missing.append(info.filename)
            else:
                relocated.append((info.filename, str(found.relative_to(dpath))))

    print(f"{zpath.name}: checked {checked} entries against {dpath}")
    print(f"   missing on disk : {len(missing)}   {missing[:5]}")
    print(f"   size mismatches : {len(mismatched)}   {mismatched[:5]}")
    print(f"   relocated (same content, different path) : {len(relocated)}")
    for zip_name, disk_rel in relocated:
        print(f"      {zip_name}  ->  {disk_rel}")
    ok = checked > 0 and not missing and not mismatched
    print("   VERDICT:", "REDUNDANT - safe to delete" if ok else "NOT REDUNDANT - keep")
    return ok

if __name__ == "__main__":
    strip = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    sys.exit(0 if verify(sys.argv[1], sys.argv[2], strip) else 1)
