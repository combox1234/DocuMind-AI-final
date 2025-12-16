"""ChromaDB database management"""
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Optional
import logging

from models.document import DocumentChunk

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages ChromaDB operations"""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Database initialized. Total documents: {self.collection.count()}")
    
    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Add document chunks to database"""
        if not chunks:
            return
        
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [chunk.to_metadata() for chunk in chunks]
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(chunks)} chunks to database")
    
    def query(self, query_text: str, n_results: int = 5) -> List[dict]:
        """Query database for relevant chunks with optimized matching"""
        if self.collection.count() == 0:
            return []
        
        try:
            # Get more results for better context coverage
            search_count = min(n_results * 4, self.collection.count())
            
            results = self.collection.query(
                query_texts=[query_text],
                n_results=search_count
            )
            
            chunks = []
            if results and results['documents'] and len(results['documents']) > 0:
                # Improved similarity filtering with better thresholds
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0
                    
                    # More aggressive filtering: distance < 1.3 for better recall
                    if distance < 1.3:
                        similarity = 1.0 - (distance / 2.0)
                        chunks.append({
                            'text': doc,
                            'filename': metadata.get('filename', 'Unknown'),
                            'category': metadata.get('category', 'Uncategorized'),
                            'filepath': metadata.get('filepath', ''),
                            'similarity': similarity,
                            'distance': distance
                        })
            
            # Sort by similarity (best first) and return top n_results
            chunks.sort(key=lambda x: x['similarity'], reverse=True)
            return chunks[:n_results]
            
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            return []
    
    def delete_by_hash(self, file_hash: str) -> int:
        """Delete all chunks for a given file hash"""
        try:
            results = self.collection.get(where={"file_hash": file_hash})
            if results and results.get('ids'):
                self.collection.delete(ids=results['ids'])
                deleted_count = len(results['ids'])
                logger.info(f"Deleted {deleted_count} chunks for file hash {file_hash}")
                return deleted_count
            return 0
        except Exception as e:
            logger.error(f"Error deleting chunks: {e}")
            return 0

    def delete_by_filepath(self, filepath: str) -> int:
        """Delete all chunks associated with a specific filepath"""
        try:
            results = self.collection.get(where={"filepath": filepath})
            if results and results.get('ids'):
                self.collection.delete(ids=results['ids'])
                deleted_count = len(results['ids'])
                logger.info(f"Deleted {deleted_count} chunks for filepath {filepath}")
                return deleted_count
            return 0
        except Exception as e:
            logger.error(f"Error deleting by filepath: {e}")
            return 0

    def has_filepath(self, filepath: str) -> bool:
        """Check if any chunks exist for the given filepath"""
        try:
            results = self.collection.get(where={"filepath": filepath}, limit=1)
            return bool(results and results.get('ids'))
        except Exception:
            return False
    
    def get_count(self) -> int:
        """Get total document count"""
        return self.collection.count()
