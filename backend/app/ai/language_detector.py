import re
from typing import Tuple

class IndicLanguageDetector:
    # Common Kannada markers (script and romanized)
    KANNADA_WORDS = {
        "saala", "udhar", "kottanu", "kotte", "kottidare", "bandide", "bantu", "eshtu", "ide", 
        "illa", "ninne", "ivattu", "naale", "roopaayi", "rupayi", "ge", "inda", "khata", "baredko",
        "mattu", "haaku", "madu", "beku", "yaru", "tumba", "ella", "nodona", "hege"
    }
    
    # Common Hindi markers (script and romanized)
    HINDI_WORDS = {
        "udhaar", "udhar", "diya", "diye", "diye the", "diya tha", "liya", "liye", "jama", 
        "baaki", "baki", "kitna", "kitne", "hai", "hain", "tha", "thi", "the", "ka", "ki", 
        "ke", "ko", "ne", "se", "aur", "kal", "aaj", "rupaye", "rupayee", "rupee", "karo", 
        "hisaab", "batao", "dikhao", "sabse", "zyada", "paisa", "paise"
    }

    # Unicode ranges
    DEVANAGARI_RANGE = range(0x0900, 0x097F)
    KANNADA_RANGE = range(0x0C80, 0x0CFF)

    @classmethod
    def detect(cls, text: str) -> str:
        """
        Detects primary language: 'kn' (Kannada), 'hi' (Hindi), or 'en' (English).
        Handles script detection and romanized Indic code-mixed text.
        """
        if not text or not text.strip():
            return "en"

        clean = text.strip()

        # 1. Check Unicode scripts
        devanagari_count = sum(1 for ch in clean if ord(ch) in cls.DEVANAGARI_RANGE)
        kannada_count = sum(1 for ch in clean if ord(ch) in cls.KANNADA_RANGE)

        if kannada_count > 2:
            return "kn"
        if devanagari_count > 2:
            return "hi"

        # 2. Check Romanized keywords
        tokens = re.findall(r'[a-zA-Z]+', clean.lower())
        kn_matches = sum(1 for t in tokens if t in cls.KANNADA_WORDS)
        hi_matches = sum(1 for t in tokens if t in cls.HINDI_WORDS)

        if kn_matches > hi_matches and kn_matches > 0:
            return "kn"
        if hi_matches > 0:
            return "hi"

        return "en"
