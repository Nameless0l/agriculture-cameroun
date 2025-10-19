# Copyright 2025 Agriculture Cameroun

"""Retriever RAG avec mode dense et mode hybride optionnel (BM25 + dense).

Le reranking hybride se fait par Reciprocal Rank Fusion — simple et robuste.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence

from .embeddings import GeminiEmbedder
from .vector_store import SearchHit, VectorStore, get_vector_store


@dataclass
class RetrievalResult:
    text: str
    source: str
    score: float
    metadata: dict


class Retriever:
    def __init__(
        self,
        vector_store: VectorStore | None = None,
        embedder: GeminiEmbedder | None = None,
    ):
        self.vector_store = vector_store or get_vector_store()
        self.embedder = embedder or GeminiEmbedder()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: dict | None = None,
        mode: str = "dense",
    ) -> list[RetrievalResult]:
        dense_hits = self._dense(query, top_k * 2, filters)
        if mode == "dense":
            hits = dense_hits[:top_k]
        elif mode == "hybrid":
            hits = self._fuse(dense_hits, self._bm25(query, dense_hits, top_k * 2))[:top_k]
        else:
            raise ValueError(f"mode inconnu: {mode}")
        return [
            RetrievalResult(
                text=h.text,
                source=h.metadata.get("source", "unknown"),
                score=h.score,
                metadata=h.metadata,
            )
            for h in hits
        ]

    def _dense(self, query: str, top_k: int, filters: dict | None) -> list[SearchHit]:
        vec = self.embedder.embed_query(query)
        return self.vector_store.query(vec, top_k=top_k, where=filters)

    def _bm25(self, query: str, candidates: list[SearchHit], top_k: int) -> list[SearchHit]:
        # BM25 appliqué uniquement sur les candidats denses — évite d'indexer
        # tout le corpus une seconde fois pour un projet de cette taille.
        if not candidates:
            return []
        tokenized_docs = [_tokenize(h.text) for h in candidates]
        tokenized_query = _tokenize(query)
        scores = _bm25_scores(tokenized_query, tokenized_docs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [hit for hit, _ in ranked[:top_k]]

    def _fuse(
        self, dense: Iterable[SearchHit], sparse: Iterable[SearchHit], k: int = 60
    ) -> list[SearchHit]:
        dense_list = list(dense)
        sparse_list = list(sparse)
        fused: dict[str, tuple[SearchHit, float]] = {}
        for rank, hit in enumerate(dense_list):
            key = hit.text
            fused[key] = (hit, fused.get(key, (hit, 0.0))[1] + 1.0 / (k + rank))
        for rank, hit in enumerate(sparse_list):
            key = hit.text
            prev = fused.get(key, (hit, 0.0))
            fused[key] = (prev[0], prev[1] + 1.0 / (k + rank))
        return [h for h, _ in sorted(fused.values(), key=lambda x: x[1], reverse=True)]


_TOKEN_RE = re.compile(r"\w+", flags=re.UNICODE)


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def _bm25_scores(
    query_tokens: Sequence[str],
    docs: Sequence[Sequence[str]],
    k1: float = 1.5,
    b: float = 0.75,
) -> list[float]:
    n = len(docs)
    if n == 0:
        return []
    avgdl = sum(len(d) for d in docs) / n
    df: Counter[str] = Counter()
    for doc in docs:
        df.update(set(doc))
    idf = {
        term: math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5)) for term in df
    }
    scores: list[float] = []
    for doc in docs:
        tf = Counter(doc)
        dl = len(doc)
        score = 0.0
        for term in query_tokens:
            if term not in tf:
                continue
            numerator = tf[term] * (k1 + 1)
            denominator = tf[term] + k1 * (1 - b + b * dl / avgdl)
            score += idf.get(term, 0.0) * numerator / denominator
        scores.append(score)
    return scores
