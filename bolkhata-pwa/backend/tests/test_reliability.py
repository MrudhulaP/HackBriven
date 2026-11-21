"""Reliability round: numbers, order vs credit, ledger maths, language precedence, arrival notifications."""
import asyncio

import pytest
from fastapi.testclient import TestClient

from app import main
from app.dialogue import Conversation
from app.nlu import parse
from app.notify import notify_arrival


@pytest.mark.parametrize("text,amount", [
    ("One hundred rupees", 100), ("पांच सौ रुपये", 500), ("एक हजार रुपये", 1000), ("दस हजार रुपये", 10000),
    ("नौ करोड़ निन्यानवे लाख निन्यानवे हजार नौ सौ निन्यानवे", 99_999_999),
    ("निन्यानवे करोड़ निन्यानवे लाख निन्यानवे हजार नौ सौ निन्यानवे", 999_999_999),
    ("दो लाख पचास हजार", 250_000), ("डेढ़ करोड़", 15_000_000), ("सैंतालीस", 47),
    ("Ramesh ne 99,99,99,999 udhaar liya", 999_999_999),
])
def test_number_normalisation(text, amount):
    assert parse(text).amount == amount


def test_amount_is_int_and_implausible_values_are_asked_again():
    assert isinstance(parse("दस हजार रुपये").amount, int)
    assert parse("Ramesh ne 9999999999999 udhaar liya").amount is None  # above ₹10,000 crore: ask again


def test_phone_stays_phone_in_contact_sentence():
    p = parse("Ramesh ka number 9999999999 hai")
    assert p.phone == "9999999999" and p.amount is None


@pytest.mark.parametrize("text", ["Arjun needs 5 kgs of sugar.", "No, I mean Arjun needs 5 kgs of sugar.",
                                  "Arjun needs 5 kg of sugar", "Arjun ko 2 packet Maggi chahiye"])
def test_quantity_orders_are_never_money(text):
    p = parse(text)
    assert p.order and p.amount is None and p.txn_type is None


def test_reported_sentence_end_to_end(store):
    c = Conversation(store, "auto", "en")
    c.handle("Arjun took 100 on credit")
    c.handle("yes")
    before = len(store.entries())
    r = c.handle("No, I mean Arjun needs 5 kgs of sugar.")
    assert r["key"] == "confirmOrder" and r["card"]["items"] == "5 kgs sugar" and "amount" not in r["card"]
    c.handle("yes")
    assert len(store.entries()) == before and store.orders("pending")[0]["items"] == "5 kgs sugar"  # no ₹5 credit


def test_counts_are_not_money():
    p = parse("I have 5 customers")
    assert p.amount is None and not p.order


def test_quantity_plus_money_asks_order_or_credit(store):
    c = Conversation(store, "auto", "en")
    before = len(store.entries())
    r = c.handle("Lakshmi 5 kg sugar 200 rupees")
    assert r["key"] == "orderOrCredit" and r["state"] == "askKind"
    assert len(store.entries()) == before and not store.orders()  # nothing done while unsure
    r = c.tap_kind(1)
    assert r["card"]["type"] == "credit" and r["card"]["amount"] == 200


def test_ria_ledger_sequence(store):
    c = Conversation(store, "auto", "en")
    expected = []
    for say, bal in [("Ria took 500 rupees on credit", 500), ("Ria paid 200 rupees", 300),
                     ("Ria took 500 rupees on credit", 800), ("Ria paid 300", 500)]:
        c.handle(say)
        r = c.handle("yes")
        expected.append(bal)
        assert r["saved"] and str(bal) in r["text"]
    ria = store.find("Ria")
    assert len(ria) == 1 and ria[0]["balance"] == 500
    assert [(e["type"], e["amount"]) for e in store.entries(ria[0]["id"])] == [
        ("credit", 500), ("payment", 200), ("credit", 500), ("payment", 300)]


def test_double_save_tap_does_not_duplicate(store):
    c = Conversation(store)
    c.handle("Lakshmi ne 50 udhaar liya")
    assert c.tap_confirm(True)["saved"]
    assert c.tap_confirm(True)["key"] == "notUnderstood"
    assert store.find("Lakshmi")[0]["balance"] == 170


