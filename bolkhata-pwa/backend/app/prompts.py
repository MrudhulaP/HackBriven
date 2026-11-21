"""Every user-facing string, in all 5 languages: spoken prompts, UI labels, reminder text.

Kannada, Telugu and Tamil strings were AI-written.  // VERIFY by native speaker
"""

PROMPTS = {
    "hi": {
        "greeting": "नमस्ते! मैं बोलखाता हूँ, आपके खाते का AI सहायक। बोलिए, किसने कितना उधार लिया?",
        "notUnderstood": "माफ़ कीजिए, समझ नहीं आया। फिर से बोलिए।",
        "askAmount": "{name} के लिए कितने रुपये?",
        "askName": "किस ग्राहक का? नाम बताइए।",
        "askType": "{name}, {amount} रुपये। उधार लिया या पैसे जमा किए?",
        "chooseCustomer": "{name} नाम के {count} ग्राहक हैं: {options}। कौन से?",
        "confirmCredit": "{name} को {amount} रुपये उधार। सेव करूँ?",
        "confirmCreditNew": "{name} नए ग्राहक हैं। {amount} रुपये उधार। सेव करूँ?",
        "confirmPayment": "{name} से {amount} रुपये मिले। सेव करूँ?",
        "saved": "सेव हो गया। {name} का बाकी {balance} रुपये है।",
        "cancelled": "ठीक है, रद्द कर दिया।",
        "balanceIs": "{name} का बाकी {balance} रुपये है।",
        "balanceMulti": "{name} नाम के ग्राहक: {list}।",
        "customerNotFound": "{name} नाम का कोई ग्राहक नहीं मिला।",
        "totalDue": "सभी ग्राहकों का कुल बाकी {amount} रुपये है।",
    },
    "en": {
        "greeting": "Hello! I am BolKhata, your AI ledger assistant. Tell me, who took how much on credit?",
        "notUnderstood": "Sorry, I didn't get that. Please say it again.",
        "askAmount": "How many rupees for {name}?",
        "askName": "Which customer? Please say the name.",
        "askType": "{name}, {amount} rupees. Credit taken, or payment received?",
        "chooseCustomer": "There are {count} customers named {name}: {options}. Which one?",
        "confirmCredit": "{amount} rupees credit for {name}. Shall I save?",
        "confirmCreditNew": "{name} is a new customer. {amount} rupees credit. Shall I save?",
        "confirmPayment": "{amount} rupees received from {name}. Shall I save?",
        "saved": "Saved. {name}'s balance is {balance} rupees.",
        "cancelled": "Okay, cancelled.",
        "balanceIs": "{name}'s balance is {balance} rupees.",
        "balanceMulti": "Customers named {name}: {list}.",
        "customerNotFound": "No customer named {name} found.",
        "totalDue": "Total due from all customers is {amount} rupees.",
    },
    "kn": {  # VERIFY by native speaker
        "greeting": "ನಮಸ್ಕಾರ! ನಾನು ಬೋಲ್‌ಖಾತಾ, ನಿಮ್ಮ ಖಾತೆಯ AI ಸಹಾಯಕ. ಹೇಳಿ, ಯಾರು ಎಷ್ಟು ಸಾಲ ತೆಗೆದುಕೊಂಡರು?",
        "notUnderstood": "ಕ್ಷಮಿಸಿ, ಅರ್ಥವಾಗಲಿಲ್ಲ. ಮತ್ತೊಮ್ಮೆ ಹೇಳಿ.",
        "askAmount": "{name} ಅವರಿಗೆ ಎಷ್ಟು ರೂಪಾಯಿ?",
        "askName": "ಯಾವ ಗ್ರಾಹಕರು? ಹೆಸರು ಹೇಳಿ.",
        "askType": "{name}, {amount} ರೂಪಾಯಿ. ಸಾಲ ತೆಗೆದುಕೊಂಡರಾ ಅಥವಾ ಹಣ ಕೊಟ್ಟರಾ?",
        "chooseCustomer": "{name} ಹೆಸರಿನ {count} ಗ್ರಾಹಕರಿದ್ದಾರೆ: {options}. ಯಾರು?",
        "confirmCredit": "{name} ಅವರಿಗೆ {amount} ರೂಪಾಯಿ ಸಾಲ. ಉಳಿಸಲೇ?",
        "confirmCreditNew": "{name} ಹೊಸ ಗ್ರಾಹಕರು. {amount} ರೂಪಾಯಿ ಸಾಲ. ಉಳಿಸಲೇ?",
        "confirmPayment": "{name} ಅವರಿಂದ {amount} ರೂಪಾಯಿ ಬಂತು. ಉಳಿಸಲೇ?",
        "saved": "ಉಳಿಸಲಾಗಿದೆ. {name} ಅವರ ಬಾಕಿ {balance} ರೂಪಾಯಿ.",
        "cancelled": "ಸರಿ, ರದ್ದು ಮಾಡಿದೆ.",
        "balanceIs": "{name} ಅವರ ಬಾಕಿ {balance} ರೂಪಾಯಿ.",
        "balanceMulti": "{name} ಹೆಸರಿನ ಗ್ರಾಹಕರು: {list}.",
        "customerNotFound": "{name} ಹೆಸರಿನ ಗ್ರಾಹಕರು ಸಿಗಲಿಲ್ಲ.",
        "totalDue": "ಎಲ್ಲಾ ಗ್ರಾಹಕರ ಒಟ್ಟು ಬಾಕಿ {amount} ರೂಪಾಯಿ.",
    },
    "te": {  # VERIFY by native speaker
        "greeting": "నమస్తే! నేను బోల్‌ఖాతా, మీ ఖాతా AI సహాయకుడిని. చెప్పండి, ఎవరు ఎంత అప్పు తీసుకున్నారు?",
        "notUnderstood": "క్షమించండి, అర్థం కాలేదు. మళ్ళీ చెప్పండి.",
        "askAmount": "{name} కి ఎన్ని రూపాయలు?",
        "askName": "ఏ కస్టమర్? పేరు చెప్పండి.",
        "askType": "{name}, {amount} రూపాయలు. అప్పు తీసుకున్నారా లేక డబ్బు ఇచ్చారా?",
        "chooseCustomer": "{name} పేరుతో {count} కస్టమర్లు ఉన్నారు: {options}. ఎవరు?",
        "confirmCredit": "{name} కి {amount} రూపాయలు అప్పు. సేవ్ చేయనా?",
        "confirmCreditNew": "{name} కొత్త కస్టమర్. {amount} రూపాయలు అప్పు. సేవ్ చేయనా?",
        "confirmPayment": "{name} నుండి {amount} రూపాయలు వచ్చాయి. సేవ్ చేయనా?",
        "saved": "సేవ్ అయింది. {name} బాకీ {balance} రూపాయలు.",
        "cancelled": "సరే, రద్దు చేశాను.",
        "balanceIs": "{name} బాకీ {balance} రూపాయలు.",
        "balanceMulti": "{name} పేరుతో కస్టమర్లు: {list}.",
        "customerNotFound": "{name} పేరుతో కస్టమర్ దొరకలేదు.",
        "totalDue": "అందరి మొత్తం బాకీ {amount} రూపాయలు.",
    },
    "ta": {  # VERIFY by native speaker
        "greeting": "வணக்கம்! நான் போல்காதா, உங்கள் கணக்கின் AI உதவியாளர். சொல்லுங்கள், யார் எவ்வளவு கடன் வாங்கினார்கள்?",
        "notUnderstood": "மன்னிக்கவும், புரியவில்லை. மீண்டும் சொல்லுங்கள்.",
        "askAmount": "{name} க்கு எத்தனை ரூபாய்?",
        "askName": "எந்த வாடிக்கையாளர்? பெயரைச் சொல்லுங்கள்.",
        "askType": "{name}, {amount} ரூபாய். கடன் வாங்கினாரா அல்லது பணம் கொடுத்தாரா?",
        "chooseCustomer": "{name} என்ற பெயரில் {count} வாடிக்கையாளர்கள் உள்ளனர்: {options}. யார்?",
        "confirmCredit": "{name} க்கு {amount} ரூபாய் கடன். சேமிக்கவா?",
        "confirmCreditNew": "{name} புதிய வாடிக்கையாளர். {amount} ரூபாய் கடன். சேமிக்கவா?",
        "confirmPayment": "{name} இடமிருந்து {amount} ரூபாய் வந்தது. சேமிக்கவா?",
        "saved": "சேமிக்கப்பட்டது. {name} நிலுவை {balance} ரூபாய்.",
        "cancelled": "சரி, ரத்து செய்தேன்.",
        "balanceIs": "{name} நிலுவை {balance} ரூபாய்.",
        "balanceMulti": "{name} என்ற பெயரில் வாடிக்கையாளர்கள்: {list}.",
        "customerNotFound": "{name} என்ற வாடிக்கையாளர் இல்லை.",
        "totalDue": "அனைவரின் மொத்த நிலுவை {amount} ரூபாய்.",
    },
}

