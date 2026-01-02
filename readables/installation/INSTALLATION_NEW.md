# DocuMind AI - Installation Guide

**Complete Setup Guide for Windows, Ubuntu/Linux, and macOS**

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation by Operating System](#installation-by-operating-system)
   - [Windows Installation](#windows-installation)
   - [Ubuntu/Linux Installation](#ubuntu-linux-installation)
   - [macOS Installation](#macos-installation)
3. [Running the System (Production)](#running-the-system)
4. [Verification & Testing](#verification--testing)
5. [Troubleshooting](#troubleshooting)

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores (Modern Intel/AMD/Apple Silicon) |
| **RAM** | 8 GB | 16 GB+ |
| **Disk** | 10 GB free | 50 GB+ free |
| **OS** | Windows 10/11, Ubuntu 20.04+, macOS 12+ | Windows 11, Ubuntu 22.04 LTS |
| **Python** | **3.12** (Required) | **3.12** |

---

## 🏗️ Understanding the Architecture

**Before installing, understand how the system works:**

DocuMind AI runs as **3 separate processes** that work together:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Server    │◄────►│ Celery Worker│◄────►│   Watcher   │
│  (serve.py) │      │   (async)    │      │(watcher.py) │
└─────────────┘      └──────────────┘      └─────────────┘
       │                    │                      │
       ▼                    ▼                      ▼
   Web API           Process Files         Monitor Files
   Port 5000          via Redis Queue       in data/incoming/
```

**Why 3 terminals?**
1. **Server (serve.py)** - Handles web UI and API requests using Waitress
2. **Celery Worker** - Processes files asynchronously (extract, classify, embed)
3. **Watcher** - Monitors `data/incoming/` and queues files for the worker

**Key Dependencies:**
- **Redis/Memurai** - Message broker between components, caching
- **Ollama** - Local LLM for answering questions
- **ChromaDB** - Vector database for semantic search

---

## Installation by Operating System

# Windows Installation

## Step 1: Install Prerequisites

### 1.1 Python 3.12 (Strict Requirement)
1. Visit https://www.python.org/downloads/
2. Download **Python 3.12.x**
3. **CRITICAL:** Check **"Add Python to PATH"** during installation
4. Click "Install Now"

### 1.2 Ollama (AI Brain)
1. Visit https://ollama.ai/download
2. Download "Ollama for Windows"
3. Run installer. It will verify your GPU automatically.
4. **Download Model:** Open PowerShell and run:
   ```powershell
   ollama pull llama3.2    # Main Chat Model
   ```

### 1.3 Memurai (Redis for Windows) ⚡ CRITICAL
*This project **REQUIRES** Redis for async task queuing and caching. Without it, files won't process!*

**On Windows, use Memurai Developer Edition:**
1. Visit https://www.memurai.com/get-memurai
2. Download "Memurai Developer" (Free for development)
3. Run the installer (it installs as a Windows service)
4. **Verify Installation:**
   ```powershell
   memurai-cli
   # Inside the CLI, type:
   ping
   # Should reply: PONG
   ```
5. **Verify Service is Running:**
   ```powershell
   Get-Service Memurai
   # Status should be: Running
   ```

**Important:** If Memurai is not running, use helper script:
```powershell
.\start_redis.bat
```

### 1.4 Tesseract OCR & FFmpeg
*Required for reading Images and Audio files.*
1. **Tesseract:** [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki). Add installation path (e.g., `C:\Program Files\Tesseract-OCR`) to System PATH.
2. **FFmpeg:** [Download Essentials](https://www.gyan.dev/ffmpeg/builds/). Extract to `C:\ffmpeg`. Add `C:\ffmpeg\bin` to System PATH.

---

## Step 2: Setup Project

**Navigate to Project Folder:**
```powershell
cd "d:\clg\ty winter internship\rag based"
```

**Create & Activate Virtual Environment:**
```powershell
python -m venv venv
.\venv\Scripts\activate
# You should see (venv) in your terminal
```

**Install Python Dependencies:**
```powershell
pip install -r requirements.txt
pip install waitress
# Note: requirements.txt already includes celery, redis, eventlet
# If install fails, also try:
pip install celery redis eventlet
```

**Verify Critical Packages:**
```powershell
python -c "import celery, redis; print('✅ Celery and Redis installed!')"
```

---

## Step 3: Run the Application (3 Terminals Required)

**⚠️ IMPORTANT: You need 3 separate terminal windows!**

### Terminal 1: Start the Production Server
```powershell
cd "d:\clg\ty winter internship\rag based"
.\venv\Scripts\activate
python serve.py
```
**Expected Output:**
```
✅ Database initialized with X documents
Serving on http://0.0.0.0:5000
```

### Terminal 2: Start the Celery Worker ⚡ NEW
```powershell
cd "d:\clg\ty winter internship\rag based"
.\venv\Scripts\activate
celery -A worker.celery_app worker --pool=solo -l info
```
**Expected Output:**
```
[tasks]
  . worker.process_file_task

celery@COMPUTERNAME ready.
```

**Why `--pool=solo`?** Windows doesn't support forking. This flag makes Celery work on Windows.

### Terminal 3: Start the File Watcher
```powershell
cd "d:\clg\ty winter internship\rag based"
.\venv\Scripts\activate
python watcher.py
```
**Expected Output:**
```
📁 Watching: d:\clg\ty winter internship\rag based\data\incoming
```

**✅ All 3 terminals should remain open while using the system!**

---

# Ubuntu/Linux Installation

## Step 1: Install System Packages
```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev \
    tesseract-ocr ffmpeg redis-server build-essential

# Start Redis service
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verify Redis is running
redis-cli ping
# Should reply: PONG
```

## Step 2: Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2
```

## Step 3: Setup Project
```bash
cd ~/projects/rag-based
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install waitress
# Celery and Redis already in requirements.txt
# If needed:
pip install celery redis
```

## Step 4: Run (3 Terminals)
```bash
# Terminal 1: Server
source venv/bin/activate
python serve.py

# Terminal 2: Celery Worker
source venv/bin/activate
celery -A worker.celery_app worker --pool=solo -l info

# Terminal 3: Watcher
source venv/bin/activate
python watcher.py
```

---

# macOS Installation

1. **Install Homebrew packages:**
   ```bash
   brew install python@3.12 ollama tesseract ffmpeg redis
   ```

2. **Start Services:**
   ```bash
   brew services start redis
   ollama serve &
   ollama pull llama3.2
   
   # Verify Redis
   redis-cli ping  # Should reply: PONG
   ```

3. **Setup Project:**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install waitress
   ```

4. **Run (3 Terminals):**
   ```bash
   # Terminal 1: python serve.py
   # Terminal 2: celery -A worker.celery_app worker --pool=solo -l info
   # Terminal 3: python watcher.py
   ```

---

# Maintenance & Structure

We have organized the project for clarity:

*   **`scripts/maintenance/`**: Contains utility scripts like `fix_users_db.py` or database repair tools.
*   **`docs/analysis/`**: detailed architectural analysis and plans.
*   **`logs/`**: Check `app.log` here if something goes wrong.

# Troubleshooting

**1. Files Not Processing**
- **Symptom:** Files dropped in `data/incoming/` stay there
- **Fix:** Check that **all 3 terminals** are running:
  1. Server (serve.py)
  2. Celery Worker (celery -A worker.celery_app...)
  3. Watcher (watcher.py)
- **Verify Celery:** Look for "celery@COMPUTERNAME ready"

**2. "Redis Connection Error"**
- **Windows:** Check Memurai service: `Get-Service Memurai`
- **Linux/Mac:** Check Redis: `sudo systemctl status redis-server`
- **Test:** `redis-cli ping` or `memurai-cli` then `ping`

**3. Celery Worker Won't Start**
- **Windows:** Make sure you use `--pool=solo` flag
- **Missing packages:** `pip install celery redis eventlet`
- **Check broker URL:** Should be `redis://127.0.0.1:6379/0`

**4. "Port 5000 in use"?**
Edit `serve.py` and change `port=5000` to `5001`.

**5. "Ollama connection failed"?**
Ensure Ollama is running in the system tray (Windows) or via `systemctl` (Linux).

**6. "Symmetric Cipher documents not found"?**
Ensure user has the `Technology` permission role (RBAC issue).
