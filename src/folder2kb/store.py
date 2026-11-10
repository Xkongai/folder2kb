"""On-disk store: ``manifest.json`` (documents) + ``chunks.jsonl`` (chunks)."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

MANIFEST = "manifest.json"
CHUNKS = "chunks.jsonl"
STORE_VERSION = 1


class StoreError(RuntimeError):
    """Raised when the store on disk is missing or corrupt."""


@dataclass
class Chunk:
    """One retrievable piece of a document."""

    doc_path: str
    chunk_index: int
    text: str

    @property
    def id(self) -> str:
        """Stable identifier ``<path>#<index>``."""
        return f"{self.doc_path}#{self.chunk_index}"


@dataclass
class DocRecord:
    """Metadata about one imported document."""

    path: str
    sha256: str
    mtime: float
    size: int
    n_chunks: int
    imported_at: str


@dataclass
class Store:
    """In-memory view of the knowledge base, loaded from / saved to ``kb_path``."""

    kb_path: Path
    docs: dict[str, DocRecord] = field(default_factory=dict)
    chunks: dict[str, list[Chunk]] = field(default_factory=dict)
    last_import: str | None = None
    created_at: str | None = None

    # ---- lifecycle -------------------------------------------------------
    @classmethod
    def init(cls, kb_path: Path) -> "Store":
        """Create an empty store directory if needed and return the store."""
        kb_path.mkdir(parents=True, exist_ok=True)
        if (kb_path / MANIFEST).exists():
            return cls.load(kb_path)
        store = cls(kb_path=kb_path, created_at=_now())
        store.save()
        return store

    @classmethod
    def load(cls, kb_path: Path) -> "Store":
        """Load a store from disk.

        Raises:
            StoreError: if the store does not exist or cannot be parsed.
        """
        manifest_path = kb_path / MANIFEST
        if not manifest_path.exists():
            raise StoreError(f"No knowledge base at {kb_path}. Run `folder2kb init` first.")
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            docs = {p: DocRecord(**d) for p, d in data.get("docs", {}).items()}
            chunks: dict[str, list[Chunk]] = {p: [] for p in docs}
            chunks_path = kb_path / CHUNKS
            if chunks_path.exists():
                with chunks_path.open(encoding="utf-8") as fh:
                    for line in fh:
                        if not line.strip():
                            continue
                        c = Chunk(**json.loads(line))
                        if c.doc_path in chunks:
                            chunks[c.doc_path].append(c)
        except (json.JSONDecodeError, TypeError, KeyError) as exc:
            raise StoreError(f"Knowledge base at {kb_path} is corrupt: {exc}") from exc
        for lst in chunks.values():
            lst.sort(key=lambda c: c.chunk_index)
        return cls(
            kb_path=kb_path,
            docs=docs,
            chunks=chunks,
            last_import=data.get("last_import"),
            created_at=data.get("created_at"),
        )

    def save(self) -> None:
        """Atomically write manifest and chunks to disk."""
        self.kb_path.mkdir(parents=True, exist_ok=True)
        manifest: dict[str, Any] = {
            "version": STORE_VERSION,
            "created_at": self.created_at,
            "last_import": self.last_import,
            "docs": {p: asdict(d) for p, d in sorted(self.docs.items())},
        }
        lines = (
            json.dumps(asdict(c), ensure_ascii=False) + "\n"
            for p in sorted(self.chunks)
            for c in self.chunks[p]
        )
        _atomic_write(self.kb_path / CHUNKS, lines)
        _atomic_write(self.kb_path / MANIFEST, [json.dumps(manifest, ensure_ascii=False, indent=2)])

    # ---- mutation --------------------------------------------------------
    def upsert(self, record: DocRecord, texts: list[str]) -> None:
        """Insert or replace a document and its chunks."""
        self.docs[record.path] = record
        self.chunks[record.path] = [Chunk(record.path, i, t) for i, t in enumerate(texts)]

    def remove(self, path: str) -> None:
        """Remove a document and its chunks (no-op if absent)."""
        self.docs.pop(path, None)
        self.chunks.pop(path, None)

    # ---- queries ---------------------------------------------------------
    def all_chunks(self) -> list[Chunk]:
        """Return every chunk in a deterministic order."""
        return [c for p in sorted(self.chunks) for c in self.chunks[p]]

    @property
    def doc_count(self) -> int:
        """Number of documents in the store."""
        return len(self.docs)

    @property
    def chunk_count(self) -> int:
        """Number of chunks in the store."""
        return sum(len(v) for v in self.chunks.values())


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _atomic_write(path: Path, parts: Iterable[str]) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            for part in parts:
                fh.write(part)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
