"""
Index all sorted files into ChromaDB with proper domain and category metadata
"""
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.processor import FileProcessor
from core.database import DatabaseManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def index_sorted_files():
    """Process all files in data/sorted and add to ChromaDB"""
    
    # Initialize
    processor = FileProcessor()
    db = DatabaseManager(Path('data/chroma_db'))
    
    sorted_dir = Path('data/sorted')
    
    if not sorted_dir.exists():
        logger.error(f"Sorted directory not found: {sorted_dir}")
        return
    
    # Track stats
    total_files = 0
    successful = 0
    failed = 0
    total_chunks = 0
    
    logger.info(f"Starting indexing from: {sorted_dir.absolute()}\n")
    
    # Traverse all files in sorted directory
    # Structure: data/sorted/DOMAIN/CATEGORY/...
    for domain_dir in sorted(sorted_dir.iterdir()):
        if not domain_dir.is_dir():
            continue
            
        domain = domain_dir.name
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing Domain: {domain}")
        logger.info(f"{'='*60}")
        
        for category_dir in sorted(domain_dir.iterdir()):
            if not category_dir.is_dir():
                continue
                
            category = category_dir.name
            logger.info(f"\n  Category: {category}")
            
            # Find all files recursively in this category
            for file_path in category_dir.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Skip hidden files and system files
                if file_path.name.startswith('.'):
                    continue
                    
                total_files += 1
                
                try:
                    logger.info(f"    Processing: {file_path.name}")
                    
                    # Process file with domain and category
                    chunks = processor.process_file(
                        filepath=str(file_path),
                        domain=domain,
                        category=category
                    )
                    
                    if chunks:
                        # Add to database
                        db.add_chunks(chunks)
                        total_chunks += len(chunks)
                        successful += 1
                        logger.info(f"      ✓ Indexed: {len(chunks)} chunks")
                    else:
                        failed += 1
                        logger.warning(f"      ✗ No chunks created")
                        
                except Exception as e:
                    failed += 1
                    logger.error(f"      ✗ Error: {e}")
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("INDEXING COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Total files found: {total_files}")
    logger.info(f"Successfully indexed: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total chunks created: {total_chunks}")
    logger.info(f"ChromaDB document count: {db.get_count()}")
    logger.info(f"{'='*60}\n")

if __name__ == "__main__":
    index_sorted_files()
