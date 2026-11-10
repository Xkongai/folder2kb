"""BM25 retrieval over stored chunks."""

from __future__ import annotations

from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from .store import Chunk, Store
from .tokenize import tokenize


@dataclass
class Hit:
    """A retrieved chunk with its BM25 score."""

    chunk: Chunk
    score: float


def search(store: Store, query: str, top_k: int = 5) -> list[Hit]:
    """Return up to ``top_k`` chunks ranked by BM25 relevance to ``query``.

    The BM25 index is rebuilt in memory from the stored chunks on every call.
    Chunks with a non-positive score are dropped.
    """
    chunks = store.all_chunks()
    if not chunks:
        return []
    q = tokenize(query)
    if not q:
        return []
    corpus = [tokenize(c.text) or [""] for c in chunks]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(q)
    # BM25Okapi IDF can go to ~0/negative on tiny corpora for very common
    # terms; fall back to raw term overlap so small KBs still rank sensibly.
    qset = set(q)
    ranked = sorted(
        (
            (float(s), sum(1 for t in toks if t in qset), i)
            for i, (s, toks) in enumerate(zip(scores, corpus))
        ),
        key=lambda x: (x[0], x[1]),
        reverse=True,
    )
    hits = [Hit(chunks[i], s) for s, overlap, i in ranked if overlap > 0]
    return hits[:top_k]
