"""RAG pipeline: embed question -> Qdrant search -> Ollama generate."""
import json
from typing import Iterator

import httpx

from embeddings import embed
from prompt import MODES, build_user_prompt
from qdrant_db import search
from utils import LLM_MODEL, OLLAMA_URL

MIN_SCORE = 0.45  # drop weak matches so the LLM isn't fed noise


def retrieve(question: str, mode: str, top_k: int = 5) -> list[dict]:
    category = MODES[mode]["category"]
    hits = search(embed(question, "query"), top_k=top_k, category=category)
    if not hits and category:  # fall back to all docs
        hits = search(embed(question, "query"), top_k=top_k)
    return [
        {"text": h.payload["text"], "source": h.payload["source"], "score": round(h.score, 3)}
        for h in hits if h.score >= MIN_SCORE
    ]


def _messages(question: str, mode: str, contexts: list[dict]) -> list[dict]:
    return [
        {"role": "system", "content": MODES[mode]["system"]},
        {"role": "user", "content": build_user_prompt(question, contexts)},
    ]


def answer(question: str, mode: str = "chat") -> dict:
    contexts = retrieve(question, mode) if mode != "command" else []
    r = httpx.post(f"{OLLAMA_URL}/api/chat", timeout=600, json={
        "model": LLM_MODEL, "stream": False,
        "messages": _messages(question, mode, contexts),
        "options": {"temperature": 0.2},
    })
    r.raise_for_status()
    text = r.json()["message"]["content"]
    # Qwen3 may emit <think>...</think>; strip it
    if "</think>" in text:
        text = text.split("</think>", 1)[1].strip()
    return {"answer": text, "sources": sorted({c["source"] for c in contexts}), "contexts": contexts}


def answer_stream(question: str, mode: str = "chat") -> Iterator[str]:
    """Yield newline-delimited JSON: first the sources, then tokens."""
    contexts = retrieve(question, mode) if mode != "command" else []
    yield json.dumps({"sources": sorted({c["source"] for c in contexts})}) + "\n"
    in_think = False
    with httpx.stream("POST", f"{OLLAMA_URL}/api/chat", timeout=600, json={
        "model": LLM_MODEL, "stream": True,
        "messages": _messages(question, mode, contexts),
        "options": {"temperature": 0.2},
    }) as r:
        for line in r.iter_lines():
            if not line:
                continue
            tok = json.loads(line).get("message", {}).get("content", "")
            if "<think>" in tok:
                in_think = True
            if not in_think and tok:
                yield json.dumps({"token": tok}) + "\n"
            if "</think>" in tok:
                in_think = False
