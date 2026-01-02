"""
Fix delete endpoint to handle files in incoming/ directory (Processing state)
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the delete_file function and update it
old_check = '''        # Construct full path
        sorted_dir = Config.SORTED_DIR
        full_path = sorted_dir / filepath
        
        # Security check - ensure path is within sorted directory
        if not str(full_path.resolve()).startswith(str(sorted_dir.resolve())):
            return jsonify({'error': 'Invalid file path'}), 400
        
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404'''

new_check = '''        # Handle files in both incoming and sorted directories
        sorted_dir = Config.SORTED_DIR
        incoming_dir = Config.INCOMING_DIR
        
        # Check if file is in incoming (still processing)
        if filepath.startswith('incoming/'):
            filename = filepath.replace('incoming/', '')
            full_path = incoming_dir / filename
            is_incoming = True
        else:
            # File is in sorted directory
            full_path = sorted_dir / filepath
            is_incoming = False
            
            # Security check - ensure path is within sorted directory
            if not str(full_path.resolve()).startswith(str(sorted_dir.resolve())):
                return jsonify({'error': 'Invalid file path'}), 400
        
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404'''

content = content.replace(old_check, new_check)

# Also update the ChromaDB deletion part to handle incoming files
old_chroma = '''        # NOW delete file (after ownership check passed)
        full_path.unlink()
        
        # Also delete from ChromaDB if indexed
        deleted_chunks = db_manager.delete_by_filepath(str(full_path))'''

new_chroma = '''        # NOW delete file (after ownership check passed)
        full_path.unlink()
        
        # Delete from ChromaDB only if file was in sorted directory (indexed)
        if is_incoming:
            deleted_chunks = 0  # Files in incoming aren't indexed yet
        else:
            deleted_chunks = db_manager.delete_by_filepath(str(full_path))'''

content = content.replace(old_chroma, new_chroma)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Updated delete endpoint to handle incoming files")
print("Delete now works for:")
print("  - Files in 'Processing' state (incoming/)")
print("  - Files in sorted directories")
