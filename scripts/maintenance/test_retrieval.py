"""Quick test to check if Dr. Anjali Mehta query retrieves the lab report"""
from core import DatabaseManager
from config import Config

db = DatabaseManager(Config.DB_DIR)

# Test query
query = "Dr. Anjali Mehta"
print(f"Testing query: '{query}'")
print("=" * 60)

results = db.query(query, n_results=10)
print(f"\nFound {len(results)} results\n")

for i, result in enumerate(results, 1):
    print(f"{i}. File: {result.get('filename', 'unknown')}")
    print(f"   Distance: {result.get('distance', 'N/A')}")
    print(f"   Text preview: {result.get('text', '')[:150]}...")
    print()

# Also check what's in the database for this file
print("\n" + "=" * 60)
print("Checking database for lab_report_blood.txt:")
print("=" * 60)

all_results = db.collection.get()
metadatas = all_results.get('metadatas', [])
texts = all_results.get('documents', [])

for i, meta in enumerate(metadatas):
    filepath = meta.get('filepath', '')
    if 'lab_report_blood' in filepath:
        print(f"\nChunk {i+1}:")
        print(f"Filepath: {filepath}")
        print(f"Text: {texts[i][:200]}...")
