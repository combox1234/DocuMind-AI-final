# Scalability Assessment Report

## Current Status: Local/Small Scale
The current V5 architecture is designed as a **Local, Single-Node System**. It is excellent for privacy and small teams but **NOT** currently suitable for "N files" at hospital scale (e.g., millions of records, hundreds of concurrent users) without modification.

### Limitations for "N-Files" & Real-Time Use

1.  **Ingestion Bottleneck (`watcher.py`)**
    - **Issue**: File processing is **Synchronous**. Files are processed one by one. If 1000 files are dropped in, the 1000th file waits for the previous 999 to finish.
    - **Impact**: Slow accumulation of knowledge. A simple backlog can cause hours of delay.

2.  **Database Bottleneck (`ChromaDB PersistentClient`)**
    - **Issue**: The current setup runs ChromaDB **in-process** (SQLite-based). It shares memory with the Python app.
    - **Impact**: Performance degrades significantly after ~100k chunks. It cannot scale horizontally across multiple servers.

3.  **Inference Bottleneck (`Ollama`)**
    - **Issue**: Large Language Models are compute-heavy. A single GPU/CPU handling multiple concurrent users will queue requests.
    - **Impact**: High latency. Users 2, 3, and 4 will wait until User 1's answer is generated.

## Roadmap to Hospital-Grade Scalability

To support "N" files and real-time usage in a hospital, we need to evolve the architecture. **Docker is the first step.**

### Phase 1: Containerization (Immediate)
Moving to Docker allows us to separate services.
- **Service A (App)**: Handles API requests.
- **Service B (Ollama)**: Dedicated AI worker.
- **Service C (Database)**: Dedicated vector store.

### Phase 2: Asynchronous Processing (Recommended for N-Files)
- **Queue System**: Add **Redis** and **Celery**.
- **Workflow**:
    1.  User uploads file → Server accepts it immediately (0.1s).
    2.  Task sent to Queue.
    3.  **Multiple Worker Containers** pick up tasks and process files in parallel.

### Phase 3: Production Vector DB (Recommended for >1M Chunks)
- Switch from local ChromaDB to **Qdrant** or **Milvus** (run as Docker services).
- These are built for millions/billions of vectors and offer much faster retrieval at scale.

## Conclusion
**Right now**: Suitable for ~1000-5000 documents and 1-5 concurrent users.
**With Docker**: Easier to manage, but performance is similar (limited by hardware).
**With Queue + Qdrant (Target State)**: Scalable to millions of documents and real-time usage.

**Recommendation**: Proceed with Dockerization (Phase 1) now. It is the prerequisite for all future scaling.
