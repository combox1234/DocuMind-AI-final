"""Integration tests for complete RAG pipeline"""
import unittest
import tempfile
from pathlib import Path
from core.processor import FileProcessor
from core.database import DatabaseManager
from core.llm import LLMService


class TestRAGPipeline(unittest.TestCase):
    """Test end-to-end RAG workflow"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.processor = FileProcessor()
        cls.db = DatabaseManager(Path("data/database"))
        cls.llm = LLMService()
        cls.llm_available = False
    
    def test_process_text_file_pipeline(self):
        """Test complete pipeline: file → extraction → chunking → storage"""
        if not self.llm_available:
            self.skipTest("Ollama not available")
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("The quick brown fox jumps over the lazy dog. " * 20)
            temp_path = Path(f.name)
        
        try:
            # Extract text and create chunks
            text = self.processor.extract_text(temp_path)
            self.assertGreater(len(text), 0)
            
            doc = self.processor.create_document(temp_path, text, "Test")
            chunks = self.processor.create_chunks(doc)
            self.db.add_chunks(chunks)
            
            # Search for content
            results = self.db.query("quick brown fox", n_results=1)
            
            self.assertGreater(len(results), 0)
            self.assertIn("fox", results[0]['text'].lower())
        
        finally:
            temp_path.unlink(missing_ok=True)
    
    def test_rag_question_answer(self):
        """Test complete RAG: add document → ask question → get answer"""
        if not self.llm_available:
            self.skipTest("Ollama not available")
        # Add test document
        test_content = "Albert Einstein developed the theory of relativity in 1905."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_path = Path(f.name)
        
        try:
            # Extract and store
            text = self.processor.extract_text(temp_path)
            doc = self.processor.create_document(temp_path, text, "Science")
            chunks = self.processor.create_chunks(doc)
            self.db.add_chunks(chunks)
            
            # Ask question
            question = "Who developed the theory of relativity?"
            context = self.db.query(question, n_results=3)
            answer, sources = self.llm.generate_response(question, context)
            
            # Verify answer mentions Einstein
            self.assertIsInstance(answer, str)
            self.assertIn("Einstein", answer)
        
        finally:
            temp_path.unlink(missing_ok=True)


class TestSystemHealth(unittest.TestCase):
    """Test system health and configuration"""
    
    def test_all_services_available(self):
        """All core services should be importable and instantiable"""
        try:
            db = DatabaseManager(Path("data/database"))
            llm = LLMService()
            processor = FileProcessor()
            
            self.assertIsNotNone(db)
            self.assertIsNotNone(llm)
            self.assertIsNotNone(processor)
        except Exception as e:
            self.fail(f"Service initialization failed: {e}")
    
    def test_data_directories_exist(self):
        """Required data directories should exist"""
        base_path = Path(__file__).parent.parent / "data"
        
        self.assertTrue((base_path / "incoming").exists())
        self.assertTrue((base_path / "sorted").exists())
        self.assertTrue((base_path / "database").exists())


if __name__ == '__main__':
    unittest.main()
