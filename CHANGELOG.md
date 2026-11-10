# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project homepage: banner, social preview, how-it-works diagram and real terminal screenshots in `docs/images/`.
- Japanese README (`README.ja.md`); English / 简体中文 / 日本語 language switcher in all READMEs.

## [0.1.0] - 2026-11-10

### Added
- `folder2kb init` creates `folder2kb.yaml` and a local `.kb/` store.
- `folder2kb import <path>` imports `.md`, `.txt` and `.pdf` files recursively, with
  incremental re-import (unchanged files are skipped by SHA-256).
- `folder2kb status` shows document/chunk counts, index path and last import time.
- `folder2kb ask "<query>"` returns the top-k matching chunks using BM25.
- Mixed Chinese/English tokenizer (Latin words + CJK unigrams and bigrams), no jieba needed.
- `folder2kb version` / `folder2kb --version`.
