import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(os.getcwd())
sys.path.append(str(project_root))

from core.auth_manager import AuthManager

def add_test_user():
    db_path = project_root / 'data' / 'users.db'
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return

    auth = AuthManager(db_path)
    
    # Get Admin role ID (usually 1)
    roles = auth.get_all_roles()
    admin_role = next((r for r in roles if r['name'] == 'Admin'), None)
    
    if not admin_role:
        # Create admin role if missing (unlikely)
        auth.create_role('Admin', ['*'])
        roles = auth.get_all_roles()
        admin_role = next((r for r in roles if r['name'] == 'Admin'), None)
    
    role_id = admin_role['id']
    
    # Create test user
    success, msg = auth.create_user("testuser", "testpassword123", role_id)
    if success:
        print("Test user created successfully.")
    else:
        print(f"Failed to create test user: {msg}")

if __name__ == "__main__":
    add_test_user()
