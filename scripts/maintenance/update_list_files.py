"""
Update list_files to show ALL files in sorted/ for Admin
"""

new_function = '''@app.route('/api/files', methods=['GET'])
@jwt_required()
def list_files():
    """List files - users see only their files, admin sees all files in sorted/"""
    try:
        # Get user info
        username = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role', None)
        
        # Get user ID
        user_data = auth_manager.get_user_by_username(username)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        current_user_id = user_data['id']
        
        files_list = []
        sorted_dir = Config.SORTED_DIR
        
        if user_role == 'Admin':
            # Admin sees ALL files in sorted directory (filesystem scan)
            # Get upload tracking data for uploader info
            conn = sqlite3.connect(DATA_DIR / 'users.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT uf.filename, u.username as uploader
                FROM user_uploads uf
                JOIN users u ON uf.user_id = u.id
            """)
            upload_map = {row['filename']: row['uploader'] for row in cursor.fetchall()}
            conn.close()
            
            # Scan sorted directory
            for root, dirs, files in os.walk(sorted_dir):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, sorted_dir)
                    
                    # Extract domain and category from path
                    path_parts = rel_path.split(os.sep)
                    domain = path_parts[0] if len(path_parts) > 0 else 'Unknown'
                    category = path_parts[1] if len(path_parts) > 1 else 'Other'
                    
                    # Get file stats
                    stats = os.stat(filepath)
                    
                    # Check if we have uploader info
                    uploader = upload_map.get(filename, 'System')
                    
                    files_list.append({
                        'filename': filename,
                        'path': rel_path,
                        'domain': domain,
                        'category': category,
                        'size': stats.st_size,
                        'uploaded_by': uploader,
                        'uploaded_at': stats.st_mtime,
                        'is_owner': False  # Admin doesn't own system files
                    })
        else:
            # Regular users see only their tracked uploads
            conn = sqlite3.connect(DATA_DIR / 'users.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT uf.filename, uf.sorted_path, uf.file_size, uf.uploaded_at, uf.user_id, u.username as uploader
                FROM user_uploads uf
                JOIN users u ON uf.user_id = u.id
                WHERE uf.user_id = ?
                ORDER BY uf.uploaded_at DESC
            """, (current_user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                filename = row['filename']
                sorted_path = row['sorted_path']
                uploader = row['uploader']
                owner_id = row['user_id']
                
                # If sorted_path is set, use it; otherwise file might still be in incoming
                if sorted_path:
                    # Extract domain and category from sorted_path
                    path_parts = sorted_path.split('/')
                    domain = path_parts[0] if len(path_parts) > 0 else 'Unknown'
                    category = path_parts[1] if len(path_parts) > 1 else 'Other'
                    
                    # RBAC check for non-admin users
                    from core.permissions import check_file_access
                    if not check_file_access(user_role, domain, category):
                        continue  # Skip files user doesn't have domain access to
                    
                    # Build file path
                    filepath = sorted_dir / sorted_path / filename
                    
                    # Check if file still exists
                    if filepath.exists():
                        files_list.append({
                            'filename': filename,
                            'path': sorted_path + '/' + filename,
                            'domain': domain,
                            'category': category,
                            'size': row['file_size'],
                            'uploaded_by': uploader,
                            'uploaded_at': row['uploaded_at'],
                            'is_owner': owner_id == current_user_id
                        })
        
        return jsonify({
            'files': files_list,
            'count': len(files_list)
        })
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({'error': str(e)}), 500
'''

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start and end of list_files function
start_marker = "@app.route('/api/files', methods=['GET'])\n@jwt_required()\ndef list_files():"
end_marker = "\n\n@app.route('/api/files/<path:filepath>', methods=['DELETE'])"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find list_files function markers")
    exit(1)

# Replace the function
new_content = content[:start_idx] + new_function + content[end_idx:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: Updated list_files to show ALL files in sorted/ for Admin")
print("Admin now sees:")
print("  - Files uploaded by users (with username)")
print("  - System files (marked as 'System')")
print("  - All files in sorted directory")
