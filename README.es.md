<p align="center">
  <img src="docs/images/banner.png" alt="folder2kb — Un comando convierte una carpeta en una base de conocimiento local." width="100%">
</p>

<h1 align="center">folder2kb</h1>

<p align="center">
  <b>Un comando convierte cualquier carpeta de documentos en una base de conocimiento local y consultable.</b><br>
  Búsqueda BM25 sin conexión sobre Markdown, texto y PDF — chino e inglés, sin GPU y sin descargar modelos.
</p>

<p align="center">
  <a href="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml"><img src="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python 3.11+">
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.ja.md">日本語</a> | <b>Español</b> | <a href="README.pt-BR.md">Português (Brasil)</a> | <a href="README.fr.md">Français</a> | <a href="README.de.md">Deutsch</a> | <a href="README.ko.md">한국어</a> | <a href="README.ru.md">Русский</a>
</p>

```bash
folder2kb import ~/notes
folder2kb ask "return policy for opened items"
```

folder2kb recorre una carpeta, extrae el texto de archivos Markdown, texto plano y PDF,
lo divide en fragmentos y te permite buscarlo desde la terminal con BM25 —
totalmente sin conexión, en chino e inglés, sin GPU y sin descargar modelos.

## Contenido

- [¿Por qué folder2kb?](#por-qué-folder2kb)
- [Demostración](#demostración)
- [Instalación](#instalación)
- [Inicio rápido](#inicio-rápido)
- [Comandos](#comandos)
- [Formatos compatibles](#formatos-compatibles)
- [Configuración](#configuración)
- [Cómo funciona](#cómo-funciona)
- [Casos de uso](#casos-de-uso)
- [Hoja de ruta y limitaciones](#hoja-de-ruta-y-limitaciones)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

## ¿Por qué folder2kb?

| | |
| --- | --- |
| 🔒 **Sin conexión primero** | Todo vive en una carpeta `.kb/` junto a tu configuración. Sin llamadas de red, sin claves de API, sin telemetría. |
| 🀄 **Chino e inglés listos para usar** | Un tokenizador integrado maneja palabras latinas y texto CJK (unigramas y bigramas de caracteres), así que consultas como `退货政策` funcionan directamente — sin jieba y sin diccionarios. |
| 🪶 **Pequeño y rápido de instalar** | Sin PyTorch, sin modelo de embeddings, sin base de datos vectorial. Cuatro dependencias pequeñas. |
| ♻️ **Incremental** | Volver a ejecutar `import` omite los archivos cuyo contenido no ha cambiado (SHA-256). |
| 📄 **Almacenamiento en archivos planos** | El índice es un `manifest.json` + `chunks.jsonl` legibles; fácil de inspeccionar, respaldar o alimentar tu propio pipeline de RAG. |

## Demostración

Las capturas de abajo son la salida real de ejecutar folder2kb 0.1.0 tras
`folder2kb import ./docs`. Los archivos de ejemplo son una política de devoluciones ficticia de “Acme 小店 / Acme Store”
(Markdown) y una FAQ de envíos (texto plano) — los mismos documentos también
están en [`tests/fixtures/`](tests/fixtures).

**1. Crear una base de conocimiento e importar una carpeta**

<img src="docs/images/demo-import.png" alt="salida de folder2kb init y folder2kb import" width="100%">

**2. Ver qué hay dentro**

<img src="docs/images/demo-status.png" alt="salida de folder2kb status" width="100%">

**3. Preguntar en chino — `退货政策` (“política de devoluciones”) encuentra primero el fragmento correcto**

<img src="docs/images/demo-ask.png" alt="salida de folder2kb ask 退货政策" width="100%">

La mejor coincidencia es la sección bilingüe de la política de devoluciones (puntuación 2.811); las coincidencias más débiles siguen
con puntuaciones más bajas. Cada resultado muestra el archivo de origen, el número de fragmento y la puntuación BM25.

## Instalación

Requiere **Python 3.11+**.

```bash
git clone https://github.com/Xkongai/folder2kb.git
cd folder2kb
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Comprueba que funciona:

```bash
folder2kb --version   # 0.1.0
```

## Inicio rápido

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

Ejemplo de salida:

```text
$ folder2kb import ./docs
imported: 2  skipped: 0  failed: 0  (ignored unsupported: 0)
total: 2 docs, 3 chunks

$ folder2kb ask "退货政策"
[1] docs/sample.md  (chunk 0, score 2.811)
    # Acme 小店退货政策 / Acme Store Return Policy ## 退货政策 自签收之日起 30 天内，未使用且包装完好的商品可以申请无理由退货。…
```

Vuelve a ejecutar `import` y los archivos sin cambios se informan como `skipped`.

## Comandos

| Comando | Qué hace |
| --- | --- |
| `folder2kb init [--force]` | Crea `folder2kb.yaml` y `.kb/` (no sobrescribe una configuración existente sin `--force`). |
| `folder2kb import <path> [-v]` | Importa un archivo o una carpeta de forma recursiva; muestra los recuentos de imported / skipped / failed. `-v` lista cada archivo. |
| `folder2kb status` | Muestra el número de documentos, el número de fragmentos, la ruta del índice y la hora de la última importación. |
| `folder2kb ask "<query>" [-k N] [--width N]` | Muestra los fragmentos top-k con la ruta de origen y la puntuación. `--width` limita los caracteres impresos por fragmento (predeterminado 300, `0` = completo). |
| `folder2kb version` / `--version` | Muestra la versión. |

Códigos de salida:

| Código | Significado |
| --- | --- |
| `0` | Éxito |
| `1` | Error (configuración incorrecta, almacén ilegible, ruta inexistente, o todos los archivos de una importación fallaron) |
| `2` | `ask` sobre una base de conocimiento vacía — ejecuta primero `folder2kb import` |
| `3` | `ask` no encontró fragmentos coincidentes |

## Formatos compatibles

| Extensión | Analizador |
| --- | --- |
| `.md`, `.markdown` | Texto UTF-8 (los bytes no válidos se sustituyen) |
| `.txt` | Texto UTF-8 (los bytes no válidos se sustituyen) |
| `.pdf` | Extracción de texto con [PyMuPDF](https://pymupdf.readthedocs.io/) (sin OCR) |

Los demás archivos se indican como "unsupported, ignored" y se omiten. Los archivos y carpetas ocultos
(`.git`, `.venv`, `node_modules`, el propio almacén `.kb/`, …) nunca se importan.

## Configuración

`folder2kb init` escribe `folder2kb.yaml` (consulta [`folder2kb.yaml.example`](folder2kb.yaml.example)):

```yaml
kb_dir: .kb          # where the knowledge base is stored (relative to this file)
chunk_size: 500      # max characters per chunk
chunk_overlap: 80    # characters shared between neighbouring chunks
top_k: 5             # default number of results for `ask`
```

| Clave | Predeterminado | Descripción |
| --- | --- | --- |
| `kb_dir` | `.kb` | Dónde se guarda la base de conocimiento, respecto de `folder2kb.yaml`. |
| `chunk_size` | `500` | Máximo de caracteres por fragmento. |
| `chunk_overlap` | `80` | Caracteres compartidos entre fragmentos vecinos. |
| `top_k` | `5` | Número predeterminado de resultados de `ask` (se cambia con `-k`). |

folder2kb busca `folder2kb.yaml` en el directorio actual y en sus padres, así que puedes
ejecutar los comandos desde cualquier subcarpeta de tu proyecto. Si no hay configuración, se usan los valores predeterminados.

## Cómo funciona

<img src="docs/images/how-it-works.png" alt="archivos → analizar → fragmentar → .kb/ → BM25 → resultados" width="100%">

```text
files ──► parse ──► chunk ──► .kb/ (manifest.json + chunks.jsonl) ──► BM25 ──► top-k results
```

1. **Analizar** — `.md`/`.txt` se leen como UTF-8; las páginas `.pdf` se extraen con PyMuPDF.
2. **Fragmentar** — un divisor recursivo de caracteres parte el texto en párrafos, luego en líneas, luego en la puntuación de fin de oración (chino e inglés) y después en espacios, en fragmentos de ≤ `chunk_size` caracteres con `chunk_overlap` caracteres de contexto.
3. **Almacenar** — los metadatos del documento (ruta, SHA-256, mtime, tamaño, número de fragmentos) van a `manifest.json`; los fragmentos van a `chunks.jsonl`. Las escrituras son atómicas.
4. **Buscar** — en `ask`, se reconstruye en memoria un índice BM25 ([rank-bm25](https://github.com/dorianbrown/rank_bm25)) a partir de los fragmentos almacenados, con el mismo tokenizador para los documentos y las consultas.

## Casos de uso

- **Notas personales.** Apúntalo a un vault de Obsidian o a una carpeta de notas Markdown y búscalas desde la terminal sin subir nada.
  ```bash
  cd ~/notes && folder2kb init && folder2kb import .
  folder2kb ask "docker compose healthcheck"
  ```
- **Manuales y preguntas frecuentes del equipo.** Indexa una carpeta compartida de políticas, SOP o respuestas de atención al cliente (como el ejemplo de Acme) y encuentra el párrafo relevante en texto mixto chino/inglés.
  ```bash
  folder2kb import ./handbook
  folder2kb ask "发票怎么开" -k 3
  ```
- **Preprocesamiento de RAG sin conexión.** Usa folder2kb como una capa de recuperación sencilla: los fragmentos viven en un `chunks.jsonl` plano, así que puedes leerlos desde tu propio script o pasar los resultados top-k de `ask` al LLM que ya uses.
  ```bash
  folder2kb ask "refund timeline" -k 5 --width 0 > context.txt
  ```

## Hoja de ruta y limitaciones

Hoja de ruta:

- [ ] Más formatos: `.docx`, `.html`
- [ ] `folder2kb watch` — reimportación incremental cuando cambian los archivos
- [ ] Retirar los documentos borrados del disco
- [ ] Embeddings opcionales mediante cualquier API compatible con OpenAI (búsqueda híbrida BM25 + vectorial)
- [ ] Chat opcional con un LLM local sobre los fragmentos recuperados (p. ej. Ollama)
- [ ] Salida JSON para scripts (`ask --json`)

Limitaciones actuales:

- **Sin OCR** — los PDF escaneados sin capa de texto no producen texto buscable.
- **Aún no hay `.docx` / `.html`** — conviértelos primero a Markdown o a texto.
- **Los archivos eliminados no se depuran** — quitar un archivo del disco todavía no lo quita del índice.
- **`ask` reconstruye BM25 en memoria** en cada llamada. Es rápido para colecciones personales y de tamaño de equipo, pero no está pensado para millones de fragmentos.
- **Búsqueda por palabras clave, no semántica** — BM25 compara palabras y caracteres, así que los sinónimos que no comparten caracteres no coinciden.

Fuera de alcance por ahora: interfaz web, multiusuario, sincronización en la nube, rastreo web.

## Contribuir

¡Las issues y las pull requests son bienvenidas! Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para el entorno de desarrollo
y cómo ejecutar las pruebas (`pytest -q`).

## Licencia

[MIT](LICENSE) © 2026 Xkongai
