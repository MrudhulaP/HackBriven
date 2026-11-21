"""Rule-based parser: amount, name, credit/payment, balance query, yes/no, correction. No LLM."""
import re
from dataclasses import dataclass

from .lang import edit_distance, name_key, script_of

_DIGITS = {chr(base + i): str(i) for base in (0x0966, 0x0CE6, 0x0C66, 0x0BE6) for i in range(10)}
_DIGIT_TABLE = str.maketrans(_DIGITS)

UNITS = {
    # Hindi (romanized)
    "ek": 1, "do": 2, "teen": 3, "tin": 3, "char": 4, "chaar": 4, "paanch": 5, "panch": 5, "chhe": 6, "chhah": 6,
    "chah": 6, "saat": 7, "sat": 7, "aath": 8, "ath": 8, "nau": 9, "das": 10, "gyarah": 11, "barah": 12,
    "baarah": 12, "terah": 13, "chaudah": 14, "pandrah": 15, "solah": 16, "satrah": 17, "atharah": 18,
    "unnis": 19, "bees": 20, "bis": 20, "pachees": 25, "pachis": 25, "tees": 30, "tis": 30, "chalees": 40,
    "chalis": 40, "chaalis": 40, "pachaas": 50, "pachas": 50, "saath": 60, "sattar": 70, "assi": 80, "nabbe": 90,
    # Hindi (Devanagari)
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "पाँच": 5, "छह": 6, "छः": 6, "सात": 7, "आठ": 8, "नौ": 9,
    "दस": 10, "बीस": 20, "पच्चीस": 25, "तीस": 30, "चालीस": 40, "पचास": 50, "साठ": 60, "सत्तर": 70, "अस्सी": 80,
    "नब्बे": 90,
    # English
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,
    # Kannada (Gnani writes spoken numbers as words)  // VERIFY by native speaker
    "ಒಂದು": 1, "ಎರಡು": 2, "ಮೂರು": 3, "ನಾಲ್ಕು": 4, "ಐದು": 5, "ಆರು": 6, "ಏಳು": 7, "ಎಂಟು": 8, "ಒಂಬತ್ತು": 9,
    "ಹತ್ತು": 10, "ಇಪ್ಪತ್ತು": 20, "ಮೂವತ್ತು": 30, "ನಲವತ್ತು": 40, "ಐವತ್ತು": 50, "ಅರವತ್ತು": 60, "ಎಪ್ಪತ್ತು": 70,
    "ಎಂಬತ್ತು": 80, "ತೊಂಬತ್ತು": 90, "ಇನ್ನೂರು": 200, "ಮುನ್ನೂರು": 300, "ನಾನೂರು": 400, "ಐನೂರು": 500,
    "ಆರುನೂರು": 600, "ಏಳುನೂರು": 700, "ಎಂಟುನೂರು": 800, "ಒಂಬೈನೂರು": 900,
    # Telugu  // VERIFY by native speaker
    "ఒకటి": 1, "రెండు": 2, "మూడు": 3, "నాలుగు": 4, "ఐదు": 5, "ఆరు": 6, "ఏడు": 7, "ఎనిమిది": 8, "తొమ్మిది": 9,
    "పది": 10, "ఇరవై": 20, "ముప్పై": 30, "నలభై": 40, "యాభై": 50, "అరవై": 60, "డెబ్బై": 70, "ఎనభై": 80, "తొంభై": 90,
    # Tamil  // VERIFY by native speaker
    "ஒன்று": 1, "இரண்டு": 2, "மூன்று": 3, "நான்கு": 4, "ஐந்து": 5, "ஆறு": 6, "ஏழு": 7, "எட்டு": 8, "ஒன்பது": 9,
    "பத்து": 10, "இருபது": 20, "முப்பது": 30, "நாற்பது": 40, "ஐம்பது": 50, "அறுபது": 60, "எழுபது": 70, "எண்பது": 80,
    "தொண்ணூறு": 90, "இருநூறு": 200, "முன்னூறு": 300, "நானூறு": 400, "ஐநூறு": 500, "அறுநூறு": 600, "எழுநூறு": 700,
    "எண்ணூறு": 800, "தொள்ளாயிரம்": 900,
    # Joined / oblique forms Gnani actually writes ("ನಾನೂರ ಐವತ್ತು", "நானூற்று ஐம்பது" = 450)  // VERIFY by native speaker
    "ಇನ್ನೂರ": 200, "ಮುನ್ನೂರ": 300, "ನಾನೂರ": 400, "ಐನೂರ": 500, "ಆರುನೂರ": 600, "ಏಳುನೂರ": 700, "ಎಂಟುನೂರ": 800,
    "ಒಂಬೈನೂರ": 900, "ನೂರೈವತ್ತು": 150, "ಇನ್ನೂರೈವತ್ತು": 250, "ಮುನ್ನೂರೈವತ್ತು": 350,
    "రెండొందలు": 200, "మూడొందలు": 300, "నాలుగొందలు": 400, "ఐదొందలు": 500, "నూటయాభై": 150,
    "முந்நூறு": 300, "ஐந்நூறு": 500, "இருநூற்று": 200, "முன்னூற்று": 300, "முந்நூற்று": 300, "நானூற்று": 400,
    "ஐநூற்று": 500, "ஐந்நூற்று": 500, "அறுநூற்று": 600, "எழுநூற்று": 700, "எண்ணூற்று": 800,
    "நூற்றம்பது": 150, "நூற்றைம்பது": 150,
}
MULT = {"sau": 100, "सौ": 100, "hundred": 100, "hazaar": 1000, "hazar": 1000, "hajar": 1000, "हज़ार": 1000,
        "हजार": 1000, "thousand": 1000, "lakh": 100000, "lac": 100000, "लाख": 100000,
        "ನೂರು": 100, "ಸಾವಿರ": 1000, "వంద": 100, "వందలు": 100, "వందల": 100, "వెయ్యి": 1000, "వేలు": 1000, "వేల": 1000,
        "நூறு": 100, "ஆயிரம்": 1000, "ನೂರ": 100, "ಸಾವಿರದ": 1000, "నూట": 100, "నూరు": 100, "நூற்று": 100,
        "ஆயிரத்து": 1000}
