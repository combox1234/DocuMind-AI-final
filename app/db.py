import sqlite3
from pathlib import Path
from typing import Optional

BASE = Path(__file__).resolve().parents[1]
DB_PATH = BASE / "data" / "metadata.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SCHEMA = '''
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    stored_path TEXT,
    department TEXT,
    year TEXT,
    file_type TEXT,
    snippet TEXT,
    checksum TEXT UNIQUE,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS vectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER,
    chunk_id INTEGER,
    embedding BLOB,
    text_snippet TEXT,
    page INTEGER,
    FOREIGN KEY(file_id) REFERENCES files(id)
);
'''

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_PATH)

def insert_file_meta(filename, stored_path, department, year, file_type, snippet, checksum, created_at):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO files (filename, stored_path, department, year, file_type, snippet, checksum, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (filename, stored_path, department, year, file_type, snippet, checksum, created_at),
        )
        conn.commit()
        file_id = cur.lastrowid
    except sqlite3.IntegrityError:
        cur.execute("SELECT id FROM files WHERE checksum = ?", (checksum,))
        row = cur.fetchone()
        file_id = row[0] if row else None
    conn.close()
    return file_id

def list_files(limit=50):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, filename, stored_path, department, year, file_type, created_at FROM files ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def sync_db_with_files():
    """
    Remove DB rows whose stored_path no longer exists on disk.
    Returns the number of rows removed.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, stored_path FROM files")
    rows = cur.fetchall()
    removed = 0
    for fid, stored_path in rows:
        if not stored_path:
            # If empty path, remove row
            cur.execute("DELETE FROM files WHERE id = ?", (fid,))
            removed += 1
            continue
        p = Path(stored_path)
        # Treat relative paths and absolute same - check exists
        if not p.exists():
            cur.execute("DELETE FROM files WHERE id = ?", (fid,))
            removed += 1
    conn.commit()
    conn.close()
    return removed
