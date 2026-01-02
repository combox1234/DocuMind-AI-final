# DocuMind AI — Repository Analysis and Setup Guide

This document is a detailed, repository-sourced runbook for `combox1234/DocuMind-AI-final`. It consolidates architecture, features, dependencies, external requirements (Memurai/Redis, Ollama, Tesseract, FFmpeg), installation, configuration, runtime operations, verification/testing, troubleshooting, performance, and roadmap. All content here is derived from files and docs within the repository.

---

## 1) Project Overview

DocuMind AI is a local-first Retrieval-Augmented Generation (RAG) system that:
- Ingests diverse document types (PDF, DOCX, PPTX, TXT, images via OCR, audio via FFmpeg/pydub, and code files).
- Classifies files into Domains and Categories using hybrid methods (regex heuristics + LLM).
- Chunks text and embeds into ChromaDB (persistent vector store) with metadata.
- Answers queries using a local Large Language Model (LLM) via Ollama (e.g., `llama3.2`), enforcing RAG constraints (answers only from retrieved context) and citations.

Core storage and logic:
- Vectors: ChromaDB in persistent mode with HNSW ANN.
- Metadata & users: SQLite (e.g., `data/users.db`).
- Caching and queuing: Redis (Memurai on Windows) for analytics cache, duplicate detection, language stats, and Celery broker/backend.

Async processing:
- Celery worker consumes tasks from Redis and runs file processing separately from the web server and watcher.

Key architecture artifacts:
- Technical deep dive on RAG, retrieval/reranking, and external binaries:  
  [technical_deep_dive.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/technical_deep_dive.md)

---

## 2) Core Features

Sourced from roadmap and project docs:
- Multi-language support (English + Hindi).
- Strict citation and source tracking.
- File types: PDF, DOCX, PPTX, TXT, MD, PY, JS, images (OCR), audio (FFmpeg), etc.
- Authentication & Authorization:
  - JWT-based authentication.
  - Role-Based Access Control (RBAC), role-to-domain permission mapping.
  - File-level permissions and strict ownership (users see/delete their own files).
  - Admin Dashboard: user and role management, protected Admin role, chat history viewer.
- File Organization:
  - Autonomous classification (AI-powered).
  - Structured storage: `data/sorted/{Domain}/{Category}/{Extension}/{Year-Month}/`.
  - Duplicate detection via SHA-256 hashing.
  - Automatic categorization into 20+ categories.
- Database Architecture:
  - SQLite for user/role management (`data/users.db`).
  - ChromaDB for vector storage (persistent).
  - Redis/Memurai for caching and Celery broker/backend.
- Performance Optimizations (completed per docs):
  - SQLite WAL mode for concurrency (scripts/optimize_db.py).
  - RBAC check caching with `@lru_cache`.
  - Production serving with Waitress (`serve.py`).

References:  
[.md/project_status_and_roadmap.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/.md/project_status_and_roadmap.md)

---

## 3) High-Level Architecture (Textual Flow)

Ingestion & Processing:
1. Files are placed in `data/incoming/`.
2. Watcher detects stable files and queues a Celery task in Redis.
3. Celery Worker:
   - Extracts text (PDF parsers, OCR, audio transcription).
   - Hybrid classification:
     - Stage 1: Regex/heuristics for obvious matches (e.g., “docker”, “gst”, “nda”).
     - Stage 2: LLM zero-shot classification if Stage 1 fails.
   - Chunking (Recursive text splitter), embeddings via sentence-transformers.
   - Upsert chunks into ChromaDB with metadata (filename, domain, category, filepath).
   - Duplicate detection (SHA-256 hash) via Redis.
   - Time-based sorting (YYYY-MM) and move files into structured directories.
   - Update SQLite metadata with sorted paths.
   - Cache analytics and language stats in Redis.

