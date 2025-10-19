# Copyright 2025 Agriculture Cameroun

"""Traçage Langfuse pour le pipeline multi-agents ADK.

Architecture de traçage:
    Requête utilisateur → Trace Langfuse
      └── root_agent call  → Span "root_agent"
            ├── crops_agent → Span "crops_agent"
            │     └── retrieve_agricultural_knowledge → Span (génération)
            └── economic_agent → Span "economic_agent"
                  └── get_market_prices → Span (outil)

Utilise les callbacks ADK:
    before_agent_callback  → ouvre un span par agent
    after_agent_callback   → ferme le span, enregistre la réponse
    before_tool_callback   → ouvre un span outil avec inputs
    after_tool_callback    → ferme le span outil avec outputs

Les spans sont identifiés par (invocation_id, agent_name) pour supporter
les appels imbriqués. L'état est stocké dans un dict en mémoire (thread-safe
car ADK est mono-thread par invocation).

Tout est enveloppé dans try/except — une erreur Langfuse ne casse jamais l'app.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

# Gemini Flash 2.0 pricing (USD per 1M tokens, Déc 2024)
_COST_PER_1M_INPUT = 0.075
_COST_PER_1M_OUTPUT = 0.30
_AVG_CHARS_PER_TOKEN = 4.0  # estimation grossière

_NOOP_SENTINEL = object()


def _estimate_tokens(text: Any) -> int:
    if not text:
        return 0
    s = str(text)
    return max(1, int(len(s) / _AVG_CHARS_PER_TOKEN))


def _estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens * _COST_PER_1M_INPUT / 1_000_000
        + output_tokens * _COST_PER_1M_OUTPUT / 1_000_000
    )


@dataclass
class SpanState:
    span: Any
    start_time: float
    input_preview: str = ""


class _NoopTracer:
    """Tracer sans-op quand Langfuse n'est pas configuré."""

    def trace(self, **_: Any) -> "_NoopTrace":
        return _NoopTrace()

    def flush(self) -> None:
        pass


class _NoopTrace:
    def span(self, **_: Any) -> "_NoopSpan":
        return _NoopSpan()

    def generation(self, **_: Any) -> "_NoopSpan":
        return _NoopSpan()

    def update(self, **_: Any) -> None:
        pass


class _NoopSpan:
    def end(self, **_: Any) -> None:
        pass

    def update(self, **_: Any) -> None:
        pass

    def span(self, **_: Any) -> "_NoopSpan":
        return _NoopSpan()

    def generation(self, **_: Any) -> "_NoopSpan":
        return _NoopSpan()


