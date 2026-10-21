"""FastAPI backend for the AI Infrastructure Assistant."""
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import qdrant_db
import rag
from prompt import MODES
from utils import EMBED_MODEL, LLM_MODEL, OLLAMA_URL, storage_calculator

app = FastAPI(title="AI Infrastructure Assistant", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Ask(BaseModel):
    question: str = Field(min_length=2)
    mode: str = "chat"


class CalcIn(BaseModel):
    users: int = Field(gt=0)
    gb_per_user: float = Field(gt=0)
    raid: str = "RAID5"
    disk_size_gb: float = Field(1000, gt=0)
    growth_percent: float = 20
    hot_spares: int = 1


@app.get("/health")
def health():
    status = {"api": "ok", "ollama": "down", "qdrant": "down", "models": []}
    try:
        tags = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5).json()
        status["models"] = [m["name"] for m in tags.get("models", [])]
        status["ollama"] = "ok"
    except Exception:
        pass
    try:
        qdrant_db.client.get_collections()
        status["qdrant"] = "ok"
    except Exception:
        pass
    return status


@app.post("/ingest")
def ingest():
    """(Re)index everything under documents/."""
    try:
        return qdrant_db.ingest_documents()
    except Exception as e:
        raise HTTPException(500, f"Ingest failed: {e}")


@app.post("/ask")
def ask(body: Ask):
    if body.mode not in MODES:
        raise HTTPException(400, f"mode must be one of {list(MODES)}")
    try:
        return rag.answer(body.question, body.mode)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"LLM/embedding service error: {e}")


@app.post("/ask/stream")
def ask_stream(body: Ask):
    if body.mode not in MODES:
        raise HTTPException(400, f"mode must be one of {list(MODES)}")
    return StreamingResponse(rag.answer_stream(body.question, body.mode), media_type="application/x-ndjson")


@app.post("/calculator")
def calculator(body: CalcIn):
    try:
        return storage_calculator(**body.model_dump())
    except ValueError as e:
        raise HTTPException(400, str(e))
