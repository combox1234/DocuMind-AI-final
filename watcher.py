# watcher.py (put in project root)
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import sys

# ensure project root is on path (should be by running from project root)
ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(ROOT))

try:
    from app.db import sync_db_with_files
except Exception as e:
    print("Failed to import app.db:", e)
    raise

class MyHandler(FileSystemEventHandler):
    def on_deleted(self, event):
        if event.is_directory:
            return
        try:
            removed = sync_db_with_files()
            if removed:
                print("[watcher] cleaned", removed, "rows after deletion")
            else:
                print("[watcher] delete detected, no rows removed")
        except Exception as ex:
            print("[watcher] sync failed:", ex)

    def on_moved(self, event):
        # treat move as potential delete
        try:
            removed = sync_db_with_files()
            if removed:
                print("[watcher] cleaned", removed, "rows after move")
            else:
                print("[watcher] move detected, no rows removed")
        except Exception as ex:
            print("[watcher] sync failed:", ex)

if __name__ == "__main__":
    path = str((ROOT / "data" / "indexed").resolve())
    if not Path(path).exists():
        print("[watcher] data/indexed does not exist yet, creating it.")
        Path(path).mkdir(parents=True, exist_ok=True)

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("[watcher] started on", path)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[watcher] stopping...")
        observer.stop()
    observer.join()
    print("[watcher] stopped")
