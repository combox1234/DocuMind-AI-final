
import logging
from pathlib import Path
from core import DatabaseManager, LLMService
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_fix():
    print("\n=== Verifying RAG Fix ===\n")
    
    # 1. Initialize with CORRECT Config path
    print(f"Using Database Directory: {Config.DB_DIR}")
    db = DatabaseManager(Config.DB_DIR)
    
    # Check if the file is indexed
    target_file = "lab_report_blood.txt"
    print(f"Checking for file: {target_file}")
    
    # Search by filename in chunks (rough check)
    # We can't easily check 'has_filepath' without the full path, 
    # so we'll query for the content.
    
    query = "Who is Dr. Anjali Mehta?"
    print(f"Query: '{query}'")
    
    results = db.query(query, n_results=10)
    
    found = False
    for i, chunk in enumerate(results):
        print(f"\n[Result #{i+1}]")
        print(f"File: {chunk.get('filename')}")
        print(f"Score: {chunk.get('similarity', 0.0):.4f}")
        print(f"Snippet: {chunk.get('text')[:100]}...")
        
        if target_file in chunk.get('filename', ''):
            found = True
            print(">>> TARGET FILE FOUND IN RESULTS! <<<")
            
    if found:
        print("\n✅ SUCCESS: The file is indexed and retrievable.")
    else:
        print("\n❌ FAILURE: The file was not found in the top results.")

if __name__ == "__main__":
    verify_fix()
