"""Embeddings via Ollama (nomic-embed-text)."""
import httpx

from utils import EMBED_MODEL, OLLAMA_URL


def embed(text: str, kind: str = "document") -> list[float]:
    # nomic-embed-text works best with task prefixes
    prefix = "search_query: " if kind == "query" else "search_document: "
    r = httpx.post(f"{OLLAMA_URL}/api/embeddings",
                   json={"model": EMBED_MODEL, "prompt": prefix + text},
                   timeout=120)
    r.raise_for_status()
    return r.json()["embedding"]


def embed_many(texts: list[str]) -> list[list[float]]:
    return [embed(t) for t in texts]