Retrieval & Answering:
1. User submits query to the web/API server.
2. Compute query embedding; perform Chroma ANN search (Cosine similarity).
3. Re-rank top results via Cross-Encoder (pairwise scoring of (question, doc)) and filter by threshold.
4. Construct strict RAG prompt with citations and answer only from context.
5. Ollama (local) generates final response; return with citations and confidence.

References:  
- Architecture generator: [generate_architecture.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/generate_architecture.py)  
- Deep technical: [technical_deep_dive.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/technical_deep_dive.md)

---

## 4) Key Components & Modules

From repository analysis docs:  
[readables/reports/project_analysis_v5.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/readables/reports/project_analysis_v5.md)

- core/llm.py (or core/core/llm.py in heuristic section):
  - Ollama API integration (model `llama3.2`).
  - Cross-Encoder reranking (e.g., `ms-marco-MiniLM-L-6-v2`) with filtering threshold (~0.35).
  - Strict RAG prompt construction, citations, confidence scoring.
- core/processor.py:
  - Orchestrates file processing and text extraction.
- core/database.py:
  - ChromaDB wrapper for persistent client and collection operations.
- core/classifier.py:
  - Hybrid classification: explicit guardrails, keyword scoring, regex heuristics; Domain → Category → FileType.
- core/analytics.py:
  - Calculates and caches sorting stats (domain/category/extension/language, storage sizes).
  - Redis caching (`analytics:stats`), language stats from `stats:languages`.
- worker.py:
  - Celery task `worker.process_file_task`.
  - Lazy-loaded services (DB, LLM, FileProcessor, Redis) to avoid fork issues.
  - Adaptive chunk sizing by file size; time-based sorting; duplicate detection.
- config.py:
  - Central configuration (paths, chunk sizes, Celery broker/backend, logging level, LLM model, sorting settings, JWT).
- Scripts:
  - `scripts/maintenance/verify_index.py` — verify Chroma index and sample metadata.
  - `debug_chroma.py` — count and inspect document chunks by filename.
  - `scripts/reingest_log.py` — re-ingest a specific file to refresh its chunks.

References (permalinks):
- [core/analytics.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/core/analytics.py)  
- [worker.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/worker.py)  
- [config.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/config.py)  
- [core/classifier.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/core/classifier.py)  
- [core/core/llm.py (heuristics)](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/core/core/llm.py)  
- [scripts/maintenance/verify_index.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/scripts/maintenance/verify_index.py)  
- [debug_chroma.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/debug_chroma.py)  
- [scripts/reingest_log.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/scripts/reingest_log.py)

---

## 5) Dependencies (Libraries & Versions)

Core categories and versions are defined in:  
[requirements.txt](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/requirements.txt)

Highlights:
- Web/API: Flask==3.1.2, Flask-JWT-Extended, itsdangerous, Jinja2
- Serving: Waitress (installed separately per docs)
- Vector DB: chromadb==0.4.22 (persistent client), onnxruntime
- Embeddings & NLP: sentence-transformers==2.2.2, nltk==3.9.2, langdetect==1.0.9
- LLM: ollama==0.6.1
- Retrieval/Ranking: sentence-transformers CrossEncoder (docs state `ms-marco-MiniLM-L-6-v2`)
- Document processing:
  - PDF: PyMuPDF==1.23.8, pdfminer.six (pinned), openpyxl for spreadsheets.
  - Docs: python-docx, python-pptx (referenced in docs; exact pins may be implied).
  - Images: Pillow==12.0.0, pytesseract (via system Tesseract).
  - Audio: pydub==0.25.1, FFmpeg (system binary).
- Async/Caching:
  - eventlet (for Windows compatibility).
  - Celery and redis are required per implementation plan and worker code; if not present in requirements.txt, install explicitly:
    ```bash
    pip install celery redis eventlet
    ```
- Security & Utils: bcrypt>=4.1.2, cryptography==46.0.3, pydantic==2.12.5, orjson==3.11.5, numpy<2.0, packaging==25.0

---

## 6) External Requirements

