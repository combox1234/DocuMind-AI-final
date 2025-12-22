# DocuMind AI (V5)

**DocuMind AI** is an intelligent, autonomous RAG (Retrieval-Augmented Generation) system designed to manage, sort, and query your documents locally using offline LLMs.

## 🚀 Features
- **Autonomous File Sorting**: Automatically classifies files (PDFs, PPTs, etc.) into domains (Technology, Finance, Legal, etc.) and moves them to organized folders.
- **RAG-Based Chat**: Query your documents using natural language. The system retrieves relevant chunks and generates accurate, cited answers.
- **Offline & Private**: Runs 100% locally using models like Llama 3 and Phi-3. No data leaves your machine.
- **Dual LLM Architecture**: Optimized performance using a lightweight model for sorting (e.g., Llama 3.2 1B) and a smarter model for chat (e.g., Llama 3.1 8B).
- **JWT Authentication**: Secure API endpoints with token-based access.

## 🛠️ Tech Stack
- **Backend**: Python, Flask, Flask-JWT-Extended
- **AI/LLM**: Ollama (Llama 3, Phi-3, etc.), PyMuPDF (Extraction)
- **Vector DB**: ChromaDB (Semantic Search)
- **Monitoring**: Watchdog (Real-time file system monitoring)

## 📦 Installation

### 1. Prerequisites
- python 3.9+
- [Ollama](https://ollama.com/) installed and running

### 2. Setup
```bash
# Clone or Unzip V5
cd V5

# Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 3. Initialize Models
Pull the recommended models in Ollama:
```bash
ollama pull llama3.2:1b  # For classification
ollama pull llama3.1:8b  # For chat
```

## 🏃‍♂️ Usage

### Start System (Windows)
Run the automated batch script:
```bash
start_all.bat
```
This launches:
1.  **Watcher**: Monitors `data/incoming` for new files.
2.  **Web App**: Launches the Flask UI (http://localhost:5000).

### Manual Start
```bash
# Terminal 1: File Watcher
python watcher.py

# Terminal 2: Web Server
python app.py
```

## 🔄 Workflow
1.  Drop files into `data/incoming/`.
2.  The **Watcher** detects, classifies, and moves them to `data/sorted/`.
3.  Open `http://localhost:5000` to chat with your sorted documents.
