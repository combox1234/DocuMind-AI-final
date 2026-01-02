# Multi-User Implementation Guide for DocuMind AI

## Current State: Single-User System
Your app currently has:
- ❌ No user authentication
- ❌ Shared chat history (anyone can see all chats)
- ❌ Shared document database (no user isolation)
- ❌ Single Flask thread handling requests

## Goal: Multi-User System
Enable multiple users to:
- ✅ Register and login with credentials
- ✅ Have isolated chat histories
- ✅ Optionally share documents or keep them private
- ✅ Use the app simultaneously without conflicts

---

## Implementation Phases

### Phase 1: Add User Authentication (Foundation)

#### 1.1 Database Schema
Create a new `users.db` (SQLite) with tables:

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Update chats to link to users
CREATE TABLE chats (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Messages table (replaces JSON files)
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    text TEXT NOT NULL,
    cited_files TEXT,  -- JSON array
    confidence_score REAL,
    source_snippets TEXT,  -- JSON array
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id)
);
```

#### 1.2 Install Dependencies
```bash
pip install flask-login flask-bcrypt flask-sqlalchemy
```

#### 1.3 Create User Model (`models/user.py`)
```python
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def create(username, email, password):
        password_hash = generate_password_hash(password)
        # Insert into database
        return User(id, username, email, password_hash)
```

#### 1.4 Update `app.py` with Flask-Login
```python
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # Load user from database
    return User.get_by_id(user_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Registration logic
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Login logic
    pass

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')
```

#### 1.5 Protect Routes
Add `@login_required` to all API routes:
```python
@app.route('/chat', methods=['POST'])
@login_required
def chat():
    # Now current_user.id is available
    pass
```

---

### Phase 2: User Data Isolation

#### 2.1 Update ChatManager
Modify `core/chat_manager.py` to filter by user:

```python
class ChatManager:
    def get_chats(self, user_id):
        # SELECT * FROM chats WHERE user_id = ?
        pass
    
    def create_chat(self, user_id, title):
        # INSERT INTO chats (user_id, title, ...)
        pass
```

#### 2.2 Update Vector Database Metadata
Add `user_id` to document chunks:

```python
# In worker.py or processor.py
metadata = {
    'filename': filename,
    'filepath': filepath,
    'category': category,
    'user_id': user_id,  # NEW
    'chunk_index': i
}
```

#### 2.3 Filter Queries by User
```python
# In database.py
def query(self, query_text, user_id, n_results=5):
    results = self.collection.query(
        query_texts=[query_text],
        where={"user_id": user_id},  # Filter by user
        n_results=n_results
    )
    return results
```

---

### Phase 3: Concurrent Request Handling

#### 3.1 Replace Flask Dev Server with Gunicorn
```bash
pip install gunicorn
```

**Start command:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
- `-w 4`: 4 worker processes (handles 4 concurrent users)
- Adjust based on CPU cores

#### 3.2 Update `docker-compose.yml`
```yaml
backend:
  command: gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

### Phase 4: Session Management

#### 4.1 Use Redis for Sessions
```python
from flask_session import Session

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
Session(app)
```

This ensures sessions work across multiple Gunicorn workers.

---

## Quick Start: Minimal Multi-User Setup

If you want to start simple without full database migration:

### Option A: JWT-Based Auth (Stateless)
```python
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    # Verify credentials
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    current_user = get_jwt_identity()
    # Use current_user to filter data
```

### Option B: Simple Session-Based (No DB)
```python
from flask import session

app.secret_key = 'your-secret-key'

@app.route('/login', methods=['POST'])
def login():
    session['user_id'] = username
    return jsonify({'status': 'success'})

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user_id = session['user_id']
```

---

## Testing Multi-User

1. **Open 2 browsers** (Chrome + Firefox or Incognito)
2. Login as different users in each
3. Create chats in both
4. Verify each user only sees their own chats

---

## Performance Considerations

| Users | Recommendation |
|-------|----------------|
| 1-10 | Flask dev server OK |
| 10-50 | Gunicorn with 4 workers |
| 50-100 | Gunicorn + Nginx reverse proxy |
| 100+ | PostgreSQL instead of SQLite, separate ChromaDB server |

---

## Next Steps

1. Choose authentication method (Flask-Login vs JWT)
2. Migrate `ChatManager` from JSON files to SQLite
3. Add `user_id` filtering to vector database
4. Deploy with Gunicorn
5. Test with multiple concurrent users

Would you like me to implement any specific phase?
