
import sqlite3
import os
import glob
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SORTED_DIR = DATA_DIR / "sorted"
DB_PATH = DATA_DIR / "users.db"

def sync_user_uploads():
    """
    Syncs user_uploads table sorted_path column with actual file locations.
    """
    if not DB_PATH.exists():
        logger.error(f"Database not found at {DB_PATH}")
        return

    logger.info(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all uploads where sorted_path is NULL or empty
    cursor.execute("SELECT id, filename FROM user_uploads WHERE sorted_path IS NULL OR sorted_path = ''")
    rows = cursor.fetchall()

    if not rows:
        logger.info("No pending uploads found with missing sorted_path.")
        conn.close()
        return

    logger.info(f"Found {len(rows)} uploads to sync.")

    updated_count = 0
    not_found_count = 0

    for row in rows:
        file_id = row['id']
        filename = row['filename']

        # Search for file in sorted directory recursively
        # GLOB pattern: **\filename
        # We search using Path.rglob which is efficient enough for this scale
        found_path = None
        
        # Exact match search first
        matches = list(SORTED_DIR.rglob(filename))
        
        if matches:
            # Take the most recent one if duplicates exist?
            # Or just the first one. Let's take the first one.
            full_path = matches[0]
            
            # Create relative path from sorted_dir
            # e.g., Domain/Category/ext/date/filename
            rel_path = full_path.relative_to(SORTED_DIR)
            
            # Normalize to forward slashes for DB consistency
            sorted_path = str(rel_path).replace('\\', '/')
            
            logger.info(f"Found: {filename} -> {sorted_path}")
            
            # Update DB
            cursor.execute("UPDATE user_uploads SET sorted_path = ? WHERE id = ?", (sorted_path, file_id))
            updated_count += 1
        else:
            logger.warning(f"File not found in sorted dir: {filename}")
            not_found_count += 1

    conn.commit()
    conn.close()

    logger.info("-" * 30)
    logger.info(f"Sync Complete.")
    logger.info(f"Updated: {updated_count}")
    logger.info(f"Not Found: {not_found_count}")
    logger.info("-" * 30)

if __name__ == "__main__":
    sync_user_uploads()
