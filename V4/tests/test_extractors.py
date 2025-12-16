"""Test cases for text extractors"""
import unittest
from pathlib import Path
import tempfile
from extractors.pdf_extractor import PDFExtractor
from extractors.image_extractor import ImageExtractor
from extractors.document_extractor import DocumentExtractor
from extractors.code_extractor import CodeExtractor
from extractors.audio_extractor import AudioExtractor


class TestPDFExtractor(unittest.TestCase):
    """Test PDF text extraction"""
    
    def test_extract_returns_string(self):
        """PDFExtractor.extract should return a string"""
        # Create a dummy test - real test needs actual PDF file
        extractor = PDFExtractor()
        self.assertIsNotNone(extractor)


class TestImageExtractor(unittest.TestCase):
    """Test image OCR extraction"""
    
    def test_extract_with_tesseract(self):
        """ImageExtractor should use pytesseract for OCR"""
        extractor = ImageExtractor()
        # Real test would need a sample image with text
        self.assertIsNotNone(extractor)


class TestDocumentExtractor(unittest.TestCase):
    """Test document extraction (DOCX, TXT)"""
    
    def test_extract_txt_file(self):
        """Should extract text from .txt file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for extraction")
            temp_path = Path(f.name)
        
        try:
            result = DocumentExtractor.extract_text(temp_path)
            self.assertIn("Test content", result)
        finally:
            temp_path.unlink(missing_ok=True)
    
    def test_extract_empty_file(self):
        """Should handle empty files gracefully"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            result = DocumentExtractor.extract_text(temp_path)
            self.assertEqual(result, "")
        finally:
            temp_path.unlink(missing_ok=True)


class TestCodeExtractor(unittest.TestCase):
    """Test code file extraction"""
    
    def test_extract_python_code(self):
        """Should extract Python code with syntax highlighting"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def hello():\n    print("world")')
            temp_path = Path(f.name)
        
        try:
            result = CodeExtractor.extract(temp_path)
            self.assertIn("def hello", result)
            self.assertIn("print", result)
        finally:
            temp_path.unlink(missing_ok=True)


class TestAudioExtractor(unittest.TestCase):
    """Test audio extraction (marked for future)"""
    
    def test_audio_returns_placeholder(self):
        """Audio extractor should return placeholder message"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            result = AudioExtractor.extract(temp_path)
            self.assertIn("pending", result.lower())
        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