# Back-orders, same-name new customers, evening reminder. kn/te/ta: // VERIFY by native speaker
_MORE = {
    "hi": {
        "askNote": "नए {name} किस इलाके से हैं? इलाका बताइए, या 'skip' बोलिए।",
        "askItems": "{name} को क्या सामान चाहिए?",
        "confirmOrder": "{name} के लिए बाद में देना है: {items}। सेव करूँ?",
        "orderSaved": "ऑर्डर सेव हो गया। {name}: {items}।",
        "confirmArrived": "{name} का सामान आ गया: {items}। मार्क करूँ?",
        "arrivedSaved": "मार्क कर दिया। {name} को WhatsApp पर बताने के लिए बटन दबाइए।",
        "arrivedNoPhone": "मार्क कर दिया। {name} का फ़ोन नंबर नहीं है, ग्राहक पेज पर जोड़ दीजिए।",
        "noPendingOrder": "{name} का कोई बाकी ऑर्डर नहीं है।",
        "noPendingOrders": "कोई बाकी ऑर्डर नहीं है।",
        "pendingList": "बाकी ऑर्डर: {list}।",
        "missingPhones": "इन {count} ग्राहकों का फ़ोन नंबर नहीं है: {names}। कृपया जोड़ दीजिए।",
    },
    "en": {
        "askNote": "Which area is the new {name} from? Say the area, or say skip.",
        "askItems": "What does {name} need?",
        "confirmOrder": "To deliver later for {name}: {items}. Shall I save?",
        "orderSaved": "Order saved. {name}: {items}.",
        "confirmArrived": "{name}'s goods have arrived: {items}. Shall I mark it?",
        "arrivedSaved": "Marked. Tap the button to tell {name} on WhatsApp.",
        "arrivedNoPhone": "Marked. {name} has no phone number; please add it on the customer page.",
        "noPendingOrder": "{name} has no pending order.",
        "noPendingOrders": "There are no pending orders.",
        "pendingList": "Pending orders: {list}.",
        "missingPhones": "These {count} customers have no phone number: {names}. Please add them.",
    },
    "kn": {
        "askNote": "ಹೊಸ {name} ಯಾವ ಏರಿಯಾದವರು? ಏರಿಯಾ ಹೇಳಿ, ಅಥವಾ 'skip' ಎನ್ನಿ.",
        "askItems": "{name} ಅವರಿಗೆ ಏನು ಬೇಕು?",
        "confirmOrder": "{name} ಅವರಿಗೆ ನಂತರ ಕೊಡಬೇಕು: {items}. ಉಳಿಸಲೇ?",
        "orderSaved": "ಆರ್ಡರ್ ಉಳಿಸಲಾಗಿದೆ. {name}: {items}.",
        "confirmArrived": "{name} ಅವರ ಸಾಮಾನು ಬಂದಿದೆ: {items}. ಗುರುತು ಮಾಡಲೇ?",
        "arrivedSaved": "ಗುರುತು ಮಾಡಿದೆ. {name} ಅವರಿಗೆ WhatsApp ನಲ್ಲಿ ತಿಳಿಸಲು ಬಟನ್ ಒತ್ತಿ.",
        "arrivedNoPhone": "ಗುರುತು ಮಾಡಿದೆ. {name} ಅವರ ಫೋನ್ ನಂಬರ್ ಇಲ್ಲ, ಗ್ರಾಹಕರ ಪುಟದಲ್ಲಿ ಸೇರಿಸಿ.",
        "noPendingOrder": "{name} ಅವರ ಯಾವುದೇ ಬಾಕಿ ಆರ್ಡರ್ ಇಲ್ಲ.",
        "noPendingOrders": "ಯಾವುದೇ ಬಾಕಿ ಆರ್ಡರ್ ಇಲ್ಲ.",
        "pendingList": "ಬಾಕಿ ಆರ್ಡರ್‌ಗಳು: {list}.",
        "missingPhones": "ಈ {count} ಗ್ರಾಹಕರ ಫೋನ್ ನಂಬರ್ ಇಲ್ಲ: {names}. ದಯವಿಟ್ಟು ಸೇರಿಸಿ.",
    },
    "te": {
        "askNote": "కొత్త {name} ఏ ఏరియా వారు? ఏరియా చెప్పండి, లేదా 'skip' అనండి.",
        "askItems": "{name} కి ఏమి కావాలి?",
        "confirmOrder": "{name} కి తర్వాత ఇవ్వాలి: {items}. సేవ్ చేయనా?",
        "orderSaved": "ఆర్డర్ సేవ్ అయింది. {name}: {items}.",
        "confirmArrived": "{name} సామాను వచ్చింది: {items}. మార్క్ చేయనా?",
        "arrivedSaved": "మార్క్ చేశాను. {name} కి WhatsApp లో చెప్పడానికి బటన్ నొక్కండి.",
        "arrivedNoPhone": "మార్క్ చేశాను. {name} ఫోన్ నంబర్ లేదు, కస్టమర్ పేజీలో చేర్చండి.",
        "noPendingOrder": "{name} కి పెండింగ్ ఆర్డర్ లేదు.",
        "noPendingOrders": "పెండింగ్ ఆర్డర్లు లేవు.",
        "pendingList": "పెండింగ్ ఆర్డర్లు: {list}.",
        "missingPhones": "ఈ {count} కస్టమర్లకు ఫోన్ నంబర్ లేదు: {names}. దయచేసి చేర్చండి.",
    },
    "ta": {
        "askNote": "புதிய {name} எந்த பகுதியைச் சேர்ந்தவர்? பகுதியைச் சொல்லுங்கள், அல்லது 'skip' என்று சொல்லுங்கள்.",
        "askItems": "{name} க்கு என்ன வேண்டும்?",
        "confirmOrder": "{name} க்கு பிறகு கொடுக்க வேண்டும்: {items}. சேமிக்கவா?",
        "orderSaved": "ஆர்டர் சேமிக்கப்பட்டது. {name}: {items}.",
        "confirmArrived": "{name} இன் பொருட்கள் வந்துவிட்டன: {items}. குறிக்கவா?",
        "arrivedSaved": "குறித்தேன். {name} க்கு WhatsApp இல் சொல்ல பொத்தானை அழுத்துங்கள்.",
        "arrivedNoPhone": "குறித்தேன். {name} இன் தொலைபேசி எண் இல்லை, வாடிக்கையாளர் பக்கத்தில் சேர்க்கவும்.",
        "noPendingOrder": "{name} க்கு நிலுவை ஆர்டர் இல்லை.",
        "noPendingOrders": "நிலுவை ஆர்டர்கள் இல்லை.",
        "pendingList": "நிலுவை ஆர்டர்கள்: {list}.",
        "missingPhones": "இந்த {count} வாடிக்கையாளர்களுக்கு தொலைபேசி எண் இல்லை: {names}. தயவுசெய்து சேர்க்கவும்.",
    },
}
for _lang, _extra in _MORE.items():
    PROMPTS[_lang].update(_extra)

