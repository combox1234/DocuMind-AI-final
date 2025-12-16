"""
Universal RAG System - File Watcher & Processing Backend (Refactored)
Clean, modular architecture with separation of concerns
"""

import os
import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core import DatabaseManager, LLMService, FileProcessor
from models import Document

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INCOMING_DIR = DATA_DIR / "incoming"
SORTED_DIR = DATA_DIR / "sorted"
DB_DIR = DATA_DIR / "database"

# Files to skip (templates, configs, backups)
SKIP_FILES = {
    'index.html', 'index_backup.html', 'index_backup_2.html', '.gitignore', '.env',
    'config.py', 'setup.py', 'requirements.txt', 'watcher.py', 'app.py', 'cleanup.py'
}

SKIP_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.sh', '.bat'}

def should_skip_file(filepath: Path) -> bool:
    """Check if file should be skipped"""
    if filepath.name in SKIP_FILES:
        return True
    if filepath.suffix.lower() in SKIP_EXTENSIONS:
        return True
    if filepath.name.startswith('.'):
        return True
    return False

# Ensure directories exist
INCOMING_DIR.mkdir(parents=True, exist_ok=True)
SORTED_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# Initialize services
db_manager = DatabaseManager(DB_DIR)
llm_service = LLMService(model='llama3.2')
file_processor = FileProcessor()

# Track processed files
processed_files = {}

def process_file(filepath):
    """Process a single file: extract, chunk, classify, store"""
    filepath = Path(filepath)
    
    if not filepath.exists() or not filepath.is_file():
        return
    
    # Skip template and config files
    if should_skip_file(filepath):
        logger.info(f"⊘ Skipped (blacklist): {filepath.name}")
        return
    
    logger.info(f"Processing file: {filepath.name}")
    
    try:
        # Extract text
        text = file_processor.extract_text(filepath)
        if not text:
            text = f"File: {filepath.name}"
        
        logger.info(f"Extracted {len(text)} characters from {filepath.name}")
        
        # Classify content
        category = llm_service.classify_content(text)
        logger.info(f"Classified as: {category}")
        
        # Create document object
        document = file_processor.create_document(filepath, text, category)
        
        # Extract topic from filename (e.g., "UAV - Unit 1.pptx" -> "UAV")
        def extract_topic(filename: str) -> str:
            """Extract meaningful topic from filename"""
            name = Path(filename).stem  # Remove extension
            # Split on common separators and take first meaningful part
            for sep in [' - ', '_', ' ']:
                if sep in name:
                    topic = name.split(sep)[0].strip()
                    if len(topic) > 2:  # Avoid single letters
                        return topic
            return None
        
        # Determine target directory with topic-based nesting
        ext = filepath.suffix.lower().lstrip('.')
        topic = extract_topic(filepath.name)
        
        if category in ("BackendCode", "FrontendCode", "Code"):
            code_root = SORTED_DIR / "Code"
            if category == "BackendCode":
                sub = "Backend"
            elif category == "FrontendCode":
                sub = "Frontend"
            else:  # Generic Code category
                sub = ext if ext else "general"
            # Create nested folders: Code/<sub>/<ext>
            if category in ("BackendCode", "FrontendCode"):
                category_dir = code_root / sub / (ext if ext else "unknown")
            else:
                category_dir = code_root / sub
        else:
            # For non-code categories: Category/Topic/Extension (if topic exists)
            if topic:
                category_dir = SORTED_DIR / category / topic / (ext if ext else "files")
            else:
                category_dir = SORTED_DIR / category / (ext if ext else "files")
        
        category_dir.mkdir(parents=True, exist_ok=True)

        # Move file to sorted directory
        dest_path = category_dir / filepath.name
        
        # Handle duplicate filenames with clean numbering (not cascading)
        if dest_path.exists():
            base_stem = filepath.stem
            suffix = filepath.suffix
            counter = 2
            while dest_path.exists():
                dest_path = category_dir / f"{base_stem}_{counter}{suffix}"
                counter += 1
            logger.info(f"File exists, using clean name: {dest_path.name}")
        
        shutil.move(str(filepath), str(dest_path))
        logger.info(f"Moved to: {dest_path}")
        
        # Update document filepath
        document.filepath = dest_path
        
        # Create chunks with better context preservation
        chunks = file_processor.create_chunks(document, chunk_size=600)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Store in ChromaDB
        if chunks:
            db_manager.add_chunks(chunks)
            
            # Track processed file
            processed_files[document.file_hash] = {
                'filename': document.filename,
                'path': str(dest_path),
                'chunk_ids': [chunk.chunk_id for chunk in chunks]
            }
            
            logger.info(f"Added {len(chunks)} chunks to database")
        
        logger.info(f"✓ Successfully processed: {filepath.name}")
        
    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")

