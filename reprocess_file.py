
import shutil
import os
from pathlib import Path
import time

# Paths
ROOT = Path(__file__).parent
SORTED_DIR = ROOT / "data" / "sorted"
INCOMING_DIR = ROOT / "data" / "incoming"

# Target File
target_rel_path = "Technology/DevOps/pdf/2025-12/unit 1 part 2 Safety Training.pdf"
src_file = SORTED_DIR / target_rel_path

if src_file.exists():
    print(f"Found file: {src_file}")
    dest_file = INCOMING_DIR / src_file.name
    
    # Ensure unique name if collision
    if dest_file.exists():
        timestamp = int(time.time())
        dest_file = INCOMING_DIR / f"{src_file.stem}_{timestamp}{src_file.suffix}"
    
    print(f"Moving to Incoming for Re-indexing: {dest_file}")
    shutil.move(str(src_file), str(dest_file))
    print("✅ Moved. The Watcher should pick this up in ~5 seconds.")
    print("Please verify output in your 'Watcher' terminal window.")
else:
    print(f"❌ File not found at: {src_file}")
