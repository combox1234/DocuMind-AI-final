"""Configuration for Universal RAG System"""
from pathlib import Path

class Config:
    """System configuration"""
    
    # Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    INCOMING_DIR = DATA_DIR / "incoming"
    SORTED_DIR = DATA_DIR / "sorted"
    DB_DIR = DATA_DIR / __import__("os").environ.get("CHROMA_DB_DIR", "chroma_db_docker")
    
    # LLM Settings
    LLM_MODEL = "llama3.2"
    
    # JWT Settings
    JWT_SECRET_KEY = "super-secret-key-change-this-in-production"
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # Processing Settings
    CHUNK_SIZE = 2000  # Optimized for context retention
    CHUNK_SIZE_SMALL = 2000  # For files < 1MB
    CHUNK_SIZE_MEDIUM = 2500  # For files 1-10MB
    CHUNK_SIZE_LARGE = 3000  # For files > 10MB
    TOP_K_RETRIEVAL = 10
    
    # Sorting Settings
    DATE_FORMAT = "%Y-%m"  # YYYY-MM format for time-based folders
    ENABLE_TIME_BASED_SORTING = True
    
    # Flask Settings
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 5000
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Logging
    LOG_LEVEL = __import__("os").environ.get("LOG_LEVEL", "INFO")
    
    # Celery Settings
    CELERY_BROKER_URL = __import__("os").environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
    CELERY_RESULT_BACKEND = __import__("os").environ.get("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")
    
    # Redis Keys
    REDIS_FILE_HASHES = "file_hashes"
    REDIS_CUSTOM_CATEGORIES = "custom_categories"
    REDIS_ANALYTICS_CACHE = "analytics:stats"
    REDIS_LANGUAGE_STATS = "stats:languages"
    REDIS_FILE_METADATA = "file_metadata"
    
    # Manager Configuration (Simple role-based access)
    MANAGERS = ["admin", "manager"]  # Add manager usernames/emails here
