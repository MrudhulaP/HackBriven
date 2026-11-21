import pytest
import io
from decimal import Decimal
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PIL import Image

from app.database.session import Base
from app.models.user import Shop, User
from app.models.customer import Customer
from app.ai.language_detector import IndicLanguageDetector
from app.ai.intent_classifier import IntentClassifier
from app.ai.conversational_agent import ConversationalAgent
from app.services.receipt_service import ReceiptService
from app.services.report_service import ReportService
from app.services.ledger_service import LedgerService

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(id="user_test_ml", name="Kiran", mobile="9876543210", password_hash="hashed_pw", preferred_language="kn")
    session.add(user)
    session.commit()

    shop = Shop(id="shop_test_ml", owner_id=user.id, shop_name="Bharat Retail Store", currency="INR")
    session.add(shop)
    session.commit()

    cust1 = Customer(id="cust_ramesh", shop_id=shop.id, name="Ramesh", mobile="9876500001")
    cust2 = Customer(id="cust_suresh", shop_id=shop.id, name="Suresh", mobile="9876500002")
    session.add_all([cust1, cust2])
    session.commit()

    yield session
    session.close()

def test_multilingual_language_detection():
    # Test Kannada
    assert IndicLanguageDetector.detect("Ramesh ge 500 roopaayi saala baredko") == "kn"
    assert IndicLanguageDetector.detect("ರಮೇಶ್‌ಗೆ ಐನೂರು ರೂಪಾಯಿ ಸಾಲ") == "kn"

    # Test Hindi
    assert IndicLanguageDetector.detect("Ramesh ka 340 udhaar, kal 200 diya tha") == "hi"
    assert IndicLanguageDetector.detect("सुरेश ने तीन सौ पचास रुपये दिए") == "hi"

    # Test Telugu
    assert IndicLanguageDetector.detect("Suresh ki 300 rupayalu appu rayi") == "te"
    assert IndicLanguageDetector.detect("రమేశ్ కు 500 అప్పు రాయండి") == "te"

    # Test Tamil
    assert IndicLanguageDetector.detect("Murugan kitta 250 roobai varavu") == "ta"
    assert IndicLanguageDetector.detect("ரமேஷ்க்கு 500 கடன் எழுது") == "ta"

    # Test English
    assert IndicLanguageDetector.detect("Record credit of 500 for Ramesh") == "en"

def test_intent_classification_new_features():
    # Receipt Scan intents
    assert IntentClassifier.classify("Scan this bill")[0] == IntentClassifier.INTENT_SCAN_RECEIPT
    assert IntentClassifier.classify("bill scan karo")[0] == IntentClassifier.INTENT_SCAN_RECEIPT
    assert IntentClassifier.classify("ಬಿಲ್ಲು ಸ್ಕ್ಯಾನ್ ಮಾಡಿ")[0] == IntentClassifier.INTENT_SCAN_RECEIPT
    assert IntentClassifier.classify("రసీదు స్కాన్ చేయి")[0] == IntentClassifier.INTENT_SCAN_RECEIPT
    assert IntentClassifier.classify("பில் ஸ்கேன் செய்")[0] == IntentClassifier.INTENT_SCAN_RECEIPT

    # Weekly report queries
    assert IntentClassifier.classify("How much money did I make this week?")[0] == IntentClassifier.INTENT_WEEKLY_REPORT
    assert IntentClassifier.classify("is hafte kitna bikri hua?")[0] == IntentClassifier.INTENT_WEEKLY_REPORT
    assert IntentClassifier.classify("ee vaaram entha vachindi")[0] == IntentClassifier.INTENT_WEEKLY_REPORT

def test_conversational_turn_flow(test_db):
    session_id = "test_conv_session_1"

    # Turn 1: Weekly question
    res1 = ConversationalAgent.process_turn(
        session_id=session_id,
        user_text="How much money did I make this week?",
        shop_id="shop_test_ml",
        db=test_db
    )
    assert res1["primary_intent"] == IntentClassifier.INTENT_WEEKLY_REPORT
    assert "₹" in res1["text_response"]

    # Turn 2: Receipt scan trigger
    res2 = ConversationalAgent.process_turn(
        session_id=session_id,
        user_text="Scan this bill",
        shop_id="shop_test_ml",
        db=test_db
    )
    assert res2["primary_intent"] == IntentClassifier.INTENT_SCAN_RECEIPT

    # Turn 3: Ambiguous entry -> requires clarification
    res3 = ConversationalAgent.process_turn(
        session_id=session_id,
        user_text="Ramesh ka 500",
        shop_id="shop_test_ml",
        db=test_db
    )
    assert res3["requires_clarification"] is True

def test_receipt_scanner_service():
    # Create test image in memory
    img = Image.new('RGB', (400, 300), color=(255, 255, 255))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    raw_bytes = img_byte_arr.getvalue()

    result = ReceiptService.scan_receipt_image(raw_bytes, filename="test_bill.png")
    assert result["success"] is True
    assert result["total_amount"] > 0
    assert len(result["items"]) >= 1
    assert "vendor_name" in result
