import sqlite3
import bcrypt
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages User Authentication and Role-Based Access Control using SQLite"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        abs_path = Path(self.db_path).resolve()
        logger.debug(f"Connecting to database: {abs_path}")
        
        # Use URI mode with cache=private to force schema reload
        conn = sqlite3.connect(f"file:{abs_path}?cache=private", uri=True, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initialize the users and roles tables"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Roles Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS roles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        permissions TEXT NOT NULL,
                        file_permissions TEXT
                    )
                ''')
                
                # Users Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        role_id INTEGER NOT NULL,
                        created_by INTEGER,
                        FOREIGN KEY (role_id) REFERENCES roles (id)
                    )
                ''')
                
                # Create Default 'Admin' Role if not exists
                cursor.execute("SELECT id FROM roles WHERE name = 'Admin'")
                if not cursor.fetchone():
                    logger.info("Initializing Default Admin Role...")
                    # Admin has wildcard permission '*'
                    cursor.execute(
                        "INSERT INTO roles (name, permissions) VALUES (?, ?)", 
                        ('Admin', '["*"]')
                    )
                    
                conn.commit()
        except Exception as e:
            logger.error(f"AuthDB Init Error: {e}")
            raise

    # --- Role Management ---
    
    def create_role(self, name: str, permissions: List[str], file_permissions: dict = None) -> bool:
        """Create a new role with specific permissions and optional file access permissions"""
        import json
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Serialize file_permissions if provided
                file_perms_json = json.dumps(file_permissions) if file_permissions else None
                
                cursor.execute(
                    "INSERT INTO roles (name, permissions, file_permissions) VALUES (?, ?, ?)",
                    (name, json.dumps(permissions), file_perms_json)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Role '{name}' already exists.")
            return False
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            return False

    def get_all_roles(self) -> List[Dict]:
        """List all roles with file permissions"""
        import json
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM roles")
                rows = cursor.fetchall()
                
                result = []
                for row in rows:
                    # Safely handle file_permissions - may not exist in old schemas
                    file_perms = None
                    try:
                        # Try to access file_permissions column
                        if 'file_permissions' in row.keys():
                            file_perm_raw = row['file_permissions']
                            if file_perm_raw:
                                file_perms = json.loads(file_perm_raw)
                    except (KeyError, IndexError, TypeError):
                        # Column doesn't exist or can't be accessed
                        file_perms = None
                    
                    result.append({
                        "id": row['id'], 
                        "name": row['name'], 
                        "permissions": json.loads(row['permissions']),
                        "file_permissions": file_perms
                    })
                
                return result
        except Exception as e:
            logger.error(f"Error listing roles: {e}")
            return []

    def get_role_permissions(self, role_id: int) -> List[str]:
        import json
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT permissions FROM roles WHERE id = ?", (role_id,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row['permissions'])
                return []
        except Exception as e:
            logger.error(f"Error fetching permissions: {e}")
            return []

    # --- User Management ---

    def create_user(self, username: str, password: str, role_id: int, created_by: int = None) -> Tuple[bool, str]:
        """Create a new user. Returns (Success, Message)"""
        if not username or not password:
            return False, "Username and password required"
            
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role_id, created_by) VALUES (?, ?, ?, ?)",
                    (username, hashed, role_id, created_by)
                )
                conn.commit()
                return True, "User created successfully"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False, str(e)

    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """Verify credentials and return user info with role"""
        import json
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.id, u.username, u.password_hash, r.name as role_name, r.permissions
                    FROM users u
                    JOIN roles r ON u.role_id = r.id
                    WHERE u.username = ?
                ''', (username,))
                
                row = cursor.fetchone()
                if row:
                    stored_hash = row['password_hash'].encode('utf-8')
                    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                        return {
                            "id": row['id'],
                            "username": row['username'],
                            "role": row['role_name'],
                            "permissions": json.loads(row['permissions'])
                        }
        except Exception as e:
            logger.error(f"Login verification error: {e}")
            
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user details by username"""
        import json
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT u.id, u.username, u.role_id, r.name as role_name, r.permissions, r.file_permissions
                    FROM users u
                    JOIN roles r ON u.role_id = r.id
                    WHERE u.username = ?
                """, (username,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Parse file permissions if present
                file_perms = None
                if row['file_permissions']:
                    try:
                        file_perms = json.loads(row['file_permissions'])
                    except:
                        file_perms = None
                
                return {
                    'id': row['id'],
                    'username': row['username'],
                    'role_id': row['role_id'],
                    'role': row['role_name'],
                    'permissions': json.loads(row['permissions']),
                    'file_permissions': file_perms
                }
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None


    def get_all_users(self) -> List[Dict]:
        """List all users"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.id, u.username, r.name as role_name, u.role_id
                    FROM users u 
                    JOIN roles r ON u.role_id = r.id
                ''')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    def update_user_role(self, user_id: int, new_role_id: int) -> Tuple[bool, str]:
        """Update a user's role. Returns (Success, Message)"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Verify role exists
                cursor.execute("SELECT id FROM roles WHERE id = ?", (new_role_id,))
                if not cursor.fetchone():
                    return False, "Role does not exist"
                
                cursor.execute(
                    "UPDATE users SET role_id = ? WHERE id = ?",
                    (new_role_id, user_id)
                )
                conn.commit()
                return True, "User role updated successfully"
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            return False, str(e)

    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """Delete a user. Returns (Success, Message)"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Don't allow deleting the last admin
                cursor.execute('''
                    SELECT COUNT(*) as admin_count FROM users u
                    JOIN roles r ON u.role_id = r.id
                    WHERE r.name = 'Admin'
                ''')
                admin_count = cursor.fetchone()['admin_count']
                
                cursor.execute('''
                    SELECT r.name FROM users u
                    JOIN roles r ON u.role_id = r.id
                    WHERE u.id = ?
                ''', (user_id,))
                user_row = cursor.fetchone()
                
                if user_row and user_row['name'] == 'Admin' and admin_count <= 1:
                    return False, "Cannot delete the last admin user"
                
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                return True, "User deleted successfully"
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False, str(e)

    def update_user_password(self, user_id: int, new_password: str, current_password: str = None, is_admin: bool = False) -> Tuple[bool, str]:
        """Update a user's password. 
        Args:
            user_id: ID of user whose password to change
            new_password: New password (min 6 chars)
            current_password: Current password (required if not admin)
            is_admin: Whether requester is admin (can skip current password check)
        Returns: (Success, Message)
        """
        # Validate password length
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters"
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # If not admin, verify current password
                if not is_admin:
                    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
                    row = cursor.fetchone()
                    if not row:
                        return False, "User not found"
                    
                    stored_hash = row['password_hash'].encode('utf-8')
                    if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash):
                        return False, "Current password is incorrect"
                
                # Hash new password and update
                new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (new_hash, user_id)
                )
                conn.commit()
                return True, "Password updated successfully"
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            return False, str(e)


    # --- Role Update/Delete ---

    def update_role(self, role_id: int, name: str = None, permissions: List[str] = None, file_permissions: dict = None) -> Tuple[bool, str]:
        """Update a role's name, permissions, or file_permissions. Returns (Success, Message)"""
        import json
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Don't allow modifying Admin role
                cursor.execute("SELECT name FROM roles WHERE id = ?", (role_id,))
                row = cursor.fetchone()
                if row and row['name'] == 'Admin':
                    return False, "Cannot modify the Admin role"
                
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = ?")
                    params.append(name)
                
                if permissions is not None:
                    updates.append("permissions = ?")
                    params.append(json.dumps(permissions))
                
                if file_permissions is not None:
                    updates.append("file_permissions = ?")
                    params.append(json.dumps(file_permissions))
                
                if not updates:
                    return False, "No updates provided"
                
                params.append(role_id)
                query = f"UPDATE roles SET {', '.join(updates)} WHERE id = ?"
                
                logger.debug(f"Executing query: {query} with params: {params}")
                cursor.execute(query, params)
                conn.commit()
                return True, "Role updated successfully"
        except sqlite3.IntegrityError:
            return False, "Role name already exists"
        except Exception as e:
            logger.error(f"Error updating role: {e}")
            return False, str(e)

    def delete_role(self, role_id: int) -> Tuple[bool, str]:
        """Delete a role. Returns (Success, Message)"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Don't allow deleting Admin role
                cursor.execute("SELECT name FROM roles WHERE id = ?", (role_id,))
                row = cursor.fetchone()
                if row and row['name'] == 'Admin':
                    return False, "Cannot delete the Admin role"
                
                # Check if any users have this role
                cursor.execute("SELECT COUNT(*) as user_count FROM users WHERE role_id = ?", (role_id,))
                user_count = cursor.fetchone()['user_count']
                
                if user_count > 0:
                    return False, f"Cannot delete role: {user_count} user(s) assigned to this role"
                
                cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
                conn.commit()
                return True, "Role deleted successfully"
        except Exception as e:
            logger.error(f"Error deleting role: {e}")
            return False, str(e)

