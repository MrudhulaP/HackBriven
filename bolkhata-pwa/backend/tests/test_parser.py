import pytest

from app.lang import detect_language, name_key, romanize
from app.nlu import amounts, choose_index, parse, tokenize


@pytest.mark.parametrize("text,amount", [
    ("Ramesh ne 340 udhaar liya", 340),
    ("dedh sau", 150),
    ("dhai sau", 250),
    ("saade teen sau", 350),
    ("paune do sau", 175),
    ("teen sau chalees", 340),
    ("do hazaar paanch sau", 2500),
    ("₹1,200", 1200),
    ("rs 1,20,000", 120000),
    ("४३०", 430),
    ("೨೦೦", 200),
    ("౩౦౦", 300),
    ("௫௦", 50),
    ("100rs", 100),
    ("Rs.250 diye", 250),
    ("2 hazaar 500", 2500),
    ("five hundred", 500),
    ("two thousand five hundred", 2500),
    ("पाँच सौ", 500),
    ("डेढ़ सौ", 150),
    ("ढाई हजार", 2500),
    ("ek kilo cheeni 50 rupaye", 50),
    ("Ramesh ne 340.50 liya", 340),
    ("four hundred fifty", 450),
    ("ಇನ್ನೂರು ರೂಪಾಯಿ", 200),
    ("ಎರಡು ಸಾವಿರ ಐನೂರು", 2500),
    ("ఐదు వందల యాభై", 550),
    ("இருநூறு ரூபாய்", 200),
])
def test_amount(text, amount):
    assert parse(text).amount == amount


def test_no_amount_in_plain_words():
    assert amounts(tokenize("Ramesh ka total kitna")) == []


@pytest.mark.parametrize("text,kind", [
    ("Ramesh ne 340 udhaar liya", "credit"),
    ("Ramesh ko 200 diya", "credit"),
    ("Ramesh se 100 mile", "payment"),
    ("Ramesh se 100 liya", "payment"),
    ("Ramesh ne 500 diya", "payment"),
    ("Ramesh ne 500 jama kiya", "payment"),
    ("Lakshmi 300 udhaar", "credit"),
    ("Suresh took 500 on credit", "credit"),
    ("Suresh paid 200", "payment"),
    ("payment 300 Ramesh", "payment"),
    ("रमेश ने 200 उधार लिया", "credit"),
    ("रमेश से 200 मिले", "payment"),
    ("ರಮೇಶ್ 200 payment ಕೊಟ್ಟರು", "payment"),
    ("Ramesh 200 baaki pe", "credit"),
    ("Ramesh 200", None),
])
def test_type(text, kind):
    assert parse(text).txn_type == kind


@pytest.mark.parametrize("text,name", [
    ("Ramesh ne 340 udhaar liya", "Ramesh"),
    ("aaj Ramesh ne 200 liya", "Ramesh"),
    ("kal Lakshmi se 50 mile", "Lakshmi"),
    ("Suresh took 500 on credit", "Suresh"),
    ("how much does Ramesh owe", "Ramesh"),
    ("Ramesh ka total kitna", "Ramesh"),
    ("लक्ष्मी का बाकी कितना है", "लक्ष्मी"),
    ("ರಮೇಶ್ 200 payment ಕೊಟ್ಟರು", "ರಮೇಶ್"),
    ("500 udhaar", None),
    ("haan", None),
])
def test_name(text, name):
    assert parse(text).name == name


@pytest.mark.parametrize("text,query", [
    ("Ramesh ka total kitna", True),
    ("लक्ष्मी का बाकी कितना है", True),
    ("kitna baaki hai", True),
    ("ರಮೇಶ್ ಎಷ್ಟು ಬಾಕಿ", True),
    ("రమేష్ బాకీ ఎంత", True),
    ("ரமேஷ் எவ்வளவு", True),
    ("Ramesh 200 baaki pe", False),
    ("Ramesh ne 340 liya", False),
])
def test_query(text, query):
    assert parse(text).is_query is query


@pytest.mark.parametrize("text,yes,no,corr", [
    ("haan", True, False, False),
    ("yes", True, False, False),
    ("ok save karo", True, False, False),
    ("हाँ", True, False, False),
    ("ಹೌದು", True, False, False),
    ("అవును", True, False, False),
    ("ஆமா", True, False, False),
    ("nahi", False, True, False),
    ("rehne do", False, True, False),
    ("cancel", False, True, False),
    ("ಇಲ್ಲ", False, True, False),
    ("nahi 430", False, True, True),
    ("no, 450", False, True, True),
    ("haan bhai woh Ramesh tha", False, False, False),
])
def test_yes_no_correction(text, yes, no, corr):
    p = parse(text)
    assert (p.yes, p.no, p.correction) == (yes, no, corr)


@pytest.mark.parametrize("word", ["रमेश", "ರಮೇಶ್", "రమేష్", "ரமேஷ்", "Ramesh", "RAMESH"])
def test_cross_script_names(word):
    assert name_key(word) == name_key("Ramesh")


