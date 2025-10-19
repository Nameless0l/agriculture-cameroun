# Copyright 2025 Agriculture Cameroun

"""Vector store ChromaDB persistant pour le RAG."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Sequence

import chromadb
from chromadb.config import Settings


DEFAULT_COLLECTION = "agriculture_cameroun"
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PERSIST_DIR = Path(os.getenv("RAG_PERSIST_DIR", str(_PROJECT_ROOT / "data" / "chroma")))


@dataclass
class SearchHit:
    text: str
    metadata: dict
    score: float  # distance normalisée (plus bas = plus proche)


class VectorStore:
    """Wrapper fin autour d'une collection ChromaDB persistante."""

    def __init__(
        self,
        collection_name: str = DEFAULT_COLLECTION,
        persist_dir: Path = DEFAULT_PERSIST_DIR,
    ):
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(
        self,
        ids: Sequence[str],
        texts: Sequence[str],
        embeddings: Sequence[Sequence[float]],
        metadatas: Sequence[dict],
    ) -> None:
        if not ids:
            return
        self._collection.upsert(
            ids=list(ids),
            documents=list(texts),
            embeddings=[list(e) for e in embeddings],
            metadatas=list(metadatas),
        )

    def query(
        self,
        query_embedding: Sequence[float],
        top_k: int = 5,
        where: dict | None = None,
    ) -> list[SearchHit]:
        result = self._collection.query(
            query_embeddings=[list(query_embedding)],
            n_results=top_k,
            where=where,
        )
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        dists = result.get("distances", [[]])[0]
        return [
            SearchHit(text=doc, metadata=meta or {}, score=float(dist))
            for doc, meta, dist in zip(docs, metas, dists)
        ]

    def count(self) -> int:
        return self._collection.count()

    def reset(self) -> None:
        self._client.delete_collection(self._collection.name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection.name,
            metadata={"hnsw:space": "cosine"},
        )


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    return VectorStore()
