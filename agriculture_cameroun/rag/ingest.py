# Copyright 2025 Agriculture Cameroun

"""Pipeline d'ingestion du corpus agricole dans ChromaDB.

Usage:
    python -m agriculture_cameroun.rag.ingest [--reset] [--corpus PATH]

Chaque document du corpus est un fichier `.md` avec un front-matter YAML léger
(topic, region, source) — on y reste simple: premier bloc `---` optionnel.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from .chunking import chunk_text
from .embeddings import GeminiEmbedder
from .vector_store import get_vector_store

DEFAULT_CORPUS = Path("data/corpus")


def parse_front_matter(raw: str) -> tuple[dict, str]:
    if not raw.startswith("---"):
        return {}, raw
    try:
        _, front, body = raw.split("---", 2)
    except ValueError:
        return {}, raw
    metadata: dict = {}
    for line in front.strip().splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, body.lstrip("\n")


def ingest_corpus(corpus_dir: Path, reset: bool = False) -> int:
    if not corpus_dir.exists():
        raise FileNotFoundError(f"Corpus introuvable: {corpus_dir}")

    store = get_vector_store()
    if reset:
        store.reset()

    embedder = GeminiEmbedder()
    files = sorted(corpus_dir.rglob("*.md"))
    if not files:
        print(f"Aucun .md trouvé dans {corpus_dir}", file=sys.stderr)
        return 0

    total_chunks = 0
    for path in files:
        raw = path.read_text(encoding="utf-8")
        metadata, body = parse_front_matter(raw)
        # Le champ 'source' du front-matter est la citation (ex: "IRAD-MINADER").
        # On le déplace en 'citation' et on utilise le chemin fichier comme 'source'
        # afin que les métriques de retrieval (expected_sources) matchent.
        if "source" in metadata:
            metadata["citation"] = metadata.pop("source")
        metadata["source"] = path.relative_to(corpus_dir).as_posix()
        chunks = chunk_text(body, metadata=metadata)
        if not chunks:
            continue
        texts = [c.text for c in chunks]
        metadatas = [c.metadata for c in chunks]
        ids = [
            hashlib.sha1(
                f"{metadata['source']}::{c.metadata['chunk_index']}".encode()
            ).hexdigest()
            for c in chunks
        ]
        embeddings = embedder.embed_documents(texts)
        store.add(ids=ids, texts=texts, embeddings=embeddings, metadatas=metadatas)
        total_chunks += len(chunks)
        print(f"  + {path.name}: {len(chunks)} chunks")

    print(f"\n[OK] {total_chunks} chunks indexes dans {store.count()} total.")
    return total_chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingestion du corpus RAG.")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--reset", action="store_true", help="Vide la collection.")
    args = parser.parse_args()
    ingest_corpus(args.corpus, reset=args.reset)


if __name__ == "__main__":
    main()
