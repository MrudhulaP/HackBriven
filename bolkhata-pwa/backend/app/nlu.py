"""Rule-based parser: amount, name, credit/payment, balance query, yes/no, correction. No LLM."""
import re
from dataclasses import dataclass

from .lang import edit_distance, name_key, script_of

_DIGITS = {chr(base + i): str(i) for base in (0x0966, 0x0CE6, 0x0C66, 0x0BE6) for i in range(10)}
_DIGIT_TABLE = str.maketrans(_DIGITS)

_HI_1_99 = {"एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पाँच": 5, "छह": 6, "सात": 7, "आठ": 8, "नौ": 9, "दस": 10, "ग्यारह": 11, "बारह": 12, "तेरह": 13, "चौदह": 14, "पंद्रह": 15, "सोलह": 16, "सत्रह": 17, "अठारह": 18, "उन्नीस": 19, "बीस": 20, "इक्कीस": 21, "बाईस": 22, "तेईस": 23, "चौबीस": 24, "पच्चीस": 25, "छब्बीस": 26, "सत्ताईस": 27, "अट्ठाईस": 28, "उनतीस": 29, "तीस": 30, "इकतीस": 31, "बत्तीस": 32, "तैंतीस": 33, "चौंतीस": 34, "पैंतीस": 35, "छत्तीस": 36, "सैंतीस": 37, "अड़तीस": 38, "उनतालीस": 39, "चालीस": 40, "इकतालीस": 41, "बयालीस": 42, "तैंतालीस": 43, "चवालीस": 44, "पैंतालीस": 45, "छियालीस": 46, "सैंतालीस": 47, "अड़तालीस": 48, "उनचास": 49, "पचास": 50, "इक्यावन": 51, "बावन": 52, "तिरपन": 53, "चौवन": 54, "पचपन": 55, "छप्पन": 56, "सत्तावन": 57, "अट्ठावन": 58, "उनसठ": 59, "साठ": 60, "इकसठ": 61, "बासठ": 62, "तिरसठ": 63, "चौंसठ": 64, "पैंसठ": 65, "छियासठ": 66, "सड़सठ": 67, "अड़सठ": 68, "उनहत्तर": 69, "सत्तर": 70, "इकहत्तर": 71, "बहत्तर": 72, "तिहत्तर": 73, "चौहत्तर": 74, "पचहत्तर": 75, "छिहत्तर": 76, "सतहत्तर": 77, "अठहत्तर": 78, "उन्यासी": 79, "अस्सी": 80, "इक्यासी": 81, "बयासी": 82, "तिरासी": 83, "चौरासी": 84, "पचासी": 85, "छियासी": 86, "सत्तासी": 87, "अट्ठासी": 88, "नवासी": 89, "नब्बे": 90, "इक्यानवे": 91, "बानवे": 92, "तिरानवे": 93, "चौरानवे": 94, "पंचानवे": 95, "छियानवे": 96, "सत्तानवे": 97, "अट्ठानवे": 98, "निन्यानवे": 99}  # every Hindi number word 1–99 (Gnani writes spoken Hindi numbers this way)
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
    "नब्बे": 90, **_HI_1_99, "पांच": 5, "छः": 6,
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
        "हजार": 1000, "thousand": 1000, "lakh": 100000, "lac": 100000, "लाख": 100000, "crore": 10000000,
        "crores": 10000000, "karod": 10000000, "karor": 10000000, "करोड़": 10000000, "करोड": 10000000,
        "ನೂರು": 100, "ಸಾವಿರ": 1000, "వంద": 100, "వందలు": 100, "వందల": 100, "వెయ్యి": 1000, "వేలు": 1000, "వేల": 1000,
        "நூறு": 100, "ஆயிரம்": 1000, "ನೂರ": 100, "ಸಾವಿರದ": 1000, "నూట": 100, "నూరు": 100, "நூற்று": 100,
        "ஆயிரத்து": 1000, "million": 1000000, "millions": 1000000, "billion": 1000000000}
FRAC = {"dedh": 1.5, "derh": 1.5, "डेढ़": 1.5, "डेढ": 1.5, "dhai": 2.5, "adhai": 2.5, "ढाई": 2.5}
SAADE = {"saade", "sade", "saare", "साढ़े", "साढे"}
SAWA = {"sawa", "sava", "savaa", "सवा"}  # one and a quarter: सवा सौ = 125
PAUNE = {"paune", "pone", "पौने"}

