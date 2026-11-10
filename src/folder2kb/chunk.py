"""Recursive character text splitter."""

from __future__ import annotations

DEFAULT_SEPARATORS: tuple[str, ...] = ("\n\n", "\n", "。", ". ", "！", "？", "! ", "? ", "；", "; ", "，", ", ", " ", "")


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
    separators: tuple[str, ...] = DEFAULT_SEPARATORS,
) -> list[str]:
    """Split ``text`` into chunks of at most ``chunk_size`` characters.

    Splitting prefers paragraph breaks, then newlines, then sentence
    punctuation, then spaces, and finally falls back to hard character cuts.
    Neighbouring chunks share roughly ``chunk_overlap`` characters of context.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and < chunk_size")
    text = text.strip()
    if not text:
        return []
    pieces = _split(text, chunk_size, list(separators))
    return [c for c in (_merge(pieces, chunk_size, chunk_overlap)) if c.strip()]


def _split(text: str, size: int, separators: list[str]) -> list[str]:
    """Recursively break text into pieces no longer than ``size``."""
    if len(text) <= size:
        return [text]
    for i, sep in enumerate(separators):
        if sep == "":
            return [text[j : j + size] for j in range(0, len(text), size)]
        if sep in text:
            parts = text.split(sep)
            # keep the separator attached to the end of each piece
            parts = [p + sep for p in parts[:-1]] + [parts[-1]]
            out: list[str] = []
            for p in parts:
                if not p:
                    continue
                if len(p) <= size:
                    out.append(p)
                else:
                    out.extend(_split(p, size, separators[i + 1 :]))
            return out
    return [text]


def _merge(pieces: list[str], size: int, overlap: int) -> list[str]:
    """Greedily merge small pieces into chunks, carrying over overlap."""
    chunks: list[str] = []
    current = ""
    for piece in pieces:
        if current and len(current) + len(piece) > size:
            chunks.append(current.strip())
            tail = current[-overlap:] if overlap else ""
            # don't let the overlap push the next chunk over the limit
            if len(tail) + len(piece) > size:
                tail = tail[len(tail) + len(piece) - size :]
            current = tail + piece
        else:
            current += piece
    if current.strip():
        chunks.append(current.strip())
    return chunks
