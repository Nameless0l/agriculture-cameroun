# Copyright 2025 Agriculture Cameroun

"""LLM-as-a-judge utilisant Gemini.

Évalue deux dimensions clés:
- **faithfulness** : la réponse est-elle ancrée dans le contexte récupéré
  (pas d'hallucination) ?
- **answer_relevance** : la réponse adresse-t-elle la question ?

Chaque score est un float dans [0, 1], le prompt demande explicitement
une note 0-5 plus une justification, qu'on normalise ensuite.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

import google.generativeai as genai

_FAITHFULNESS_PROMPT = """Tu es un juge impartial évaluant la fidélité d'une réponse RAG.

Question: {question}

Contexte récupéré:
{context}

Réponse de l'agent:
{answer}

Évalue si la réponse est ENTIÈREMENT supportée par le contexte (pas d'information
inventée). Ignore si la réponse est pertinente ou complète — seul compte le fait
que chaque affirmation factuelle soit traçable au contexte.

Réponds en JSON strict:
{{"score": <0-5>, "reason": "<courte justification>"}}

Barème:
- 5 : tout est ancré dans le contexte
- 4 : 1-2 affirmations mineures non ancrées mais plausibles
- 3 : plusieurs affirmations non ancrées
- 2 : moitié de la réponse inventée
- 1 : majorité inventée
- 0 : réponse entièrement inventée ou contradictoire avec le contexte
"""

_RELEVANCE_PROMPT = """Tu es un juge impartial évaluant la pertinence d'une réponse.

Question: {question}

Réponse de l'agent:
{answer}

Réponse de référence:
{ground_truth}

Évalue dans quelle mesure la réponse de l'agent répond à la question et couvre
les éléments essentiels de la réponse de référence. Ne pénalise pas pour des
formulations différentes, tant que le fond est correct.

Réponds en JSON strict:
{{"score": <0-5>, "reason": "<courte justification>"}}

Barème:
- 5 : répond complètement, couvre les points clés de la référence
- 4 : répond mais manque un détail mineur
- 3 : répond partiellement (moitié des points clés)
- 2 : effleure le sujet
- 1 : hors-sujet mais connexe
- 0 : totalement hors-sujet ou vide
"""


@dataclass
class JudgeScore:
    score: float  # [0, 1]
    raw_score: int  # [0, 5]
    reason: str


class LLMJudge:
    def __init__(self, model: str = "gemini-2.0-flash-001", api_key: str | None = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY manquant.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model,
            generation_config={"temperature": 0.0, "response_mime_type": "application/json"},
        )

    def faithfulness(self, question: str, context: str, answer: str) -> JudgeScore:
        prompt = _FAITHFULNESS_PROMPT.format(
            question=question, context=context, answer=answer
        )
        return self._score(prompt)

    def relevance(self, question: str, answer: str, ground_truth: str) -> JudgeScore:
        prompt = _RELEVANCE_PROMPT.format(
            question=question, answer=answer, ground_truth=ground_truth
        )
        return self._score(prompt)

    def _score(self, prompt: str) -> JudgeScore:
        response = self.model.generate_content(prompt)
        text = response.text.strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Dernier recours : extraction regex du premier entier.
            match = re.search(r'"score"\s*:\s*(\d)', text)
            data = {
                "score": int(match.group(1)) if match else 0,
                "reason": text[:200],
            }
        raw = max(0, min(5, int(data.get("score", 0))))
        return JudgeScore(
            score=raw / 5.0,
            raw_score=raw,
            reason=str(data.get("reason", ""))[:500],
        )