# "5 kg", "2 packet", "5 customers": the number before these words is a quantity or a count, never rupees
QTY = set("""kg kgs kilo kilos kilogram kilograms g gm gms gram grams litre liter litres liters ltr ltrs ml packet packets
    pkt pkts pack packs piece pieces pcs pc dozen bag bags bottle bottles box boxes tin tins quintal kilos meter metre
    किलो किलोग्राम ग्राम लीटर पैकेट दर्जन बोतल डिब्बा ಕೆಜಿ ಕಿಲೋ ಗ್ರಾಂ ಲೀಟರ್ ಪ್ಯಾಕೆಟ್ కిలో కిలోల కిలోలు గ్రాములు లీటర్ ప్యాకెట్
    கிலோ கிராம் லிட்டர் பாக்கெட் किलोग्राम्स किलोज़ किलोस केजी ग्राम्स लीटर्स पैकेट्स पैकेटें बोतलें दर्जन""".split())
ALL = {"all", "everyone", "everybody", "sab", "sabka", "sabki", "sabke", "sabhi", "सब", "सबका", "सबकी", "सभी", "सबके"}
RECENT = {"recent", "latest", "last", "transactions", "entries", "history", "haal", "pichhli", "pichle", "हाल", "पिछली",
          "पिछले", "एंट्री", "एंट्रीज़", "लेनदेन", "len", "den"}
ADD_WORDS = {"add", "jodo", "jod", "जोड़ो", "जोड़", "जोड़ें", "जोड़िए", "banao", "बनाओ", "new", "naya", "नया"}
CUSTOMER_WORDS = {"customer", "grahak", "ग्राहक"}
COUNTED = {"customers", "customer", "people", "log", "लोग", "ग्राहक", "ಗ್ರಾಹಕರು", "కస్టమర్లు", "வாடிக்கையாளர்கள்"}
MAX_AMOUNT = 10 ** 11  # ₹10,000 crore: anything larger is a mishearing, ask again

YES = {"haan", "ha", "haa", "han", "haanji", "ok", "okay", "yes", "yeah", "sahi", "theek", "हाँ", "हां", "हा",
       "ಹೌದು", "అవును", "ஆமா", "ஆம்", "save", "ओके", "यस", "सेव", "हाँजी", "जी",
       # English yes/ok/save as Gnani writes them inside kn/te/ta speech
       "ಓಕೆ", "ಯೆಸ್", "ಸೇವ್", "ఓకే", "ఒకే", "యెస్", "సేవ్", "ஓகே", "யெஸ்", "சேவ்",
       "ஆமாம்", "ஆமாங்க", "சரி", "ಸರಿ", "సరే"}
NO = {"nahi", "nahin", "na", "no", "not", "wrong", "cancel", "mat", "galat", "नहीं", "नही", "ना", "ಇಲ್ಲ", "కాదు", "இல்லை", "कैंसल", "नो", "ಕ್ಯಾನ್ಸಲ್", "ಕ್ಯಾನ್ಸಲ್", "క్యాన్సిల్", "క్యాన్సల్", "கேன்சல்", "கேன்சல்", "ಬೇಡ", "ಬೇಡಾ", "వద్దు", "வேண்டாம்"}
QUERY = {"outstanding", "bakaya", "baqaya", "बकाया", "dues", "balance", "kitna", "kitne", "kitni", "baaki", "baki", "total", "hisaab", "hisab", "owe", "owes", "due",
         "बाकी", "बाक़ी", "कितना", "कितने", "कितनी", "हिसाब", "टोटल", "बैलेंस", "ಟೋಟಲ್", "ಬ್ಯಾಲೆನ್ಸ್", "టోటల్", "బ్యాలెన్స్",
         "டோட்டல்", "பேலன்ஸ்", "ಎಷ್ಟು", "ಬಾಕಿ", "ఎంత", "బాకీ", "எவ்வளவு", "நிலுவை"}
