"""
Clean up sorted files and reset database for fresh start
"""
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SORTED_DIR = DATA_DIR / "sorted"
DB_DIR = DATA_DIR / "database"
INCOMING_DIR = DATA_DIR / "incoming"

def cleanup_and_reset():
    """Reset the system for fresh data"""
    logger.info("=" * 60)
    logger.info("CLEANING UP SYSTEM FOR FRESH START")
    logger.info("=" * 60)
    
    # Backup existing database
    if DB_DIR.exists():
        backup_dir = DATA_DIR / "database_backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(DB_DIR, backup_dir)
        logger.info(f"✓ Database backed up to: {backup_dir}")
    
    # Clear sorted directory
    if SORTED_DIR.exists():
        for category_dir in SORTED_DIR.iterdir():
            if category_dir.is_dir():
                files_count = len(list(category_dir.glob('*')))
                shutil.rmtree(category_dir)
                logger.info(f"✓ Cleared {category_dir.name}/ ({files_count} files removed)")
    
    # Recreate empty category directories
    categories = ["Code", "Documentation", "Education", "Programming", "Technology", "Other"]
    for category in categories:
        category_dir = SORTED_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Created empty category: {category}")
    
    # Clear database
    if DB_DIR.exists():
        shutil.rmtree(DB_DIR)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"✓ Database reset and cleared")
    
    # Ensure incoming directory exists
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"✓ Incoming directory ready at: {INCOMING_DIR}")
    
    logger.info("\n" + "=" * 60)
    logger.info("SYSTEM READY FOR FRESH DATA")
    logger.info("=" * 60)
    logger.info(f"\n📁 Drop new files into: {INCOMING_DIR}")
    logger.info(f"📊 Sorted files will appear in: {SORTED_DIR}")
    logger.info(f"🗄️  Database will be created at: {DB_DIR}")
    logger.info("\nNext steps:")
    logger.info("1. Run: python watcher.py")
    logger.info("2. Run: python app.py")
    logger.info("3. Drop files into data/incoming/")
    logger.info("=" * 60)

if __name__ == "__main__":
    cleanup_and_reset()
