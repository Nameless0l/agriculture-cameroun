# Copyright 2025 Agriculture Cameroun

"""Chunker récursif simple pour documents markdown/texte.

Pas de dépendance externe — on coupe en priorité sur les séparateurs les plus
structurants (titres, paragraphes, phrases) avec un chevauchement configurable.
"""

from __future__ import annotations

from dataclasses import dataclass

_SEPARATORS = ["\n## ", "\n### ", "\n\n", "\n", ". ", " "]


@dataclass
class Chunk:
    text: str
    metadata: dict


def chunk_text(
    text: str,
    metadata: dict | None = None,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[Chunk]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size doit être > overlap")
    metadata = metadata or {}
    pieces = _split(text, chunk_size, separator_idx=0)
    if not pieces:
        return []

    chunks: list[Chunk] = []
    buffer = ""
    for piece in pieces:
        if len(buffer) + len(piece) <= chunk_size:
            buffer = f"{buffer}{piece}" if buffer else piece
            continue
        if buffer:
            chunks.append(Chunk(buffer.strip(), dict(metadata)))
            tail = buffer[-overlap:] if overlap else ""
            buffer = tail + piece
        else:
            chunks.append(Chunk(piece.strip(), dict(metadata)))
            buffer = ""
    if buffer.strip():
        chunks.append(Chunk(buffer.strip(), dict(metadata)))

    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = idx
    return chunks


def _split(text: str, max_len: int, separator_idx: int) -> list[str]:
    """Découpe récursivement en essayant chaque séparateur dans l'ordre.

    `separator_idx` garantit qu'on avance toujours dans la liste — pas de boucle
    infinie si un fragment contient le même séparateur mais reste trop long.
    """
    if len(text) <= max_len:
        return [text]
    if separator_idx >= len(_SEPARATORS):
        # Coupe dure au caractère.
        return [text[i : i + max_len] for i in range(0, len(text), max_len)]

    sep = _SEPARATORS[separator_idx]
    if sep not in text:
        return _split(text, max_len, separator_idx + 1)

    parts = text.split(sep)
    result: list[str] = []
    for i, part in enumerate(parts):
        fragment = part if i == 0 else sep + part
        if len(fragment) <= max_len:
            result.append(fragment)
        else:
            result.extend(_split(fragment, max_len, separator_idx + 1))
    return result
