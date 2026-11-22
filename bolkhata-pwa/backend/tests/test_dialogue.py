import pytest

from app.dialogue import Conversation


def ids_by_note(store):
    return {c["note"] or c["name"]: c["id"] for c in store.customers()}


def n_entries(store):
    return len(store.entries())


def test_seed_balances(store):
    b = {c["note"] or c["name"]: c["balance"] for c in store.customers()}
    assert b == {"Gandhi Nagar": 450, "Station Road": 200, "Lakshmi": 120}


def test_greeting_says_ai(store):
    r = Conversation(store).greeting()
    assert "AI" in r["text"] and r["lang"] == "hi"


def test_duplicate_ramesh_station_road_flow(store):
    c = Conversation(store)
    before = n_entries(store)
    r = c.handle("Ramesh ne 100 udhaar liya")
    assert r["state"] == "chooseCustomer" and r["options"][:2] == ["Gandhi Nagar", "Station Road"]
    assert "2" in r["text"]
    r = c.handle("Station Road wala")
    assert r["state"] == "confirming" and r["card"]["note"] == "Station Road" and r["card"]["amount"] == 100
    assert n_entries(store) == before  # nothing saved before confirm
    r = c.handle("haan")
    assert r["saved"] and "300" in r["text"]
    assert store.balance(ids_by_note(store)["Station Road"]) == 300


def test_both_balances_for_shared_name(store):
    r = Conversation(store).handle("Ramesh ka total kitna")
    assert r["key"] == "balanceMulti"
    assert "Gandhi Nagar 450" in r["text"] and "Station Road 200" in r["text"]


def test_devanagari_finds_latin_lakshmi(store):
    r = Conversation(store).handle("लक्ष्मी का बाकी कितना है")
    assert r["key"] == "balanceIs" and "Lakshmi" in r["text"] and "120" in r["text"] and r["lang"] == "hi"


def test_total_due_without_name(store):
    r = Conversation(store).handle("kitna baaki hai")
    assert r["key"] == "totalDue" and "770" in r["text"]


def test_kannada_payment_with_choice(store):
    c = Conversation(store)
    r = c.handle("ರಮೇಶ್ 200 payment ಕೊಟ್ಟರು")
    assert r["state"] == "chooseCustomer" and r["lang"] == "kn"
    r = c.handle("ಮೊದಲ")
    assert r["state"] == "confirming" and r["lang"] == "kn" and r["card"]["note"] == "Gandhi Nagar"
    assert r["card"]["type"] == "payment"
    r = c.handle("ಹೌದು")
    assert r["saved"] and r["lang"] == "kn" and "250" in r["text"]


def test_new_customer_with_correction(store):
    c = Conversation(store)
    r = c.handle("Suresh took 500 on credit")
    assert r["key"] == "confirmCreditNew" and r["card"]["isNew"] and r["lang"] == "en"
    r = c.handle("nahi 450")
    assert r["state"] == "confirming" and r["card"]["amount"] == 450
    assert not store.find("Suresh")  # not created before confirm
    r = c.handle("yes")
    assert r["saved"] and "450" in r["text"]
    s = store.find("Suresh")
    assert len(s) == 1 and s[0]["balance"] == 450
    assert store.entries(s[0]["id"])[0]["raw_text"] == "Suresh took 500 on credit | nahi 450"


def test_correction_changes_340_to_430(store):
    c = Conversation(store)
    c.handle("Lakshmi ne 340 udhaar liya")
    r = c.handle("nahi 430")
    assert r["card"]["amount"] == 430
    c.handle("haan")
    assert store.find("Lakshmi")[0]["balance"] == 120 + 430


def test_cancel_saves_nothing(store):
    c = Conversation(store)
    before = n_entries(store)
    c.handle("Lakshmi ne 340 udhaar liya")
    r = c.handle("nahi")
    assert r["key"] == "cancelled" and r["state"] == "idle"
    assert n_entries(store) == before


def test_rehne_do_cancels(store):
    c = Conversation(store)
    c.handle("Lakshmi ne 340 udhaar liya")
    assert c.handle("rehne do")["key"] == "cancelled"


def test_ask_amount_then_number(store):
    c = Conversation(store)
    r = c.handle("Lakshmi ne udhaar liya")
    assert r["state"] == "askAmount" and "Lakshmi" in r["text"]
    r = c.handle("dedh sau")
    assert r["state"] == "confirming" and r["card"]["amount"] == 150


