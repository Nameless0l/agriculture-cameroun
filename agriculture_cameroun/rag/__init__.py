# Copyright 2025 Agriculture Cameroun

"""Module RAG (Retrieval-Augmented Generation) pour l'agriculture camerounaise.

Expose un vector store ChromaDB, un embedder Gemini, et un retriever
que les sous-agents peuvent invoquer via l'outil `retrieve_agricultural_knowledge`.
"""

from .vector_store import VectorStore, get_vector_store
from .embeddings import GeminiEmbedder
from .retriever import Retriever, RetrievalResult
from .tools import retrieve_agricultural_knowledge

__all__ = [
    "VectorStore",
    "get_vector_store",
    "GeminiEmbedder",
    "Retriever",
    "RetrievalResult",
    "retrieve_agricultural_knowledge",
]
