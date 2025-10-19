# Copyright 2025 Agriculture Cameroun

"""Observabilité via Langfuse (optionnel).

Si LANGFUSE_PUBLIC_KEY et LANGFUSE_SECRET_KEY sont absents, toutes les fonctions
deviennent des no-ops transparents — l'application tourne sans erreur.
"""

from .tracing import LangfuseTracer, get_tracer, make_adk_callbacks

__all__ = ["LangfuseTracer", "get_tracer", "make_adk_callbacks"]
