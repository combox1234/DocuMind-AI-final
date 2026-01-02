# JWT Implementation Guide for DocuMind AI

This guide details how to secure your Flask application using JSON Web Tokens (JWT).

## 1. Prerequisites
Install `flask-jwt-extended` to handle token generation and verification.
```bash
pip install flask-jwt-extended
```

## 2. Configuration (`config.py`)
Add JWT configuration to your config file or directly in `app.py`.
```python
# Add to config.py or app.py
JWT_SECRET_KEY = 'super-secret-key-change-this-in-production'  # Change this!
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
```

## 3. Implementation Steps (`app.py`)

### A. Initialize JWT
```python
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# ... after app initialization ...
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)
```

### B. Create Login Endpoint
Since you don't have a user database yet, here is a mock implementation.
```python
# Mock user database
USERS = {
    "admin": "password123",
    "user": "userpass"
}

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
        
    if username not in USERS or USERS[username] != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)
```

### C. Protect Routes
Add `@jwt_required()` to endpoints you want to secure, like `/chat` or `/classify`.

```python
@app.route('/chat', methods=['POST'])
@jwt_required()  # <--- Add this decorator
def chat():
    current_user = get_jwt_identity() # Optional: get who is calling
    # ... rest of the function ...
```

### D. Frontend Update
Your `index.html` (JS) will need to:
1.  **Call `/login`** first to get the `access_token`.
2.  **Store the token** (e.g., in `localStorage`).
3.  **Include the token** in the `Authorization` header for subsequent requests.

```javascript
// Example headers for fetch
headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
}
```

## 4. Testing
Use Postman or Curl:
1.  **Login**: `POST /login` with `{"username": "admin", "password": "password123"}` -> Get Token.
2.  **Access**: `POST /chat` with Header `Authorization: Bearer <TOKEN>`.
