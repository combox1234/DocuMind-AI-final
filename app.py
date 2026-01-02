"""
Universal RAG System - Flask Application
"""

from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import logging
import os
import redis
import sqlite3

from core import DatabaseManager, LLMService
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from core.classifier import DocumentClassifier
from core.chat_manager import ChatManager
from core.analytics import Analytics
from core.duplicate_detector import DuplicateDetector
from core.category_manager import CategoryManager
from middleware.auth import require_manager, require_permission, get_current_user
from config import Config

# Setup logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR = BASE_DIR / "data"
# Default to chroma_db_docker if v2 is empty/missing
# Default to chroma_db_docker if v2 is empty/missing
DB_DIR = Config.DB_DIR
SORTED_DIR = DATA_DIR / "sorted"
SORTED_DIR = DATA_DIR / "sorted"

# Initialize services
db_manager = DatabaseManager(DB_DIR)
llm_service = LLMService(model='llama3.2')
classifier = DocumentClassifier()
chat_manager = ChatManager(DATA_DIR)

# Initialize Redis and new modules
redis_client = redis.Redis.from_url(Config.CELERY_BROKER_URL, decode_responses=True)
analytics = Analytics(redis_client, SORTED_DIR)
duplicate_detector = DuplicateDetector(redis_client)
category_manager = CategoryManager(redis_client)

# Initialize JWT
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
jwt = JWTManager(app)

# Mock User Database (For MVP)
# Initialize AuthManager
from core.auth_manager import AuthManager
auth_manager = AuthManager(DATA_DIR / 'users.db')

# Create default admin if not exists (Role ID 1 is Admin by default in AuthManager init)
# We need to find if admin role exists, let's assume ID 1 is Admin for now, or fetch it.
# Actually AuthManager logic handles Role creation. We need to create the User.
# We'll do a quick check on startup.
admin_user = auth_manager.verify_user("admin", "admin123")
if not admin_user:
    # Check if admin exists at all (maybe password changed)
    # Ideally should check by username, but verify_user does auth.
    # We will use get_all_users() to check.
    users = auth_manager.get_all_users()
    admin_exists = any(u['username'] == 'admin' for u in users)
    if not admin_exists:
        logger.info("Creating default 'admin' user...")
        # Assuming Role ID 1 is Admin (created in _init_db)
        # To be cleaner, we could add a get_role_id_by_name method, but for now ID 1 is safe 
        # as it's the first thing inserted in _init_db
        auth_manager.create_user("admin", "admin123", role_id=1, created_by=0)

logger.info(f"✅ Database initialized with {db_manager.get_count()} documents")