TAKE = {"liya", "liye", "lia", "li", "le", "लिया", "लिए", "लिये", "ली"}
GIVE = {"diya", "diye", "dia", "di", "दिया", "दिए", "दिये", "दी"}
GOT = {"mila", "mile", "mili", "मिला", "मिले", "मिली"}
JAMA = {"jama", "जमा"}
PAYMENT_KW = GOT | JAMA | {"payment", "paid", "pay", "received", "gave", "given", "returned", "wapas", "vapas",
                           "jamaa", "kattidaru", "kattaru", "kattinar",
                           "वापस", "ಕೊಟ್ಟರು", "ಕೊಟ್ಟ", "ಕೊಟ್ಟಿದ್ದಾರೆ", "ಪಾವತಿ", "ఇచ్చారు", "ఇచ్చాడు", "చెల్లించారు",
                           "கொடுத்தார்", "கொடுத்தான்", "செலுத்தினார்", "kottaru", "icharu", "koduthaar",
                           "पेमेंट", "पेड", "ಪೇಮೆಂಟ್", "పేమెంట్", "பேமெண்ட்"}
# writing an amount on someone's account is credit: "write 250 on Lakshmi's account", "khaate mein 340 likh do"
ACCOUNT_CREDIT = {"likh", "likho", "likhdo", "लिख", "लिखो", "लिखिए", "write", "khaate", "khate", "khata", "खाते", "खाता", "account"}
CREDIT_KW = TAKE | ACCOUNT_CREDIT | {"owes", "owe", "udhaar", "udhar", "udhari", "udhaari", "उधार", "credit", "took", "taken", "ಸಾಲ", "ತಗೊಂಡ್ರು",
                    "ತಗೊಂಡರು", "ತೆಗೆದುಕೊಂಡರು", "అప్పు", "తీసుకున్నారు", "తీసుకున్నాడు", "கடன்", "வாங்கினார்",
                    "வாங்கினான்", "saala", "appu", "kadan", "क्रेडिट", "उधारी", "ಕ್ರೆಡಿಟ್", "క్రెడిట్", "கிரெடிட்",
                    "ಸಾಲದಲ್ಲಿ", "ಸಾಲಕ್ಕೆ", "అప్పులో", "అప్పుగా", "கடனாக", "கடனா", "கடனில்",
                    "ತಗೊಂಡು", "ತೆಗೆದುಕೊಂಡು", "ತಗೊಂಡ", "తీసుకెళ్ళాడు", "తీసుకెళ్లాడు", "తీసుకెళ్ళారు", "తీసుకున్నాడు",
                    "எடுத்துட்டு", "எடுத்துகிட்டு", "எடுத்தார்", "வாங்கிட்டு"}
POSTPOS = {"ne", "se", "ko", "ka", "ki", "ke", "ने", "से", "को", "का", "की", "के"}
# Kannada/Telugu/Tamil perspective, like Hindi ne/ko:  // VERIFY by native speaker
#   "I gave" (shop gave goods) = credit;  "Ramesh gave" = payment, unless "gave TO Ramesh" (ರಮೇಶ್‌ಗೆ) = credit.
GIVE_I = {"ಕೊಟ್ಟೆ", "ಕೊಟ್ಟಿದ್ದೇನೆ", "ಕೊಟ್ಟಿದೀನಿ", "ఇచ్చాను", "ఇచ్చా", "கொடுத்தேன்", "குடுத்தேன்", "கொடுத்திருக்கேன்"}
GIVE_HE = {"ಕೊಟ್ಟರು", "ಕೊಟ್ರು", "ಕೊಟ್ಟ", "ಕೊಟ್ಟಿದ್ದಾರೆ", "ಕೊಟ್ಟನು", "ఇచ్చారు", "ఇచ్చాడు", "ఇచ్చింది",
           "கொடுத்தார்", "கொடுத்தான்", "குடுத்தாரு", "குடுத்தார்", "கொடுத்தாரு", "கொடுத்தாங்க", "kottaru", "icharu",
           "koduthaar"}
PAID_REG = {"ಕಟ್ಟಿದರು", "ಕಟ್ಟಿದ್ರು", "ಕಟ್ಟಿದ", "ಕಟ್ಟಿದ್ದಾರೆ", "ಜಮಾ", "కట్టారు", "కట్టాడు", "కట్టింది", "జమ",
            "கட்டினார்", "கட்டினாரு", "கட்டிட்டாரு", "கட்டினாங்க", "வரவு"}
