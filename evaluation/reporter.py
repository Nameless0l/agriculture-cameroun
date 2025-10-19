# Copyright 2025 Agriculture Cameroun

"""Rapport markdown comparatif à partir d'un ou plusieurs runs JSON.

Usage:
    python -m evaluation.reporter evaluation/reports/*.json \\
        --output evaluation/reports/comparison.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_runs(paths: list[Path]) -> list[dict]:
    runs = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        data["_path"] = str(path)
        data["_name"] = path.stem
        runs.append(data)
    return runs


def render_report(runs: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# Rapport d'évaluation RAG — Agriculture Cameroun\n")
    lines.append(f"Runs comparés: **{len(runs)}**\n")

    lines.append("## Configuration des runs\n")
    lines.append("| Run | Mode | top_k | Modèle génération | N ex. |")
    lines.append("|-----|------|-------|-------------------|-------|")
    for run in runs:
        cfg = run["config"]
        agg = run["aggregate"]
        lines.append(
            f"| {run['_name']} | {cfg['mode']} | {cfg['top_k']} | "
            f"`{cfg['generation_model']}` | {agg['n_examples']} |"
        )

    lines.append("\n## Métriques de retrieval\n")
    lines.append(
        "| Run | Hit rate | Context recall | Context precision | MRR |"
    )
    lines.append("|-----|----------|----------------|-------------------|-----|")
    for run in runs:
        r = run["aggregate"]["retrieval"]
        lines.append(
            f"| {run['_name']} | {r['hit_rate']:.3f} | {r['context_recall']:.3f} "
            f"| {r['context_precision']:.3f} | {r['mrr']:.3f} |"
        )

    lines.append("\n## Métriques de génération\n")
    lines.append(
        "| Run | Faithfulness | Relevance | Semantic similarity |"
    )
    lines.append("|-----|--------------|-----------|---------------------|")
    for run in runs:
        g = run["aggregate"]["generation"]
        lines.append(
            f"| {run['_name']} | {g['faithfulness']:.3f} | "
            f"{g['relevance']:.3f} | {g['semantic_similarity']:.3f} |"
        )

    lines.append("\n## Latence\n")
    lines.append("| Run | Moyenne (s) | p95 (s) |")
    lines.append("|-----|-------------|---------|")
    for run in runs:
        lat = run["aggregate"]["latency"]
        lines.append(
            f"| {run['_name']} | {lat['mean_seconds']:.2f} | "
            f"{lat['p95_seconds']:.2f} |"
        )

    lines.append("\n## Détail des échecs (score relevance < 0.6)\n")
    for run in runs:
        failures = [
            ex
            for ex in run.get("examples", [])
            if ex["relevance"]["score"] < 0.6
        ]
        if not failures:
            lines.append(f"- `{run['_name']}` : aucun échec.")
            continue
        lines.append(f"\n### {run['_name']} ({len(failures)} échecs)\n")
        for ex in failures:
            lines.append(
                f"- **{ex['id']}** — {ex['question'][:80]}… "
                f"(relevance {ex['relevance']['score']:.2f}, "
                f"faith {ex['faithfulness']['score']:.2f})"
            )
            lines.append(f"  - _{ex['relevance']['reason']}_")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Génère un rapport comparatif.")
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evaluation/reports/comparison.md"),
    )
    args = parser.parse_args()

    runs = load_runs(args.runs)
    markdown = render_report(runs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(f"✓ Rapport: {args.output}")


if __name__ == "__main__":
    main()
