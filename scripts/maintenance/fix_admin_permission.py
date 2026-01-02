"""
Fix the permission check in main.js to allow Admin to see upload buttons
"""

file_path = "static/js/main.js"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the permission check line
old_line = "        if (permissions.includes('files.upload')) {"
new_lines ="""        // Admin has wildcard '*', others need explicit 'files.upload'
        const role = sessionStorage.getItem('role');
        const hasPermission = role === 'Admin' || permissions.includes('*') || permissions.includes('files.upload');
        if (hasPermission) {"""

# Replace
content = content.replace(old_line, new_lines)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Fixed permission check in main.js")
print("Admin users will now see upload/delete buttons!")
