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
        "greeting": "Hello! I'm BolKhata, your AI ledger assistant. How can I help you today?",
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

# Undo (10 seconds after a save). kn/te/ta: // VERIFY by native speaker
_UNDO = {
    "hi": {"undone": "ठीक है, {name} की आखिरी एंट्री हटा दी।",
           "undoExpired": "10 सेकंड निकल गए, अब undo नहीं हो सकता। कुछ नहीं बदला।"},
    "en": {"undone": "Okay, I took back the last entry for {name}.",
           "undoExpired": "Undo works only within 10 seconds. Nothing was changed."},
    "kn": {"undone": "ಸರಿ, {name} ಅವರ ಕೊನೆಯ ಎಂಟ್ರಿ ತೆಗೆದೆ.",
           "undoExpired": "10 ಸೆಕೆಂಡ್ ಆಗಿಹೋಯಿತು, ಈಗ undo ಆಗಲ್ಲ. ಏನೂ ಬದಲಾಗಿಲ್ಲ."},
    "te": {"undone": "సరే, {name} చివరి ఎంట్రీ తీసేశాను.",
           "undoExpired": "10 సెకన్లు అయిపోయాయి, ఇప్పుడు undo కుదరదు. ఏమీ మారలేదు."},
    "ta": {"undone": "சரி, {name} கடைசி பதிவை நீக்கிட்டேன்.",
           "undoExpired": "10 வினாடி ஆகிவிட்டது, இப்போது undo முடியாது. எதுவும் மாறவில்லை."},
}
for _lang, _extra in _UNDO.items():
    PROMPTS[_lang].update(_extra)

# Contact saving, collections, top debtor. kn/te/ta: // VERIFY by native speaker
_CONTACT = {
    "hi": {"askPhone": "{name} का मोबाइल नंबर बोलिए।",
           "confirmPhoneNew": "{name} नए ग्राहक हैं, फ़ोन नंबर {phone}। सेव करूँ?",
           "phoneTaken": "यह नंबर {other} के नाम पर पहले से है। {name} के लिए भी {phone} सेव करूँ?",
           "collectionsToday": "आज {amount} रुपये मिले।", "collectionsWeek": "इस हफ़्ते {amount} रुपये मिले।",
           "topDebtor": "सबसे ज़्यादा बाकी {name} का है, {balance} रुपये।", "noDues": "किसी का कुछ बाकी नहीं है।"},
    "en": {"askPhone": "Please say {name}'s mobile number.",
           "confirmPhoneNew": "{name} is a new customer, phone number {phone}. Shall I save?",
           "phoneTaken": "This number is already saved for {other}. Save {phone} for {name} too?",
           "collectionsToday": "You received {amount} rupees today.", "collectionsWeek": "You received {amount} rupees this week.",
           "topDebtor": "{name} has the highest balance, {balance} rupees.", "noDues": "Nobody has any balance due."},
    "kn": {"askPhone": "{name} ಅವರ ಮೊಬೈಲ್ ನಂಬರ್ ಹೇಳಿ.",
           "confirmPhoneNew": "{name} ಹೊಸ ಗ್ರಾಹಕರು, ಫೋನ್ ನಂಬರ್ {phone}. ಉಳಿಸಲೇ?",
           "phoneTaken": "ಈ ನಂಬರ್ ಈಗಾಗಲೇ {other} ಅವರ ಹೆಸರಿನಲ್ಲಿದೆ. {name} ಅವರಿಗೂ {phone} ಉಳಿಸಲೇ?",
           "collectionsToday": "ಇಂದು {amount} ರೂಪಾಯಿ ಬಂತು.", "collectionsWeek": "ಈ ವಾರ {amount} ರೂಪಾಯಿ ಬಂತು.",
           "topDebtor": "ಅತಿ ಹೆಚ್ಚು ಬಾಕಿ {name} ಅವರದು, {balance} ರೂಪಾಯಿ.", "noDues": "ಯಾರದೂ ಬಾಕಿ ಇಲ್ಲ."},
    "te": {"askPhone": "{name} మొబైల్ నంబర్ చెప్పండి.",
           "confirmPhoneNew": "{name} కొత్త కస్టమర్, ఫోన్ నంబర్ {phone}. సేవ్ చేయనా?",
           "phoneTaken": "ఈ నంబర్ ఇప్పటికే {other} పేరు మీద ఉంది. {name} కి కూడా {phone} సేవ్ చేయనా?",
           "collectionsToday": "ఈరోజు {amount} రూపాయలు వచ్చాయి.", "collectionsWeek": "ఈ వారం {amount} రూపాయలు వచ్చాయి.",
           "topDebtor": "అందరికంటే ఎక్కువ బాకీ {name}, {balance} రూపాయలు.", "noDues": "ఎవరికీ బాకీ లేదు."},
    "ta": {"askPhone": "{name} இன் மொபைல் எண்ணைச் சொல்லுங்கள்.",
           "confirmPhoneNew": "{name} புதிய வாடிக்கையாளர், தொலைபேசி எண் {phone}. சேமிக்கவா?",
           "phoneTaken": "இந்த எண் ஏற்கனவே {other} பெயரில் உள்ளது. {name} க்கும் {phone} சேமிக்கவா?",
           "collectionsToday": "இன்று {amount} ரூபாய் வந்தது.", "collectionsWeek": "இந்த வாரம் {amount} ரூபாய் வந்தது.",
           "topDebtor": "அதிக நிலுவை {name}, {balance} ரூபாய்.", "noDues": "யாருக்கும் நிலுவை இல்லை."},
}
for _lang, _extra in _CONTACT.items():
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
                 "closingTime dismiss order arrival eveningTitle brain regionalLanguage none undo thinking failed retry offline").split()
