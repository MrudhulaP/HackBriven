"""Kannada/Telugu/Tamil verbs ('gave TO' = credit), order/arrival words, and undo within 10 seconds."""
import pytest

from app.dialogue import UNDO_SECONDS, Conversation
from app.nlu import parse


@pytest.mark.parametrize("text,kind", [
    # Kannada
    ("ರಮೇಶ್‌ಗೆ 200 ಕೊಟ್ಟೆ", "credit"), ("ರಮೇಶ್‌ಗೆ 200 ಕೊಟ್ಟರು", "credit"), ("ರಮೇಶ್ 200 ಕೊಟ್ಟರು", "payment"),
    ("ರಮೇಶ್ 200 ಕೊಟ್ರು", "payment"), ("ರಮೇಶ್ 200 ಕಟ್ಟಿದರು", "payment"), ("ರಮೇಶ್ 200 ಉದ್ರಿ", "credit"),
    ("ರಮೇಶ್ 200 ಜಮಾ", "payment"), ("ರಮೇಶ್ 200 ಸಾಲ ತಗೊಂಡ್ರು", "credit"),
    # Telugu
    ("రమేష్‌కి 200 ఇచ్చాను", "credit"), ("రమేష్ 200 ఇచ్చాడు", "payment"), ("రమేష్ 200 ఇచ్చారు", "payment"),
    ("రమేష్ 200 కట్టారు", "payment"), ("రమేష్ 200 జమ", "payment"), ("రమేష్ 200 అప్పు తీసుకున్నారు", "credit"),
    # Tamil
    ("ரமேஷுக்கு 200 கொடுத்தேன்", "credit"), ("ரமேஷ் 200 குடுத்தாரு", "payment"), ("ரமேஷ் 200 கொடுத்தார்", "payment"),
    ("ரமேஷ் 200 கட்டினார்", "payment"), ("ரமேஷ் 200 வரவு", "payment"), ("ரமேஷ் 200 கடன் வாங்கினார்", "credit"),
    # code-mixed and Hindi unchanged
    ("ರಮೇಶ್ 200 payment ಕೊಟ್ಟರು", "payment"), ("Ramesh ku 500 kadan", "credit"), ("రమేష్ 300 credit", "credit"),
    ("Ramesh ne 340 udhaar liya", "credit"), ("Ramesh ko 200 diya", "credit"), ("Ramesh se 100 mile", "payment"),
])
def test_regional_verbs(text, kind):
    assert parse(text).txn_type == kind


def test_gave_to_customer_is_credit_end_to_end(store):
    r = Conversation(store).handle("ಲಕ್ಷ್ಮಿಗೆ 200 ಕೊಟ್ಟೆ")
    assert r["state"] == "confirming" and r["card"]["type"] == "credit" and r["card"]["name"] == "Lakshmi"


@pytest.mark.parametrize("text,items", [
    ("Lakshmi ko 5 kilo cheeni chahiye", "5 kilo cheeni"),
    ("Lakshmi ke liye 2 packet Maggi mangwana hai", "2 packet maggi"),
    ("ಲಕ್ಷ್ಮಿಗೆ 2 ಕೆಜಿ ಸಕ್ಕರೆ ಬೇಕು", "2 ಕೆಜಿ ಸಕ್ಕರೆ"),
    ("లక్ష్మికి 2 కిలోలు చక్కెర కావాలి", "2 కిలోలు చక్కెర"),
    ("லக்ஷ்மிக்கு 2 கிலோ சர்க்கரை வேணும்", "2 கிலோ சர்க்கரை"),
])
def test_want_words_make_orders(store, text, items):
    p = parse(text)
    assert p.order and p.amount is None
    r = Conversation(store).handle(text)
    assert r["key"] == "confirmOrder" and r["card"]["items"] == items


def test_money_want_is_not_an_order():
    assert not parse("ಅಣ್ಣ, ಮುನ್ನೂರು ರೂಪಾಯಿ ಸಾಮಾನು ಬೇಕು, ಸಾಲದಲ್ಲಿ ಬರೆದುಕೊಳ್ಳಿ").order
    assert not parse("அண்ணா, முந்நூறு ரூபாய்க்கு சாமான் வேணும்").order


def _order(store, who="Lakshmi", what="5 kilo cheeni"):
    c = Conversation(store)
    c.handle(f"{who} ke liye {what} order karo")
    c.handle("haan")


