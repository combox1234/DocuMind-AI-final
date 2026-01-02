
# 🎨 DocuMind Architecture Generator
# Prerequisites:
# 1. pip install diagrams
# 2. Install Graphviz (https://graphviz.org/download/) and add to PATH

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.programming.language import Python
from diagrams.onprem.database import Postgresql  # More standard
from diagrams.onprem.inmemory import Redis
# Removed onprem.ml as it causes issues on some versions
from diagrams.generic.storage import Storage

with Diagram("DocuMind AI System Architecture", show=False, direction="LR"):
    
    user = User("User (Web/API)")
    
    with Cluster("Ingestion Pipeline"):
        watcher = Python("Watcher Service")
        processor = Python("File Processor")
        
        with Cluster("Extraction Layer"):
            tesseract = Server("OCR (Tesseract)")
            ffmpeg = Server("Audio (FFmpeg)")
        
        watcher >> Edge(label="Detects PDF") >> processor
        processor >> tesseract
        processor >> ffmpeg
    
    with Cluster("Core Storage & Logic"):
        redis = Redis("Memurai (Cache)")
        chroma = Postgresql("ChromaDB (Vectors)")
        
        processor >> Edge(label="Chunks") >> chroma
        processor >> Edge(label="Task Queue") >> redis
        
    with Cluster("Reasoning Engine (RAG)"):
        llm = Server("Llama 3.2 (Ollama)")
        reranker = Python("Cross-Encoder")
        
        # Retrieval Flow
        user >> Edge(label="Query") >> processor
        processor >> Edge(label="Vector Search") >> chroma
        chroma >> Edge(label="Top 5 Docs") >> reranker
        reranker >> Edge(label="Filtered Ctx") >> llm
        llm >> Edge(label="Answer") >> user
