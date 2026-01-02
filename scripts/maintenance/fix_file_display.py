"""
Update list_files to show files even if sorted_path is NULL (still processing)
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the section where we check "if sorted_path:"
old_code = '''            for row in rows:
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
                        })'''

new_code = '''            for row in rows:
                filename = row['filename']
                sorted_path = row['sorted_path']
                uploader = row['uploader']
                owner_id = row['user_id']
                
                if sorted_path:
                    # File has been sorted
                    path_parts = sorted_path.split('/')
                    domain = path_parts[0] if len(path_parts) > 0 else 'Unknown'
                    category = path_parts[1] if len(path_parts) > 1 else 'Other'
                    
                    # RBAC check for non-admin users
                    from core.permissions import check_file_access
                    if not check_file_access(user_role, domain, category):
                        continue  # Skip files user doesn't have domain access to
                    
                    # Build file path - sorted_path already includes subdirectories
                    filepath = sorted_dir / sorted_path
                    
                    # Check if file still exists
                    if not filepath.exists():
                        continue
                    
                    files_list.append({
                        'filename': filename,
                        'path': sorted_path,
                        'domain': domain,
                        'category': category,
                        'size': row['file_size'],
                        'uploaded_by': uploader,
                        'uploaded_at': row['uploaded_at'],
                        'is_owner': owner_id == current_user_id
                    })
                else:
                    # File is still being processed (in incoming directory)
                    files_list.append({
                        'filename': filename,
                        'path': 'incoming/' + filename,
                        'domain': 'Processing',
                        'category': 'Pending',
                        'size': row['file_size'],
                        'uploaded_by': uploader,
                        'uploaded_at': row['uploaded_at'],
                        'is_owner': owner_id == current_user_id
                    })'''

content = content.replace(old_code, new_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Updated list_files to show files being processed")
print("Files will now show even if sorted_path is NULL")
print("Status: 'Processing / Pending' for unprocessed files")
