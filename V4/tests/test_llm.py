"""Test cases for LLM service"""
import unittest
from core.llm import LLMService


class TestLLMService(unittest.TestCase):
    """Test Ollama LLM integration"""
    
    @classmethod
    def setUpClass(cls):
        """Initialize LLM service once"""
        cls.llm = LLMService()
        # Disable LLM network calls during automated test runs
        cls.available = False
    
    def test_llm_initialization(self):
        """LLM service should initialize"""
        self.assertIsNotNone(self.llm)
        self.assertEqual(self.llm.model, "llama3.2")
    
    def test_classify_content(self):
        """Should classify content into categories"""
        if not self.available:
            self.skipTest("Ollama not available")

        content = "Python is a programming language used for web development"
        category = self.llm.classify_content(content)
        
        self.assertIsInstance(category, str)
        self.assertGreater(len(category), 0)
        # Should be in title case
        self.assertTrue(category[0].isupper())
    
    def test_answer_question_with_context(self):
        """Should answer question using provided context"""
        if not self.available:
            self.skipTest("Ollama not available")

        context = [
            {"text": "Python was created by Guido van Rossum", "filename": "python.txt"},
            {"text": "Python 1.0 was released in 1991", "filename": "history.txt"}
        ]
        question = "Who created Python?"
        
        answer, sources = self.llm.generate_response(question, context)
        
        self.assertIsInstance(answer, str)
        self.assertGreater(len(answer), 0)
        # Should mention the creator
        self.assertIn("Guido", answer)
    
    def test_answer_question_no_context(self):
        """Should say 'cannot find' when no context provided"""
        if not self.available:
            self.skipTest("Ollama not available")

        answer, sources = self.llm.generate_response("What is Python?", [])
        
        self.assertIn("cannot find", answer.lower())
    
    def test_classify_handles_code(self):
        """Should classify code correctly"""
        if not self.available:
            self.skipTest("Ollama not available")

        code_content = "def hello_world():\n    print('Hello, World!')"
        category = self.llm.classify_content(code_content)
        
        self.assertIsInstance(category, str)
        # Might be "Programming" or "Code" or similar
        self.assertGreater(len(category), 0)


if __name__ == '__main__':
    unittest.main()
