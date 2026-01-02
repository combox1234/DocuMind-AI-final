
import logging
from config import Config
from core import DatabaseManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inspect_chunks():
    print(f"\nUsing Database Directory: {Config.DB_DIR}")
    db = DatabaseManager(Config.DB_DIR)
    
    target_filename = "lab_report_blood.txt"
    print(f"\n--- Inspecting Chunks for: {target_filename} ---")
    
    # Get all chunks from the collection (filtering by filename metadata is tricky in pure chroma query if not exact match on ID, 
    # but we can fetch all and filter client side for inspection since DB is small)
    
    # Better: Query with a dummy embedding or keyword but high k, then filter
    results = db.collection.get()
    
    ids = results['ids']
    metadatas = results['metadatas']
    documents = results['documents']
    
    found_chunks = []
    
    for i, meta in enumerate(metadatas):
        if meta.get('filename') == target_filename:
            found_chunks.append({
                'id': ids[i],
                'text': documents[i],
                'meta': meta
            })
            
    print(f"Found {len(found_chunks)} chunks for {target_filename}.")
    
    for i, chunk in enumerate(found_chunks):
        print(f"\n[Chunk #{i+1} | ID: {chunk['id']}]")
        print("-" * 40)
        print(chunk['text'])
        print("-" * 40)

if __name__ == "__main__":
    inspect_chunks()
