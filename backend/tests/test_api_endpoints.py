import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.database.seed import seed_demo_data
from app.models.customer import Customer
from app.models.user import User, Shop
from app.main import health_check
from app.api.auth import demo_login
from app.api.customers import list_customers, get_customer_ledger
from app.api.voice import interpret_transcript, confirm_voice_transactions
from app.api.assistant import query_financial_assistant
from app.api.reports import get_daily_report, get_monthly_report
from app.schemas.voice import VoiceInterpretRequest, VoiceConfirmRequest, VoiceConfirmItem, AssistantQueryRequest

@pytest.fixture
def db_and_shop():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()

    seed_demo_data(db, reset=True)
    user = db.query(User).filter(User.mobile == "9876543210").first()
    shop = db.query(Shop).filter(Shop.owner_id == user.id).first()

    yield db, shop, user
    db.close()

def test_health_check_endpoint():
    res = health_check()
    assert res["status"] == "healthy"
    assert res["app"] == "BolKhata"

def test_demo_auth_and_customers_list_endpoint(db_and_shop):
    db, shop, user = db_and_shop
    auth_res = demo_login(db)
    assert auth_res.access_token is not None
    assert auth_res.user.mobile == "9876543210"

    # List customers
    cust_list = list_customers(search=None, has_balance_only=False, shop=shop, db=db)
    names = [c["name"] for c in cust_list]
    assert "Ramesh" in names
    assert "Suresh" in names

    ramesh = next(c for c in cust_list if c["name"] == "Ramesh")
    assert ramesh["outstanding_balance"] == Decimal("0.00")

def test_voice_interpret_and_confirm_workflow_endpoint(db_and_shop):
    db, shop, user = db_and_shop

    # 1. Shopkeeper says: "Ramesh ka 340 udhaar, kal 200 diya tha"
    interpret_req = VoiceInterpretRequest(text="Ramesh ka 340 udhaar, kal 200 diya tha", language="hi")
    v_data = interpret_transcript(data=interpret_req, shop=shop, db=db)
    assert len(v_data.events) == 2

    event_a = v_data.events[0]
    event_b = v_data.events[1]
    assert event_a.customer_name == "Ramesh"
    assert event_a.intent == "ADD_CREDIT"
    assert event_a.amount == Decimal("340")
    assert event_b.customer_name == "Ramesh"
    assert event_b.intent == "RECORD_PAYMENT"
    assert event_b.amount == Decimal("200")

    # 2. Confirm both transactions
    cust = db.query(Customer).filter(Customer.name == "Ramesh", Customer.shop_id == shop.id).first()
    confirm_payload = VoiceConfirmRequest(
        language="hi",
        items=[
            VoiceConfirmItem(
                customer_id=cust.id,
                customer_name="Ramesh",
                type="CREDIT",
                amount=Decimal("340.00"),
                transaction_date=event_a.transaction_date,
                description="Ramesh credit today"
            ),
            VoiceConfirmItem(
                customer_id=cust.id,
                customer_name="Ramesh",
                type="PAYMENT",
                amount=Decimal("200.00"),
                transaction_date=event_b.transaction_date,
                description="Ramesh payment yesterday"
            )
        ]
    )
    confirm_result = confirm_voice_transactions(data=confirm_payload, shop=shop, user=user, db=db)
    assert confirm_result.success is True
    assert confirm_result.new_outstanding_balance == Decimal("140.00")
    assert "140" in confirm_result.spoken_response
    assert "340" in confirm_result.spoken_response
    assert "200" in confirm_result.spoken_response

    # 3. Customer Ledger
    ledger = get_customer_ledger(customer_id=cust.id, shop=shop, db=db)
    assert ledger.outstanding_balance == Decimal("140.00")
    assert len(ledger.transactions) == 2

    # 4. Financial Assistant Query
    asst_query = AssistantQueryRequest(query="Ramesh ka kitna baaki hai?", language="hi")
    asst_resp = query_financial_assistant(data=asst_query, shop=shop, db=db)
    assert "140" in asst_resp.answer

def test_reports_endpoints(db_and_shop):
    db, shop, user = db_and_shop
    daily = get_daily_report(target_date=None, shop=shop, db=db)
    assert "total_credit" in daily
    assert "total_payment" in daily

    monthly = get_monthly_report(year=None, month=None, shop=shop, db=db)
    assert "total_credit" in monthly
    assert "top_debtors" in monthly
    assert "current_total_outstanding" in monthly
