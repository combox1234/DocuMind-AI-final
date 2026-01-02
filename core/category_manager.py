"""
Category Manager Module
Handles custom category management with Redis persistence
"""

import logging
import json
from typing import Dict, List
import redis
from config import Config

logger = logging.getLogger(__name__)


class CategoryManager:
    """Manages custom categories with Redis storage"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def load_custom_categories(self, domain: str) -> Dict[str, List[str]]:
        """Load custom categories for a specific domain"""
        try:
            key = f"{Config.REDIS_CUSTOM_CATEGORIES}:{domain}"
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return {}
        except Exception as e:
            logger.error(f"Error loading custom categories for {domain}: {e}")
            return {}
    
    def add_category(self, domain: str, category_name: str, keywords: List[str]) -> bool:
        """Add a new custom category to a domain"""
        try:
            # Load existing categories
            categories = self.load_custom_categories(domain)
            
            # Add new category
            categories[category_name] = keywords
            
            # Save back to Redis
            key = f"{Config.REDIS_CUSTOM_CATEGORIES}:{domain}"
            self.redis.set(key, json.dumps(categories))
            
            logger.info(f"Added custom category '{category_name}' to domain '{domain}'")
            return True
        except Exception as e:
            logger.error(f"Error adding category: {e}")
            return False
    
    def update_category(self, domain: str, category_name: str, keywords: List[str]) -> bool:
        """Update an existing custom category"""
        return self.add_category(domain, category_name, keywords)
    
    def delete_category(self, domain: str, category_name: str) -> bool:
        """Delete a custom category"""
        try:
            categories = self.load_custom_categories(domain)
            
            if category_name in categories:
                del categories[category_name]
                
                key = f"{Config.REDIS_CUSTOM_CATEGORIES}:{domain}"
                self.redis.set(key, json.dumps(categories))
                
                logger.info(f"Deleted custom category '{category_name}' from domain '{domain}'")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            return False
    
    def get_all_categories(self, domain: str, default_categories: Dict = None) -> Dict[str, List[str]]:
        """Get merged default + custom categories for a domain"""
        # Start with default categories
        all_categories = default_categories.copy() if default_categories else {}
        
        # Merge with custom categories
        custom = self.load_custom_categories(domain)
        all_categories.update(custom)
        
        return all_categories
    
    def list_all_custom_categories(self) -> Dict[str, Dict]:
        """List all custom categories across all domains"""
        result = {}
        
        # Scan Redis for all custom category keys
        pattern = f"{Config.REDIS_CUSTOM_CATEGORIES}:*"
        for key in self.redis.scan_iter(match=pattern):
            domain = key.split(":")[-1]
            categories = self.load_custom_categories(domain)
            if categories:
                result[domain] = categories
        
        return result
    
    def validate_category(self, category_name: str, keywords: List[str]) -> tuple[bool, str]:
        """Validate category name and keywords"""
        if not category_name or not category_name.strip():
            return False, "Category name cannot be empty"
        
        if not keywords or len(keywords) == 0:
            return False, "At least one keyword is required"
        
        if len(category_name) > 50:
            return False, "Category name too long (max 50 characters)"
        
        return True, "Valid"