# LLM brain: fixed help text, fallback for small talk, phone number confirm. kn/te/ta: // VERIFY by native speaker
_BRAIN = {
    "hi": {"help": "मैं बोलखाता हूँ, आपका AI खाता सहायक। बोलिए जैसे 'Ramesh ne 300 udhaar liya', 'Lakshmi se 200 mile', 'Ramesh ka baaki kitna', या 'Sita ke liye 2 kilo cheeni order'।",
           "smalltalkFallback": "जी। जब भी उधार या जमा लिखवाना हो, बोलिए।",
           "confirmPhone": "{name} का फ़ोन नंबर {phone}। सेव करूँ?", "phoneSaved": "{name} का फ़ोन नंबर सेव हो गया।"},
    "en": {"help": "I am BolKhata, your AI ledger assistant. Say things like 'Ramesh took 300 on credit', 'Lakshmi paid 200', 'Ramesh's balance', or 'order 2 kg sugar for Sita'.",
           "smalltalkFallback": "Sure. Tell me whenever you want to note a credit or payment.",
           "confirmPhone": "{name}'s phone number is {phone}. Shall I save?", "phoneSaved": "{name}'s phone number is saved."},
    "kn": {"help": "ನಾನು ಬೋಲ್‌ಖಾತಾ, ನಿಮ್ಮ AI ಖಾತೆ ಸಹಾಯಕ. 'ರಮೇಶ್ 300 ಸಾಲ ತಗೊಂಡ್ರು', 'ಲಕ್ಷ್ಮಿ 200 ಕೊಟ್ಟರು', 'ರಮೇಶ್ ಬಾಕಿ ಎಷ್ಟು' ಎಂದು ಹೇಳಿ.",
           "smalltalkFallback": "ಸರಿ. ಸಾಲ ಅಥವಾ ಪಾವತಿ ಬರೆಯಬೇಕಾದಾಗ ಹೇಳಿ.",
           "confirmPhone": "{name} ಅವರ ಫೋನ್ ನಂಬರ್ {phone}. ಉಳಿಸಲೇ?", "phoneSaved": "{name} ಅವರ ಫೋನ್ ನಂಬರ್ ಉಳಿಸಲಾಗಿದೆ."},
    "te": {"help": "నేను బోల్‌ఖాతా, మీ AI ఖాతా సహాయకుడిని. 'రమేష్ 300 అప్పు తీసుకున్నారు', 'లక్ష్మి 200 ఇచ్చారు', 'రమేష్ బాకీ ఎంత' అని చెప్పండి.",
           "smalltalkFallback": "సరే. అప్పు లేదా చెల్లింపు రాయాలంటే చెప్పండి.",
           "confirmPhone": "{name} ఫోన్ నంబర్ {phone}. సేవ్ చేయనా?", "phoneSaved": "{name} ఫోన్ నంబర్ సేవ్ అయింది."},
    "ta": {"help": "நான் போல்காதா, உங்கள் AI கணக்கு உதவியாளர். 'ரமேஷ் 300 கடன் வாங்கினார்', 'லக்ஷ்மி 200 கொடுத்தார்', 'ரமேஷ் நிலுவை எவ்வளவு' என்று சொல்லுங்கள்.",
           "smalltalkFallback": "சரி. கடன் அல்லது பணம் எழுத வேண்டும் என்றால் சொல்லுங்கள்.",
           "confirmPhone": "{name} இன் தொலைபேசி எண் {phone}. சேமிக்கவா?", "phoneSaved": "{name} இன் தொலைபேசி எண் சேமிக்கப்பட்டது."},
}
for _lang, _extra in _BRAIN.items():
    PROMPTS[_lang].update(_extra)

