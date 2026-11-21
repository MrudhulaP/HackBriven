import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Date, Numeric, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.database.session import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    shop_id = Column(String(36), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 'CREDIT' (udhaar - goods given on credit, increases balance) or 'PAYMENT' (jama - cash/online paid by customer, decreases balance)
    type = Column(String(20), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    
    # Date of transaction (can be past date e.g. "kal 200 diya tha")
    transaction_date = Column(Date, default=date.today, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    description = Column(String(255), nullable=True)
    input_method = Column(String(20), default="VOICE", nullable=False)  # 'VOICE', 'MANUAL', 'OFFLINE_SYNC'
    status = Column(String(20), default="CONFIRMED", nullable=False, index=True)  # 'CONFIRMED', 'PENDING', 'REVERSED'
    
    idempotency_key = Column(String(100), nullable=True, index=True)
    reversal_of_transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)

    shop = relationship("Shop", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")
    audit_logs = relationship("TransactionAudit", back_populates="transaction", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_shop_idempotency", "shop_id", "idempotency_key", unique=False),
        Index("ix_shop_customer_date", "shop_id", "customer_id", "transaction_date"),
    )


class TransactionAudit(Base):
    __tablename__ = "transaction_audit"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(30), nullable=False)  # 'CREATE', 'CORRECT', 'REVERSE'
    old_values = Column(Text, nullable=True)    # JSON string
    new_values = Column(Text, nullable=True)    # JSON string
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(String(36), nullable=True)

    transaction = relationship("Transaction", back_populates="audit_logs")


class PendingSync(Base):
    __tablename__ = "pending_sync"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    shop_id = Column(String(36), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    operation_id = Column(String(64), unique=True, nullable=False, index=True)
    operation_type = Column(String(50), nullable=False)  # 'CREATE_TRANSACTION', 'CREATE_CUSTOMER'
    payload = Column(Text, nullable=False)               # JSON string
    sync_status = Column(String(30), default="PENDING_SYNC", nullable=False)  # 'SAVED_LOCALLY', 'PENDING_SYNC', 'SYNCED', 'FAILED'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
