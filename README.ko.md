<p align="center">
  <img src="docs/images/banner.png" alt="folder2kb — 명령 하나로 폴더를 로컬 지식 베이스로 바꿉니다." width="100%">
</p>

<h1 align="center">folder2kb</h1>

<p align="center">
  <b>명령 하나로, 어떤 문서 폴더든 로컬에서 검색할 수 있는 지식 베이스로 바꿉니다.</b><br>
  Markdown, 텍스트, PDF를 오프라인 BM25로 검색합니다. 중국어와 영어를 지원하며 GPU도, 모델 다운로드도 필요 없습니다.
</p>

<p align="center">
  <a href="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml"><img src="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python 3.11+">
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <a href="README.pt-BR.md">Português (Brasil)</a> | <a href="README.fr.md">Français</a> | <a href="README.de.md">Deutsch</a> | <b>한국어</b> | <a href="README.ru.md">Русский</a>
</p>

```bash
folder2kb import ~/notes
folder2kb ask "return policy for opened items"
```

folder2kb는 폴더를 훑어 Markdown, 일반 텍스트, PDF에서 글을 뽑아내고,
청크로 나눈 뒤 터미널에서 BM25로 검색하게 합니다.
완전히 오프라인이며 중국어와 영어를 다루고, GPU와 모델 다운로드가 필요 없습니다.

## 목차