# An LLM reply containing any of these is never spoken (no pressure or threats about money).
BANNED = {
    "en": ["pay now", "or else", "immediately", "legal action", "police", "court", "shame", "penalty", "last warning",
           "consequences", "defaulter", "blacklist"],
    "hi": ["अभी पैसे दो", "वरना", "तुरंत", "पुलिस", "कोर्ट", "शर्म", "जुर्माना", "आखिरी चेतावनी", "नतीजा", "abhi paise do",
           "warna", "turant", "sharam"],
    "kn": ["ಈಗಲೇ ಕೊಡಿ", "ಇಲ್ಲದಿದ್ದರೆ", "ಪೊಲೀಸ್", "ಕೋರ್ಟ್", "ನಾಚಿಕೆ", "ದಂಡ"],  # VERIFY by native speaker
    "te": ["ఇప్పుడే ఇవ్వండి", "లేకపోతే", "పోలీస్", "కోర్టు", "సిగ్గు", "జరిమానా"],  # VERIFY by native speaker
    "ta": ["இப்போதே கொடு", "இல்லையென்றால்", "போலீஸ்", "நீதிமன்றம்", "வெட்கம்", "அபராதம்"],  # VERIFY by native speaker
}

# WhatsApp text when ordered goods arrive. Polite, no pressure.
ARRIVED_MSG = {
    "hi": "नमस्ते {name} जी, आपका सामान ({items}) {shop} पर आ गया है। जब सुविधा हो, ले जाइए। धन्यवाद!",
    "en": "Hello {name}, your goods ({items}) have arrived at {shop}. Please pick them up whenever convenient. Thank you!",
    "kn": "ನಮಸ್ಕಾರ {name}, ನಿಮ್ಮ ಸಾಮಾನು ({items}) {shop} ಗೆ ಬಂದಿದೆ. ಅನುಕೂಲವಾದಾಗ ತೆಗೆದುಕೊಂಡು ಹೋಗಿ. ಧನ್ಯವಾದ!",  # VERIFY by native speaker
    "te": "నమస్తే {name}, మీ సామాను ({items}) {shop} కి వచ్చింది. మీకు వీలైనప్పుడు తీసుకెళ్ళండి. ధన్యవాదాలు!",  # VERIFY by native speaker
    "ta": "வணக்கம் {name}, உங்கள் பொருட்கள் ({items}) {shop} க்கு வந்துவிட்டன. வசதியான போது வந்து வாங்கிக்கொள்ளுங்கள். நன்றி!",  # VERIFY by native speaker
}

