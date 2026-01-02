"""
Role-Based File Access Control (RBAC)
Maps roles to allowed file domains and categories
"""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Role to File Access Mapping
ROLE_FILE_ACCESS = {
    'Admin': {
        'allowed_domains': '*',  # Wildcard - full access
        'allowed_categories': '*',
        'description': 'Full access to all files'
    },
    'Manager': {
        'allowed_domains': ['Company', 'Business', 'Finance', 'Technology'],
        'denied_categories': ['Personal', 'Medical'],
        'description': 'Business and company files'
    },
    'Teacher': {
        'allowed_domains': ['Education', 'School', 'College', 'ResearchPaper', 'Technology'],
        'denied_categories': ['Admin', 'HR', 'Finance'],
        'description': 'Educational content, no admin records'
    },
    'Student': {
        'allowed_domains': ['Education', 'School', 'College', 'Technology'],
        'denied_categories': ['Admin', 'Placement', 'HR'],
        'description': 'Course materials only, no admin access'
    },
    'Doctor': {
        'allowed_domains': ['Healthcare', 'ResearchPaper'],
        'denied_categories': [],
        'description': 'All healthcare and research files'
    },
    'Nurse': {
        'allowed_domains': ['Healthcare'],
        'allowed_categories': ['Clinical', 'LabReport', 'Imaging'],
        'denied_categories': ['Finance', 'Admin', 'HR'],
        'description': 'Patient files only, no admin/finance'
    },
    'Accountant': {
        'allowed_domains': ['Finance', 'Company'],
        'allowed_categories': ['Accounting', 'Tax', 'Payroll'],
        'denied_categories': ['Personal', 'Medical'],
        'description': 'Financial documents only'
    },
    'HR': {
        'allowed_domains': ['Company'],
        'allowed_categories': ['HR', 'Payroll'],
        'denied_categories': ['Finance', 'Medical', 'Product'],
        'description': 'HR and employee files'
    },
    'Developer': {
        'allowed_domains': ['Technology', 'Code', 'Documentation'],
        'denied_categories': ['Finance', 'HR', 'Personal'],
        'description': 'Technical and code files'
    }
}


@lru_cache(maxsize=32)
def get_role_file_permissions(user_role: str) -> dict:
    """
    Get file permissions for a role from database, with fallback to hardcoded defaults
    
    Args:
        user_role: User's role name
        
    Returns:
        Dictionary with file permission configuration
    """
    try:
        # Try to load from database first
        from core.auth_manager import AuthManager
        from pathlib import Path
        
        auth_manager = AuthManager(Path("data/users.db"))
        roles = auth_manager.get_all_roles()
        
        logger.debug(f"Looking for role '{user_role}' in database ({len(roles)} roles total)")
        
        for role in roles:
            if role['name'] == user_role and role.get('file_permissions'):
                logger.debug(f"Loaded file permissions for {user_role} from database")
                return role['file_permissions']
        
    except Exception as e:
        logger.warning(f"Could not load file permissions from database: {e}")
    
    # Fallback to hardcoded defaults
    if user_role in ROLE_FILE_ACCESS:
        logger.debug(f"Using default file permissions for {user_role}")
        return ROLE_FILE_ACCESS[user_role]
    
    logger.warning(f"No file permissions found for role: {user_role}")
    return {}


def check_file_access(user_role: str, file_domain: str, file_category: str = None) -> bool:
    """
    Check if a user role has access to a file based on its domain and category
    
    Args:
        user_role: User's role name (e.g., 'Student', 'Nurse')
        file_domain: File's domain classification (e.g., 'Healthcare', 'Education')
        file_category: Optional file category (e.g., 'Clinical', 'Admin')
        
    Returns:
        True if user can access the file, False otherwise
    """
    # Get role configuration (from database or defaults)
    role_config = get_role_file_permissions(user_role)
    
    if not role_config:
        logger.warning(f"Unknown role: {user_role}. Denying access.")
        return False
    
    # Admin wildcard - allow all
    if role_config.get('allowed_domains') == '*':
        return True
    
    # Check domain access
    allowed_domains = role_config.get('allowed_domains', [])
    if file_domain not in allowed_domains:
        logger.warning(f"Access denied: role={user_role}, domain={file_domain} not in allowed_domains")
        return False
    
    # Check category restrictions if category is specified
    if file_category:
        denied_categories = role_config.get('denied_categories', [])
        if file_category in denied_categories:
            return False
        
        # If specific allowed_categories list exists, enforce it
        allowed_categories = role_config.get('allowed_categories')
        if allowed_categories and allowed_categories != '*':
            if file_category not in allowed_categories:
                return False
    
    return True


def get_role_description(user_role: str) -> str:
    """Get human-readable description of role's file access"""
    if user_role in ROLE_FILE_ACCESS:
        return ROLE_FILE_ACCESS[user_role].get('description', 'No description')
    return 'Unknown role'
