# System Requirements & Dependencies

## 📋 **Quick Overview**

**Python Version:** 3.12.0 (Recommended: 3.10+ to 3.12)  
**Operating Systems:** Windows 10/11, Ubuntu 20.04+, macOS 12+  
**RAM:** 8GB minimum, 16GB recommended  
**Storage:** 10GB free space (for models and database)

---

## 🔧 **System Dependencies (Install First)**

### **Windows Requirements**

#### **1. Microsoft Visual C++ 14.0+ Build Tools** ⚠️ **REQUIRED**

**Why needed:** Many Python packages (cryptography, numpy, etc.) require compilation

**Installation Options:**

**Option A - Visual Studio Build Tools (Lightweight - Recommended):**
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer
3. Select: "Desktop development with C++"
4. Install size: ~6GB

**Option B - Full Visual Studio:**
1. Download: Visual Studio 2019 or 2022 Community Edition
2. During installation, select:
   - ✅ "Desktop development with C++"
   - ✅ "Python development" (optional but useful)
3. Install size: ~10-15GB

**Verify Installation:**
```powershell
# Check if cl.exe (compiler) is available
where cl
# Should show path like: C:\Program Files (x86)\Microsoft Visual Studio\...\cl.exe
```

---

#### **2. Tesseract OCR** ⚠️ **REQUIRED for Image Text Extraction**

**Why needed:** Extracts text from images (JPG, PNG, etc.)

**Installation:**
1. **Download:** https://github.com/UB-Mannheim/tesseract/wiki
   - Get latest installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
2. **Install to:** `C:\Program Files\Tesseract-OCR`
3. **Add to PATH:**
   - Open: System Properties → Advanced → Environment Variables
   - Edit "Path" variable
   - Add: `C:\Program Files\Tesseract-OCR`
4. **Restart terminal/VS Code**

**Verify Installation:**
```powershell
tesseract --version
# Should show: tesseract 5.3.x
```

---

#### **3. Ollama (LLM Runtime)** ⚠️ **REQUIRED**

**Why needed:** Runs local LLM models (llama3.2, etc.)

**Installation:**
1. **Download:** https://ollama.ai/download (Windows installer)
2. **Run installer** (installs as Windows service)
3. **Pull model:**
   ```powershell
   ollama pull llama3.2
   ```
   (Downloads ~2GB model)

**Verify Installation:**
```powershell
ollama list
# Should show: llama3.2
```

---

### **Linux (Ubuntu/Debian) Requirements**

```bash
# Update system
sudo apt-get update

# Install build tools
sudo apt-get install -y build-essential python3-dev python3-pip python3-venv

# Install Tesseract OCR
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull LLM model
ollama pull llama3.2

# Verify installations
python3 --version  # Should be 3.10+
tesseract --version
ollama list
```

---

### **macOS Requirements**

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.12 tesseract

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

# Verify
python3 --version
tesseract --version
ollama list
```

---

## 📦 **Python Package Dependencies**

### **Total Packages:** 150+ (all managed via requirements.txt)

### **Core Categories:**

1. **Web Framework:** Flask, Werkzeug, Jinja2
2. **Vector Database:** ChromaDB (with ONNX runtime)
3. **LLM Framework:** Ollama, LangChain
4. **Document Processing:**
   - PDF: pdfminer.six, pypdf
   - Office: python-docx, python-pptx, openpyxl
   - Images: Pillow, pytesseract
   - Audio: SpeechRecognition, pydub
5. **File Monitoring:** watchdog
6. **Data Processing:** numpy, pydantic, marshmallow
7. **HTTP:** requests, httpx
8. **Security:** cryptography, bcrypt

See `requirements.txt` for complete list with versions.

---

## 🚀 **Complete Installation Guide**

### **Windows Installation (Step-by-Step)**

```powershell
# Step 1: Install Visual Studio Build Tools
# Download and install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Select: "Desktop development with C++"

# Step 2: Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR
# Add to PATH

# Step 3: Install Ollama
# Download from: https://ollama.ai/download
# Run installer
ollama pull llama3.2

# Step 4: Clone/Download Project
cd "d:\clg\ty winter internship"
git clone <your-repo-url>  # Or download ZIP
cd "rag based"

# Step 5: Create Virtual Environment
python -m venv venv
venv\Scripts\activate

# Step 6: Upgrade pip
python -m pip install --upgrade pip

# Step 7: Install Python Packages
pip install -r requirements.txt
# This takes 5-10 minutes

# Step 8: Verify Installation
python -c "import chromadb, ollama, flask; print('✅ All core packages installed!')"

# Step 9: Run Application
python app.py
# Open browser: http://localhost:5000
```

---

### **Linux Installation (Ubuntu/Debian)**

```bash
# Step 1: System Dependencies
sudo apt-get update
sudo apt-get install -y build-essential python3-dev python3-pip python3-venv
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng

