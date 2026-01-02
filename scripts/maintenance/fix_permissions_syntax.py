"""Fix the syntax error in permissions.py by replacing escaped newline with actual newline"""

# Read the file
with open('core/permissions.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the literal escaped newline with actual newline
# The pattern is: ])\\n    if
# Should be: ])\n    if
content = content.replace('])\\n    if', '])\n    if')

# Write back
with open('core/permissions.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] Fixed syntax error in permissions.py")