- [왜 folder2kb인가요?](#왜-folder2kb인가요)
- [데모](#데모)
- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [명령](#명령)
- [지원 형식](#지원-형식)
- [설정](#설정)
- [동작 방식](#동작-방식)
- [사용 예](#사용-예)
- [로드맵과 한계](#로드맵과-한계)
- [기여](#기여)
- [라이선스](#라이선스)

## 왜 folder2kb인가요?

| | |
| --- | --- |
| 🔒 **오프라인 우선** | 모든 데이터는 설정 옆 `.kb/` 폴더에 있습니다. 네트워크 호출도, API 키도, 텔레메트리도 없습니다. |
| 🀄 **중국어와 영어를 바로 지원** | 내장 토크나이저가 라틴 단어와 CJK 텍스트(문자 유니그램과 바이그램)를 처리하므로 `退货政策` 같은 질의가 그대로 동작합니다. jieba도, 사전도 필요 없습니다. |
| 🪶 **작고 설치가 빠름** | PyTorch도, 임베딩 모델도, 벡터 데이터베이스도 없습니다. 작은 의존성 네 개뿐입니다. |
| ♻️ **증분** | `import`를 다시 실행하면 내용이 바뀌지 않은 파일(SHA-256)은 건너뜁니다. |
| 📄 **일반 파일로 저장** | 인덱스는 읽을 수 있는 `manifest.json`과 `chunks.jsonl`입니다. 살펴보고, 백업하고, 자체 RAG 파이프라인에 넣기 쉽습니다. |

## 데모

아래 스크린샷은 folder2kb 0.1.0에서
`folder2kb import ./docs`를 실행한 실제 출력입니다. 예제 파일은 가상의 “Acme 小店 / Acme Store”
반품 정책(Markdown)과 배송 FAQ(일반 텍스트)이며, [`tests/fixtures/`](tests/fixtures)에 있는 문서와 같습니다.

**1. 지식 베이스를 만들고 폴더를 가져오기**

<img src="docs/images/demo-import.png" alt="folder2kb init과 folder2kb import 출력" width="100%">

**2. 안에 무엇이 있는지 확인**

<img src="docs/images/demo-status.png" alt="folder2kb status 출력" width="100%">

**3. 중국어로 질문 — `退货政策`(“반품 정책”)이 맞는 청크를 맨 위에 찾습니다**

<img src="docs/images/demo-ask.png" alt="folder2kb ask 退货政策 출력" width="100%">

가장 잘 맞는 결과는 중국어와 영어가 함께 있는 반품 정책 절(점수 2.811)이고, 점수가 더 낮은 결과가 뒤를 잇습니다.
각 결과에는 원본 파일, 청크 번호, BM25 점수가 표시됩니다.

## 설치

**Python 3.11+**가 필요합니다.

```bash
git clone https://github.com/Xkongai/folder2kb.git
cd folder2kb
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

동작을 확인합니다.

```bash
folder2kb --version   # 0.1.0
```

## 빠른 시작

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

출력 예:

```text
$ folder2kb import ./docs
imported: 2  skipped: 0  failed: 0  (ignored unsupported: 0)
total: 2 docs, 3 chunks

$ folder2kb ask "退货政策"
[1] docs/sample.md  (chunk 0, score 2.811)
    # Acme 小店退货政策 / Acme Store Return Policy ## 退货政策 自签收之日起 30 天内，未使用且包装完好的商品可以申请无理由退货。…
```

`import`를 다시 실행하면 바뀌지 않은 파일은 `skipped`로 표시됩니다.

## 명령

| 명령 | 하는 일 |
| --- | --- |
| `folder2kb init [--force]` | `folder2kb.yaml`과 `.kb/`를 만듭니다(`--force`가 없으면 기존 설정은 덮어쓰지 않습니다). |
| `folder2kb import <path> [-v]` | 파일이나 폴더를 재귀적으로 가져오고 imported / skipped / failed 개수를 출력합니다. `-v`는 파일마다 나열합니다. |
| `folder2kb status` | 문서 수, 청크 수, 인덱스 경로, 마지막 가져오기 시각을 보여 줍니다. |
| `folder2kb ask "<query>" [-k N] [--width N]` | 출처 경로와 점수와 함께 top-k 청크를 출력합니다. `--width`는 청크마다 출력하는 문자 수를 제한합니다(기본 300, `0`이면 전체). |
| `folder2kb version` / `--version` | 버전을 출력합니다. |

종료 코드:

| 코드 | 의미 |
| --- | --- |
| `0` | 성공 |
| `1` | 오류(설정이 잘못됨, 저장소를 읽을 수 없음, 경로가 없음, 또는 한 번의 가져오기에서 모든 파일이 실패) |
| `2` | 빈 지식 베이스에서 `ask` — 먼저 `folder2kb import`를 실행하세요 |
| `3` | `ask`가 맞는 청크를 찾지 못함 |

## 지원 형식

| 확장자 | 파서 |
| --- | --- |
| `.md`, `.markdown` | UTF-8 텍스트(잘못된 바이트는 대체) |
| `.txt` | UTF-8 텍스트(잘못된 바이트는 대체) |
| `.pdf` | [PyMuPDF](https://pymupdf.readthedocs.io/)로 텍스트 추출(OCR 없음) |

그 밖의 파일은 "unsupported, ignored"로 표시되고 건너뜁니다. 숨김 파일과 폴더
(`.git`, `.venv`, `node_modules`, `.kb/` 저장소 자체, …)는 가져오지 않습니다.

## 설정

`folder2kb init`은 `folder2kb.yaml`을 씁니다([`folder2kb.yaml.example`](folder2kb.yaml.example) 참고):

```yaml
kb_dir: .kb          # where the knowledge base is stored (relative to this file)
chunk_size: 500      # max characters per chunk
chunk_overlap: 80    # characters shared between neighbouring chunks
top_k: 5             # default number of results for `ask`
```

| 키 | 기본값 | 설명 |
| --- | --- | --- |
| `kb_dir` | `.kb` | 지식 베이스가 저장되는 위치. `folder2kb.yaml` 기준 상대 경로입니다. |
| `chunk_size` | `500` | 청크당 최대 문자 수. |
| `chunk_overlap` | `80` | 이웃한 청크가 공유하는 문자 수. |
| `top_k` | `5` | `ask`의 기본 결과 수(`-k`로 바꿀 수 있음). |

folder2kb는 현재 디렉터리와 상위 디렉터리에서 `folder2kb.yaml`을 찾으므로
프로젝트의 어떤 하위 폴더에서든 명령을 실행할 수 있습니다. 설정 파일이 없으면 기본값을 사용합니다.

## 동작 방식

<img src="docs/images/how-it-works.png" alt="파일 → 파싱 → 청크 분할 → .kb/ → BM25 → 결과" width="100%">

```text
files ──► parse ──► chunk ──► .kb/ (manifest.json + chunks.jsonl) ──► BM25 ──► top-k results
```

1. **파싱** — `.md`/`.txt`는 UTF-8로 읽고, `.pdf` 페이지는 PyMuPDF로 추출합니다.
2. **청크 분할** — 재귀 문자 분할기가 문단, 줄, 문장 부호(중국어와 영어), 공백 순으로 잘라 `chunk_size`자 이하의 청크로 만들고, 청크 사이에 `chunk_overlap`자의 문맥을 둡니다.
3. **저장** — 문서 메타데이터(경로, SHA-256, mtime, 크기, 청크 수)는 `manifest.json`에, 청크는 `chunks.jsonl`에 들어갑니다. 쓰기는 원자적입니다.
4. **검색** — `ask`할 때마다 저장된 청크로 BM25 인덱스([rank-bm25](https://github.com/dorianbrown/rank_bm25))를 메모리에 다시 만듭니다. 문서와 질의에 같은 토크나이저를 씁니다.

## 사용 예

- **개인 노트.** Obsidian 보관함이나 Markdown 노트 폴더를 가리키면, 아무것도 올리지 않고 터미널에서 검색할 수 있습니다.
  ```bash
  cd ~/notes && folder2kb init && folder2kb import .
  folder2kb ask "docker compose healthcheck"
  ```
- **팀 매뉴얼과 FAQ.** 정책, SOP, 고객 응대 답변(Acme 예제처럼)이 있는 공유 폴더를 색인하고, 중국어와 영어가 섞인 글에서 해당 문단을 찾습니다.
  ```bash
  folder2kb import ./handbook
  folder2kb ask "发票怎么开" -k 3
  ```
- **오프라인 RAG 전처리.** folder2kb를 단순한 검색 계층으로 씁니다. 청크는 일반 `chunks.jsonl`에 있으므로 자체 스크립트에서 읽거나, `ask`의 top-k 결과를 이미 쓰는 LLM에 넘길 수 있습니다.
  ```bash
  folder2kb ask "refund timeline" -k 5 --width 0 > context.txt
  ```

## 로드맵과 한계

로드맵:

- [ ] 형식 추가: `.docx`, `.html`
- [ ] `folder2kb watch` — 파일이 바뀌면 증분 재가져오기
- [ ] 디스크에서 삭제된 문서 정리
- [ ] 선택 사항: OpenAI 호환 API로 임베딩(BM25와 벡터의 혼합 검색)
- [ ] 선택 사항: 검색된 청크를 두고 로컬 LLM과 대화(예: Ollama)
- [ ] 스크립트용 JSON 출력(`ask --json`)

현재 한계:

- **OCR 없음** — 텍스트 레이어가 없는 스캔 PDF는 검색할 텍스트를 만들지 못합니다.
- **아직 `.docx` / `.html` 미지원** — 먼저 Markdown이나 텍스트로 바꾸세요.
- **삭제된 파일은 정리되지 않음** — 디스크에서 파일을 지워도 아직은 인덱스에 남습니다.
- **`ask`는 호출할 때마다 메모리에서 BM25를 다시 만듭니다.** 개인과 팀 규모에서는 빠르지만, 수백만 청크용으로 설계되지 않았습니다.
- **키워드 검색이지 의미 검색이 아님** — BM25는 단어와 문자를 맞추므로, 공통 문자가 없는 동의어는 맞지 않습니다.

지금은 범위 밖: 웹 UI, 다중 사용자, 클라우드 동기화, 웹 크롤링.

## 기여

이슈와 풀 리퀘스트를 환영합니다! 개발 환경 구성과 테스트 실행(`pytest -q`)은 [CONTRIBUTING.md](CONTRIBUTING.md)를 보세요.

## 라이선스

[MIT](LICENSE) © 2026 Xkongai
