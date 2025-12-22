"""Code file text extraction"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CodeExtractor:
    """Extract text from code files"""
    
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.java', '.cpp', '.c', '.h', '.cs',
        '.html', '.css', '.sql', '.xml', '.json', '.yaml', 
        '.yml', '.md', '.txt', '.csv', '.log', '.sh', '.bat'
    }
    
    @staticmethod
    def extract(filepath: Path) -> str:
        """Extract text from code file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error extracting code {filepath}: {e}")
            return ""