CREDIT_REG = {"ಉದ್ರಿ", "ಉದರಿ", "udri", "ತೆಗೆದುಕೊಂಡ", "ತಗೊಂಡಿದ್ದಾರೆ", "తీసుకెళ్లారు", "வாங்கினாரு",
              "வாங்கிட்டாரு", "வாங்கினாங்க"}
_DATIVE = ("ige", "ge", "kke", "ke", "ki", "ku", "kku", "uku", "ukku")
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
WANT = {"नीड्स", "नीड", "वांट्स", "वांट", "needs", "need", "wants", "want", "require", "requires", "chahiye", "चाहिए", "mangwana", "mangana", "मंगवाना", "मंगाना", "ಬೇಕು", "ಬೇಕಂತೆ", "ಬೇಕಾಗಿದೆ", "కావాలి",
        "కావాలంట", "வேணும்", "வேண்டும்", "வேணுமாம்"}  # VERIFY by native speaker
CAME = {"ಬಂತು", "ಬಂದ್ಬಿಡ್ತು", "వచ్చేసింది", "வந்துச்சு", "வந்தாச்சு", "வந்துருச்சு"}  # goods came; VERIFY
MONEY = {"paise", "paisa", "पैसे", "पैसा", "ಹಣ", "ದುಡ್ಡು", "డబ్బు", "డబ్బులు", "பணம்", "காசு", "money", "rupaye",
         "रुपये", "ರೂಪಾಯಿ", "రూపాయలు", "ரூபாய்"}
GOODS = {"saamaan", "saman", "samaan", "सामान", "ಸಾಮಾನು", "సామాను", "சாமான்", "பொருள்", "goods", "order", "orders",
         "ऑर्डर", "ಆರ್ಡರ್", "ఆర్డర్", "ஆர்டர்"}
TOTAL = {"ottu", "mottam", "mottham", "kul", "कुल", "ಒಟ್ಟು", "మొత్తం", "மொத்தம்", "மொத்த"}
ARRIVED = {"arrived", "came", "aaya", "aayi", "aaye", "आया", "आई", "आए", "ಬಂದಿದೆ", "ಬಂದಿವೆ", "వచ్చింది", "వచ్చాయి",
           "வந்துவிட்டது", "வந்தது"}
AA, GAYA = {"aa", "आ"}, {"gaya", "gayi", "gaye", "gya", "gai", "गया", "गई", "गयी", "गए"}
NEW = {"naya", "nayi", "naye", "new", "नया", "नई", "नए", "ಹೊಸ", "ಹೊಸಬರು", "కొత్త", "కొత్తవారు", "புதிய", "புதியவர்"}
SKIP = {"skip", "स्किप", "pata", "ಸ್ಕಿಪ್", "స్కిప్", "ஸ்கிப்"}
ITEM_FILLER = set("""liye लिए लिये chahiye चाहिए dena deni dene देना देनी देने lana laana लाना mangwana mangana
    मंगवाना needs need wants want it likho likh लिखो note mean actually sorry wait keep rakh rakho रख रखो रखना बाद देनी batao बताओ dikhao दिखाओ sunao सुनाओ
    list show tell me ಹೇಳಿ ತೋರಿಸಿ చెప్పండి చూపించు சொல்லுங்க சொல்லுங்கள் காட்டு ಸಾಮಾನು సామాను சாமான்
    பொருள் பொருட்கள் வேணும் ಬರೆದುಕೊಳ್ಳಿ ಬರ್ಕೊಳ್ಳಿ ಬರ್ಕೊಳಿ రాసుకోండి రాసుకో எழுதிக்கோங்க எழுதிக்கோ காசு ದುಡ್ಡು డబ్బులు baad later saamaan saman सामान goods items stuff hai है hain हैं karo करो
    kar कर gaya gayi gaye aa aaya aayi ಬೇಕು ಕೊಡಬೇಕು ಅವರಿಗೆ ఆయనకు அவருக்கு కావాలి ఇవ్వాలి வேண்டும் கொடுக்கணும்""".split())
