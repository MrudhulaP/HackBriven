import re
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, Tuple, List

class EntityExtractor:
    INDIAN_NUMBER_WORDS = {
        "ek": 1, "do": 2, "teen": 3, "char": 4, "chaar": 4, "panch": 5, "paanch": 5,
        "chhe": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
        "sau": 100, "so": 100, "hazaar": 1000, "hazar": 1000, "lakh": 100000,
        "ondu": 1, "eradu": 2, "mooru": 3, "naalku": 4, "aidu": 5, "aydu": 5, "aaru": 6,
        "elu": 7, "entu": 8, "ombhatthu": 9, "hatthu": 10, "nooru": 100, "saavira": 1000,
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
        "nine": 9, "ten": 10, "hundred": 100, "thousand": 1000
    }

    POSTPOSITIONS = {
        "ka", "ki", "ke", "ko", "ne", "se", "ge", "inda", "re", "na", "nu", "da", "di"
    }

    # Stop words that should never be customer names
    NON_NAMES = {
        "udhaar", "udhar", "credit", "saala", "jama", "paid", "payment", "diya", "diye", "tha", "the",
        "kal", "aaj", "today", "yesterday", "ninne", "ivattu", "rupaye", "rupees", "roopaayi", "rs",
        "inr", "show", "me", "how", "much", "balance", "baaki", "baki", "actually", "it", "was",
        "not", "undo", "last", "reverse", "collection", "hisaab", "tingala", "eshtu", "ide", "kottanu",
        "bandide", "batao", "dikhao", "sabse", "zyada", "who", "which"
    }

    @classmethod
    def extract_amount(cls, text: str) -> Optional[Decimal]:
        """Extract numeric amount from text (digits, ₹ symbols, or number words)."""
        # 1. Match digits with optional decimals e.g. "340", "₹ 340", "340.50", "340/-"
        match = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d{1,2})?)\s*(?:/-|rupees|rupaye|roopaayi)?', text, re.IGNORECASE)
        if match:
            try:
                val = Decimal(match.group(1))
                if val > Decimal("0"):
                    return val
            except Exception:
                pass

        # 2. Check compound Indic words e.g. "teen sau" -> 300, "panch sau" -> 500
        words = text.lower().split()
        for i in range(len(words) - 1):
            w1 = words[i]
            w2 = words[i+1]
            if w1 in cls.INDIAN_NUMBER_WORDS and w2 in ("sau", "so", "nooru", "hundred"):
                return Decimal(cls.INDIAN_NUMBER_WORDS[w1] * 100)
            if w1 in cls.INDIAN_NUMBER_WORDS and w2 in ("hazaar", "hazar", "saavira", "thousand"):
                return Decimal(cls.INDIAN_NUMBER_WORDS[w1] * 1000)

        # Single word amounts
        for w in words:
            if w in cls.INDIAN_NUMBER_WORDS and cls.INDIAN_NUMBER_WORDS[w] >= 50:
                return Decimal(cls.INDIAN_NUMBER_WORDS[w])

        return None

    @classmethod
    def extract_date(cls, text: str) -> Tuple[date, str]:
        """
        Extract relative date from text:
        - 'kal' / 'yesterday' / 'ninne' -> yesterday
        - 'parso' / 'day before yesterday' -> 2 days ago
        - 'aaj' / 'today' / 'ivattu' -> today (default)
        """
        low = text.lower()
        today = date.today()

        if any(w in low for w in ["parso", "day before yesterday", "monne"]):
            return today - timedelta(days=2), "Day Before Yesterday"
        if any(w in low for w in ["kal", "yesterday", "ninne"]):
            return today - timedelta(days=1), "Yesterday"
        if any(w in low for w in ["aaj", "today", "ivattu"]):
            return today, "Today"

        return today, "Today"

    @classmethod
    def extract_customer_name(cls, text: str, known_customers: Optional[List[str]] = None) -> Optional[str]:
        """
        Extract customer name from text, taking into account known customers or Indian grammar.
        E.g. "Ramesh ka 340 udhaar" -> "Ramesh"
        "Ramesh ge 500 saala" -> "Ramesh"
        "Ramesh ne 200 diye" -> "Ramesh"
        """
        # 1. Match against known customer names first
        if known_customers:
            text_low = text.lower()
            for kc in known_customers:
                if re.search(r'\b' + re.escape(kc.lower()) + r'\b', text_low):
                    return kc

        # 2. Heuristic extraction for patterns: Name [ka|ki|ke|ko|ne|se|ge|inda]
        match = re.search(r'\b([A-Za-z\u0900-\u097F\u0C80-\u0CFF]{3,20})\s+(?:ka|ki|ke|ko|ne|se|ge|inda)\b', text, re.IGNORECASE)
        if match:
            candidate = match.group(1).capitalize()
            if candidate.lower() not in cls.NON_NAMES:
                return candidate

        # 3. Match opening word if capitalized or plausible Indian name
        words = text.split()
        if words:
            first = re.sub(r'[^A-Za-z\u0900-\u097F\u0C80-\u0CFF]', '', words[0])
            if len(first) >= 3 and first.lower() not in cls.NON_NAMES:
                return first.capitalize()

        # 4. Check phrases like "Ramesh paid 300"
        match2 = re.search(r'\b([A-Za-z]{3,20})\s+(?:paid|owes|gave|sent)\b', text, re.IGNORECASE)
        if match2:
            candidate = match2.group(1).capitalize()
            if candidate.lower() not in cls.NON_NAMES:
                return candidate

        return None
