"""Audio text extraction - FUTURE IMPLEMENTATION"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AudioExtractor:
    """Extract text from audio files - marked for future implementation"""
    
    @staticmethod
    def extract(filepath: Path) -> str:
        """Audio extraction not yet implemented"""
        logger.warning(f"Audio extraction not implemented yet for {filepath}")
        return f"[Audio file - extraction pending: {filepath.name}]"
