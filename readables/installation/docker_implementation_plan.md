# Dockerization Implementation Plan

## Goal
Containerize the "DocuMind AI" application to ensure consistent deployment and separation of services (App, Database, LLM).

## User Review Required
> [!IMPORTANT]
> **Ollama Model Pulling**: After starting the containers, you will need to run a one-time command to pull the `llama3.2` model:
> `docker exec -it documind-ollama ollama pull llama3.2`

> [!NOTE]
> **System Dependencies**: The Dockerfile will include heavy dependencies like `tesseract-ocr`, `libreoffice`, and `poppler-utils` to support all file types. This will make the image size larger (approx 2-3GB).

## Proposed Changes

### 1. Dockerfile [NEW]
Create a `Dockerfile` in the project root.
- **Base Image**: `python:3.11-slim`
- **System Dependencies**:
    - `build-essential` (for compiling python libs)
    - `tesseract-ocr` (for image OCR)
    - `libmagic-dev` (for file type detection)
    - `poppler-utils` (for PDF processing)
    - `libreoffice` (for office documents)
    - `ffmpeg` (for audio processing)
- **Python Dependencies**:
    - Install from `requirements.txt`.
    - **Fix**: Remove `python-magic-bin` (Windows only) and enforce `python-magic`.
- **Configuration**: Set working directory to `/app`, expose port 5000.

### 2. docker-compose.yml [NEW]
Create `docker-compose.yml` to orchestrate services.
- **Service: `backend`**
    - Build: `.`
    - Ports: `5000:5000`
    - Volumes:
        - `./data:/app/data` (Persist data/DB)
        - `./app.log:/app/app.log`
    - Environment:
        - `OLLAMA_HOST=http://ollama:11434`
- **Service: `ollama`**
    - Image: `ollama/ollama:latest`
    - Ports: `11434:11434`
    - Volumes: `ollama_data:/root/.ollama`
    - Deploy: GPU resources reservation (commented out by default, enable if GPU available).

### 3. .dockerignore [NEW]
Exclude unnecessary files to keep build context light.
- `venv/`
- `.git/`
- `__pycache__/`
- `data/` (mounted at runtime)
- `tests/`
- `*.zip`

### 4. updates to config.py [MODIFY]
- Update `LLM_HOST` (or similar) to allow configuration via environment variable, defaulting to `localhost` but capable of switching to `http://ollama:11434` inside Docker.

## Verification Plan

### Automated Tests
- Build the container: `docker-compose build`
- Start services: `docker-compose up -d`
- Check health: `curl http://localhost:5000/status`

### Manual Verification
1.  **Startup**: Run `docker-compose up`.
2.  **Model Checks**: Exec into ollama container and pull model.
3.  **UI Access**: Open `http://localhost:5000` in browser.
4.  **Functionality**:
    - Upload a document.
    - Ask a question.
    - Verify response and citations work.
