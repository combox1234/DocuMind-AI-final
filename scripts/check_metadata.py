
import logging
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import DatabaseManager
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_metadata():
    db = DatabaseManager(Config.DB_DIR)
    
    # Get a sample of documents
    results = db.collection.get(limit=20, include=['metadatas', 'documents'])
    
    if not results['metadatas']:
        logger.info("No documents found in DB.")
        return

    logger.info(f"Checking {len(results['metadatas'])} documents...")
    
    unknown_count = 0
    missing_count = 0
    
    for i, meta in enumerate(results['metadatas']):
        filename = meta.get('filename', 'Unknown')
        domain = meta.get('domain')
        category = meta.get('category')
        filepath = meta.get('filepath', 'Unknown')
        
        logger.info(f"[{i}] File: {filename}")
        logger.info(f"    Domain: {domain} (Type: {type(domain)})")
        logger.info(f"    Category: {category}")
        logger.info(f"    Path: {filepath}")
        
        if domain is None:
            missing_count += 1
        elif domain == 'Unknown':
            unknown_count += 1
            
    logger.info("-" * 30)
    logger.info(f"Total checked: {len(results['metadatas'])}")
    logger.info(f"Missing domain: {missing_count}")
    logger.info(f"Unknown domain: {unknown_count}")

if __name__ == "__main__":
    check_metadata()
