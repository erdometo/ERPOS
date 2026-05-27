import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from contextvars import ContextVar
import bcrypt
from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "erp-secret-key-super-secure-vibe-coder-123!"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

security_bearer = HTTPBearer(auto_error=False)

# Request-scoped context variables to store active user details
current_user_role: ContextVar[Optional[str]] = ContextVar("current_user_role", default=None)
current_user_email: ContextVar[Optional[str]] = ContextVar("current_user_email", default=None)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_authenticated_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication credentials missing.")
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        role: str = payload.get("role")
        user_id: int = payload.get("user_id")
        
        if email is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload.")
        
        user_info = {"email": email, "role": role, "user_id": user_id}
        
        # Set the context variables for database middleware to inspect
        current_user_role.set(role)
        current_user_email.set(email)
        
        return user_info
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
