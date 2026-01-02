# Ubuntu/Linux Installation & Setup Guide

## 🐧 **Linux/Ubuntu System Requirements**

**Tested on:** Ubuntu 20.04 LTS, 22.04 LTS, 24.04 LTS, Debian 11+  
**Python Version:** 3.10, 3.11, or 3.12  
**Architecture:** x86_64 (AMD64) or ARM64  
**RAM:** 4GB minimum, 8GB recommended  
**Storage:** 8GB free space  

---

## 📋 **Prerequisites (System Packages)**

### **Ubuntu/Debian:**

```bash
# Update package list
sudo apt-get update

# Install Python 3 and development tools
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    gcc \
    g++ \
    make \
    cmake

# Install Tesseract OCR (for image text extraction)
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev

# Install system libraries (required for various packages)
sudo apt-get install -y \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libopenjp2-7-dev \
    libmagic1 \
    libmagic-dev \
    poppler-utils \
    ffmpeg

# Install Git (if not already installed)
sudo apt-get install -y git curl wget
```

### **Fedora/RHEL/CentOS:**

```bash
# Install development tools
sudo dnf groupinstall "Development Tools"
sudo dnf install -y python3 python3-pip python3-devel

# Install Tesseract and libraries
sudo dnf install -y tesseract tesseract-langpack-eng

# Install system libraries
sudo dnf install -y \
    openssl-devel \
    libffi-devel \
    libxml2-devel \
    libxslt-devel \
    zlib-devel \
    libjpeg-devel \
    libpng-devel \
    file-devel \
    poppler-utils \
    ffmpeg
```

### **Arch Linux:**

```bash
# Install base packages
sudo pacman -S --needed \
    python \
    python-pip \
    base-devel \
    tesseract \
    tesseract-data-eng \
    libmagic \
    poppler \
    ffmpeg
```

---

## 🚀 **Complete Installation (Ubuntu/Debian)**

### **Step 1: Verify System Dependencies**

```bash
# Check Python version (should be 3.10+)
python3 --version

# Check if build tools are installed
gcc --version
make --version

# Check Tesseract
tesseract --version
```

---

### **Step 2: Install Ollama (LLM Runtime)**

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Start Ollama service (runs in background)
ollama serve &

# Pull the LLM model (2GB download)
ollama pull llama3.2

# Verify model is available
ollama list
```

**Note:** Ollama will run as a background service. Check status:
```bash
# Check if Ollama is running
ps aux | grep ollama

# Or use systemctl (if installed as service)
sudo systemctl status ollama
```

---

### **Step 3: Clone/Download Project**

```bash
# Navigate to your workspace
cd ~
mkdir -p projects
cd projects

# Clone repository (replace with your repo URL)
git clone <your-repo-url> rag-system
cd rag-system

# Or download and extract ZIP
wget <your-zip-url> -O rag-system.zip
unzip rag-system.zip
cd rag-system
```

---

### **Step 4: Create Virtual Environment**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Your prompt should now show (venv)
```

---

### **Step 5: Install Python Dependencies**

```bash
# Install from requirements.txt
pip install -r requirements.txt

# This takes 5-10 minutes depending on internet speed
# Watch for errors - most should install successfully
```

**If you encounter errors:**
```bash
# Install problematic packages individually
pip install Flask chromadb ollama langchain

# Then try full install again
pip install -r requirements.txt
```

---

### **Step 6: Verify Installation**

```bash
# Test core imports
python3 -c "
import flask
import chromadb
import ollama
import pytesseract
print('✅ All core packages installed successfully!')
"

# Test Tesseract
python3 -c "
import pytesseract
print('Tesseract version:', pytesseract.get_tesseract_version())
"

# Test Ollama connection
python3 -c "
import ollama
models = ollama.list()
print('✅ Ollama connected, models:', models)
"
```

---

### **Step 7: Prepare Data Directories**

```bash
# Create data directories (if not exist)
mkdir -p data/incoming
mkdir -p data/sorted
mkdir -p data/database
mkdir -p data/database_backup

# Set permissions
chmod -R 755 data/
```

---

### **Step 8: Run the Application**

#### **Option A: Run Web App Only**

```bash
# Activate virtual environment (if not already)
source venv/bin/activate

# Start web application
python3 app.py

# Open browser (if running with GUI)
xdg-open http://localhost:5000

# Or access from remote machine
# http://<server-ip>:5000
```

#### **Option B: Run File Watcher Only**

