"""File utility functions"""
import hashlib
from pathlib import Path
import zipfile
import logging

logger = logging.getLogger(__name__)


class FileUtils:
    """File handling utilities"""
    
    @staticmethod
    def get_file_hash(filepath: Path) -> str:
        """Generate MD5 hash for file"""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    @staticmethod
    def get_file_type(filepath: Path) -> str:
        """Determine file type category"""
        ext = filepath.suffix.lower()
        
        type_mapping = {
            'pdf': ['.pdf'],
            'document': ['.docx', '.doc', '.odt', '.rtf', '.epub'],
            'spreadsheet': ['.xlsx', '.xls', '.ods', '.csv'],
            'presentation': ['.pptx', '.ppt', '.odp'],
            'text': ['.txt', '.md'],
            'image': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif', '.webp', '.heic', '.raw'],
            'audio': ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.flv'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.rb', '.go'],
            'web': ['.html', '.css', '.xml'],
            'data': ['.json', '.yaml', '.yml', '.sql'],
            'archive': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'medical': ['.dcm', '.dicom', '.hl7', '.nii', '.svs', '.ecg'],
            'engineering': ['.dwg', '.dxf', '.stl'],
            'research': ['.tex', '.bib', '.ipynb', '.sav', '.sps', '.dta']
        }
        
        # Handle compound extensions
        full_ext = ''.join(filepath.suffixes).lower()
        if full_ext == '.nii.gz':
            return 'medical'
        
        for file_type, extensions in type_mapping.items():
            if ext in extensions:
                return file_type
        
        return 'other'
    
    @staticmethod
    def list_zip_contents(filepath: Path) -> str:
        """List contents of ZIP file"""
        try:
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                return f"ZIP Archive containing: {', '.join(file_list[:20])}"
        except Exception as e:
            logger.error(f"Error reading ZIP {filepath}: {e}")
            return ""
