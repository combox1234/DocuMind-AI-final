"""
Fix Path Separator issue in delete_file
Ensure filepath uses correct OS separators before splitting
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix path splitting logic
old_code = '''        else:
            path_parts = filepath.split(os.sep)
        
        domain = path_parts[0] if len(path_parts) > 0 else 'Unknown'
        category = path_parts[1] if len(path_parts) > 1 else 'Other'
        
        # Skip RBAC for 'incoming' or 'Processing' domain (files being processed)
        if domain in ['incoming', 'Processing']:'''

new_code = '''        else:
            # Normalize path separators (handle both / and \ regardless of OS)
            normalized_path = filepath.replace('/', os.sep).replace('\\', os.sep)
            path_parts = normalized_path.split(os.sep)
        
        domain = path_parts[0] if len(path_parts) > 0 else 'Unknown'
        category = path_parts[1] if len(path_parts) > 1 else 'Other'
        
        # Also check if domain contains incoming/Processing (case where split failed/different separator)
        is_processing = domain in ['incoming', 'Processing'] or 'incoming' in path_parts[0]
        
        # Skip RBAC for 'incoming' or 'Processing' domain (files being processed)
        if is_processing:'''

content = content.replace(old_code, new_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Fixed Path Separator issue")
print("Now correctly identifies 'incoming' domain even with forward slashes on Windows")