- Redis on Windows via Memurai:
  - Used as Celery broker/backend and for caching analytics, duplicate hashes, and language stats.
  - Startup helper:  
    [start_redis.bat](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/start_redis.bat)
- Ollama:
  - Local LLM runner; pull `llama3.2` model.
- Tesseract OCR:
  - Required for image/scanned PDF extraction (install system binary; ensure PATH is set).
- FFmpeg:
  - Required for audio processing tasks (install system binary; ensure PATH).
- Graphviz (optional):
  - Needed if you run the Diagrams-based architecture generator script.
- Python:
  - 3.12 is the required version across OS.

---

## 7) Installation Guide

Source docs:  
- [readables/installation/INSTALLATION_NEW.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/readables/installation/INSTALLATION_NEW.md)  
- [readables/installation/UBUNTU_INSTALLATION.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/readables/installation/UBUNTU_INSTALLATION.md)  
- [readables/architecture/SYSTEM_REQUIREMENTS.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/readables/architecture/SYSTEM_REQUIREMENTS.md)

### Windows

1) Install prerequisites:
- Python 3.12 (add to PATH).
- Ollama: install and `ollama pull llama3.2`.
- Memurai Developer: verify via `memurai-cli` then `ping` → `PONG`.
- Tesseract: install; add `C:\Program Files\Tesseract-OCR` to PATH.
- FFmpeg: download; add `C:\ffmpeg\bin` to PATH.
- Optional: Visual C++ Build Tools (Desktop dev with C++).

2) Project setup:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install waitress
# If needed (Celery/Redis not present in requirements.txt):
pip install celery redis eventlet
```

3) Start services and app:
```powershell
# Ensure Memurai/Redis is running
# Ensure Ollama has llama3.2

# Terminal 1: API Server
python serve.py

# Terminal 2: Celery Worker (Windows-safe)
celery -A worker.celery_app worker --pool=solo -l info

# Terminal 3: Watcher
python watcher.py
```

### Ubuntu/Linux

1) System packages:
```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev \
    tesseract-ocr ffmpeg redis-server build-essential
```

2) Ollama:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2
```

3) Project setup:
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install waitress
# If needed:
pip install celery redis
```

4) Run:
```bash
python serve.py
celery -A worker.celery_app worker --pool=solo -l info
python watcher.py
```

### macOS

1) Homebrew:
```bash
brew install python@3.12 ollama tesseract ffmpeg redis
```

2) Services:
```bash
brew services start redis
ollama serve
ollama pull llama3.2
```

3) Project setup:
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install waitress
# If needed:
pip install celery redis
```

4) Run:
```bash
python serve.py
celery -A worker.celery_app worker --pool=solo -l info
python watcher.py
```

---

## 8) Configuration

Central config:  
[config.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/config.py)

Key settings:
- Paths:
  - `DATA_DIR`, `INCOMING_DIR`, `SORTED_DIR`
  - `DB_DIR` sourced from env var `CHROMA_DB_DIR` (default `"chroma_db_docker"`).
- LLM:
  - `LLM_MODEL = "llama3.2"`
- JWT:
  - `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_EXPIRES` (seconds).
- Processing:
  - `CHUNK_SIZE`, `CHUNK_SIZE_SMALL/MEDIUM/LARGE`, `TOP_K_RETRIEVAL`.
- Sorting:
  - `DATE_FORMAT = "%Y-%m"`, `ENABLE_TIME_BASED_SORTING = True`.
- Server:
  - `FLASK_HOST`, `FLASK_PORT`, `MAX_CONTENT_LENGTH`.
- Logging:
  - `LOG_LEVEL` from env (default `"INFO"`).
- Celery/Redis:
  - `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` (default `redis://127.0.0.1:6379/0`).
- Redis keys:
  - `REDIS_FILE_HASHES`, `REDIS_CUSTOM_CATEGORIES`, `REDIS_ANALYTICS_CACHE`, `REDIS_LANGUAGE_STATS`, `REDIS_FILE_METADATA`.