# Contact saving: "Save Arjun's number as 99999 99999", "Arjun ka mobile number ... save karo"  // VERIFY kn/te/ta
CONTACT = {"number", "phone", "mobile", "contact", "नंबर", "नम्बर", "फ़ोन", "फोन", "मोबाइल", "ನಂಬರ್", "ಫೋನ್",
           "ಮೊಬೈಲ್", "నంబర్", "ఫోన్", "మొబైల్", "நம்பர்", "போன்", "மொபைல்", "எண்"}
CONTACT_VERBS = {"save", "add", "update", "change", "set", "store", "note", "सेव", "ಸೇವ್", "సేవ్", "சேவ்"}
# "He paid 200" right after Lakshmi -> Lakshmi
PRONOUN = {"he", "she", "him", "her", "usne", "unhone", "uska", "uski", "unka", "unki", "उसने", "उन्होंने", "उसका",
           "उसकी", "ಅವರು", "ಅವನು", "ಅವಳು", "ఆయన", "ఆమె", "అతను", "அவர்", "அவன்", "அவள்"}
COLLECT = {"collection", "collections", "collected", "collect", "vasooli", "vasuli", "वसूली", "कलेक्शन", "ಕಲೆಕ್ಷನ್",
           "వసూలు", "కలెక్షన్", "வசூல்", "கலெக்ஷன்"}
WEEK = {"week", "weekly", "hafta", "hafte", "हफ्ता", "हफ्ते", "सप्ताह", "ವಾರ", "ವಾರದ", "వారం", "వారంలో", "வாரம்", "வாரத்தில்"}
MOST = {"most", "highest", "top", "maximum", "sabse", "zyada", "jyada", "सबसे", "ज्यादा", "ज़्यादा", "ಹೆಚ್ಚು", "ఎక్కువ",
        "அதிகம்", "அதிகமா"}

KEYWORDS = (set(UNITS) | set(MULT) | set(FRAC) | SAADE | PAUNE | YES | NO | QUERY | GIVE | PAYMENT_KW | CREDIT_KW
            | POSTPOS | TIME | RUPEE | STOP | {"pe", "baaki"} | set().union(*ORDINALS) | ORDER | ARRIVED | AA
            | GAYA | NEW | SKIP | ITEM_FILLER | HONORIFIC | FILLER | GIVE_I | GIVE_HE | PAID_REG | CREDIT_REG | WANT
            | CAME | TOTAL | {"kiska", "kiski", "kiske", "kaun", "किसका", "किसकी", "कौन"} | CONTACT | CONTACT_VERBS
            | PRONOUN | COLLECT | WEEK | MOST | MONEY | QTY | COUNTED | ALL | RECENT | ADD_WORDS | CUSTOMER_WORDS
            | {"which", "what", "kaun", "konsa", "kaunsa", "कौन", "कौनसा", "रूप", "roop", "rup", "is", "are", "dikhao",
               "दिखाओ", "batao", "बताओ", "give", "put", "keep"} | {"as", "to", "for", "me", "my", "who", "i", "did", "show", "today's", "this", "that", "these", "all"})


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

    keys = [_num_key(t) for t in tokens]
    # "do" is Hindi 2 only next to money/units/hundreds ("do sau", "do kilo", "do rupaye"); otherwise it's English "do"
    keys = [k if k != "do" or (i + 1 < len(keys) and (keys[i + 1] in MULT or keys[i + 1] in RUPEE or keys[i + 1] in QTY
                                                       or keys[i + 1] in COUNTED)) else "_do"
            for i, k in enumerate(keys)]

    def flush(i):
        nonlocal total, cur, mod, active
        if active and not (i < len(keys) and keys[i] in QTY | COUNTED):  # "5 kg", "5 customers": not ₹5
            out.append(int(round(total + cur)))
        total = cur = mod = 0.0
        active = False

    for i, t in enumerate(keys):
        if t.isdigit() or t in UNITS:
            v = int(t) if t.isdigit() else UNITS[t]
            # "ninety nine", "twenty five": a single digit after a round tens joins it; other runs are new numbers
            joins = not t.isdigit() and cur % 10 == 0 and v < 10
            prev = keys[i - 1] if i else ""
            if (not t.isdigit() and active and 1 <= cur <= 9 and total == 0 and 10 <= v <= 99 and prev in UNITS
                    and UNITS[prev] == cur and not mod and prev.isascii() and prev not in ("do", "teen", "char", "paanch", "panch")):
                cur = cur * 100 + v  # "two fifty" = 250, "three forty" = 340
                continue
            if active and cur and (t.isdigit() or (cur % 100 and not joins)):
                flush(i)
            cur += v + mod
            mod, active = 0.0, True
        elif t in FRAC:
            if active and cur:
                flush(i)
            cur, active = cur + FRAC[t], True
        elif t in SAADE or t in PAUNE or t in SAWA:
            if active and cur:
                flush(i)
            mod, active = (0.5 if t in SAADE else 0.25 if t in SAWA else -0.25), True
        elif t in MULT:
            m = MULT[t]
            if mod and not cur:  # "sawa sau" = 1.25 x 100
                cur, mod = 1 + mod, 0.0
            if m == 100:
                cur = (cur or 1) * 100
            else:
                total, cur = total + (cur or 1) * m, 0.0
            active = True
        elif active and t in ("and", "aur", "और") and i + 1 < len(keys) and (keys[i + 1] in UNITS or keys[i + 1] in MULT):
            continue  # "three hundred and forty"
        else:
            flush(i)
    flush(len(keys))
    return [a for a in out if a > 0]


