from core.database import DatabaseManager
from pathlib import Path

db = DatabaseManager(Path('data/chroma_db'))
results = db.collection.get(limit=10, include=['metadatas'])

print(f"Total documents in ChromaDB: {db.get_count()}\n")
print("Sample documents:")
for m in results.get('metadatas', [])[:10]:
    print(f"  - File: {m.get('filename')}, Domain: {m.get('domain')}, Category: {m.get('category')}")
