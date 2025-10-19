# Copyright 2025 Agriculture Cameroun

"""Embedder Gemini pour le RAG.

Utilise `text-embedding-004` de Google, aligné avec le reste de la stack Gemini.
Batchés côté client pour rester sous les quotas et accélérer l'ingestion.
"""

from __future__ import annotations

import os
import time
from typing import Iterable, Sequence

import google.generativeai as genai

_DEFAULT_MODEL = "models/gemini-embedding-001"
_BATCH_SIZE = 100


class GeminiEmbedder:
    """Wrapper minimal autour de l'API d'embeddings Gemini."""

    def __init__(self, model: str = _DEFAULT_MODEL, api_key: str | None = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY manquant dans l'environnement.")
        genai.configure(api_key=api_key)
        self.model = model

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return list(self._embed(texts, task_type="retrieval_document"))

    def embed_query(self, text: str) -> list[float]:
        return next(iter(self._embed([text], task_type="retrieval_query")))

    def _embed(self, texts: Iterable[str], task_type: str) -> Iterable[list[float]]:
        batch: list[str] = []
        for text in texts:
            batch.append(text)
            if len(batch) >= _BATCH_SIZE:
                yield from self._embed_batch(batch, task_type)
                batch = []
        if batch:
            yield from self._embed_batch(batch, task_type)

    def _embed_batch(self, batch: list[str], task_type: str) -> list[list[float]]:
        # Pas de bulk officiel → appels unitaires avec un petit backoff.
        vectors: list[list[float]] = []
        for text in batch:
            for attempt in range(3):
                try:
                    result = genai.embed_content(
                        model=self.model, content=text, task_type=task_type
                    )
                    vectors.append(result["embedding"])
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(2 ** attempt)
        return vectors
