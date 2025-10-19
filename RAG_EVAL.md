# RAG & Évaluation

Ce document décrit la pile RAG (Retrieval-Augmented Generation) et le framework
d'évaluation utilisés par Agriculture Cameroun.

## Architecture RAG

```
┌────────────────────────────────────────────────────────────────┐
│                   Requête utilisateur                          │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│     root_agent (ADK) → dispatch vers sous-agent approprié      │
└──────────────────────┬─────────────────────────────────────────┘
                       │
          ┌────────────┴──────────────────┐
          ▼                               ▼
┌────────────────────┐       ┌──────────────────────────┐
│ Tools métier       │       │ retrieve_agricultural_   │
│ (simulations,      │       │ knowledge (RAG)          │
│ API externes…)     │       └───────────┬──────────────┘
└────────────────────┘                   │
                                         ▼
                        ┌───────────────────────────────┐
                        │ Retriever                     │
                        │ ├── Dense (Gemini embeddings) │
                        │ └── Hybrid (RRF: dense+BM25)  │
                        └───────────┬───────────────────┘
                                    ▼
                        ┌───────────────────────────────┐
                        │ ChromaDB (persistent)         │
                        │ Collection: agriculture_cmr   │
                        └───────────────────────────────┘
```

## Composants

| Fichier | Rôle |
|---------|------|
| `agriculture_cameroun/rag/embeddings.py` | Wrapper Gemini `text-embedding-004`, batché, retry |
| `agriculture_cameroun/rag/chunking.py` | Splitter récursif par séparateurs (pas de dépendance) |
| `agriculture_cameroun/rag/vector_store.py` | ChromaDB persistant, distance cosinus |
| `agriculture_cameroun/rag/retriever.py` | Dense + BM25 + fusion RRF |
| `agriculture_cameroun/rag/ingest.py` | Pipeline d'ingestion du corpus |
| `agriculture_cameroun/rag/tools.py` | Outil ADK exposé aux sous-agents |

## Ingestion du corpus

Le corpus agricole est sous `data/corpus/` en markdown avec front-matter YAML :

```markdown
---
topic: crops
crop: cacao
source: IRAD-MINADER
region: Centre,Sud
---

# Cacaoyer au Cameroun
…
```

Ingestion :

```bash
poetry run python -m agriculture_cameroun.rag.ingest --reset
```

## Évaluation

### Dataset doré

25 questions annotées dans `evaluation/golden.jsonl` couvrant les 5 topics
(crops, health, weather, economic, resources). Format JSONL :

```json
{"id": "q001", "question": "...", "ground_truth": "...", "expected_sources": ["crops/cacao.md"], "topic": "crops"}
```

### Métriques

**Retrieval** (déterministes, sans LLM) :
- `hit_rate` : au moins une source attendue dans le top-k
- `context_recall` : fraction des sources attendues récupérées
- `context_precision` : fraction des passages récupérés qui étaient pertinents
- `mrr` : mean reciprocal rank de la première source attendue

**Génération** (LLM-as-a-judge sur Gemini, prompt à barème 0-5 → normalisé [0,1]) :
- `faithfulness` : la réponse est-elle ancrée dans le contexte (pas d'hallucination) ?
- `answer_relevance` : la réponse adresse-t-elle la question vs. référence ?

**Similarité sémantique** :
- Cosinus entre embeddings `answer` et `ground_truth`

### Lancer une évaluation

```bash
# Évaluation en mode hybride, top_k=5
poetry run python -m evaluation.runner \
    --dataset evaluation/golden.jsonl \
    --output evaluation/reports/hybrid_k5.json \
    --mode hybrid --top-k 5

# Ablation : mode dense uniquement
poetry run python -m evaluation.runner \
    --dataset evaluation/golden.jsonl \
    --output evaluation/reports/dense_k5.json \
    --mode dense --top-k 5

# Génération du rapport comparatif
poetry run python -m evaluation.reporter \
    evaluation/reports/dense_k5.json \
    evaluation/reports/hybrid_k5.json \
    --output evaluation/reports/comparison.md
```

### Exemple de sortie

```
| Run        | Hit rate | Context recall | MRR  | Faithfulness | Relevance |
|------------|----------|----------------|------|--------------|-----------|
| dense_k5   | 0.88     | 0.76           | 0.81 | 0.84         | 0.78      |
| hybrid_k5  | 0.92     | 0.82           | 0.85 | 0.86         | 0.81      |
```

## Reproductibilité

- Embeddings : `models/text-embedding-004` (Gemini)
- Generation model (eval) : `gemini-2.0-flash-001`, température 0.2
- Judge : même modèle, température 0.0, response JSON strict
- Chunk size 800, overlap 120, séparateurs markdown-first