Optional `.env` to standardize settings:
```env
LLM_MODEL=llama3.2
LOG_LEVEL=INFO
CHROMA_DB_DIR=chroma_db_docker

CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

---

## 9) Running the System

1) Ensure Redis/Memurai is running:
- Windows: `memurai-cli` → `ping` → `PONG`
- Linux/macOS: `redis-cli ping` → `PONG`

2) Ensure Ollama has the model:
```bash
ollama pull llama3.2
```

3) Start components:
```bash
python serve.py
celery -A worker.celery_app worker --pool=solo -l info
python watcher.py
```

4) Ingest test:
- Place a file into `data/incoming/`.
- Watch Watcher log for “Queued file: …”.
- Watch Worker log for processing steps.
- Confirm file moved to `data/sorted/<Domain>/<Category>/<Extension>/<YYYY-MM>/`.

---

## 10) Verification & Testing

- Quick index verification:
  - [scripts/maintenance/verify_index.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/scripts/maintenance/verify_index.py):
    - Prints total documents and sample metadata from ChromaDB.
- File-specific chunk presence:
  - [debug_chroma.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/debug_chroma.py):
    - Checks count and previews chunk content for a given filename.
- Guided testing for Redis/Celery on Windows:
  - [readables/guides/testing_guide.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/readables/guides/testing_guide.md):
    - Start Memurai/Redis.
    - Start Celery worker: `celery -A worker.celery_app worker --pool=solo -l info`.
    - Start watcher: `python watcher.py`.
    - Drop a file into `data/incoming/` and validate logs.

---

## 11) Troubleshooting

Redis/Memurai
- Symptom: Worker fails or “Redis Server Missing”.
  - Validate service is running (Memurai or redis-server).
  - Confirm `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` target the correct host/port.
  - On Windows, use `--pool=solo` or install `eventlet`.

Celery Worker
- If `celery` or `redis` modules missing:
  ```bash
  pip install celery redis eventlet
  ```
- Ensure Python 3.12 and venv activation.
- Broker connectivity (firewall/port 6379).

Ollama/LLM
- Model missing — pull `llama3.2`.
- Service not running — start `ollama serve` (Linux/macOS); verify Windows service.
- Quick Python check:
  ```python
  import ollama
  print(ollama.list())
  ```

ChromaDB
- Ensure `CHROMA_DB_DIR` exists and writable.
- Verify with maintenance scripts.
- Avoid synchronous heavy processing; rely on Celery.

OCR & Audio
- Tesseract PATH set correctly.
- FFmpeg PATH set correctly.
- Prefer text parsers for text-based PDFs; OCR only for scanned documents.

Windows build tools
- Install Visual C++ Build Tools when compilation is required.
- Upgrade pip toolchain:
  ```bash
  python -m pip install --upgrade pip setuptools wheel
  ```

Path normalization & ownership
- Windows path separators may need normalization; fixes are documented in roadmap.
- RBAC/ownership checks ensure file visibility correctness.

### Common Network and API Errors

| Status | Meaning                     | Typical Causes (Repo Context)                                                                 | Fix / Action                                                                                               |
|-------:|-----------------------------|-----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| 200    | OK                          | Successful request (e.g., `/chat` returns an answer; file list or status endpoints succeed). | No action needed. If response body is unexpected, check server logs and verify request payload formatting.  |
| 201    | Created                     | Resource created (e.g., upload acknowledged; queued for processing).                          | Confirm Celery worker logs show task intake; verify Redis broker connectivity.                              |
| 204    | No Content                  | Action succeeded but no body (e.g., delete or health ping).                                   | Expected for some endpoints. If unexpected, ensure the route returns JSON and not an empty response.        |
| 301/302| Redirect                    | Framework or proxy redirects (e.g., trailing slash).                                          | Use canonical route paths; test with `curl -L`. Configure Flask route strictness if needed.                 |
| 304    | Not Modified                | Client cache hit.                                                                             | Clear cache or disable client caching during debug.                                                         |
| 400    | Bad Request                 | Malformed JSON/body; missing required fields.                                                 | Validate JSON schema; include required params; check content-type headers (e.g., `application/json`).       |
| 401    | Unauthorized                | Missing/invalid JWT; expired token.                                                           | Acquire fresh token; check `JWT_SECRET_KEY`; ensure `Authorization: Bearer <token>` header present.         |
| 403    | Forbidden                   | RBAC denies access to domain/category; ownership check fails.                                 | Verify user’s role and domain permissions; adjust RBAC mapping; confirm strict ownership logic.             |
| 404    | Not Found                   | Route doesn’t exist; static/file path invalid; doc not indexed in Chroma yet.                | Check Flask routes; verify file moved to `data/sorted/...`; re-ingest or wait for worker to index.          |
| 405    | Method Not Allowed          | Wrong HTTP verb (POST vs GET).                                                                | Use correct method per endpoint; align client call with Flask route methods.                                |
| 408    | Request Timeout             | Long sync operation; worker backlog; network latency.                                         | Use async flow (Celery); increase worker `--concurrency`; avoid large uploads synchronously.                |
| 409    | Conflict                    | Duplicate resource (e.g., SHA-256 duplicate detection).                                       | Resolve duplicate by renaming or removing; check Redis `file_hashes` map; allow intentional overwrite logic.|
| 413    | Payload Too Large           | Upload exceeds `MAX_CONTENT_LENGTH` (default 16MB).                                           | Reduce file size; increase `MAX_CONTENT_LENGTH` in `Config` if acceptable; switch to async upload strategy. |
| 415    | Unsupported Media Type      | Wrong content-type header (e.g., text vs JSON).                                               | Set appropriate `Content-Type`; adjust server parsing logic.                                                |
| 429    | Too Many Requests           | Rate limiting (if added) or overload.                                                         | Backoff; increase server threads/workers; add Redis rate limits; optimize processing.                      |
| 500    | Internal Server Error       | Uncaught server exception (LLM failure, DB error, path split bug).                            | Check logs; validate Ollama status; confirm Chroma client path; apply fixes from roadmap (path normalization). |
| 502    | Bad Gateway                 | Reverse proxy upstream failure (if using proxy).                                              | Restart upstream (Flask/Waitress); verify proxy config; ensure upstream port matches `FLASK_PORT`.          |
| 503    | Service Unavailable         | Redis/Ollama down; worker offline.                                                            | Start Redis/Memurai; `ollama serve`; start Celery worker; add health checks; retry after services up.       |
| 504    | Gateway Timeout             | Proxy timeout due to long processing.                                                         | Increase proxy timeouts; ensure async processing; pre-index large docs; stream responses if applicable.     |

Notes:
- 413 is particularly relevant given `Config.MAX_CONTENT_LENGTH = 16 * 1024 * 1024` (16MB).
- 401/403 map to JWT and RBAC enforced in the repo.
- 404 commonly indicates unindexed files or incorrect paths (Windows path normalization issues mentioned in roadmap).
- 503/504 often imply Redis/Memurai or Ollama not running, or Celery worker not consuming tasks.

---

## 12) Performance & Optimization

From repository analysis and improvement docs:
- Memory footprint (approximate):
  - Celery workers: ~500MB RAM.
  - Redis: ~100–200MB RAM.
  - ChromaDB: ~300–500MB RAM.
  - Total: ~1.5–1.8GB typical under load on 32GB systems.

- Retrieval & reranking details (tech deep dive):
  - Chroma ANN with Cosine distance; lower is better.
  - Cross-Encoder reranking; filter out chunks below ~0.35 score.

- Optimization tips:
  - Increase Celery `--concurrency` to process multiple files in parallel.
  - Choose faster PDF parsing when applicable (e.g., PyPDF or pdfplumber).
  - Consider semantic chunking (paragraph-based) to improve retrieval accuracy.
  - Streaming responses (Server-Sent Events) to improve perceived latency.
  - Hybrid search (BM25 + vectors) can improve relevance.

References:  
- [.md/SORTING_IMPROVEMENTS_ANALYSIS.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/.md/SORTING_IMPROVEMENTS_ANALYSIS.md)  
- [readables/project_improvements.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/readables/project_improvements.md)  
- [technical_deep_dive.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/technical_deep_dive.md)

---

## 13) Roadmap & Improvements

Highlights from status and roadmap:
- Completed:
  - Database consolidation (removed `auth.db`, consolidated into `users.db`).
  - Debug logging cleanup (`LOG_LEVEL` added; verbosity adjusted).
  - File domain/category metadata fix (syncing `sorted_path` to SQLite; Windows path normalization).
  - Performance optimizations (SQLite WAL; RBAC caching; Waitress serving).
- Pending & Proposed:
  - Multi-tenant architecture (soft or hard isolation).
  - DB migration to PostgreSQL for high concurrency.
  - Object storage (S3/MinIO) for files at scale.
  - Managed vector databases (Qdrant/Pinecone/Weaviate) for scaling.
  - Dockerization, Kubernetes, load balancing as future phases.

References:  
[.md/project_status_and_roadmap.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/.md/project_status_and_roadmap.md)

---

## 14) Command Cheat-Sheet

Environment setup:
```bash
python -m venv venv           # Windows: python -m venv venv
source venv/bin/activate      # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
pip install waitress
# If missing:
pip install celery redis eventlet
```

Services:
```bash
# Redis/Memurai
redis-cli ping          # Linux/macOS
# Windows:
memurai-cli             # enter CLI, then `ping` → `PONG`

