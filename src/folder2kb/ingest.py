"""Import files into the store (incremental by content hash)."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path

from .chunk import chunk_text
from .parse import ParseError, is_supported, parse_file
from .store import DocRecord, Store, _now

SKIP_DIRS = {".git", ".hg", ".svn", ".kb", ".venv", "venv", "node_modules", "__pycache__"}


@dataclass
class ImportResult:
    """Counts and notes from one import run."""

    imported: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file's contents."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def iter_files(target: Path, kb_path: Path | None = None) -> list[Path]:
    """List files under ``target`` (or ``target`` itself), skipping hidden/VCS/store dirs."""
    if target.is_file():
        return [target]
    kb_resolved = kb_path.resolve() if kb_path else None
    out: list[Path] = []
    for root, dirs, files in os.walk(target):
        rootp = Path(root)
        dirs[:] = sorted(
            d
            for d in dirs
            if d not in SKIP_DIRS
            and not d.startswith(".")
            and (kb_resolved is None or (rootp / d).resolve() != kb_resolved)
        )
        out.extend(rootp / f for f in sorted(files) if not f.startswith("."))
    return out


def doc_key(path: Path, root: Path) -> str:
    """Key used to identify a document: POSIX path relative to ``root`` if possible."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def import_path(
    store: Store,
    target: Path,
    root: Path,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> ImportResult:
    """Import a file or directory tree into ``store`` and save it.

    Unchanged files (same SHA-256 as already stored) are skipped.
    Unsupported extensions are noted and ignored; parse failures are recorded.
    """
    if not target.exists():
        raise FileNotFoundError(f"Path not found: {target}")
    result = ImportResult()
    for path in iter_files(target, store.kb_path):
        key = doc_key(path, root)
        if not is_supported(path):
            result.unsupported.append(key)
            continue
        try:
            digest = sha256_file(path)
            existing = store.docs.get(key)
            if existing and existing.sha256 == digest:
                result.skipped.append(key)
                continue
            text = parse_file(path)
            chunks = chunk_text(text, chunk_size, chunk_overlap)
            st = path.stat()
            record = DocRecord(
                path=key,
                sha256=digest,
                mtime=st.st_mtime,
                size=st.st_size,
                n_chunks=len(chunks),
                imported_at=_now(),
            )
            store.upsert(record, chunks)
            result.imported.append(key)
        except (ParseError, OSError) as exc:
            result.failed.append((key, str(exc)))
    store.last_import = _now()
    store.save()
    return result
