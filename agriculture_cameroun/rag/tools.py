# Copyright 2025 Agriculture Cameroun

"""Outils RAG exposés aux sous-agents ADK."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from google.adk.tools import ToolContext

from .retriever import Retriever


@lru_cache(maxsize=1)
def _get_retriever() -> Retriever:
    return Retriever()


def retrieve_agricultural_knowledge(
    query: str,
    tool_context: ToolContext,
    top_k: int = 5,
    topic: Optional[str] = None,
    mode: str = "hybrid",
) -> dict:
    """Récupère des passages pertinents depuis la base documentaire agricole.

    Args:
        query: Question ou mots-clés à rechercher.
        tool_context: Contexte ADK.
        top_k: Nombre de passages à retourner (défaut 5).
        topic: Filtre optionnel sur `topic` (crops/health/weather/economic/resources).
        mode: "hybrid" (défaut) ou "dense".

    Returns:
        Dict avec `results` (liste de passages + source + score) et `mode`.
    """
    retriever = _get_retriever()
    filters = {"topic": topic} if topic else None
    hits = retriever.retrieve(query=query, top_k=top_k, filters=filters, mode=mode)
    payload = {
        "mode": mode,
        "query": query,
        "results": [
            {
                "text": h.text,
                "source": h.source,
                "score": h.score,
                "metadata": {
                    k: v for k, v in h.metadata.items() if k not in {"chunk_index"}
                },
            }
            for h in hits
        ],
    }
    tool_context.state["last_retrieval"] = payload
    return payload
