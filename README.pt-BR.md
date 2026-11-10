<p align="center">
  <img src="docs/images/banner.png" alt="folder2kb — Um comando transforma uma pasta em uma base de conhecimento local." width="100%">
</p>

<h1 align="center">folder2kb</h1>

<p align="center">
  <b>Um comando transforma qualquer pasta de documentos em uma base de conhecimento local e consultável.</b><br>
  Busca BM25 offline em Markdown, texto e PDF — chinês e inglês, sem GPU e sem baixar modelos.
</p>

<p align="center">
  <a href="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml"><img src="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python 3.11+">
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <b>Português (Brasil)</b> | <a href="README.fr.md">Français</a> | <a href="README.de.md">Deutsch</a> | <a href="README.ko.md">한국어</a> | <a href="README.ru.md">Русский</a>
</p>

```bash
folder2kb import ~/notes
folder2kb ask "return policy for opened items"
```

O folder2kb percorre uma pasta, extrai o texto de arquivos Markdown, texto simples e PDF,
divide em trechos e deixa você pesquisar no terminal com BM25 —
totalmente offline, em chinês e inglês, sem GPU e sem baixar modelos.

## Conteúdo

- [Por que o folder2kb?](#por-que-o-folder2kb)
- [Demonstração](#demonstração)
- [Instalação](#instalação)
- [Início rápido](#início-rápido)
- [Comandos](#comandos)
- [Formatos compatíveis](#formatos-compatíveis)
- [Configuração](#configuração)
- [Como funciona](#como-funciona)
- [Casos de uso](#casos-de-uso)
- [Roteiro e limitações](#roteiro-e-limitações)
- [Como contribuir](#como-contribuir)
- [Licença](#licença)

## Por que o folder2kb?

| | |
| --- | --- |
| 🔒 **Offline em primeiro lugar** | Tudo fica em uma pasta `.kb/` ao lado da sua configuração. Sem chamadas de rede, sem chaves de API, sem telemetria. |
| 🀄 **Chinês e inglês de fábrica** | Um tokenizador integrado trata palavras latinas e texto CJK (unigramas e bigramas de caracteres), então consultas como `退货政策` funcionam direto — sem jieba e sem dicionários. |
| 🪶 **Pequeno e rápido de instalar** | Sem PyTorch, sem modelo de embeddings, sem banco de dados vetorial. Quatro dependências pequenas. |
| ♻️ **Incremental** | Executar `import` de novo ignora arquivos cujo conteúdo não mudou (SHA-256). |
| 📄 **Armazenamento em arquivos simples** | O índice é um `manifest.json` + `chunks.jsonl` legíveis; fácil de inspecionar, fazer backup ou alimentar o seu próprio pipeline de RAG. |

## Demonstração

As capturas abaixo são a saída real de executar o folder2kb 0.1.0 depois de
`folder2kb import ./docs`. Os arquivos de exemplo são uma política de devolução fictícia da “Acme 小店 / Acme Store”
(Markdown) e um FAQ de envio (texto simples) — os mesmos documentos também
estão em [`tests/fixtures/`](tests/fixtures).

**1. Criar uma base de conhecimento e importar uma pasta**

<img src="docs/images/demo-import.png" alt="saída de folder2kb init e folder2kb import" width="100%">

**2. Ver o que tem dentro**

<img src="docs/images/demo-status.png" alt="saída de folder2kb status" width="100%">

**3. Perguntar em chinês — `退货政策` (“política de devolução”) encontra o trecho certo primeiro**

<img src="docs/images/demo-ask.png" alt="saída de folder2kb ask 退货政策" width="100%">

A melhor correspondência é a seção bilíngue da política de devolução (pontuação 2.811); correspondências mais fracas vêm
com pontuações menores. Cada resultado mostra o arquivo de origem, o número do trecho e a pontuação BM25.

## Instalação

Requer **Python 3.11+**.

```bash
git clone https://github.com/Xkongai/folder2kb.git
cd folder2kb
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Confira se funciona:

```bash
folder2kb --version   # 0.1.0
```

## Início rápido

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

Exemplo de saída:

```text
$ folder2kb import ./docs
imported: 2  skipped: 0  failed: 0  (ignored unsupported: 0)
total: 2 docs, 3 chunks

$ folder2kb ask "退货政策"
[1] docs/sample.md  (chunk 0, score 2.811)
    # Acme 小店退货政策 / Acme Store Return Policy ## 退货政策 自签收之日起 30 天内，未使用且包装完好的商品可以申请无理由退货。…
```

Rode `import` de novo e os arquivos inalterados aparecem como `skipped`.

## Comandos

| Comando | O que faz |
| --- | --- |
| `folder2kb init [--force]` | Cria `folder2kb.yaml` e `.kb/` (não sobrescreve uma configuração existente sem `--force`). |
| `folder2kb import <path> [-v]` | Importa um arquivo ou uma pasta de forma recursiva; mostra as contagens de imported / skipped / failed. `-v` lista cada arquivo. |
| `folder2kb status` | Mostra a quantidade de documentos, a quantidade de trechos, o caminho do índice e a hora da última importação. |
| `folder2kb ask "<query>" [-k N] [--width N]` | Mostra os trechos top-k com o caminho de origem e a pontuação. `--width` limita os caracteres impressos por trecho (padrão 300, `0` = completo). |
| `folder2kb version` / `--version` | Mostra a versão. |

Códigos de saída:

| Código | Significado |
| --- | --- |
| `0` | Sucesso |
| `1` | Erro (configuração inválida, armazenamento ilegível, caminho ausente, ou todos os arquivos de uma importação falharam) |
| `2` | `ask` em uma base de conhecimento vazia — execute `folder2kb import` antes |
| `3` | `ask` não encontrou trechos correspondentes |

## Formatos compatíveis

| Extensão | Analisador |
| --- | --- |
| `.md`, `.markdown` | Texto UTF-8 (bytes inválidos são substituídos) |
| `.txt` | Texto UTF-8 (bytes inválidos são substituídos) |
| `.pdf` | Extração de texto com [PyMuPDF](https://pymupdf.readthedocs.io/) (sem OCR) |

Os outros arquivos são listados como "unsupported, ignored" e ignorados. Arquivos e pastas ocultos
(`.git`, `.venv`, `node_modules`, o próprio armazenamento `.kb/`, …) nunca são importados.

## Configuração

`folder2kb init` grava `folder2kb.yaml` (veja [`folder2kb.yaml.example`](folder2kb.yaml.example)):

```yaml
kb_dir: .kb          # where the knowledge base is stored (relative to this file)
chunk_size: 500      # max characters per chunk
chunk_overlap: 80    # characters shared between neighbouring chunks
top_k: 5             # default number of results for `ask`
```

| Chave | Padrão | Descrição |
| --- | --- | --- |
| `kb_dir` | `.kb` | Onde a base de conhecimento fica armazenada, em relação a `folder2kb.yaml`. |
| `chunk_size` | `500` | Máximo de caracteres por trecho. |
| `chunk_overlap` | `80` | Caracteres compartilhados entre trechos vizinhos. |
| `top_k` | `5` | Número padrão de resultados de `ask` (substitua com `-k`). |

O folder2kb procura `folder2kb.yaml` no diretório atual e nos pais, então você pode
rodar os comandos a partir de qualquer subpasta do projeto. Se não houver configuração, os padrões são usados.

## Como funciona

<img src="docs/images/how-it-works.png" alt="arquivos → analisar → dividir → .kb/ → BM25 → resultados" width="100%">

```text
files ──► parse ──► chunk ──► .kb/ (manifest.json + chunks.jsonl) ──► BM25 ──► top-k results
```

1. **Analisar** — `.md`/`.txt` são lidos como UTF-8; as páginas `.pdf` são extraídas com PyMuPDF.
2. **Dividir** — um divisor recursivo de caracteres quebra o texto em parágrafos, depois em linhas, depois na pontuação de fim de frase (chinês e inglês) e então em espaços, em trechos de ≤ `chunk_size` caracteres com `chunk_overlap` caracteres de contexto.
3. **Armazenar** — os metadados do documento (caminho, SHA-256, mtime, tamanho, quantidade de trechos) vão para `manifest.json`; os trechos vão para `chunks.jsonl`. As gravações são atômicas.
4. **Buscar** — no `ask`, um índice BM25 ([rank-bm25](https://github.com/dorianbrown/rank_bm25)) é reconstruído em memória a partir dos trechos armazenados, usando o mesmo tokenizador para documentos e consultas.

## Casos de uso

- **Notas pessoais.** Aponte para um vault do Obsidian ou uma pasta de notas Markdown e pesquise no terminal sem enviar nada.
  ```bash
  cd ~/notes && folder2kb init && folder2kb import .
  folder2kb ask "docker compose healthcheck"
  ```
- **Manuais e FAQs da equipe.** Indexe uma pasta compartilhada de políticas, SOPs ou respostas de atendimento (como o exemplo da Acme) e encontre o parágrafo relevante em texto misto chinês/inglês.
  ```bash
  folder2kb import ./handbook
  folder2kb ask "发票怎么开" -k 3
  ```
- **Pré-processamento de RAG offline.** Use o folder2kb como uma camada simples de recuperação: os trechos ficam em um `chunks.jsonl` simples, então você pode lê-los no seu próprio script ou passar os resultados top-k do `ask` para o LLM que você já usa.
  ```bash
  folder2kb ask "refund timeline" -k 5 --width 0 > context.txt
  ```

## Roteiro e limitações

Roteiro:

- [ ] Mais formatos: `.docx`, `.html`
- [ ] `folder2kb watch` — reimportação incremental quando os arquivos mudam
- [ ] Remover documentos apagados do disco
- [ ] Embeddings opcionais via qualquer API compatível com OpenAI (busca híbrida BM25 + vetorial)
- [ ] Chat opcional com um LLM local sobre os trechos recuperados (por exemplo, Ollama)
- [ ] Saída JSON para scripts (`ask --json`)

Limitações atuais:

- **Sem OCR** — PDFs digitalizados sem camada de texto não produzem texto pesquisável.
- **Ainda sem `.docx` / `.html`** — converta-os antes para Markdown ou texto.
- **Arquivos excluídos não são removidos** — apagar um arquivo do disco ainda não o tira do índice.
- **`ask` reconstrói o BM25 em memória** a cada chamada. Isso é rápido para acervos pessoais e de equipe, mas não foi feito para milhões de trechos.
- **Busca por palavras-chave, não semântica** — o BM25 casa palavras e caracteres, então sinônimos que não compartilham caracteres não coincidem.

Fora de escopo por enquanto: interface web, multiusuário, sincronização na nuvem, rastreamento da web.

## Como contribuir

Issues e pull requests são bem-vindos! Veja [CONTRIBUTING.md](CONTRIBUTING.md) para o ambiente de desenvolvimento
e como executar os testes (`pytest -q`).

## Licença

[MIT](LICENSE) © 2026 Xkongai
