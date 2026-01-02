"""
Initialize/reset the auth database with correct schema
"""
import sqlite3
from pathlib import Path

db_path = Path("data/users.db")
db_path.parent.mkdir(exist_ok=True)

# Delete old database if exists
if db_path.exists():
    print(f"Deleting old database...")
    db_path.unlink()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create roles table with file_permissions column
cursor.execute('''
    CREATE TABLE roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        permissions TEXT NOT NULL,
        file_permissions TEXT
    )
''')

# Create users table
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role_id INTEGER NOT NULL,
        created_by INTEGER,
        FOREIGN KEY (role_id) REFERENCES roles (id)
    )
''')

# Create default Admin role
cursor.execute(
    "INSERT INTO roles (name, permissions) VALUES (?, ?)",
    ('Admin', '["*"]')
)

conn.commit()
conn.close()

print("[SUCCESS] Database initialized successfully!")
print("[SUCCESS] Admin role created")
print("\nNow restart the app and it should work!")
