import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User, Shop
from app.schemas.auth import UserRegister, UserLogin, UserResponse, ShopResponse, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.mobile == data.mobile).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A shopkeeper account with this mobile number already exists"
        )

    user = User(
        id=str(uuid.uuid4()),
        name=data.name.strip(),
        mobile=data.mobile.strip(),
        password_hash=hash_password(data.password),
        preferred_language=data.preferred_language or "hi",
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.flush()

    shop = Shop(
        id=str(uuid.uuid4()),
        owner_id=user.id,
        shop_name=data.shop_name.strip(),
        currency=data.currency or "INR",
        created_at=datetime.utcnow()
    )
    db.add(shop)
    db.commit()
    db.refresh(user)
    db.refresh(shop)

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            mobile=user.mobile,
            preferred_language=user.preferred_language,
            created_at=user.created_at,
            shop=ShopResponse(
                id=shop.id,
                shop_name=shop.shop_name,
                currency=shop.currency,
                created_at=shop.created_at
            )
        )
    )

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile == data.mobile.strip()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile number or password"
        )

    shop = db.query(Shop).filter(Shop.owner_id == user.id).first()
    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            mobile=user.mobile,
            preferred_language=user.preferred_language,
            created_at=user.created_at,
            shop=ShopResponse(
                id=shop.id,
                shop_name=shop.shop_name,
                currency=shop.currency,
                created_at=shop.created_at
            ) if shop else None
        )
    )

@router.post("/demo", response_model=TokenResponse)
def demo_login(db: Session = Depends(get_db)):
    """One-click demo account entry for evaluation without typing credentials."""
    demo_user = db.query(User).filter(User.mobile == "9876543210").first()
    if not demo_user:
        # Create demo shopkeeper on demand if not yet seeded
        demo_user = User(
            id=str(uuid.uuid4()),
            name="Rajesh Sharma",
            mobile="9876543210",
            password_hash=hash_password("demo1234"),
            preferred_language="hi",
            created_at=datetime.utcnow()
        )
        db.add(demo_user)
        db.flush()

        demo_shop = Shop(
            id=str(uuid.uuid4()),
            owner_id=demo_user.id,
            shop_name="Sharma Kirana & General Store",
            currency="INR",
            created_at=datetime.utcnow()
        )
        db.add(demo_shop)
        db.commit()
        db.refresh(demo_user)
        db.refresh(demo_shop)
    else:
        demo_shop = db.query(Shop).filter(Shop.owner_id == demo_user.id).first()

    token = create_access_token(demo_user.id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=demo_user.id,
            name=demo_user.name,
            mobile=demo_user.mobile,
            preferred_language=demo_user.preferred_language,
            created_at=demo_user.created_at,
            shop=ShopResponse(
                id=demo_shop.id,
                shop_name=demo_shop.shop_name,
                currency=demo_shop.currency,
                created_at=demo_shop.created_at
            ) if demo_shop else None
        )
    )

@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    shop = db.query(Shop).filter(Shop.owner_id == user.id).first()
    return UserResponse(
        id=user.id,
        name=user.name,
        mobile=user.mobile,
        preferred_language=user.preferred_language,
        created_at=user.created_at,
        shop=ShopResponse(
            id=shop.id,
            shop_name=shop.shop_name,
            currency=shop.currency,
            created_at=shop.created_at
        ) if shop else None
    )

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