FRAC = {"dedh": 1.5, "derh": 1.5, "डेढ़": 1.5, "डेढ": 1.5, "dhai": 2.5, "adhai": 2.5, "ढाई": 2.5}
SAADE = {"saade", "sade", "saare", "साढ़े", "साढे"}
PAUNE = {"paune", "pone", "पौने"}

YES = {"haan", "ha", "haa", "han", "haanji", "ok", "okay", "yes", "yeah", "sahi", "theek", "हाँ", "हां", "हा",
       "ಹೌದು", "అవును", "ஆமா", "ஆம்", "save", "ओके", "यस", "सेव", "हाँजी", "जी",
       # English yes/ok/save as Gnani writes them inside kn/te/ta speech
       "ಓಕೆ", "ಯೆಸ್", "ಸೇವ್", "ఓకే", "ఒకే", "యెస్", "సేవ్", "ஓகே", "யெஸ்", "சேவ்",
       "ஆமாம்", "ஆமாங்க", "சரி", "ಸರಿ", "సరే"}
NO = {"nahi", "nahin", "na", "no", "not", "wrong", "cancel", "mat", "galat", "नहीं", "नही", "ना", "ಇಲ್ಲ", "కాదు", "இல்லை", "कैंसल", "नो", "ಕ್ಯಾನ್ಸಲ್", "ಕ್ಯಾನ್ಸಲ್", "క్యాన్సిల్", "క్యాన్సల్", "கேன்சல்", "கேன்சல்", "ಬೇಡ", "ಬೇಡಾ", "వద్దు", "வேண்டாம்"}
QUERY = {"balance", "kitna", "kitne", "kitni", "baaki", "baki", "total", "hisaab", "hisab", "owe", "owes", "due",
         "बाकी", "बाक़ी", "कितना", "कितने", "कितनी", "हिसाब", "टोटल", "बैलेंस", "ಟೋಟಲ್", "ಬ್ಯಾಲೆನ್ಸ್", "టోటల్", "బ్యాలెన్స్",
         "டோட்டல்", "பேலன்ஸ்", "ಎಷ್ಟು", "ಬಾಕಿ", "ఎంత", "బాకీ", "எவ்வளவு", "நிலுவை"}