_UI_MORE = {
    "en": ["Orders", "Pending orders", "Arrived, not picked up", "Arrived", "Delivered", "Tell on WhatsApp", "Items",
           "Area", "Last visit", "Shop closing time (evening reminder)", "Done", "ORDER", "ARRIVED", "Evening check", "LLM brain", "Shop's regional language (helps Auto)", "None", "Undo", "Working on it…", "Something went wrong while processing your request. Please try again.", "Try again", "Reconnecting… your next command will be sent when the connection is back."],
    "hi": ["ऑर्डर", "बाकी ऑर्डर", "आ गया, ले जाना बाकी", "आ गया", "दे दिया", "WhatsApp पर बताएँ", "सामान", "इलाका",
           "पिछली बार", "दुकान बंद होने का समय (शाम का रिमाइंडर)", "ठीक है", "ऑर्डर", "आ गया", "शाम की जाँच", "LLM दिमाग", "दुकान की क्षेत्रीय भाषा (ऑटो में मदद)", "कोई नहीं", "वापस लें", "समझ रहा हूँ…", "कुछ गड़बड़ हो गई। कृपया फिर से कोशिश करें।", "फिर से", "फिर से जुड़ रहे हैं… अगला कमांड जुड़ते ही भेजा जाएगा।"],
    "kn": ["ಆರ್ಡರ್", "ಬಾಕಿ ಆರ್ಡರ್", "ಬಂದಿದೆ, ತೆಗೆದುಕೊಂಡಿಲ್ಲ", "ಬಂದಿದೆ", "ಕೊಟ್ಟಾಯಿತು", "WhatsApp ನಲ್ಲಿ ತಿಳಿಸಿ", "ಸಾಮಾನು",
           "ಏರಿಯಾ", "ಕೊನೆಯ ಭೇಟಿ", "ಅಂಗಡಿ ಮುಚ್ಚುವ ಸಮಯ (ಸಂಜೆ ನೆನಪು)", "ಸರಿ", "ಆರ್ಡರ್", "ಬಂದಿದೆ", "ಸಂಜೆ ಪರಿಶೀಲನೆ", "LLM ಮೆದುಳು", "ಅಂಗಡಿಯ ಪ್ರಾದೇಶಿಕ ಭಾಷೆ (ಆಟೋಗೆ ಸಹಾಯ)", "ಯಾವುದೂ ಇಲ್ಲ", "ಹಿಂಪಡೆ", "ಅರ್ಥ ಮಾಡಿಕೊಳ್ಳುತ್ತಿದ್ದೇನೆ…", "ಏನೋ ತಪ್ಪಾಯಿತು. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.", "ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ", "ಮತ್ತೆ ಸಂಪರ್ಕಿಸುತ್ತಿದೆ… ಸಂಪರ್ಕ ಬಂದ ತಕ್ಷಣ ಮುಂದಿನ ಆದೇಶ ಕಳುಹಿಸಲಾಗುತ್ತದೆ."],  # VERIFY by native speaker
    "te": ["ఆర్డర్లు", "పెండింగ్ ఆర్డర్లు", "వచ్చింది, తీసుకెళ్ళలేదు", "వచ్చింది", "ఇచ్చేశాం", "WhatsApp లో చెప్పండి", "సామాను",
           "ఏరియా", "చివరి సందర్శన", "షాప్ మూసే సమయం (సాయంత్రం గుర్తు)", "సరే", "ఆర్డర్", "వచ్చింది", "సాయంత్రం తనిఖీ", "LLM మెదడు", "షాప్ ప్రాంతీయ భాష (ఆటోకు సహాయం)", "ఏదీ లేదు", "వెనక్కి", "అర్థం చేసుకుంటున్నాను…", "ఏదో తప్పు జరిగింది. దయచేసి మళ్ళీ ప్రయత్నించండి.", "మళ్ళీ ప్రయత్నించు", "మళ్ళీ కనెక్ట్ అవుతోంది… కనెక్షన్ రాగానే తదుపరి ఆదేశం పంపబడుతుంది."],  # VERIFY by native speaker
    "ta": ["ஆர்டர்கள்", "நிலுவை ஆர்டர்கள்", "வந்துவிட்டது, எடுக்கவில்லை", "வந்துவிட்டது", "கொடுத்தாயிற்று", "WhatsApp இல் சொல்",
           "பொருட்கள்", "பகுதி", "கடைசி வருகை", "கடை மூடும் நேரம் (மாலை நினைவூட்டல்)", "சரி", "ஆர்டர்", "வந்தது", "மாலை சரிபார்ப்பு", "LLM மூளை", "கடையின் பிராந்திய மொழி (தானியங்கிக்கு உதவும்)", "எதுவும் இல்லை", "திரும்பப் பெறு", "புரிந்துகொள்கிறேன்…", "ஏதோ தவறு நடந்தது. மீண்டும் முயற்சிக்கவும்.", "மீண்டும் முயற்சி", "மீண்டும் இணைக்கிறது… இணைப்பு வந்ததும் அடுத்த கட்டளை அனுப்பப்படும்."],  # VERIFY by native speaker
}
for _lang, _row in _UI_MORE.items():
    UI[_lang].update(zip(_UI_MORE_KEYS, _row, strict=True))

