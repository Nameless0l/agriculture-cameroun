# Copyright 2025 Agriculture Cameroun

"""Application FastAPI — point d'entrée pour l'API REST.

Endpoints:
    GET  /health        — statut du service + vérif ChromaDB + Langfuse
    GET  /ready         — liveness simple (pour Kubernetes/Docker)
    POST /chat          — requête conversationnelle (bloquant ou SSE stream)
    GET  /rag/stats     — statistiques du corpus RAG indexé

Lancement:
    uvicorn agriculture_cameroun.api.main:app --host 0.0.0.0 --port 8080 --reload
"""

from __future__ import annotations

import asyncio
import time
import uuid
from contextlib import asynccontextmanager

import os

from dotenv import load_dotenv

load_dotenv(override=True)
if os.getenv("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from ..observability import get_tracer
from ..rag import get_vector_store
from .models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    SourceRef,
    StreamChunk,
    UsageStats,
)

# ── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Pré-chargement du vector store au démarrage (évite cold-start sur /chat).
    try:
        store = get_vector_store()
        app.state.vector_store_ready = store.count() > 0
    except Exception:
        app.state.vector_store_ready = False
    yield
    # Flush Langfuse à l'arrêt.
    try:
        get_tracer().flush()
    except Exception:
        pass


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agriculture Cameroun API",
    description=(
        "Système Multi-Agents IA pour l'Agriculture Camerounaise — "
        "RAG sur corpus IRAD/FAO, 5 agents spécialisés (météo, cultures, "
        "santé, économie, ressources), orchestré via Google ADK."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Helper ─────────────────────────────────────────────────────────────────────


def _extract_sources(state: dict) -> list[SourceRef]:
    """Extrait les sources RAG depuis l'état de session ADK."""
    retrieval = state.get("last_retrieval", {})
    sources = []
    for hit in retrieval.get("results", [])[:3]:
        sources.append(
            SourceRef(
                file=hit.get("source", ""),
                topic=hit.get("metadata", {}).get("topic", ""),
                score=round(1 - float(hit.get("score", 1)), 3),
            )
        )
    return sources


async def _run_agent(message: str, session_id: str, region: str | None = None) -> tuple[str, dict]:
    """Appelle le root_agent ADK et retourne (réponse, état_session)."""
    # Import ici pour éviter la circularité et alléger le cold-start.
    from google.adk.artifacts import InMemoryArtifactService
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types as genai_types

    from ..agent import root_agent

    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="agriculture_cameroun",
        session_service=session_service,
        artifact_service=InMemoryArtifactService(),
    )
    session = session_service.create_session(
        app_name="agriculture_cameroun",
        user_id="api_user",
        session_id=session_id,
        state={"default_region": region or "Centre"},
    )
    user_msg = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=message)],
    )
    answer_parts: list[str] = []
    async for event in runner.run_async(
        user_id="api_user",
        session_id=session_id,
        new_message=user_msg,
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    answer_parts.append(part.text)
    session_state = dict(session.state or {})
    return "".join(answer_parts) or "Aucune réponse générée.", session_state


# ── Routes ─────────────────────────────────────────────────────────────────────


@app.get("/health", response_model=HealthResponse, tags=["Infra"])
async def health():
    """Vérifie l'état du service et de ses dépendances."""
    try:
        store = get_vector_store()
        doc_count = store.count()
        rag_ready = doc_count > 0
    except Exception:
        doc_count = 0
        rag_ready = False

    tracer = get_tracer()
    return HealthResponse(
        status="healthy" if rag_ready else "degraded",
        vector_store_docs=doc_count,
        langfuse_enabled=tracer.enabled,
        rag_ready=rag_ready,
    )


@app.get("/ready", tags=["Infra"])
async def ready():
    """Liveness probe minimal pour Docker/K8s."""
    return {"status": "ok"}


@app.get("/rag/stats", tags=["RAG"])
async def rag_stats():
    """Statistiques du corpus RAG indexé."""
    try:
        store = get_vector_store()
        count = store.count()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Vector store indisponible: {exc}") from exc
    return {"indexed_chunks": count, "collection": "agriculture_cameroun"}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, http_request: Request):
    """Envoie une question au système multi-agents.

    Supporte le streaming SSE via `stream=true` dans le corps.
    """
    if request.stream:
        return await _stream_chat(request)

    session_id = request.session_id or str(uuid.uuid4())
    start = time.perf_counter()

    try:
        answer, session_state = await asyncio.wait_for(
            _run_agent(request.message, session_id, request.region),
            timeout=120.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Délai d'attente dépassé (120s)")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    latency_ms = (time.perf_counter() - start) * 1000
    sources = _extract_sources(session_state)

    return ChatResponse(
        answer=answer,
        session_id=session_id,
        sources=sources,
        usage=UsageStats(
            latency_ms=round(latency_ms, 1),
            agents_called=_infer_agents_called(session_state),
            rag_hits=len(session_state.get("last_retrieval", {}).get("results", [])),
            estimated_cost_usd=round(latency_ms * 0.000001, 6),
        ),
    )


async def _stream_chat(request: ChatRequest) -> EventSourceResponse:
    """Répond en Server-Sent Events pour l'intégration frontend."""
    session_id = request.session_id or str(uuid.uuid4())

    async def event_generator() -> AsyncGenerator[dict, None]:
        try:
            answer, session_state = await asyncio.wait_for(
                _run_agent(request.message, session_id, request.region),
                timeout=120.0,
            )
            # Simule le streaming par tokens (ADK ne supporte pas le vrai streaming
            # côté agent — on coupe la réponse finale en mots).
            words = answer.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield {"data": StreamChunk(type="token", data=chunk).model_dump_json()}
                await asyncio.sleep(0.02)

            sources = _extract_sources(session_state)
            yield {
                "data": StreamChunk(
                    type="sources",
                    data=[s.model_dump() for s in sources],
                ).model_dump_json()
            }
            yield {"data": StreamChunk(type="done", data=session_id).model_dump_json()}
        except Exception as exc:
            yield {"data": StreamChunk(type="error", data=str(exc)).model_dump_json()}

    return EventSourceResponse(event_generator())


def _infer_agents_called(state: dict) -> list[str]:
    agents = []
    for key in ("weather_response", "crops_response", "health_response",
                "economic_response", "resources_response"):
        if state.get(key):
            agents.append(key.replace("_response", ""))
    return agents
