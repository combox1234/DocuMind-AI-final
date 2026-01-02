"""
Create user_uploads table for tracking file upload quotas
"""
import sqlite3
from pathlib import Path

db_path = Path("data/users.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create user_uploads table
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    sorted_path TEXT,
    file_size INTEGER NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

conn.commit()
conn.close()

print("SUCCESS: user_uploads table created successfully!")

