# Copyright 2025 Agriculture Cameroun

"""Chargement du dataset doré pour l'évaluation.

Format JSONL, un objet par ligne:
    {
      "id": "q001",
      "question": "...",
      "ground_truth": "réponse de référence...",
      "expected_sources": ["crops/cacao.md", ...],
      "topic": "crops",
      "tags": ["variete", "rendement"]
    }
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GoldenExample:
    id: str
    question: str
    ground_truth: str
    expected_sources: list[str] = field(default_factory=list)
    topic: str | None = None
    tags: list[str] = field(default_factory=list)


def load_dataset(path: Path) -> list[GoldenExample]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset introuvable: {path}")
    examples: list[GoldenExample] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            row = json.loads(line)
            examples.append(
                GoldenExample(
                    id=row["id"],
                    question=row["question"],
                    ground_truth=row["ground_truth"],
                    expected_sources=row.get("expected_sources", []),
                    topic=row.get("topic"),
                    tags=row.get("tags", []),
                )
            )
    return examples