# Step 2: Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

# Step 3: Clone Project
git clone <your-repo-url>
cd "rag based"

# Step 4: Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Step 5: Upgrade pip
pip install --upgrade pip

# Step 6: Install Requirements
pip install -r requirements.txt

# Step 7: Verify
python -c "import chromadb, ollama, flask; print('✅ Success!')"

# Step 8: Run
python app.py
```

---

## ⚠️ **Common Installation Issues**

### **Issue 1: "Microsoft Visual C++ 14.0 is required"**

**Solution:**
- Install Visual Studio Build Tools
- Select "Desktop development with C++" workload
- Restart terminal after installation

---

### **Issue 2: "tesseract is not installed or it's not in your PATH"**

**Solution:**
```powershell
# Windows:
# 1. Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
# 2. Add to PATH: C:\Program Files\Tesseract-OCR
# 3. Restart terminal

# Linux:
sudo apt-get install tesseract-ocr

# Verify:
tesseract --version
```

---

### **Issue 3: "Could not connect to Ollama"**

**Solution:**
```powershell
# Check if Ollama is running
ollama list

# If not running, start it:
# Windows: Ollama runs as Windows service (starts automatically)
# Linux: ollama serve

# Pull model if missing:
ollama pull llama3.2
```

---

### **Issue 4: ChromaDB Import Error**

**Solution:**
```powershell
# Ensure Python version is 3.10-3.12
python --version

# If wrong version, install correct Python
# Then recreate venv with correct version

# Reinstall ChromaDB
pip install --force-reinstall chromadb
```

---

### **Issue 5: Slow Package Installation**

**Solution:**
```powershell
# Use faster mirror (Windows/Linux)
pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Or upgrade pip first
python -m pip install --upgrade pip
```

---

## 🖥️ **Hardware Recommendations**

### **Minimum Requirements:**
- **CPU:** 4 cores (Intel i5/AMD Ryzen 5 or better)
- **RAM:** 8GB
- **Storage:** 10GB free space
- **GPU:** Not required (CPU-only works)

### **Recommended for Best Performance:**
- **CPU:** 8 cores (Intel i7/AMD Ryzen 7)
- **RAM:** 16GB
- **Storage:** 20GB SSD
- **GPU:** NVIDIA GPU with 6GB+ VRAM (for 5-20x faster responses)

### **With GPU (Optional but Recommended):**
- **Requirements:**
  - NVIDIA GPU (GTX 1060 6GB or better)
  - CUDA Toolkit 11.8 or 12.x
  - Ollama automatically uses GPU (no config needed)
- **Benefits:**
  - 5-20x faster LLM generation
  - Handle larger models (7B, 13B parameters)

---

## 📊 **Disk Space Breakdown**

```
Python + venv:         ~1.5 GB
Pip packages:          ~3 GB
Ollama + llama3.2:     ~2 GB
ChromaDB database:     ~500 MB (331 docs)
Tesseract OCR:         ~100 MB
VS Build Tools:        ~6 GB
----------------------------------
Total:                 ~13 GB
```

---

## 🔍 **Verification Commands**

Run these to verify everything is installed:

```powershell
# Python version
python --version
# Expected: Python 3.12.0

# Pip version
pip --version
# Expected: pip 25.x or higher

# Tesseract
tesseract --version
# Expected: tesseract 5.3.x

# Ollama
ollama list
# Expected: llama3.2 listed

# Visual C++ (Windows only)
where cl
# Expected: Path to cl.exe

# Import test
python -c "import chromadb, ollama, flask, pytesseract; print('✅ All dependencies OK!')"
# Expected: No errors

# Full system check
python -c "
import sys
import chromadb
import ollama
import flask
import pytesseract
import numpy
import PIL

print(f'✅ Python: {sys.version}')
print(f'✅ ChromaDB: {chromadb.__version__}')
print(f'✅ Flask: {flask.__version__}')
print(f'✅ NumPy: {numpy.__version__}')
print('✅ All core packages working!')
"
```

---

## 🎯 **Quick Start After Installation**

```powershell
# 1. Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux

# 2. Verify Ollama is running
ollama list

# 3. Start web app
python app.py

# 4. Start file watcher (in another terminal)
python watcher.py

# 5. Open browser
# http://localhost:5000
```

---

## 📚 **Additional Resources**

- **Python:** https://www.python.org/downloads/
- **Visual Studio Build Tools:** https://visualstudio.microsoft.com/visual-cpp-build-tools/
- **Tesseract OCR:** https://github.com/tesseract-ocr/tesseract
- **Ollama:** https://ollama.ai/
- **ChromaDB:** https://docs.trychroma.com/
- **Flask:** https://flask.palletsprojects.com/

---

**System fully configured? Run `python app.py` to start! 🚀**
