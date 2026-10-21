"""Qdrant helpers: create collection, ingest documents, search."""
import hashlib
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from embeddings import embed
from utils import COLLECTION, DOCS_DIR, EMBED_DIM, QDRANT_URL, chunk_text

client = QdrantClient(url=QDRANT_URL)


def ensure_collection() -> None:
    names = [c.name for c in client.get_collections().collections]
    if COLLECTION not in names:
        client.create_collection(
            COLLECTION,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )


def ingest_documents(docs_dir: Path = DOCS_DIR) -> dict:
    """Walk documents/<category>/*.md|txt, chunk, embed and upsert."""
    ensure_collection()
    total_files, total_chunks = 0, 0
    for path in sorted(Path(docs_dir).rglob("*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        category = path.parent.name
        text = path.read_text(encoding="utf-8", errors="ignore")
        points = []
        for i, chunk in enumerate(chunk_text(text)):
            # deterministic id -> re-ingesting updates instead of duplicating
            pid = int(hashlib.md5(f"{path}:{i}".encode()).hexdigest()[:15], 16)
            points.append(PointStruct(
                id=pid, vector=embed(chunk),
                payload={"text": chunk, "source": str(path.name), "category": category},
            ))
        if points:
            client.upsert(COLLECTION, points=points)
            total_files += 1
            total_chunks += len(points)
    return {"files": total_files, "chunks": total_chunks}


def search(query_vector: list[float], top_k: int = 5, category: str | None = None):
    flt = None
    if category:
        flt = Filter(must=[FieldCondition(key="category", match=MatchValue(value=category))])
    res = client.query_points(COLLECTION, query=query_vector, limit=top_k,
                              query_filter=flt, with_payload=True)
    return res.points
