# Universal RAG System - Architecture Overview

## 🏗️ Modular Architecture

This project follows a **clean, modular architecture** with separation of concerns for maintainability and scalability.

---

## 📂 Directory Structure

```
rag-based/
│
├── app.py                      # Flask web application entry point
├── watcher.py                  # File monitoring service entry point
├── config.py                   # System configuration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
│
├── venv/                       # Python 3.12 virtual environment
│
├── models/                     # Data models (Domain layer)
│   ├── __init__.py
│   └── document.py             # Document and DocumentChunk classes
│
├── core/                       # Business logic (Service layer)
│   ├── __init__.py
│   ├── database.py             # DatabaseManager - ChromaDB operations
│   ├── llm.py                  # LLMService - Ollama interactions
│   └── processor.py            # FileProcessor - Orchestrates extraction
│
├── extractors/                 # Text extraction (Utility layer)
│   ├── __init__.py
│   ├── pdf_extractor.py        # PDF text extraction
│   ├── image_extractor.py      # OCR for images
│   ├── audio_extractor.py      # Speech-to-text
│   ├── document_extractor.py   # DOCX, TXT extraction
│   └── code_extractor.py       # Code files extraction
│
├── utils/                      # Helper functions
│   ├── __init__.py
│   ├── file_utils.py           # File operations (hash, type detection)
│   └── text_utils.py           # Text processing (chunking, cleaning)
│
├── templates/                  # Frontend
│   └── index.html              # Web interface
│
└── data/                       # Data storage
    ├── incoming/               # Upload folder
    ├── sorted/                 # Organized by category
    └── database/               # ChromaDB persistent storage
```

---

## 🔄 Application Flow

### File Processing Flow (watcher.py)

```
1. Watchdog detects new file in data/incoming/
   ↓
2. FileProcessor.extract_text()
   ├─→ PDFExtractor (for PDFs)
   ├─→ ImageExtractor (for images via OCR)
   ├─→ AudioExtractor (for audio via speech-to-text)
   ├─→ DocumentExtractor (for DOCX, TXT)
   └─→ CodeExtractor (for code files)
   ↓
3. LLMService.classify_content()
   - Uses Ollama to categorize content
   ↓
4. FileProcessor.create_chunks()
   - TextUtils.chunk_text() splits into 500-char chunks
   ↓
5. DatabaseManager.add_chunks()
   - Stores in ChromaDB with metadata
   ↓
6. File moved to data/sorted/{Category}/
```

### Query Flow (app.py)

```
1. User submits query via web interface
   ↓
2. DatabaseManager.query()
   - Semantic search in ChromaDB
   - Returns top 4 relevant chunks
   ↓
3. LLMService.generate_response()
   - Builds strict RAG prompt
   - Calls Ollama with context
   - Extracts citations
   ↓
4. Response returned to user with:
   - Answer text
   - Cited filenames
   - Download links
```

---

## 🧩 Component Details

### Models Layer (`models/`)

**Purpose**: Define data structures

**Components**:
- `Document`: Represents a processed file
  - filename, filepath, file_hash, category, text_content, etc.
- `DocumentChunk`: Represents a text chunk
  - chunk_id, text, metadata for ChromaDB

**Why**: Clean data contracts, type safety, easy serialization

---

### Core Layer (`core/`)

**Purpose**: Business logic and services

#### DatabaseManager (`database.py`)
- **Responsibilities**:
  - Initialize ChromaDB client
  - Add document chunks
  - Query for relevant chunks
  - Delete chunks by file hash
- **Dependencies**: chromadb, models.DocumentChunk

#### LLMService (`llm.py`)
- **Responsibilities**:
  - Classify content into categories
  - Generate strict RAG responses
  - Check Ollama availability
- **Dependencies**: ollama

#### FileProcessor (`processor.py`)
- **Responsibilities**:
  - Orchestrate text extraction
  - Create Document objects
  - Create DocumentChunk objects
- **Dependencies**: extractors, utils, models

---

### Extractors Layer (`extractors/`)

**Purpose**: File format-specific text extraction

Each extractor is **single-responsibility**:
- `PDFExtractor`: Uses pdfminer.six
- `ImageExtractor`: Uses pytesseract (OCR)
- `AudioExtractor`: Uses SpeechRecognition + pydub
- `DocumentExtractor`: Uses python-docx, plain text readers
- `CodeExtractor`: Plain text for code files

