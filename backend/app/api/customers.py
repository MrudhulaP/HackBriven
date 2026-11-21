from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import Shop
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerWithBalanceResponse
from app.schemas.transaction import CustomerLedgerResponse, TransactionResponse
from app.services.customer_service import CustomerService
from app.services.ledger_service import LedgerService
from app.api.deps import get_current_shop

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    data: CustomerCreate,
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    return CustomerService.create_customer(db, shop.id, data)

@router.get("", response_model=List[CustomerWithBalanceResponse])
def list_customers(
    search: Optional[str] = Query(None, description="Search by name or mobile"),
    has_balance_only: bool = Query(False, description="Filter only customers with outstanding balance"),
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    return CustomerService.list_customers_with_balance(db, shop.id, search=search, has_balance_only=has_balance_only)

@router.get("/{customer_id}", response_model=CustomerWithBalanceResponse)
def get_customer(
    customer_id: str,
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    cust = CustomerService.get_customer(db, shop.id, customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    outstanding, credit, payment = LedgerService.get_customer_balance(db, shop.id, cust.id)
    tx_count = db.query(Transaction).filter(
        Transaction.shop_id == shop.id,
        Transaction.customer_id == cust.id,
        Transaction.status == "CONFIRMED"
    ).count()

    last_tx = db.query(Transaction.transaction_date).filter(
        Transaction.shop_id == shop.id,
        Transaction.customer_id == cust.id,
        Transaction.status == "CONFIRMED"
    ).order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc()).first()

    return CustomerWithBalanceResponse(
        id=cust.id,
        shop_id=cust.shop_id,
        name=cust.name,
        mobile=cust.mobile,
        address=cust.address,
        notes=cust.notes,
        created_at=cust.created_at,
        archived_at=cust.archived_at,
        outstanding_balance=outstanding,
        total_credit=credit,
        total_payment=payment,
        transaction_count=tx_count,
        last_transaction_date=last_tx[0].isoformat() if last_tx else None
    )

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    return CustomerService.update_customer(db, shop.id, customer_id, data)

@router.delete("/{customer_id}")
def archive_customer(
    customer_id: str,
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    cust = CustomerService.get_customer(db, shop.id, customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    cust.archived_at = datetime.utcnow()
    db.commit()
    return {"message": f"Customer '{cust.name}' archived successfully"}

@router.get("/{customer_id}/ledger", response_model=CustomerLedgerResponse)
def get_customer_ledger(
    customer_id: str,
    shop: Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    cust = CustomerService.get_customer(db, shop.id, customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    outstanding, credit, payment = LedgerService.get_customer_balance(db, shop.id, cust.id)
    txs = db.query(Transaction).filter(
        Transaction.shop_id == shop.id,
        Transaction.customer_id == cust.id
    ).order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc()).all()

    tx_responses = [
        TransactionResponse(
            id=t.id,
            shop_id=t.shop_id,
            customer_id=t.customer_id,
            customer_name=cust.name,
            type=t.type,
            amount=t.amount,
            currency=t.currency,
            transaction_date=t.transaction_date,
            created_at=t.created_at,
            description=t.description,
            input_method=t.input_method,
            status=t.status,
            idempotency_key=t.idempotency_key,
            reversal_of_transaction_id=t.reversal_of_transaction_id
        ) for t in txs
    ]

    return CustomerLedgerResponse(
        customer_id=cust.id,
        customer_name=cust.name,
        outstanding_balance=outstanding,
        total_credit=credit,
        total_payment=payment,
        transactions=tx_responses
    )
