import pytest

from folder2kb.chunk import chunk_text


def test_empty() -> None:
    assert chunk_text("   ") == []


def test_short_text_single_chunk() -> None:
    assert chunk_text("hello world", 100, 10) == ["hello world"]


def test_chunks_respect_size() -> None:
    text = "\n\n".join(f"Paragraph {i} " + "word " * 40 for i in range(20))
    chunks = chunk_text(text, 300, 50)
    assert len(chunks) > 1
    assert all(len(c) <= 300 for c in chunks)


def test_prefers_paragraph_boundaries() -> None:
    a, b = "A" * 200, "B" * 200
    chunks = chunk_text(f"{a}\n\n{b}", 250, 0)
    assert chunks == [a, b]


def test_overlap_carries_context() -> None:
    text = " ".join(f"w{i}" for i in range(300))
    chunks = chunk_text(text, 200, 40)
    assert len(chunks) > 1
    for prev, nxt in zip(chunks, chunks[1:]):
        assert prev[-15:].split()[-1] in nxt


def test_hard_split_long_cjk() -> None:
    text = "退" * 1200
    chunks = chunk_text(text, 500, 80)
    assert all(len(c) <= 500 for c in chunks)
    assert len(chunks) >= 3


def test_bad_params() -> None:
    with pytest.raises(ValueError):
        chunk_text("x", 100, 100)
    with pytest.raises(ValueError):
        chunk_text("x", 0, 0)