# Ollama
ollama serve            # Linux/macOS (Windows: service auto-managed)
ollama pull llama3.2
```

Run:
```bash
python serve.py
celery -A worker.celery_app worker --pool=solo -l info
python watcher.py
```

Verify Chroma:
```bash
python scripts/maintenance/verify_index.py
python debug_chroma.py
```

---

## 15) File References (Key Permalinks)

- [start_redis.bat](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/start_redis.bat) — Memurai start helper (Windows).
- [readables/guides/testing_guide.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/readables/guides/testing_guide.md) — Redis & Celery testing guide.
- [readables/installation/INSTALLATION_NEW.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/readables/installation/INSTALLATION_NEW.md) — Installation for Windows/Linux/macOS.
- [readables/installation/UBUNTU_INSTALLATION.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/readables/installation/UBUNTU_INSTALLATION.md) — Ubuntu instructions and verification steps.
- [readables/architecture/SYSTEM_REQUIREMENTS.md](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/readables/architecture/SYSTEM_REQUIREMENTS.md) — OS-specific requirements and core package categories.
- [requirements.txt](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/requirements.txt) — Library versions.
- [config.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/config.py) — Configuration and environment overrides.
- [worker.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/worker.py) — Celery tasks (duplicate detection, adaptive chunking, sorting).
- [core/analytics.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/core/analytics.py) — Analytics and Redis caching.
- [core/classifier.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/core/classifier.py) — Guardrails and keyword rules.
- [core/core/llm.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/core/core/llm.py) — Content heuristics and category scoring.
- [scripts/maintenance/verify_index.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/scripts/maintenance/verify_index.py) — ChromaDB sampling.
- [debug_chroma.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/debug_chroma.py) — ChromaDB count and retrieval by filename.
- [scripts/reingest_log.py](https://github.com/combox1234/DocuMind-AI-final/blob/35310f98c03ebb960eeb8b561bd33e6d25c9e72b/scripts/reingest_log.py) — Re-ingestion workflow demo.

---

If you want this extended with environment-specific paths (e.g., Windows drive letters), containerization notes, or automated startup scripts, we can add those as separate sections or appendices based strictly on the repo’s documented approaches.