# Polite reminder only: no pressure, shame or threats.
REMINDER = {
    "hi": "नमस्ते {name} जी, {shop} की ओर से एक gentle reminder: आपका बाकी ₹{amount} है। जब सुविधा हो, यहाँ से दे सकते हैं: {upi} धन्यवाद!",
    "en": "Hello {name}, a gentle reminder from {shop}: your balance is ₹{amount}. Whenever convenient, you can pay here: {upi} Thank you!",
    "kn": "ನಮಸ್ಕಾರ {name}, {shop} ಇಂದ ಒಂದು gentle reminder: ನಿಮ್ಮ ಬಾಕಿ ₹{amount}. ಅನುಕೂಲವಾದಾಗ ಇಲ್ಲಿ ಪಾವತಿಸಬಹುದು: {upi} ಧನ್ಯವಾದ!",  # VERIFY by native speaker
    "te": "నమస్తే {name}, {shop} నుండి ఒక gentle reminder: మీ బాకీ ₹{amount}. మీకు వీలైనప్పుడు ఇక్కడ చెల్లించవచ్చు: {upi} ధన్యవాదాలు!",  # VERIFY by native speaker
    "ta": "வணக்கம் {name}, {shop} இலிருந்து ஒரு gentle reminder: உங்கள் நிலுவை ₹{amount}. வசதியான போது இங்கே செலுத்தலாம்: {upi} நன்றி!",  # VERIFY by native speaker
}

