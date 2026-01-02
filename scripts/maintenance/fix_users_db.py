import sqlite3

# Add column to USERS.DB (the actual database being used!)
conn = sqlite3.connect('data/users.db')
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(roles)")
columns = [row[1] for row in cursor.fetchall()]

if 'file_permissions' in columns:
    print("Column already exists in users.db!")
else:
    print("Adding file_permissions column to users.db...")
    cursor.execute("ALTER TABLE roles ADD COLUMN file_permissions TEXT")
    conn.commit()
    print("SUCCESS! Column added to users.db")

conn.close()
print("\nRestart Flask now!")