```bash
# In another terminal (or use tmux/screen)
source venv/bin/activate

# Start file watcher
python3 watcher.py

# Drop files into data/incoming/ folder
# They will be automatically processed
```

#### **Option C: Run Both (Recommended)**

**Using Terminal Multiplexer (tmux):**

```bash
# Install tmux if not installed
sudo apt-get install -y tmux

# Start tmux session
tmux new -s rag-system

# Split terminal horizontally
# Press: Ctrl+B then "

# In first pane (top)
source venv/bin/activate
python3 app.py

# Switch to second pane
# Press: Ctrl+B then Down Arrow

# In second pane (bottom)
source venv/bin/activate
python3 watcher.py

# Detach from session: Ctrl+B then D
# Reattach later: tmux attach -t rag-system
```

**Using Screen:**

```bash
# Install screen if not installed
sudo apt-get install -y screen

# Start screen session
screen -S rag-system

# Start web app
source venv/bin/activate
python3 app.py

# Create new window: Ctrl+A then C
# Start watcher in new window
source venv/bin/activate
python3 watcher.py

# Switch windows: Ctrl+A then N (next) or P (previous)
# Detach: Ctrl+A then D
# Reattach: screen -r rag-system
```

**Using Background Processes:**

```bash
# Activate venv
source venv/bin/activate

# Run web app in background
nohup python3 app.py > logs/app.log 2>&1 &

# Run watcher in background
nohup python3 watcher.py > logs/watcher.log 2>&1 &

# Check processes
ps aux | grep python3

# View logs
tail -f logs/app.log
tail -f logs/watcher.log

# Stop processes
pkill -f "python3 app.py"
pkill -f "python3 watcher.py"
```

---

## 🖥️ **Headless Server Setup (No GUI)**

### **Running on Remote Server via SSH:**

```bash
# Connect to server
ssh user@server-ip

# Follow installation steps above

# Run in background with nohup
cd ~/projects/rag-system
source venv/bin/activate

# Start services
nohup python3 app.py > app.log 2>&1 &
nohup python3 watcher.py > watcher.log 2>&1 &

# Check status
ps aux | grep python3

# Access web interface from local machine
# http://<server-ip>:5000

# View logs
tail -f app.log
tail -f watcher.log
```

---

## 🔧 **Creating System Services (Auto-start on Boot)**

### **Systemd Service for Web App:**

```bash
# Create service file
sudo nano /etc/systemd/system/rag-webapp.service
```

**Add content:**
```ini
[Unit]
Description=RAG System Web Application
After=network.target ollama.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/projects/rag-system
Environment="PATH=/home/YOUR_USERNAME/projects/rag-system/venv/bin"
ExecStart=/home/YOUR_USERNAME/projects/rag-system/venv/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable rag-webapp

# Start service now
sudo systemctl start rag-webapp

# Check status
sudo systemctl status rag-webapp

# View logs
sudo journalctl -u rag-webapp -f
```

### **Systemd Service for File Watcher:**

```bash
# Create service file
sudo nano /etc/systemd/system/rag-watcher.service
```

**Add content:**
```ini
[Unit]
Description=RAG System File Watcher
After=network.target ollama.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/projects/rag-system
Environment="PATH=/home/YOUR_USERNAME/projects/rag-system/venv/bin"
ExecStart=/home/YOUR_USERNAME/projects/rag-system/venv/bin/python3 watcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable rag-watcher
sudo systemctl start rag-watcher
sudo systemctl status rag-watcher
```

**Manage services:**
```bash
# Stop services
sudo systemctl stop rag-webapp
sudo systemctl stop rag-watcher

# Restart services
sudo systemctl restart rag-webapp
sudo systemctl restart rag-watcher

# View logs
sudo journalctl -u rag-webapp -n 50
sudo journalctl -u rag-watcher -n 50
```

---

## 🌐 **Access from Remote Machine**

### **Configure Firewall:**

```bash
# Allow port 5000 (UFW firewall)
sudo ufw allow 5000/tcp
sudo ufw status

# Or using iptables
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

### **Access from Browser:**

```
http://<server-ip>:5000
```

### **Using Nginx as Reverse Proxy (Optional):**

```bash
# Install Nginx
sudo apt-get install -y nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/rag-system
```

**Add content:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Or server IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/rag-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Now access via: `http://your-domain.com` (port 80)

---

## 📊 **System Resource Usage**

```bash
# Monitor Python processes
htop
# Filter by: python3

# Check disk usage
df -h
du -sh data/

# Check RAM usage
free -h

# Monitor Ollama
ps aux | grep ollama
```