_UI_KEYS = ("home customers ledger settings typeHere send save cancel editAmount credit payment newCustomer search "
            "sortBalance sortName back remind phone total today creditGiven paymentsReceived net export all customer "
            "type amount language time said balance shopName upiVpa defaultLanguage auto demoData demoOn demoOff "
            "saved tapToSpeak listening detected bargeIn biasWarning noMic engineFallback running").split()

_UI_ROWS = {
    "en": ["Home", "Customers", "Ledger", "Settings", "Type instead…", "Send", "Save", "Cancel", "Edit amount",
           "CREDIT", "PAYMENT", "New customer", "Search", "Sort: balance", "Sort: name", "Back", "Send reminder",
           "Phone", "Total", "Today", "Credit given", "Payments received", "Net", "Export", "All", "Customer",
           "Type", "Amount", "Language", "Time", "What was said", "Balance", "Shop name", "UPI ID (VPA)",
           "Default language", "Auto", "Demo data (synthetic)", "Demo data is ON (SEED_DEMO)",
           "Demo data is OFF (SEED_DEMO=false)", "Saved", "Tap to speak", "Listening… tap to stop",
           "Detected", "Barge-in", "Name hints not accepted by Gnani; still transcribing.",
           "Microphone not available. Type instead.", "Switched voice engine to", "Running balance"],
    "hi": ["होम", "ग्राहक", "खाता", "सेटिंग्स", "यहाँ लिखें…", "भेजें", "सेव करें", "रद्द करें", "रकम बदलें",
           "उधार", "जमा", "नया ग्राहक", "खोजें", "क्रम: बाकी", "क्रम: नाम", "वापस", "याद दिलाएँ", "फ़ोन", "कुल",
           "आज", "उधार दिया", "पैसे मिले", "शुद्ध", "डाउनलोड", "सभी", "ग्राहक", "प्रकार", "रकम", "भाषा", "समय",
           "क्या बोला", "बाकी", "दुकान का नाम", "UPI ID (VPA)", "डिफ़ॉल्ट भाषा", "ऑटो", "डेमो डेटा (नकली)",
           "डेमो डेटा चालू है (SEED_DEMO)", "डेमो डेटा बंद है (SEED_DEMO=false)", "सेव हो गया", "बोलने के लिए दबाएँ",
           "सुन रहा हूँ… रोकने के लिए दबाएँ", "पहचानी गई", "बीच में बोलें", "Gnani ने नाम-सूची नहीं ली; सुनना जारी है।",
           "माइक नहीं मिला। लिखकर बताइए।", "आवाज़ इंजन बदला:", "चालू बाकी"],
    "kn": ["ಮುಖಪುಟ", "ಗ್ರಾಹಕರು", "ಖಾತೆ", "ಸೆಟ್ಟಿಂಗ್ಸ್", "ಇಲ್ಲಿ ಬರೆಯಿರಿ…", "ಕಳುಹಿಸಿ", "ಉಳಿಸಿ", "ರದ್ದು", "ಮೊತ್ತ ಬದಲಿಸಿ",
           "ಸಾಲ", "ಪಾವತಿ", "ಹೊಸ ಗ್ರಾಹಕ", "ಹುಡುಕಿ", "ಕ್ರಮ: ಬಾಕಿ", "ಕ್ರಮ: ಹೆಸರು", "ಹಿಂದೆ", "ನೆನಪಿಸಿ", "ಫೋನ್", "ಒಟ್ಟು",
           "ಇಂದು", "ಕೊಟ್ಟ ಸಾಲ", "ಬಂದ ಹಣ", "ನಿವ್ವಳ", "ಡೌನ್‌ಲೋಡ್", "ಎಲ್ಲಾ", "ಗ್ರಾಹಕ", "ವಿಧ", "ಮೊತ್ತ", "ಭಾಷೆ", "ಸಮಯ",
           "ಏನು ಹೇಳಿದರು", "ಬಾಕಿ", "ಅಂಗಡಿ ಹೆಸರು", "UPI ID (VPA)", "ಡೀಫಾಲ್ಟ್ ಭಾಷೆ", "ಆಟೋ", "ಡೆಮೊ ಡೇಟಾ (ಕೃತಕ)",
           "ಡೆಮೊ ಡೇಟಾ ಆನ್ (SEED_DEMO)", "ಡೆಮೊ ಡೇಟಾ ಆಫ್ (SEED_DEMO=false)", "ಉಳಿಸಲಾಗಿದೆ", "ಮಾತನಾಡಲು ಒತ್ತಿ",
           "ಕೇಳುತ್ತಿದ್ದೇನೆ… ನಿಲ್ಲಿಸಲು ಒತ್ತಿ", "ಗುರುತಿಸಿದ", "ಮಧ್ಯೆ ಮಾತು", "Gnani ಹೆಸರು ಪಟ್ಟಿ ಸ್ವೀಕರಿಸಲಿಲ್ಲ; ಕೇಳುವುದು ಮುಂದುವರಿದಿದೆ.",
           "ಮೈಕ್ ಸಿಗಲಿಲ್ಲ. ಬರೆದು ತಿಳಿಸಿ.", "ಧ್ವನಿ ಎಂಜಿನ್ ಬದಲಾಯಿತು:", "ಚಾಲ್ತಿ ಬಾಕಿ"],  # VERIFY by native speaker
    "te": ["హోమ్", "కస్టమర్లు", "ఖాతా", "సెట్టింగ్స్", "ఇక్కడ టైప్ చేయండి…", "పంపు", "సేవ్", "రద్దు", "మొత్తం మార్చు",
           "అప్పు", "చెల్లింపు", "కొత్త కస్టమర్", "వెతకండి", "క్రమం: బాకీ", "క్రమం: పేరు", "వెనుకకు", "గుర్తు చేయండి",
           "ఫోన్", "మొత్తం", "ఈరోజు", "ఇచ్చిన అప్పు", "వచ్చిన డబ్బు", "నికరం", "డౌన్‌లోడ్", "అన్నీ", "కస్టమర్", "రకం",
           "మొత్తం", "భాష", "సమయం", "ఏమి చెప్పారు", "బాకీ", "షాప్ పేరు", "UPI ID (VPA)", "డిఫాల్ట్ భాష", "ఆటో",
           "డెమో డేటా (కృత్రిమ)", "డెమో డేటా ఆన్ (SEED_DEMO)", "డెమో డేటా ఆఫ్ (SEED_DEMO=false)", "సేవ్ అయింది",
           "మాట్లాడటానికి నొక్కండి", "వింటున్నాను… ఆపడానికి నొక్కండి", "గుర్తించిన", "మధ్యలో మాట్లాడు",
           "Gnani పేర్ల జాబితాను తీసుకోలేదు; వినడం కొనసాగుతోంది.", "మైక్ దొరకలేదు. టైప్ చేయండి.", "వాయిస్ ఇంజిన్ మారింది:",
           "నడుస్తున్న బాకీ"],  # VERIFY by native speaker
    "ta": ["முகப்பு", "வாடிக்கையாளர்கள்", "கணக்கு", "அமைப்புகள்", "இங்கே தட்டச்சு செய்யவும்…", "அனுப்பு", "சேமி",
           "ரத்து", "தொகையை மாற்று", "கடன்", "செலுத்தல்", "புதிய வாடிக்கையாளர்", "தேடு", "வரிசை: நிலுவை",
           "வரிசை: பெயர்", "பின்", "நினைவூட்டு", "தொலைபேசி", "மொத்தம்", "இன்று", "கொடுத்த கடன்", "வந்த பணம்", "நிகரம்",
           "பதிவிறக்கு", "அனைத்தும்", "வாடிக்கையாளர்", "வகை", "தொகை", "மொழி", "நேரம்", "சொன்னது", "நிலுவை",
           "கடை பெயர்", "UPI ID (VPA)", "இயல்பு மொழி", "தானியங்கி", "டெமோ தரவு (செயற்கை)", "டெமோ தரவு ஆன் (SEED_DEMO)",
           "டெமோ தரவு ஆஃப் (SEED_DEMO=false)", "சேமிக்கப்பட்டது", "பேச அழுத்தவும்", "கேட்கிறேன்… நிறுத்த அழுத்தவும்",
           "கண்டறிந்தது", "இடையில் பேசு", "Gnani பெயர் பட்டியலை ஏற்கவில்லை; கேட்பது தொடர்கிறது.",
           "மைக் கிடைக்கவில்லை. தட்டச்சு செய்யவும்.", "குரல் இயந்திரம் மாறியது:", "நடப்பு நிலுவை"],  # VERIFY by native speaker
}
UI = {lang: dict(zip(_UI_KEYS, row, strict=True)) for lang, row in _UI_ROWS.items()}

