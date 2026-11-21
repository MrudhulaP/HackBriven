import re
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, Tuple, List

class EntityExtractor:
    INDIAN_NUMBER_WORDS = {
        # Hindi / Hinglish
        "ek": 1, "do": 2, "teen": 3, "char": 4, "chaar": 4, "panch": 5, "paanch": 5,
        "chhe": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
        "sau": 100, "so": 100, "hazaar": 1000, "hazar": 1000, "lakh": 100000,
        # Kannada
        "ondu": 1, "eradu": 2, "mooru": 3, "naalku": 4, "aidu": 5, "aydu": 5, "aaru": 6,
        "elu": 7, "entu": 8, "ombhatthu": 9, "hatthu": 10, "nooru": 100, "saavira": 1000,
        # Telugu
        "okati": 1, "rendu": 2, "moodu": 3, "nalugu": 4, "ayidu": 5, "aaru_te": 6,
        "yedu": 7, "enimidi": 8, "tommidi": 9, "padi": 10, "vanda": 100, "veyyi": 1000,
        # Tamil
        "ondru": 1, "irandu": 2, "moonru": 3, "naangu": 4, "ainthu": 5, "ezhu": 7,
        "ettu": 8, "onpathu": 9, "pathu": 10, "aayiram": 1000,
        # English
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
        "nine": 9, "ten": 10, "hundred": 100, "thousand": 1000
    }

    # Postpositions across Hindi, Kannada, Telugu, Tamil
    POSTPOSITIONS = {
        "ka", "ki", "ke", "ko", "ne", "se",        # Hindi
        "ge", "inda", "re", "na", "nu", "da", "di", # Kannada
        "ki", "to", "gariki", "lo", "ku",          # Telugu
        "ku", "oda", "kitta", "lerunthu"           # Tamil
    }

    NON_NAMES = {
        "udhaar", "udhar", "credit", "saala", "jama", "paid", "payment", "diya", "diye", "tha", "the",
        "kal", "aaj", "today", "yesterday", "ninne", "ivattu", "ninna", "eroju", "nerru", "netru", "inru",
        "rupaye", "rupees", "roopaayi", "rupailu", "rubai", "rs", "inr", "show", "me", "how", "much",
        "balance", "baaki", "baki", "actually", "it", "was", "not", "undo", "last", "reverse", "collection",
        "hisaab", "tingala", "eshtu", "ide", "kottanu", "bandide", "batao", "dikhao", "sabse", "zyada",
        "who", "which", "bill", "scan", "parcha", "invoice", "receipt", "kadan", "appu", "ichanu", "koduthen"
    }

    @classmethod
    def extract_amount(cls, text: str) -> Optional[Decimal]:
        """Extract numeric amount from text (digits, ₹ symbols, or number words)."""
        # 1. Match digits with optional decimals e.g. "340", "₹ 340", "340.50", "340/-"
        match = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d{1,2})?)\s*(?:/-|rupees|rupaye|roopaayi|rupailu|rubai)?', text, re.IGNORECASE)
        if match:
            try:
                val = Decimal(match.group(1))
                if val > Decimal("0"):
                    return val
            except Exception:
                pass

        # 2. Check compound Indic words e.g. "teen sau" -> 300, "panch sau" -> 500, "vanda" -> 100
        words = text.lower().split()
        for i in range(len(words) - 1):
            w1 = words[i]
            w2 = words[i+1]
            if w1 in cls.INDIAN_NUMBER_WORDS and w2 in ("sau", "so", "nooru", "vanda", "hundred"):
                return Decimal(cls.INDIAN_NUMBER_WORDS[w1] * 100)
            if w1 in cls.INDIAN_NUMBER_WORDS and w2 in ("hazaar", "hazar", "saavira", "veyyi", "aayiram", "thousand"):
                return Decimal(cls.INDIAN_NUMBER_WORDS[w1] * 1000)

        for w in words:
            if w in cls.INDIAN_NUMBER_WORDS and cls.INDIAN_NUMBER_WORDS[w] >= 50:
                return Decimal(cls.INDIAN_NUMBER_WORDS[w])

        return None

    @classmethod
    def extract_date(cls, text: str) -> Tuple[date, str]:
        """
        Extract relative date across English, Hindi, Kannada, Telugu, and Tamil:
        - Yesterday: kal (hi), ninne (kn), ninna (te), nerru/netru (ta), yesterday (en)
        - Day Before Yesterday: parso (hi), monne (kn/te), munnaal (ta)
        - Today: aaj (hi), ivattu (kn), eroju (te), inru/indru (ta), today (en)
        """
        low = text.lower()
        today = date.today()

        if any(w in low for w in ["parso", "day before yesterday", "monne", "munnaal"]):
            return today - timedelta(days=2), "Day Before Yesterday"
        if any(w in low for w in ["kal", "yesterday", "ninne", "ninna", "nerru", "netru"]):
            return today - timedelta(days=1), "Yesterday"
        if any(w in low for w in ["aaj", "today", "ivattu", "eroju", "inru", "indru"]):
            return today, "Today"

        return today, "Today"

    @classmethod
    def extract_customer_name(cls, text: str, known_customers: Optional[List[str]] = None) -> Optional[str]:
        """
        Extract customer name from text across Indian scripts and Romanized speech.
        Supports Hindi, Kannada, Telugu, Tamil, and English sentence grammar.
        """
        if known_customers:
            text_low = text.lower()
            for kc in known_customers:
                if re.search(r'\b' + re.escape(kc.lower()) + r'\b', text_low):
                    return kc

        # Match Unicode (Devanagari, Kannada, Telugu, Tamil) or English words before postpositions
        # E.g. "Ramesh ka", "Ramesh ge", "Ramesh ki", "Ramesh ku", "Ramesh to"
        postposition_regex = r'\b([A-Za-z\u0900-\u097F\u0C80-\u0CFF\u0C00-\u0C7F\u0B80-\u0BFF]{3,25})\s+(?:ka|ki|ke|ko|ne|se|ge|inda|to|gariki|ku|oda|kitta)\b'
        match = re.search(postposition_regex, text, re.IGNORECASE)
        if match:
            candidate = match.group(1).capitalize()
            if candidate.lower() not in cls.NON_NAMES:
                return candidate

        # Phrases like "Ramesh paid 300", "Ramesh appu", "Ramesh kadan", "Ramesh saala"
        match2 = re.search(r'\b([A-Za-z]{3,25})\s+(?:paid|owes|gave|sent|appu|kadan|saala|udhaar)\b', text, re.IGNORECASE)
        if match2:
            candidate = match2.group(1).capitalize()
            if candidate.lower() not in cls.NON_NAMES:
                return candidate

        # Fallback to first non-stop word
        words = text.split()
        if words:
            first = re.sub(r'[^A-Za-z\u0900-\u097F\u0C80-\u0CFF\u0C00-\u0C7F\u0B80-\u0BFF]', '', words[0])
            if len(first) >= 3 and first.lower() not in cls.NON_NAMES:
                return first.capitalize()

        return None
