# Copyright 2025 Agriculture Cameroun

"""Framework d'évaluation du pipeline RAG et des réponses agent.

Métriques couvertes:
- Retrieval: context_recall, context_precision, hit_rate@k
- Génération: faithfulness, answer_relevance (LLM-as-judge)
- Similarité: cosine(embedding ground_truth, answer)
"""

from .dataset import GoldenExample, load_dataset
from .metrics import retrieval_metrics, semantic_similarity
from .judge import LLMJudge
from .runner import run_evaluation

__all__ = [
    "GoldenExample",
    "load_dataset",
    "retrieval_metrics",
    "semantic_similarity",
    "LLMJudge",
    "run_evaluation",
]
