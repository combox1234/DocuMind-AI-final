"""
Fast database rebuild script
Rebuilds ChromaDB from sorted files with progress indication
"""

import logging
import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).parent.parent))

from core import DatabaseManager, FileProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rebuild_database_fast():
    """Rebuild database quickly with minimal ONNX operations"""
    
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    SORTED_DIR = DATA_DIR / "sorted"
    DB_DIR = DATA_DIR / "database"
    
    # Initialize database
    db_manager = DatabaseManager(DB_DIR)
    processor = FileProcessor()
    
    print("=" * 60)
    print("FAST DATABASE REBUILD")
    print("=" * 60)
    
    total_chunks = 0
    total_files = 0
    
    # Process each category
    for category_dir in sorted(SORTED_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        files = list(category_dir.glob('*'))
        
        if not files:
            continue
        
        print(f"\n📁 {category} ({len(files)} files)")
        
        for file_path in files:
            if file_path.is_file():
                try:
                    # Process file
                    chunks = processor.process_file(str(file_path), category)
                    
                    if chunks:
                        db_manager.add_chunks(chunks)
                        total_chunks += len(chunks)
                        total_files += 1
                        print(f"   ✓ {file_path.name} ({len(chunks)} chunks)")
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
    
    # Final count
    final_count = db_manager.get_count()
    
    print("\n" + "=" * 60)
    print(f"✅ REBUILD COMPLETE")
    print(f"   Files processed: {total_files}")
    print(f"   Total chunks: {total_chunks}")
    print(f"   Database count: {final_count}")
    print("=" * 60)

if __name__ == "__main__":
    rebuild_database_fast()
