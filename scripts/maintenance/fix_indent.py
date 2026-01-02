"""
Fix indentation error in app.py line 1037
"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix lines 1037-1048 indentation
# Change from 12 spaces to 8 spaces
for i in range(1036, 1048):  # 0-indexed, so line 1037 is index 1036
    if lines[i].startswith('            '):  # 12 spaces
        lines[i] = lines[i][4:]  # Remove 4 spaces

# Also fix user_id to current_user_id on line 1041
lines[1040] = lines[1040].replace('(user_id,)', '(current_user_id,)')

# Remove the else clause that's not needed
if 'else:' in lines[1047] and 'quota_str = None' in lines[1048]:
    # Remove lines 1047-1048
    del lines[1046:1048]

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("SUCCESS: Fixed indentation in app.py")
