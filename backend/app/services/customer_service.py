import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc
from fastapi import HTTPException

from app.models.customer import Customer
from app.models.transaction import Transaction
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerWithBalanceResponse
from app.services.ledger_service import LedgerService

class CustomerService:
    @staticmethod
    def create_customer(db: Session, shop_id: str, data: CustomerCreate) -> Customer:
        customer = Customer(
            id=str(uuid.uuid4()),
            shop_id=shop_id,
            name=data.name.strip(),
            mobile=data.mobile.strip() if data.mobile else None,
            address=data.address.strip() if data.address else None,
            notes=data.notes.strip() if data.notes else None,
            created_at=datetime.utcnow()
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def get_customer(db: Session, shop_id: str, customer_id: str) -> Optional[Customer]:
        return db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.shop_id == shop_id,
            Customer.archived_at == None
        ).first()

    @staticmethod
    def search_customers(db: Session, shop_id: str, query: str) -> List[Customer]:
        q = f"%{query.strip().lower()}%"
        return db.query(Customer).filter(
            Customer.shop_id == shop_id,
            Customer.archived_at == None,
            or_(
                func.lower(Customer.name).like(q),
                Customer.mobile.like(q)
            )
        ).all()

    @staticmethod
    def find_by_exact_or_fuzzy_name(db: Session, shop_id: str, name: str) -> List[Customer]:
        cleaned = name.strip().lower()
        # First try exact match
        exact = db.query(Customer).filter(
            Customer.shop_id == shop_id,
            Customer.archived_at == None,
            func.lower(Customer.name) == cleaned
        ).all()
        if exact:
            return exact
        # Then prefix or substring
        return db.query(Customer).filter(
            Customer.shop_id == shop_id,
            Customer.archived_at == None,
            func.lower(Customer.name).like(f"%{cleaned}%")
        ).all()

    @staticmethod
    def list_customers_with_balance(
        db: Session,
        shop_id: str,
        search: Optional[str] = None,
        has_balance_only: bool = False
    ) -> List[dict]:
        query = db.query(Customer).filter(
            Customer.shop_id == shop_id,
            Customer.archived_at == None
        )
        if search:
            s = f"%{search.strip().lower()}%"
            query = query.filter(
                or_(
                    func.lower(Customer.name).like(s),
                    Customer.mobile.like(s)
                )
            )
        customers = query.order_by(Customer.name.asc()).all()

        results = []
        for cust in customers:
            outstanding, credit, payment = LedgerService.get_customer_balance(db, shop_id, cust.id)
            if has_balance_only and outstanding == Decimal("0"):
                continue

            # Count confirmed transactions
            tx_count = db.query(func.count(Transaction.id)).filter(
                Transaction.shop_id == shop_id,
                Transaction.customer_id == cust.id,
                Transaction.status == "CONFIRMED"
            ).scalar() or 0

            # Last transaction date
            last_tx = db.query(Transaction.transaction_date).filter(
                Transaction.shop_id == shop_id,
                Transaction.customer_id == cust.id,
                Transaction.status == "CONFIRMED"
            ).order_by(desc(Transaction.transaction_date), desc(Transaction.created_at)).first()

            results.append({
                "id": cust.id,
                "shop_id": cust.shop_id,
                "name": cust.name,
                "mobile": cust.mobile,
                "address": cust.address,
                "notes": cust.notes,
                "created_at": cust.created_at,
                "archived_at": cust.archived_at,
                "outstanding_balance": outstanding,
                "total_credit": credit,
                "total_payment": payment,
                "transaction_count": tx_count,
                "last_transaction_date": last_tx[0].isoformat() if last_tx else None
            })
        return results

    @staticmethod
    def update_customer(db: Session, shop_id: str, customer_id: str, data: CustomerUpdate) -> Customer:
        cust = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.shop_id == shop_id
        ).first()
        if not cust:
            raise HTTPException(status_code=404, detail="Customer not found")

        if data.name is not None:
            cust.name = data.name.strip()
        if data.mobile is not None:
            cust.mobile = data.mobile.strip() if data.mobile else None
        if data.address is not None:
            cust.address = data.address.strip() if data.address else None
        if data.notes is not None:
            cust.notes = data.notes.strip() if data.notes else None
        if data.archived_at is not None:
            cust.archived_at = data.archived_at

        db.commit()
        db.refresh(cust)
        return cust