def remove_file_from_db(filepath):
    """Remove file vectors from database when file is deleted"""
    filepath = Path(filepath)
    
    try:
        # Prefer removing by tracked file hash
        file_hash = None
        for hash_key, info in processed_files.items():
            if info['path'] == str(filepath):
                file_hash = hash_key
                break
        
        deleted_count = 0
        if file_hash:
            deleted_count = db_manager.delete_by_hash(file_hash)
            if file_hash in processed_files:
                del processed_files[file_hash]
        else:
            # Fallback: remove by filepath metadata if hash not tracked
            deleted_count = db_manager.delete_by_filepath(str(filepath))
        
        logger.info(f"Removed {deleted_count} chunks from database for {filepath.name}")
        
    except Exception as e:
        logger.error(f"Error removing file from database: {e}")



class FileWatcherHandler(FileSystemEventHandler):
    """Handle file system events (files and folders)"""
    
    def on_created(self, event):
        # Wait a bit to ensure file/folder is fully written
        time.sleep(1)
        
        if event.is_directory:
            logger.info(f"New folder detected: {event.src_path}")
            process_folder_recursive(event.src_path)
        else:
            logger.info(f"New file detected: {event.src_path}")
            process_file(event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")
            remove_file_from_db(event.src_path)
        else:
            logger.info(f"Folder deleted: {event.src_path}")


def process_folder_recursive(folder_path):
    """Recursively process all files in a folder and its subfolders"""
    folder_path = Path(folder_path)
    
    if not folder_path.is_dir():
        logger.warning(f"Path is not a folder: {folder_path}")
        return
    
    logger.info(f"Processing folder recursively: {folder_path}")
    file_count = 0
    
    # Walk through all subdirectories
    for item in folder_path.rglob('*'):
        if item.is_file():
            try:
                process_file(item)
                file_count += 1
            except Exception as e:
                logger.error(f"Error processing file {item}: {e}")
    
    logger.info(f"Completed folder processing: {file_count} files processed")


def process_existing_files():
    """Process any existing files/folders in incoming directory recursively"""
    logger.info("Checking for existing files and folders in incoming directory...")
    
    for item in INCOMING_DIR.iterdir():
        if item.is_file():
            process_file(item)
        elif item.is_dir():
            # Recursively process folders
            process_folder_recursive(item)


def sync_sorted_with_db():
    """Clean up DB entries for deleted files only (no re-processing)"""
    try:
        # Only remove DB entries whose files no longer exist
        results = db_manager.collection.get()
        ids = results.get('ids', [])
        metadatas = results.get('metadatas', [])
        to_delete = []
        for i, meta in enumerate(metadatas):
            fp = meta.get('filepath')
            if fp and not Path(fp).exists():
                to_delete.append(ids[i])
        if to_delete:
            db_manager.collection.delete(ids=to_delete)
            logger.info(f"Pruned {len(to_delete)} dangling chunks from DB (files missing)")
    except Exception as e:
        logger.error(f"Error during sync: {e}")


def start_watching():
    """Start the file watcher"""
    logger.info("=" * 60)
    logger.info("DocuMind AI - File Watcher Started")
    logger.info("=" * 60)
    logger.info(f"Monitoring incoming: {INCOMING_DIR}")
    logger.info(f"Monitoring sorted: {SORTED_DIR}")
    logger.info(f"Database: {DB_DIR}")
    logger.info("=" * 60)
    
    # Process existing incoming files first
    process_existing_files()
    # Initial sync between sorted folder and DB
    sync_sorted_with_db()
    
    # Setup watchdog for incoming directory only
    event_handler = FileWatcherHandler()
    observer_incoming = Observer()
    observer_incoming.schedule(event_handler, str(INCOMING_DIR), recursive=False)
    observer_incoming.start()
    
    logger.info("✓ Watcher active. Monitoring data/incoming/ for new files.")
    logger.info("Press Ctrl+C to stop...")
    
    try:
        while True:
            # Periodic sync to clean up deleted files from DB (every 60 seconds)
            sync_sorted_with_db()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Stopping file watcher...")
        observer_incoming.stop()
    
    observer_incoming.join()
    logger.info("File watcher stopped.")


if __name__ == "__main__":
    start_watching()
