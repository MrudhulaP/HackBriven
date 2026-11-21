import re
from typing import Tuple

class IntentClassifier:
    INTENT_ADD_CREDIT = "ADD_CREDIT"
    INTENT_RECORD_PAYMENT = "RECORD_PAYMENT"
    INTENT_CHECK_BALANCE = "CHECK_BALANCE"
    INTENT_VIEW_HISTORY = "VIEW_HISTORY"
    INTENT_DAILY_SUMMARY = "DAILY_SUMMARY"
    INTENT_WEEKLY_REPORT = "WEEKLY_REPORT"
    INTENT_MONTHLY_SUMMARY = "MONTHLY_SUMMARY"
    INTENT_TOP_DEBTORS = "TOP_DEBTORS"
    INTENT_CORRECT_TRANSACTION = "CORRECT_TRANSACTION"
    INTENT_REVERSE_TRANSACTION = "REVERSE_TRANSACTION"
    INTENT_LIST_CUSTOMERS = "LIST_CUSTOMERS"
    INTENT_SCAN_RECEIPT = "SCAN_RECEIPT"
    INTENT_GENERAL_HELP = "GENERAL_HELP"
    INTENT_AMBIGUOUS_TRANSACTION = "AMBIGUOUS_TRANSACTION"
    INTENT_UNKNOWN = "UNKNOWN"

    # Pre-compiled regex for receipt scan voice commands across 5 languages
    SCAN_BILL_PATTERNS = [
        r'\bscan\s+(?:this\s+)?(?:bill|receipt|invoice|parcha)\b',
        r'\b(?:bill|receipt|parcha|billu)\s+scan\b',
        r'\b(?:bill|parcha)\s+(?:dekh|dekho|karo)\b',
        r'\bbill\s+(?:nodi|maadu)\b',                 # Kannada
        r'\b(?:billu|bill)\s+(?:scan\s+)?cheyyi\b',   # Telugu
        r'\b(?:bill|receipt)\s+(?:scan\s+)?pannu\b',   # Tamil
        r'\btake\s+(?:a\s+)?photo\s+of\s+bill\b',
        r'ಸ್ಕ್ಯಾನ್', r'ಬಿಲ್ಲು.*ಸ್ಕ್ಯಾನ್', r'రసీదు', r'బిల్లు.*స్కాన్', r'ஸ்கேன்', r'பில்.*ஸ்கேன்', r'पर्चा.*स्कैन', r'बिल.*स्कैन'
    ]

    @classmethod
    def clean_fillers(cls, text: str) -> str:
        """Strip colloquial Indian conversation fillers without losing semantic words."""
        fillers = [
            r'\barre\b', r'\bbhai\b', r'\bsuno\b', r'\bplease\b', r'\byaar\b',
            r'\banna\b', r'\bthambi\b', r'\bgaru\b', r'\bji\b', r'\bdekho\b',
            r'\bchoodu\b', r'\bparu\b', r'\bmatlab\b'
        ]
        res = text.lower()
        for f in fillers:
            res = re.sub(f, '', res, flags=re.IGNORECASE)
        return ' '.join(res.split())

    @classmethod
    def classify(cls, text: str) -> Tuple[str, float]:
        """
        Classify intent across English, Hindi, Kannada, Telugu, and Tamil.
        """
        if not text:
            return cls.INTENT_UNKNOWN, 0.0

        low = cls.clean_fillers(text)

        # 1. Check Voice-Activated Receipt / Bill Scanning
        for pat in cls.SCAN_BILL_PATTERNS:
            if re.search(pat, low):
                return cls.INTENT_SCAN_RECEIPT, 0.98

        # 2. Check Correction
        if any(w in low for w in ["actually", "correction", "nahi", "not", "ke badle", "instead of", "badalu"]) and re.search(r'\d+', low):
            if any(w in low for w in ["was", "tha", "thi", "it was", "actual", "undi"]):
                return cls.INTENT_CORRECT_TRANSACTION, 0.95

        # 3. Check Reversal / Undo
        if any(w in low for w in ["undo", "reverse", "wapas", "cancel last", "hatao", "delete last", "teesi veyyi", "thooku"]):
            return cls.INTENT_REVERSE_TRANSACTION, 0.95

        # 4. Check Top Debtors ("Who owes me the most money?")
        if any(w in low for w in [
            "who owes", "most money", "highest", "sabse zyada", "sabse bada",
            "tumba saala", "ati hecchu", "ekkuva appu", "athigam kadan", "evariki ekkuva", "yaarukku athigam"
        ]):
            return cls.INTENT_TOP_DEBTORS, 0.96

        # 5. Check Weekly Report ("How much money did I make this week?")
        if any(w in low for w in [
            "this week", "made this week", "iss hafte", "is hafte", "ee varam",
            "ee vaaram", "inda vaaram", "indha vaaram", "week collection", "hafte ka"
        ]):
            return cls.INTENT_WEEKLY_REPORT, 0.96

        # 6. Check Daily Summary / Today's Collections
        if any(w in low for w in [
            "aaj ka hisaab", "today's collection", "today collection", "today's summary",
            "aaj kitna collection", "aaj kitna aaya", "ivattina hisaab", "eroju enta vachindi",
            "inru evalavu vanthuchu", "today report"
        ]):
            return cls.INTENT_DAILY_SUMMARY, 0.95

        # 7. Check Monthly Summary
        if any(w in low for w in [
            "mahine ka hisaab", "this month", "monthly report", "monthly summary",
            "tingala hisaab", "ee nela", "inda maasam"
        ]):
            return cls.INTENT_MONTHLY_SUMMARY, 0.95

        has_number = bool(re.search(r'\d+', low) or any(w in low for w in [
            "sau", "hazaar", "thousand", "hundred", "nooru", "roopaayi", "rupailu", "rubai", "vanda", "veyyi"
        ]))

        # 8. Check Balance Query (Only when asking for balance, not stating an amount to record)
        if (not has_number or "how much" in low or "kitna" in low or "eshtu" in low or "enta" in low or "evalavu" in low) and any(w in low for w in [
            "kitna baaki", "kitna baki", "balance", "how much",
            "eshtu baaki", "eshtu saala", "eshtu ide", "enta baki", "entha baki",
            "evalavu baki", "evvalavu baki", "kitna dena hai", "kitna lena hai"
        ]):
            return cls.INTENT_CHECK_BALANCE, 0.95

        # 9. Check History / Transactions Query
        if any(w in low for w in ["history", "pichla", "pichle", "kab payment", "transactions", "last five", "last three"]):
            return cls.INTENT_VIEW_HISTORY, 0.92

        # 10. Check List Customers
        if any(w in low for w in ["customers", "grahak", "sab grahak", "all customers", "list customers", "andaroo", "ellaru"]):
            return cls.INTENT_LIST_CUSTOMERS, 0.90

        # 11. Check Help
        if any(w in low for w in ["help", "kaise use", "madad", "sahayata", "sahayam", "udhavi", "what can you do"]):
            return cls.INTENT_GENERAL_HELP, 0.95

        # 12. Financial Entry Check (Directional Credit vs Payment across 5 languages)
        credit_keywords = [
            # English
            "should pay", "needs to pay", "must pay", "owes me", "owes", "owe me", "give credit",
            "credit of", "credit for", "to pay me", "has to pay", "credit", "gave credit",
            # Hindi / Hinglish
            "udhaar", "udhar", "dena hai", "lena hai", "likho", "likh do", "likh", "उधार", "देना है",
            # Telugu / Tenglish
            "ivvali", "ivvalasi", "appu", "rayi", "raayi", "pettuko", "rasuko", "appu rayi", "appu rayandi",
            "ఇవ్వాలి", "అప్పు", "రాయి", "రాయండి", "అప్పు రాయి",
            # Kannada / Kanglish
            "saala", "baredko", "baredkoli", "kodabeku", "ಕೊಡಬೇಕು", "ಸಾಲ", "ಬರೆದುಕೊ",
            # Tamil / Tanglish
            "kadan", "ezhudhu", "thara vendum", "tharanum", "kodukanum", "கடன்", "எழுது", "தர வேண்டும்"
        ]

        payment_keywords = [
            # English
            "paid me", "paid", "received", "received from", "payment of", "payment from", "cleared", "settled", "payment",
            # Hindi / Hinglish
            "diya", "diye", "diye the", "diya tha", "jama", "jama kiya", "bhara", "mila", "aaya", "जमा", "दिया", "दिए",
            # Telugu / Tenglish
            "vachindi", "ichadu", "ichanu", "chellimpu", "chellincharu", "payment vachindi",
            "వచ్చింది", "ఇచ్చాడు", "ఇచ్చాను", "చెల్లించారు", "చెల్లింపు",
            # Kannada / Kanglish
            "bandide", "kottanu", "kotte", "kottidare", "payment bantu", "ಪಾವತಿ", "ಬಂದಿದೆ", "ಕೊಟ್ಟನು",
            # Tamil / Tanglish
            "vanthuchu", "vandhathu", "koduthen", "koduthar", "varavu", "வரவு", "வந்தது", "கொடுத்தார்"
        ]

        # Explicit combinations e.g. "credit diya" / "udhaar diya" -> credit
        if any(p in low for p in ["credit diya", "udhaar diya", "appu ichanu", "kadan koduthen"]):
            return cls.INTENT_ADD_CREDIT, 0.98

        has_credit_words = any(w in low for w in credit_keywords)
        has_payment_words = any(w in low for w in payment_keywords)

        if has_credit_words and not has_payment_words:
            return cls.INTENT_ADD_CREDIT, 0.98

        if has_payment_words and not has_credit_words:
            return cls.INTENT_RECORD_PAYMENT, 0.98

        # Ambiguous case: has number & customer but missing directional indicators (e.g. "Ramesh 300", "Ramesh ka 500")
        if has_number and not has_credit_words and not has_payment_words:
            return cls.INTENT_AMBIGUOUS_TRANSACTION, 0.70

        return cls.INTENT_UNKNOWN, 0.30