def test_ask_name(store):
    c = Conversation(store)
    r = c.handle("500 udhaar")
    assert r["state"] == "askName"
    r = c.handle("Lakshmi")
    assert r["state"] == "confirming" and r["card"]["name"] == "Lakshmi"


def test_ask_type(store):
    c = Conversation(store)
    r = c.handle("Lakshmi 200")
    assert r["state"] == "askType"
    r = c.handle("udhaar")
    assert r["state"] == "confirming" and r["card"]["type"] == "credit"


def test_tap_save_and_choose(store):
    c = Conversation(store)
    c.handle("Ramesh ne 100 udhaar liya")
    r = c.tap_choose(0)
    assert r["card"]["note"] == "Gandhi Nagar"
    r = c.tap_amount(120)
    assert r["card"]["amount"] == 120
    r = c.tap_confirm(True)
    assert r["saved"] and "570" in r["text"]


def test_tap_cancel(store):
    c = Conversation(store)
    before = n_entries(store)
    c.handle("Lakshmi ne 50 liya")
    assert c.tap_confirm(False)["key"] == "cancelled"
    assert n_entries(store) == before


def test_unknown_customer_query(store):
    r = Conversation(store).handle("Mohan ka baaki kitna")
    assert r["key"] == "customerNotFound"


def test_not_understood(store):
    assert Conversation(store).handle("haan")["key"] == "notUnderstood"


def test_fixed_language_mode(store):
    c = Conversation(store, lang_mode="en")
    r = c.handle("Lakshmi ka baaki kitna")
    assert r["lang"] == "en" and "Lakshmi's balance is 120" in r["text"]


def test_raw_text_encrypted_at_rest(store, db):
    c = Conversation(store)
    c.handle("Lakshmi ne 77 udhaar liya")
    c.handle("haan")
    raw = db.entries.find_one({"amount": 77})["raw_text"]
    assert "Lakshmi" not in raw
    assert any(e["raw_text"] == "Lakshmi ne 77 udhaar liya" for e in store.entries())
    assert "9000000003" not in str(db.customers.find_one({"name": "Lakshmi"})["phone"])


def test_amount_is_int(store):
    c = Conversation(store)
    c.handle("Lakshmi ne saade teen sau liya")
    c.handle("haan")
    e = store.entries()[-1]
    assert e["amount"] == 350 and type(e["amount"]) is int


def test_new_full_command_replaces_pending_question(store):
    c = Conversation(store)
    assert c.handle("Ramesh ne udhaar liya")["state"] == "askAmount"
    r = c.handle("Suresh took 500 on credit")
    assert r["key"] == "confirmCreditNew" and r["card"]["name"] == "Suresh" and r["card"]["amount"] == 500


@pytest.mark.parametrize("text", ["theek nahi hai", "sahi nahi", "not correct", "ಸರಿ ಇಲ್ಲ", "సరే కాదు", "சரி இல்லை", "ok nahi"])
def test_negated_yes_never_saves(store, text):
    c = Conversation(store)
    before = len(store.entries())
    c.handle("Lakshmi ne 300 udhaar liya")
    r = c.handle(text)
    assert not r["saved"] and r["key"] == "cancelled" and len(store.entries()) == before


@pytest.mark.parametrize("text", ["haan", "theek hai", "yes", "haan haan", "ಹೌದು", "ஆமாம்"])
def test_plain_yes_still_saves(store, text):
    c = Conversation(store)
    c.handle("Lakshmi ne 300 udhaar liya")
    assert c.handle(text)["saved"]


def test_haan_na_is_yes(store):
    c = Conversation(store)
    c.handle("Lakshmi ne 300 udhaar liya")
    assert c.handle("haan na")["saved"]  # bare 'na' as a filler is not a no


def test_yes_with_different_amount_corrects_without_saving(store):
    c = Conversation(store)
    before = len(store.entries())
    c.handle("Lakshmi ne 300 udhaar liya")
    r = c.handle("haan 400")
    assert r["state"] == "confirming" and r["card"]["amount"] == 400 and len(store.entries()) == before
    r = c.handle("haan")
    assert r["saved"] and store.find("Lakshmi")[0]["balance"] == 520


def test_yes_with_same_amount_saves(store):
    c = Conversation(store)
    c.handle("Lakshmi ne 300 udhaar liya")
    r = c.handle("haan 300")
    assert r["saved"] and store.find("Lakshmi")[0]["balance"] == 420
