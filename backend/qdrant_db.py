"""Qdrant helpers: create collection, ingest/delete/list documents, search."""
import hashlib
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import (Distance, FieldCondition, Filter, FilterSelector,
                                  MatchValue, PointStruct, VectorParams)

from embeddings import embed
from utils import (ALLOWED_EXT, COLLECTION, DOCS_DIR, EMBED_DIM, QDRANT_URL,
                   chunk_text, extract_text)

client = QdrantClient(url=QDRANT_URL)


def ensure_collection() -> None:
    names = [c.name for c in client.get_collections().collections]
    if COLLECTION not in names:
        client.create_collection(
            COLLECTION,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )


def _doc_filter(category: str, source: str) -> Filter:
    return Filter(must=[
        FieldCondition(key="category", match=MatchValue(value=category)),
        FieldCondition(key="source", match=MatchValue(value=source)),
    ])


def delete_points(category: str, source: str) -> None:
    ensure_collection()
    client.delete(COLLECTION, points_selector=FilterSelector(filter=_doc_filter(category, source)))


def ingest_file(path: Path, category: str) -> int:
    """(Re)index one file. Old chunks of the same file are removed first,
    so editing/replacing a document never leaves stale chunks behind."""
    ensure_collection()
    text = extract_text(path)
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("No readable text found (scanned/image-only PDF?)")
    delete_points(category, path.name)
    points = []
    for i, chunk in enumerate(chunks):
        pid = int(hashlib.md5(f"{category}/{path.name}:{i}".encode()).hexdigest()[:15], 16)
        points.append(PointStruct(
            id=pid, vector=embed(chunk),
            payload={"text": chunk, "source": path.name, "category": category},
        ))
    client.upsert(COLLECTION, points=points)
    return len(points)


def list_documents() -> list[dict]:
    """Aggregate chunk counts per (category, source) straight from Qdrant."""
    ensure_collection()
    counts: dict[tuple[str, str], int] = {}
    offset = None
    while True:
        points, offset = client.scroll(COLLECTION, limit=256, offset=offset,
                                       with_payload=["source", "category"], with_vectors=False)
        for p in points:
            key = (p.payload.get("category", ""), p.payload.get("source", ""))
            counts[key] = counts.get(key, 0) + 1
        if offset is None:
            break
    return [{"category": c, "name": n, "chunks": k} for (c, n), k in sorted(counts.items())]


def ingest_documents(docs_dir: Path = DOCS_DIR) -> dict:
    """Index everything under documents/<category>/ and drop chunks of files that no longer exist."""
    ensure_collection()
    files, chunks, errors, on_disk = 0, 0, [], set()
    for path in sorted(Path(docs_dir).rglob("*")):
        if not path.is_file() or path.suffix.lower() not in ALLOWED_EXT:
            continue
        category = path.parent.name
        on_disk.add((category, path.name))
        try:
            chunks += ingest_file(path, category)
            files += 1
        except Exception as e:
            errors.append({"file": f"{category}/{path.name}", "error": str(e)})
    removed = 0
    for d in list_documents():
        if (d["category"], d["name"]) not in on_disk:
            delete_points(d["category"], d["name"])
            removed += 1
    return {"files": files, "chunks": chunks, "removed": removed, "errors": errors}


def search(query_vector: list[float], top_k: int = 5, category: str | None = None):
    flt = None
    if category:
        flt = Filter(must=[FieldCondition(key="category", match=MatchValue(value=category))])
    res = client.query_points(COLLECTION, query=query_vector, limit=top_k,
                              query_filter=flt, with_payload=True)
    return res.points
