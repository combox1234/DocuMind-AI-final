"""File processor - orchestrates text extraction and processing"""
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import logging

from models.document import Document, DocumentChunk
from extractors import (
    PDFExtractor, ImageExtractor, AudioExtractor,
    DocumentExtractor, CodeExtractor
)
from utils import FileUtils, TextUtils

logger = logging.getLogger(__name__)


class FileProcessor:
    """Processes files and extracts text"""
    
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.image_extractor = ImageExtractor()
        self.audio_extractor = AudioExtractor()
        self.document_extractor = DocumentExtractor()
        self.code_extractor = CodeExtractor()
    
    def extract_text(self, filepath: Path) -> str:
        """Extract text from any file type"""
        file_type = FileUtils.get_file_type(filepath)
        ext = filepath.suffix.lower()
        
        try:
            # PDF files
            if file_type == 'pdf':
                return self.pdf_extractor.extract(filepath)
            
            # Images (OCR)
            elif file_type == 'image':
                return self.image_extractor.extract(filepath)
            
            # Audio files (Speech-to-text)
            elif file_type == 'audio':
                return self.audio_extractor.extract(filepath)
            
            # DOCX files
            elif ext in ['.docx', '.doc', '.odt', '.rtf', '.epub']:
                return self.document_extractor.extract_docx(filepath)
            
            # PPTX files (PowerPoint)
            elif ext in ['.pptx', '.ppt', '.odp']:
                return self.document_extractor.extract_pptx(filepath)
            
            # Excel/Spreadsheet files
            elif ext in ['.xlsx', '.xls', '.ods']:
                return self.document_extractor.extract_xlsx(filepath)
            
            # CSV files
            elif ext == '.csv':
                return self.document_extractor.extract_csv(filepath)
            
            # JSON files
            elif ext == '.json':
                return self.document_extractor.extract_json(filepath)
            
            # Jupyter Notebooks
            elif ext == '.ipynb':
                return self.document_extractor.extract_jupyter(filepath)
            
            # Text/Code/Web files
            elif file_type in ['text', 'code', 'web', 'data']:
                return self.document_extractor.extract_text(filepath)
            
            # Research files (LaTeX, BibTeX)
            elif ext in ['.tex', '.bib']:
                return self.document_extractor.extract_text(filepath)
            
            # ZIP files
            elif file_type == 'archive':
                return FileUtils.list_zip_contents(filepath)
            
            # Medical files (metadata only)
            elif file_type == 'medical':
                return f"Medical imaging file ({ext}): {filepath.name}\nNote: Binary medical data - metadata extraction not yet implemented"
            
            # Engineering files (metadata only)
            elif file_type == 'engineering':
                return f"Engineering CAD file ({ext}): {filepath.name}\nNote: Binary CAD data - full extraction requires specialized tools"
            
            # Statistical/Research data (metadata only)
            elif ext in ['.sav', '.sps', '.dta']:
                return f"Statistical data file ({ext}): {filepath.name}\nNote: Binary statistical data - requires SPSS/Stata tools"
            
            # Video (metadata only)
            elif file_type == 'video':
                return f"Video file: {filepath.name}"
            
            # Fallback: use filename
            else:
                return f"File: {filepath.name}"
                
        except Exception as e:
            logger.error(f"Error extracting text from {filepath}: {e}")
            return f"File: {filepath.name}"
    
    def create_document(self, filepath: Path, text: str, category: str) -> Document:
        """Create Document object"""
        return Document(
            filename=filepath.name,
            filepath=filepath,
            file_hash=FileUtils.get_file_hash(filepath),
            category=category,
            text_content=text,
            file_type=FileUtils.get_file_type(filepath),
            size_bytes=filepath.stat().st_size,
            created_at=datetime.fromtimestamp(filepath.stat().st_ctime),
            processed_at=datetime.now()
        )
    
    def create_chunks(self, document: Document, chunk_size: int = 1200) -> List[DocumentChunk]:
        """Create chunks from document - optimized size for accuracy and retrieval"""
        text_chunks = TextUtils.chunk_text(document.text_content, chunk_size)
        
        chunks = []
        for i, text in enumerate(text_chunks):
            chunk = DocumentChunk(
                chunk_id=f"{document.file_hash}_{i}",
                document_hash=document.file_hash,
                text=text,
                chunk_index=i,
                filename=document.filename,
                category=document.category,
                filepath=str(document.filepath)
            )
            chunks.append(chunk)
        
        return chunks

    def process_file(self, filepath: str, category: str) -> List[DocumentChunk]:
        """Process a file and return chunks"""
        try:
            file_path = Path(filepath)
            text = self.extract_text(file_path)
            document = self.create_document(file_path, text, category)
            chunks = self.create_chunks(document)
            return chunks
        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}")
            return []
