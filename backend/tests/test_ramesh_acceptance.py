import pytest
import uuid
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.models.user import User, Shop
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.ai.transaction_parser import TransactionParser
from app.ai.response_generator import ResponseGenerator
from app.services.ledger_service import LedgerService

@pytest.fixture
def acceptance_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create shopkeeper
    user = User(
        id=str(uuid.uuid4()),
        name="Rajesh Sharma",
        mobile="9876543210",
        password_hash="mockhash",
        preferred_language="hi"
    )
    session.add(user)
    session.flush()

    shop = Shop(
        id=str(uuid.uuid4()),
        owner_id=user.id,
        shop_name="Sharma Kirana",
        currency="INR"
    )
    session.add(shop)
    session.flush()

    # Step 1: Initial Condition - Customer Ramesh, Outstanding ₹0
    ramesh = Customer(
        id=str(uuid.uuid4()),
        shop_id=shop.id,
        name="Ramesh",
        mobile="9876500001"
    )
    session.add(ramesh)
    session.commit()

    yield session, shop, ramesh, user
    session.close()

def test_critical_ramesh_end_to_end_acceptance_scenario(acceptance_db):
    session, shop, ramesh, user = acceptance_db
    today = date.today()
    yesterday = today - timedelta(days=1)

    # 1. Verify Initial Condition: Outstanding is strictly ₹0
    initial_balance, c_sum, p_sum = LedgerService.get_customer_balance(session, shop.id, ramesh.id)
    assert initial_balance == Decimal("0.00")
    assert c_sum == Decimal("0.00")
    assert p_sum == Decimal("0.00")

    # 2. Shopkeeper says: "Ramesh ka 340 udhaar, kal 200 diya tha."
    utterance = "Ramesh ka 340 udhaar, kal 200 diya tha."
    nlu_result = TransactionParser.parse(utterance, db=session, shop_id=shop.id)

    # 3. System MUST recognize TWO separate events:
    assert len(nlu_result.events) == 2, f"Expected 2 events, got {len(nlu_result.events)}"

    event_a = nlu_result.events[0]
    event_b = nlu_result.events[1]

    # Verify Event A:
    # Customer: Ramesh, Type: CREDIT, Amount: ₹340, Date: Today
    assert event_a.customer_name == "Ramesh"
    assert event_a.intent == "ADD_CREDIT"
    assert event_a.amount == Decimal("340")
    assert event_a.transaction_date == today
    assert event_a.date_label == "Today"

    # Verify Event B:
    # Customer: Ramesh, Type: PAYMENT, Amount: ₹200, Date: Yesterday
    assert event_b.customer_name == "Ramesh"
    assert event_b.intent == "RECORD_PAYMENT"
    assert event_b.amount == Decimal("200")
    assert event_b.transaction_date == yesterday
    assert event_b.date_label == "Yesterday"

    # 4. Confirmation Interface:
    # Both events confirmed and saved to actual database
    tx_a = LedgerService.create_transaction(
        db=session,
        shop_id=shop.id,
        customer_id=ramesh.id,
        type="CREDIT",
        amount=event_a.amount,
        transaction_date=event_a.transaction_date,
        description="Ramesh 340 credit today",
        input_method="VOICE",
        user_id=user.id
    )

    tx_b = LedgerService.create_transaction(
        db=session,
        shop_id=shop.id,
        customer_id=ramesh.id,
        type="PAYMENT",
        amount=event_b.amount,
        transaction_date=event_b.transaction_date,
        description="Ramesh 200 payment yesterday",
        input_method="VOICE",
        user_id=user.id
    )

    # Verify two separate records are created in DB with distinct IDs and types
    assert tx_a.id != tx_b.id
    assert tx_a.type == "CREDIT"
    assert tx_b.type == "PAYMENT"
    assert tx_a.amount == Decimal("340.00")
    assert tx_b.amount == Decimal("200.00")
    assert tx_a.transaction_date == today
    assert tx_b.transaction_date == yesterday

    # 5. Calculation Logic:
    # Outstanding = Total Confirmed Credits (340) - Total Confirmed Payments (200) = 140
    new_balance, total_cred, total_pay = LedgerService.get_customer_balance(session, shop.id, ramesh.id)
    assert total_cred == Decimal("340.00")
    assert total_pay == Decimal("200.00")
    assert new_balance == Decimal("140.00")

    # 6. Spoken Response:
    # "Ramesh ka ₹140 baaki hai. ₹340 ka udhaar aur kal ₹200 ka payment record kar diya."
    events_summary = [
        {"type": "CREDIT", "amount": "340.00", "date_label": "Today"},
        {"type": "PAYMENT", "amount": "200.00", "date_label": "Yesterday"}
    ]
    resp = ResponseGenerator.generate_transaction_confirmation_response(
        customer_name="Ramesh",
        new_balance=new_balance,
        events_summary=events_summary,
        language="hi"
    )

    assert "Ramesh ka ₹140.00 baaki hai" in resp["spoken"] or "Ramesh ka ₹140 baaki hai" in resp["spoken"]
    assert "₹340.00 ka udhaar" in resp["spoken"] or "₹340 ka udhaar" in resp["spoken"]
    assert "kal ₹200.00 ka payment" in resp["spoken"] or "kal ₹200 ka payment" in resp["spoken"]
    assert "record kar diya" in resp["spoken"]

    # 7. Customer Balance Query verification:
    # A subsequent balance query returns ₹140
    bal_query_resp = ResponseGenerator.generate_balance_response("Ramesh", new_balance, language="hi")
    assert "Ramesh ka ₹140.00 baaki hai" in bal_query_resp["text"] or "Ramesh ka ₹140 baaki hai" in bal_query_resp["text"]

    # 8. History displays both records
    history = session.query(Transaction).filter(
        Transaction.shop_id == shop.id,
        Transaction.customer_id == ramesh.id
    ).order_by(Transaction.transaction_date.desc()).all()

    assert len(history) == 2
    types = [h.type for h in history]
    assert "CREDIT" in types
    assert "PAYMENT" in types
