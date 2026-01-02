
import os
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.parent
SORTED_DIR = BASE_DIR / "data" / "sorted"
INCOMING_DIR = BASE_DIR / "data" / "incoming"

def reset_files():
    """
    Moves all files from SORTED_DIR (recursive) to INCOMING_DIR (flat).
    Handles filename collisions by renaming.
    Leaves empty folders in SORTED_DIR.
    """
    if not SORTED_DIR.exists():
        logger.warning(f"Sorted directory not found: {SORTED_DIR}")
        return

    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Moving files from {SORTED_DIR} to {INCOMING_DIR}...")
    
    count = 0
    collisions = 0
    
    # Walk bottom-up (though order doesn't matter for files)
    for root, dirs, files in os.walk(SORTED_DIR):
        for file in files:
            src_path = Path(root) / file
            
            # Skip if it's already in incoming (unlikely given logic, but safety)
            if INCOMING_DIR in src_path.parents:
                continue
                
            dest_path = INCOMING_DIR / file
            
            # Handle Collision
            if dest_path.exists():
                collisions += 1
                base = dest_path.stem
                suffix = dest_path.suffix
                counter = 1
                while dest_path.exists():
                    dest_path = INCOMING_DIR / f"{base}_reset_{counter}{suffix}"
                    counter += 1
                logger.info(f"Collision resolved: {file} -> {dest_path.name}")
            
            try:
                shutil.move(str(src_path), str(dest_path))
                count += 1
            except Exception as e:
                logger.error(f"Failed to move {file}: {e}")
                
    logger.info("-" * 30)
    logger.info(f"Reset Complete.")
    logger.info(f"Moved: {count} files")
    logger.info(f"Collisions resolved: {collisions}")
    logger.info("-" * 30)
    logger.info("Files are now in 'incoming'. If the server is running, they will be re-processed shortly.")

if __name__ == "__main__":
    reset_files()
