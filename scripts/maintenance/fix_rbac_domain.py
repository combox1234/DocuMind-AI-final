"""
Fix RBAC domain extraction - use actual file path, not incoming path
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: Extract domain from actual full_path, not from incoming filepath
old_code = '''        # Extract domain from path for RBAC check
        path_parts = filepath.split(os.sep)
        domain = path_parts[0] if len(path_parts) > 0 else 'Unknown'
        category = path_parts[1] if len(path_parts) > 1 else 'Other'
        
        # RBAC check
        if user_role and not can_delete_all:
            from core.permissions import check_file_access
            if not check_file_access(user_role, domain, category):
                return jsonify({'error': 'Access denied: You do not have permission to delete files from this domain'}), 403'''

new_code = '''        # Extract domain from ACTUAL file path for RBAC check
        # If file was in incoming but found in sorted, use sorted path
        if is_incoming and str(full_path).find(str(sorted_dir)) != -1:
            # File was found in sorted directory via glob
            rel_path = os.path.relpath(str(full_path), str(sorted_dir))
            path_parts = rel_path.split(os.sep)
        else:
            path_parts = filepath.split(os.sep)
        
        domain = path_parts[0] if len(path_parts) > 0 else 'Unknown'
        category = path_parts[1] if len(path_parts) > 1 else 'Other'
        
        # Skip RBAC for 'incoming' or 'Processing' domain (files being processed)
        if domain in ['incoming', 'Processing']:
            pass  # Allow delete for files being processed
        elif user_role and not can_delete_all:
            from core.permissions import check_file_access
            if not check_file_access(user_role, domain, category):
                return jsonify({'error': 'Access denied: You do not have permission to delete files from this domain'}), 403'''

content = content.replace(old_code, new_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Fixed RBAC domain extraction")
print("Now extracts domain from actual file location, not incoming path")