TAKE = {"liya", "liye", "lia", "li", "le", "लिया", "लिए", "लिये", "ली"}
GIVE = {"diya", "diye", "dia", "di", "दिया", "दिए", "दिये", "दी"}
GOT = {"mila", "mile", "mili", "मिला", "मिले", "मिली"}
JAMA = {"jama", "जमा"}
PAYMENT_KW = GOT | JAMA | {"payment", "paid", "pay", "received", "gave", "given", "returned", "wapas", "vapas",
                           "वापस", "ಕೊಟ್ಟರು", "ಕೊಟ್ಟ", "ಕೊಟ್ಟಿದ್ದಾರೆ", "ಪಾವತಿ", "ఇచ్చారు", "ఇచ్చాడు", "చెల్లించారు",
                           "கொடுத்தார்", "கொடுத்தான்", "செலுத்தினார்", "kottaru", "icharu", "koduthaar",
                           "पेमेंट", "पेड", "ಪೇಮೆಂಟ್", "పేమెంట్", "பேமெண்ட்"}
CREDIT_KW = TAKE | {"udhaar", "udhar", "udhari", "udhaari", "उधार", "credit", "took", "taken", "ಸಾಲ", "ತಗೊಂಡ್ರು",
                    "ತಗೊಂಡರು", "ತೆಗೆದುಕೊಂಡರು", "అప్పు", "తీసుకున్నారు", "తీసుకున్నాడు", "கடன்", "வாங்கினார்",
                    "வாங்கினான்", "saala", "appu", "kadan", "क्रेडिट", "उधारी", "ಕ್ರೆಡಿಟ್", "క్రెడిట్", "கிரெடிட்",
                    "ಸಾಲದಲ್ಲಿ", "ಸಾಲಕ್ಕೆ", "అప్పులో", "అప్పుగా", "கடனாக", "கடனா", "கடனில்",
                    "ತಗೊಂಡು", "ತೆಗೆದುಕೊಂಡು", "ತಗೊಂಡ", "తీసుకెళ్ళాడు", "తీసుకెళ్లాడు", "తీసుకెళ్ళారు", "తీసుకున్నాడు",
                    "எடுத்துட்டு", "எடுத்துகிட்டு", "எடுத்தார்", "வாங்கிட்டு"}
POSTPOS = {"ne", "se", "ko", "ka", "ki", "ke", "ने", "से", "को", "का", "की", "के"}
TIME = {"aaj", "kal", "abhi", "today", "yesterday", "tomorrow", "now", "आज", "कल", "अभी", "ಇವತ್ತು", "ಇಂದು", "ನಾಳೆ",
        "ఈరోజు", "రేపు", "இன்று", "இன்னைக்கு", "இன்றைக்கு", "நாளைக்கு", "நாளை"}
RUPEE = {"rs", "rupaye", "rupay", "rupye", "rupee", "rupees", "inr", "रुपये", "रुपए", "रूपये", "ರೂಪಾಯಿ",
         "ರೂ", "రూపాయలు", "ரூபாய்", "ರೂಪಾಯಿಗೆ", "రూపాయల", "రూపాయిలు", "ரூபாய்க்கு", "ரூபாயை"}
STOP = set("""hai hain tha thi the kiya kar karo kijiye ji aur pe par wala wale wali mein me bhi hi to toh kya
    ko how much what is was are of on for to from a an and the his her has have does did please lo bolo who
    paise paisa कितना है हैं था थी किया और में पर वाला वाले वाली का ಅವರ ಅವರು ఆయన அவர் nu ಮಾಡಿ ಮಾಡು చేయండి చేయి பண்ணுங்க பண்ணு""".split())
# Pronouns, fillers and honorifics are never customer names ("aap kya kar sakte ho", "Ramesh bhai ne ...").
HONORIFIC = {"bhai", "bhaiya", "didi", "ji", "sahab", "saab", "aunty", "uncle", "भाई", "भैया", "दीदी", "जी", "साहब",
             "anna", "akka", "amma", "thambi", "sir", "madam", "அண்ணா", "அண்ணே", "அக்கா", "அம்மா", "தம்பி", "ಅಣ್ಣ",
             "ಅಣ್ಣಾ", "ಅಕ್ಕ", "ಅಮ್ಮ", "ಸರ್", "అన్నా", "అన్న", "అక్కా", "అమ్మా", "తమ్ముడు", "సార్", "சார்"}
FILLER = set("""aap main mai hum tum woh wo yeh ye usne unhone unka uska yaar arre arey acha accha achha sakte sakta
    sakti ho hoon hu number phone mobile ayyo arey ಅಯ್ಯೋ అయ్యో ஐயோ அய்யோ अरे లేవు లేదు ఇస్తాను ఇస్తా ಇಲ್ಲ ಕೊಡ್ತೀನಿ ಕೊಡ್ತೇನೆ தரேன் தருவேன் आप मैं हम तुम वो वह यह ये यार अरे अच्छा नंबर फ़ोन फोन""".split())
