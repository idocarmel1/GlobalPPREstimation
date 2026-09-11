"""One-line progress logging, quiet by default in library use."""

from __future__ import annotations

import sys
import time

_T0 = time.time()
_ENABLED = True


def set_enabled(flag: bool) -> None:
    global _ENABLED
    _ENABLED = flag


def log(msg: str) -> None:
    if _ENABLED:
        print(f"[{time.time() - _T0:7.1f}s] {msg}", file=sys.stderr, flush=True)
