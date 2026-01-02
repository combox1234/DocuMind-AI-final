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

### 1.3 Memurai (Redis for Windows)
*This project requires Redis for caching. On Windows, we use **Memurai Developer Edition**.*
1. Visit https://www.memurai.com/get-memurai
2. Download "Memurai Developer" (Free for development).
3. Run the installer.
4. **Verify:** Open PowerShell and type `memurai-cli`. Type `ping`. It should reply `PONG`.

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
# This installs Flask, ChromaDB, Torch, LangChain, etc.
```

---

## Step 3: Run the Application (Production Mode)

We use **Waitress** for a robust, multi-threaded server.

**Terminal 1: Start the Server**
```powershell
.\venv\Scripts\activate
python serve.py
# Server runs on http://0.0.0.0:5000 (Accessible to network)
```

**Terminal 2: Start the Background Worker** (For processing files)
```powershell
.\venv\Scripts\activate
python watcher.py
```

---

# Ubuntu/Linux Installation

## Step 1: Install System Packages
```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev \
    tesseract-ocr ffmpeg redis-server build-essential
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
```

## Step 4: Run
```bash
# Terminal 1
python serve.py

# Terminal 2
python watcher.py
```

---

# macOS Installation

1. **Install Homebrew:** `brew install python@3.12 ollama tesseract ffmpeg redis`
2. **Start Services:** `brew services start redis`, `ollama serve`
3. **Pull Model:** `ollama pull llama3.2`
4. **Setup Project:** Same as Linux (use `venv`).

---

# Maintenance & Structure

We have organized the project for clarity:

*   **`scripts/maintenance/`**: Contains utility scripts like `fix_users_db.py` or database repair tools.
*   **`docs/analysis/`**: detailed architectural analysis and plans.
*   **`logs/`**: Check `app.log` here if something goes wrong.

# Troubleshooting

**1. "Symmetric Cipher" documents not found?**
Ensure a user has the `Technology` permission role.

**2. "Port 5000 in use"?**
Edit `serve.py` and change `port=5000` to `5001`.

**3. "Ollama connection failed"?**
Ensure Ollama is running in the system tray (Windows) or via `systemctl` (Linux).
