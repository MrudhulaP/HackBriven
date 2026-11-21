import uuid
from decimal import Decimal
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session

from app.models.user import User, Shop
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionAudit
from app.core.security import hash_password
from app.services.ledger_service import LedgerService

def seed_demo_data(db: Session, reset: bool = False):
    """Seed realistic Indian Kirana demo shop with customers and transactions."""
    # Check if demo user already exists
    demo_user = db.query(User).filter(User.mobile == "9876543210").first()

    if reset and demo_user:
        # Delete old transactions, customers, shops for demo user
        shop = db.query(Shop).filter(Shop.owner_id == demo_user.id).first()
        if shop:
            db.query(TransactionAudit).filter(
                TransactionAudit.transaction_id.in_(
                    db.query(Transaction.id).filter(Transaction.shop_id == shop.id)
                )
            ).delete(synchronize_session=False)
            db.query(Transaction).filter(Transaction.shop_id == shop.id).delete(synchronize_session=False)
            db.query(Customer).filter(Customer.shop_id == shop.id).delete(synchronize_session=False)
            db.query(Shop).filter(Shop.id == shop.id).delete(synchronize_session=False)
        db.query(User).filter(User.id == demo_user.id).delete(synchronize_session=False)
        db.commit()
        demo_user = None

    if demo_user:
        return  # Already seeded

    # Create Demo User & Shop
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        name="Rajesh Sharma",
        mobile="9876543210",
        password_hash=hash_password("demo1234"),
        preferred_language="hi",
        created_at=datetime.utcnow() - timedelta(days=30)
    )
    db.add(user)
    db.flush()

    shop_id = str(uuid.uuid4())
    shop = Shop(
        id=shop_id,
        owner_id=user.id,
        shop_name="Sharma Kirana & General Store",
        currency="INR",
        created_at=datetime.utcnow() - timedelta(days=30)
    )
    db.add(shop)
    db.flush()

    # 1. Ramesh - Dedicated for Acceptance Test: Clean ₹0 Opening Balance!
    # "Initial condition: Customer Ramesh. Outstanding: ₹0."
    ramesh = Customer(
        id=str(uuid.uuid4()),
        shop_id=shop.id,
        name="Ramesh",
        mobile="9876500001",
        address="12, Cross Road, Gandhi Bazaar",
        notes="Regular customer, buys groceries and daily essentials",
        created_at=datetime.utcnow() - timedelta(days=20)
    )
    db.add(ramesh)

    # 2. Suresh - Outstanding ₹850
    suresh = Customer(
        id=str(uuid.uuid4()),
        shop_id=shop.id,
        name="Suresh",
        mobile="9876500002",
        address="45, Main Market Road",
        notes="Buys monthly provisions",
        created_at=datetime.utcnow() - timedelta(days=15)
    )
    db.add(suresh)

    # 3. Priya - Outstanding ₹420
    priya = Customer(
        id=str(uuid.uuid4()),
        shop_id=shop.id,
        name="Priya",
        mobile="9876500003",
        address="8, Temple Street",
        notes="Online UPI and cash mix",
        created_at=datetime.utcnow() - timedelta(days=10)
    )
    db.add(priya)

    # 4. Anjali - Settled (₹0 balance)
    anjali = Customer(
        id=str(uuid.uuid4()),
        shop_id=shop.id,
        name="Anjali",
        mobile="9876500004",
        address="22, 1st Cross, Layout",
        notes="Settles on the same day",
        created_at=datetime.utcnow() - timedelta(days=12)
    )
    db.add(anjali)

    # 5. Kumar - Outstanding ₹1200
    kumar = Customer(
        id=str(uuid.uuid4()),
        shop_id=shop.id,
        name="Kumar",
        mobile="9876500005",
        address="Shop No. 4, Auto Stand",
        notes="Auto driver, weekly settlement",
        created_at=datetime.utcnow() - timedelta(days=8)
    )
    db.add(kumar)
    db.commit()

    # Seed confirmed transactions for Suresh, Priya, Anjali, Kumar (Ramesh left at ₹0 for testing!)
    today = date.today()

    # Suresh transactions (Net: ₹850)
    LedgerService.create_transaction(db, shop.id, suresh.id, "CREDIT", Decimal("1200.00"), today - timedelta(days=5), "Monthly Atta, Oil & Spices", "MANUAL", user_id=user.id)
    LedgerService.create_transaction(db, shop.id, suresh.id, "PAYMENT", Decimal("350.00"), today - timedelta(days=2), "Cash payment received", "MANUAL", user_id=user.id)

    # Priya transactions (Net: ₹420)
    LedgerService.create_transaction(db, shop.id, priya.id, "CREDIT", Decimal("720.00"), today - timedelta(days=4), "Rice bag and pulses", "MANUAL", user_id=user.id)
    LedgerService.create_transaction(db, shop.id, priya.id, "PAYMENT", Decimal("300.00"), today - timedelta(days=1), "GPay payment", "MANUAL", user_id=user.id)

    # Anjali transactions (Net: ₹0)
    LedgerService.create_transaction(db, shop.id, anjali.id, "CREDIT", Decimal("500.00"), today - timedelta(days=6), "Biscuits and dairy", "MANUAL", user_id=user.id)
    LedgerService.create_transaction(db, shop.id, anjali.id, "PAYMENT", Decimal("500.00"), today - timedelta(days=3), "Full settlement", "MANUAL", user_id=user.id)

    # Kumar transactions (Net: ₹1200)
    LedgerService.create_transaction(db, shop.id, kumar.id, "CREDIT", Decimal("1500.00"), today - timedelta(days=7), "Dry fruits and snacks", "MANUAL", user_id=user.id)
    LedgerService.create_transaction(db, shop.id, kumar.id, "PAYMENT", Decimal("300.00"), today, "Part payment morning", "VOICE", user_id=user.id)

    db.commit()
