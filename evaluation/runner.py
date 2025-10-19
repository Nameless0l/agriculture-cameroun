# Copyright 2025 Agriculture Cameroun

"""Orchestration d'une run d'évaluation du pipeline RAG.

Usage:
    python -m evaluation.runner \\
        --dataset evaluation/golden.jsonl \\
        --output evaluation/reports/run.json \\
        --mode hybrid --top-k 5

Structure d'une run:
    1. Pour chaque exemple du dataset doré:
       a. Appel du retriever (dense, hybrid, ou custom)
       b. Génération d'une réponse agent-like à partir du contexte
       c. Calcul des métriques retrieval (recall/precision/MRR)
       d. LLM-as-judge (faithfulness + relevance)
       e. Similarité sémantique answer↔ground_truth
    2. Agrégation globale + groupement par topic

Les runs sont sérialisées en JSON pour comparaison ultérieure (ablation study).
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import google.generativeai as genai

from agriculture_cameroun.rag import GeminiEmbedder, Retriever, get_vector_store

from .dataset import GoldenExample, load_dataset
from .judge import JudgeScore, LLMJudge
from .metrics import RetrievalScores, retrieval_metrics, semantic_similarity


DEFAULT_GENERATION_MODEL = "gemini-2.0-flash-001"
_ANSWER_PROMPT = """Tu es un agronome expert au Cameroun. Réponds à la question
ci-dessous UNIQUEMENT à partir du contexte fourni. Si le contexte ne contient
pas l'information, dis-le explicitement.

Question: {question}

Contexte:
{context}

Réponse (concise, factuelle, avec chiffres quand pertinents):
"""


@dataclass
class ExampleResult:
    id: str
    question: str
    topic: str | None
    retrieved_sources: list[str]
    expected_sources: list[str]
    answer: str
    retrieval: dict
    faithfulness: dict
    relevance: dict
    semantic_similarity: float
    latency_seconds: float


def generate_answer(
    model: genai.GenerativeModel, question: str, context: str
) -> str:
    prompt = _ANSWER_PROMPT.format(question=question, context=context)
    response = model.generate_content(prompt)
    return (response.text or "").strip()


def format_context(retrieved: list) -> str:
    return "\n\n".join(
        f"[{i+1}] (source: {r.source})\n{r.text}" for i, r in enumerate(retrieved)
    )


def run_example(
    example: GoldenExample,
    retriever: Retriever,
    judge: LLMJudge,
    embedder: GeminiEmbedder,
    gen_model: genai.GenerativeModel,
    mode: str,
    top_k: int,
) -> ExampleResult:
    start = time.perf_counter()
    retrieved = retriever.retrieve(
        query=example.question,
        top_k=top_k,
        filters={"topic": example.topic} if example.topic else None,
        mode=mode,
    )
    retrieved_sources = [r.source for r in retrieved]
    context = format_context(retrieved)
    answer = generate_answer(gen_model, example.question, context)
    latency = time.perf_counter() - start

    retrieval = retrieval_metrics(retrieved_sources, example.expected_sources)
    faith = judge.faithfulness(example.question, context, answer)
    rel = judge.relevance(example.question, answer, example.ground_truth)

    gt_vec = embedder.embed_query(example.ground_truth)
    ans_vec = embedder.embed_query(answer) if answer else gt_vec
    sim = semantic_similarity(gt_vec, ans_vec)

    return ExampleResult(
        id=example.id,
        question=example.question,
        topic=example.topic,
        retrieved_sources=retrieved_sources,
        expected_sources=list(example.expected_sources),
        answer=answer,
        retrieval=asdict(retrieval),
        faithfulness=asdict(faith),
        relevance=asdict(rel),
        semantic_similarity=sim,
        latency_seconds=latency,
    )


def aggregate(results: list[ExampleResult]) -> dict:
    def avg(key_path: list[str]) -> float:
        vals = []
        for r in results:
            obj: object = r
            for key in key_path:
                obj = obj[key] if isinstance(obj, dict) else getattr(obj, key)
            vals.append(float(obj))
        return statistics.mean(vals) if vals else 0.0

    return {
        "n_examples": len(results),
        "retrieval": {
            "hit_rate": avg(["retrieval", "hit_rate"]),
            "context_recall": avg(["retrieval", "context_recall"]),
            "context_precision": avg(["retrieval", "context_precision"]),
            "mrr": avg(["retrieval", "mrr"]),
        },
        "generation": {
            "faithfulness": avg(["faithfulness", "score"]),
            "relevance": avg(["relevance", "score"]),
            "semantic_similarity": statistics.mean(
                [r.semantic_similarity for r in results]
            )
            if results
            else 0.0,
        },
        "latency": {
            "mean_seconds": statistics.mean([r.latency_seconds for r in results])
            if results
            else 0.0,
            "p95_seconds": _percentile(
                [r.latency_seconds for r in results], 0.95
            ),
        },
    }


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    k = int(pct * (len(sorted_values) - 1))
    return sorted_values[k]


def run_evaluation(
    dataset_path: Path,
    output_path: Path,
    mode: str = "hybrid",
    top_k: int = 5,
    generation_model: str = DEFAULT_GENERATION_MODEL,
) -> dict:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    retriever = Retriever(vector_store=get_vector_store())
    embedder = GeminiEmbedder()
    judge = LLMJudge()
    gen_model = genai.GenerativeModel(
        generation_model,
        generation_config={"temperature": 0.2},
    )

    examples = load_dataset(dataset_path)
    print(f"→ {len(examples)} exemples chargés. Mode={mode}, top_k={top_k}.")

    results: list[ExampleResult] = []
    for i, example in enumerate(examples, start=1):
        print(f"  [{i}/{len(examples)}] {example.id} — {example.question[:60]}…")
        try:
            result = run_example(
                example, retriever, judge, embedder, gen_model, mode, top_k
            )
        except Exception as exc:  # noqa: BLE001
            print(f"     ! erreur: {exc}")
            continue
        results.append(result)

    summary = {
        "config": {
            "mode": mode,
            "top_k": top_k,
            "generation_model": generation_model,
            "dataset": str(dataset_path),
        },
        "aggregate": aggregate(results),
        "examples": [asdict(r) for r in results],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Rapport écrit: {output_path}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the RAG pipeline.")
    parser.add_argument(
        "--dataset", type=Path, default=Path("evaluation/golden.jsonl")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("evaluation/reports/run.json")
    )
    parser.add_argument("--mode", choices=["dense", "hybrid"], default="hybrid")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--generation-model", default=DEFAULT_GENERATION_MODEL)
    args = parser.parse_args()

    run_evaluation(
        dataset_path=args.dataset,
        output_path=args.output,
        mode=args.mode,
        top_k=args.top_k,
        generation_model=args.generation_model,
    )


if __name__ == "__main__":
    main()
