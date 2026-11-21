from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import decode_access_token
from app.models.user import User, Shop

security_bearer = HTTPBearer(auto_error=False)

def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    """Retrieve current authenticated user from JWT token, with automatic demo fallback if needed."""
    if auth and auth.credentials:
        payload = decode_access_token(auth.credentials)
        if payload and "sub" in payload:
            user = db.query(User).filter(User.id == payload["sub"]).first()
            if user:
                return user

    # Check for demo user fallback if no valid token
    demo_user = db.query(User).filter(User.mobile == "9876543210").first()
    if demo_user:
        return demo_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please login or select demo mode."
    )

def get_current_shop(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Shop:
    """Ensure user has an active shop and return it."""
    shop = db.query(Shop).filter(Shop.owner_id == user.id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shop registered for this user account"
        )
    return shop
