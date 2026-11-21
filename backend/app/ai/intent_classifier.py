import re
from typing import Tuple

class IntentClassifier:
    INTENT_ADD_CREDIT = "ADD_CREDIT"
    INTENT_RECORD_PAYMENT = "RECORD_PAYMENT"
    INTENT_CHECK_BALANCE = "CHECK_BALANCE"
    INTENT_VIEW_HISTORY = "VIEW_HISTORY"
    INTENT_DAILY_SUMMARY = "DAILY_SUMMARY"
    INTENT_MONTHLY_SUMMARY = "MONTHLY_SUMMARY"
    INTENT_CORRECT_TRANSACTION = "CORRECT_TRANSACTION"
    INTENT_REVERSE_TRANSACTION = "REVERSE_TRANSACTION"
    INTENT_LIST_CUSTOMERS = "LIST_CUSTOMERS"
    INTENT_GENERAL_HELP = "GENERAL_HELP"
    INTENT_AMBIGUOUS_TRANSACTION = "AMBIGUOUS_TRANSACTION"
    INTENT_UNKNOWN = "UNKNOWN"

    @classmethod
    def classify(cls, text: str) -> Tuple[str, float]:
        """
        Classify the intent of an utterance or sub-clause with a confidence score.
        """
        if not text:
            return cls.INTENT_UNKNOWN, 0.0

        low = text.lower().strip()

        # Check Correction
        if any(w in low for w in ["actually", "correction", "nahi", "not", "ke badle", "instead of"]) and re.search(r'\d+', low):
            if any(w in low for w in ["was", "tha", "thi", "it was", "actual"]):
                return cls.INTENT_CORRECT_TRANSACTION, 0.95

        # Check Reversal / Undo
        if any(w in low for w in ["undo", "reverse", "wapas", "cancel last", "hatao", "delete last", "revoked"]):
            return cls.INTENT_REVERSE_TRANSACTION, 0.95

        # Check Daily Summary / Today's Collections
        if any(w in low for w in ["aaj ka hisaab", "today's collection", "today collection", "today's summary", "aaj kitna collection", "aaj kitna aaya", "ivattina hisaab", "today report"]):
            return cls.INTENT_DAILY_SUMMARY, 0.95

        # Check Monthly Summary
        if any(w in low for w in ["mahine ka hisaab", "this month", "monthly report", "monthly summary", "tingala hisaab"]):
            return cls.INTENT_MONTHLY_SUMMARY, 0.95

        # Check Balance Query
        if any(w in low for w in [
            "kitna baaki", "kitna baki", "balance", "how much", "owe", "owes", 
            "eshtu baaki", "eshtu saala", "eshtu ide", "kitna dena hai", "kitna lena hai"
        ]):
            return cls.INTENT_CHECK_BALANCE, 0.95

        # Check History / Transactions Query
        if any(w in low for w in ["last", "history", "pichla", "pichle", "kab payment", "transactions", "last five", "last three", "entry"]):
            return cls.INTENT_VIEW_HISTORY, 0.92

        # Check List Customers
        if any(w in low for w in ["customers", "grahak", "sab grahak", "all customers", "list customers", "who owes", "sabse zyada"]):
            return cls.INTENT_LIST_CUSTOMERS, 0.90

        # Check Help
        if any(w in low for w in ["help", "kaise use", "madad", "sahayata", "what can you do"]):
            return cls.INTENT_GENERAL_HELP, 0.95

        # Financial Entry Check
        has_credit_words = any(w in low for w in ["udhaar", "udhar", "credit", "saala", "baredko", "likho", "liya", "liye", "diya credit", "gave credit"])
        has_payment_words = any(w in low for w in ["diya", "diye", "paid", "payment", "jama", "jama kiya", "bhara", "bandide", "kottanu", "received", "chuka"])
        has_number = bool(re.search(r'\d+', low) or any(w in low for w in ["sau", "hazaar", "thousand", "hundred", "roopaayi"]))

        # If both words appear in one clause, check context:
        # e.g. "credit diya" -> credit
        if "credit diya" in low or "udhaar diya" in low:
            return cls.INTENT_ADD_CREDIT, 0.96

        if has_credit_words and not has_payment_words:
            return cls.INTENT_ADD_CREDIT, 0.95
        
        if has_payment_words and not has_credit_words:
            return cls.INTENT_RECORD_PAYMENT, 0.95

        # Ambiguous case: has number and customer or "ka 500" without explicit udhaar or diya
        if has_number and not has_credit_words and not has_payment_words:
            return cls.INTENT_AMBIGUOUS_TRANSACTION, 0.70

        return cls.INTENT_UNKNOWN, 0.30