def test_explicit_english_is_never_overridden(store):
    c = Conversation(store, "en", "en")
    for said in ["लक्ष्मी का बाकी कितना है", "ರಮೇಶ್ 200 ಕೊಟ್ಟರು", "haan"]:
        assert c.handle(said)["lang"] == "en"


def test_twenty_turn_session_stays_consistent(store):
    c = Conversation(store, "auto", "en")
    script = [("Lakshmi took 10 on credit", "confirmCredit"), ("yes", "saved"), ("What does Lakshmi owe me?", "balanceIs"),
              ("Arjun needs 5 kgs of sugar", "confirmOrderNew"), ("yes", "orderSaved"), ("Who owes me the most?", "topDebtor"),
              ("Save Arjun's number as 9876543210", "confirmPhone"), ("yes", "phoneSaved"), ("Show today's collections", "collectionsToday"),
              ("Lakshmi paid 10", "confirmPayment"), ("no", "cancelled"), ("Lakshmi paid 10", "confirmPayment"), ("yes", "saved"),
              ("pending orders", "pendingList"), ("Arjun's sugar arrived", "confirmArrived"), ("yes", "arrivedSaved"),
              ("undo", "undone"), ("kitna baaki hai", "totalDue"), ("Ramesh ka total kitna", "balanceMulti"), ("hello there", None)]
    for said, key in script:
        r = c.handle(said)
        if key == "confirmOrderNew":
            assert r["key"] == "confirmOrder" and r["card"]["isNew"]
        elif key:
            assert r["key"] == key, (said, r["key"], r["text"])
    assert store.find("Lakshmi")[0]["balance"] == 120 and store.orders("pending")  # arrival undone


class FakeSender:
    name = "fake"

    def __init__(self, ok=True, boom=False):
        self.ok, self.boom, self.sent = ok, boom, []

    async def send(self, phone, text):
        if self.boom:
            raise TimeoutError()
        self.sent.append((phone, text))
        return self.ok, None if self.ok else "rejected"


def _arrived(store, who="Lakshmi"):
    cid = store.find(who)[0]["id"]
    oid = store.add_order(cid, "5 kg sugar", "x", "en")
    store.set_order_status(oid, "arrived")
    return oid


def _text(c, items):
    return f"Hello {c['name']}, {items} arrived"


def test_notification_sent_once(store):
    s, oid = FakeSender(), _arrived(store)
    r1 = asyncio.run(notify_arrival(store, [oid], s, _text))
    r2 = asyncio.run(notify_arrival(store, [oid], s, _text))
    assert r1["status"] == "sent" and r2["status"] == "already_sent" and len(s.sent) == 1
    assert s.sent[0][0] == "9000000003" and "5 kg sugar" in s.sent[0][1]


def test_notification_no_phone(store):
    c = store.add_customer("Sita")
    oid = store.add_order(c["id"], "2 packet maggi", "x", "en")
    store.set_order_status(oid, "arrived")
    s = FakeSender()
    assert asyncio.run(notify_arrival(store, [oid], s, _text))["status"] == "no_phone" and not s.sent


def test_notification_failure_keeps_order_arrived_and_can_retry(store):
    oid = _arrived(store)
    assert asyncio.run(notify_arrival(store, [oid], FakeSender(boom=True), _text))["status"] == "failed"
    assert store.orders("arrived")  # status not rolled back
    assert asyncio.run(notify_arrival(store, [oid], FakeSender(), _text))["status"] == "sent"
    rec = store.notifications_c.find_one({})
    assert rec["attempts"] == 2 and rec["status"] == "sent"


def test_notification_not_configured(store):
    oid = _arrived(store)
    assert asyncio.run(notify_arrival(store, [oid], None, _text))["status"] == "not_configured"


