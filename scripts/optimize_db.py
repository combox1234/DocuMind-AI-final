
import sqlite3
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "users.db"

def optimize_database():
    """
    Enable Write-Ahead Logging (WAL) mode for better concurrency.
    Recommended for production apps where Worker writes and App reads simultaneously.
    """
    if not DB_PATH.exists():
        logger.error(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check current mode
        cursor.execute("PRAGMA journal_mode;")
        current_mode = cursor.fetchone()[0]
        logger.info(f"Current journal mode: {current_mode}")
        
        if current_mode.upper() != 'WAL':
            logger.info("Enabling WAL mode...")
            cursor.execute("PRAGMA journal_mode=WAL;")
            new_mode = cursor.fetchone()[0]
            logger.info(f"New journal mode: {new_mode}")
            
            # Also increase cache size (default is 2000 pages)
            cursor.execute("PRAGMA cache_size=-64000;") # 64MB cache
            logger.info("Increased cache size to 64MB")
            
            # Set busy timeout to 5000ms to handle locks gracefully
            cursor.execute("PRAGMA busy_timeout=5000;") 
            logger.info("Set busy timeout to 5000ms")
        else:
            logger.info("WAL mode already enabled. Optimization applied.")
            
        conn.close()
        logger.info("✅ Database optimization complete.")
        
    except Exception as e:
        logger.error(f"Failed to optimize database: {e}")

if __name__ == "__main__":
    optimize_database()
