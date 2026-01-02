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
    
    def query(self, query_text: str, n_results: int = 5, user_role: str = None):
        """Query database for relevant chunks with role-based access control
        
        Args:
            query_text: The search query
            n_results: Number of results to return
            user_role: User's role for access control filtering (None = no filtering)
            
        Returns:
            Tuple of (chunks: List[dict], rbac_filtered: bool)
            rbac_filtered=True means documents existed but were blocked by permissions
        """
        if self.collection.count() == 0:
            return [], False
        
        try:
            # Import permissions module
            from core.permissions import check_file_access
            
            # Get more results for better context coverage
            search_count = min(n_results * 4, self.collection.count())
            
            results = self.collection.query(
                query_texts=[query_text],
                n_results=search_count
            )
            
            chunks = []
            rbac_blocked_count = 0  # Track how many were blocked by RBAC
            
            if results and results['documents'] and len(results['documents']) > 0:
                # Improved similarity filtering with better thresholds
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results.get('metadatas') and results['metadatas'][0] else {}
                    distance = results['distances'][0][i] if results.get('distances') and results['distances'][0] else 0
                    
                    # More aggressive filtering: distance < 1.3 for better recall
                    if distance < 1.3:
                        # RBAC FILTERING: Check file access if role provided
                        if user_role:
                            file_domain = metadata.get('domain', 'Unknown')
                            file_category = metadata.get('category', None)
                            
                            logger.debug(f"RBAC check: role={user_role}, domain={file_domain}, category={file_category}, file={metadata.get('filename')}")
                            
                            # Skip if user doesn't have permission
                            has_access = check_file_access(user_role, file_domain, file_category)
                            
                            if not has_access:
                                logger.debug(f"Access denied for {user_role} to {file_domain}/{file_category}")
                                rbac_blocked_count += 1
                                continue
                        
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
            
            # Return tuple: (chunks, was_rbac_filtered)
            # rbac_filtered = True if we had results but RBAC blocked them all
            rbac_filtered = (rbac_blocked_count > 0 and len(chunks) == 0)
            
            return chunks[:n_results], rbac_filtered
            
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            return [], False

    
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
    
    def get_full_file(self, filename: str) -> Optional[str]:
        """Retrieve ALL chunks for a specific filename and reassemble into full content
        
        Args:
            filename: Name of the file to retrieve (e.g., 'my_script.py')
            
        Returns:
            Full file content as string, or None if file not found
        """
        try:
            # Query for all chunks with exact filename match
            results = self.collection.get(
                where={"filename": filename},
                include=['documents', 'metadatas']
            )
            
            if not results or not results.get('documents'):
                logger.info(f"No chunks found for filename: {filename}")
                return None
            
            # Extract chunks with their indices
            chunks_data = []
            for i, doc in enumerate(results['documents']):
                metadata = results['metadatas'][i] if results.get('metadatas') else {}
                chunk_index = metadata.get('chunk_index', 0)
                chunks_data.append((chunk_index, doc))
            
            # Sort by chunk_index to maintain original order
            chunks_data.sort(key=lambda x: x[0])
            
            # Reassemble full content
            full_content = '\n'.join(chunk[1] for chunk in chunks_data)
            
            logger.info(f"Retrieved full file '{filename}' with {len(chunks_data)} chunks")
            return full_content
            
        except Exception as e:
            logger.error(f"Error retrieving full file '{filename}': {e}")
            return None