_UI_MORE_KEYS = ("orders pendingOrders arrivedOrders markArrived markDelivered notifyCustomer items area lastVisit "
                 "closingTime dismiss order arrival eveningTitle brain regionalLanguage none").split()
_UI_MORE = {
    "en": ["Orders", "Pending orders", "Arrived, not picked up", "Arrived", "Delivered", "Tell on WhatsApp", "Items",
           "Area", "Last visit", "Shop closing time (evening reminder)", "Done", "ORDER", "ARRIVED", "Evening check", "LLM brain", "Shop's regional language (helps Auto)", "None"],
    "hi": ["ऑर्डर", "बाकी ऑर्डर", "आ गया, ले जाना बाकी", "आ गया", "दे दिया", "WhatsApp पर बताएँ", "सामान", "इलाका",
           "पिछली बार", "दुकान बंद होने का समय (शाम का रिमाइंडर)", "ठीक है", "ऑर्डर", "आ गया", "शाम की जाँच", "LLM दिमाग", "दुकान की क्षेत्रीय भाषा (ऑटो में मदद)", "कोई नहीं"],
    "kn": ["ಆರ್ಡರ್", "ಬಾಕಿ ಆರ್ಡರ್", "ಬಂದಿದೆ, ತೆಗೆದುಕೊಂಡಿಲ್ಲ", "ಬಂದಿದೆ", "ಕೊಟ್ಟಾಯಿತು", "WhatsApp ನಲ್ಲಿ ತಿಳಿಸಿ", "ಸಾಮಾನು",
           "ಏರಿಯಾ", "ಕೊನೆಯ ಭೇಟಿ", "ಅಂಗಡಿ ಮುಚ್ಚುವ ಸಮಯ (ಸಂಜೆ ನೆನಪು)", "ಸರಿ", "ಆರ್ಡರ್", "ಬಂದಿದೆ", "ಸಂಜೆ ಪರಿಶೀಲನೆ", "LLM ಮೆದುಳು", "ಅಂಗಡಿಯ ಪ್ರಾದೇಶಿಕ ಭಾಷೆ (ಆಟೋಗೆ ಸಹಾಯ)", "ಯಾವುದೂ ಇಲ್ಲ"],  # VERIFY by native speaker
    "te": ["ఆర్డర్లు", "పెండింగ్ ఆర్డర్లు", "వచ్చింది, తీసుకెళ్ళలేదు", "వచ్చింది", "ఇచ్చేశాం", "WhatsApp లో చెప్పండి", "సామాను",
           "ఏరియా", "చివరి సందర్శన", "షాప్ మూసే సమయం (సాయంత్రం గుర్తు)", "సరే", "ఆర్డర్", "వచ్చింది", "సాయంత్రం తనిఖీ", "LLM మెదడు", "షాప్ ప్రాంతీయ భాష (ఆటోకు సహాయం)", "ఏదీ లేదు"],  # VERIFY by native speaker
    "ta": ["ஆர்டர்கள்", "நிலுவை ஆர்டர்கள்", "வந்துவிட்டது, எடுக்கவில்லை", "வந்துவிட்டது", "கொடுத்தாயிற்று", "WhatsApp இல் சொல்",
           "பொருட்கள்", "பகுதி", "கடைசி வருகை", "கடை மூடும் நேரம் (மாலை நினைவூட்டல்)", "சரி", "ஆர்டர்", "வந்தது", "மாலை சரிபார்ப்பு", "LLM மூளை", "கடையின் பிராந்திய மொழி (தானியங்கிக்கு உதவும்)", "எதுவும் இல்லை"],  # VERIFY by native speaker
}
for _lang, _row in _UI_MORE.items():
    UI[_lang].update(zip(_UI_MORE_KEYS, _row, strict=True))


def say(lang: str, key: str, **kw) -> str:
    return PROMPTS.get(lang, PROMPTS["en"])[key].format(**kw)
