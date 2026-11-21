from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    mobile: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    archived_at: Optional[datetime] = None

class CustomerResponse(CustomerBase):
    id: str
    shop_id: str
    created_at: datetime
    archived_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CustomerWithBalanceResponse(CustomerResponse):
    outstanding_balance: Decimal
    total_credit: Decimal
    total_payment: Decimal
    transaction_count: int
    last_transaction_date: Optional[str] = None

    class Config:
        from_attributes = True
