
import logging
from core import DatabaseManager, LLMService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from pathlib import Path

def verify():
    print("Initializng Stack...")
    
    BASE_DIR = Path(__file__).parent
    BASE_DIR = Path(__file__).parent
    from config import Config
    DB_DIR = Config.DB_DIR
    
    db = DatabaseManager(DB_DIR)
    llm = LLMService()
    
    query = "What specific error happened on Port 80 during deployment?"
    print(f"\nQuery: '{query}'")
    
    # 1. Raw Retrieval (DB)
    print("\n--- Phase 1: Raw Vector Search (Top 25) ---")
    raw_chunks = db.query(query, n_results=25)
    
    # Find rank of log file in raw results
    log_rank = -1
    for i, c in enumerate(raw_chunks):
        if "docker" in c['filename'].lower():
            log_rank = i + 1
            break
    print(f"Log File Rank (Vector Only): #{log_rank} (First occurence)")
    
    # 2. Re-ranked (LLM Service)
    print("\n--- Phase 2: Cross-Encoder Re-ranking (Top 5) ---")
    # We call the internal method manually to inspect scores, or just generate_response
    # Let's peek at the internal method
    reranked = llm._rerank_chunks(query, raw_chunks, top_k=5)
    
    for i, c in enumerate(reranked, 1):
        print(f"#{i}: {c['filename']} (Score: {c.get('relevance_score', 0):.4f})")
        if "docker" in c['filename'].lower():
            print("   TARGET FOUND!")

if __name__ == "__main__":
    verify()
