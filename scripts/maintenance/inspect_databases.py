"""
Script to inspect the users.db database
"""
import sqlite3
from pathlib import Path

def inspect_database(db_path):
    """Inspect database schema and data counts"""
    if not Path(db_path).exists():
        print(f"[X] Database not found: {db_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Inspecting: {db_path}")
    print('='*60)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\nTables: {tables}")
        
        for table in tables:
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            print(f"\n--- Table: {table} ({count} rows) ---")
            print("Columns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']} {'(PRIMARY KEY)' if col['pk'] else ''}")
            
            # Show sample data if exists
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                print(f"\nSample data ({min(3, count)} rows):")
                for i, row in enumerate(rows, 1):
                    print(f"  Row {i}:")
                    for key in row.keys():
                        value = row[key]
                        # Truncate long values
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        print(f"    {key}: {value}")
    
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_database("data/users.db")
    
    print(f"\n{'='*60}")
    print("[SUCCESS] Inspection complete!")
    print('='*60)
