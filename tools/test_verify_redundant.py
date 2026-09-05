"""Tests for tools/verify_redundant.py.

Covers the three cases the content-hash fallback must distinguish:
  1. an entry matched in place (same path, same size)
  2. an entry relocated on disk (different path, byte-identical content)
  3. an entry whose content is genuinely absent anywhere under the target directory

All fixtures are tiny zips and directories built under pytest's tmp_path -- the real
archives under PPRAtlas/ and SeaAroundUsExtraction/ are never touched.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_redundant import verify  # noqa: E402


def _make_zip(zpath: Path, entries: dict) -> None:
    with zipfile.ZipFile(zpath, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)


def test_matched_in_place(tmp_path, capsys):
    zpath = tmp_path / "a.zip"
    _make_zip(zpath, {"wrap/keep.txt": b"hello world"})
    target = tmp_path / "disk"
    target.mkdir()
    (target / "keep.txt").write_bytes(b"hello world")

    ok = verify(str(zpath), str(target), strip=1)

    assert ok is True
    out = capsys.readouterr().out
    assert "REDUNDANT - safe to delete" in out
    assert "NOT REDUNDANT" not in out
    # no relocation needed when the path matches directly
    assert "relocated (same content, different path) : 0" in out


def test_relocated_with_identical_content(tmp_path, capsys):
    zpath = tmp_path / "b.zip"
    payload = b"unique-bytes-xyz"
    _make_zip(zpath, {"wrap/old_name.txt": payload})
    target = tmp_path / "disk"
    (target / "subdir").mkdir(parents=True)
    # nothing at the expected path "old_name.txt" -- the file was renamed on disk
    (target / "subdir" / "new_name.txt").write_bytes(payload)

    ok = verify(str(zpath), str(target), strip=1)

    assert ok is True
    out = capsys.readouterr().out
    assert "REDUNDANT - safe to delete" in out
    assert "NOT REDUNDANT" not in out
    assert "relocated (same content, different path) : 1" in out
    assert "old_name.txt" in out
    assert "new_name.txt" in out
    assert "->" in out


def test_genuinely_absent_content(tmp_path, capsys):
    zpath = tmp_path / "c.zip"
    _make_zip(zpath, {"wrap/gone.txt": b"nowhere-to-be-found"})
    target = tmp_path / "disk"
    (target / "other").mkdir(parents=True)
    (target / "other" / "unrelated.txt").write_bytes(b"totally different content")

    ok = verify(str(zpath), str(target), strip=1)

    assert ok is False
    out = capsys.readouterr().out
    assert "NOT REDUNDANT - keep" in out
    assert "gone.txt" in out
    assert "relocated (same content, different path) : 0" in out
