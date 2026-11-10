<p align="center">
  <img src="docs/images/banner.png" alt="folder2kb — Une commande transforme un dossier en base de connaissances locale." width="100%">
</p>

<h1 align="center">folder2kb</h1>

<p align="center">
  <b>Une commande transforme n'importe quel dossier de documents en une base de connaissances locale et interrogeable.</b><br>
  Recherche BM25 hors ligne sur Markdown, texte et PDF — chinois et anglais, sans GPU, sans téléchargement de modèle.
</p>

<p align="center">
  <a href="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml"><img src="https://github.com/Xkongai/folder2kb/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python 3.11+">
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <a href="README.pt-BR.md">Português (Brasil)</a> | <b>Français</b> | <a href="README.de.md">Deutsch</a> | <a href="README.ko.md">한국어</a> | <a href="README.ru.md">Русский</a>
</p>

```bash
folder2kb import ~/notes
folder2kb ask "return policy for opened items"
```

folder2kb parcourt un dossier, extrait le texte des fichiers Markdown, texte brut et PDF,
le découpe en fragments et vous permet de le rechercher depuis le terminal avec BM25 —
entièrement hors ligne, en chinois et en anglais, sans GPU et sans téléchargement de modèle.

## Sommaire

- [Pourquoi folder2kb ?](#pourquoi-folder2kb-)
- [Démo](#démo)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Commandes](#commandes)
- [Formats pris en charge](#formats-pris-en-charge)
- [Configuration](#configuration)
- [Fonctionnement](#fonctionnement)
- [Cas d'usage](#cas-dusage)
- [Feuille de route et limites](#feuille-de-route-et-limites)
- [Contribuer](#contribuer)
- [Licence](#licence)

## Pourquoi folder2kb ?

| | |
| --- | --- |
| 🔒 **Hors ligne d'abord** | Tout vit dans un dossier `.kb/` à côté de votre configuration. Aucun appel réseau, aucune clé d'API, aucune télémétrie. |
| 🀄 **Chinois et anglais prêts à l'emploi** | Un tokenizer intégré traite les mots latins et le texte CJK (unigrammes et bigrammes de caractères), donc des requêtes comme `退货政策` fonctionnent directement — sans jieba, sans dictionnaires. |
| 🪶 **Petit et rapide à installer** | Pas de PyTorch, pas de modèle d'embeddings, pas de base de données vectorielle. Quatre petites dépendances. |
| ♻️ **Incrémental** | Relancer `import` ignore les fichiers dont le contenu n'a pas changé (SHA-256). |
| 📄 **Stockage en fichiers lisibles** | L'index est un `manifest.json` + `chunks.jsonl` lisibles ; facile à inspecter, à sauvegarder ou à injecter dans votre propre pipeline RAG. |

## Démo

Les captures ci-dessous sont la sortie réelle de folder2kb 0.1.0 après
`folder2kb import ./docs`. Les fichiers d'exemple sont une politique de retour fictive de “Acme 小店 / Acme Store”
(Markdown) et une FAQ d'expédition (texte brut) — les mêmes documents se trouvent aussi
dans [`tests/fixtures/`](tests/fixtures).

**1. Créer une base de connaissances et importer un dossier**

<img src="docs/images/demo-import.png" alt="sortie de folder2kb init et folder2kb import" width="100%">

**2. Voir ce qu'il contient**

<img src="docs/images/demo-status.png" alt="sortie de folder2kb status" width="100%">

**3. Interroger en chinois — `退货政策` (« politique de retour ») trouve d'abord le bon fragment**

<img src="docs/images/demo-ask.png" alt="sortie de folder2kb ask 退货政策" width="100%">

La meilleure correspondance est la section bilingue de la politique de retour (score 2.811) ; les correspondances plus faibles suivent
avec des scores plus bas. Chaque résultat affiche le fichier source, le numéro de fragment et le score BM25.

## Installation

Nécessite **Python 3.11+**.

```bash
git clone https://github.com/Xkongai/folder2kb.git
cd folder2kb
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Vérifiez que cela fonctionne :

```bash
folder2kb --version   # 0.1.0
```

## Démarrage rapide

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

Exemple de sortie :

```text
$ folder2kb import ./docs
imported: 2  skipped: 0  failed: 0  (ignored unsupported: 0)
total: 2 docs, 3 chunks

$ folder2kb ask "退货政策"
[1] docs/sample.md  (chunk 0, score 2.811)
    # Acme 小店退货政策 / Acme Store Return Policy ## 退货政策 自签收之日起 30 天内，未使用且包装完好的商品可以申请无理由退货。…
```

Relancez `import` : les fichiers inchangés sont signalés comme `skipped`.

## Commandes

| Commande | Ce qu'elle fait |
| --- | --- |
| `folder2kb init [--force]` | Crée `folder2kb.yaml` et `.kb/` (n'écrase pas une configuration existante sans `--force`). |
| `folder2kb import <path> [-v]` | Importe un fichier ou un dossier de façon récursive ; affiche les nombres imported / skipped / failed. `-v` liste chaque fichier. |
| `folder2kb status` | Affiche le nombre de documents, le nombre de fragments, le chemin de l'index et l'heure du dernier import. |
| `folder2kb ask "<query>" [-k N] [--width N]` | Affiche les fragments top-k avec le chemin source et le score. `--width` limite les caractères affichés par fragment (300 par défaut, `0` = intégral). |
| `folder2kb version` / `--version` | Affiche la version. |

Codes de sortie :

| Code | Signification |
| --- | --- |
| `0` | Succès |
| `1` | Erreur (configuration incorrecte, stockage illisible, chemin manquant, ou échec de tous les fichiers d'un import) |
| `2` | `ask` sur une base de connaissances vide — lancez d'abord `folder2kb import` |
| `3` | `ask` n'a trouvé aucun fragment correspondant |

## Formats pris en charge

| Extension | Analyseur |
| --- | --- |
| `.md`, `.markdown` | Texte UTF-8 (les octets invalides sont remplacés) |
| `.txt` | Texte UTF-8 (les octets invalides sont remplacés) |
| `.pdf` | Extraction de texte avec [PyMuPDF](https://pymupdf.readthedocs.io/) (sans OCR) |

Les autres fichiers sont signalés comme "unsupported, ignored" et ignorés. Les fichiers et dossiers cachés
(`.git`, `.venv`, `node_modules`, le stockage `.kb/` lui-même, …) ne sont jamais importés.

## Configuration

`folder2kb init` écrit `folder2kb.yaml` (voir [`folder2kb.yaml.example`](folder2kb.yaml.example)) :

```yaml
kb_dir: .kb          # where the knowledge base is stored (relative to this file)
chunk_size: 500      # max characters per chunk
chunk_overlap: 80    # characters shared between neighbouring chunks
top_k: 5             # default number of results for `ask`
```

| Clé | Défaut | Description |
| --- | --- | --- |
| `kb_dir` | `.kb` | Emplacement de la base de connaissances, relatif à `folder2kb.yaml`. |
| `chunk_size` | `500` | Nombre maximal de caractères par fragment. |
| `chunk_overlap` | `80` | Caractères partagés entre fragments voisins. |
| `top_k` | `5` | Nombre de résultats de `ask` par défaut (à remplacer avec `-k`). |

folder2kb cherche `folder2kb.yaml` dans le répertoire courant et ses parents, vous pouvez donc
lancer les commandes depuis n'importe quel sous-dossier du projet. S'il n'y a pas de configuration, les valeurs par défaut sont utilisées.

## Fonctionnement

<img src="docs/images/how-it-works.png" alt="fichiers → analyser → découper → .kb/ → BM25 → résultats" width="100%">

```text
files ──► parse ──► chunk ──► .kb/ (manifest.json + chunks.jsonl) ──► BM25 ──► top-k results
```

1. **Analyser** — `.md`/`.txt` sont lus en UTF-8 ; les pages `.pdf` sont extraites avec PyMuPDF.
2. **Découper** — un découpeur récursif de caractères coupe le texte aux paragraphes, puis aux lignes, puis à la ponctuation de fin de phrase (chinois et anglais), puis aux espaces, en fragments de ≤ `chunk_size` caractères avec `chunk_overlap` caractères de contexte.
3. **Stocker** — les métadonnées du document (chemin, SHA-256, mtime, taille, nombre de fragments) vont dans `manifest.json` ; les fragments vont dans `chunks.jsonl`. Les écritures sont atomiques.
4. **Rechercher** — lors d'un `ask`, un index BM25 ([rank-bm25](https://github.com/dorianbrown/rank_bm25)) est reconstruit en mémoire à partir des fragments stockés, avec le même tokenizer pour les documents et les requêtes.

## Cas d'usage

- **Notes personnelles.** Pointez-le vers un coffre Obsidian ou un dossier de notes Markdown et recherchez-les depuis le terminal sans rien envoyer.
  ```bash
  cd ~/notes && folder2kb init && folder2kb import .
  folder2kb ask "docker compose healthcheck"
  ```
- **Manuels et FAQ d'équipe.** Indexez un dossier partagé de politiques, de SOP ou de réponses du service client (comme l'exemple Acme) et trouvez le paragraphe pertinent dans un texte mélangeant chinois et anglais.
  ```bash
  folder2kb import ./handbook
  folder2kb ask "发票怎么开" -k 3
  ```
- **Prétraitement RAG hors ligne.** Utilisez folder2kb comme une couche de recherche simple : les fragments vivent dans un `chunks.jsonl` lisible, vous pouvez donc les lire depuis votre propre script, ou passer les résultats top-k de `ask` au LLM que vous utilisez déjà.
  ```bash
  folder2kb ask "refund timeline" -k 5 --width 0 > context.txt
  ```

## Feuille de route et limites

Feuille de route :

- [ ] Davantage de formats : `.docx`, `.html`
- [ ] `folder2kb watch` — réimport incrémental lorsque les fichiers changent
- [ ] Retirer les documents supprimés du disque
- [ ] Embeddings facultatifs via n'importe quelle API compatible OpenAI (recherche hybride BM25 + vectorielle)
- [ ] Discussion facultative avec un LLM local à partir des fragments retrouvés (p. ex. Ollama)
- [ ] Sortie JSON pour les scripts (`ask --json`)

Limites actuelles :

- **Pas d'OCR** — les PDF numérisés sans couche de texte ne produisent aucun texte recherchable.
- **Pas encore de `.docx` / `.html`** — convertissez-les d'abord en Markdown ou en texte.
- **Les fichiers supprimés ne sont pas retirés** — enlever un fichier du disque ne le retire pas encore de l'index.
- **`ask` reconstruit BM25 en mémoire** à chaque appel. C'est rapide pour des collections personnelles ou d'équipe, mais ce n'est pas conçu pour des millions de fragments.
- **Recherche par mots-clés, pas sémantique** — BM25 rapproche des mots et des caractères, donc les synonymes qui ne partagent aucun caractère ne correspondent pas.

Hors périmètre pour l'instant : interface web, multi-utilisateur, synchronisation cloud, exploration du web.

## Contribuer

Les issues et les pull requests sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour l'environnement de développement
et la façon de lancer les tests (`pytest -q`).

## Licence

[MIT](LICENSE) © 2026 Xkongai