---

## 🐛 **Troubleshooting**

### **Issue 1: "Permission denied" errors**

```bash
# Fix file permissions
chmod -R 755 ~/projects/rag-system
chmod +x app.py watcher.py

# Fix data directory permissions
chmod -R 755 data/
```

---

### **Issue 2: Ollama not connecting**

```bash
# Check if Ollama is running
ps aux | grep ollama

# If not running, start it
ollama serve &

# Or as systemd service
sudo systemctl start ollama
sudo systemctl status ollama

# Test connection
curl http://localhost:11434/api/tags
```

---

### **Issue 3: Port 5000 already in use**

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process
kill -9 <PID>

# Or change port in app.py
nano app.py
# Change: app.run(..., port=5000)
# To:     app.run(..., port=8080)
```

---

### **Issue 4: Missing system libraries**

```bash
# Install common missing libraries
sudo apt-get install -y \
    libmagic1 \
    libmagic-dev \
    tesseract-ocr \
    libtesseract-dev \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev

# Then reinstall Python packages
pip install --force-reinstall -r requirements.txt
```

---

### **Issue 5: ChromaDB SQLite errors**

```bash
# Install SQLite3 development files
sudo apt-get install -y libsqlite3-dev

# Rebuild ChromaDB
pip uninstall chromadb
pip install chromadb --no-cache-dir
```

---

## 📦 **Package Installation Size (Ubuntu)**

```
System packages:        ~500 MB
Python + venv:          ~200 MB
Pip packages:           ~2.5 GB
Ollama + model:         ~2.0 GB
Tesseract data:         ~50 MB
Database (after use):   ~500 MB
------------------------------------------
Total:                  ~5.75 GB
```

---

## 🔐 **Security Recommendations**

```bash
# Run as non-root user (RECOMMENDED)
# DO NOT run as root/sudo

# Create dedicated user
sudo adduser raguser
sudo usermod -aG sudo raguser

# Switch to user
su - raguser

# Install everything as this user

# Restrict data directory access
chmod 700 data/

# Use firewall
sudo ufw enable
sudo ufw allow 5000/tcp
sudo ufw allow ssh

# Keep system updated
sudo apt-get update && sudo apt-get upgrade -y
```

---

## 🚀 **Quick Start Script**

**Create `install.sh`:**

```bash
#!/bin/bash
set -e

echo "🚀 Installing RAG System on Ubuntu/Linux..."

# Update system
sudo apt-get update

# Install system dependencies
sudo apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    build-essential gcc g++ make cmake \
    tesseract-ocr tesseract-ocr-eng libtesseract-dev \
    libssl-dev libffi-dev libxml2-dev libxslt1-dev \
    zlib1g-dev libjpeg-dev libpng-dev libtiff-dev \
    libmagic1 libmagic-dev poppler-utils ffmpeg \
    git curl wget tmux

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve &
sleep 5

# Pull model
ollama pull llama3.2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Create data directories
mkdir -p data/{incoming,sorted,database,database_backup}

# Verify installation
python3 -c "import flask, chromadb, ollama; print('✅ Installation complete!')"

echo "✅ Setup complete! Run: source venv/bin/activate && python3 app.py"
```

**Run script:**
```bash
chmod +x install.sh
./install.sh
```

---

## 📚 **Additional Linux Resources**

- **Ubuntu Server Guide:** https://ubuntu.com/server/docs
- **Systemd Services:** https://www.freedesktop.org/software/systemd/man/systemd.service.html
- **Nginx Documentation:** https://nginx.org/en/docs/
- **tmux Guide:** https://github.com/tmux/tmux/wiki
- **Python Virtual Environments:** https://docs.python.org/3/library/venv.html

---

## ✅ **Verification Commands**

```bash
# System check
uname -a
python3 --version
pip --version
tesseract --version
ollama --version

# Service check
systemctl status ollama
systemctl status rag-webapp
systemctl status rag-watcher

# Resource check
df -h
free -h
htop

# Application check
curl http://localhost:5000
curl http://localhost:11434/api/tags

# Logs check
tail -f logs/app.log
tail -f logs/watcher.log
sudo journalctl -u rag-webapp -f
```

---

**Your RAG system is now ready on Ubuntu/Linux! 🐧🚀**

**Start services:**
```bash
source venv/bin/activate
python3 app.py  # Web interface
python3 watcher.py  # File processor
```

**Access:** http://localhost:5000 or http://<server-ip>:5000
