import pytest
import uuid
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.models.user import User, Shop
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionAudit
from app.services.ledger_service import LedgerService, quantize_inr

# In-memory SQLite for testing
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create test user and shop
    user = User(
        id=str(uuid.uuid4()),
        name="Test Owner",
        mobile="9000000001",
        password_hash="hash",
        preferred_language="hi"
    )
    session.add(user)
    session.flush()

    shop1 = Shop(id=str(uuid.uuid4()), owner_id=user.id, shop_name="Kirana 1", currency="INR")
    shop2 = Shop(id=str(uuid.uuid4()), owner_id=user.id, shop_name="Kirana 2", currency="INR")
    session.add(shop1)
    session.add(shop2)
    session.commit()

    yield session
    session.close()

def test_credit_increases_and_payment_decreases_balance(db_session):
    shop = db_session.query(Shop).first()
    cust = Customer(id=str(uuid.uuid4()), shop_id=shop.id, name="Test Customer")
    db_session.add(cust)
    db_session.commit()

    # Initial balance is 0
    bal, cred, pay = LedgerService.get_customer_balance(db_session, shop.id, cust.id)
    assert bal == Decimal("0.00")

    # Add credit: 500
    LedgerService.create_transaction(db_session, shop.id, cust.id, "CREDIT", Decimal("500.00"))
    bal, cred, pay = LedgerService.get_customer_balance(db_session, shop.id, cust.id)
    assert cred == Decimal("500.00")
    assert pay == Decimal("0.00")
    assert bal == Decimal("500.00")

    # Add payment: 200
    LedgerService.create_transaction(db_session, shop.id, cust.id, "PAYMENT", Decimal("200.00"))
    bal, cred, pay = LedgerService.get_customer_balance(db_session, shop.id, cust.id)
    assert cred == Decimal("500.00")
    assert pay == Decimal("200.00")
    assert bal == Decimal("300.00")

def test_multiple_credits_and_payments_math(db_session):
    # From PART 10 of prompt:
    # Initial credit ₹500, Additional credit ₹300, Payment ₹200, Payment ₹100
    # Total credit: ₹800, Total payments: ₹300, Outstanding: ₹500
    shop = db_session.query(Shop).first()
    cust = Customer(id=str(uuid.uuid4()), shop_id=shop.id, name="Multi Customer")
    db_session.add(cust)
    db_session.commit()

    LedgerService.create_transaction(db_session, shop.id, cust.id, "CREDIT", Decimal("500.00"))
    LedgerService.create_transaction(db_session, shop.id, cust.id, "CREDIT", Decimal("300.00"))
    LedgerService.create_transaction(db_session, shop.id, cust.id, "PAYMENT", Decimal("200.00"))
    LedgerService.create_transaction(db_session, shop.id, cust.id, "PAYMENT", Decimal("100.00"))

    bal, cred, pay = LedgerService.get_customer_balance(db_session, shop.id, cust.id)
    assert cred == Decimal("800.00")
    assert pay == Decimal("300.00")
    assert bal == Decimal("500.00")

def test_advance_negative_balance(db_session):
    shop = db_session.query(Shop).first()
    cust = Customer(id=str(uuid.uuid4()), shop_id=shop.id, name="Advance Customer")
    db_session.add(cust)
    db_session.commit()

    LedgerService.create_transaction(db_session, shop.id, cust.id, "CREDIT", Decimal("200.00"))
    LedgerService.create_transaction(db_session, shop.id, cust.id, "PAYMENT", Decimal("250.00"))

    bal, cred, pay = LedgerService.get_customer_balance(db_session, shop.id, cust.id)
    assert bal == Decimal("-50.00")

