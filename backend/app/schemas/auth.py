from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    shop_name: str = Field(..., min_length=2, max_length=150)
    mobile: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=4)
    preferred_language: str = Field(default="hi")
    currency: str = Field(default="INR")

class UserLogin(BaseModel):
    mobile: str
    password: str

class ShopResponse(BaseModel):
    id: str
    shop_name: str
    currency: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    name: str
    mobile: str
    preferred_language: str
    shop: Optional[ShopResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
