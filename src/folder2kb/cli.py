"""Command-line interface for folder2kb."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from . import __version__
from .ask import search
from .config import CONFIG_FILENAME, Config, ConfigError, find_config, load_config, write_config
from .ingest import import_path
from .store import Store, StoreError

app = typer.Typer(
    name="folder2kb",
    help="One command turns any folder of documents into a local, queryable knowledge base.",
    add_completion=False,
    no_args_is_help=True,
)


def _fail(msg: str, code: int = 1) -> None:
    typer.secho(f"Error: {msg}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-V", callback=_version_callback, is_eager=True, help="Show version and exit."
    ),
) -> None:
    """folder2kb: offline BM25 knowledge base for your documents (Chinese + English)."""


def _load() -> tuple[Config, Store]:
    try:
        cfg = load_config()
    except ConfigError as exc:
        _fail(str(exc))
    try:
        store = Store.load(cfg.kb_path)
    except StoreError as exc:
        _fail(str(exc))
    return cfg, store


@app.command()
def version() -> None:
    """Print the folder2kb version."""
    typer.echo(__version__)


@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite an existing folder2kb.yaml."),
) -> None:
    """Create folder2kb.yaml and the .kb/ store in the current directory."""
    cwd = Path.cwd()
    cfg_path = cwd / CONFIG_FILENAME
    if cfg_path.exists() and not force:
        typer.echo(f"{CONFIG_FILENAME} already exists (use --force to overwrite).")
    else:
        write_config(cwd)
        typer.echo(f"Wrote {cfg_path}")
    try:
        cfg = load_config(cwd)
        Store.init(cfg.kb_path)
    except (ConfigError, StoreError, OSError) as exc:
        _fail(str(exc))
    typer.echo(f"Knowledge base ready at {cfg.kb_path}")
    typer.echo('Next: folder2kb import <folder>  then  folder2kb ask "your question"')


@app.command("import")
def import_cmd(
    path: Path = typer.Argument(..., help="File or folder to import (recursive)."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="List every file."),
) -> None:
    """Import .md / .txt / .pdf files into the knowledge base."""
    cfg, store = _load()
    try:
        result = import_path(store, path, cfg.root, cfg.chunk_size, cfg.chunk_overlap)
    except FileNotFoundError as exc:
        _fail(str(exc))
    except OSError as exc:
        _fail(f"Could not write knowledge base: {exc}")

    if verbose:
        for p in result.imported:
            typer.echo(f"  + {p}")
        for p in result.skipped:
            typer.echo(f"  = {p} (unchanged)")
    for p in result.unsupported:
        typer.secho(f"  ~ {p} (unsupported type, ignored)", fg=typer.colors.YELLOW)
    for p, err in result.failed:
        typer.secho(f"  ! {p}: {err}", fg=typer.colors.RED, err=True)
    typer.echo(
        f"imported: {len(result.imported)}  skipped: {len(result.skipped)}  "
        f"failed: {len(result.failed)}  (ignored unsupported: {len(result.unsupported)})"
    )
    typer.echo(f"total: {store.doc_count} docs, {store.chunk_count} chunks")
    if result.failed and not result.imported and not result.skipped:
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Show document count, chunk count, index path and last import time."""
    cfg, store = _load()
    cfg_path = find_config()
    typer.echo(f"config:      {cfg_path if cfg_path else '(defaults)'}")
    typer.echo(f"index path:  {cfg.kb_path}")
    typer.echo(f"documents:   {store.doc_count}")
    typer.echo(f"chunks:      {store.chunk_count}")
    typer.echo(f"last import: {store.last_import or 'never'}")


@app.command()
def ask(
    query: str = typer.Argument(..., help="Question or keywords (Chinese or English)."),
    k: Optional[int] = typer.Option(None, "--top-k", "-k", min=1, help="Number of results (default from config)."),
    width: int = typer.Option(300, "--width", help="Max characters of each chunk to print (0 = full)."),
) -> None:
    """Retrieve the top-k most relevant chunks for QUERY."""
    cfg, store = _load()
    if store.chunk_count == 0:
        _fail("The knowledge base is empty. Run `folder2kb import <folder>` first.", code=2)
    hits = search(store, query, k or cfg.top_k)
    if not hits:
        typer.echo("No matching chunks.")
        raise typer.Exit(3)
    for rank, hit in enumerate(hits, 1):
        text = " ".join(hit.chunk.text.split())
        if width and len(text) > width:
            text = text[:width].rstrip() + "…"
        typer.secho(
            f"[{rank}] {hit.chunk.doc_path}  (chunk {hit.chunk.chunk_index}, score {hit.score:.3f})",
            fg=typer.colors.CYAN,
            bold=True,
        )
        typer.echo(f"    {text}\n")


if __name__ == "__main__":  # pragma: no cover
    app()
