"""Portable PDF primitives used by the Ecopath extraction scripts.

PyMuPDF is preferred because it works consistently on Windows, macOS, and
Linux. Poppler command-line tools remain supported as a fallback.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


class PDFBackendError(RuntimeError):
    pass


def _fitz():
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            return None
    return fitz


def available_backends() -> list[str]:
    found: list[str] = []
    if _fitz() is not None:
        found.append("pymupdf")
    if shutil.which("pdftotext") and shutil.which("pdfinfo"):
        found.append("poppler")
    return found


def choose_backend(requested: str = "auto") -> str:
    requested = requested.lower()
    available = available_backends()
    if requested == "auto":
        if available:
            return available[0]
    elif requested in available:
        return requested
    elif requested not in {"pymupdf", "poppler"}:
        raise PDFBackendError(f"unknown PDF backend: {requested}")
    raise PDFBackendError(
        "no usable PDF backend; install PyMuPDF or make Poppler's "
        "pdftotext and pdfinfo available on PATH"
    )


def page_count(pdf: str | Path, backend: str = "auto") -> int:
    pdf = str(Path(pdf))
    selected = choose_backend(backend)
    if selected == "pymupdf":
        fitz = _fitz()
        with fitz.open(pdf) as doc:
            return len(doc)
    result = subprocess.run(
        ["pdfinfo", pdf], capture_output=True, text=True, errors="replace", check=True
    )
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if not match:
        raise PDFBackendError("pdfinfo did not report a page count")
    return int(match.group(1))


def _check_page(page: int, count: int) -> None:
    if page < 1 or page > count:
        raise PDFBackendError(f"page {page} outside valid range 1-{count}")


def page_text(pdf: str | Path, page: int, backend: str = "auto") -> str:
    pdf = str(Path(pdf))
    selected = choose_backend(backend)
    if selected == "pymupdf":
        fitz = _fitz()
        with fitz.open(pdf) as doc:
            _check_page(page, len(doc))
            return doc[page - 1].get_text("text", sort=True)
    result = subprocess.run(
        ["pdftotext", "-f", str(page), "-l", str(page), pdf, "-"],
        capture_output=True,
        text=True,
        errors="replace",
        check=True,
    )
    return result.stdout


def word_boxes(
    pdf: str | Path, page: int, backend: str = "auto"
) -> list[tuple[float, float, float, float, str]]:
    """Return 1-based page words as x0, y0, x1, y1, text tuples."""
    pdf = str(Path(pdf))
    selected = choose_backend(backend)
    if selected != "pymupdf":
        raise PDFBackendError("Poppler word boxes are parsed by pdfgrid directly")
    fitz = _fitz()
    with fitz.open(pdf) as doc:
        _check_page(page, len(doc))
        words = doc[page - 1].get_text("words", sort=False)
    return [
        (float(x0), float(y0), float(x1), float(y1), str(text))
        for x0, y0, x1, y1, text, *_ in words
        if str(text).strip()
    ]


def render_page(
    pdf: str | Path,
    page: int,
    output: str | Path,
    dpi: int = 200,
    backend: str = "auto",
) -> Path:
    pdf = str(Path(pdf))
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    selected = choose_backend(backend)
    if selected == "pymupdf":
        fitz = _fitz()
        with fitz.open(pdf) as doc:
            _check_page(page, len(doc))
            pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
            pix.save(str(output))
        return output
    if not shutil.which("pdftoppm"):
        raise PDFBackendError(
            "Poppler text tools are available, but pdftoppm is missing; "
            "install PyMuPDF or add pdftoppm to PATH for page rendering"
        )
    prefix = output.with_suffix("")
    subprocess.run(
        [
            "pdftoppm", "-f", str(page), "-l", str(page), "-r", str(dpi),
            "-png", "-singlefile", pdf, str(prefix),
        ],
        check=True,
    )
    rendered = prefix.with_suffix(".png")
    if rendered != output:
        rendered.replace(output)
    return output
