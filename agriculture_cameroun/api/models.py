# Copyright 2025 Agriculture Cameroun

"""Modèles Pydantic pour l'API REST."""

from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Corps d'une requête /chat."""

    message: str = Field(..., min_length=1, max_length=4096, description="Question de l'agriculteur")
    session_id: Optional[str] = Field(None, description="ID de session pour conserver le contexte")
    region: Optional[str] = Field(None, description="Région du Cameroun (ex: Centre, Nord)")
    stream: bool = Field(False, description="Activer le streaming SSE")

    model_config = {"json_schema_extra": {
        "examples": [{
            "message": "Mon cacao a des taches brunes sur les cabosses, que faire ?",
            "session_id": "session-001",
            "region": "Centre",
        }]
    }}


class SourceRef(BaseModel):
    """Référence à un document source du corpus RAG."""

    file: str
    topic: str
    score: float


class UsageStats(BaseModel):
    """Statistiques d'utilisation de la requête."""

    latency_ms: float
    agents_called: list[str]
    rag_hits: int
    estimated_cost_usd: float


class ChatResponse(BaseModel):
    """Réponse complète du système."""

    answer: str
    session_id: str
    sources: list[SourceRef] = Field(default_factory=list)
    usage: Optional[UsageStats] = None


class StreamChunk(BaseModel):
    """Chunk d'une réponse SSE streamée."""

    type: Literal["token", "sources", "done", "error"]
    data: str | list | dict


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded"]
    vector_store_docs: int
    langfuse_enabled: bool
    rag_ready: bool
