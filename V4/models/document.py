"""Document data models"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
from datetime import datetime


@dataclass
class Document:
    """Represents a document in the system"""
    filename: str
    filepath: Path
    file_hash: str
    category: str
    text_content: str
    file_type: str
    size_bytes: int
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if isinstance(self.filepath, str):
            self.filepath = Path(self.filepath)


@dataclass
class DocumentChunk:
    """Represents a chunk of document text"""
    chunk_id: str
    document_hash: str
    text: str
    chunk_index: int
    filename: str
    category: str
    filepath: str
    
    def to_metadata(self) -> dict:
        """Convert chunk to ChromaDB metadata format"""
        return {
            'filename': self.filename,
            'category': self.category,
            'filepath': self.filepath,
            'file_hash': self.document_hash,
            'chunk_index': self.chunk_index
        }