ORDINALS = [
    {"pehla", "pehle", "pahla", "pehli", "first", "1", "ek", "पहला", "पहले", "पहली", "फर्स्ट", "ಮೊದಲ", "ಮೊದಲನೇ", "ಮೊದಲನೆಯ",
     "మొదటి", "మొదటిది", "முதல்", "முதலாவது"},
    {"doosra", "dusra", "doosre", "dusre", "second", "2", "do", "दूसरा", "दूसरे", "दूसरी", "सेकंड", "ಎರಡನೇ", "ಎರಡನೆಯ", "రెండవ",
     "రెండో", "இரண்டாவது"},
    {"teesra", "tisra", "third", "3", "तीसरा", "ಮೂರನೇ", "మూడవ", "மூன்றாவது"},
]
# Back-orders: "Ramesh ke liye 5 kilo cheeni order karo", "Sita ko 2 packet Maggi baad mein deni hai"
ORDER = {"order", "orders", "ordered", "pending", "ऑर्डर", "आर्डर", "ऑर्डर्स", "आर्डर्स", "पेंडिंग", "ಆರ್ಡರ್",
         "ಆರ್ಡರ್‌ಗಳು", "ಆರ್ಡರ್ಗಳು", "ಪೆಂಡಿಂಗ್", "ఆర్డర్", "ఆర్డర్లు", "పెండింగ్", "ஆர்டர்", "ஆர்டர்கள்", "பெண்டிங்"}
LATER = [("baad", "mein"), ("baad", "me"), ("बाद", "में")]
# "Ramesh ka saamaan aa gaya", "Ramesh's sugar arrived"
ARRIVED = {"arrived", "came", "aaya", "aayi", "aaye", "आया", "आई", "आए", "ಬಂದಿದೆ", "ಬಂದಿವೆ", "వచ్చింది", "వచ్చాయి",
           "வந்துவிட்டது", "வந்தது"}
AA, GAYA = {"aa", "आ"}, {"gaya", "gayi", "gaye", "gya", "gai", "गया", "गई", "गयी", "गए"}
NEW = {"naya", "nayi", "naye", "new", "नया", "नई", "नए", "ಹೊಸ", "ಹೊಸಬರು", "కొత్త", "కొత్తవారు", "புதிய", "புதியவர்"}
SKIP = {"skip", "स्किप", "pata", "ಸ್ಕಿಪ್", "స్కిప్", "ஸ்கிப்"}
ITEM_FILLER = set("""liye लिए लिये chahiye चाहिए dena deni dene देना देनी देने lana laana लाना mangwana mangana
    मंगवाना needs need wants want it likho likh लिखो note बाद देनी batao बताओ dikhao दिखाओ sunao सुनाओ
    list show tell me ಹೇಳಿ ತೋರಿಸಿ చెప్పండి చూపించు சொல்லுங்க சொல்லுங்கள் காட்டு ಸಾಮಾನು సామాను சாமான்
    பொருள் பொருட்கள் வேணும் ಬರೆದುಕೊಳ್ಳಿ ಬರ್ಕೊಳ್ಳಿ ಬರ್ಕೊಳಿ రాసుకోండి రాసుకో எழுதிக்கோங்க எழுதிக்கோ காசு ದುಡ್ಡು డబ్బులు baad later saamaan saman सामान goods items stuff hai है hain हैं karo करो
    kar कर gaya gayi gaye aa aaya aayi ಬೇಕು ಕೊಡಬೇಕು ಅವರಿಗೆ ఆయనకు அவருக்கு కావాలి ఇవ్వాలి வேண்டும் கொடுக்கணும்""".split())
KEYWORDS = (set(UNITS) | set(MULT) | set(FRAC) | SAADE | PAUNE | YES | NO | QUERY | GIVE | PAYMENT_KW | CREDIT_KW
            | POSTPOS | TIME | RUPEE | STOP | {"pe", "baaki"} | set().union(*ORDINALS) | ORDER | ARRIVED | AA
            | GAYA | NEW | SKIP | ITEM_FILLER | HONORIFIC | FILLER)


def tokenize(text: str) -> list[str]:
    t = text.translate(_DIGIT_TABLE).lower().replace("₹", " ")
    while re.search(r"(\d),(\d)", t):
        t = re.sub(r"(\d),(\d)", r"\1\2", t)
    t = re.sub(r"(\d)([^\d\s.,])", r"\1 \2", t)
    t = re.sub(r"([^\d\s.,])(\d)", r"\1 \2", t)
    t = re.sub(r"[!?.,;:।॥\"'’‘()\[\]{}/\\|_-]+", " ", t)
    t = re.sub(r"\brehne (do|dijiye|dena)\b|रहने दो", "cancel", t)
    return t.split()


