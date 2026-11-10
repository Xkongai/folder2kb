"""Turn supported files into plain text."""

from __future__ import annotations

from pathlib import Path

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({".md", ".markdown", ".txt", ".pdf"})


class UnsupportedFileType(ValueError):
    """Raised for file extensions folder2kb cannot parse."""


class ParseError(RuntimeError):
    """Raised when a supported file cannot be read."""


def is_supported(path: Path) -> bool:
    """Return True if ``path`` has a supported extension."""
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def parse_file(path: Path) -> str:
    """Extract text from ``path``.

    Markdown and text files are decoded as UTF-8 (invalid bytes replaced,
    BOM stripped). PDFs are read page by page with PyMuPDF.

    Raises:
        UnsupportedFileType: if the extension is not supported.
        ParseError: if the file cannot be read.
    """
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileType(f"Unsupported file type: {ext or '(none)'}")
    try:
        if ext == ".pdf":
            return _parse_pdf(path)
        text = path.read_bytes().decode("utf-8", errors="replace")
        return text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    except (UnsupportedFileType, ParseError):
        raise
    except Exception as exc:  # noqa: BLE001 - surface any reader failure clearly
        raise ParseError(f"Could not read {path}: {exc}") from exc


def _parse_pdf(path: Path) -> str:
    import pymupdf  # imported lazily: only needed for PDFs

    pages: list[str] = []
    with pymupdf.open(path) as doc:
        if doc.needs_pass:
            raise ParseError(f"PDF is encrypted: {path}")
        for page in doc:
            pages.append(page.get_text("text"))
    return "\n\n".join(p.strip() for p in pages if p.strip())
