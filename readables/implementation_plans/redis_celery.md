# Redis & Celery Integration Plan

## Goal
Decouple file ingestion from processing to handle high volume ("N-files") without blocking the system.
**Current Flow**: `Watcher` -> `Process File` (Wait) -> `DB Store`.
**New Flow**: `Watcher` -> `Push to Redis Queue` (Instant) | `Celery Worker` -> `Pop from Queue` -> `Process File` -> `DB Store`.

## Prerequisites (User Action Required)
> [!IMPORTANT]
> **Redis Server**: You must have a Redis server running.
> - **Option A (WSL/Linux)**: `sudo apt install redis-server`
> - **Option B (Docker)**: `docker run -p 6379:6379 redis`
> - **Option C (Windows Port)**: Install Memurai or similar Redis-on-Windows (Not recommended for prod, okay for dev).

## Components

### 1. Dependencies [MODIFY]
Add to `requirements.txt`:
- `celery`
- `redis`
- `eventlet` (Required for Celery on Windows to avoid process forking issues)

### 2. Configuration [MODIFY]
Update `config.py`:
- Add `CELERY_BROKER_URL = "redis://localhost:6379/0"`
- Add `CELERY_RESULT_BACKEND = "redis://localhost:6379/0"`

### 3. Worker Module (`worker.py`) [NEW]
Create a new file `worker.py` to define the Celery app and tasks.
- **Initialize Celery**: Connect to Redis.
- **Task `process_file_task(filepath)`**:
    - Initialize `FileProcessor`, `LLMService`, `DatabaseManager` (inside task to ensure process safety).
    - Perform the extraction, classification, and embedding logic (moved from `watcher.py`).
    - **Optimization**: Use `pool=solo` or `eventlet` on Windows to prevent implementation freeze.

### 4. Refactor Watcher (`watcher.py`) [MODIFY]
- Import `process_file_task` from `worker.py`.
- Instead of calling `process_file()` directly:
    - Call `process_file_task.delay(filepath)`.
    - Log "Queued file: X".

## Verification
1.  Start Redis.
2.  Start Celery Worker: `celery -A worker.celery_app worker --pool=solo -l info`
3.  Start Watcher: `python watcher.py`
4.  Drop a file in `data/incoming`.
5.  Observe Watcher log "Queued".
6.  Observe Worker log "Processing... Completed".
