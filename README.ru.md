<p align="center">
  <img src="docs/images/banner.png" alt="folder2kb — Одна команда превращает папку в локальную базу знаний." width="100%">
</p>

<h1 align="center">folder2kb</h1>

<p align="center">
  <b>Одна команда превращает любую папку с документами в локальную базу знаний, по которой можно искать.</b><br>
  Офлайн-поиск BM25 по Markdown, тексту и PDF — китайский и английский, без GPU и без загрузки модели.
</p>

<p align="center">
  <a href="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml"><img src="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python 3.11+">
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <a href="README.pt-BR.md">Português (Brasil)</a> | <a href="README.fr.md">Français</a> | <a href="README.de.md">Deutsch</a> | <a href="README.ko.md">한국어</a> | <b>Русский</b>
</p>

```bash
folder2kb import ~/notes
folder2kb ask "return policy for opened items"
```

folder2kb обходит папку, извлекает текст из Markdown, обычного текста и PDF,
делит его на фрагменты и позволяет искать по ним из терминала с помощью BM25 —
полностью офлайн, на китайском и английском, без GPU и без загрузки модели.

## Содержание

- [Зачем folder2kb?](#зачем-folder2kb)
- [Демонстрация](#демонстрация)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Команды](#команды)
- [Поддерживаемые форматы](#поддерживаемые-форматы)
- [Настройка](#настройка)
- [Как это работает](#как-это-работает)
- [Сценарии использования](#сценарии-использования)
- [План и ограничения](#план-и-ограничения)
- [Участие](#участие)
- [Лицензия](#лицензия)

## Зачем folder2kb?

| | |
| --- | --- |
| 🔒 **Сначала офлайн** | Всё хранится в папке `.kb/` рядом с конфигурацией. Никаких сетевых запросов, ключей API и телеметрии. |
| 🀄 **Китайский и английский сразу** | Встроенный токенизатор обрабатывает латинские слова и текст CJK (униграммы и биграммы символов), поэтому запросы вроде `退货政策` работают сразу — без jieba и без словарей. |
| 🪶 **Маленький и быстро ставится** | Без PyTorch, модели эмбеддингов и векторной базы. Четыре небольшие зависимости. |
| ♻️ **Инкрементный** | Повторный `import` пропускает файлы, содержимое которых не изменилось (SHA-256). |
| 📄 **Хранение в обычных файлах** | Индекс — это читаемые `manifest.json` и `chunks.jsonl`: их легко просмотреть, сохранить в резервную копию или отдать в свой RAG-конвейер. |

## Демонстрация

Скриншоты ниже — реальный вывод folder2kb 0.1.0 после
`folder2kb import ./docs`. Примеры — вымышленная политика возврата «Acme 小店 / Acme Store»
(Markdown) и FAQ по доставке (обычный текст). Те же документы лежат
в [`tests/fixtures/`](tests/fixtures).

**1. Создать базу знаний и импортировать папку**

<img src="docs/images/demo-import.png" alt="вывод folder2kb init и folder2kb import" width="100%">

**2. Посмотреть, что внутри**

<img src="docs/images/demo-status.png" alt="вывод folder2kb status" width="100%">

**3. Спросить по-китайски — `退货政策` («политика возврата») находит нужный фрагмент первым**

<img src="docs/images/demo-ask.png" alt="вывод folder2kb ask 退货政策" width="100%">

Лучшее совпадение — двуязычный раздел политики возврата (оценка 2.811); более слабые совпадения идут
с меньшими оценками. Каждый результат показывает исходный файл, номер фрагмента и оценку BM25.

## Установка

Нужен **Python 3.11+**.

```bash
git clone https://github.com/Xkongai/folder2kb.git
cd folder2kb
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Проверьте, что всё работает:

```bash
folder2kb --version   # 0.1.0
```

## Быстрый старт

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

Пример вывода:

```text
$ folder2kb import ./docs
imported: 2  skipped: 0  failed: 0  (ignored unsupported: 0)
total: 2 docs, 3 chunks

$ folder2kb ask "退货政策"
[1] docs/sample.md  (chunk 0, score 2.811)
    # Acme 小店退货政策 / Acme Store Return Policy ## 退货政策 自签收之日起 30 天内，未使用且包装完好的商品可以申请无理由退货。…
```

Запустите `import` ещё раз — неизменённые файлы будут показаны как `skipped`.

## Команды

| Команда | Что делает |
| --- | --- |
| `folder2kb init [--force]` | Создаёт `folder2kb.yaml` и `.kb/` (не перезаписывает существующую конфигурацию без `--force`). |
| `folder2kb import <path> [-v]` | Рекурсивно импортирует файл или папку; печатает числа imported / skipped / failed. `-v` перечисляет каждый файл. |
| `folder2kb status` | Показывает число документов, число фрагментов, путь к индексу и время последнего импорта. |
| `folder2kb ask "<query>" [-k N] [--width N]` | Печатает top-k фрагментов с путём к источнику и оценкой. `--width` ограничивает число печатаемых символов фрагмента (по умолчанию 300, `0` — целиком). |
| `folder2kb version` / `--version` | Печатает версию. |

Коды выхода:

| Код | Значение |
| --- | --- |
| `0` | Успех |
| `1` | Ошибка (неверная конфигурация, хранилище не читается, путь не найден, или все файлы импорта завершились ошибкой) |
| `2` | `ask` по пустой базе знаний — сначала выполните `folder2kb import` |
| `3` | `ask` не нашёл подходящих фрагментов |

## Поддерживаемые форматы

| Расширение | Разбор |
| --- | --- |
| `.md`, `.markdown` | Текст UTF-8 (недопустимые байты заменяются) |
| `.txt` | Текст UTF-8 (недопустимые байты заменяются) |
| `.pdf` | Извлечение текста через [PyMuPDF](https://pymupdf.readthedocs.io/) (без OCR) |

Остальные файлы помечаются как "unsupported, ignored" и пропускаются. Скрытые файлы и папки
(`.git`, `.venv`, `node_modules`, само хранилище `.kb/`, …) никогда не импортируются.

## Настройка

`folder2kb init` записывает `folder2kb.yaml` (см. [`folder2kb.yaml.example`](folder2kb.yaml.example)):

```yaml
kb_dir: .kb          # where the knowledge base is stored (relative to this file)
chunk_size: 500      # max characters per chunk
chunk_overlap: 80    # characters shared between neighbouring chunks
top_k: 5             # default number of results for `ask`
```

| Ключ | По умолчанию | Описание |
| --- | --- | --- |
| `kb_dir` | `.kb` | Где хранится база знаний, относительно `folder2kb.yaml`. |
| `chunk_size` | `500` | Максимум символов во фрагменте. |
| `chunk_overlap` | `80` | Символы, общие для соседних фрагментов. |
| `top_k` | `5` | Число результатов `ask` по умолчанию (переопределяется через `-k`). |

folder2kb ищет `folder2kb.yaml` в текущем каталоге и в родительских, поэтому команды
можно запускать из любой подпапки проекта. Если конфигурации нет, используются значения по умолчанию.

## Как это работает

<img src="docs/images/how-it-works.png" alt="файлы → разбор → нарезка → .kb/ → BM25 → результаты" width="100%">

```text
files ──► parse ──► chunk ──► .kb/ (manifest.json + chunks.jsonl) ──► BM25 ──► top-k results
```

1. **Разбор** — `.md`/`.txt` читаются как UTF-8; страницы `.pdf` извлекаются через PyMuPDF.
2. **Нарезка** — рекурсивный разделитель по символам режет текст по абзацам, затем по строкам, затем по знакам конца предложения (китайский и английский), затем по пробелам, на фрагменты длиной ≤ `chunk_size` символов с контекстом в `chunk_overlap` символов.
3. **Хранение** — метаданные документа (путь, SHA-256, mtime, размер, число фрагментов) попадают в `manifest.json`; фрагменты — в `chunks.jsonl`. Запись атомарна.
4. **Поиск** — при `ask` индекс BM25 ([rank-bm25](https://github.com/dorianbrown/rank_bm25)) заново строится в памяти по сохранённым фрагментам, с одним и тем же токенизатором для документов и запросов.

## Сценарии использования

- **Личные заметки.** Укажите хранилище Obsidian или папку с заметками Markdown и ищите по ним из терминала, ничего не загружая.
  ```bash
  cd ~/notes && folder2kb init && folder2kb import .
  folder2kb ask "docker compose healthcheck"
  ```
- **Командные руководства и FAQ.** Проиндексируйте общую папку с политиками, SOP или ответами поддержки (как в примере Acme) и найдите нужный абзац в смешанном китайско-английском тексте.
  ```bash
  folder2kb import ./handbook
  folder2kb ask "发票怎么开" -k 3
  ```
- **Офлайн-подготовка для RAG.** Используйте folder2kb как простой слой поиска: фрагменты лежат в обычном `chunks.jsonl`, их можно читать своим скриптом или передавать top-k результаты `ask` той LLM, которой вы уже пользуетесь.
  ```bash
  folder2kb ask "refund timeline" -k 5 --width 0 > context.txt
  ```

## План и ограничения

План:

- [ ] Больше форматов: `.docx`, `.html`
- [ ] `folder2kb watch` — инкрементный повторный импорт при изменении файлов
- [ ] Убирать документы, удалённые с диска
- [ ] Необязательные эмбеддинги через любой API, совместимый с OpenAI (гибридный поиск BM25 и векторов)
- [ ] Необязательный чат с локальной LLM по найденным фрагментам (например, Ollama)
- [ ] Вывод JSON для скриптов (`ask --json`)

Текущие ограничения:

- **Нет OCR** — сканы PDF без текстового слоя не дают текста для поиска.
- **`.docx` / `.html` пока нет** — сначала преобразуйте их в Markdown или текст.
- **Удалённые файлы не вычищаются** — удаление файла с диска пока не убирает его из индекса.
- **`ask` каждый раз заново строит BM25 в памяти.** Для личных и командных коллекций это быстро, но не рассчитано на миллионы фрагментов.
- **Поиск по ключевым словам, а не семантический** — BM25 сопоставляет слова и символы, поэтому синонимы без общих символов не находятся.

Пока вне области: веб-интерфейс, несколько пользователей, облачная синхронизация, обход веба.

## Участие

Issues и pull request’ы приветствуются! Среда разработки и запуск тестов (`pytest -q`) описаны в [CONTRIBUTING.md](CONTRIBUTING.md).

## Лицензия

[MIT](LICENSE) © 2026 Xkongai