def _num_key(t):
    """Spelling-proof lookup for Indian-script number words: ನಾನ್ನೂರ = ನಾನೂರ = 400."""
    if t in UNITS or t in MULT or script_of(t) in (None, "latin"):
        return t
    k = name_key(t)
    return _UNIT_KEYS.get(k) or _MULT_KEYS.get(k) or _STEM_KEYS.get(_stem(k)) or t


def amounts(tokens: list[str]) -> list[int]:
    """Every number phrase in the sentence: '2 hazaar 500', 'teen sau chalees', 'saade teen sau'..."""
    out, total, cur, mod, active = [], 0.0, 0.0, 0.0, False

    def flush():
        nonlocal total, cur, mod, active
        if active:
            out.append(int(round(total + cur)))
        total = cur = mod = 0.0
        active = False

    for t in map(_num_key, tokens):
        if t.isdigit() or t in UNITS:
            v = int(t) if t.isdigit() else UNITS[t]
            if active and cur and (t.isdigit() or cur % 100):
                flush()
            cur += v + mod
            mod, active = 0.0, True
        elif t in FRAC:
            if active and cur:
                flush()
            cur, active = cur + FRAC[t], True
        elif t in SAADE or t in PAUNE:
            if active and cur:
                flush()
            mod, active = (0.5 if t in SAADE else -0.25), True
        elif t in MULT:
            m = MULT[t]
            if m == 100:
                cur = (cur or 1) * 100
            else:
                total, cur = total + (cur or 1) * m, 0.0
            active = True
        else:
            flush()
    flush()
    return [a for a in out if a > 0]


_UNIT_KEYS = {name_key(w): w for w in UNITS if script_of(w) not in (None, "latin")}
_MULT_KEYS = {name_key(w): w for w in MULT if script_of(w) not in (None, "latin")}


def _stem(k):
    return k[:-1] if len(k) > 3 and k[-1] in "aeiou" else k


def _stem_table():
    """Final-vowel-free keys for hundreds and up: ನಾನೂರ / நானூற்று / நானூற்றி -> 400. Clashing stems are left out."""
    table, clash = {}, set()
    for w, v in [(w, UNITS[w]) for w in UNITS] + [(w, MULT[w]) for w in MULT]:
        if script_of(w) in (None, "latin") or v < 100:  # small numbers are short words: too easy to confuse (ఎంత ≠ ಎಂಟು)
            continue
        s = _stem(name_key(w))
        if s in table and (UNITS.get(table[s]) or MULT.get(table[s])) != v:
            clash.add(s)
        table.setdefault(s, w)
    return {s: w for s, w in table.items() if s not in clash}


_STEM_KEYS = _stem_table()


def is_name_word(t: str) -> bool:
    return (t not in KEYWORDS and not t.isdigit() and len(t) >= 2 and script_of(t) is not None
            and _num_key(t) == t)


def display_name(t: str) -> str:
    return t.capitalize() if script_of(t) == "latin" else t


def extract_name(tokens: list[str]):
    """(name, strong). Strong = found by grammar ('X ne', 'X ka', 'for X'), not just the first unknown word."""
    for i, t in enumerate(tokens):
        if t in POSTPOS and i > 0:
            j = i - 2 if tokens[i - 1] in HONORIFIC and i > 1 else i - 1  # "Ramesh bhai ne"
            if is_name_word(tokens[j]):
                return display_name(tokens[j]), True
    for a, b in zip(tokens, tokens[1:]):
        if a == "for" and is_name_word(b):  # "5 kg sugar for Ramesh"
            return display_name(b), True
    for t in tokens:
        if is_name_word(t):
            return display_name(t), False
    return None, False


_PHONE = re.compile(r"(?<!\d)(?:\+?91[\s-]?|0)?([6-9]\d{4}[\s-]?\d{5})(?!\d)")


def extract_phone(text: str):
    """Indian mobile number in the sentence -> (10 digits or None, text without it). Phone digits are never money."""
    t = text.translate(_DIGIT_TABLE)
    m = _PHONE.search(t)
    if not m:
        return None, text
    return re.sub(r"\D", "", m.group(1)), t[:m.start()] + " " + t[m.end():]


