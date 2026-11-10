<p align="center">
  <img src="docs/images/banner.png" alt="folder2kb — Ein Befehl macht aus einem Ordner eine lokale Wissensbasis." width="100%">
</p>

<h1 align="center">folder2kb</h1>

<p align="center">
  <b>Ein Befehl macht aus jedem Dokumentordner eine lokale, abfragbare Wissensbasis.</b><br>
  Offline-BM25-Suche über Markdown, Text und PDF — Chinesisch und Englisch, ohne GPU, ohne Modell-Download.
</p>

<p align="center">
  <a href="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml"><img src="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python 3.11+">
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <a href="README.pt-BR.md">Português (Brasil)</a> | <a href="README.fr.md">Français</a> | <b>Deutsch</b> | <a href="README.ko.md">한국어</a> | <a href="README.ru.md">Русский</a>
</p>

```bash
folder2kb import ~/notes
folder2kb ask "return policy for opened items"
```

folder2kb geht einen Ordner durch, extrahiert Text aus Markdown-, Klartext- und PDF-Dateien,
teilt ihn in Chunks und lässt dich im Terminal mit BM25 danach suchen —
vollständig offline, auf Chinesisch und Englisch, ohne GPU und ohne Modell-Download.

## Inhalt

- [Warum folder2kb?](#warum-folder2kb)
- [Demo](#demo)
- [Installation](#installation)
- [Schnellstart](#schnellstart)
- [Befehle](#befehle)
- [Unterstützte Formate](#unterstützte-formate)
- [Konfiguration](#konfiguration)
- [So funktioniert es](#so-funktioniert-es)
- [Anwendungsfälle](#anwendungsfälle)
- [Roadmap und Einschränkungen](#roadmap-und-einschränkungen)
- [Mitwirken](#mitwirken)
- [Lizenz](#lizenz)

## Warum folder2kb?

| | |
| --- | --- |
| 🔒 **Offline zuerst** | Alles liegt in einem Ordner `.kb/` neben deiner Konfiguration. Keine Netzwerkanfragen, keine API-Schlüssel, keine Telemetrie. |
| 🀄 **Chinesisch und Englisch von Anfang an** | Ein eingebauter Tokenizer verarbeitet lateinische Wörter und CJK-Text (Zeichen-Unigramme und -Bigramme), sodass Abfragen wie `退货政策` sofort funktionieren — ohne jieba, ohne Wörterbücher. |
| 🪶 **Klein und schnell installiert** | Kein PyTorch, kein Embedding-Modell, keine Vektordatenbank. Vier kleine Abhängigkeiten. |
| ♻️ **Inkrementell** | Ein erneutes `import` überspringt Dateien, deren Inhalt sich nicht geändert hat (SHA-256). |
| 📄 **Speicherung in lesbaren Dateien** | Der Index ist lesbares `manifest.json` plus `chunks.jsonl`; leicht zu prüfen, zu sichern oder in die eigene RAG-Pipeline zu geben. |

## Demo

Die Screenshots unten sind die echte Ausgabe von folder2kb 0.1.0 nach
`folder2kb import ./docs`. Die Beispieldateien sind eine fiktive Rückgaberichtlinie von „Acme 小店 / Acme Store“
(Markdown) und eine Versand-FAQ (Klartext) — dieselben Dokumente liegen auch
in [`tests/fixtures/`](tests/fixtures).

**1. Eine Wissensbasis anlegen und einen Ordner importieren**

<img src="docs/images/demo-import.png" alt="Ausgabe von folder2kb init und folder2kb import" width="100%">

**2. Nachsehen, was darin ist**

<img src="docs/images/demo-status.png" alt="Ausgabe von folder2kb status" width="100%">

**3. Auf Chinesisch fragen — `退货政策` („Rückgaberichtlinie“) trifft den richtigen Chunk zuerst**

<img src="docs/images/demo-ask.png" alt="Ausgabe von folder2kb ask 退货政策" width="100%">

Der beste Treffer ist der zweisprachige Abschnitt zur Rückgaberichtlinie (Score 2.811); schwächere Treffer folgen
mit niedrigeren Scores. Jedes Ergebnis zeigt die Quelldatei, die Chunk-Nummer und den BM25-Score.

## Installation

Erfordert **Python 3.11+**.

```bash
git clone https://github.com/Xkongai/folder2kb.git
cd folder2kb
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Prüfen, ob es läuft:

```bash
folder2kb --version   # 0.1.0
```

## Schnellstart

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

Beispielausgabe:

```text
$ folder2kb import ./docs
imported: 2  skipped: 0  failed: 0  (ignored unsupported: 0)
total: 2 docs, 3 chunks

$ folder2kb ask "退货政策"
[1] docs/sample.md  (chunk 0, score 2.811)
    # Acme 小店退货政策 / Acme Store Return Policy ## 退货政策 自签收之日起 30 天内，未使用且包装完好的商品可以申请无理由退货。…
```

Führe `import` erneut aus; unveränderte Dateien werden als `skipped` gemeldet.

## Befehle

| Befehl | Was er tut |
| --- | --- |
| `folder2kb init [--force]` | Legt `folder2kb.yaml` und `.kb/` an (überschreibt eine vorhandene Konfiguration nicht ohne `--force`). |
| `folder2kb import <path> [-v]` | Importiert eine Datei oder einen Ordner rekursiv; gibt die Zahlen für imported / skipped / failed aus. `-v` listet jede Datei. |
| `folder2kb status` | Zeigt Dokumentanzahl, Chunk-Anzahl, Indexpfad und Zeitpunkt des letzten Imports. |
| `folder2kb ask "<query>" [-k N] [--width N]` | Gibt die Top-k-Chunks mit Quellpfad und Score aus. `--width` begrenzt die ausgegebenen Zeichen pro Chunk (Vorgabe 300, `0` = vollständig). |
| `folder2kb version` / `--version` | Gibt die Version aus. |

Beendigungscodes:

| Code | Bedeutung |
| --- | --- |
| `0` | Erfolg |
| `1` | Fehler (fehlerhafte Konfiguration, Speicher nicht lesbar, fehlender Pfad, oder alle Dateien eines Imports sind fehlgeschlagen) |
| `2` | `ask` auf einer leeren Wissensbasis — zuerst `folder2kb import` ausführen |
| `3` | `ask` hat keine passenden Chunks gefunden |

## Unterstützte Formate

| Erweiterung | Parser |
| --- | --- |
| `.md`, `.markdown` | UTF-8-Text (ungültige Bytes werden ersetzt) |
| `.txt` | UTF-8-Text (ungültige Bytes werden ersetzt) |
| `.pdf` | Textextraktion mit [PyMuPDF](https://pymupdf.readthedocs.io/) (kein OCR) |

Andere Dateien werden als "unsupported, ignored" aufgeführt und übersprungen. Versteckte Dateien und Ordner
(`.git`, `.venv`, `node_modules`, der `.kb/`-Speicher selbst, …) werden nie importiert.

## Konfiguration

`folder2kb init` schreibt `folder2kb.yaml` (siehe [`folder2kb.yaml.example`](folder2kb.yaml.example)):

```yaml
kb_dir: .kb          # where the knowledge base is stored (relative to this file)
chunk_size: 500      # max characters per chunk
chunk_overlap: 80    # characters shared between neighbouring chunks
top_k: 5             # default number of results for `ask`
```

| Schlüssel | Vorgabe | Beschreibung |
| --- | --- | --- |
| `kb_dir` | `.kb` | Wo die Wissensbasis liegt, relativ zu `folder2kb.yaml`. |
| `chunk_size` | `500` | Maximale Zeichenzahl pro Chunk. |
| `chunk_overlap` | `80` | Zeichen, die sich benachbarte Chunks teilen. |
| `top_k` | `5` | Standardzahl der Ergebnisse von `ask` (mit `-k` überschreibbar). |

folder2kb sucht `folder2kb.yaml` im aktuellen Verzeichnis und in den übergeordneten Verzeichnissen, du kannst
Befehle also aus jedem Unterordner deines Projekts ausführen. Gibt es keine Konfiguration, gelten die Vorgaben.

## So funktioniert es

<img src="docs/images/how-it-works.png" alt="Dateien → parsen → aufteilen → .kb/ → BM25 → Ergebnisse" width="100%">

```text
files ──► parse ──► chunk ──► .kb/ (manifest.json + chunks.jsonl) ──► BM25 ──► top-k results
```

1. **Parsen** — `.md`/`.txt` werden als UTF-8 gelesen; `.pdf`-Seiten werden mit PyMuPDF extrahiert.
2. **Aufteilen** — ein rekursiver Zeichen-Splitter trennt den Text an Absätzen, dann an Zeilen, dann an Satzzeichen (Chinesisch und Englisch), dann an Leerzeichen, in Chunks von ≤ `chunk_size` Zeichen mit `chunk_overlap` Zeichen Kontext.
3. **Speichern** — Dokumentmetadaten (Pfad, SHA-256, mtime, Größe, Chunk-Anzahl) landen in `manifest.json`; die Chunks in `chunks.jsonl`. Schreibvorgänge sind atomar.
4. **Suchen** — bei `ask` wird ein BM25-Index ([rank-bm25](https://github.com/dorianbrown/rank_bm25)) im Speicher aus den gespeicherten Chunks neu aufgebaut, mit demselben Tokenizer für Dokumente und Abfragen.

## Anwendungsfälle

- **Persönliche Notizen.** Richte es auf ein Obsidian-Vault oder einen Ordner mit Markdown-Notizen und durchsuche sie im Terminal, ohne etwas hochzuladen.
  ```bash
  cd ~/notes && folder2kb init && folder2kb import .
  folder2kb ask "docker compose healthcheck"
  ```
- **Team-Handbücher und FAQs.** Indexiere einen gemeinsamen Ordner mit Richtlinien, SOPs oder Antworten des Kundendienstes (wie im Acme-Beispiel) und finde den passenden Absatz in gemischtem chinesisch-englischem Text.
  ```bash
  folder2kb import ./handbook
  folder2kb ask "发票怎么开" -k 3
  ```
- **Offline-Vorverarbeitung für RAG.** Nutze folder2kb als einfache Retrieval-Schicht: Die Chunks liegen in einer lesbaren `chunks.jsonl`, du kannst sie aus deinem eigenen Skript lesen oder die Top-k-Ergebnisse von `ask` an das LLM weitergeben, das du schon verwendest.
  ```bash
  folder2kb ask "refund timeline" -k 5 --width 0 > context.txt
  ```

## Roadmap und Einschränkungen

Roadmap:

- [ ] Weitere Formate: `.docx`, `.html`
- [ ] `folder2kb watch` — inkrementeller Neuimport bei Dateiänderungen
- [ ] Vom Datenträger gelöschte Dokumente entfernen
- [ ] Optionale Embeddings über jede OpenAI-kompatible API (hybride Suche aus BM25 und Vektoren)
- [ ] Optionaler Chat mit einem lokalen LLM über die gefundenen Chunks (z. B. Ollama)
- [ ] JSON-Ausgabe für Skripte (`ask --json`)

Aktuelle Einschränkungen:

- **Kein OCR** — gescannte PDFs ohne Textebene liefern keinen durchsuchbaren Text.
- **Noch kein `.docx` / `.html`** — wandle sie zuerst in Markdown oder Text um.
- **Gelöschte Dateien werden nicht bereinigt** — eine Datei, die du von der Festplatte löschst, bleibt vorerst im Index.
- **`ask` baut BM25 bei jedem Aufruf im Speicher neu auf.** Das ist für persönliche Sammlungen und Sammlungen in Teamgröße schnell, aber nicht für Millionen von Chunks ausgelegt.
- **Stichwortsuche, keine semantische Suche** — BM25 vergleicht Wörter und Zeichen, daher treffen Synonyme ohne gemeinsame Zeichen nicht zu.

Derzeit nicht vorgesehen: Weboberfläche, mehrere Benutzer, Cloud-Synchronisierung, Web-Crawling.

## Mitwirken

Issues und Pull Requests sind willkommen! In [CONTRIBUTING.md](CONTRIBUTING.md) steht, wie du die Entwicklungsumgebung einrichtest
und die Tests ausführst (`pytest -q`).

## Lizenz

[MIT](LICENSE) © 2026 Xkongai
