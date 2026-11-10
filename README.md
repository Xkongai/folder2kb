<p align="center">
  <img src="docs/images/banner.png" alt="folder2kb — One command turns a folder into a local knowledge base." width="100%">
</p>

<h1 align="center">folder2kb</h1>

<p align="center">
  <b>One command turns any folder of documents into a local, queryable knowledge base.</b><br>
  Offline BM25 search over Markdown, text and PDF — Chinese and English, no GPU, no model download.
</p>

<p align="center">
  <a href="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml"><img src="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python 3.11+">
</p>

<p align="center">
  <b>English</b> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <a href="README.pt-BR.md">Português (Brasil)</a> | <a href="README.fr.md">Français</a> | <a href="README.de.md">Deutsch</a> | <a href="README.ko.md">한국어</a> | <a href="README.ru.md">Русский</a>
</p>

```bash
folder2kb import ~/notes
folder2kb ask "return policy for opened items"
```

folder2kb walks a folder, extracts text from Markdown, plain text and PDF files,
splits it into chunks, and lets you search it from the terminal with BM25 —
fully offline, in Chinese and English, with no GPU and no model download.

## Contents

- [Why folder2kb?](#why-folder2kb)
- [Demo](#demo)
- [Install](#install)
- [Quick start](#quick-start)
- [Commands](#commands)
- [Supported formats](#supported-formats)
- [Configuration](#configuration)
- [How it works](#how-it-works)
- [Use cases](#use-cases)
- [Roadmap & limitations](#roadmap--limitations)
- [Contributing](#contributing)
- [License](#license)

## Why folder2kb?

| | |
| --- | --- |
| 🔒 **Offline-first** | Everything lives in a `.kb/` folder next to your config. No network calls, no API keys, no telemetry. |
| 🀄 **Chinese + English out of the box** | A built-in tokenizer handles Latin words and CJK text (character unigrams + bigrams), so queries like `退货政策` just work — no jieba, no dictionaries. |
| 🪶 **Tiny and fast to install** | No PyTorch, no embedding model, no vector database. Four small dependencies. |
| ♻️ **Incremental** | Re-running `import` skips files whose contents haven't changed (SHA-256). |
| 📄 **Plain-file storage** | The index is a readable `manifest.json` + `chunks.jsonl`; easy to inspect, back up, or feed into your own RAG pipeline. |

## Demo

The screenshots below are real output from running folder2kb 0.1.0 after
`folder2kb import ./docs`. The sample files are a fictional “Acme 小店 / Acme Store”
return policy (Markdown) and shipping FAQ (plain text) — the same documents also
live in [`tests/fixtures/`](tests/fixtures).

**1. Create a knowledge base and import a folder**

<img src="docs/images/demo-import.png" alt="folder2kb init and folder2kb import output" width="100%">

**2. Check what's inside**

<img src="docs/images/demo-status.png" alt="folder2kb status output" width="100%">

**3. Ask in Chinese — `退货政策` (“return policy”) finds the right chunk first**

<img src="docs/images/demo-ask.png" alt="folder2kb ask 退货政策 output" width="100%">

The best match is the bilingual return-policy section (score 2.811); weaker matches follow
with lower scores. Each result shows the source file, the chunk number and the BM25 score.

## Install

Requires **Python 3.11+**.

```bash
git clone https://github.com/Xkongai/folder2kb.git
cd folder2kb
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Check it works:

```bash
folder2kb --version   # 0.1.0
```

## Quick start

```bash
# 1. Create folder2kb.yaml and an empty .kb/ in the current directory
folder2kb init

# 2. Import a file or a whole folder (recursive)
folder2kb import ./docs

# 3. See what's in the knowledge base
folder2kb status

# 4. Ask a question (Chinese or English)
folder2kb ask "退货政策"
folder2kb ask "how long do refunds take" -k 3
```

Example output:

```text
$ folder2kb import ./docs
imported: 2  skipped: 0  failed: 0  (ignored unsupported: 0)
total: 2 docs, 3 chunks

$ folder2kb ask "退货政策"
[1] docs/sample.md  (chunk 0, score 2.811)
    # Acme 小店退货政策 / Acme Store Return Policy ## 退货政策 自签收之日起 30 天内，未使用且包装完好的商品可以申请无理由退货。…
```

Run `import` again and unchanged files are reported as `skipped`.

## Commands

| Command | What it does |
| --- | --- |
| `folder2kb init [--force]` | Create `folder2kb.yaml` and `.kb/` (won't overwrite an existing config without `--force`). |
| `folder2kb import <path> [-v]` | Import a file or folder recursively; prints imported / skipped / failed counts. `-v` lists every file. |
| `folder2kb status` | Show document count, chunk count, index path and last import time. |
| `folder2kb ask "<query>" [-k N] [--width N]` | Print the top-k chunks with source path and score. `--width` limits printed characters per chunk (default 300, `0` = full). |
| `folder2kb version` / `--version` | Print the version. |

Exit codes:

| Code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Error (bad config, unreadable store, missing path, or every file in an import failed) |
| `2` | `ask` on an empty knowledge base — run `folder2kb import` first |
| `3` | `ask` found no matching chunks |

## Supported formats

| Extension | Parser |
| --- | --- |
| `.md`, `.markdown` | UTF-8 text (invalid bytes replaced) |
| `.txt` | UTF-8 text (invalid bytes replaced) |
| `.pdf` | [PyMuPDF](https://pymupdf.readthedocs.io/) text extraction (no OCR) |

Other files are listed as "unsupported, ignored" and skipped. Hidden files and folders
(`.git`, `.venv`, `node_modules`, the `.kb/` store itself, …) are never imported.

## Configuration

`folder2kb init` writes `folder2kb.yaml` (see [`folder2kb.yaml.example`](folder2kb.yaml.example)):

```yaml
kb_dir: .kb          # where the knowledge base is stored (relative to this file)
chunk_size: 500      # max characters per chunk
chunk_overlap: 80    # characters shared between neighbouring chunks
top_k: 5             # default number of results for `ask`
```

| Key | Default | Description |
| --- | --- | --- |
| `kb_dir` | `.kb` | Where the knowledge base is stored, relative to `folder2kb.yaml`. |
| `chunk_size` | `500` | Maximum characters per chunk. |
| `chunk_overlap` | `80` | Characters shared between neighbouring chunks. |
| `top_k` | `5` | Default number of results for `ask` (override with `-k`). |

folder2kb looks for `folder2kb.yaml` in the current directory and its parents, so you can
run commands from any subfolder of your project. If no config exists, defaults are used.

## How it works

<img src="docs/images/how-it-works.png" alt="files → parse → chunk → .kb/ → BM25 → results" width="100%">

```text
files ──► parse ──► chunk ──► .kb/ (manifest.json + chunks.jsonl) ──► BM25 ──► top-k results
```

1. **Parse** — `.md`/`.txt` are read as UTF-8; `.pdf` pages are extracted with PyMuPDF.
2. **Chunk** — a recursive character splitter breaks text at paragraphs, then lines, then sentence punctuation (Chinese and English), then spaces, into chunks of ≤ `chunk_size` characters with `chunk_overlap` characters of context.
3. **Store** — document metadata (path, SHA-256, mtime, size, chunk count) goes into `manifest.json`; chunks go into `chunks.jsonl`. Writes are atomic.
4. **Search** — on `ask`, a BM25 index ([rank-bm25](https://github.com/dorianbrown/rank_bm25)) is rebuilt in memory from the stored chunks, using the same tokenizer for documents and queries.

## Use cases

- **Personal notes.** Point it at an Obsidian vault or a folder of Markdown notes and search them from the terminal without uploading anything.
  ```bash
  cd ~/notes && folder2kb init && folder2kb import .
  folder2kb ask "docker compose healthcheck"
  ```
- **Team manuals and FAQs.** Index a shared folder of policies, SOPs or customer-service answers (like the Acme sample) and find the relevant paragraph in mixed Chinese/English text.
  ```bash
  folder2kb import ./handbook
  folder2kb ask "发票怎么开" -k 3
  ```
- **Offline RAG preprocessing.** Use folder2kb as a simple retrieval layer: chunks live in plain `chunks.jsonl`, so you can read them from your own script, or pass the top-k results from `ask` to whatever LLM you already use.
  ```bash
  folder2kb ask "refund timeline" -k 5 --width 0 > context.txt
  ```

## Roadmap & limitations

Roadmap:

- [ ] More formats: `.docx`, `.html`
- [ ] `folder2kb watch` — incremental re-import on file changes
- [ ] Prune documents deleted from disk
- [ ] Optional embeddings via any OpenAI-compatible API (hybrid BM25 + vector search)
- [ ] Optional local LLM chat over retrieved chunks (e.g. Ollama)
- [ ] JSON output for scripting (`ask --json`)

Current limitations:

- **No OCR** — scanned PDFs without a text layer produce no searchable text.
- **No `.docx` / `.html` yet** — convert them to Markdown or text first.
- **Deleted files are not pruned** — removing a file from disk doesn't remove it from the index yet.
- **`ask` rebuilds BM25 in memory** on every call. That's fast for personal and team-sized collections, but not designed for millions of chunks.
- **Keyword search, not semantic search** — BM25 matches words/characters, so synonyms that share no characters won't match.

Out of scope for now: web UI, multi-user, cloud sync, web crawling.

## Contributing

Issues and pull requests are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for the dev setup
and how to run the tests (`pytest -q`).

## License

[MIT](LICENSE) © 2026 Xkongai
