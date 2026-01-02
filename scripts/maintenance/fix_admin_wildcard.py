"""
Fix Admin wildcard permission check in delete_file
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix permission check to include wildcard
old_check = '''        # Check permissions
        can_delete_all = 'files.delete.all' in permissions
        can_delete_own = 'files.delete.own' in permissions'''

new_check = '''        # Check permissions (include wildcard for Admin)
        can_delete_all = 'files.delete.all' in permissions or '*' in permissions
        can_delete_own = 'files.delete.own' in permissions or '*' in permissions'''

content = content.replace(old_check, new_check)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Updated permission check to support '*' wildcard")
print("Admin will now have delete permissions")
