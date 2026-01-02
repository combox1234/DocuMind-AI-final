import os
import logging
from pathlib import Path
from celery import Celery
import shutil
import hashlib
from datetime import datetime
import redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core modules
from config import Config
from core import DatabaseManager, LLMService, FileProcessor
from models import Document

# Initialize Celery
celery_app = Celery('documind_worker', broker=Config.CELERY_BROKER_URL)
celery_app.conf.update(
    result_backend=Config.CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Initialize Services (Lazy loading to avoid fork issues)
db_manager = None
llm_service = None
file_processor = None
redis_client = None

def get_services():
    """Lazy load services to ensure connection safety in workers"""
    global db_manager, llm_service, file_processor, redis_client
    if db_manager is None:
        db_manager = DatabaseManager(Config.DB_DIR)
    if llm_service is None:
        llm_service = LLMService(model=Config.LLM_MODEL)
    if file_processor is None:
        file_processor = FileProcessor()
    if redis_client is None:
        redis_client = redis.Redis.from_url(Config.CELERY_BROKER_URL, decode_responses=True)
    return db_manager, llm_service, file_processor, redis_client

def get_adaptive_chunk_size(file_size_mb):
    """Calculate optimal chunk size based on file size"""
    if file_size_mb > 10:
        return Config.CHUNK_SIZE_LARGE  # 2000 for large files
    elif file_size_mb > 1:
        return Config.CHUNK_SIZE_MEDIUM  # 1500 for medium files
    else:
        return Config.CHUNK_SIZE_SMALL  # 1000 for small files

def calculate_file_hash(filepath):
    """Calculate SHA256 hash of file content for duplicate detection"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {filepath}: {e}")
        return None

def check_duplicate(redis_client, file_hash):
    """Check if file hash already exists in Redis"""
    if not file_hash:
        return None
    existing_path = redis_client.hget(Config.REDIS_FILE_HASHES, file_hash)
    return existing_path

def store_file_hash(redis_client, file_hash, filepath):
    """Store file hash in Redis for duplicate detection"""
    if file_hash:
        redis_client.hset(Config.REDIS_FILE_HASHES, file_hash, str(filepath))

def get_date_folder():
    """Get current date folder in YYYY-MM format"""
    if Config.ENABLE_TIME_BASED_SORTING:
        return datetime.now().strftime(Config.DATE_FORMAT)
    return None

@celery_app.task(bind=True, name='worker.process_file_task')
def process_file_task(self, filepath_str):
    """
    Celery task to process a file asynchronously.
    Enhanced with:
    - Adaptive chunk sizing based on file size
    - Time-based sorting (YYYY-MM folders)
    - Duplicate detection via SHA256 hashing
    """
    filepath = Path(filepath_str)
    logger.info(f"🚀 [Worker] Picking up task for: {filepath.name}")
    
    # Get services
    db, llm, processor, redis_conn = get_services()
    
    try:
        # Check existence
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return {"status": "failed", "reason": "File not found"}

        # Get file size in MB
        file_size_bytes = filepath.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        # Calculate file hash for duplicate detection
        file_hash = calculate_file_hash(filepath)
        
        # Check for duplicates
        duplicate_path = check_duplicate(redis_conn, file_hash)
        if duplicate_path and Path(duplicate_path).exists():
            logger.warning(f"⚠️ [Worker] Duplicate detected: {filepath.name} (original: {duplicate_path})")
            # Store duplicate info but continue processing (user might want both)
        
        # 1. Extract Text
        text = processor.extract_text(filepath)
        if not text:
            text = f"File: {filepath.name}"
        
        # 2. Classify
        hierarchy = llm.classify_hierarchical(text, filepath.name)
        domain = hierarchy["domain"]
        category = hierarchy["category"]
        file_ext = hierarchy["file_extension"]
        
        # 3. Create Document
        document = processor.create_document(filepath, text, domain, category)
        
        # 4. Build sorting path with time-based folder
        date_folder = get_date_folder()
        if date_folder:
            category_dir = Config.SORTED_DIR / domain / category / file_ext / date_folder
        else:
            category_dir = Config.SORTED_DIR / domain / category / file_ext
        
        category_dir.mkdir(parents=True, exist_ok=True)
        dest_path = category_dir / filepath.name
        
        # Handle duplicates: OVERWRITE logic for "Live Updates"
        if dest_path.exists():
            logger.info(f"🔄 [Worker] File exists. Overwriting: {dest_path.name}")
            # 1. Remove old data from DB
            db.delete_by_filepath(str(dest_path))
            # 2. Remove old file
            try:
                os.remove(dest_path)
            except OSError as e:
                logger.warning(f"Could not remove existing file: {e}")
                # Fallback to rename if overwrite fails (e.g. file open)
                base_stem = filepath.stem
                suffix = filepath.suffix
                counter = 2
                while dest_path.exists():
                    dest_path = category_dir / f"{base_stem}_{counter}{suffix}"
                    counter += 1
        
        shutil.move(str(filepath), str(dest_path))
        document.filepath = dest_path  # Update path
        
        # 5. Determine adaptive chunk size
        chunk_size = get_adaptive_chunk_size(file_size_mb)
        logger.info(f"📏 [Worker] File size: {file_size_mb:.2f}MB, Chunk size: {chunk_size}")
        
        # 6. Create Chunks with adaptive sizing
        chunks = processor.create_chunks(document, chunk_size=chunk_size)
        
        # 7. Store in Database
        if chunks:
            db.add_chunks(chunks)
            
            # Store file hash and metadata in Redis
            store_file_hash(redis_conn, file_hash, dest_path)
            
            # Store file metadata
            metadata = {
                "size_mb": round(file_size_mb, 2),
                "chunk_size": chunk_size,
                "chunks_count": len(chunks),
                "domain": domain,
                "category": category,
                "uploaded_at": datetime.now().isoformat(),
                "file_hash": file_hash
            }
            redis_conn.hset(
                f"{Config.REDIS_FILE_METADATA}:{file_hash}",
                mapping=metadata
            )
            
            # CRITICAL: Update user_uploads table with the final sorted path
            # This ensures users can see the file in their list
            try:
                import sqlite3
                users_db_path = Config.DATA_DIR / 'users.db'
                if users_db_path.exists():
                    conn = sqlite3.connect(users_db_path)
                    cursor = conn.cursor()
                    
                    # Create relative path for DB (e.g., Domain/Category/ext/date/filename)
                    # Normalize to forward slashes for consistency
                    rel_path = dest_path.relative_to(Config.SORTED_DIR)
                    clean_sorted_path = str(rel_path).replace('\\', '/')
                    
                    # Update where filename matches and sorted_path is NULL (pending)
                    cursor.execute("""
                        UPDATE user_uploads 
                        SET sorted_path = ? 
                        WHERE filename = ? AND (sorted_path IS NULL OR sorted_path = '')
                    """, (clean_sorted_path, filepath.name))
                    
                    if cursor.rowcount > 0:
                        logger.info(f"✅ [Worker] Updated user_uploads sorted_path for {filepath.name}")
                    else:
                         # Fallback: maybe filename changed? But we match on original incoming filename.
                         # If rowcount is 0, maybe it was already updated or not found (e.g. CLI upload)
                         logger.warning(f"⚠️ [Worker] No pending upload record found for {filepath.name} to update sorted_path")
                         
                    conn.commit()
                    conn.close()
            except Exception as e:
                logger.error(f"❌ [Worker] Failed to update user_uploads table: {e}")
            
            logger.info(f"✅ [Worker] Processed {len(chunks)} chunks for {filepath.name}")
            return {
                "status": "success", 
                "filename": filepath.name, 
                "chunks": len(chunks),
                "chunk_size": chunk_size,
                "file_size_mb": round(file_size_mb, 2),
                "destination": str(dest_path),
                "is_duplicate": duplicate_path is not None
            }
        
    except Exception as e:
        logger.error(f"❌ [Worker] Error processing {filepath.name}: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}

    return {"status": "success", "message": "Processed but no chunks created"}
