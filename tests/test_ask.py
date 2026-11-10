import os
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from folder2kb import __version__
from folder2kb.ask import search
from folder2kb.cli import app
from folder2kb.ingest import import_path
from folder2kb.store import Store

runner = CliRunner()


@pytest.fixture
def kb(tmp_path: Path, fixtures_dir: Path) -> tuple[Store, Path]:
    docs = tmp_path / "docs"
    shutil.copytree(fixtures_dir, docs)
    store = Store.init(tmp_path / ".kb")
    import_path(store, docs, tmp_path, 500, 80)
    return store, docs


def test_chinese_query_finds_return_policy(kb: tuple[Store, Path]) -> None:
    store, _ = kb
    hits = search(Store.load(store.kb_path), "退货政策", 3)
    assert hits
    assert hits[0].chunk.doc_path.endswith("sample.md")
    assert "退货" in hits[0].chunk.text


def test_english_query(kb: tuple[Store, Path]) -> None:
    store, _ = kb
    hits = search(store, "express shipping next day", 2)
    assert hits[0].chunk.doc_path.endswith("sample.txt")


def test_no_match_returns_empty(kb: tuple[Store, Path]) -> None:
    store, _ = kb
    assert search(store, "zzqqxx", 5) == []


def test_incremental_import(tmp_path: Path, kb: tuple[Store, Path]) -> None:
    store, docs = kb
    again = import_path(store, docs, tmp_path)
    assert again.imported == [] and len(again.skipped) == 2
    (docs / "sample.txt").write_text("changed content about warranty", encoding="utf-8")
    (docs / "notes.docx").write_text("x")
    third = import_path(store, docs, tmp_path)
    assert third.imported == ["docs/sample.txt"]
    assert third.unsupported == ["docs/notes.docx"]
    reloaded = Store.load(store.kb_path)
    assert reloaded.doc_count == 2
    assert search(reloaded, "warranty", 1)[0].chunk.doc_path == "docs/sample.txt"


def test_cli_end_to_end(tmp_path: Path, fixtures_dir: Path) -> None:
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        assert runner.invoke(app, ["--version"]).stdout.strip() == __version__
        assert runner.invoke(app, ["version"]).stdout.strip() == __version__

        # ask before init -> friendly failure
        r = runner.invoke(app, ["ask", "退货"])
        assert r.exit_code != 0

        r = runner.invoke(app, ["init"])
        assert r.exit_code == 0, r.output
        assert (tmp_path / "folder2kb.yaml").exists() and (tmp_path / ".kb").is_dir()

        # empty index -> nonzero
        r = runner.invoke(app, ["ask", "退货"])
        assert r.exit_code == 2

        # init again does not overwrite
        (tmp_path / "folder2kb.yaml").write_text("top_k: 2\n", encoding="utf-8")
        runner.invoke(app, ["init"])
        assert (tmp_path / "folder2kb.yaml").read_text(encoding="utf-8") == "top_k: 2\n"

        r = runner.invoke(app, ["import", str(fixtures_dir)])
        assert r.exit_code == 0, r.output
        assert "imported: 2" in r.output

        r = runner.invoke(app, ["status"])
        assert "documents:   2" in r.output

        r = runner.invoke(app, ["ask", "退货政策"])
        assert r.exit_code == 0, r.output
        assert "sample.md" in r.output
        assert r.output.count("score") <= 2  # top_k from config

        r = runner.invoke(app, ["import", str(tmp_path / "missing")])
        assert r.exit_code != 0
    finally:
        os.chdir(cwd)
