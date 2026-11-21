import pytest
from decimal import Decimal
from datetime import date, timedelta

from app.ai.language_detector import IndicLanguageDetector
from app.ai.intent_classifier import IntentClassifier
from app.ai.entity_extractor import EntityExtractor
from app.ai.transaction_parser import TransactionParser

def test_language_detection():
    assert IndicLanguageDetector.detect("Ramesh ka 340 udhaar") == "hi"
    assert IndicLanguageDetector.detect("Ramesh ge 500 roopaayi saala baredko") == "kn"
    assert IndicLanguageDetector.detect("Ramesh paid 300 rupees yesterday") == "en"

def test_intent_classification():
    # Credit
    assert IntentClassifier.classify("Ramesh ka 340 udhaar")[0] == IntentClassifier.INTENT_ADD_CREDIT
    assert IntentClassifier.classify("Ramesh ko 500 rupees ka credit diya")[0] == IntentClassifier.INTENT_ADD_CREDIT
    assert IntentClassifier.classify("Ramesh ge 500 saala baredko")[0] == IntentClassifier.INTENT_ADD_CREDIT

    # Payment
    assert IntentClassifier.classify("Ramesh ne 200 diye")[0] == IntentClassifier.INTENT_RECORD_PAYMENT
    assert IntentClassifier.classify("Ramesh paid 300 rupees")[0] == IntentClassifier.INTENT_RECORD_PAYMENT
    assert IntentClassifier.classify("Ramesh inda 500 roopaayi bandide")[0] == IntentClassifier.INTENT_RECORD_PAYMENT

    # Balance Query
    assert IntentClassifier.classify("Ramesh ka kitna baaki hai?")[0] == IntentClassifier.INTENT_CHECK_BALANCE
    assert IntentClassifier.classify("How much does Suresh owe me?")[0] == IntentClassifier.INTENT_CHECK_BALANCE
    assert IntentClassifier.classify("Ramesh ge eshtu baaki ide?")[0] == IntentClassifier.INTENT_CHECK_BALANCE

    # History Query
    assert IntentClassifier.classify("Show me Ramesh's last five transactions")[0] == IntentClassifier.INTENT_VIEW_HISTORY
    assert IntentClassifier.classify("Ramesh ne last time kab payment kiya tha?")[0] == IntentClassifier.INTENT_VIEW_HISTORY

    # Reversal
    assert IntentClassifier.classify("Undo the last payment")[0] == IntentClassifier.INTENT_REVERSE_TRANSACTION

    # Correction
    assert IntentClassifier.classify("Actually, it was 400, not 300")[0] == IntentClassifier.INTENT_CORRECT_TRANSACTION

def test_ambiguity_detection():
    # Ambiguous credit or payment
    res1 = TransactionParser.parse("Ramesh ka 500")
    assert res1.requires_clarification is True
    assert "Is ₹500 credit given to Ramesh or a payment received from Ramesh?" in res1.clarification_prompt

    # Missing amount
    res2 = TransactionParser.parse("Ramesh paid")
    assert res2.requires_clarification is True
    assert "How much did Ramesh pay?" in res2.clarification_prompt

def test_relative_date_extraction():
    today = date.today()
    yesterday = today - timedelta(days=1)

    d1, label1 = EntityExtractor.extract_date("kal 200 diya tha")
    assert d1 == yesterday
    assert label1 == "Yesterday"

    d2, label2 = EntityExtractor.extract_date("aaj 500 udhaar")
    assert d2 == today
    assert label2 == "Today"
