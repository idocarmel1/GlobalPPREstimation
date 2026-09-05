# save as tools/verify_redundant.py
"""Prove a zip's contents already exist on disk before the zip is deleted.

Every entry is classified into exactly one of:
  - matched          : found at its expected (stripped) path, content identical (SHA-256).
  - relocated        : not found at its expected path, but some file elsewhere under the
                        target directory has byte-identical content -- it was renamed/moved
                        on disk after the zip was created.
  - size-mismatch    : found at its expected path, but a different size (a definitive
                        failure -- no hash is needed to know the content differs).
  - content-mismatch : found at its expected path, same size, but different bytes.
  - absent           : not found at its expected path, and no file anywhere under the
                        target directory matches its content.

A zip is REDUNDANT only when every entry is `matched` or `relocated`. Content is always
verified by streamed SHA-256 (never a whole file read into memory), and a size check
happens first wherever possible so a definitive size mismatch never pays for a hash.

The on-disk hash index used for the relocation fallback is built lazily -- only once at
least one entry is unresolved (not found at its expected path) -- so the common
all-matched-in-place case never pays to hash the whole target tree a second time.
"""
from __future__ import annotations
import hashlib
import sys, zipfile
from pathlib import Path

_HASH_CHUNK = 1 << 20  # 1 MiB


def _sha256_stream(fobj) -> str:
    h = hashlib.sha256()
    for chunk in iter(lambda: fobj.read(_HASH_CHUNK), b""):
        h.update(chunk)
    return h.hexdigest()


def _sha256_file(path: Path) -> str:
    with open(path, "rb") as f:
        return _sha256_stream(f)


def _sha256_zip_entry(zf: zipfile.ZipFile, info: zipfile.ZipInfo) -> str:
    with zf.open(info) as f:
        return _sha256_stream(f)


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

    matched: list[str] = []
    relocated: list[tuple[str, str]] = []
    size_mismatch: list[tuple[str, int, int]] = []
    content_mismatch: list[str] = []
    absent: list[str] = []
    checked = 0
    unresolved: list[zipfile.ZipInfo] = []  # not found at their expected path

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
                continue
            disk_size = on_disk.stat().st_size
            if disk_size != info.file_size:
                # Definitive failure -- sizes differ, so no hash is needed.
                size_mismatch.append((info.filename, info.file_size, disk_size))
                continue
            # Same path, same size -- only now is a hash comparison worth paying for.
            if _sha256_zip_entry(zf, info) == _sha256_file(on_disk):
                matched.append(info.filename)
            else:
                content_mismatch.append(info.filename)

        hash_index: dict[str, Path] | None = None
        for info in unresolved:
            if hash_index is None:
                hash_index = _build_hash_index(dpath)
            digest = _sha256_zip_entry(zf, info)
            found = hash_index.get(digest)
            if found is None:
                absent.append(info.filename)
            else:
                relocated.append((info.filename, str(found.relative_to(dpath))))

    print(f"{zpath.name}: checked {checked} entries against {dpath}")
    print(f"   matched (in place, content identical)               : {len(matched)}")
    print(f"   relocated (elsewhere, content identical)            : {len(relocated)}")
    for zip_name, disk_rel in relocated:
        print(f"      {zip_name}  ->  {disk_rel}")
    print(f"   size-mismatch (same path, different size)           : {len(size_mismatch)}")
    for zip_name, zsize, dsize in size_mismatch:
        print(f"      {zip_name}  (zip {zsize} bytes, disk {dsize} bytes)")
    print(f"   content-mismatch (same path/size, different bytes) : {len(content_mismatch)}")
    for zip_name in content_mismatch:
        print(f"      {zip_name}")
    print(f"   absent (no matching content anywhere)                : {len(absent)}")
    for zip_name in absent:
        print(f"      {zip_name}")

    ok = checked > 0 and not size_mismatch and not content_mismatch and not absent
    print("   VERDICT:", "REDUNDANT - safe to delete" if ok else "NOT REDUNDANT - keep")
    return ok

if __name__ == "__main__":
    strip = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    sys.exit(0 if verify(sys.argv[1], sys.argv[2], strip) else 1)