def has_quantity(tokens):
    return any(t in QTY and i and (tokens[i - 1].isdigit() or _num_key(tokens[i - 1]) in UNITS)
               for i, t in enumerate(tokens))


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


_GROUP = re.compile(r"\+?\d+")


def extract_phone(text: str):
    """Indian mobile number in the sentence -> (10 digits or None, text without it). Phone digits are never money.

    Spoken numbers come back grouped any way ("999 9999999", "99999 99999", "999-999-9999", "+91 98765 43210"), so
    consecutive digit groups separated only by spaces, hyphens or dots are joined; 10 digits starting 6-9 (after an
    optional +91 / 91 / 0 prefix) make a phone number."""
    t = text.translate(_DIGIT_TABLE)
    groups = list(_GROUP.finditer(t))
    for i in range(len(groups)):
        digits, end = "", None
        for j in range(i, len(groups)):
            if j > i and not re.fullmatch(r"[\s.-]+", t[groups[j - 1].end():groups[j].start()]):
                break
            digits += groups[j].group().lstrip("+")
            end = groups[j].end()
            core = digits[2:] if len(digits) == 12 and digits.startswith("91") else digits[1:] if len(digits) == 11 and digits[0] == "0" else digits
            if len(core) == 10 and core[0] in "6789":
                return core, t[:groups[i].start()] + " " + t[end:]
            if len(digits) >= 12:
                break
    return None, text


def _txn_with_amount(tokens, amount):
    """Account words ("khaate mein", "write on ... account") mean credit only when an amount is said."""
    kind = txn_type(tokens)
    if kind == "credit" and amount is None and not any(t in CREDIT_KW - ACCOUNT_CREDIT for t in tokens):
        return None
    return kind


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
    if has(GIVE_I):
        return "credit"
    if has(GIVE_HE):
        return "credit" if any(_is_dative_name(t) for t in tokens) else "payment"
    if has(PAYMENT_KW) or has(PAID_REG):
        return "payment"
    if has(CREDIT_KW) or has(CREDIT_REG) or any(a in ("baaki", "baki") and b == "pe" for a, b in zip(tokens, tokens[1:])):
        return "credit"
    return None


def _is_dative_name(t):
    """ರಮೇಶ್‌ಗೆ / రమేష్‌కి / ரமேஷுக்கு = 'to Ramesh' (a name word with a dative ending)."""
    if script_of(t) not in ("kn", "te", "ta") or t in KEYWORDS:
        return False
    k = name_key(t)
    return len(k) >= 5 and k.endswith(_DATIVE)


def is_order(tokens):
    if any(t in ORDER for t in tokens) or any(p in LATER for p in zip(tokens, tokens[1:])):
        return True
    # "Ramesh ko 5 kilo cheeni chahiye" / "ರಮೇಶ್‌ಗೆ 2 ಕೆಜಿ ಸಕ್ಕರೆ ಬೇಕು": wanting goods, unless it is about credit/money
    # "ke liye" is "for", not "took"
    rest = [t for i, t in enumerate(tokens) if not (t in ("liye", "लिए", "लिये") and i and tokens[i - 1] in ("ke", "के"))]
    money = any(t in CREDIT_KW | PAYMENT_KW | MONEY | RUPEE for t in rest)
    return (any(t in WANT for t in rest) or has_quantity(tokens)) and not money


