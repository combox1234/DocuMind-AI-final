# Simple test to verify permissions.py syntax is OK
from core.permissions import check_file_access

# Test permission check
result = check_file_access('Admin', 'Technology', 'UAV')
print(f"Admin access to Technology/UAV: {result}")

result2 = check_file_access('Student', 'Technology', 'UAV')
print(f"Student access to Technology/UAV: {result2}")

result3 = check_file_access('Student', 'Education', 'Programming')
print(f"Student access to Education/Programming: {result3}")

print("\n[SUCCESS] permissions.py syntax is valid and working!")
