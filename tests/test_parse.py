from pathlib import Path

import pytest

from folder2kb.parse import UnsupportedFileType, is_supported, parse_file


def test_parse_markdown(fixtures_dir: Path) -> None:
    text = parse_file(fixtures_dir / "sample.md")
    assert "退货政策" in text
    assert "Return policy" in text


def test_parse_txt(fixtures_dir: Path) -> None:
    assert "shipping" in parse_file(fixtures_dir / "sample.txt")


def test_invalid_utf8_is_replaced(tmp_path: Path) -> None:
    p = tmp_path / "bad.txt"
    p.write_bytes(b"hello \xff\xfe world")
    text = parse_file(p)
    assert "hello" in text and "world" in text


def test_bom_and_crlf(tmp_path: Path) -> None:
    p = tmp_path / "bom.md"
    p.write_bytes("\ufeffline1\r\nline2".encode("utf-8"))
    assert parse_file(p) == "line1\nline2"


def test_unsupported(tmp_path: Path) -> None:
    p = tmp_path / "x.docx"
    p.write_text("x")
    assert not is_supported(p)
    with pytest.raises(UnsupportedFileType):
        parse_file(p)


def test_parse_pdf(tmp_path: Path) -> None:
    pymupdf = pytest.importorskip("pymupdf")
    p = tmp_path / "doc.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Refund within 30 days of delivery.")
    doc.save(p)
    doc.close()
    assert "Refund within 30 days" in parse_file(p)
