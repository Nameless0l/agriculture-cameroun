# Copyright 2025 Agriculture Cameroun

"""Métriques d'évaluation déterministes (pas de LLM)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass
class RetrievalScores:
    hit_rate: float  # au moins une source attendue retrouvée
    context_recall: float  # proportion des sources attendues retrouvées
    context_precision: float  # proportion des sources retrouvées qui étaient attendues
    mrr: float  # mean reciprocal rank de la première source attendue


def retrieval_metrics(
    retrieved_sources: Sequence[str],
    expected_sources: Sequence[str],
) -> RetrievalScores:
    if not expected_sources:
        return RetrievalScores(hit_rate=1.0, context_recall=1.0, context_precision=1.0, mrr=1.0)

    expected_set = set(expected_sources)
    retrieved_set = set(retrieved_sources)
    hits = expected_set & retrieved_set

    hit_rate = 1.0 if hits else 0.0
    context_recall = len(hits) / len(expected_set)
    context_precision = (
        len(hits) / len(retrieved_set) if retrieved_set else 0.0
    )

    rr = 0.0
    for rank, source in enumerate(retrieved_sources, start=1):
        if source in expected_set:
            rr = 1.0 / rank
            break

    return RetrievalScores(
        hit_rate=hit_rate,
        context_recall=context_recall,
        context_precision=context_precision,
        mrr=rr,
    )


def semantic_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def mean(values: Iterable[float]) -> float:
    vals = list(values)
    return sum(vals) / len(vals) if vals else 0.0