def is_arrival(tokens):
    if any(t in ARRIVED for t in tokens) or any(a in AA and b in GAYA for a, b in zip(tokens, tokens[1:])):
        return True
    return any(t in CAME for t in tokens) and not any(t in MONEY for t in tokens)  # "ಹಣ ಬಂತು" is money, not goods


def extract_items(tokens, name):
    """What the customer wants, quantity included: '5 kilo cheeni'."""
    skip = (KEYWORDS - set(UNITS) - set(MULT) - set(FRAC) - QTY) | ITEM_FILLER | {"for"}
    nm = (name or "").lower()
    return " ".join(t for t in tokens if t != nm and (t.isdigit() or (t not in skip and len(t) > 1)))


# Undo the last saved action (within 10 s).  kn/te/ta: // VERIFY by native speaker
UNDO = [("undo",), ("wapas", "lo"), ("galti", "ho", "gayi"), ("galti", "ho", "gaya"), ("cancel", "karo"),
        ("गलती", "हो", "गई"), ("वापस", "लो"), ("go", "back"), ("that", "was", "wrong"), ("ತಪ್ಪಾಯ್ತು",), ("ವಾಪಸ್",),
        ("ಅಳಿಸಿ",), ("ತಪ್ಪಾಯಿತು",), ("ತಪ್ಪಾಗಿದೆ",), ("ತಪ್ಪಾಯ್ತು", "ಬಿಡಿ"), ("తప్పు", "అయింది"), ("తప్పైంది",),
        ("తప్పు", "అయ్యింది"), ("தப்பாயிடுச்சு",), ("தப்பாச்சு",), ("వెనక్కి",), ("తీసేయండి",), ("தப்பா", "போச்சு"), ("தப்பு", "ஆயிடுச்சு"),
        ("அழிங்க",), ("அழிச்சிடுங்க",)]


def is_undo(tokens):
    if len(tokens) > 5:
        return False
    return any(tuple(tokens[i:i + len(u)]) == u for u in UNDO for i in range(len(tokens) - len(u) + 1))


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
    undo: bool = False
    add_customer: bool = False
    recent: bool = False
    list_goods: bool = False
    qty: bool = False  # the sentence has a quantity like "5 kg"
    contact: bool = False  # saving / updating a phone number
    pronoun: bool = False  # "he paid 200": refers to the last customer
    collections: str | None = None  # "today" | "week"
    top_debtor: bool = False


# Phone numbers read out digit by digit: "nine eight seven six ..." / "नौ आठ सात छह ..."
_DIGIT_WORDS = {"zero": "0", "oh": "0", "शून्य": "0", "जीरो": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
                "seven": "7", "eight": "8", "nine": "9", "शून्य": "0", "ज़ीरो": "0", "एक": "1", "दो": "2", "तीन": "3",
                "चार": "4", "पांच": "5", "पाँच": "5", "छह": "6", "सात": "7", "आठ": "8", "नौ": "9"}


_REPEAT = {"double": 2, "triple": 3, "डबल": 2, "ट्रिपल": 3}


