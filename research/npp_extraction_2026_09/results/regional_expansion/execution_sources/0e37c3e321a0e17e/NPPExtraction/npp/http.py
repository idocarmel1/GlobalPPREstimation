"""Minimal HTTP helpers: JSON, text and resumable file download with retries.

Deliberately built on ``urllib`` so the package has no hard dependency on ``requests``.
Everything honours the standard ``HTTPS_PROXY`` / ``NO_PROXY`` environment variables.
"""

from __future__ import annotations

import json
import time
import ssl
import urllib.error
import urllib.request
from pathlib import Path

from .log import log

USER_AGENT = "ppr-npp/1.0 (research pipeline; contact via repository)"


def _open(url: str, timeout: int, headers: dict | None = None):
    import certifi
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=certifi.where())
    return urllib.request.urlopen(req, timeout=timeout, context=context)


def get_bytes(url: str, timeout: int = 180, retries: int = 4) -> bytes:
    last = None
    for attempt in range(retries):
        try:
            with _open(url, timeout) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
            wait = 2 ** attempt
            log(f"http: {url} failed ({exc}); retry {attempt+1}/{retries} in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"GET {url} failed after {retries} attempts: {last}")


def get_text(url: str, timeout: int = 180, retries: int = 4) -> str:
    return get_bytes(url, timeout, retries).decode("utf-8", errors="replace")


def get_json(url: str, timeout: int = 180, retries: int = 4):
    return json.loads(get_text(url, timeout, retries))


def download(url: str, dest: Path, timeout: int = 180, retries: int = 4, overwrite: bool = False) -> Path:
    """Download to ``dest``, skipping the transfer if the file is already there.

    Writes to a ``.part`` file and renames on success, so an interrupted run never leaves
    a truncated file that a later run would mistake for complete.
    """
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0 and not overwrite:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    last = None
    for attempt in range(retries):
        try:
            with _open(url, timeout) as r, part.open("wb") as fh:
                expected = r.headers.get("Content-Length")
                received = 0
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    fh.write(chunk)
                    received += len(chunk)
                if received == 0 or (expected is not None and received != int(expected)):
                    raise OSError(f"content length mismatch: expected {expected}, received {received}")
            part.replace(dest)
            log(f"http: {dest.name} ({dest.stat().st_size/1e6:.1f} MB)")
            return dest
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
            part.unlink(missing_ok=True)
            wait = 2 ** attempt
            log(f"http: {url} failed ({exc}); retry {attempt+1}/{retries} in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"download {url} failed after {retries} attempts: {last}")
