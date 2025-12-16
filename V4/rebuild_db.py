"""
Rebuild database from sorted files - for production deployment
"""
import os
from pathlib import Path
from core import DatabaseManager, FileProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SORTED_DIR = DATA_DIR / "sorted"
DB_DIR = DATA_DIR / "database"

# Initialize services
db_manager = DatabaseManager(DB_DIR)
file_processor = FileProcessor()

def rebuild_database():
    """Rebuild database from existing sorted files"""
    logger.info("=" * 60)
    logger.info("REBUILDING DATABASE FROM SORTED FILES")
    logger.info("=" * 60)
    
    total_files = 0
    total_chunks = 0
    
    # Walk through all sorted directories
    for category_dir in sorted(SORTED_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        logger.info(f"\nProcessing category: {category}")
        
        for filepath in category_dir.iterdir():
            if filepath.is_file() and not filepath.name.startswith('.'):
                try:
                    logger.info(f"  Processing: {filepath.name}")
                    
                    # Extract text
                    text = file_processor.extract_text(filepath)
                    
                    # Create document
                    document = file_processor.create_document(filepath, text, category)
                    
                    # Create chunks with new improved settings
                    chunks = file_processor.create_chunks(document, chunk_size=600)
                    
                    # Add to database
                    if chunks:
                        db_manager.add_chunks(chunks)
                        logger.info(f"    ✓ Added {len(chunks)} chunks")
                        total_files += 1
                        total_chunks += len(chunks)
                    
                except Exception as e:
                    logger.error(f"  ✗ Error processing {filepath.name}: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"REBUILD COMPLETE")
    logger.info(f"Total files: {total_files}")
    logger.info(f"Total chunks: {total_chunks}")
    logger.info(f"Documents in database: {db_manager.get_count()}")
    logger.info("=" * 60)

if __name__ == "__main__":
    rebuild_database()
