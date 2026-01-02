"""
Analytics Module
Calculates and caches sorting statistics
"""

import logging
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta
import redis
from config import Config

logger = logging.getLogger(__name__)


class Analytics:
    """Handles analytics calculation and caching"""
    
    def __init__(self, redis_client: redis.Redis, sorted_dir: Path):
        self.redis = redis_client
        self.sorted_dir = sorted_dir
        self.cache_ttl = 300  # 5 minutes
    
    def get_sorting_stats(self, use_cache=True) -> Dict:
        """Get overall sorting statistics"""
        # Check cache first
        if use_cache:
            cached = self.redis.get(Config.REDIS_ANALYTICS_CACHE)
            if cached:
                try:
                    return json.loads(cached)
                except:
                    pass
        
        # Calculate fresh stats
        stats = {
            "total_files": 0,
            "by_domain": {},
            "by_category": {},
            "by_extension": {},
            "by_language": {},
            "storage_mb": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        # Walk through sorted directory
        for domain_dir in self.sorted_dir.iterdir():
            if not domain_dir.is_dir():
                continue
            
            domain_name = domain_dir.name
            stats["by_domain"][domain_name] = 0
            
            for category_dir in domain_dir.rglob("*"):
                if not category_dir.is_dir():
                    continue
                
                # Count files in this category
                files = list(category_dir.glob("*"))
                file_count = len([f for f in files if f.is_file()])
                
                if file_count > 0:
                    stats["total_files"] += file_count
                    stats["by_domain"][domain_name] += file_count
                    
                    # Track by category
                    category_name = category_dir.parent.name if category_dir.parent != domain_dir else "Other"
                    if category_name not in stats["by_category"]:
                        stats["by_category"][category_name] = 0
                    stats["by_category"][category_name] += file_count
                    
                    # Track by extension and calculate storage
                    for file in files:
                        if file.is_file():
                            ext = file.suffix.lower() or "no_ext"
                            if ext not in stats["by_extension"]:
                                stats["by_extension"][ext] = 0
                            stats["by_extension"][ext] += 1
                            
                            # Add to storage size
                            stats["storage_mb"] += file.stat().st_size / (1024 * 1024)
        
        # Get language distribution from Redis
        lang_stats = self.redis.hgetall(Config.REDIS_LANGUAGE_STATS)
        if lang_stats:
            stats["by_language"] = {k: int(v) for k, v in lang_stats.items()}
        
        # Round storage
        stats["storage_mb"] = round(stats["storage_mb"], 2)
        
        # Cache the results
        self.redis.setex(
            Config.REDIS_ANALYTICS_CACHE,
            self.cache_ttl,
            json.dumps(stats)
        )
        
        return stats
    
    def get_domain_distribution(self) -> Dict[str, int]:
        """Get file count by domain"""
        stats = self.get_sorting_stats()
        return stats.get("by_domain", {})
    
    def get_category_distribution(self) -> Dict[str, int]:
        """Get file count by category"""
        stats = self.get_sorting_stats()
        return stats.get("by_category", {})
    
    def get_language_distribution(self) -> Dict[str, int]:
        """Get file count by language"""
        stats = self.get_sorting_stats()
        return stats.get("by_language", {})
    
    def get_recent_uploads(self, days=7) -> List[Dict]:
        """Get recently uploaded files"""
        recent_files = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Scan sorted directory for recent files
        for file_path in self.sorted_dir.rglob("*"):
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime >= cutoff_date:
                    recent_files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                        "uploaded_at": mtime.isoformat()
                    })
        
        # Sort by upload time (newest first)
        recent_files.sort(key=lambda x: x["uploaded_at"], reverse=True)
        return recent_files[:50]  # Return top 50
    
    def increment_language_count(self, language: str):
        """Increment count for a specific language"""
        self.redis.hincrby(Config.REDIS_LANGUAGE_STATS, language, 1)
    
    def clear_cache(self):
        """Clear analytics cache to force refresh"""
        self.redis.delete(Config.REDIS_ANALYTICS_CACHE)
