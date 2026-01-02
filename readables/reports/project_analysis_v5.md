# Project Analysis: DocuMind AI (V5)

## 1. Project Overview
**DocuMind AI** is a **Universal RAG (Retrieval-Augmented Generation) System** designed to be "Deployment Ready". It focuses on **Strict RAG** (zero hallucinations), clear citations, and modular architecture.

**Current Version:** V5
**Key Goals:**
- Zero hallucination (Strict RAG) with citations.
- Clean architecture and modularity.
- Hierarchical document classification.
- Robust file ingestion (PDF, Images, Audio, Code).

## 2. Architecture & Components

### A. Directory Structure
- **`app.py`**: Main Flask application entry point. Handles API routes, initializes services, and manages request flow.
- **`config.py`**: Central configuration for paths (Base, Data, Database), LLM settings (`llama3.2`), and Flask settings.
- **`core/`**: Contains the core business logic.
    - **`classifier.py`**: Hierarchical classification system.
    - **`llm.py`**: LLM interface (Ollama), Re-ranking (CrossEncoder), and Prompt Engineering.
    - **`processor.py`**: Orchestrates file processing and text extraction.
    - **`database.py`**: Wrapper around ChromaDB for vector storage.
    - **`chat_manager.py`**: Manages chat history JSONs in `data/`.
- **`data/`**: Stores incoming files, sorted documents (`sorted/`), and the vector database (`database/` or `chroma_db_v2`).

### B. Core Logic Analysis

#### 1. Document Processing (`core/processor.py`)
- **Capabilities**: Supports a wide range of file types including PDF (PyPDF), Images (OCR), Audio (Speech-to-Text), DOCX, PPTX, Excel, Code files, etc.
- **Organization**: Extracts text and creates `Document` and `DocumentChunk` objects ready for embedding.

#### 2. Classification (`core/classifier.py`)
- **Hierarchy**: Domain -> Category -> FileType.
- **Methodology**: 
    - **Guardrails**: Hardcoded rules for high-confidence matches (e.g., specific filenames or keywords like "aadhaar").
    - **Keyword Scoring**: Counts "strong" and "weak" keywords to score domains and categories.
    - **Confidence**: Calculates a confidence score based on matches.

#### 3. Vector Database (`core/database.py`)
- **Technology**: ChromaDB.
- **Storage**: Stores document chunks with metadata (filename, category, filepath).
- **Querying**: Basic similarity search + aggressive filtering (distance < 1.3) to ensure relevance.

#### 4. LLM & Retrieval (`core/llm.py`)
- **Model**: Uses `llama3.2` via `ollama`.
- **Reranking**: Uses `CrossEncoder` (`ms-marco-MiniLM-L-6-v2`) to re-score top 25 retrieved chunks for better precision.
- **Strict RAG Enforcement**:
    - **Prompt**: Explicitly instructs the model to *only* answer from provided documents.
    - **Validation**: Checks if the model output indicates "information not found" to prevent hallucinations.
    - **Citation**: Returns cited filenames and source snippets.
    - **Confidence**: Calculates a confidence score based on similarity and semantic distance.

### C. Application Flow (`app.py`)
1.  **Ingestion/Classification**: (Not fully visible in `app.py` query path, probably runs via `watcher.py` or manual extraction scripts not deeply analyzed yet, but `classifier` is initialized).
2.  **Query Handling (`/chat`)**:
    - Receives user query.
    - Queries `DatabaseManager` (Top 25).
    - Reranks results using `LLMService` (Top 5).
    - Generates response using Ollama with strict prompt.
    - Returns answer, citations, confidence score, and source snippets.
    - Saves chat history.

## 3. Key Observations
- **Robustness**: The system seems well-engineered for accuracy (reranking, strict filtering).
- **Modularity**: Separation of concerns is respected (Database, LLM, Classifier, Processor are decoupled).
- **Local-First**: Relies on local Ollama and ChromaDB, ensuring privacy.
- **Frontend**: Uses Flask templates (`index.html` not analyzed, but referenced).

## 4. Potential Areas for Improvement
- **Error Handling**: While present, robust error recovery for Ollama unavailability could be enhanced.
- **Ingestion Pipeline**: The connection between `watcher.py` (seen in file list) and the main app wasn't deeply inspected, but critical for automation.

## 5. Summary
The project is a sophisticated, locally-hosted RAG system with a strong emphasis on accuracy and document organization. The V5 codebse is clean and follows good practices.