def test_lakshmi_cross_script():
    assert name_key("लक्ष्मी") == name_key("Lakshmi") == name_key("ಲಕ್ಷ್ಮಿ")


def test_romanize():
    assert romanize("रमेश") == "ramesh"


@pytest.mark.parametrize("text,idx", [
    ("Station Road wala", 1),
    ("Gandhi Nagar wale", 0),
    ("pehla", 0),
    ("doosra", 1),
    ("second", 1),
    ("2", 1),
    ("ಮೊದಲ", 0),
    ("kuch bhi", None),
    ("स्टेशन रोड वाला।", 1),  # real Gnani transcript of "Station Road wala"
    ("गांधी नगर वाले", 0),
    ("दूसरा वाला", 1),
])
def test_choose(text, idx):
    assert choose_index(text, ["Gandhi Nagar", "Station Road"]) == idx


@pytest.mark.parametrize("text,current,gnani,expected", [
    ("Ramesh ne 100 udhaar liya", "en", None, "hi"),
    ("Suresh took 500 on credit", "hi", None, "en"),
    ("ರಮೇಶ್ 200 payment ಕೊಟ್ಟರು", "hi", None, "kn"),
    ("लक्ष्मी का बाकी कितना है", "en", None, "hi"),
    ("haan", "kn", None, "kn"),
    ("430", "te", None, "te"),
    ("ಮೊದಲ", "kn", None, "kn"),
    ("nahi 450", "en", None, "en"),
    ("Ramesh ka total kitna", "en", "en-IN", "hi"),
    ("payment ne", "en", "hi-IN", "hi"),  # tie broken by Gnani
])
def test_language(text, current, gnani, expected):
    assert detect_language(text, current, gnani) == expected


# Real Gnani prisma-v3.0 transcripts (indic-auto) of spoken Hinglish.
@pytest.mark.parametrize("text,amount,kind,name,query", [
    ("रमेश ने तीन सौ चालीस रुपये उधार लिया।", 340, "credit", "रमेश", False),
    ("रमेश ने 340 रुपये उधार लिया।", 340, "credit", "रमेश", False),
    ("रमेश का टोटल कितना?", None, None, "रमेश", True),
    ("लक्ष्मी ने पाँच सौ का पेमेंट किया", 500, "payment", "लक्ष्मी", False),
    ("ರಮೇಶ್ ಇನ್ನೂರು ರೂಪಾಯಿ ಪೇಮೆಂಟ್ ಕೊಟ್ಟರು.", 200, "payment", "ರಮೇಶ್", False),
    ("No four hundred fifty.", 450, None, None, False),
])
def test_real_gnani_transcripts(text, amount, kind, name, query):
    p = parse(text)
    assert (p.amount, p.txn_type, p.name, p.is_query) == (amount, kind, name, query)


# Real Gnani transcripts: English words come back in the speaker's script in every language, not just Hindi.
@pytest.mark.parametrize("text,yes,no,query", [
    ("ಓಕೆ ಸೇವ್ ಮಾಡಿ", True, False, False),
    ("ఒకే సేవ్ చేయండి", True, False, False),
    ("ஓகே சேவ் பண்ணுங்க", True, False, False),
    ("கேன்சல் பண்ணுங்க", False, True, False),
    ("రమేష్, టోటల్ బ్యాలెన్స్ ఎంత?", False, False, True),
    ("ரமேஷ் டோட்டல் பேலன்ஸ் எவ்வளவு", False, False, True),
])
def test_loanwords_in_regional_scripts(text, yes, no, query):
    p = parse(text)
    assert (p.yes, p.no, p.is_query, p.name is None or p.is_query) == (yes, no, query, True)


def test_garbled_cancel_still_cancels():
    assert parse("Cancel my D").no  # Gnani's English reading of "cancel maadi"


@pytest.mark.parametrize("text,amount,kind", [
    ("ರಮೇಶ್ ಮುನ್ನೂರು ಕ್ರೆಡಿಟ್ ತಗೊಂಡ್ರು.", 300, "credit"),
    ("రమేష్ రెండు వందలు పేమెంట్ ఇచ్చారు.", 200, "payment"),
    ("లక్ష్మి మూడు వందలు క్రెడిట్ తీసుకున్నారు.", 300, "credit"),
    ("லக்ஷ்மி இருநூறு பேமெண்ட் கொடுத்தார்.", 200, "payment"),
])
def test_regional_transcripts(text, amount, kind):
    p = parse(text)
    assert (p.amount, p.txn_type) == (amount, kind)


@pytest.mark.parametrize("text,name,strong", [
    ("aap kya kar sakte ho", None, False),
    ("Ramesh bhai ne 200 liya", "Ramesh", True),
    ("Lakshmi didi ka hisaab", "Lakshmi", True),
    ("yaar woh Ramesh aaya tha", "Ramesh", False),
])
def test_pronouns_and_honorifics_are_not_names(text, name, strong):
    p = parse(text)
    assert (p.name, p.name_strong) == (name, strong)