def txn_type(tokens: list[str]):
    has = lambda s: any(t in s for t in tokens)
    marker = next((t for t in tokens if t in {"ne", "se", "ko", "ने", "से", "को"}), None)
    if marker in ("ne", "ने"):
        if has(GIVE) or has(JAMA):
            return "payment"
        if has(TAKE):
            return "credit"
    if marker in ("ko", "को") and has(GIVE):
        return "credit"
    if marker in ("se", "से") and (has(TAKE) or has(GOT)):
        return "payment"
    if has(PAYMENT_KW):
        return "payment"
    if has(CREDIT_KW) or any(a in ("baaki", "baki") and b == "pe" for a, b in zip(tokens, tokens[1:])):
        return "credit"
    return None


def is_order(tokens):
    return any(t in ORDER for t in tokens) or any(p in LATER for p in zip(tokens, tokens[1:]))


def is_arrival(tokens):
    return any(t in ARRIVED for t in tokens) or any(a in AA and b in GAYA for a, b in zip(tokens, tokens[1:]))


def extract_items(tokens, name):
    """What the customer wants, quantity included: '5 kilo cheeni'."""
    skip = KEYWORDS - set(UNITS) - set(MULT) - set(FRAC) | ITEM_FILLER | {"for"}
    nm = (name or "").lower()
    return " ".join(t for t in tokens if t != nm and (t.isdigit() or (t not in skip and len(t) > 1)))


@dataclass
class Parsed:
    tokens: list
    amount: int | None
    name: str | None
    txn_type: str | None
    is_query: bool
    yes: bool
    no: bool
    correction: bool
    order: bool = False
    arrival: bool = False
    items: str = ""
    new: bool = False
    skip: bool = False
    phone: str | None = None
    name_strong: bool = False


def parse(text: str) -> Parsed:
    phone, text = extract_phone(text)
    tokens = tokenize(text)
    nums = amounts(tokens)
    amount = max(nums) if nums else None
    first = tokens[0] if tokens else ""
    short = len(tokens) <= 3
    # A "no" word anywhere beats a yes: "theek nahi hai", "ಸರಿ ಇಲ್ಲ", "not correct". Bare "na" counts only on its own.
    negated = any(t in NO and t not in ("na", "ना") for t in tokens)
    arrival = is_arrival(tokens)
    order = not arrival and is_order(tokens)
    if order or arrival:
        amount = None  # numbers here are quantities, not rupees
    is_query = amount is None and any(t in QUERY for t in tokens)
    name, strong = extract_name(tokens)
    return Parsed(
        tokens=tokens,
        amount=amount,
        name=name,
        txn_type=None if (is_query or order or arrival) else txn_type(tokens),
        is_query=is_query,
        yes=short and first in YES and not negated,
        no=short and (first in NO or negated),
        correction=(first in NO or negated) and amount is not None,
        order=order,
        arrival=arrival,
        items=extract_items(tokens, name) if (order or arrival) else "",
        new=any(t in NEW for t in tokens),
        skip=short and any(t in SKIP | NO for t in tokens),
        phone=phone,
        name_strong=strong,
    )


def _skeleton(word: str) -> str:
    """Consonants only: spoken areas come back in any script and vowels drift ('steshan' vs 'station')."""
    return re.sub("[aeiouy]", "", name_key(word))


def choose_index(text: str, notes: list[str]):
    """'Station Road wala' / 'pehla' / 'second' / '2' / 'ಮೊದಲ' -> index into the options, or None."""
    tokens = tokenize(text)
    skels = [_skeleton(t) for t in tokens]

    joined = [name_key(t) for t in tokens]

    def hit(word):
        s = _skeleton(word)
        return any(s == k or (min(len(s), len(k)) >= 3 and edit_distance(s, k) <= 1) for k in skels)

    for i, note in enumerate(notes):  # area said as one word with an ending: ಗಾಂಧಿನಗರದವರು, గాంధీనగర్
        key = name_key((note or "").replace(" ", ""))
        if len(key) >= 5 and any(j.startswith(key) for j in joined) and \
                not any(name_key((o or "").replace(" ", "")) in j for o in notes if o != note for j in joined):
            return i

    scores = [sum(hit(w) for w in (n or "").split()) for n in notes]
    best = max(scores, default=0)
    if best and scores.count(best) == 1:
        return scores.index(best)
    for t in tokens:
        for i, words in enumerate(ORDINALS):
            if t in words and i < len(notes):
                return i
    return None
