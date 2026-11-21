"""Each command stands on its own (no leftover questions), contact saving, follow-ups, collections, top debtor."""
import json

import pytest
from fastapi.testclient import TestClient

from app import main
from app.dialogue import Conversation
from app.nlu import parse


def test_prompt_isolation_sequence(store):
    c = Conversation(store)
    r = c.handle("Ramesh took 500 rupees on credit.")
    assert r["state"] == "chooseCustomer"
    r = c.handle("Save Arjun's number as 9999999999.")  # a new command, not an answer to "which Ramesh?"
    assert r["key"] == "confirmPhoneNew" and r["card"]["name"] == "Arjun" and r["card"]["phone"] == "99999 99999"
    r = c.handle("How much does Ramesh owe?")
    assert r["key"] == "balanceMulti" and "Arjun" not in r["text"]
    r = c.handle("Add Priya's number 9876543210.")
    assert r["key"] == "confirmPhoneNew" and r["card"]["name"] == "Priya"
    r = c.handle("Show today's collections.")
    assert r["key"] == "collectionsToday"
    assert not store.find("Arjun") and not store.find("Priya")  # nothing confirmed, nothing saved


@pytest.mark.parametrize("text,name", [
    ("Save Arjun's number as 9999999999.", "Arjun"),
    ("Add Priya's number 9876543210.", "Priya"),
    ("Arjun ka mobile number 9999999999 save karo", "Arjun"),
    ("ಅರ್ಜುನ್ ನಂಬರ್ 9999999999 ಸೇವ್ ಮಾಡಿ", "ಅರ್ಜುನ್"),
    ("అర్జున్ నంబర్ 9999999999 సేవ్ చేయండి", "అర్జున్"),
    ("அர்ஜுன் நம்பர் 9999999999 சேவ் பண்ணுங்க", "அர்ஜுன்"),
])
def test_save_contact_creates_customer_on_confirm(store, text, name):
    c = Conversation(store)
    r = c.handle(text)
    assert r["key"] == "confirmPhoneNew" and r["card"]["name"] == name and "amount" not in r["card"]
    r = c.handle("haan")
    assert r["key"] == "phoneSaved"
    saved = store.find(name)
    assert len(saved) == 1 and saved[0]["phone"] in ("9999999999", "9876543210")
    assert saved[0]["balance"] == 0 and isinstance(saved[0]["phone"], str)


def test_update_existing_customer_phone(store):
    c = Conversation(store)
    r = c.handle("Update Lakshmi's phone number to 9876543210")
    assert r["key"] == "confirmPhone" and r["card"]["name"] == "Lakshmi"
    c.handle("yes")
    lak = store.find("Lakshmi")
    assert len(lak) == 1 and lak[0]["phone"] == "9876543210" and lak[0]["balance"] == 120  # nothing else changed


def test_update_duplicate_name_asks_which(store):
    r = Conversation(store).handle("Update Ramesh's phone number to 9876543210")
    assert r["state"] == "chooseCustomer"


def test_number_already_used_by_someone_else(store):
    r = Conversation(store).handle("Save Arjun's number as 9000000003")  # Lakshmi's demo number
    assert r["key"] == "phoneTaken" and "Lakshmi" in r["text"]


def test_missing_number_is_asked(store):
    c = Conversation(store)
    r = c.handle("Save Arjun's number")
    assert r["key"] == "askPhone"
    r = c.handle("98765 43210")
    assert r["key"] == "confirmPhoneNew" and r["card"]["phone"] == "98765 43210"


def test_missing_name_is_asked(store):
    c = Conversation(store)
    r = c.handle("save number 9876543210")
    assert r["key"] == "askName"
    r = c.handle("Priya")
    assert r["key"] == "confirmPhoneNew" and r["card"]["name"] == "Priya"


def test_invalid_number_never_saved():
    p = parse("Save Arjun's number as 12345")
    assert p.phone is None and p.amount == 12345 and p.contact  # contact words but no valid mobile -> ask


def test_follow_up_pronoun_uses_last_customer(store):
    c = Conversation(store)
    c.handle("Lakshmi took 300 on credit")
    c.handle("yes")
    r = c.handle("He paid 200 today")
    assert r["card"]["name"] == "Lakshmi" and r["card"]["type"] == "payment" and r["card"]["amount"] == 200


def test_independent_command_does_not_inherit(store):
    c = Conversation(store)
    c.handle("Lakshmi took 300 on credit")
    c.handle("yes")
    r = c.handle("Save Arjun's number as 9999999999.")
    assert r["card"]["name"] == "Arjun"


def test_collections_and_top_debtor(store):
    c = Conversation(store)
    c.handle("Lakshmi se 50 mile")
    c.handle("haan")
    assert "200" in c.handle("Show today's collections.")["text"]  # demo's ₹150 today + this ₹50
    assert c.handle("How much money did I collect this week?")["key"] == "collectionsWeek"
    r = c.handle("Who owes me the most money?")
    assert r["key"] == "topDebtor" and "Gandhi Nagar" in r["text"] and "450" in r["text"]


# ---------- over the voice socket: replies carry their request id
def test_reply_carries_request_id(db):
    with TestClient(main.create_app(db, brain=None)) as client, client.websocket_connect("/ws/voice") as ws:
        ws.send_text(json.dumps({"type": "start", "engine": "browser", "lang": "auto"}))
        while json.loads(ws.receive_text())["type"] != "reply":
            pass
        for rid, text in [("c1", "Ramesh took 500 rupees on credit."), ("c2", "Save Arjun's number as 9999999999.")]:
            ws.send_text(json.dumps({"type": "text", "text": text, "id": rid}))
        got = []
        while len([m for m in got if m["type"] == "reply"]) < 2:
            m = json.loads(ws.receive_text())
            if m["type"] in ("transcript", "reply"):
                got.append(m)
        replies = [m for m in got if m["type"] == "reply"]
        assert [m["req"] for m in replies] == ["c1", "c2"]
        assert replies[1]["key"] == "confirmPhoneNew"  # c2's reply is about Arjun, not Ramesh


def test_money_questions_answered_by_rules_in_english(store):
    c = Conversation(store)
    r = c.handle("Who owes me the most money?")
    assert r["key"] == "topDebtor" and not c.soft_miss and r["lang"] == "en"
    r = c.handle("How much money did I collect this week?")
    assert r["key"] == "collectionsWeek" and not c.soft_miss
    assert Conversation(store).handle("Save Arjun's number as 9999999999.")["lang"] == "en"