def test_arrived_button_reports_notification(db):
    with TestClient(main.create_app(db, brain=None)) as client:
        st = client.app.state.store
        oid = _arrived(st)
        st.set_order_status(oid, "pending")
        body = client.put(f"/api/orders/{oid}?lang=en", json={"status": "arrived"}).json()
        assert body["ok"] and body["notification"]["status"] == "not_configured" and body["notification"]["name"] == "Lakshmi"
        assert client.post(f"/api/orders/{oid}/notify").json()["notification"]["status"] == "not_configured"
        assert client.get("/api/notifications").json()[0]["attempts"] == 2


def test_phone_read_out_as_words():
    p = parse("Save Arjun's number as nine eight seven six five four three two one zero")
    assert p.phone == "9876543210" and p.amount is None and p.contact
    assert parse("नौ आठ सात छह पांच चार तीन दो एक शून्य").phone == "9876543210"
    assert parse("do teen sau").amount == 300  # short runs stay number words


def test_stray_spoken_yes_is_ignored_when_nothing_pending(store):
    c = Conversation(store, "auto", "en")
    r, source, _ = asyncio.run(c.handle_smart("Yes.", spoken=True))
    assert r is None and source == "junk"
    c.handle("Lakshmi took 10 on credit")
    r, _, _ = asyncio.run(c.handle_smart("Yes.", spoken=True))
    assert r["saved"]  # while confirming, yes still saves


@pytest.mark.parametrize("text", ["999 9999999", "9999999999", "99999 99999", "999-999-9999", "+91 99999 99999", "0 9999999999",
                                  "Arjun ka number 999 9999999 hai", "Ramesh ne 999 9999999 udhaar liya", "999 999 9999",
                                  "Save Ria's number as 98765 43210", "९९९ ९९९९९९९"])
def test_any_grouping_of_a_mobile_number_is_a_phone(text):
    p = parse(text)
    assert p.phone in ("9999999999", "9876543210") and p.amount is None


def test_numbers_that_are_not_phones_stay_amounts():
    assert parse("Ramesh ne 500 udhaar liya").phone is None
    assert parse("Ramesh ne 1,20,000 udhaar liya").amount == 120000
    assert parse("12345 67890").phone is None  # starts with 1: not an Indian mobile


# How Gnani actually writes spoken phone numbers and amounts (from the real-voice benchmark)
@pytest.mark.parametrize("heard,phone", [
    ("Save Arjun's number as triple nine triple nine double nine double nine.", "9999999999"),
    ("Arjun's phone number is nine eight seven six five four three two one zero.", "9876543210"),
    ("अर्जुन का नंबर नौ सौ निन्यानवे नौ नौ नौ नौ नौ नौ नौ है।", "9999999999"),
    ("Arjun ka mobile number ninety eight seven six five four three two one zero hai", "9876543210"),
    ("अर्जुन का नंबर डबल नौ आठ सात छह पांच चार तीन दो शून्य है", "9987654320"),
])
def test_phone_numbers_as_gnani_writes_them(heard, phone):
    p = parse(heard)
    assert p.phone == phone and p.amount is None and p.contact


@pytest.mark.parametrize("heard,amount", [("Write two five zero on Lakshmi's account.", 250),
                                          ("Lakshmi took two fifty on credit", 250), ("three forty rupees", 340)])
def test_amounts_as_gnani_writes_them(heard, amount):
    assert parse(heard).amount == amount


def test_devanagari_english_words_for_orders():
    p = parse("अर्जुन नीड्स पाँच किलोग्राम्स चीनी।")
    assert p.order and p.amount is None and p.name == "अर्जुन"


def test_hindi_top_debtor():
    assert parse("सबसे ज्यादा उधार किसका है?").top_debtor


@pytest.mark.parametrize("heard,intent", [
    ("Save Arjun's number as triple nine triple nine double nine double nine.", "phone"),
    ("अर्जुन नीड्स पाँच किलोग्राम्स चीनी।", "order")])
def test_new_customer_certain_intent_skips_llm(store, heard, intent):
    """A new name is only a guess, but a full phone or an order of goods is certain: rules answer, no LLM."""
    c = Conversation(store, "auto", "en")

    class Boom:
        async def interpret(self, *a):
            raise AssertionError("LLM must not be called")
    asyncio.run(c.handle_smart(heard, brain=Boom()))
    assert c.p.get("intent") == intent
