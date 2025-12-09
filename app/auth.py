from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

USERS = {
    'alice': 'student',
    'bob': 'teacher',
    'carol': 'management',
    'owner': 'owner'
}

TOKENS = {
    'token-student': 'alice',
    'token-teacher': 'bob',
    'token-management': 'carol',
    'token-owner': 'owner'
}

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    token = creds.credentials
    if token not in TOKENS:
        raise HTTPException(status_code=401, detail='Invalid token')
    username = TOKENS[token]
    role = USERS.get(username)
    return {'username': username, 'role': role}

def require_role(*allowed):
    def _inner(user = Depends(get_current_user)):
        if user['role'] not in allowed:
            raise HTTPException(status_code=403, detail='Forbidden')
        return user
    return _inner
