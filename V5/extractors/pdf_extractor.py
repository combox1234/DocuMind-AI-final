"""PDF text and image extraction"""
from pdfminer.high_level import extract_text as extract_pdf_text
from pathlib import Path
import logging
import fitz  # PyMuPDF
import io
from PIL import Image

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text and images from PDF files"""
    
    @staticmethod
    def extract(filepath: Path) -> str:
        """Extract text from PDF"""
        try:
            text = extract_pdf_text(str(filepath))
            return text.strip() if text else ""
        except Exception as e:
            logger.error(f"Error extracting PDF {filepath}: {e}")
            return ""
    
    @staticmethod
    def extract_images(filepath: Path, output_dir: Path) -> list:
        """Extract images from PDF and save them
        
        Returns: List of extracted image paths
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            doc = fitz.open(str(filepath))
            image_paths = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Create unique filename
                    image_filename = f"{filepath.stem}_page{page_num + 1}_img{img_index + 1}.{image_ext}"
                    image_path = output_dir / image_filename
                    
                    # Save image
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    image_paths.append(str(image_path))
                    logger.info(f"Extracted image: {image_filename}")
            
            doc.close()
            logger.info(f"Extracted {len(image_paths)} images from {filepath.name}")
            return image_paths
            
        except Exception as e:
            logger.error(f"Error extracting images from PDF {filepath}: {e}")
            return []
