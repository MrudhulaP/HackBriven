from decimal import Decimal
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import Shop, User
from app.models.customer import Customer
from app.services.receipt_service import ReceiptService
from app.services.ledger_service import LedgerService
from app.api.deps import get_current_shop, get_current_user

router = APIRouter(prefix="/receipt", tags=["Receipt & Bill Scanning"])

class ReceiptConfirmRequest(BaseModel):
    vendor_or_customer_name: str
    amount: Decimal
    type: str = "CREDIT"  # CREDIT or PAYMENT
    transaction_date: Optional[date] = None
    description: Optional[str] = "Paper bill scan"

@router.post("/scan")
async def scan_receipt(
    file: UploadFile = File(...),
    shop: Shop = Depends(get_current_shop)
):
    """
    Voice-Activated & Camera Receipt Scanning Endpoint:
    Accepts photo of a bill or invoice, extracts vendor, amount, date, and line items.
    """
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty receipt image file provided")

    result = ReceiptService.scan_receipt_image(image_bytes, filename=file.filename)
    return result

@router.post("/confirm")
def confirm_receipt_transaction(
    data: ReceiptConfirmRequest,
    shop: Shop = Depends(get_current_shop),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Commits verified receipt data into the shopkeeper's ledger atomically.
    """
    name = data.vendor_or_customer_name.strip()
    # Find existing customer or vendor, or create new one
    customer = db.query(Customer).filter(
        Customer.shop_id == shop.id,
        Customer.name.ilike(f"%{name}%")
    ).first()

    if not customer:
        customer = Customer(
            shop_id=shop.id,
            name=name,
            notes="Auto-created from receipt scan",
            created_at=date.today()
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    tx = LedgerService.create_transaction(
        db=db,
        shop_id=shop.id,
        customer_id=customer.id,
        type=data.type,
        amount=data.amount,
        transaction_date=data.transaction_date or date.today(),
        description=data.description or f"Bill scan for {name}",
        input_method="SCAN_BILL",
        user_id=user.id
    )

    new_balance, _, _ = LedgerService.get_customer_balance(db, shop.id, customer.id)

    return {
        "success": True,
        "transaction_id": tx.id,
        "customer_id": customer.id,
        "customer_name": customer.name,
        "amount": float(tx.amount),
        "type": tx.type,
        "new_balance": float(new_balance),
        "message": f"Successfully recorded ₹{tx.amount} {tx.type.lower()} from bill scan."
    }
