"""
Script to re-index existing ChromaDB documents with correct domain metadata
This fixes files that have domain='Unknown' but correct category values
"""
import logging
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import DatabaseManager
from core.classifier import DocumentClassifier
from config import Config

# Category to Domain mapping
# Based on the classification system, many categories map to their parent domains
CATEGORY_TO_DOMAIN = {
    # Technology domain categories
    'UAV': 'Technology',
    'Web': 'Technology',
    'Database': 'Technology',
    'API': 'Technology',
    'DevOps': 'Technology',
    'AI': 'Technology',
    'Security': 'Technology',
    'Mobile': 'Technology',
    
    # Code domain categories
    'Backend': 'Code',
    'Frontend': 'Code',
    'Algorithm': 'Code',
    'Testing': 'Code',
    'Script': 'Code',
    
    # Finance domain categories
    'Accounting': 'Finance',
    'Payroll': 'Finance',
    'Tax': 'Finance',
    'Investment': 'Finance',
    
    # Education domain categories
    'Programming': 'Education',
    'Mathematics': 'Education',
    'Science': 'Education',
    'DataScience': 'Education',
    
    # College domain categories
    'Admin': 'College',  # Could also be School or Company
    'Placement': 'College',
    'Academic': 'College',  # Could also be School
    'Clubs': 'College',
    
    # School domain categories (note: some overlap with College)
    # 'Admin': 'School',
    # 'Academic': 'School',
    'Events': 'School',
    
    # Company domain categories
    'Product': 'Company',
    'Service': 'Company',
    'HR': 'Company',
    
    # Healthcare domain categories
    'Clinical': 'Healthcare',
    'LabReport': 'Healthcare',
    'Imaging': 'Healthcare',
    'Insurance': 'Healthcare',
    
    # Personal domain categories
    'Identity': 'Personal',
    'Bills': 'Personal',
    'Financial': 'Personal',
    'Housing': 'Personal',
    
    # Government domain categories
    'ID': 'Government',
    
    # Legal domain categories
    'Contract': 'Legal',
    'Property': 'Legal',
    'Court': 'Legal',
    
    # Business domain categories
    'Strategy': 'Business',
    'Marketing': 'Business',
    'Sales': 'Business',
    
    # Fallback for uncategorized
    'Other': 'Technology',  # Default fallback
}

def reindex_documents():
    """Re-index all documents with correct domain values"""
    try:
        # Initialize database
        logger.info("Initializing database connection...")
        db = DatabaseManager(Config.DB_DIR)
        
        # Get total count
        total_docs = db.collection.count()
        logger.info(f"Found {total_docs} total chunks in database\n")
        
        if total_docs == 0:
            logger.warning("No documents found in database!")
            return
        
        # Get all documents with metadata
        logger.info("Retrieving all documents...")
        results = db.collection.get(
            include=['metadatas']
        )
        
        if not results or not results.get('ids'):
            logger.error("Failed to retrieve documents!")
            return
        
        ids = results['ids']
        metadatas = results['metadatas']
        
        logger.info(f"Retrieved {len(ids)} chunks\n")
        
        # Track statistics
        updated_count = 0
        unknown_domain_count = 0
        already_correct_count = 0
        unmapped_categories = set()
        
        # List of valid domains for legacy detection
        VALID_DOMAINS = {
            'Technology', 'Code', 'Finance', 'Education', 'College', 'School',
            'Company', 'Healthcare', 'Legal', 'Business', 'ResearchPaper',
            'Documentation', 'Personal', 'Government'
        }
        
        # Update each document
        for i, (chunk_id, metadata) in enumerate(zip(ids, metadatas)):
            current_domain = metadata.get('domain', 'Unknown')
            category = metadata.get('category', 'Other')
            filename = metadata.get('filename', 'unknown')
            
            # Check if domain is Unknown
            if current_domain == 'Unknown':
                unknown_domain_count += 1
                
                # LEGACY FORMAT CHECK: If category is actually a domain name, use it as domain
                if category in VALID_DOMAINS:
                    # Legacy format: category contains the domain
                    correct_domain = category
                    # Set category to 'Other' since we don't have true category info
                    metadata['domain'] = correct_domain
                    metadata['category'] = 'Other'
                    
                    # Update in ChromaDB
                    db.collection.update(
                        ids=[chunk_id],
                        metadatas=[metadata]
                    )
                    
                    updated_count += 1
                    
                    if i % 50 == 0:  # Log every 50th update
                        logger.info(f"[{i+1}/{len(ids)}] Updated (legacy): {filename} - domain={correct_domain}")
                
                else:
                    # Try category-to-domain mapping for proper hierarchical categories
                    correct_domain = CATEGORY_TO_DOMAIN.get(category)
                    
                    if correct_domain:
                        # Update metadata
                        metadata['domain'] = correct_domain
                        
                        # Update in ChromaDB
                        db.collection.update(
                            ids=[chunk_id],
                            metadatas=[metadata]
                        )
                        
                        updated_count += 1
                        
                        if i % 50 == 0:  # Log every 50th update
                            logger.info(f"[{i+1}/{len(ids)}] Updated: {filename} - {category} -> {correct_domain}")
                    else:
                        unmapped_categories.add(category)
                        if i % 50 == 0:
                            logger.warning(f"No domain mapping for category: {category} (file: {filename})")
            else:
                already_correct_count += 1
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("RE-INDEXING COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total chunks processed: {len(ids)}")
        logger.info(f"Had 'Unknown'domain: {unknown_domain_count}")
        logger.info(f"Successfully updated: {updated_count}")
        logger.info(f"Already correct: {already_correct_count}")
        
        if unmapped_categories:
            logger.warning(f"\nUnmapped categories found: {', '.join(unmapped_categories)}")
            logger.warning("These files will retain 'Unknown' domain until mapping is added")
        
        logger.info(f"{'='*60}\n")
        
    except Exception as e:
        logger.error(f"Error during re-indexing: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("Starting domain metadata re-indexing...")
    reindex_documents()
    logger.info("Done!")
