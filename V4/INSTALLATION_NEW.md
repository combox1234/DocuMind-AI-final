# DocuMind AI - Installation Guide

**Complete Setup Guide for Windows, Ubuntu/Linux, and macOS**

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation by Operating System](#installation-by-operating-system)
   - [Windows Installation](#windows-installation)
   - [Ubuntu/Linux Installation](#ubuntu-linux-installation)
   - [macOS Installation](#macos-installation)
3. [Running the System](#running-the-system)
4. [Verification & Testing](#verification--testing)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 10 GB free | 50 GB+ free |
| **OS** | Windows 10, Ubuntu 20.04, macOS 11 | Windows 11, Ubuntu 22.04+, macOS 12+ |
| **Python** | 3.12+ | 3.12+ |

---

## Installation by Operating System

# Windows Installation

## Step 1: Install Prerequisites

### 1.1 Python 3.12+

**Download & Install:**
1. Visit https://www.python.org/downloads/
2. Download Python 3.12 or later
3. **CRITICAL:** Check "Add Python to PATH" during installation
4. Click "Install Now"

**Verify:**
```powershell
python --version
# Should show: Python 3.12.x or higher
```

---

### 1.2 Ollama (LLM Runtime)

**Download & Install:**
1. Visit https://ollama.ai/download
2. Download "Ollama for Windows"
3. Run installer (Ollama starts automatically)

**Pull LLM Model:**
```powershell
ollama pull llama3.2
# Downloads ~2GB model, wait for completion
```

**Verify:**
```powershell
ollama list
# Should show: llama3.2
```

---

### 1.3 Tesseract OCR (For Image Processing)

**Download & Install:**
1. Visit https://github.com/UB-Mannheim/tesseract/wiki
2. Download latest Windows installer: `tesseract-ocr-w64-setup-v5.x.x.exe`
3. Run installer, note installation path (usually `C:\Program Files\Tesseract-OCR`)

**Add to System PATH:**
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to "Advanced" tab → "Environment Variables"
3. Under "System variables", find "Path", click "Edit"
4. Click "New", add: `C:\Program Files\Tesseract-OCR`
5. Click OK on all dialogs
6. **Restart PowerShell**

**Verify:**
```powershell
tesseract --version
# Should show version info
```

---

### 1.4 FFmpeg (For Audio/Video Processing)

**Download & Install:**
1. Visit https://www.gyan.dev/ffmpeg/builds/
2. Download "ffmpeg-release-essentials.zip"
3. Extract to `C:\ffmpeg`
4. Add `C:\ffmpeg\bin` to System PATH (same process as Tesseract)
5. **Restart PowerShell**

**Verify:**
```powershell
ffmpeg -version
# Should show version info
```

---

## Step 2: Setup Project

**Navigate to Project:**
```powershell
cd "d:\clg\ty winter internship\rag based"
```

**Create Virtual Environment:**
```powershell
python -m venv venv
```

**Activate Virtual Environment:**
```powershell
.\venv\Scripts\activate
# You should see (venv) in your prompt
```

**Install Dependencies:**
```powershell
pip install -r requirements.txt
# Takes 5-10 minutes
```

**Verify Installation:**
```powershell
python -c "import flask, chromadb, ollama, watchdog; print('✓ All packages installed!')"
```

---

## Step 3: Start the System

**Terminal 1 - File Watcher:**
```powershell
python watcher.py
```

**Terminal 2 (New Window) - Web App:**
```powershell
cd "d:\clg\ty winter internship\rag based"
.\venv\Scripts\activate
python app.py
```

**Access Web UI:**
Open browser → http://localhost:5000

---

# Ubuntu/Linux Installation

## Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

---

## Step 2: Install Python 3.12+

**Ubuntu 22.04+ (Python 3.12 included):**
```bash
python3 --version
# Should show 3.12+
```

**Ubuntu 20.04 (Add PPA for Python 3.12):**
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
```

**Install pip:**
```bash
sudo apt install -y python3-pip
```

**Verify:**
```bash
python3 --version
# Should show: Python 3.12.x
```

---

## Step 3: Install Ollama

**Download & Install:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Start Ollama Service:**
```bash
sudo systemctl start ollama
sudo systemctl enable ollama
```

**Pull LLM Model:**
```bash
ollama pull llama3.2
```

**Verify:**
```bash
ollama list
# Should show: llama3.2

# Check service status
sudo systemctl status ollama
```

---

## Step 4: Install Tesseract OCR

```bash
sudo apt install -y tesseract-ocr tesseract-ocr-eng
```

**Verify:**
```bash
tesseract --version
# Should show version 4.x or 5.x
```

---

## Step 5: Install FFmpeg

```bash
sudo apt install -y ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

---

## Step 6: Install Additional Dependencies

```bash
# Development tools
sudo apt install -y build-essential libssl-dev libffi-dev

# Image processing libraries
sudo apt install -y libjpeg-dev libpng-dev libtiff-dev

# Audio processing libraries
sudo apt install -y portaudio19-dev python3-pyaudio

# For PDF processing
sudo apt install -y libpoppler-cpp-dev
```

---

## Step 7: Setup Project

**Clone/Navigate to Project:**
```bash
cd ~/projects
# Or wherever you have the project
```

**Create Virtual Environment:**
```bash
python3 -m venv venv
```

**Activate Virtual Environment:**
```bash
source venv/bin/activate
# You should see (venv) in your prompt
```

**Install Python Dependencies:**
```bash
pip install -r requirements.txt
```

**Verify Installation:**
```bash
python -c "import flask, chromadb, ollama, watchdog; print('✓ All packages installed!')"
```

---

## Step 8: Start the System

**Terminal 1 - File Watcher:**
```bash
source venv/bin/activate
python watcher.py
```

**Terminal 2 - Web App:**
```bash
# Open new terminal
cd ~/projects/rag-based  # Your project path
source venv/bin/activate
python app.py
```

**Access Web UI:**
Open browser → http://localhost:5000

---

## Step 9: Create Systemd Services (Optional - Run as Background Service)

**Create File Watcher Service:**
```bash
sudo nano /etc/systemd/system/documind-watcher.service
```

**Add content:**
```ini
[Unit]
Description=DocuMind AI File Watcher
After=network.target ollama.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/projects/rag-based
Environment="PATH=/home/YOUR_USERNAME/projects/rag-based/venv/bin"
ExecStart=/home/YOUR_USERNAME/projects/rag-based/venv/bin/python watcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Create Web App Service:**
```bash
sudo nano /etc/systemd/system/documind-webapp.service
```

**Add content:**
```ini
[Unit]
Description=DocuMind AI Web Application
After=network.target ollama.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/projects/rag-based
Environment="PATH=/home/YOUR_USERNAME/projects/rag-based/venv/bin"
ExecStart=/home/YOUR_USERNAME/projects/rag-based/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable documind-watcher documind-webapp
sudo systemctl start documind-watcher documind-webapp
```

**Check status:**
```bash
sudo systemctl status documind-watcher
sudo systemctl status documind-webapp
```

**View logs:**
```bash
sudo journalctl -u documind-watcher -f
sudo journalctl -u documind-webapp -f
```

---

# macOS Installation

## Step 1: Install Homebrew (Package Manager)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## Step 2: Install Prerequisites

**Install Python 3.12:**
```bash
brew install python@3.12
```

**Install Ollama:**
```bash
# Download from https://ollama.ai/download
# Or use Homebrew
brew install ollama

# Start Ollama
ollama serve &

# Pull model
ollama pull llama3.2
```

**Install Tesseract:**
```bash
brew install tesseract
```

**Install FFmpeg:**
```bash
brew install ffmpeg
```

**Verify Installations:**
```bash
python3 --version
ollama list
tesseract --version
ffmpeg -version
```

---

## Step 3: Setup Project

**Navigate to Project:**
```bash
cd ~/projects/rag-based
```

**Create Virtual Environment:**
```bash
python3 -m venv venv
```

**Activate Virtual Environment:**
```bash
source venv/bin/activate
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

---

## Step 4: Start the System

**Terminal 1 - File Watcher:**
```bash
source venv/bin/activate
python watcher.py
```

**Terminal 2 - Web App:**
```bash
source venv/bin/activate
python app.py
```

**Access Web UI:**
Open Safari/Chrome → http://localhost:5000

---

# Running the System

## Quick Start Commands

### Windows
```powershell
# Terminal 1
cd "d:\clg\ty winter internship\rag based"
.\venv\Scripts\activate
python watcher.py

# Terminal 2 (new window)
cd "d:\clg\ty winter internship\rag based"
.\venv\Scripts\activate
python app.py
```

### Linux/macOS
```bash
# Terminal 1
cd ~/projects/rag-based
source venv/bin/activate
python watcher.py

# Terminal 2 (new terminal)
cd ~/projects/rag-based
source venv/bin/activate
python app.py
```

---

## Using the System

### Add Documents

**Windows:**
```
Drag files into: d:\clg\ty winter internship\rag based\data\incoming\
```

**Linux/macOS:**
```bash
cp ~/Documents/file.pdf ~/projects/rag-based/data/incoming/
```

### Ask Questions

1. Open browser → http://localhost:5000
2. Type question in chat interface
3. Get answer with source citations
4. Click on cited files to download

---

# Verification & Testing

## Run Test Suite

**Windows:**
```powershell
python run_tests.py
```

**Linux/macOS:**
```bash
python run_tests.py
```

**Expected Output:**
```
Running tests...
✓ test_database.py .......... (10 passed)
✓ test_extractors.py ....... (7 passed)
✓ test_llm.py ........... (8 passed, 6 skipped)
✓ test_integration.py ... (3 passed)

Total: 28 tests (22 passed, 6 skipped)
```

---

## Test File Processing

**Create test file:**
```bash
echo "This is a test document about machine learning and AI" > data/incoming/test.txt
```

**Watch Terminal 1 for output:**
```
Processing file: test.txt
Extracted 50 characters
Classified as: Technology
Moved to: data/sorted/Technology/test.txt
Indexed 1 chunks
✓ Processing complete
```

---

# Troubleshooting

## Common Issues - All Platforms

### Issue: "Ollama is not running"

**Windows:**
```powershell
# Check if running
Get-Process ollama

# Start Ollama
ollama serve
```

**Linux:**
```bash
# Check service
sudo systemctl status ollama

# Start service
sudo systemctl start ollama
```

**macOS:**
```bash
# Start Ollama
ollama serve &
```

---

### Issue: "No module named 'xyz'"

**Solution:**
```bash
pip install xyz
# Or reinstall all
pip install -r requirements.txt --force-reinstall
```

---

### Issue: "Port 5000 already in use"

**Find what's using the port:**

**Windows:**
```powershell
netstat -ano | findstr :5000
```

**Linux/macOS:**
```bash
lsof -i :5000
```

**Solution:** Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

### Issue: "Permission denied" (Linux/macOS)

**Fix data directory permissions:**
```bash
chmod -R 755 data/
chown -R $USER:$USER data/
```

---

### Issue: Tesseract not found

**Windows:**
- Verify PATH includes `C:\Program Files\Tesseract-OCR`
- Restart PowerShell after adding to PATH

**Linux:**
```bash
sudo apt install -y tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

---

## Platform-Specific Issues

### Windows: "Microsoft Visual C++ required"

**Solution:**
```
Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
Install and retry: pip install -r requirements.txt
```

---

### Linux: "PortAudio library not found"

**Solution:**
```bash
sudo apt install portaudio19-dev python3-pyaudio
pip install pyaudio --force-reinstall
```

---

### macOS: "xcrun: error: invalid active developer path"

**Solution:**
```bash
xcode-select --install
```

---

# FAQ

## General Questions

**Q: Do I need internet after installation?**  
A: No! After setup, everything runs offline (except speech-to-text for audio).

**Q: How much disk space do I need?**  
A: ~2-3x your document size. 10GB docs = ~25GB total (including database).

**Q: Can I run on a server without GUI?**  
A: Yes! Works perfectly on headless Ubuntu/Debian servers.

**Q: How do I backup my data?**  
A: Copy these folders:
- `data/sorted/` (organized files)
- `data/database/` (vector database)

---

## Performance Questions

**Q: System is slow on my old laptop**  
A: Increase chunk size in `config.py`:
```python
CHUNK_SIZE = 1000  # Increase from 500
```

**Q: Processing large PDFs takes forever**  
A: Normal for 100+ page PDFs. Process smaller batches or use faster hardware.

**Q: Can I use a different LLM model?**  
A: Yes! Edit `config.py`:
```python
OLLAMA_MODEL = "llama3.1"  # Or any other model
```
Then pull the model: `ollama pull llama3.1`

---

## Multi-User Questions

**Q: Can multiple people access simultaneously?**  
A: Yes! They access via browser: `http://SERVER_IP:5000`

**Q: How do I expose to network?**  
A: Already configured! Find your IP:

**Windows:**
```powershell
ipconfig
# Look for IPv4 Address
```

**Linux/macOS:**
```bash
ip addr show
# or
ifconfig
```

Then access from other devices: `http://YOUR_IP:5000`

---

## Security Questions

**Q: Is it secure for sensitive documents?**  
A: Yes! All processing is local. For extra security:
1. Don't expose to internet
2. Use VPN for remote access
3. Encrypt your disk

**Q: Can I use with HIPAA/GDPR data?**  
A: Yes! 100% offline processing, no cloud uploads.

---

# Next Steps

1. ✅ Complete installation for your OS
2. ✅ Start both services (watcher + web app)
3. ✅ Add test documents
4. ✅ Verify processing in Terminal 1
5. ✅ Ask test questions in web UI
6. 📖 Read [README.md](README.md) for features
7. 🏗️ Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
8. 📋 Check [SUPPORTED_FILE_TYPES.md](SUPPORTED_FILE_TYPES.md) for file formats

---

# Quick Reference

## Start System

**Windows:**
```powershell
.\venv\Scripts\activate
python watcher.py  # Terminal 1
python app.py      # Terminal 2
```

**Linux/macOS:**
```bash
source venv/bin/activate
python watcher.py  # Terminal 1
python app.py      # Terminal 2
```

## Stop System

Press `Ctrl+C` in both terminals

## Check Status

```bash
ollama list                    # Check models
python --version              # Check Python
pip list                      # Check packages
```

## Access UI

**Local:** http://localhost:5000  
**Network:** http://YOUR_IP:5000

---

**🎉 Installation Complete!**

**Your private AI knowledge base is ready.**

*No internet. No subscriptions. Complete control.*

