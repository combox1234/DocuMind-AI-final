"""
Fix syntax error in app.py line 1047-1048
"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove lines 1047-1048 (the stray else clause)
# Line 1047 (index 1046): "        else:\r\n"
# Line 1048 (index 1047): "        quota_str = None\r\n"
if 'else:' in lines[1046] and 'quota_str = None' in lines[1047]:
    del lines[1046:1048]

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("SUCCESS: Fixed syntax error in app.py")
print("Removed orphaned else clause at line 1047")
