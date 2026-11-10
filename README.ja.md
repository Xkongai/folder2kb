<p align="center">
  <img src="docs/images/banner.png" alt="folder2kb — コマンドひとつで、フォルダをローカルのナレッジベースに。" width="100%">
</p>

<h1 align="center">folder2kb</h1>

<p align="center">
  <b>コマンドひとつで、ドキュメントのフォルダを検索できるローカルのナレッジベースに。</b><br>
  Markdown・テキスト・PDF をオフラインで BM25 検索。中国語と英語に対応し、GPU もモデルのダウンロードも不要です。
</p>

<p align="center">
  <a href="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml"><img src="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python 3.11+">
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a> | <b>日本語</b> | <a href="README.es.md">Español</a> | <a href="README.pt-BR.md">Português (Brasil)</a> | <a href="README.fr.md">Français</a> | <a href="README.de.md">Deutsch</a> | <a href="README.ko.md">한국어</a> | <a href="README.ru.md">Русский</a>
</p>

```bash
folder2kb import ~/notes
folder2kb ask "return policy for opened items"
```

folder2kb はフォルダをたどって Markdown・プレーンテキスト・PDF から文字を取り出し、
チャンクに分割して、ターミナルから BM25 で検索できるようにします。
完全オフラインで動作し、中国語と英語に対応、GPU もモデルのダウンロードも必要ありません。

## 目次