def test_idempotency_prevents_duplicate_transactions(db_session):
    shop = db_session.query(Shop).first()
    cust = Customer(id=str(uuid.uuid4()), shop_id=shop.id, name="Idem Customer")
    db_session.add(cust)
    db_session.commit()

    key = "sync_unique_key_123"
    tx1 = LedgerService.create_transaction(db_session, shop.id, cust.id, "CREDIT", Decimal("100.00"), idempotency_key=key)
    tx2 = LedgerService.create_transaction(db_session, shop.id, cust.id, "CREDIT", Decimal("100.00"), idempotency_key=key)

    assert tx1.id == tx2.id
    bal, _, _ = LedgerService.get_customer_balance(db_session, shop.id, cust.id)
    assert bal == Decimal("100.00")  # Not 200.00

def test_reversal_creates_audit_and_recalculates_balance(db_session):
    shop = db_session.query(Shop).first()
    cust = Customer(id=str(uuid.uuid4()), shop_id=shop.id, name="Rev Customer")
    db_session.add(cust)
    db_session.commit()

    tx = LedgerService.create_transaction(db_session, shop.id, cust.id, "CREDIT", Decimal("400.00"))
    bal, _, _ = LedgerService.get_customer_balance(db_session, shop.id, cust.id)
    assert bal == Decimal("400.00")

    orig, rev = LedgerService.reverse_transaction(db_session, shop.id, tx.id, reason="Customer canceled item")
    assert orig.status == "REVERSED"
    assert rev.reversal_of_transaction_id == orig.id

    # Balance reverts to 0
    bal, _, _ = LedgerService.get_customer_balance(db_session, shop.id, cust.id)
    assert bal == Decimal("0.00")

    # Audit record check
    audit = db_session.query(TransactionAudit).filter(TransactionAudit.transaction_id == tx.id).order_by(TransactionAudit.created_at.desc()).first()
    assert audit.action == "REVERSE"

def test_correction_preserves_audit_trail(db_session):
    shop = db_session.query(Shop).first()
    cust = Customer(id=str(uuid.uuid4()), shop_id=shop.id, name="Correct Customer")
    db_session.add(cust)
    db_session.commit()

    # User originally entered 340
    tx = LedgerService.create_transaction(db_session, shop.id, cust.id, "CREDIT", Decimal("340.00"))
    bal, _, _ = LedgerService.get_customer_balance(db_session, shop.id, cust.id)
    assert bal == Decimal("340.00")

    # "Actually it was 400, not 340"
    corrected = LedgerService.correct_transaction(db_session, shop.id, tx.id, Decimal("400.00"), reason="Shopkeeper typo correction")
    assert corrected.amount == Decimal("400.00")

    bal, _, _ = LedgerService.get_customer_balance(db_session, shop.id, cust.id)
    assert bal == Decimal("400.00")

    audit = db_session.query(TransactionAudit).filter(
        TransactionAudit.transaction_id == tx.id,
        TransactionAudit.action == "CORRECT"
    ).first()
    assert audit is not None
    assert "340.00" in audit.old_values
    assert "400.00" in audit.new_values

def test_shop_data_isolation(db_session):
    shops = db_session.query(Shop).all()
    shop1, shop2 = shops[0], shops[1]

    cust1 = Customer(id=str(uuid.uuid4()), shop_id=shop1.id, name="Customer Shop 1")
    cust2 = Customer(id=str(uuid.uuid4()), shop_id=shop2.id, name="Customer Shop 2")
    db_session.add(cust1)
    db_session.add(cust2)
    db_session.commit()

    LedgerService.create_transaction(db_session, shop1.id, cust1.id, "CREDIT", Decimal("500.00"))
    LedgerService.create_transaction(db_session, shop2.id, cust2.id, "CREDIT", Decimal("900.00"))

    bal1, _, _ = LedgerService.get_customer_balance(db_session, shop1.id, cust1.id)
    bal2, _, _ = LedgerService.get_customer_balance(db_session, shop2.id, cust2.id)

    assert bal1 == Decimal("500.00")
    assert bal2 == Decimal("900.00")

    # Shop 2 cannot access Shop 1's customer balance
    bal_isolated, _, _ = LedgerService.get_customer_balance(db_session, shop2.id, cust1.id)
    assert bal_isolated == Decimal("0.00")