_DASH_KEYS = "goodMorning goodAfternoon goodEvening todayIn outstanding owingCount todayCredit todayCollections totalCustomers withDues addCredit recordPayment addCustomer viewLedger recent seeAll topDues thisWeek collected given pendingOrdersN noEntries processing tapToStop tapToStart micDenied micMissing playbackFailed online notifications name next noisyShop noisyShopHelp micCheck micOn micOff allClear".split()
_DASH = {'en': ['Good morning', 'Good afternoon', 'Good evening', "Here's today in {shop}.", 'Outstanding', '{n} owe', "Today's credit", "Today's collections", 'Customers', '{n} with dues', 'Add credit', 'Record payment', 'Add customer', 'View ledger', 'Recent entries', 'See all', 'Highest dues', 'This week', 'Collected', 'Given on credit', '{n} pending orders', 'No entries yet. Tap the mic and say "Ramesh took 200 on credit", or use Add credit.', 'Processing your request…', 'Listening… tap to stop', 'Tap to start the assistant', "Microphone permission is blocked. Allow it in the browser's site settings, or type instead.", 'No microphone found. Connect one, or type instead.', "Couldn't play the reply aloud. It's shown above.", 'Online', 'Reminders', 'Customer name', 'Next', 'Noisy shop mode', 'Ignores more background talk and noise. Speak a little louder and closer.', 'Microphone check', 'on', 'off', 'Nothing needs attention right now.'], 'hi': ['सुप्रभात', 'नमस्ते', 'शुभ संध्या', '{shop} में आज का हाल।', 'कुल बाकी', '{n} पर बाकी', 'आज का उधार', 'आज की वसूली', 'ग्राहक', '{n} पर बाकी', 'उधार लिखें', 'जमा लिखें', 'ग्राहक जोड़ें', 'खाता देखें', 'हाल की एंट्री', 'सब देखें', 'सबसे ज़्यादा बाकी', 'इस हफ़्ते', 'मिले', 'उधार दिया', '{n} ऑर्डर बाकी', 'अभी कोई एंट्री नहीं। माइक दबाकर बोलिए "Ramesh ne 200 udhaar liya", या उधार लिखें दबाइए।', 'आपकी बात समझ रहा हूँ…', 'सुन रहा हूँ… रोकने के लिए दबाएँ', 'सहायक शुरू करने के लिए दबाएँ', 'माइक की अनुमति बंद है। ब्राउज़र की साइट सेटिंग में अनुमति दें, या लिखकर बताइए।', 'माइक नहीं मिला। माइक लगाइए, या लिखकर बताइए।', 'जवाब बोलकर नहीं सुना पाए। ऊपर लिखा है।', 'ऑनलाइन', 'याद दिलाने वाली बातें', 'ग्राहक का नाम', 'आगे', 'शोर वाली दुकान मोड', 'पीछे की बातचीत और शोर को ज़्यादा अनदेखा करता है। थोड़ा पास और ज़ोर से बोलिए।', 'माइक जाँच', 'चालू', 'बंद', 'अभी कुछ ध्यान देने लायक नहीं है।'], 'kn': ['ಶುಭೋದಯ', 'ನಮಸ್ಕಾರ', 'ಶುಭ ಸಂಜೆ', '{shop} ನಲ್ಲಿ ಇಂದಿನ ವಿವರ.', 'ಒಟ್ಟು ಬಾಕಿ', '{n} ಜನರ ಬಾಕಿ', 'ಇಂದಿನ ಸಾಲ', 'ಇಂದಿನ ವಸೂಲಿ', 'ಗ್ರಾಹಕರು', '{n} ಜನರ ಬಾಕಿ', 'ಸಾಲ ಬರೆಯಿರಿ', 'ಪಾವತಿ ಬರೆಯಿರಿ', 'ಗ್ರಾಹಕ ಸೇರಿಸಿ', 'ಖಾತೆ ನೋಡಿ', 'ಇತ್ತೀಚಿನ ಎಂಟ್ರಿಗಳು', 'ಎಲ್ಲಾ ನೋಡಿ', 'ಹೆಚ್ಚು ಬಾಕಿ', 'ಈ ವಾರ', 'ಬಂದದ್ದು', 'ಸಾಲ ಕೊಟ್ಟದ್ದು', '{n} ಆರ್ಡರ್ ಬಾಕಿ', 'ಇನ್ನೂ ಎಂಟ್ರಿ ಇಲ್ಲ. ಮೈಕ್ ಒತ್ತಿ "ರಮೇಶ್ 200 ಸಾಲ ತಗೊಂಡ್ರು" ಎನ್ನಿ, ಅಥವಾ ಸಾಲ ಬರೆಯಿರಿ ಒತ್ತಿ.', 'ನಿಮ್ಮ ಮಾತು ಅರ್ಥ ಮಾಡಿಕೊಳ್ಳುತ್ತಿದ್ದೇನೆ…', 'ಕೇಳುತ್ತಿದ್ದೇನೆ… ನಿಲ್ಲಿಸಲು ಒತ್ತಿ', 'ಸಹಾಯಕ ಆರಂಭಿಸಲು ಒತ್ತಿ', 'ಮೈಕ್ ಅನುಮತಿ ಇಲ್ಲ. ಬ್ರೌಸರ್ ಸೈಟ್ ಸೆಟ್ಟಿಂಗ್\u200cನಲ್ಲಿ ಅನುಮತಿ ಕೊಡಿ, ಅಥವಾ ಬರೆಯಿರಿ.', 'ಮೈಕ್ ಸಿಗಲಿಲ್ಲ. ಮೈಕ್ ಜೋಡಿಸಿ, ಅಥವಾ ಬರೆಯಿರಿ.', 'ಉತ್ತರವನ್ನು ಓದಿ ಹೇಳಲಾಗಲಿಲ್ಲ. ಮೇಲೆ ತೋರಿಸಲಾಗಿದೆ.', 'ಆನ್\u200cಲೈನ್', 'ನೆನಪುಗಳು', 'ಗ್ರಾಹಕರ ಹೆಸರು', 'ಮುಂದೆ', 'ಗದ್ದಲದ ಅಂಗಡಿ ಮೋಡ್', 'ಹಿನ್ನೆಲೆ ಮಾತು ಮತ್ತು ಗದ್ದಲವನ್ನು ಹೆಚ್ಚು ನಿರ್ಲಕ್ಷಿಸುತ್ತದೆ. ಸ್ವಲ್ಪ ಹತ್ತಿರ ಮತ್ತು ಜೋರಾಗಿ ಮಾತನಾಡಿ.', 'ಮೈಕ್ ಪರಿಶೀಲನೆ', 'ಆನ್', 'ಆಫ್', 'ಈಗ ಗಮನಿಸಬೇಕಾದದ್ದು ಏನೂ ಇಲ್ಲ.'], 'te': ['శుభోదయం', 'నమస్కారం', 'శుభ సాయంత్రం', '{shop} లో ఈరోజు వివరాలు.', 'మొత్తం బాకీ', '{n} మంది బాకీ', 'ఈరోజు అప్పు', 'ఈరోజు వసూలు', 'కస్టమర్లు', '{n} మంది బాకీ', 'అప్పు రాయండి', 'చెల్లింపు రాయండి', 'కస్టమర్ జోడించండి', 'ఖాతా చూడండి', 'ఇటీవలి ఎంట్రీలు', 'అన్నీ చూడండి', 'ఎక్కువ బాకీ', 'ఈ వారం', 'వచ్చింది', 'అప్పు ఇచ్చింది', '{n} ఆర్డర్లు పెండింగ్', 'ఇంకా ఎంట్రీలు లేవు. మైక్ నొక్కి "రమేష్ 200 అప్పు తీసుకున్నారు" అనండి, లేదా అప్పు రాయండి నొక్కండి.', 'మీ మాట అర్థం చేసుకుంటున్నాను…', 'వింటున్నాను… ఆపడానికి నొక్కండి', 'సహాయకుడిని ప్రారంభించడానికి నొక్కండి', 'మైక్ అనుమతి లేదు. బ్రౌజర్ సైట్ సెట్టింగ్స్\u200cలో అనుమతి ఇవ్వండి, లేదా టైప్ చేయండి.', 'మైక్ దొరకలేదు. మైక్ కనెక్ట్ చేయండి, లేదా టైప్ చేయండి.', 'సమాధానాన్ని వినిపించలేకపోయాం. పైన చూపించాం.', 'ఆన్\u200cలైన్', 'గుర్తులు', 'కస్టమర్ పేరు', 'తర్వాత', 'సందడి షాప్ మోడ్', 'వెనుక మాటలు, శబ్దాన్ని ఎక్కువగా పట్టించుకోదు. కొంచెం దగ్గరగా, గట్టిగా మాట్లాడండి.', 'మైక్ తనిఖీ', 'ఆన్', 'ఆఫ్', 'ఇప్పుడు చూడాల్సినది ఏమీ లేదు.'], 'ta': ['காலை வணக்கம்', 'வணக்கம்', 'மாலை வணக்கம்', '{shop} இல் இன்றைய நிலவரம்.', 'மொத்த நிலுவை', '{n} பேர் நிலுவை', 'இன்றைய கடன்', 'இன்றைய வசூல்', 'வாடிக்கையாளர்கள்', '{n} பேர் நிலுவை', 'கடன் எழுது', 'பணம் எழுது', 'வாடிக்கையாளர் சேர்', 'கணக்கு பார்', 'சமீபத்திய பதிவுகள்', 'அனைத்தும் பார்', 'அதிக நிலுவை', 'இந்த வாரம்', 'வந்தது', 'கடன் கொடுத்தது', '{n} ஆர்டர்கள் நிலுவையில்', 'இன்னும் பதிவுகள் இல்லை. மைக்கை அழுத்தி "ரமேஷ் 200 கடன் வாங்கினார்" என்று சொல்லுங்கள், அல்லது கடன் எழுது அழுத்துங்கள்.', 'உங்கள் கோரிக்கையைப் புரிந்துகொள்கிறேன்…', 'கேட்கிறேன்… நிறுத்த அழுத்தவும்', 'உதவியாளரைத் தொடங்க அழுத்தவும்', 'மைக் அனுமதி தடுக்கப்பட்டுள்ளது. உலாவியின் தள அமைப்பில் அனுமதியுங்கள், அல்லது தட்டச்சு செய்யுங்கள்.', 'மைக் கிடைக்கவில்லை. மைக்கை இணையுங்கள், அல்லது தட்டச்சு செய்யுங்கள்.', 'பதிலைக் குரலில் இயக்க முடியவில்லை. மேலே காட்டப்பட்டுள்ளது.', 'ஆன்லைன்', 'நினைவூட்டல்கள்', 'வாடிக்கையாளர் பெயர்', 'அடுத்து', 'சத்தமான கடை முறை', 'பின்னணிப் பேச்சு மற்றும் சத்தத்தை அதிகம் தவிர்க்கும். சற்று அருகில் சத்தமாகப் பேசுங்கள்.', 'மைக் சோதனை', 'ஆன்', 'ஆஃப்', 'இப்போது கவனிக்க எதுவும் இல்லை.']}  # kn/te/ta: // VERIFY by native speaker
for _lang, _row in _DASH.items():
    UI[_lang].update(zip(_DASH_KEYS, _row, strict=True))
_TRY = {"en": "Try saying or tap:", "hi": "ऐसे बोलिए या दबाइए:", "kn": "ಹೀಗೆ ಹೇಳಿ ಅಥವಾ ಒತ್ತಿ:",  # VERIFY kn/te/ta
        "te": "ఇలా చెప్పండి లేదా నొక్కండి:", "ta": "இப்படிச் சொல்லுங்கள் அல்லது அழுத்துங்கள்:"}
for _lang, _s in _TRY.items():
    UI[_lang]["trySaying"] = _s



def say(lang: str, key: str, **kw) -> str:
    return PROMPTS.get(lang, PROMPTS["en"])[key].format(**kw)
