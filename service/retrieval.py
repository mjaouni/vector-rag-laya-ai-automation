"""Embedded Qdrant + MiniLM. Keep seed and app in separate processes (not concurrent)."""
from __future__ import annotations
from functools import lru_cache
import hashlib
from typing import Any
from .config import settings


@lru_cache(maxsize=1)
def embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model)


@lru_cache(maxsize=1)
def qdrant():
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    from qdrant_client import QdrantClient
    return QdrantClient(path=str(settings.data_dir))


def close_qdrant() -> None:
    """Release the embedded Qdrant store before interpreter teardown.

    The Qdrant client is lazily cached. Clearing the cache after an explicit
    close lets its destructor run while Python's import machinery is alive.
    """
    if qdrant.cache_info().currsize:
        client = qdrant()
        try:
            client.close()
        finally:
            qdrant.cache_clear()


def chunks_of(text: str, size: int = 680, overlap: int = 110):
    """Stable, character-based chunks suitable for the small example documents."""
    if not text.strip():
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = end - overlap
    return [c for c in chunks if c]


def seed() -> dict[str, Any]:
    from qdrant_client import models
    client = qdrant()
    # Repeated setup must never delete a user's persisted collection.
    if client.collection_exists(settings.collection):
        return {"collection": settings.collection, "skipped": True, "reason": "collection_already_exists"}
    files = sorted(settings.docs_dir.glob("*.md"))
    if not files:
        raise RuntimeError("No sample_docs/*.md files to seed")
    records = [(p.name, i, chunk) for p in files for i, chunk in enumerate(chunks_of(p.read_text(encoding="utf-8")))]
    embeddings = embedding_model().encode([r[2] for r in records], normalize_embeddings=True).tolist()
    client.create_collection(
        collection_name=settings.collection,
        vectors_config=models.VectorParams(size=len(embeddings[0]), distance=models.Distance.COSINE),
    )
    points = []
    for (filename, index, content), vector in zip(records, embeddings):
        point_id = int(hashlib.sha256(f"{filename}:{index}".encode()).hexdigest()[:15], 16)
        points.append(models.PointStruct(id=point_id, vector=vector, payload={"source": filename, "chunk": index, "text": content}))
    client.upsert(collection_name=settings.collection, points=points, wait=True)
    return {"documents": len(files), "chunks": len(points), "collection": settings.collection}


def retrieve(query: str, limit: int | None = None) -> list[dict[str, Any]]:
    client = qdrant()
    if not client.collection_exists(settings.collection):
        raise RuntimeError("Knowledge base is not seeded. Run: python cli.py seed")
    vector = embedding_model().encode(query, normalize_embeddings=True).tolist()
    points = client.query_points(collection_name=settings.collection, query=vector, limit=limit or settings.top_k, with_payload=True).points
    return [{"id": str(p.id), "score": round(float(p.score), 4), "source": p.payload["source"], "chunk": p.payload["chunk"], "text": p.payload["text"]} for p in points if p.score >= settings.min_relevance]
