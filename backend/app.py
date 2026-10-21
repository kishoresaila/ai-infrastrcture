"""FastAPI backend for the AI Infrastructure Assistant."""
from pathlib import Path

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import qdrant_db
import rag
from prompt import MODES
from utils import (ALLOWED_EXT, CATEGORIES, DOCS_DIR, MAX_UPLOAD_MB, OLLAMA_URL,
                   storage_calculator)

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


# ------------------------------------------------------------ documents
def _safe_name(name: str) -> str:
    return Path(name).name.replace("\\", "_").strip()


@app.get("/documents")
def documents():
    try:
        docs = qdrant_db.list_documents()
    except Exception as e:
        raise HTTPException(502, f"Qdrant error: {e}")
    for d in docs:
        p = DOCS_DIR / d["category"] / d["name"]
        d["size"] = p.stat().st_size if p.exists() else None
    return {"documents": docs, "categories": CATEGORIES,
            "allowed": sorted(ALLOWED_EXT), "max_mb": MAX_UPLOAD_MB}


@app.post("/documents/upload")
def upload(category: str = Form(...), files: list[UploadFile] = File(...)):
    """Save each file under documents/<category>/ and index it right away."""
    if category not in CATEGORIES:
        raise HTTPException(400, f"category must be one of {CATEGORIES}")
    target = DOCS_DIR / category
    target.mkdir(parents=True, exist_ok=True)
    results = []
    for f in files:
        name = _safe_name(f.filename or "")
        ext = Path(name).suffix.lower()
        if not name or ext not in ALLOWED_EXT:
            results.append({"name": name or "(unnamed)", "ok": False,
                            "error": f"Unsupported type. Allowed: {', '.join(sorted(ALLOWED_EXT))}"})
            continue
        data = f.file.read(MAX_UPLOAD_MB * 1024 * 1024 + 1)
        if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
            results.append({"name": name, "ok": False, "error": f"Larger than {MAX_UPLOAD_MB} MB"})
            continue
        path = target / name
        path.write_bytes(data)
        try:
            n = qdrant_db.ingest_file(path, category)
            results.append({"name": name, "ok": True, "chunks": n})
        except Exception as e:
            path.unlink(missing_ok=True)  # don't keep files we could not index
            results.append({"name": name, "ok": False, "error": str(e)})
    return {"category": category, "results": results}


@app.delete("/documents/{category}/{name}")
def delete_document(category: str, name: str):
    name = _safe_name(name)
    if category not in CATEGORIES:
        raise HTTPException(400, "unknown category")
    (DOCS_DIR / category / name).unlink(missing_ok=True)
    qdrant_db.delete_points(category, name)
    return {"deleted": f"{category}/{name}"}
