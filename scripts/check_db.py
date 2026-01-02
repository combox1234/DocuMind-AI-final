import chromadb
from chromadb.config import Settings
import os

try:
    # Point to the Docker volume mount location inside the container
    # But since we are running this script probably from the host, we point to the host path
    # relative to where we run it.
    
    # Check if we are running in Docker or Host
    if os.path.exists("/app/data"):
        DB_DIR = "/app/data/chroma_db_docker"
    else:
        DB_DIR = "data/chroma_db_docker"

    print(f"Checking DB at: {DB_DIR}")

    client = chromadb.PersistentClient(path=DB_DIR)
    
    print("Collections:")
    for col in client.list_collections():
        print(f" - {col.name}: {col.count()} docs")
        
except Exception as e:
    print(f"Error: {e}")
