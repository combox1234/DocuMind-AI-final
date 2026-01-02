"""
Fix: Delete endpoint should search for file if sorted_path is NULL
Instead of assuming it's in incoming, search in sorted directory
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the incoming/sorted check logic
old_logic = '''        # Check if file is in incoming (still processing)
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

new_logic = '''        # Handle different file locations
        if filepath.startswith('incoming/'):
            # File is marked as still processing
            filename = filepath.replace('incoming/', '')
            
            # Try incoming directory first
            full_path = incoming_dir / filename
            is_incoming = True
            
            # If not in incoming, search in sorted (*worker processed but DB not updated*)
            if not full_path.exists():
                # Search for file in sorted directory
                import glob
                pattern = str(sorted_dir / '**' / filename)
                matches = glob.glob(pattern, recursive=True)
                
                if matches:
                    full_path = Path(matches[0])
                    is_incoming = False  # Actually sorted
                else:
                    return jsonify({'error': 'File not found'}), 404
        else:
            # File is in sorted directory
            full_path = sorted_dir / filepath
            is_incoming = False
            
            # Security check - ensure path is within sorted directory
            if not str(full_path.resolve()).startswith(str(sorted_dir.resolve())):
                return jsonify({'error': 'Invalid file path'}), 400
            
            if not full_path.exists():
                return jsonify({'error': 'File not found'}), 404'''

content = content.replace(old_logic, new_logic)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Delete now searches for files in sorted directory")
print("Even if database shows 'Processing', delete will find the file")
