import json
import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from fastapi import HTTPException, status

from app.models.transaction import Transaction, TransactionAudit
from app.models.customer import Customer
from app.schemas.transaction import TransactionCreate

def quantize_inr(value: Decimal) -> Decimal:
    """Format and round to 2 decimal places using standard financial rounding."""
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class LedgerService:
    @staticmethod
    def get_customer_balance(db: Session, shop_id: str, customer_id: str) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calculate customer's exact balance using confirmed transactions:
        Total Credit = sum of all confirmed 'CREDIT' transactions
        Total Payment = sum of all confirmed 'PAYMENT' transactions
        Outstanding = Total Credit - Total Payment
        
        Returns: (outstanding_balance, total_credit, total_payment)
        """
        # Sum credits
        credit_sum = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.shop_id == shop_id,
            Transaction.customer_id == customer_id,
            Transaction.type == "CREDIT",
            Transaction.status == "CONFIRMED"
        ).scalar()

        # Sum payments
        payment_sum = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.shop_id == shop_id,
            Transaction.customer_id == customer_id,
            Transaction.type == "PAYMENT",
            Transaction.status == "CONFIRMED"
        ).scalar()

        total_credit = quantize_inr(Decimal(str(credit_sum)))
        total_payment = quantize_inr(Decimal(str(payment_sum)))
        outstanding = quantize_inr(total_credit - total_payment)

        return (outstanding, total_credit, total_payment)

    @staticmethod
    def create_transaction(
        db: Session,
        shop_id: str,
        customer_id: str,
        type: str,
        amount: Decimal,
        transaction_date: Optional[date] = None,
        description: Optional[str] = None,
        input_method: str = "MANUAL",
        idempotency_key: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Transaction:
        """Create a new financial transaction atomically with idempotency protection."""
        if type not in ("CREDIT", "PAYMENT"):
            raise HTTPException(status_code=400, detail="Transaction type must be 'CREDIT' or 'PAYMENT'")

        amount_dec = quantize_inr(amount)
        if amount_dec <= Decimal("0"):
            raise HTTPException(status_code=400, detail="Transaction amount must be greater than zero")

        # Verify customer belongs to shop
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.shop_id == shop_id
        ).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found in this shop")

        # Check idempotency
        if idempotency_key:
            existing = db.query(Transaction).filter(
                Transaction.shop_id == shop_id,
                Transaction.idempotency_key == idempotency_key
            ).first()
            if existing:
                return existing

        tx = Transaction(
            id=str(uuid.uuid4()),
            shop_id=shop_id,
            customer_id=customer_id,
            type=type,
            amount=amount_dec,
            currency="INR",
            transaction_date=transaction_date or date.today(),
            created_at=datetime.utcnow(),
            description=description,
            input_method=input_method,
            status="CONFIRMED",
            idempotency_key=idempotency_key
        )
        db.add(tx)
        db.flush()

        # Audit record
        audit = TransactionAudit(
            id=str(uuid.uuid4()),
            transaction_id=tx.id,
            action="CREATE",
            new_values=json.dumps({
                "type": tx.type,
                "amount": str(tx.amount),
                "date": tx.transaction_date.isoformat(),
                "customer_id": tx.customer_id
            }),
            reason=description or "Initial ledger entry",
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def reverse_transaction(
        db: Session,
        shop_id: str,
        transaction_id: str,
        reason: Optional[str] = "Shopkeeper reversal request",
        user_id: Optional[str] = None
    ) -> Tuple[Transaction, Transaction]:
        """
        Reverse a confirmed transaction without silent deletion:
        1. Mark original transaction status as 'REVERSED'.
        2. Create an offsetting transaction linked via `reversal_of_transaction_id`.
        3. Record full audit trail.
        """
        tx = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.shop_id == shop_id
        ).first()

        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if tx.status != "CONFIRMED":
            raise HTTPException(status_code=400, detail=f"Cannot reverse transaction with status '{tx.status}'")

        # The compensating opposite type:
        # If original was CREDIT, reversing it means we need a compensating PAYMENT or mark original as REVERSED
        # In a strict double-entry ledger, marking status as REVERSED stops it from counting toward confirmed balances,
        # and creating an explicit reversal log guarantees auditability.
        old_values = {
            "id": tx.id,
            "status": tx.status,
            "type": tx.type,
            "amount": str(tx.amount),
            "date": tx.transaction_date.isoformat()
        }

        tx.status = "REVERSED"

        # Create reversal compensating record
        reversal_type = "PAYMENT" if tx.type == "CREDIT" else "CREDIT"
        reversal_tx = Transaction(
            id=str(uuid.uuid4()),
            shop_id=shop_id,
            customer_id=tx.customer_id,
            type=reversal_type,
            amount=tx.amount,
            currency=tx.currency,
            transaction_date=date.today(),
            created_at=datetime.utcnow(),
            description=f"Reversal of transaction {tx.id[:8]}: {reason}",
            input_method="MANUAL",
            status="REVERSED",  # Marked so ledger sum doesn't double-cancel if original is already excluded
            reversal_of_transaction_id=tx.id
        )
        db.add(reversal_tx)
        db.flush()

        audit = TransactionAudit(
            id=str(uuid.uuid4()),
            transaction_id=tx.id,
            action="REVERSE",
            old_values=json.dumps(old_values),
            new_values=json.dumps({"status": "REVERSED", "reversal_tx_id": reversal_tx.id}),
            reason=reason,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        db.refresh(tx)
        db.refresh(reversal_tx)

        return (tx, reversal_tx)

    @staticmethod
    def correct_transaction(
        db: Session,
        shop_id: str,
        transaction_id: str,
        corrected_amount: Decimal,
        reason: Optional[str] = "Shopkeeper correction",
        user_id: Optional[str] = None
    ) -> Transaction:
        """
        Correct a transaction amount while retaining full audit history:
        1. Store previous amount in audit log.
        2. Update transaction amount to corrected amount.
        """
        tx = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.shop_id == shop_id
        ).first()

        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if tx.status != "CONFIRMED":
            raise HTTPException(status_code=400, detail="Can only correct confirmed transactions")

        new_amount_dec = quantize_inr(corrected_amount)
        if new_amount_dec <= Decimal("0"):
            raise HTTPException(status_code=400, detail="Corrected amount must be greater than zero")

        old_amount_str = str(tx.amount)
        tx.amount = new_amount_dec

        audit = TransactionAudit(
            id=str(uuid.uuid4()),
            transaction_id=tx.id,
            action="CORRECT",
            old_values=json.dumps({"amount": old_amount_str}),
            new_values=json.dumps({"amount": str(new_amount_dec)}),
            reason=reason,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        db.refresh(tx)
        return tx
