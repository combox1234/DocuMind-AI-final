"""Test cases for ChromaDB database operations"""
import unittest
from pathlib import Path
from core.database import DatabaseManager
from models.document import Document, DocumentChunk


class TestDatabaseManager(unittest.TestCase):
    """Test ChromaDB operations"""
    
    @classmethod
    def setUpClass(cls):
        """Initialize database manager once for all tests"""
        cls.db = DatabaseManager(Path("data/database"))
    
    def test_database_initialization(self):
        """Database should initialize without errors"""
        self.assertIsNotNone(self.db)
        self.assertIsNotNone(self.db.collection)
    
    def test_add_chunks(self):
        """Should add chunks to database"""
        chunks = [
            DocumentChunk(
                chunk_id="test_1",
                document_hash="test_hash",
                text="Test chunk content",
                chunk_index=0,
                filename="test.txt",
                category="Test",
                filepath="test.txt"
            )
        ]
        
        try:
            self.db.add_chunks(chunks)
            # If no exception, test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"add_chunks failed: {e}")
    
    def test_query(self):
        """Should query for similar chunks"""
        # Add a test chunk first
        chunks = [
            DocumentChunk(
                chunk_id="search_1",
                document_hash="search_hash",
                text="Python programming language",
                chunk_index=0,
                filename="python.txt",
                category="Programming",
                filepath="python.txt"
            )
        ]
        self.db.add_chunks(chunks)
        
        # Search for it
        results = self.db.query("Python", n_results=1)
        self.assertIsInstance(results, list)
    
    def test_delete_by_hash(self):
        """Should delete chunks by file hash"""
        file_hash = "delete_hash"
        chunks = [
            DocumentChunk(
                chunk_id="delete_1",
                document_hash=file_hash,
                text="Content to delete",
                chunk_index=0,
                filename="delete_test.txt",
                category="Test",
                filepath="delete_test.txt"
            )
        ]
        
        self.db.add_chunks(chunks)
        deleted = self.db.delete_by_hash(file_hash)
        
        # Verify deletion
        self.assertGreater(deleted, 0)


if __name__ == '__main__':
    unittest.main()
