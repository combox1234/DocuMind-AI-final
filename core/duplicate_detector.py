"""
Duplicate Detection Module
Handles file duplicate detection using SHA256 hashing
"""

import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Optional
import redis
from config import Config

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """Manages duplicate file detection and resolution"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def calculate_hash(self, filepath: Path) -> Optional[str]:
        """Calculate SHA256 hash of file content"""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {filepath}: {e}")
            return None
    
    def is_duplicate(self, file_hash: str) -> Optional[str]:
        """Check if file hash already exists"""
        if not file_hash:
            return None
        existing_path = self.redis.hget(Config.REDIS_FILE_HASHES, file_hash)
        return existing_path
    
    def store_hash(self, file_hash: str, filepath: str):
        """Store file hash in Redis"""
        if file_hash:
            self.redis.hset(Config.REDIS_FILE_HASHES, file_hash, filepath)
    
    def get_all_duplicates(self) -> List[Dict]:
        """Get all duplicate file groups"""
        all_hashes = self.redis.hgetall(Config.REDIS_FILE_HASHES)
        
        # Group files by hash
        hash_groups = {}
        for file_hash, filepath in all_hashes.items():
            if file_hash not in hash_groups:
                hash_groups[file_hash] = []
            hash_groups[file_hash].append(filepath)
        
        # Filter only duplicates (more than one file with same hash)
        duplicates = []
        for file_hash, filepaths in hash_groups.items():
            if len(filepaths) > 1:
                duplicates.append({
                    "hash": file_hash,
                    "files": filepaths,
                    "count": len(filepaths)
                })
        
        return duplicates
    
    def remove_duplicate(self, file_hash: str, filepath: str):
        """Remove a duplicate file entry"""
        try:
            # Remove from Redis
            self.redis.hdel(Config.REDIS_FILE_HASHES, file_hash)
            
            # Remove physical file if exists
            file_path = Path(filepath)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Removed duplicate file: {filepath}")
                return True
        except Exception as e:
            logger.error(f"Error removing duplicate {filepath}: {e}")
            return False
    
    def get_duplicate_count(self) -> int:
        """Get total count of duplicate file groups"""
        duplicates = self.get_all_duplicates()
        return len(duplicates)