class LangfuseTracer:
    """Tracer Langfuse pour ADK avec fallback no-op."""

    def __init__(self) -> None:
        self._client: Any = None
        self._enabled = False
        self._active_spans: dict[str, SpanState] = {}
        self._active_traces: dict[str, Any] = {}
        self._init()

    def _init(self) -> None:
        pk = os.getenv("LANGFUSE_PUBLIC_KEY")
        sk = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        if not pk or not sk:
            self._client = _NoopTracer()
            return
        try:
            from langfuse import Langfuse  # type: ignore[import]

            self._client = Langfuse(public_key=pk, secret_key=sk, host=host)
            self._enabled = True
        except ImportError:
            self._client = _NoopTracer()

    @property
    def enabled(self) -> bool:
        return self._enabled

    # ── Lifecycle ──────────────────────────────────────────────────────────

    def start_trace(self, invocation_id: str, query: str, session_id: str | None = None) -> Any:
        try:
            trace = self._client.trace(
                id=invocation_id,
                name="agriculture-query",
                input={"query": query},
                session_id=session_id,
                tags=["agriculture-cameroun", "multi-agent"],
                metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
            )
            self._active_traces[invocation_id] = trace
            return trace
        except Exception:
            return _NoopTrace()

    def end_trace(self, invocation_id: str, output: str) -> None:
        try:
            trace = self._active_traces.pop(invocation_id, None)
            if trace:
                trace.update(output={"answer": output})
        except Exception:
            pass

    # ── Agent spans ────────────────────────────────────────────────────────

    def start_agent_span(
        self, invocation_id: str, agent_name: str, user_input: str
    ) -> None:
        try:
            trace = self._active_traces.get(invocation_id)
            parent = trace or _NoopTrace()
            span = parent.span(
                name=f"agent:{agent_name}",
                input={"query": user_input[:500]},
                metadata={"agent": agent_name},
            )
            span_key = f"{invocation_id}:{agent_name}"
            self._active_spans[span_key] = SpanState(
                span=span,
                start_time=time.perf_counter(),
                input_preview=user_input[:100],
            )
        except Exception:
            pass

    def end_agent_span(self, invocation_id: str, agent_name: str, output: str) -> None:
        try:
            span_key = f"{invocation_id}:{agent_name}"
            state = self._active_spans.pop(span_key, None)
            if state:
                latency = time.perf_counter() - state.start_time
                state.span.end(
                    output={"answer": output[:500]},
                    metadata={"latency_seconds": round(latency, 3)},
                )
        except Exception:
            pass

    # ── Tool spans ─────────────────────────────────────────────────────────

    def start_tool_span(
        self,
        invocation_id: str,
        agent_name: str,
        tool_name: str,
        tool_args: dict,
    ) -> None:
        try:
            span_key = f"{invocation_id}:{agent_name}"
            parent_state = self._active_spans.get(span_key)
            parent = parent_state.span if parent_state else (
                self._active_traces.get(invocation_id) or _NoopTrace()
            )
            input_tokens = _estimate_tokens(tool_args)
            child = parent.span(
                name=f"tool:{tool_name}",
                input=tool_args,
                metadata={"tool": tool_name, "estimated_input_tokens": input_tokens},
            )
            tool_key = f"{invocation_id}:{agent_name}:{tool_name}"
            self._active_spans[tool_key] = SpanState(
                span=child,
                start_time=time.perf_counter(),
                input_preview=str(tool_args)[:100],
            )
        except Exception:
            pass

    def end_tool_span(
        self,
        invocation_id: str,
        agent_name: str,
        tool_name: str,
        output: Any,
    ) -> None:
        try:
            tool_key = f"{invocation_id}:{agent_name}:{tool_name}"
            state = self._active_spans.pop(tool_key, None)
            if state:
                latency = time.perf_counter() - state.start_time
                output_tokens = _estimate_tokens(output)
                cost = _estimate_cost_usd(
                    _estimate_tokens(state.input_preview), output_tokens
                )
                state.span.end(
                    output=output if isinstance(output, dict) else {"result": str(output)[:500]},
                    metadata={
                        "latency_seconds": round(latency, 3),
                        "estimated_output_tokens": output_tokens,
                        "estimated_cost_usd": round(cost, 6),
                    },
                )
        except Exception:
            pass

    def flush(self) -> None:
        try:
            self._client.flush()
        except Exception:
            pass


@lru_cache(maxsize=1)
def get_tracer() -> LangfuseTracer:
    return LangfuseTracer()


def make_adk_callbacks() -> dict:
    """Retourne les callbacks ADK à brancher sur root_agent et sous-agents.

    Usage:
        callbacks = make_adk_callbacks()
        root_agent = Agent(
            ...
            before_agent_callback=callbacks["before_agent"],
            after_agent_callback=callbacks["after_agent"],
            before_tool_callback=callbacks["before_tool"],
            after_tool_callback=callbacks["after_tool"],
        )
    """
    tracer = get_tracer()

    def before_agent(callback_context: Any) -> None:
        try:
            invocation_id = str(callback_context.invocation_id)
            agent_name = str(callback_context.agent_name)
            user_content = callback_context.user_content
            query = ""
            if user_content and hasattr(user_content, "parts"):
                query = " ".join(
                    p.text for p in user_content.parts if hasattr(p, "text") and p.text
                )
            # Pour le root_agent, on démarre la trace globale.
            if agent_name == "agriculture_multiagent":
                tracer.start_trace(invocation_id, query)
            tracer.start_agent_span(invocation_id, agent_name, query)
        except Exception:
            pass

    def after_agent(callback_context: Any) -> None:
        try:
            invocation_id = str(callback_context.invocation_id)
            agent_name = str(callback_context.agent_name)
            tracer.end_agent_span(invocation_id, agent_name, "")
            if agent_name == "agriculture_multiagent":
                tracer.end_trace(invocation_id, "")
                tracer.flush()
        except Exception:
            pass

    def before_tool(tool: Any, args: dict, tool_context: Any) -> None:
        try:
            invocation_id = str(tool_context.invocation_id)
            agent_name = str(tool_context.agent_name)
            tool_name = getattr(tool, "__name__", str(tool))
            tracer.start_tool_span(invocation_id, agent_name, tool_name, args)
        except Exception:
            pass

    def after_tool(tool: Any, args: dict, tool_context: Any, tool_response: Any) -> None:
        try:
            invocation_id = str(tool_context.invocation_id)
            agent_name = str(tool_context.agent_name)
            tool_name = getattr(tool, "__name__", str(tool))
            tracer.end_tool_span(invocation_id, agent_name, tool_name, tool_response)
        except Exception:
            pass

    return {
        "before_agent": before_agent,
        "after_agent": after_agent,
        "before_tool": before_tool,
        "after_tool": after_tool,
    }
