"""Configuration for Universal RAG System"""
from pathlib import Path

class Config:
    """System configuration"""
    
    # Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    INCOMING_DIR = DATA_DIR / "incoming"
    SORTED_DIR = DATA_DIR / "sorted"
    DB_DIR = DATA_DIR / "database"
    
    # LLM Settings
    LLM_MODEL = "llama3.2"
    
    # Processing Settings
    CHUNK_SIZE = 500
    TOP_K_RETRIEVAL = 4
    
    # Flask Settings
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 5000
    FLASK_DEBUG = True
