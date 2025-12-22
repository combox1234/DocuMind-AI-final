"""Image text extraction using OCR"""
from PIL import Image
import pytesseract
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ImageExtractor:
    """Extract text from images using OCR"""
    
    @staticmethod
    def extract(filepath: Path) -> str:
        """Extract text from image using Tesseract OCR"""
        try:
            image = Image.open(filepath)
            text = pytesseract.image_to_string(image)
            return text.strip() if text else ""
        except Exception as e:
            logger.error(f"Error extracting image {filepath}: {e}")
            return ""