**Why**: Easy to add new file types, isolated dependencies

---

### Utils Layer (`utils/`)

**Purpose**: Reusable helper functions

#### FileUtils (`file_utils.py`)
- `get_file_hash()`: MD5 hash for deduplication
- `get_file_type()`: Categorize file by extension
- `list_zip_contents()`: Extract ZIP metadata

#### TextUtils (`text_utils.py`)
- `chunk_text()`: Split text into fixed-size chunks
- `clean_text()`: Normalize whitespace

---

## 🎯 Design Principles

### 1. **Separation of Concerns**
- Each module has ONE clear responsibility
- No business logic in extractors
- No file I/O in LLM service

### 2. **Dependency Injection**
- Services passed as parameters
- Easy to mock for testing
- Configuration externalized

### 3. **Single Responsibility Principle**
- Each class/function does ONE thing well
- Easy to understand, modify, test

### 4. **Open/Closed Principle**
- Easy to add new extractors without modifying core
- New file types = new extractor class

### 5. **DRY (Don't Repeat Yourself)**
- Common logic extracted to utils
- Reusable components

---

## 🔌 Extension Points

### Adding a New File Type

1. Create extractor in `extractors/`:
```python
# extractors/excel_extractor.py
import pandas as pd

class ExcelExtractor:
    @staticmethod
    def extract(filepath):
        df = pd.read_excel(filepath)
        return df.to_string()
```

2. Update `FileProcessor.extract_text()`:
```python
elif file_type == 'spreadsheet':
    return self.excel_extractor.extract(filepath)
```

3. Update `FileUtils.get_file_type()`:
```python
'spreadsheet': ['.xlsx', '.xls', '.csv']
```

### Adding a New Feature

- **Custom chunking strategy**: Modify `TextUtils.chunk_text()`
- **Different LLM**: Modify `LLMService.__init__(model=...)`
- **Additional metadata**: Extend `Document` model
- **New API endpoint**: Add route in `app.py`

---

## 🧪 Testing Strategy

### Unit Tests
- Test each extractor independently
- Mock file I/O
- Test edge cases (empty files, corrupt files)

### Integration Tests
- Test DatabaseManager with real ChromaDB
- Test LLMService with Ollama
- Test full processing pipeline

### Example Test Structure
```
tests/
├── test_extractors.py
├── test_database.py
├── test_llm.py
├── test_processor.py
└── test_utils.py
```

---

## 🚀 Performance Optimizations

### Current
- Synchronous processing
- File-by-file

### Future Enhancements
1. **Async Processing**
   - Use `asyncio` for parallel extraction
   - Process multiple files simultaneously

2. **Batch Database Inserts**
   - Collect chunks, insert in batches
   - Reduce ChromaDB overhead

3. **Caching**
   - Cache file hashes to avoid reprocessing
   - Cache LLM classifications

4. **Streaming**
   - Stream large file processing
   - Chunked reading for big PDFs

---

## 🔒 Security Considerations

1. **Input Validation**
   - Validate file types before processing
   - Limit file sizes
   - Sanitize filenames

2. **Path Traversal Protection**
   - Use `Path` for safe path operations
   - Validate destination paths

3. **Resource Limits**
   - Limit chunk size
   - Timeout on long operations

---

## 📊 Scalability

### Vertical Scaling
- More RAM → More documents in ChromaDB
- Faster CPU → Faster LLM inference
- SSD → Faster file I/O

### Horizontal Scaling
- Multiple watcher instances (different folders)
- Load balancer for Flask app
- Distributed ChromaDB (future)

---

## 🛠️ Development Workflow

1. **Local Development**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Services**
   ```bash
   # Terminal 1
   python watcher.py
   
   # Terminal 2
   python app.py
   ```

3. **Code Style**
   - Follow PEP 8
   - Use type hints where possible
   - Document public functions

---

## 📖 References

- **Flask**: https://flask.palletsprojects.com/
- **ChromaDB**: https://docs.trychroma.com/
- **Ollama**: https://ollama.ai/
- **Watchdog**: https://python-watchdog.readthedocs.io/

---

**Last Updated**: December 10, 2025  
**Python Version**: 3.12  
**Architecture**: Modular, Service-Oriented
