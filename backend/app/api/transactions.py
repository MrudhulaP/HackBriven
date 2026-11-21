from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.session import get_db
from app.models.user import Shop, User
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionAudit
from app.schemas.transaction import (
    TransactionCreate, TransactionResponse, TransactionCorrectRequest, TransactionReverseRequest
)
from app.services.ledger_service import LedgerService
from app.api.deps import get_current_shop, get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    shop: Shop = Depends(get_current_shop),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = LedgerService.create_transaction(
        db=db,
        shop_id=shop.id,
        customer_id=data.customer_id,
        type=data.type,
        amount=data.amount,
        transaction_date=data.transaction_date,
        description=data.description,
        input_method=data.input_method,
        idempotency_key=data.idempotency_key,
        user_id=user.id
    )
    cust = db.query(Customer).filter(Customer.id == tx.customer_id).first()
    return TransactionResponse(
        id=tx.id,
        shop_id=tx.shop_id,
        customer_id=tx.customer_id,
        customer_name=cust.name if cust else "Unknown",
        type=tx.type,
        amount=tx.amount,
        currency=tx.currency,
        transaction_date=tx.transaction_date,
        created_at=tx.created_at,
        description=tx.description,
        input_method=tx.input_method,
        status=tx.status,
        idempotency_key=tx.idempotency_key,
        reversal_of_transaction_id=tx.reversal_of_transaction_id
    )

@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    customer_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None, description="CREDIT or PAYMENT"),
    status: Optional[str] = Query(None, description="CONFIRMED, PENDING, REVERSED"),
    period: Optional[str] = Query(None, description="today, yesterday, 7days, 30days"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    sort: Optional[str] = Query("newest", description="newest, oldest, amount_desc, amount_asc"),
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction, Customer.name.label("customer_name")).join(
        Customer, Transaction.customer_id == Customer.id
    ).filter(Transaction.shop_id == shop.id)

    if customer_id:
        query = query.filter(Transaction.customer_id == customer_id)
    if type:
        query = query.filter(Transaction.type == type)
    if status:
        query = query.filter(Transaction.status == status)

    today = date.today()
    if period == "today":
        query = query.filter(Transaction.transaction_date == today)
    elif period == "yesterday":
        query = query.filter(Transaction.transaction_date == today - timedelta(days=1))
    elif period == "7days":
        query = query.filter(Transaction.transaction_date >= today - timedelta(days=7))
    elif period == "30days":
        query = query.filter(Transaction.transaction_date >= today - timedelta(days=30))
    elif start_date and end_date:
        query = query.filter(Transaction.transaction_date >= start_date, Transaction.transaction_date <= end_date)

    if sort == "oldest":
        query = query.order_by(Transaction.transaction_date.asc(), Transaction.created_at.asc())
    elif sort == "amount_desc":
        query = query.order_by(Transaction.amount.desc())
    elif sort == "amount_asc":
        query = query.order_by(Transaction.amount.asc())
    else:  # newest
        query = query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())

    records = query.offset(offset).limit(limit).all()

    return [
        TransactionResponse(
            id=tx.id,
            shop_id=tx.shop_id,
            customer_id=tx.customer_id,
            customer_name=c_name,
            type=tx.type,
            amount=tx.amount,
            currency=tx.currency,
            transaction_date=tx.transaction_date,
            created_at=tx.created_at,
            description=tx.description,
            input_method=tx.input_method,
            status=tx.status,
            idempotency_key=tx.idempotency_key,
            reversal_of_transaction_id=tx.reversal_of_transaction_id
        ) for tx, c_name in records
    ]

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    tx = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.shop_id == shop.id
    ).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    cust = db.query(Customer).filter(Customer.id == tx.customer_id).first()
    return TransactionResponse(
        id=tx.id,
        shop_id=tx.shop_id,
        customer_id=tx.customer_id,
        customer_name=cust.name if cust else "Unknown",
        type=tx.type,
        amount=tx.amount,
        currency=tx.currency,
        transaction_date=tx.transaction_date,
        created_at=tx.created_at,
        description=tx.description,
        input_method=tx.input_method,
        status=tx.status,
        idempotency_key=tx.idempotency_key,
        reversal_of_transaction_id=tx.reversal_of_transaction_id
    )

@router.post("/{transaction_id}/correct", response_model=TransactionResponse)
def correct_transaction(
    transaction_id: str,
    data: TransactionCorrectRequest,
    shop: Shop = Depends(get_current_shop),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = LedgerService.correct_transaction(
        db=db,
        shop_id=shop.id,
        transaction_id=transaction_id,
        corrected_amount=data.corrected_amount,
        reason=data.reason,
        user_id=user.id
    )
    cust = db.query(Customer).filter(Customer.id == tx.customer_id).first()
    return TransactionResponse(
        id=tx.id,
        shop_id=tx.shop_id,
        customer_id=tx.customer_id,
        customer_name=cust.name if cust else "Unknown",
        type=tx.type,
        amount=tx.amount,
        currency=tx.currency,
        transaction_date=tx.transaction_date,
        created_at=tx.created_at,
        description=tx.description,
        input_method=tx.input_method,
        status=tx.status,
        idempotency_key=tx.idempotency_key,
        reversal_of_transaction_id=tx.reversal_of_transaction_id
    )

@router.post("/{transaction_id}/reverse")
def reverse_transaction(
    transaction_id: str,
    data: TransactionReverseRequest,
    shop: Shop = Depends(get_current_shop),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx, reversal_tx = LedgerService.reverse_transaction(
        db=db,
        shop_id=shop.id,
        transaction_id=transaction_id,
        reason=data.reason,
        user_id=user.id
    )
    return {
        "message": "Transaction reversed successfully",
        "original_transaction_id": tx.id,
        "reversal_transaction_id": reversal_tx.id,
        "status": tx.status
    }
