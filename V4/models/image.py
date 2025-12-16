"""Image metadata model for storing extracted images"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ImageMetadata:
    """Represents metadata for an extracted image"""
    
    image_id: str  # Unique identifier
    source_file: str  # Original document filename
    image_path: str  # Path to extracted image
    page_or_slide: int  # Page number (PDF) or slide number (PPTX)
    file_hash: str  # Hash of source document
    caption: Optional[str] = None  # Optional text description near image
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'image_id': self.image_id,
            'source_file': self.source_file,
            'image_path': self.image_path,
            'page_or_slide': self.page_or_slide,
            'file_hash': self.file_hash,
            'caption': self.caption
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ImageMetadata':
        """Create from dictionary"""
        return cls(
            image_id=data['image_id'],
            source_file=data['source_file'],
            image_path=data['image_path'],
            page_or_slide=data['page_or_slide'],
            file_hash=data['file_hash'],
            caption=data.get('caption')
        )