- [folder2kb の特長](#folder2kb-の特長)
- [デモ](#デモ)
- [インストール](#インストール)
- [クイックスタート](#クイックスタート)
- [コマンド一覧](#コマンド一覧)
- [対応フォーマット](#対応フォーマット)
- [設定](#設定)
- [仕組み](#仕組み)
- [活用例](#活用例)
- [ロードマップと現在の制限](#ロードマップと現在の制限)
- [コントリビュート](#コントリビュート)
- [ライセンス](#ライセンス)

## folder2kb の特長

| | |
| --- | --- |
| 🔒 **オフラインファースト** | データはすべて設定ファイルの隣にある `.kb/` フォルダに保存されます。ネットワーク通信なし、API キー不要、テレメトリなし。 |
| 🀄 **中国語＋英語をそのまま検索** | 内蔵トークナイザーがラテン文字の単語と CJK テキスト（1 文字 + 隣接 2 文字）を処理するので、`退货政策` のようなクエリもそのまま使えます。jieba も辞書も不要です。 |
| 🪶 **軽量ですぐ入る** | PyTorch・埋め込みモデル・ベクトル DB は不要。依存パッケージは小さなものが 4 つだけです。 |
| ♻️ **差分インポート** | `import` を再実行すると、内容が変わっていないファイル（SHA-256 で判定）はスキップされます。 |
| 📄 **プレーンファイルで保存** | インデックスは読める形式の `manifest.json` + `chunks.jsonl`。中身の確認やバックアップ、独自の RAG パイプラインへの受け渡しも簡単です。 |

## デモ

以下のスクリーンショットは、folder2kb 0.1.0 で `folder2kb import ./docs` を実行したときの
実際の出力です。サンプルは架空の「Acme 小店 / Acme Store」の返品ポリシー（Markdown）と
配送 FAQ（プレーンテキスト）で、[`tests/fixtures/`](tests/fixtures) にある文書と同じものです。中国語と英語が混在しています。

**1. ナレッジベースを作成してフォルダをインポート**

<img src="docs/images/demo-import.png" alt="folder2kb init と folder2kb import の出力" width="100%">

**2. 中身を確認**

<img src="docs/images/demo-status.png" alt="folder2kb status の出力" width="100%">

**3. 中国語で質問 — `退货政策`（返品ポリシー）で正しいチャンクが 1 位に**

<img src="docs/images/demo-ask.png" alt="folder2kb ask 退货政策 の出力" width="100%">

1 位は中英併記の返品ポリシーのセクション（スコア 2.811）で、関連度の低い結果がそれに続きます。
各結果にはソースファイル、チャンク番号、BM25 スコアが表示されます。

## インストール

**Python 3.11 以上**が必要です。

```bash
git clone https://github.com/Xkongai/folder2kb.git
cd folder2kb
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

動作確認：

```bash
folder2kb --version   # 0.1.0
```

## クイックスタート

```bash
# 1. カレントディレクトリに folder2kb.yaml と空の .kb/ を作成
folder2kb init

# 2. ファイルまたはフォルダ全体をインポート（再帰的）
folder2kb import ./docs

# 3. ナレッジベースの状態を確認
folder2kb status

# 4. 質問する（中国語または英語）
folder2kb ask "退货政策"
folder2kb ask "how long do refunds take" -k 3
```

出力例：

```text
$ folder2kb import ./docs
imported: 2  skipped: 0  failed: 0  (ignored unsupported: 0)
total: 2 docs, 3 chunks

$ folder2kb ask "退货政策"
[1] docs/sample.md  (chunk 0, score 2.811)
    # Acme 小店退货政策 / Acme Store Return Policy ## 退货政策 自签收之日起 30 天内，未使用且包装完好的商品可以申请无理由退货。…
```

もう一度 `import` を実行すると、変更のないファイルは `skipped` と表示されます。

## コマンド一覧

| コマンド | 説明 |
| --- | --- |
| `folder2kb init [--force]` | `folder2kb.yaml` と `.kb/` を作成します（既存の設定は `--force` を付けない限り上書きしません）。 |
| `folder2kb import <パス> [-v]` | ファイルまたはフォルダを再帰的にインポートし、インポート / スキップ / 失敗の件数を表示します。`-v` で全ファイルを一覧表示。 |
| `folder2kb status` | ドキュメント数、チャンク数、インデックスのパス、最終インポート日時を表示します。 |
| `folder2kb ask "<質問>" [-k N] [--width N]` | 関連度の高い上位 k 件のチャンクを、ソースパスとスコア付きで表示します。`--width` はチャンクごとの表示文字数の上限（デフォルト 300、`0` で全文）。 |
| `folder2kb version` / `--version` | バージョンを表示します。 |

終了コード：

| コード | 意味 |
| --- | --- |
| `0` | 成功 |
| `1` | エラー（設定の不備、ストアが読めない、パスが存在しない、またはインポートした全ファイルが失敗） |
| `2` | 空のナレッジベースで `ask` を実行した — 先に `folder2kb import` を実行してください |
| `3` | `ask` で一致するチャンクが見つからなかった |

## 対応フォーマット

| 拡張子 | パーサー |
| --- | --- |
| `.md`、`.markdown` | UTF-8 テキスト（不正なバイトは置換） |
| `.txt` | UTF-8 テキスト（不正なバイトは置換） |
| `.pdf` | [PyMuPDF](https://pymupdf.readthedocs.io/) によるテキスト抽出（OCR なし） |

それ以外のファイルは「unsupported, ignored」と表示されてスキップされます。隠しファイル・隠しフォルダ
（`.git`、`.venv`、`node_modules`、`.kb/` ストア自体など）はインポートされません。

## 設定

`folder2kb init` は `folder2kb.yaml` を書き出します（[`folder2kb.yaml.example`](folder2kb.yaml.example) を参照）：

```yaml
kb_dir: .kb          # ナレッジベースの保存先（このファイルからの相対パス）
chunk_size: 500      # 1 チャンクあたりの最大文字数
chunk_overlap: 80    # 隣り合うチャンク間で重複させる文字数
top_k: 5             # ask のデフォルト結果件数
```

| キー | デフォルト | 説明 |
| --- | --- | --- |
| `kb_dir` | `.kb` | ナレッジベースの保存先（`folder2kb.yaml` からの相対パス）。 |
| `chunk_size` | `500` | 1 チャンクあたりの最大文字数。 |
| `chunk_overlap` | `80` | 隣り合うチャンク間で重複させる文字数。 |
| `top_k` | `5` | `ask` のデフォルト結果件数（`-k` で上書き可能）。 |

folder2kb はカレントディレクトリとその親ディレクトリから `folder2kb.yaml` を探すので、
プロジェクトのどのサブフォルダからでもコマンドを実行できます。設定ファイルがない場合はデフォルト値が使われます。

## 仕組み

<img src="docs/images/how-it-works.png" alt="ファイル → 解析 → 分割 → .kb/ → BM25 → 結果" width="100%">

```text
ファイル ──► 解析 ──► 分割 ──► .kb/（manifest.json + chunks.jsonl）──► BM25 ──► 上位 k 件
```

1. **解析** — `.md`/`.txt` は UTF-8 として読み込み、`.pdf` は PyMuPDF でページごとにテキストを抽出します。
2. **分割** — 再帰的な文字分割器が、段落 → 改行 → 文末の句読点（中国語・英語）→ スペースの順に区切り、`chunk_size` 文字以下のチャンクに分けます。前後のチャンクとは `chunk_overlap` 文字分の文脈を共有します。
3. **保存** — ドキュメントのメタデータ（パス、SHA-256、更新日時、サイズ、チャンク数）は `manifest.json` に、チャンクは `chunks.jsonl` に保存されます。書き込みはアトミックです。
4. **検索** — `ask` のたびに、保存済みチャンクから BM25 インデックス（[rank-bm25](https://github.com/dorianbrown/rank_bm25)）をメモリ上に再構築します。ドキュメントとクエリには同じトークナイザーを使います。

> **日本語について：** トークナイザーはひらがな・カタカナも漢字と同じく 1 文字 + 2 文字で分割するため、日本語の文書も検索できます。ただし、テストは主に中国語と英語で行っています。

## 活用例

- **個人のメモ。** Obsidian の Vault や Markdown メモのフォルダを指定すれば、何もアップロードせずにターミナルから検索できます。
  ```bash
  cd ~/notes && folder2kb init && folder2kb import .
  folder2kb ask "docker compose healthcheck"
  ```
- **チームのマニュアルや FAQ。** 規程、SOP、カスタマーサポートの回答集（Acme のサンプルのようなもの）を共有フォルダごとインデックス化し、中英混在のテキストから該当する段落をすぐに見つけられます。
  ```bash
  folder2kb import ./handbook
  folder2kb ask "返品の送料" -k 3
  ```
- **オフライン RAG の前処理。** シンプルな検索レイヤーとして使えます。チャンクは普通の `chunks.jsonl` に入っているので自作スクリプトから読めますし、`ask` の上位 k 件をお使いの LLM にそのまま渡すこともできます。
  ```bash
  folder2kb ask "refund timeline" -k 5 --width 0 > context.txt
  ```

## ロードマップと現在の制限

ロードマップ：

- [ ] 対応フォーマットの追加：`.docx`、`.html`
- [ ] `folder2kb watch` — ファイル変更時の自動差分インポート
- [ ] ディスクから削除されたドキュメントの整理
- [ ] オプション：OpenAI 互換 API による埋め込み（BM25 + ベクトルのハイブリッド検索）
- [ ] オプション：検索結果をもとにしたローカル LLM とのチャット（Ollama など）
- [ ] スクリプト向けの JSON 出力（`ask --json`）

現在の制限：

- **OCR なし** — テキストレイヤーのないスキャン PDF は検索できません。
- **`.docx` / `.html` は未対応** — 先に Markdown またはテキストに変換してください。
- **削除したファイルは自動で除去されない** — ディスクからファイルを消しても、今のところインデックスには残ります。
- **`ask` は毎回 BM25 をメモリ上に再構築します。** 個人やチーム規模の文書なら十分高速ですが、数百万チャンク規模は想定していません。
- **キーワード検索であり、意味検索ではありません** — BM25 は語や文字で一致を判定するため、共通する文字のない言い換えはヒットしません。

当面の対象外：Web UI、マルチユーザー、クラウド同期、Web クロール。

## コントリビュート

Issue と Pull Request を歓迎します！開発環境のセットアップとテストの実行方法（`pytest -q`）は [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## ライセンス

[MIT](LICENSE) © 2026 Xkongai
