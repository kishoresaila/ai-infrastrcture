# AI-Powered Infrastructure Assistant (v2.0)

RAG-based assistant for troubleshooting Linux, Docker, Kubernetes and Storage.
Stack: FastAPI · Ollama (Qwen3 + nomic-embed-text) · Qdrant · React (Vite) + nginx · Docker Compose.

```
User -> Streamlit UI -> FastAPI -> Qdrant (retrieve top-k chunks)
                              \-> Ollama (generate answer from chunks)
```

---

## Step-by-step setup

### Step 1 - Prerequisites
- Docker + Docker Compose v2 (`docker compose version`)
- 16 GB RAM recommended for `qwen3:8b` (use `qwen3:4b` or `llama3.2:3b` on smaller machines)
- ~10 GB free disk

### Step 2 - Start the infrastructure
```bash
cd AI-Infrastructure-Assistant
docker compose up -d --build
docker compose ps          # all 4 containers should be Up
```

### Step 3 - Pull the models into Ollama (one time)
```bash
docker exec -it ollama ollama pull qwen3:8b
docker exec -it ollama ollama pull nomic-embed-text
```
Different model? Change `LLM_MODEL` in docker-compose.yml (e.g. `llama3.1:8b`) and run `docker compose up -d`.

### Step 4 - Verify the services
```bash
curl http://localhost:8000/health
# {"api":"ok","ollama":"ok","qdrant":"ok","models":["qwen3:8b","nomic-embed-text:latest"]}
```

### Step 5 - Index your documents
Drop `.md` / `.txt` files into `documents/<linux|docker|kubernetes|storage|devops>/`, then:
```bash
curl -X POST http://localhost:8000/ingest
# {"files":9,"chunks":...}
```
(or click **Re-index documents** in the UI sidebar). Re-running is safe: chunk IDs are deterministic, so it updates instead of duplicating.

**Easier: upload from the UI.** Open the **Documents** page (sidebar > Knowledge), pick a category, drag & drop `.md`, `.txt`, `.pdf` or `.docx` files and click *Upload & index*. Files are saved into `documents/<category>/` and indexed immediately. You can delete documents there too. Scanned (image-only) PDFs have no text and are rejected.

### Step 6 - Use the UI
Open http://localhost:3000 (React UI) - sidebar: AI Chat, Linux, Kubernetes, Storage, Docker, Command Generator, Log Analyzer, Storage Calculator.
(The older Streamlit UI is still available: `docker compose --profile streamlit up -d`, then http://localhost:8501.)

### Step 7 - Try the API directly
```bash
curl -s -X POST localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question":"How do I fix CrashLoopBackOff?","mode":"kubernetes"}' | jq -r .answer

curl -s -X POST localhost:8000/calculator -H 'Content-Type: application/json' \
  -d '{"users":100,"gb_per_user":5,"raid":"RAID5","disk_size_gb":600}' | jq
```
Interactive API docs: http://localhost:8000/docs

---

## How each feature maps to code

| Feature | Mode / endpoint | Where |
|---|---|---|
| AI Chat | `mode=chat` | `prompt.py` (Explanation/Root Cause/Commands/References) |
| Linux Troubleshooter | `mode=linux` | filters Qdrant to `documents/linux` |
| Kubernetes Assistant | `mode=kubernetes` | meaning, causes, logs, describe, fix |
| Storage Assistant | `mode=storage` | LVM/RAID/NFS/iSCSI answers |
| Docker Assistant | `mode=docker` | logs, inspect, exit code, restart policy |
| Command Generator | `mode=command` | no RAG, commands only |
| Log Analyzer | `mode=logs` | explain, root cause, fix |
| Storage Calculator | `POST /calculator` | `utils.storage_calculator` - exact maths, **not** the LLM |

## Build it yourself in order (learning path)
1. `utils.py` - config + chunking + calculator (test the calculator first; it needs no AI).
2. `embeddings.py` - call Ollama `/api/embeddings`; print the vector length (768).
3. `qdrant_db.py` - create collection, upsert chunks with `category` payload.
4. `rag.py` - retrieve -> build prompt -> `/api/chat`.
5. `prompt.py` - tune the per-mode system prompts (biggest quality lever).
6. `app.py` - expose endpoints; add streaming.
7. `streamlit_app.py` - UI.
8. Add more documents - answer quality = document quality.

## Run without Docker (dev)
```bash
docker run -d -p 6333:6333 qdrant/qdrant
ollama serve & ollama pull qwen3:8b && ollama pull nomic-embed-text
pip install -r requirements.txt
cd backend && uvicorn app:app --reload --port 8000        # DOCS_DIR defaults to ./documents -> run: DOCS_DIR=../documents
cd frontend && streamlit run streamlit_app.py
```

## Troubleshooting this project
- `/health` shows ollama `down` -> `docker logs ollama`.
- Empty/generic answers -> run `/ingest`; check `docker logs infra-backend`.
- Slow first answer -> the model is loading into RAM; later calls are faster.
- Out of memory -> use a smaller model.

## Ideas for v2.1 (interview talking points)
- Hybrid search (BM25 + vectors) and a reranker
- Ingest PDFs / web pages; watch the folder for changes
- Conversation memory per session
- Read-only `kubectl`/`df` tool-calling agent with approval for commands
- RAG evaluation set (Ragas) and a Prometheus `/metrics` endpoint
- Auth (API key) and Nginx reverse proxy

## Resume description
**AI-Powered Infrastructure Assistant** - Built a RAG assistant using Python, FastAPI, Ollama (Qwen3), Qdrant and Docker Compose to troubleshoot Linux, Docker, Kubernetes and storage issues. Implemented document ingestion, nomic-embed vector search with category filtering, streaming responses, a log analyzer, and a deterministic RAID capacity calculator, served through a Streamlit UI.
