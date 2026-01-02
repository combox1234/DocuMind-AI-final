
import chromadb
from config import Config

try:
    client = chromadb.PersistentClient(path=str(Config.DB_DIR))
    collection = client.get_or_create_collection("documents")
    
    print(f"Total Documents: {collection.count()}")
    
    # Check if file is indexed
    target_file = "unit 1 part 2 Safety Training.pdf"
    
    # Query by metadata
    results = collection.get(
        where={"filename": target_file}
    )
    
    chunk_count = len(results['ids'])
    print(f"\nFile '{target_file}' - Chunks Found: {chunk_count}")
    
    if chunk_count > 0:
        print("Sample Chunk Content:")
        print(results['documents'][0][:500])
        
        # Check if Bhopal is in the chunks
        bhopal_count = sum(1 for doc in results['documents'] if "bhopal" in doc.lower())
        print(f"Chunks containing 'Bhopal': {bhopal_count}")
    else:
        print("❌ FILE NOT FOUND IN DATABASE")

except Exception as e:
    print(f"Error: {e}")
