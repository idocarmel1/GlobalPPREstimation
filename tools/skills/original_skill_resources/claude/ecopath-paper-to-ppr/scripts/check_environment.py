"""Check whether the local environment can run each extraction stage."""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import shutil
import sys

from pdf_backend import available_backends


def present(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    packages = {
        "openpyxl": present("openpyxl"),
        "pandas": present("pandas"),
        "numpy": present("numpy"),
        "pymupdf": present("pymupdf") or present("fitz"),
    }
    commands = {name: bool(shutil.which(name)) for name in ["pdftotext", "pdfinfo", "pdftoppm"]}
    backends = available_backends()
    status = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": packages,
        "commands": commands,
        "pdf_backends": backends,
        "can_extract_pdf": bool(backends),
        "can_render_pdf": packages["pymupdf"] or commands["pdftoppm"],
        "can_write_import_files": packages["openpyxl"],
        "can_build_database_json": all(packages[k] for k in ["openpyxl", "pandas", "numpy"]),
    }
    status["ready"] = all(
        [
            status["can_extract_pdf"],
            status["can_render_pdf"],
            status["can_write_import_files"],
            status["can_build_database_json"],
        ]
    )

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(f"Python {status['python']} on {status['platform']}")
        print(f"PDF backends: {', '.join(backends) if backends else 'none'}")
        print(f"PDF rendering: {'ready' if status['can_render_pdf'] else 'unavailable'}")
        print(f"Import-file writer: {'ready' if status['can_write_import_files'] else 'missing openpyxl'}")
        print(f"Database JSON: {'ready' if status['can_build_database_json'] else 'missing pandas/numpy/openpyxl'}")
        print(f"Overall: {'READY' if status['ready'] else 'INCOMPLETE'}")
    return 0 if status["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