@pytest.mark.parametrize("text", ["ಲಕ್ಷ್ಮಿ ಸಾಮಾನು ಬಂತು", "లక్ష్మి సామాను వచ్చేసింది", "லக்ஷ்மி சாமான் வந்துச்சு", "Lakshmi ka saamaan aa gaya"])
def test_goods_came_words(store, text):
    _order(store)
    r = Conversation(store).handle(text)
    assert r["key"] == "confirmArrived"


def test_money_came_is_not_arrival():
    assert not parse("ರಮೇಶ್ ಹಣ ಬಂತು").arrival


def test_arrival_found_by_item_alone(store):
    _order(store)
    r = Conversation(store).handle("cheeni aa gayi")
    assert r["key"] == "confirmArrived" and r["card"]["name"] == "Lakshmi"


def test_arrival_by_item_two_customers_asks_which(store):
    _order(store, "Lakshmi")
    _order(store, "Suresh")
    r = Conversation(store).handle("cheeni aa gayi")
    assert r["state"] == "chooseCustomer" and len(r["options"]) == 2  # Lakshmi or Suresh; no 'new customer' chip


def test_whose_goods_pending(store):
    _order(store)
    r = Conversation(store).handle("kiska saamaan baaki hai")
    assert r["key"] == "pendingList" and "5 kilo cheeni" in r["text"]


@pytest.mark.parametrize("text", ["ಒಟ್ಟು ಬಾಕಿ ಎಷ್ಟು", "మొత్తం బాకీ ఎంత", "மொத்த நிலுவை எவ்வளவு"])
def test_total_words_are_not_names(store, text):
    assert Conversation(store).handle(text)["key"] == "totalDue"


# ---------- undo
class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def conv(store):
    c = Conversation(store)
    c.clock = Clock()
    return c


@pytest.mark.parametrize("phrase", ["undo", "galti ho gayi", "wapas lo", "cancel karo", "ತಪ್ಪಾಯ್ತು", "ತಪ್ಪಾಯಿತು.", "తప్పు అయింది",
                                    "தப்பா போச்சு", "go back"])
def test_undo_entry_by_voice(store, phrase):
    c = conv(store)
    before = len(store.entries())
    c.handle("Lakshmi ne 300 udhaar liya")
    r = c.handle("haan")
    assert r["saved"] and r["undo"] == UNDO_SECONDS and len(store.entries()) == before + 1
    c.clock.t += 5
    r = c.handle(phrase)
    assert r["key"] == "undone" and len(store.entries()) == before
    assert store.find("Lakshmi")[0]["balance"] == 120


def test_undo_after_10_seconds_does_nothing(store):
    c = conv(store)
    c.handle("Lakshmi ne 300 udhaar liya")
    c.handle("haan")
    c.clock.t += 11
    assert c.handle("undo")["key"] == "undoExpired"
    assert store.find("Lakshmi")[0]["balance"] == 420


def test_undo_only_once(store):
    c = conv(store)
    c.handle("Lakshmi ne 300 udhaar liya")
    c.handle("haan")
    assert c.undo()["key"] == "undone"
    assert c.undo()["key"] == "undoExpired"


def test_undo_removes_new_customer(store):
    c = conv(store)
    c.handle("Suresh took 500 on credit")
    c.handle("yes")
    assert store.find("Suresh")
    c.undo()
    assert not store.find("Suresh")


def test_undo_phone_restores_old_number(store):
    c = conv(store)
    c.p = {"intent": "phone", "name": "Lakshmi", "customer": store.find("Lakshmi")[0], "phone": "9876543210",
           "raw": "x", "type": None, "amount": None, "items": ""}
    c.state = "confirming"
    c.tap_confirm(True)
    assert store.find("Lakshmi")[0]["phone"] == "9876543210"
    c.undo()
    assert store.find("Lakshmi")[0]["phone"] == "9000000003"


def test_undo_order_and_arrival(store):
    c = conv(store)
    c.handle("Lakshmi ke liye 5 kilo cheeni order karo")
    c.handle("haan")
    assert len(store.orders("pending")) == 1
    c.undo()
    assert not store.orders()
    c.handle("Lakshmi ke liye 5 kilo cheeni order karo")
    c.handle("haan")
    c.handle("Lakshmi ka saamaan aa gaya")
    c.handle("haan")
    assert len(store.orders("arrived")) == 1
    c.undo()
    assert len(store.orders("pending")) == 1


def test_undo_word_while_confirming_cancels(store):
    c = conv(store)
    before = len(store.entries())
    c.handle("Lakshmi ne 300 udhaar liya")
    assert c.handle("undo")["key"] == "cancelled" and len(store.entries()) == before


def test_undo_with_nothing_to_undo(store):
    assert conv(store).handle("undo")["key"] == "undoExpired"
