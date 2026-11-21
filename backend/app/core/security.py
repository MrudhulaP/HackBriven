import hashlib
import hmac
import os
import json
import base64
import time
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from app.core.config import settings

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a unique salt."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    return f"{salt.hex()}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored salt$hash."""
    try:
        salt_hex, key_hex = hashed_password.split('$')
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100_000)
        return hmac.compare_digest(key, expected_key)
    except Exception:
        return False

def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def _b64decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a tamper-proof signed JWT-compatible token using HMAC-SHA256."""
    if expires_delta:
        expire = time.time() + expires_delta.total_seconds()
    else:
        expire = time.time() + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": str(subject), "exp": int(expire)}
    
    header_b64 = _b64encode(json.dumps(header).encode('utf-8'))
    payload_b64 = _b64encode(json.dumps(payload).encode('utf-8'))
    
    message = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(settings.SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()
    signature_b64 = _b64encode(signature)
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_access_token(token: str) -> Optional[dict]:
    """Verify signature and return token payload if valid and unexpired."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        
        message = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(settings.SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()
        actual_sig = _b64decode(signature_b64)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
            
        payload = json.loads(_b64decode(payload_b64).decode('utf-8'))
        if payload.get("exp") and time.time() > payload["exp"]:
            return None
            
        return payload
    except Exception:
        return None
