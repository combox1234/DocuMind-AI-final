"""Test cases for utility functions"""
import unittest
from pathlib import Path
from utils.text_utils import TextUtils
from utils.file_utils import FileUtils


class TestTextUtils(unittest.TestCase):
    """Test text processing utilities"""
    
    def test_chunk_text_basic(self):
        """Should split text into chunks of specified size"""
        text = "a" * 1000
        chunks = TextUtils.chunk_text(text, chunk_size=500)
        
        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(len(chunks[0]), 500)
    
    def test_chunk_text_small_text(self):
        """Should handle text smaller than chunk size"""
        text = "Short text"
        chunks = TextUtils.chunk_text(text, chunk_size=500)
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)
    
    def test_chunk_text_empty(self):
        """Should handle empty text"""
        chunks = TextUtils.chunk_text("", chunk_size=500)
        self.assertEqual(len(chunks), 0)
    
    def test_clean_text_whitespace(self):
        """Should normalize whitespace"""
        text = "Multiple    spaces\n\n\nand    newlines"
        result = TextUtils.clean_text(text)
        
        self.assertNotIn("\n\n\n", result)
    
    def test_clean_text_special_chars(self):
        """Should preserve alphanumeric and basic punctuation"""
        text = "Hello, world! 123"
        result = TextUtils.clean_text(text)
        
        self.assertIn("Hello", result)
        self.assertIn("world", result)
        self.assertIn("123", result)


class TestFileUtils(unittest.TestCase):
    """Test file utility functions"""
    
    def test_file_type_detection(self):
        """Should detect file types correctly"""
        self.assertEqual(FileUtils.get_file_type(Path("test.pdf")), "pdf")
        self.assertEqual(FileUtils.get_file_type(Path("test.py")), "code")
        self.assertEqual(FileUtils.get_file_type(Path("test.jpg")), "image")


if __name__ == '__main__':
    unittest.main()
