import re
from typing import Tuple

class IndicLanguageDetector:
    # Common Kannada markers (script and romanized)
    KANNADA_WORDS = {
        "saala", "udhar", "kottanu", "kotte", "kottidare", "bandide", "bantu", "eshtu", "ide", 
        "illa", "ninne", "ivattu", "naale", "roopaayi", "rupayi", "ge", "inda", "khata", "baredko",
        "mattu", "haaku", "madu", "beku", "yaru", "tumba", "ella", "nodona", "hege", "saalavaagi",
        "nanage", "kodabeku", "kottiddare", "baredkoli", "serisi"
    }
    
    # Common Hindi markers (script and romanized)
    HINDI_WORDS = {
        "udhaar", "udhar", "diya", "diye", "diye the", "diya tha", "liya", "liye", "jama", 
        "baaki", "baki", "kitna", "kitne", "hai", "hain", "tha", "thi", "the", "ka", "ki", 
        "ke", "ko", "ne", "se", "aur", "kal", "aaj", "rupaye", "rupayee", "rupee", "karo", 
        "hisaab", "batao", "dikhao", "sabse", "zyada", "paisa", "paise", "bhai", "arre", "parcha",
        "mujhe", "dena", "dena hai", "lena", "lena hai", "likho", "likh"
    }

    # Common Telugu markers (script and romanized)
    TELUGU_WORDS = {
        "appu", "ichanu", "ichadu", "vachindi", "vachayi", "enta", "entha", "baki", "baaki",
        "ninna", "eroju", "repu", "rupailu", "rupayalu", "undi", "ledu", "ivvali", "kavali",
        "choodu", "billu", "cheyyi", "garu", "anna", "leka", "pettuko", "rasuko", "kottu",
        "evariki", "ekkuva", "chupinchu", "katha", "varam", "naaku", "naaki", "inka", "rayi",
        "raayi", "roopayalu", "rupeelu", "chellincharu"
    }

    # Common Tamil markers (script and romanized)
    TAMIL_WORDS = {
        "kadan", "koduthen", "koduthar", "vanthuchu", "vandhathu", "evalavu", "evvalavu", "baki",
        "nerru", "netru", "inru", "indru", "naalai", "irukku", "illai", "rubai", "roobai", "thanga",
        "kodu", "paru", "pannu", "thambi", "kanakku", "ezhudhu", "yaarukku", "adhigam", "kaattu",
        "vaaram", "pothum", "enakku", "thara", "vendum", "kuduthan", "kudutha", "tharanum"
    }

    # Unicode ranges
    DEVANAGARI_RANGE = range(0x0900, 0x097F)
    KANNADA_RANGE = range(0x0C80, 0x0CFF)
    TELUGU_RANGE = range(0x0C00, 0x0C7F)
    TAMIL_RANGE = range(0x0B80, 0x0BFF)

    @classmethod
    def detect(cls, text: str) -> str:
        """
        Detects primary language:
        - 'en' (English)
        - 'hi' (Hindi / Hinglish)
        - 'kn' (Kannada / Kanglish)
        - 'te' (Telugu / Tenglish)
        - 'ta' (Tamil / Tanglish)
        """
        if not text or not text.strip():
            return "en"

        clean = text.strip()

        # 1. Check Unicode scripts
        devanagari_count = sum(1 for ch in clean if ord(ch) in cls.DEVANAGARI_RANGE)
        kannada_count = sum(1 for ch in clean if ord(ch) in cls.KANNADA_RANGE)
        telugu_count = sum(1 for ch in clean if ord(ch) in cls.TELUGU_RANGE)
        tamil_count = sum(1 for ch in clean if ord(ch) in cls.TAMIL_RANGE)

        script_counts = {
            "hi": devanagari_count,
            "kn": kannada_count,
            "te": telugu_count,
            "ta": tamil_count
        }
        max_script_lang, max_script_cnt = max(script_counts.items(), key=lambda x: x[1])
        if max_script_cnt > 1:
            return max_script_lang

        # 2. Check Romanized keywords (Code-mixed shop floor speech)
        tokens = re.findall(r'[a-zA-Z]+', clean.lower())
        scores = {
            "hi": sum(1 for t in tokens if t in cls.HINDI_WORDS),
            "kn": sum(1 for t in tokens if t in cls.KANNADA_WORDS),
            "te": sum(1 for t in tokens if t in cls.TELUGU_WORDS),
            "ta": sum(1 for t in tokens if t in cls.TAMIL_WORDS)
        }

        max_lang, max_score = max(scores.items(), key=lambda x: x[1])
        if max_score > 0:
            return max_lang

        return "en"