def _phone_from_words(text: str):
    """In a sentence about a phone/number, join every spoken number piece into digits:
    'triple nine triple nine double nine double nine', 'नौ सौ निन्यानवे नौ नौ नौ नौ', 'ninety eight seven six ...'."""
    toks = re.sub(r"[,.?!।]", " ", text.translate(_DIGIT_TABLE).lower()).split()
    out, last_word_val, i = [], None, 0
    while i < len(toks):
        t = toks[i]
        k = _num_key(t)
        if t in _REPEAT and i + 1 < len(toks):
            nxt = _DIGIT_WORDS.get(toks[i + 1]) or (str(UNITS[_num_key(toks[i + 1])]) if _num_key(toks[i + 1]) in UNITS else None)
            if nxt is not None and len(nxt) == 1:
                out.append(nxt * _REPEAT[t])
                last_word_val, i = None, i + 2
                continue
        if t.isdigit():
            out.append(t)
            last_word_val = None
        elif t in _DIGIT_WORDS and t not in UNITS:  # zero / oh / शून्य
            out.append(_DIGIT_WORDS[t])
            last_word_val = None
        elif k in UNITS:
            v = UNITS[k]
            if last_word_val is not None and last_word_val % 10 == 0 and last_word_val % 100 and v < 10:
                out[-1] = str(last_word_val + v)  # "ninety" + "nine" -> 99
                last_word_val = None
            elif last_word_val is not None and last_word_val % 100 == 0 and last_word_val >= 100 and v < 100:
                out[-1] = str(last_word_val + v)  # "nine hundred" + "ninety nine" -> 999
                last_word_val = last_word_val + v if v % 10 == 0 else None
            else:
                out.append(str(v))
                last_word_val = v
        elif k in MULT and MULT[k] == 100 and out and last_word_val is not None:
            out[-1] = str(last_word_val * 100)
            last_word_val = last_word_val * 100
        elif out and not (t in RUPEE or t in ("and", "aur")):
            if len("".join(out)) >= 10:
                break
            out, last_word_val = [], None
        i += 1
    digits = "".join(out)
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    return digits if len(digits) == 10 and digits[0] in "6789" else None


def join_spoken_digits(text: str) -> str:
    """A run of 7+ single-digit words becomes one digit string (never shorter runs: 'do teen sau' stays words).
    English 'two five zero' (3+ digit words including zero) is read out digit by digit too."""
    words = text.split()
    out, run = [], []
    for w in words + [""]:
        d = _DIGIT_WORDS.get(w.strip(",.?!।").lower())
        if d is not None:
            run.append((w, d))
            continue
        if len(run) >= 7 or (len(run) >= 3 and any(d == "0" for _, d in run) and all(x.isascii() for x, _ in run)):
            out.append("".join(d for _, d in run))
        else:
            out.extend(x for x, _ in run)
        run = []
        if w:
            out.append(w)
    return " ".join(out)


def parse(text: str) -> Parsed:
    spoken = text
    text = join_spoken_digits(text)
    phone, rest = extract_phone(text)
    if not phone and any(t in CONTACT for t in tokenize(text)):
        phone = _phone_from_words(spoken)  # before digit-joining, so "ninety eight ..." and "double nine" stay whole
        text = spoken if phone else text
        if phone:  # the whole number was read out in words: it is the phone, not an amount
            rest = " ".join(w for w in text.split() if not (_num_key(w.strip(",.?!।").lower()) in UNITS
                                                          or w.strip(",.?!।").lower() in _DIGIT_WORDS
                                                          or w.strip(",.?!।").lower() in _REPEAT or w.strip(",.?!।").isdigit()
                                                          or _num_key(w.strip(",.?!।").lower()) in MULT))
    text = rest  # a 10-digit mobile number is always a phone, never an amount (changing it still needs confirm)
    tokens = tokenize(text)
    nums = amounts(tokens)
    amount = max(nums) if nums else None
    if amount is not None and amount > MAX_AMOUNT:
        amount = None  # implausible: ask for the amount instead of saving a mishearing
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
        txn_type=None if (is_query or order or arrival) else _txn_with_amount(tokens, amount),
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
        undo=is_undo(tokens),
        add_customer=not phone and any(t in ADD_WORDS for t in tokens) and any(t in CUSTOMER_WORDS for t in tokens),
        recent=amount is None and any(t in RECENT for t in tokens) and not any(t in ORDER for t in tokens),
        qty=has_quantity(tokens),
        contact=bool(phone) or (any(t in CONTACT for t in tokens) and any(t in CONTACT_VERBS for t in tokens)),
        pronoun=any(t in PRONOUN for t in tokens),
        collections=(("week" if any(t in WEEK for t in tokens) else "today") if any(t in COLLECT for t in tokens)
                     or (any(t in TIME | WEEK for t in tokens) and any(t in GOT | {"received", "मिले"} for t in tokens)
                         and amount is None) else None),
        top_debtor=any(t in MOST for t in tokens) and any(t in QUERY | {"owe", "owes", "debtor", "udhaar", "उधार"} for t in tokens),
        list_goods=is_query and any(t in GOODS for t in tokens),  # "kiska saamaan baaki hai"
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