@app.route('/')
def index():
    """Render main chat interface (auth checked client-side)"""
    return render_template('index.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    """Test endpoint"""
    return jsonify({'status': 'OK', 'message': 'Server is running'})


# --- Auth Routes ---
@app.route('/login', methods=['GET'])
def login_page():
    """Render login page"""
    return render_template('login.html')


@app.route('/admin', methods=['GET'])
def admin_dashboard():
    """Render admin dashboard (auth enforced client-side in template)"""
    return render_template('admin_dashboard.html')


@app.route('/login', methods=['POST'])
def login():
    """Handle login and issue JWT"""
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
        
    user = auth_manager.verify_user(username, password)
    
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    # Embed permissions in token
    additional_claims = {
        "role": user['role'],
        "permissions": user['permissions']
    }
    
    access_token = create_access_token(identity=username, additional_claims=additional_claims)
    return jsonify(access_token=access_token, username=username, role=user['role'])


# --- Admin API Routes ---
@app.route('/api/admin/users', methods=['GET'])
@require_permission('admin.dashboard')
def list_users():
    """List all users (Admin only)"""
    users = auth_manager.get_all_users()
    return jsonify(users)

@app.route('/api/admin/users', methods=['POST'])
@require_permission('admin.dashboard')
def create_user():
    """Create a new user (Admin only)"""
    data = request.json
    success, msg = auth_manager.create_user(
        data.get('username'), 
        data.get('password'), 
        data.get('role_id'),
        created_by=0 # In real app, extract ID from JWT
    )
    if success:
        return jsonify({'status': 'success', 'message': msg})
    return jsonify({'error': msg}), 400

@app.route('/api/admin/roles', methods=['GET'])
@require_permission('admin.dashboard')
def get_roles():
    """Get all roles (Admin only)"""
    logger.debug("=== GET /api/admin/roles called ===")
    try:
        roles = auth_manager.get_all_roles()
        logger.debug(f">>> Retrieved {len(roles)} roles from auth_manager")
        logger.debug(f">>> Roles data: {roles}")
        return jsonify(roles)
    except Exception as e:
        logger.error(f"!!! ERROR in get_roles: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/roles', methods=['POST'])
@require_permission('admin.dashboard')
def create_role():
    """Create a new role with file permissions (Admin only)"""
    try:
        data = request.json
        name = data.get('name')
        permissions = data.get('permissions', [])
        file_permissions = data.get('file_permissions')  # File access config
        
        if not name or not permissions:
            return jsonify({'error': 'Name and permissions required'}), 400
        
        success = auth_manager.create_role(name, permissions, file_permissions)
        if success:
            return jsonify({'status': 'success', 'message': 'Role created'})
        return jsonify({'error': 'Role already exists or creation failed'}), 400
    except Exception as e:
        logger.error(f"Error creating role: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/roles/<int:role_id>', methods=['PUT'])
@require_permission('admin.dashboard')
def update_role(role_id):
    """Update a role's permissions or file_permissions (Admin only)"""
    try:
        data = request.json
        name = data.get('name')
        permissions = data.get('permissions')
        file_permissions = data.get('file_permissions')  # File access config
        
        success, msg = auth_manager.update_role(
            role_id, 
            name=name, 
            permissions=permissions,
            file_permissions=file_permissions
        )
        
        if success:
            return jsonify({'status': 'success', 'message': msg})
        return jsonify({'error': msg}), 400
    except Exception as e:
        logger.error(f"Error updating role: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/roles/<int:role_id>', methods=['DELETE'])
@require_permission('admin.dashboard')
def delete_role(role_id):
    """Delete a role (Admin only)"""
    success, msg = auth_manager.delete_role(role_id)
    if success:
        return jsonify({'status': 'success', 'message': msg})
    return jsonify({'error': msg}), 400

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@require_permission('admin.dashboard')
def update_user(user_id):
    """Update a user's role (Admin only)"""
    data = request.json
    success, msg = auth_manager.update_user_role(user_id, data.get('role_id'))
    if success:
        return jsonify({'status': 'success', 'message': msg})
    return jsonify({'error': msg}), 400


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@require_permission('admin.dashboard')
def delete_user(user_id):
    """Delete a user (Admin only)"""
    success, msg = auth_manager.delete_user(user_id)
    if success:
        return jsonify({'status': 'success', 'message': msg})
    return jsonify({'error': msg}), 400


@app.route('/api/admin/users/<int:user_id>/password', methods=['PUT'])
@jwt_required()
@require_permission('admin.dashboard')
def admin_change_user_password(user_id):
    """Admin changes any user's password"""
    data = request.get_json()
    new_password = data.get('new_password')
    
    if not new_password:
        return jsonify({'error': 'New password required'}), 400
    
    success, message = auth_manager.update_user_password(
        user_id=user_id,
        new_password=new_password,
        is_admin=True
    )
    
    if success:
        return jsonify({'status': 'success', 'message': message})
    return jsonify({'error': message}), 400


@app.route('/api/users/change-password', methods=['POST'])
@jwt_required()
def user_change_password():
    """User changes their own password"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password required'}), 400
    
    success, message = auth_manager.update_user_password(
        user_id=current_user_id,
        new_password=new_password,
        current_password=current_password,
        is_admin=False
    )
    
    if success:
        return jsonify({'status': 'success', 'message': message})
    return jsonify({'error': message}), 400




# --- Chat History APIs ---
@app.route('/api/chats', methods=['GET'])
@jwt_required()
def get_chats():
    """Get chat sessions for current user"""
    user_id = get_jwt_identity()
    return jsonify(chat_manager.get_user_chats(user_id))

@app.route('/api/chats', methods=['POST'])
@jwt_required()
def create_chat():
    """Create a new chat session"""
    user_id = get_jwt_identity()
    data = request.json or {}
    title = data.get('title', 'New Chat')
    chat = chat_manager.create_chat(title, user_id=user_id)
    return jsonify(chat)

@app.route('/api/chats/<chat_id>', methods=['DELETE'])
@jwt_required()
def delete_chat(chat_id):
    """Delete a chat session"""
    chat_manager.delete_chat(chat_id)
    return jsonify({'status': 'success'})

@app.route('/api/admin/chats/all', methods=['GET'])
@require_permission('admin.dashboard')
def get_all_chats_admin():
    """Get all users' chats (admin only) - Flat List"""
    all_chats_metadata = chat_manager._load_metadata()
    users = auth_manager.get_all_users()
    
    # Create a map of ID -> Username and Username -> Username (for legacy/string IDs)
    user_map = {str(u['id']): u['username'] for u in users}
    # Also map usernames to themselves in case user_id was saved as username
    for u in users:
        user_map[u['username']] = u['username']

    flattened_chats = []
    
    for chat in all_chats_metadata:
        uid = str(chat.get('user_id'))
        # Resolve username
        username = user_map.get(uid, f"Unknown ({uid})") if uid and uid != 'None' else "Guest"
        
        chat_entry = chat.copy()
        chat_entry['username'] = username
        flattened_chats.append(chat_entry)
        
    return jsonify(flattened_chats)

@app.route('/api/chats/<chat_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(chat_id):
    """Get messages for a specific chat"""
    messages = chat_manager.get_messages(chat_id)
    return jsonify(messages)

@app.route('/api/chats/<chat_id>/title', methods=['PUT'])
@jwt_required()
def update_title(chat_id):
    """Update chat title"""
    data = request.json
    new_title = data.get('title')
    if new_title:
        chat_manager.update_title(chat_id, new_title)
    return jsonify({'status': 'success'})



@app.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """Handle chat queries with role-based access control"""
    try:
        data = request.get_json(silent=True)
        if data and 'message' in data:
            logger.debug(f"⚡ RECEIVED REQUEST: {data['message']}")
        
        if not data:
            return jsonify({'error': 'Invalid request'}), 400
        
        query = str(data.get('query', '')).strip()
        chat_id = data.get('chat_id')
        
        if not query:
            return jsonify({'error': 'Empty query'}), 400
        
        # RBAC: Extract user role from JWT claims
        claims = get_jwt()
        user_role = claims.get('role', None)  # Get role from JWT
        logger.debug(f"User role for RBAC: {user_role}")
        
        # FILENAME DETECTION: Check if user is asking for a specific file
        # Patterns: "give me xyz.py", "what's in abc.pdf", "show me test.js"
        import re
        filename_pattern = r'\b([a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)\b'
        filename_matches = re.findall(filename_pattern, query.lower())
        
        # Keywords that indicate file retrieval intent
        file_keywords = ['give me', 'show me', 'what', 'whats', 'what is', 'in', 'inside', 'content']
        asking_for_file = any(keyword in query.lower() for keyword in file_keywords)
        
        # If filename detected AND asking for it, try full file retrieval
        if filename_matches and asking_for_file:
            for detected_filename in filename_matches:
                full_content = db_manager.get_full_file(detected_filename)
                if full_content:
                    logger.debug(f"📄 Full file retrieval triggered for: {detected_filename}")
                    
                    # Create snippet for UI buttons (first 500 chars as preview)
                    preview = full_content[:500] + "..." if len(full_content) > 500 else full_content
                    
                    response = {
                        'answer': f"Here is the complete content of **{detected_filename}**:\n\n```\n{full_content}\n```",
                        'cited_files': [detected_filename],
                        'confidence_score': 1.0,
                        'source_snippets': [{
                            'filename': detected_filename,
                            'text': preview,
                            'category': 'Full File'
                        }],
                        'detected_language': 'en',
                        'full_file_retrieval': True
                    }
                    
                    # Save to chat history
                    if chat_id:
                        messages = chat_manager.get_messages(chat_id)
                        messages.append({
                            "sender": "user", 
                            "text": query, 
                            "timestamp": __import__('datetime').datetime.now().isoformat()
                        })
                        messages.append({
                            "sender": "assistant", 
                            "text": response['answer'], 
                            "cited_files": response['cited_files'],
                            "confidence_score": response['confidence_score'],
                            "source_snippets": response['source_snippets'],
                            "timestamp": __import__('datetime').datetime.now().isoformat()
                        })
                        chat_manager.save_messages(chat_id, messages)
                        
                        if len(messages) <= 2:
                            new_title = (query[:30] + '...') if len(query) > 30 else query
                            chat_manager.update_title(chat_id, new_title)
                    
                    return jsonify(response)
        
        # NORMAL RAG FLOW with RBAC: Pass user_role to query
        # V6: Increase to 25 for Re-ranking (CrossEncoder will filter to Top 5)
        chunks, rbac_filtered = db_manager.query(query, n_results=25, user_role=user_role)
        
        if not chunks:
            # Check if it was RBAC that blocked access vs. no results found
            if rbac_filtered:
                response = {
                    'answer': '🔒 **Access Denied**: You do not have permission to access documents related to this query. Please contact your administrator if you believe this is an error.',
                    'cited_files': [],
                    'confidence_score': 0,
                    'source_snippets': [],
                    'detected_language': 'en'
                }
            else:
                response = {
                    'answer': 'No relevant documents found.',
                    'cited_files': [],
                    'confidence_score': 0,
                    'source_snippets': [],
                    'detected_language': 'en'
                }
        else:
            answer, cited_files, confidence_score, source_snippets, detected_lang = llm_service.generate_response(query, chunks)
            response = {
                'answer': answer,
                'cited_files': cited_files,
                'confidence_score': confidence_score,
                'source_snippets': source_snippets,
                'detected_language': detected_lang
            }
            
        # Save to chat history if chat_id provided
        if chat_id:
            messages = chat_manager.get_messages(chat_id)
            messages.append({
                "sender": "user", 
                "text": query, 
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
            messages.append({
                "sender": "assistant", 
                "text": response['answer'], 
                "cited_files": response['cited_files'],
                "confidence_score": response['confidence_score'],
                "source_snippets": response['source_snippets'],
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
            chat_manager.save_messages(chat_id, messages)
            
            # Auto-update title if it's the first message and title is currently generic
            if len(messages) <= 2:
                 # Simple heuristic: first few words of query
                 new_title = (query[:30] + '...') if len(query) > 30 else query
                 chat_manager.update_title(chat_id, new_title)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/classify', methods=['POST'])
def classify():
    """Classify given text/filename into Domain/Category with confidence.

    Request JSON:
    - text: Optional string content to classify
    - filename: Optional filename to aid classification

    Returns JSON with: domain, category, file_extension, confidence,
    domain_score, category_score.
    """
    try:
        data = request.get_json(silent=True) or {}
        text = str(data.get('text') or '').strip()
        filename = str(data.get('filename') or '').strip()

        if not text and not filename:
            return jsonify({'error': 'Provide at least text or filename'}), 400

        result = classifier.classify_hierarchical(text or '', filename or '')
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in /classify: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/download/<path:filename>')
@require_permission('files.download')
def download_file(filename):
    """Download cited file (requires files.download permission)"""
    try:
        # Search for file in sorted directory
        for root, dirs, files in os.walk(SORTED_DIR):
            if filename in files:
                filepath = os.path.join(root, filename)
                return send_file(filepath, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/export-chat', methods=['POST'])
def export_chat():
    """Export chat history as JSON or TXT"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'json')
        chat_history = data.get('chat_history', [])
        
        if format_type == 'json':
            response_data = {
                'export_date': __import__('datetime').datetime.now().isoformat(),
                'total_messages': len(chat_history),
                'chat_history': chat_history
            }
            return jsonify(response_data)
        
        elif format_type == 'txt':
            txt_content = "DocuMind AI - Chat History\n"
            txt_content += f"Exported: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            txt_content += "=" * 60 + "\n\n"
            
            for msg in chat_history:
                txt_content += f"[{msg.get('timestamp', 'N/A')}] {msg.get('sender', 'Unknown')}\n"
                txt_content += f"{msg.get('text', '')}\n"
                if msg.get('confidence_score') is not None:
                    txt_content += f"Confidence: {msg.get('confidence_score', 0)}%\n"
                txt_content += "-" * 60 + "\n\n"
            
            return {'content': txt_content, 'format': 'txt'}
        
        return jsonify({'error': 'Unsupported format'}), 400
        
    except Exception as e:
        logger.error(f"Error exporting chat: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/status')
def status():
    """Get system status"""
    try:
        doc_count = db_manager.get_count()
        
        # Count files in sorted directory
        sorted_files = 0
        categories = []
        for category_dir in SORTED_DIR.iterdir():
            if category_dir.is_dir():
                categories.append(category_dir.name)
                sorted_files += len(list(category_dir.glob('*')))
        
        return jsonify({
            'database_count': doc_count,
            'sorted_files': sorted_files,
            'categories': categories,
            'ollama_available': llm_service.check_availability()
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


def check_ollama():
    """Check if Ollama is available"""
    try:
        ollama.list()
        return True
    except:
        return False


# ===== NEW API ENDPOINTS =====

@app.route('/api/analytics', methods=['GET'])
@require_permission('analytics.view')
def get_analytics():
    """Get sorting analytics and statistics (requires analytics.view permission)"""
    try:
        use_cache = request.args.get('cache', 'true').lower() == 'true'
        stats = analytics.get_sorting_stats(use_cache=use_cache)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/recent', methods=['GET'])
@require_permission('analytics.view')
def get_recent_uploads():
    """Get recently uploaded files (requires analytics.view permission)"""
    try:
        days = int(request.args.get('days', 7))
        recent = analytics.get_recent_uploads(days=days)
        return jsonify({'recent_files': recent})
    except Exception as e:
        logger.error(f"Error getting recent uploads: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/duplicates', methods=['GET'])
@require_permission('files.view_duplicates')
def get_duplicates():
    """Get all duplicate file groups (requires files.view_duplicates permission)"""
    try:
        duplicates = duplicate_detector.get_all_duplicates()
        return jsonify({
            'duplicates': duplicates,
            'count': len(duplicates)
        })
    except Exception as e:
        logger.error(f"Error getting duplicates: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/duplicates/<file_hash>', methods=['DELETE'])
@require_permission('files.delete_duplicates')
def delete_duplicate(file_hash):
    """Delete a duplicate file (requires files.delete_duplicates permission)"""
    try:
        filepath = request.json.get('filepath')
        if not filepath:
            return jsonify({'error': 'Filepath required'}), 400
        
        success = duplicate_detector.remove_duplicate(file_hash, filepath)
        if success:
            return jsonify({'status': 'success', 'message': 'Duplicate removed'})
        else:
            return jsonify({'error': 'Failed to remove duplicate'}), 500
    except Exception as e:
        logger.error(f"Error deleting duplicate: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories (default + custom)"""
    try:
        domain = request.args.get('domain')
        if domain:
            # Get categories for specific domain
            from core.classifier import DocumentClassifier
            default_cats = DocumentClassifier.CATEGORY_KEYWORDS_BY_DOMAIN.get(domain, {})
            all_cats = category_manager.get_all_categories(domain, default_cats)
            return jsonify({'domain': domain, 'categories': all_cats})
        else:
            # Get all custom categories
            custom_cats = category_manager.list_all_custom_categories()
            return jsonify({'custom_categories': custom_cats})
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/categories', methods=['POST'])
@require_permission('categories.create')
def add_category():
    """Add a custom category (requires categories.create permission)"""
    try:
        data = request.json
        domain = data.get('domain')
        category_name = data.get('category_name')
        keywords = data.get('keywords', [])
        
        if not domain or not category_name or not keywords:
            return jsonify({'error': 'domain, category_name, and keywords are required'}), 400
        
        # Validate
        is_valid, message = category_manager.validate_category(category_name, keywords)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Add category
        success = category_manager.add_category(domain, category_name, keywords)
        if success:
            # Clear analytics cache to reflect new category
            analytics.clear_cache()
            return jsonify({
                'status': 'success',
                'message': f'Category "{category_name}" added to domain "{domain}"'
            })
        else:
            return jsonify({'error': 'Failed to add category'}), 500
    except Exception as e:
        logger.error(f"Error adding category: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/categories/<domain>/<category_name>', methods=['DELETE'])
@require_permission('categories.delete')
def delete_category(domain, category_name):
    """Delete a custom category (requires categories.delete permission)"""
    try:
        success = category_manager.delete_category(domain, category_name)
        if success:
            analytics.clear_cache()
            return jsonify({
                'status': 'success',
                'message': f'Category "{category_name}" deleted from domain "{domain}"'
            })
        else:
            return jsonify({'error': 'Category not found or failed to delete'}), 404
    except Exception as e:
        logger.error(f"Error deleting category: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/clear-cache', methods=['POST'])
@require_permission('analytics.clear_cache')
def clear_analytics_cache():
    """Clear analytics cache to force refresh (requires analytics.clear_cache permission)"""
    try:
        analytics.clear_cache()
        return jsonify({'status': 'success', 'message': 'Analytics cache cleared'})
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({'error': str(e)}), 500


# ===== FILE UPLOAD & MANAGEMENT ENDPOINTS =====

@app.route('/api/upload', methods=['POST'])
@jwt_required()
@require_permission('files.upload')
def upload_file():
    """Upload a file to the incoming directory (requires files.upload permission)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get user info
        username = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role', None)
        
        # Get user ID from database
        user_data = auth_manager.get_user_by_username(username)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        user_id = user_data['id']
        
        # Check file size (25MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Maximum size is 25MB (File size: {file_size / (1024*1024):.2f}MB)'}), 413
        
        # Check quota (skip for Admin)
        if user_role != 'Admin':
            # Count user's current uploads
            conn = sqlite3.connect(DATA_DIR / 'users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_uploads WHERE user_id = ?", (user_id,))
            current_count = cursor.fetchone()[0]
            conn.close()
            
            MAX_FILES = 10
            if current_count >= MAX_FILES:
                return jsonify({
                    'error': f'Upload limit reached ({current_count}/{MAX_FILES}). Delete some files to upload more.',
                    'quota': f'{current_count}/{MAX_FILES}'
                }), 429
        
        # Get filename and save to incoming directory
        filename = file.filename
        incoming_dir = Config.INCOMING_DIR
        incoming_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if file already exists
        filepath = incoming_dir / filename
        if filepath.exists():
            return jsonify({'error': f'File "{filename}" already exists in incoming directory'}), 409
        
        # Save file
        file.save(str(filepath))
        
        # Record upload in database
        conn = sqlite3.connect(DATA_DIR / 'users.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_uploads (user_id, filename, sorted_path, file_size)
            VALUES (?, ?, NULL, ?)
        """, (user_id, filename, file_size))
        conn.commit()
        conn.close()
        
        logger.info(f"File uploaded: {filename} ({file_size / 1024:.2f}KB) by {username}")
        
        # Get updated quota
        if user_role != 'Admin':
            conn = sqlite3.connect(DATA_DIR / 'users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_uploads WHERE user_id = ?", (user_id,))
            new_count = cursor.fetchone()[0]
            conn.close()
            quota_str = f'{new_count}/10'
        else:
            quota_str = 'Unlimited'
        
        return jsonify({
            'status': 'success',
            'message': f'File "{filename}" uploaded successfully and will be processed automatically',
            'filename': filename,
            'quota': quota_str
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/files', methods=['GET'])
@jwt_required()
def list_files():
    """List files - users see only their files, admin sees all files in sorted/"""
    try:
        # Get user info
        username = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role', None)
        
        # Get user ID
        user_data = auth_manager.get_user_by_username(username)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        current_user_id = user_data['id']
        
        files_list = []
        sorted_dir = Config.SORTED_DIR
        
        if user_role == 'Admin':
            # Admin sees ALL files in sorted directory (filesystem scan)
            # Get upload tracking data for uploader info
            conn = sqlite3.connect(DATA_DIR / 'users.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT uf.filename, u.username as uploader
                FROM user_uploads uf
                JOIN users u ON uf.user_id = u.id
            """)
            upload_map = {row['filename']: row['uploader'] for row in cursor.fetchall()}
            conn.close()
            
            # Scan sorted directory
            for root, dirs, files in os.walk(sorted_dir):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, sorted_dir)
                    
                    # Extract domain and category from path
                    path_parts = rel_path.split(os.sep)
                    domain = path_parts[0] if len(path_parts) > 0 else 'Unknown'
                    category = path_parts[1] if len(path_parts) > 1 else 'Other'
                    
                    # Get file stats
                    stats = os.stat(filepath)
                    
                    # Check if we have uploader info
                    uploader = upload_map.get(filename, 'System')
                    
                    files_list.append({
                        'filename': filename,
                        'path': rel_path,
                        'domain': domain,
                        'category': category,
                        'size': stats.st_size,
                        'uploaded_by': uploader,
                        'uploaded_at': stats.st_mtime,
                        'is_owner': False  # Admin doesn't own system files
                    })
        else:
            # Regular users see only their tracked uploads
            conn = sqlite3.connect(DATA_DIR / 'users.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT uf.filename, uf.sorted_path, uf.file_size, uf.uploaded_at, uf.user_id, u.username as uploader
                FROM user_uploads uf
                JOIN users u ON uf.user_id = u.id
                WHERE uf.user_id = ?
                ORDER BY uf.uploaded_at DESC
            """, (current_user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                filename = row['filename']
                sorted_path = row['sorted_path']
                uploader = row['uploader']
                owner_id = row['user_id']
                
                if sorted_path:
                    # File has been sorted
                    # Normalize separators to handle Windows paths in DB
                    normalized_path = sorted_path.replace('\\', '/')
                    path_parts = normalized_path.split('/')
                    domain = path_parts[0] if len(path_parts) > 0 else 'Unknown'
                    category = path_parts[1] if len(path_parts) > 1 else 'Other'
                    
                    # RBAC check for non-admin users
                    from core.permissions import check_file_access
                    if not check_file_access(user_role, domain, category):
                        continue  # Skip files user doesn't have domain access to
                    
                    # Build file path - sorted_path already includes subdirectories
                    filepath = sorted_dir / sorted_path
                    
                    # Check if file still exists
                    if not filepath.exists():
                        continue
                    
                    files_list.append({
                        'filename': filename,
                        'path': sorted_path,
                        'domain': domain,
                        'category': category,
                        'size': row['file_size'],
                        'uploaded_by': uploader,
                        'uploaded_at': row['uploaded_at'],
                        'is_owner': owner_id == current_user_id
                    })
                else:
                    # File is still being processed (in incoming directory)
                    files_list.append({
                        'filename': filename,
                        'path': 'incoming/' + filename,
                        'domain': 'Processing',
                        'category': 'Pending',
                        'size': row['file_size'],
                        'uploaded_by': uploader,
                        'uploaded_at': row['uploaded_at'],
                        'is_owner': owner_id == current_user_id
                    })
        
        return jsonify({
            'files': files_list,
            'count': len(files_list)
        })
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/files/<path:filepath>', methods=['DELETE'])
@jwt_required()
def delete_file(filepath):
    """Delete a file from sorted directory (requires appropriate permission)"""
    try:
        claims = get_jwt()
        user_role = claims.get('role', None)
        permissions = claims.get('permissions', [])
        
        # Check permissions (include wildcard for Admin)
        can_delete_all = 'files.delete.all' in permissions or '*' in permissions
        can_delete_own = 'files.delete.own' in permissions or '*' in permissions
        
        if not can_delete_all and not can_delete_own:
            return jsonify({'error': 'Permission denied: You cannot delete files'}), 403
        
        # Handle files in both incoming and sorted directories
        sorted_dir = Config.SORTED_DIR
        incoming_dir = Config.INCOMING_DIR
        
        # Handle different file locations
        if filepath.startswith('incoming/'):
            # File is marked as still processing
            filename = filepath.replace('incoming/', '')
            
            # Try incoming directory first
            full_path = incoming_dir / filename
            is_incoming = True
            
            # If not in incoming, search in sorted (*worker processed but DB not updated*)
            if not full_path.exists():
                # Search for file in sorted directory
                import glob
                pattern = str(sorted_dir / '**' / filename)
                matches = glob.glob(pattern, recursive=True)
                
                if matches:
                    full_path = Path(matches[0])
                    is_incoming = False  # Actually sorted
                else:
                    return jsonify({'error': 'File not found'}), 404
        else:
            # File is in sorted directory
            full_path = sorted_dir / filepath
            is_incoming = False
            
            # Security check - ensure path is within sorted directory
            if not str(full_path.resolve()).startswith(str(sorted_dir.resolve())):
                return jsonify({'error': 'Invalid file path'}), 400
            
            if not full_path.exists():
                return jsonify({'error': 'File not found'}), 404
        
        # Extract domain from ACTUAL file path for RBAC check
        # If file was in incoming but found in sorted, use sorted path
        if is_incoming and str(full_path).find(str(sorted_dir)) != -1:
            # File was found in sorted directory via glob
            rel_path = os.path.relpath(str(full_path), str(sorted_dir))
            path_parts = rel_path.split(os.sep)
        else:
            # Normalize path separators (handle both / and \ regardless of OS)
            normalized_path = filepath.replace('/', os.sep).replace('\\', os.sep)
            path_parts = normalized_path.split(os.sep)
        
        domain = path_parts[0] if len(path_parts) > 0 else 'Unknown'
        category = path_parts[1] if len(path_parts) > 1 else 'Other'
        
        # Also check if domain contains incoming/Processing (case where split failed/different separator)
        is_processing = domain in ['incoming', 'Processing'] or 'incoming' in path_parts[0]
        
        # Skip RBAC for 'incoming' or 'Processing' domain (files being processed)
        if is_processing:
            pass  # Allow delete for files being processed
        elif user_role and not can_delete_all:
            from core.permissions import check_file_access
            if not check_file_access(user_role, domain, category):
                return jsonify({'error': 'Access denied: You do not have permission to delete files from this domain'}), 403
        
        # Get current user info
        username = get_jwt_identity()
        user_data = auth_manager.get_user_by_username(username)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        current_user_id = user_data['id']
        
        # Check ownership BEFORE deleting if user has only delete.own permission
        filename = full_path.name
        if can_delete_own and not can_delete_all:
            conn_check = sqlite3.connect(DATA_DIR / 'users.db')
            cursor_check = conn_check.cursor()
            cursor_check.execute("SELECT user_id FROM user_uploads WHERE filename = ?", (filename,))
            row = cursor_check.fetchone()
            conn_check.close()
            
            if not row:
                return jsonify({'error': 'File not found in upload records'}), 404
            
            file_owner_id = row[0]
            if file_owner_id != current_user_id:
                return jsonify({'error': 'Permission denied: You can only delete your own files'}), 403
        
        # NOW delete file (after ownership check passed)
        full_path.unlink()
        
        # Delete from ChromaDB only if file was in sorted directory (indexed)
        if is_incoming:
            deleted_chunks = 0  # Files in incoming aren't indexed yet
        else:
            deleted_chunks = db_manager.delete_by_filepath(str(full_path))
        
        # Remove from user_uploads tracking table
        conn = sqlite3.connect(DATA_DIR / 'users.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_uploads WHERE filename = ?", (filename,))
        conn.commit()
        
        # Get updated count for non-admin users
        if user_role != 'Admin':
            cursor.execute("SELECT COUNT(*) FROM user_uploads WHERE user_id = ?", (current_user_id,))
            new_count = cursor.fetchone()[0]
            quota_str = f'{new_count}/10'
        else:
            quota_str = 'Unlimited'
        conn.close()
        
        logger.info(f"File deleted: {filepath} by {username} ({deleted_chunks} chunks removed from DB)")
        
        response = {
            'status': 'success',
            'message': f'File deleted successfully',
            'chunks_removed': deleted_chunks
        }
        if quota_str:
            response['quota'] = quota_str
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/quota', methods=['GET'])
@jwt_required()
def get_upload_quota():
    """Get user's upload quota"""
    try:
        username = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role', None)
        
        # Admin has unlimited uploads
        if user_role == 'Admin':
            return jsonify({
                'used': None,
                'limit': None,
                'remaining': 'unlimited',
                'quota_string': 'Unlimited'
            })
        
        # Get user ID
        user_data = auth_manager.get_user_by_username(username)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        user_id = user_data['id']
        
        # Count user's current uploads
        conn = sqlite3.connect(DATA_DIR / 'users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user_uploads WHERE user_id = ?", (user_id,))
        used_count = cursor.fetchone()[0]
        conn.close()
        
        MAX_FILES = 10
        remaining = MAX_FILES - used_count
        
        return jsonify({
            'used': used_count,
            'limit': MAX_FILES,
            'remaining': remaining,
            'quota_string': f'{used_count}/{MAX_FILES}'
        })
        
    except Exception as e:
        logger.error(f"Error getting quota: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("🚀 Starting DocuMind AI...")
    logger.info(f"📁 Database: {DB_DIR}")
    logger.info(f"📚 Documents: {db_manager.get_count()}")
    
    app.run(
        debug=False,  # Disable debug for stability
        host='0.0.0.0', 
        port=5000,
        threaded=True
    )
    # Trigger reload
