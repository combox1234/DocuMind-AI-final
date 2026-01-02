
import logging
import shutil
from pathlib import Path
from core import DatabaseManager
from core.processor import FileProcessor
from models.document import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rebuild():
    BASE_DIR = Path(__file__).parent
    BASE_DIR = Path(__file__).parent
    # Use the same DB path as the application (from Config)
    from config import Config
    DB_DIR = Config.DB_DIR
    SORTED_DIR = BASE_DIR / "data/sorted"
    
    print("Starting Database Rebuild...")
    
    # 1. Nuke existing DB (Python way)
    if DB_DIR.exists():
        print(f"Removing existing DB at {DB_DIR}...")
        try:
            shutil.rmtree(DB_DIR)
        except Exception as e:
            print(f"Warning: Could not delete DB (file in use?): {e}")
            # If we can't delete, we might just overwrite chunks if IDs match, 
            # but we want to clear old junk.
            # Best is to ensure app is killed first.
            
    # 2. Init new DB
    db = DatabaseManager(DB_DIR)
    processor = FileProcessor()
    
    # 3. Scan and Ingest
    files = list(SORTED_DIR.rglob("*.*"))
    print(f"Found {len(files)} files in sorted directory.")
    
    count = 0
    for filepath in files:
        if filepath.is_file() and filepath.name != ".DS_Store":
            try:
                # Deduce category from path (e.g., .../Technology/DevOps/log/file.log -> Technology)
                # Structure: sorted/Domain/Category/Type/file
                parts = filepath.relative_to(SORTED_DIR).parts
                if len(parts) > 0:
                    domain = parts[0]
                else:
                    domain = "Uncategorized"
                    
                print(f"Processing: {filepath.name} ({domain})...")
                
                text = processor.extract_text(filepath)
                if not text or text.startswith("File: ") and filepath.suffix in ['.log', '.txt']:
                     # Double check log extraction
                     pass
                
                # Use larger chunks to keep headers with content
                doc = processor.create_document(filepath, text, domain)
                chunks = processor.create_chunks(doc, chunk_size=2000)
                
                if chunks:
                    db.add_chunks(chunks)
                    count += 1
            except Exception as e:
                print(f"Failed to process {filepath.name}: {e}")

    print(f"Rebuild Complete. Processed {count} files.")

if __name__ == "__main__":
    rebuild()
