from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class TransactionCreate(BaseModel):
    customer_id: str
    type: str = Field(..., pattern="^(CREDIT|PAYMENT)$")
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="INR")
    transaction_date: Optional[date] = None
    description: Optional[str] = None
    input_method: str = Field(default="MANUAL", pattern="^(VOICE|MANUAL|OFFLINE_SYNC)$")
    idempotency_key: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    shop_id: str
    customer_id: str
    customer_name: Optional[str] = None
    type: str
    amount: Decimal
    currency: str
    transaction_date: date
    created_at: datetime
    description: Optional[str] = None
    input_method: str
    status: str
    idempotency_key: Optional[str] = None
    reversal_of_transaction_id: Optional[str] = None

    class Config:
        from_attributes = True

class TransactionCorrectRequest(BaseModel):
    corrected_amount: Decimal = Field(..., gt=0)
    reason: Optional[str] = "Shopkeeper correction"

class TransactionReverseRequest(BaseModel):
    reason: Optional[str] = "Shopkeeper reversal request"

class CustomerLedgerResponse(BaseModel):
    customer_id: str
    customer_name: str
    outstanding_balance: Decimal
    total_credit: Decimal
    total_payment: Decimal
    transactions: List[TransactionResponse]
